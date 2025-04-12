from django.db import transaction
from django.template import loader
from django.conf import settings
from django.core.exceptions import ValidationError

from contrib.controller import JsonResponseController
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from edocs.protocolo.channels.models import Channel
from edocs.protocolo.models import (
    Protocolo as Protocol,
    Movimentacao as Movement,
    ProtocoloManager as ProtocolManager,
)
from edocs.protocolo.rpc.forms import CitizenCertificateForm, LegalPersonCertificateForm
from rh.models import PessoaFisica as Citizen, PessoaJuridica as LegalPerson
from datetime import date

log = getLogger()

FORM_FILL_ERROR_MESSAGE = "Preencha corretamente o formulário"
SAVE_SUCCESS_MESSAGE = "Protocolo realizado."
SAVE_FAILURE_MESSAGE = "Não foi possível criar protocolo."


class OnlineCertificate(JsonResponseController):

    def _step_zero(self, protocol):
        return Movement.objects.get(protocolo=protocol, passo=0)

    def _attachments(self, qs):
        return [
            dict(name=a.attach.filename, url=a.attach.no_logged_permalink()) for a in qs
        ]

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

    def _get_base_person_params(self, data):
        return {"nome": data["name"], "email": data["email"]}

    def _get_citizen_params(self, data):
        params = self._get_base_person_params(data)

        return params

    def _create_citizen_person(self, data):
        params = self._get_citizen_params(data)

        citizens = Citizen.objects.filter(cpf=data["cpf"])
        is_diff = False
        registered_emails = []
        if citizens.exists():
            citizen = citizens.first()

            emails = [
                email.lower()
                for email in (citizen.email, citizen.email_institucional)
                if email
            ]

            if data["email"].lower() not in emails or (
                params.get("nome").lower() != citizen.nome.lower()
            ):
                is_diff = True
                registered_emails = emails
        else:
            params.update(cpf=data["cpf"])
            citizen = Citizen.objects.create(**params)

        return citizen, is_diff, registered_emails

    def _get_protocol_params(self, data, workplace, doc_type):

        summary = {
            "registered_name": data["person"],
            "registered_emails": data["registered_emails"],
            "is_diff": data["is_diff"],
            "informed_name": data["name"],
            "informed_email": data["email"],
            "date": date.today().strftime("%d de  %B de %Y"),
        }

        if data.get("cpf"):
            summary.update(cpf=data.get("cpf"))
        elif data.get("cnpj"):
            summary.update(cnpj=data.get("cnpj"))

        template = loader.get_template("protocolo/rpc/online-certificate.html")

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

        protocol = Protocol(**params)
        protocol.save()

        move = protocol.movimentacoes.get(passo=0)

        move.do_send(
            location_destination=[workplace.pk], employee_origin=workplace.responsavel
        )

        return protocol

    def _get_legal_person_params(self, data):
        params = self._get_base_person_params(data)
        params.update(razao_social=data["name"])

        return params

    def _create_legal_person(self, data):
        params = self._get_legal_person_params(data)

        legal_persons = LegalPerson.objects.filter(cnpj=data["cnpj"])

        is_diff = False
        registered_emails = []
        if legal_persons.exists():
            legal_person = legal_persons.first()
            emails = [legal_person.email.lower() if legal_person.email else ""]

            if data["email"].lower() not in emails or (
                params.get("nome").lower() != legal_person.nome.lower()
            ):
                is_diff = True
                registered_emails = emails
        else:
            params.update(cnpj=data["cnpj"])
            legal_person = LegalPerson.objects.create(**params)

        return legal_person, is_diff, registered_emails

    def request_citizen_certificate(self, data):
        response_data = {"success": False}

        form = CitizenCertificateForm(data)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person, is_diff, registered_emails = self._create_citizen_person(
                        form_data
                    )
                    form_data.update(
                        person=person,
                        is_diff=is_diff,
                        registered_emails=registered_emails,
                    )
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

    def citizen_certificate(self, args=[]):
        response_data = self.request_citizen_certificate(self.request.POST)
        self.render(response_data)

    def request_legal_person_certificate(self, data):
        response_data = {"success": False}

        form = LegalPersonCertificateForm(self.request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person, is_diff, registered_emails = self._create_legal_person(
                        form_data
                    )
                    form_data.update(
                        person=person,
                        is_diff=is_diff,
                        registered_emails=registered_emails,
                    )
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

    def legal_person_certificate(self, args=[]):
        response_data = self.request_legal_person_certificate(self.request.POST)
        self.render(response_data)
