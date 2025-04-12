# -*- coding: utf-8 -*-

from django.db import transaction
from django.conf import settings
from django.template import loader
from django.core.exceptions import ValidationError


from contrib.middleware import set_current_user
from contrib.helpers import clean_text
from contrib.utils import getLogger
from contrib.controller import JsonResponseController
from ged.models import Arquivo as File
from rh.models import (
    Endereco as Address,
    PessoaFisica as Citizen,
    PessoaJuridica as LegalPerson,
    Telefone as Phone,
)
from edocs.protocolo.models import (
    Protocolo as Protocol,
    Attachment,
    ProtocoloManager as ProtocolManager,
    Movimentacao as Movement,
)
from edocs.protocolo.channels.models import Channel
from rh.models import (
    Endereco as Address,
    PessoaFisica as Citizen,
    PessoaJuridica as LegalPerson,
    Localidade as City,
    Telefone as Phone,
)
from edocs.protocolo.models import (
    Protocolo as Protocol,
    Attachment,
    ProtocoloManager as ProtocolManager,
    Movimentacao as Movement,
)
from .forms import (
    AnonymousProtocolForm,
    CitizenProtocolForm,
    LegalPersonProtocolForm,
    CHOICES,
)


FORM_FILL_ERROR_MESSAGE = "Preencha corretamente o formulário"
SAVE_SUCCESS_MESSAGE = "Protocolo realizado."
SAVE_FAILURE_MESSAGE = "Não foi possível criar protocolo."


log = getLogger()


