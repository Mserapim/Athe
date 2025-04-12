from django.core.exceptions import ValidationError

from contrib.middleware import set_current_user
from contrib.newrest import RestfulDRY
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.channels.models import Channel
from edocs.protocolo.models import Protocolo, ProtocoloManager
from rh.models import Endereco as Address
from rh.models import PessoaFisica as Citizen
from rh.models import PessoaJuridica as LegalPerson
from rh.models import Telefone as Phone


class BaseProtocolAPI(EDOCManage):
    def _get_address_params(self, data):
        return {
            "tipo_endereco": data["address_type"],
            "tipo_logradouro": data["public_place_type"],
            "cep": data["zipcode"],
            "logradouro": data["public_place"],
            "complemento": data["extra"],
            "bairro": data["neighborhood"],
            "numero": data["number"],
            "municipio": data["city"],
        }

    def _create_address(self, data):
        params = self._get_address_params(data)
        address, _ = Address.objects.get_or_create(
            cep=data["zipcode"], person=data["person"], defaults=params
        )

        return address

    def _get_phone_params(self, data):
        return {"tipo_telefone": data["phone_type"], "numero": data["phone_number"]}

    def _create_phone(self, data):
        params = self._get_phone_params(data)
        phone = None
        if data["phone_type"] and data["phone_number"]:
            phone, _ = Phone.objects.get_or_create(
                numero=data["number"], person=data["person"], defaults=params
            )

        return phone

    def _get_base_person_params(self, data):
        return {"nome": data["name"], "email": data["email"]}

    def _get_legal_person_params(self, data):
        params = self._get_base_person_params(data)
        params.update(razao_social=data["name"])

        return params

    def _create_legal_person(self, data):
        params = self._get_legal_person_params(data)

        legal_persons = LegalPerson.objects.filter(cnpj=data["cnpj"])
        if legal_persons.exists():
            legal_person = legal_persons.first()

            if data["email"].lower() not in (legal_person.email,):
                raise ValidationError(
                    {"email": "O email informado não com confere com o cadastrado"}
                )
        else:
            params.update(cnpj=data["cnpj"])
            legal_person = LegalPerson.objects.create(**params)

        return legal_person

    def _get_citizen_params(self, data):
        params = self._get_base_person_params(data)
        params.update(
            {
                "sexo": data["genre"],
                "grau_instrucao": data["education_level"],
                "estado_civil": data["marital_status"],
                "raca_cor": data["race"],
            }
        )

        return params

    def _create_citizen_person(self, data):
        params = self._get_citizen_params(data)

        citizens = Citizen.objects.filter(cpf=data["cpf"])
        if citizens.exists():
            citizen = citizens.first()
            emails = [
                email.lower()
                for email in (citizen.email, citizen.email_institucional)
                if email
            ]
            if data["email"].lower() not in emails:
                raise ValidationError(
                    {"email": "O email informado não com confere com o cadastrado"}
                )
        else:
            params.update(cpf=data["cpf"])
            citizen = Citizen.objects.create(**params)

        return citizen

    def _get_protocol_params(self, data):
        channel = Channel.objects.get(slug=data.get("channel_slug"))
        set_current_user(channel.workplace.responsavel.user)

        params = {
            "subject": data["subject"],
            "document_type": channel.document_type,
            "interested": data["person"],
            "home_court": channel.workplace,
            "content": data["text"],
            "ip_address": self.request.META.get(
                "HTTP_X_REAL_IP", self.request.META.get("REMOTE_ADDR")
            ),
            "files": self.request.FILES,
        }

        return params


class BaseProtocolRestfulAPI(RestfulDRY):

    _model = Protocolo

    def __attachments(self, qs):
        return [dict(name=a.attach.filename, url=a.attach.permalink()) for a in qs]

    def __movements(self, protocol):
        cap_words = lambda e: e.capitalize() if len(e) > 2 else e.lower()
        return [
            dict(
                sender=" ".join(map(cap_words, mov.lotacao_origem.nome.split(" "))),
                receiver=" ".join(
                    map(
                        cap_words,
                        (mov.destinatario or mov.lotacao_destino).nome.split(" "),
                    )
                ),
                sent_date=(
                    mov.data_encaminhamento.strftime("%d/%m/%Y")
                    if mov.data_encaminhamento
                    else "Sem data de encaminhamento"
                ),
                feedback=mov.parecer,
                attachments=self.__attachments(mov.attachments.all()),
            )
            for mov in protocol.movimentacoes.all()
        ]

    def __lawsuits(self, protocol):
        return [
            {"number": lawsuit.cache_number}
            for lawsuit in protocol.out_court_lawsuits.filter(
                removed_at__isnull=True, parts__signed_by__isnull=False
            ).distinct()
        ]

    def __do_not_allow(self):
        rst = {"success": False, "message": "Operação proibida"}

        self.renderer(rst)

    def do_post(self):
        self.__do_not_allow()

    def do_put(self):
        self.__do_not_allow()

    def do_delete(self):
        self.__do_not_allow()

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update(
            creation_date=instance.data_criacao.strftime("%d/%m/%Y"),
            interested=instance.interessado.nome,
            subject=instance.assunto,
            finished=ProtocoloManager.is_movimentacoes_finalizadas(instance),
            abstract=instance.resumo,
            attachments=self.__attachments(
                instance.movimentacoes.get(passo=0).attachments.all()
            ),
            movements=self.__movements(instance),
            lawsuits=self.__lawsuits(instance),
        )

        return _dict_
