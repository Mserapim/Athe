# -*- coding: utf-8 -*-

from django.db import transaction
from django.conf import settings
from django.template import loader
from django.core.exceptions import ValidationError

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from contrib.controller import JsonResponseController
from ged.models import Arquivo as File
from rh.models import PessoaFisica as Citizen
from edocs.protocolo.models import (
    Protocolo as Protocol,
    Attachment,
    ProtocoloManager as ProtocolManager,
    Movimentacao as Movement,
)
from edocs.protocolo.channels.models import Channel

from .forms import LGPDCitizenProtocolForm, CHOICES


FORM_FILL_ERROR_MESSAGE = "Preencha corretamente o formulário"
SAVE_SUCCESS_MESSAGE = "Protocolo realizado."
SAVE_FAILURE_MESSAGE = "Não foi possível criar protocolo."


log = getLogger()


class LGPDProtocol(JsonResponseController):

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

        summary = {
            "name": data.get("name", ""),
            "social_name": data.get("social_name", ""),
            "birth_date": data.get("birth_date").strftime("%d/%m/%Y"),
            "cpf": data.get("cpf", "Não informado"),
            "phone_number": data.get("phone_number", "Não informado"),
            "email": data.get("email", "Não informado"),
            "text": data["text"],
        }

        template = loader.get_template("protocolo/rpc/lgpd-protocol.html")

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

    def _get_base_person_params(self, data):
        return {"nome": data["name"], "email": data["email"]}

    def _get_citizen_params(self, data):
        params = self._get_base_person_params(data)

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

    def create_citizen_protocol(self, data):
        response_data = {"success": False}

        form = LGPDCitizenProtocolForm(data)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_citizen_person(form_data)
                    form_data.update(person=person)
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