class OnlineProtocol(JsonResponseController):

    def form_choices(self, args=[]):
        self.render({"success": True, "choices": CHOICES})

    def _protocol_moves(self, protocol):
        protocol._finished = False

        moves_qs = Movement.objects.filter(protocolo=protocol, passo__gt=0).order_by(
            "-data_encaminhamento"
        )

        moves = []
        for move in moves_qs:
            if ProtocolManager.is_finalizado(move):
                protocol._finished = True

            _from = move.lotacao_origem
            to = move.destinatario or move.lotacao_destino
            sent_date = move.data_encaminhamento

            feedback = ""
            for term in [
                "<!-- Correção de bug da ExtJS -->",
                "<br>",
                "<br/>",
                "<BR>",
                "<BR/>",
            ]:
                if move.parecer:
                    feedback = move.parecer.replace(term, "")

            cap_words = lambda e: e.capitalize() if len(e) > 2 else e.lower()
            moves.append(
                {
                    "from": " ".join(map(cap_words, _from.nome.split(" "))),
                    "to": " ".join(map(cap_words, to.nome.split(" "))),
                    "sent_date": (
                        sent_date.strftime("%d/%m/%Y")
                        if sent_date
                        else "Sem data de encaminhamento"
                    ),
                    "feedback": feedback,
                    "attachs": self._attachments(move.attachments.all()),
                }
            )

        return moves

    def _attachments(self, qs):
        return [
            dict(name=a.attach.filename, url=a.attach.no_logged_permalink()) for a in qs
        ]

    def _lawsuits(self, protocol):
        lawsuits = []
        web_domain_context = getattr(settings, "WEB", "")
        qs = protocol.out_court_lawsuits.filter(
            removed_at__isnull=True, parts__signed_by__isnull=False
        ).distinct()

        for lawsuit in qs:
            lawsuits.append(
                {
                    "number": lawsuit.cache_number,
                    "url": "%s/cidadao/ejud-search?number=%s&filter=yes"
                    % (web_domain_context, lawsuit.cache_number),
                }
            )

        return lawsuits

    def _step_zero(self, protocol):
        return Movement.objects.get(protocolo=protocol, passo=0)

    def _protocol2dict(self, protocol):

        return {
            "code": protocol.codigo,
            "seal": protocol.chancela,
            "sent_by": str(protocol.interessado),
            "create_date": protocol.data_criacao,
            "subject": protocol.assunto,
            "text": protocol.resumo,
            "secrecy": protocol.sigiloso,
            "lawsuits": self._lawsuits(protocol),
            "moves": self._protocol_moves(protocol),
            "attachs": self._attachments(self._step_zero(protocol).attachments.all()),
            "finished": ProtocolManager.is_movimentacoes_finalizadas(protocol),
        }

    def search(self, args=[]):
        response_data = {"success": False}
        if args:
            params = {"seal": "chancela", "code": "codigo"}
            by = self.request.GET.get("by", "code")
            query_params = {params.get(by): args[0]}
            protocol = Protocol.objects.filter(**query_params).first()
            if protocol:
                response_data = {
                    "success": True,
                    "protocol": self._protocol2dict(protocol),
                }
        self.render(response_data)

    def _get_protocol_params(self, data, workplace, doc_type):
        live_in_referenced_city = "Não informado"
        if data.get("live_in_referenced_city"):
            live_in_referenced_city = dict(CHOICES["YESNO"]).get(
                int(data.get("live_in_referenced_city"))
            )

        referenced_city = data.get("city", "Não informado")
        if data.get("live_in_referenced_city") == "2":
            referenced_city = data.get("referenced_city", "Não informado")

        summary = {
            "zipcode": data.get("zipcode", "Não informado"),
            "phone_number": data.get("phone_number", "Não informado"),
            "genre": dict(CHOICES["GENRE"]).get(data.get("genre"), "Não informado"),
            "school": dict(CHOICES["SCHOOL"]).get(
                int(data.get("school", 0)), "Não informado"
            ),
            "city": data.get("city", "Não informado"),
            "live_in_referenced_city": live_in_referenced_city,
            "referenced_city": referenced_city,
            "text": data["text"],
            "subject_detail": data.get("subject_detail", "Não informado"),
            "document_number": data.get("document_number", "Não informado"),
        }

        if data.get("cpf"):
            summary.update(cpf=data.get("cpf"))
        elif data.get("cnpj"):
            summary.update(cnpj=data.get("cnpj"))

        template = loader.get_template("protocolo/rpc/online-protocol.html")

        params = {
            "interessado": data["person"],
            "assunto": data["subject"],
            "orgao_geral_origem": workplace.orgaogeral_ptr,
            "servidor_origem": workplace.responsavel,
            "tipo_documento": doc_type,
            "resumo": template.render(summary),
        }

        return params

    def _create_protocol(self, data):
        channel = Channel.objects.get(slug=data.get("channel_slug"))
        workplace = channel.workplace
        doc_type = channel.document_type
        params = self._get_protocol_params(data, workplace, doc_type)

        set_current_user(workplace.responsavel.user)

        self.log.info("Creating protocol")
        protocol = Protocol(**params)
        protocol.save()

        self.log.info("getting step zero")
        move = protocol.movimentacoes.get(passo=0)

        self.log.info("Checking and saving uploaded files")
        for name, upfile in self.request.FILES.items():
            title = self.request.POST.get("file_%s" % name.split("_")[-1], upfile.name)

            Attachment.objects.create(
                title=title,
                protocol=protocol,
                moviment=move,
                attach=File.create_ged(upfile),
            )

        self.log.info("Making movement")
        move.do_send(
            location_destination=[workplace.pk], employee_origin=workplace.responsavel
        )

        self.log.info("Returning protocol")
        return protocol

    def _get_phone_params(self, data):
        return {
            "tipo_telefone": data["phone_type"],
            "numero": clean_text(data["phone_number"]),
        }

    def _create_phone(self, data):
        params = self._get_phone_params(data)
        phone = None
        if data["phone_type"] and data["phone_number"]:
            phone, created = Phone.objects.get_or_create(
                numero=clean_text(data["number"]),
                person=data["person"],
                defaults=params,
            )
        return phone

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
        params.update(person=data["person"])

        try:
            filter_params = params.copy()
            filter_params.update(person=data["person"].pk, municipio=data["city"].pk)

            addresses = Address.objects.filter(**filter_params)

            if not addresses.exists():
                Address.objects.create(**params)

        except Exception as e:
            log.exception(e)
            raise Exception("Não foi possível criar o endereço.")

        else:
            return True

    def _get_base_person_params(self, data):
        return {"nome": data["name"], "email": data["email"]}

    def _get_legal_person_params(self, data):
        params = self._get_base_person_params(data)
        params.update(razao_social=data["name"])
        return params

    def _create_legal_person(self, data):
        params = self._get_legal_person_params(data)

        legal_persons = LegalPerson.objects.filter(cnpj=data["cnpj"])

        if not legal_persons.exists():
            params.update(cnpj=data["cnpj"])
            legal_person = LegalPerson.objects.create(**params)
        else:
            legal_person = legal_persons.first()

        return legal_person

    def _get_citizen_params(self, data):
        params = self._get_base_person_params(data)
        params.update(
            {
                "sexo": data["genre"],
                "grau_instrucao": data["school"],
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

    def load_personal_data(self, args=[]):
        cpf = self.request.GET.get("cpf")
        cnpj = self.request.GET.get("cnpj")

        response_data = {"success": False}
        data = {}
        person = None

        if cpf:
            person = Citizen.objects.filter(cpf=cpf).first()
            if person:
                data.update(
                    genre=person.sexo,
                    school=person.grau_instrucao,
                    marital_status=person.estado_civil,
                    race=person.raca_cor,
                )

        elif cnpj:
            person = LegalPerson.objects.filter(cnpj=cnpj).first()

        if person:
            data.update(name=person.nome, email=person.email)

            address = person.address.last()
            if address:
                data.update(
                    address_type=address.tipo_endereco,
                    public_place_type=address.tipo_logradouro,
                    zipcode=address.cep,
                    public_place=address.logradouro,
                    extra=address.complemento,
                    neighborhood=address.bairro,
                    number=address.numero,
                    city=address.municipio.pk,
                )

            phone = person.phone.last()
            if phone:
                data.update(phone_type=phone.tipo_telefone, phone_number=phone.numero)

            response_data.update(success=True, data=data)

        self.render(response_data)

    def load_cities(self, args=[]):
        state = self.request.GET.get("state")

        response_data = {"success": False}
        data = {}
        cities_by_state = {}

        if state:
            cities_by_state = (
                City.objects.filter(estado__id=state)
                .order_by("nome")
                .values_list("id", "nome")
            )
            if cities_by_state:
                data.update(cities=list(cities_by_state))

            response_data.update(success=True, data=data)

        self.render(response_data)

    def create_anonymous_protocol(self, data):
        response_data = {"success": False}

        form = AnonymousProtocolForm(data)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    protocol = self._create_protocol(form_data)
            except Exception as e:
                response_data["message"] = SAVE_FAILURE_MESSAGE
                self.log.exception(
                    "ERRO EM OUVIDORIA: %s. Exception => %s."
                    % (SAVE_FAILURE_MESSAGE, e)
                )
            else:
                response_data.update(
                    success=True, message=SAVE_SUCCESS_MESSAGE, protocol=protocol.codigo
                )
        else:
            response_data.update(
                message=FORM_FILL_ERROR_MESSAGE, errors=dict(form.errors)
            )
        return response_data

    def anonymous_protocol(self, args=[]):
        response_data = self.create_anonymous_protocol(self.request.POST)
        self.render(response_data)

    def create_citizen_protocol(self, data):
        response_data = {"success": False}

        form = CitizenProtocolForm(data)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_citizen_person(form_data)
                    form_data.update(person=person)
                    self._create_address(form_data)
                    self._create_phone(form_data)
                    protocol = self._create_protocol(form_data)
            except Exception as e:
                response_data["message"] = str(e)
                self.log.exception(
                    "ERRO EM PROTOCOLO ONLINE: %s. Exception => %s."
                    % (SAVE_FAILURE_MESSAGE, e)
                )
            else:
                response_data.update(
                    success=True, message=SAVE_SUCCESS_MESSAGE, protocol=protocol.codigo
                )
        else:
            response_data.update(
                message=FORM_FILL_ERROR_MESSAGE, errors=dict(form.errors)
            )
        return response_data

    def citizen_protocol(self, args=[]):
        response_data = self.create_citizen_protocol(self.request.POST)
        self.render(response_data)

    def create_legal_person_protocol(self, data):
        response_data = {"success": False}

        form = LegalPersonProtocolForm(self.request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_legal_person(form_data)
                    form_data.update(person=person)
                    self._create_address(form_data)
                    self._create_phone(form_data)
                    protocol = self._create_protocol(form_data)

            except Exception as e:
                response_data["message"] = str(e)
                self.log.exception(
                    "ERRO EM OUVIDORIA: %s. Exception => %s."
                    % (SAVE_FAILURE_MESSAGE, e)
                )
            else:
                response_data.update(
                    success=True, message=SAVE_SUCCESS_MESSAGE, protocol=protocol.codigo
                )
        else:
            response_data.update(
                message=FORM_FILL_ERROR_MESSAGE, errors=dict(form.errors)
            )

        return response_data

    def legal_person_protocol(self, args=[]):
        response_data = self.create_legal_person_protocol(self.request.POST)
        self.render(response_data)
