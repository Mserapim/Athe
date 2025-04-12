# -*- coding: utf-8 -*-

import json

from django.db import transaction
from django.template import loader
from django.core.exceptions import ValidationError

import datetime
from contrib.controller import JsonResponseController
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from edocs.protocolo.channels.models import Channel
from edocs.protocolo.models import Attachment
from edocs.protocolo.models import Protocolo as Protocol
from ged.models import Arquivo as File
from rh.const import RACA_COR_CHOICES, SEXO_CHOICES
from rh.models import Estado as State
from rh.models import PessoaFisica as Citizen

from .forms import (
    PLIDBaseForm,
    PLIDCommunicatorQualificationForm,
    PLIDOccorrenceDataForm,
    PLIDVictimCharacteristicsForm,
    PLIDVictimQualificationForm,
)

FORM_FILL_ERROR_MESSAGE = "Preencha corretamente o formulário"
SAVE_SUCCESS_MESSAGE = "Registro de desaparecimento enviado com sucesso."
SAVE_FAILURE_MESSAGE = "Não foi possível criar protocolo."


log = getLogger()

CHOICES = {
    "SUBJECT": (
        ("", "----------------------"),
        ("Comentário", "Comentário"),
        ("Crítica", "Crítica"),
        ("Denúncia", "Denúncia"),
        ("Elogio", "Elogio"),
        ("Pedido de Informação", "Pedido de Informação"),
        ("Reclamação", "Reclamação"),
        ("Sugestão", "Sugestão"),
        ("Protocolo Online", "Protocolo Online"),
    ),
    "SKIN_COLOR": RACA_COR_CHOICES,
    "EYE_COLOR": (
        ("", "Não Informado"),
        ("Azul", "Azul"),
        ("Castanho claro", "Castanho claro"),
        ("Castanho escuro", "Castanho escuro"),
        ("Cinzentos", "Cinzentos"),
        ("Pretos", "Pretos"),
        ("Verdes", "Verdes"),
        ("Desiguais na cor", "Desiguais na cor"),
        ("Outros", "Outros"),
    ),
    "HAIR_TYPE": (
        ("Calvo", "Calvo"),
        ("Encaracolado", "Encaracolado"),
        ("Liso", "Liso"),
        ("Ondulado", "Ondulado"),
        ("Raspado", "Raspado"),
    ),
    "HAIR_COLOR": (
        ("Castanho claro", "Castanho claro"),
        ("Castanho escuro", "Castanho escuro"),
        ("Grisalho", "Grisalho"),
        ("Loiro", "Loiro"),
        ("Preto", "Preto"),
        ("Ruivo", "Ruivo"),
    ),
    "GENRE": SEXO_CHOICES,
    "STATE": list(
        State.objects.filter(pais__pk=1).order_by("nome").values_list("id", "nome")
    ),
}


class PLIDProtocol(JsonResponseController):

    def form_choices(self, args=[]):
        self.render({"success": True, "choices": CHOICES})

    def _get_params(self, data):
        params = data.copy()

        for key, value in list(data.items()):
            if not value:
                params.update({key: "Não Informado"})
            else:
                if isinstance(value, datetime.date):
                    params.update({key: value.strftime("%d/%m/%Y")})
                if key == "genre":
                    params.update({key: dict(CHOICES["GENRE"]).get(data.get("genre"))})
                if key == "skin_color":
                    params.update(
                        {
                            key: dict(CHOICES["SKIN_COLOR"]).get(
                                int(data.get("skin_color"))
                            )
                        }
                    )

        return params

    def _get_protocol_params(self, data, workplace, doc_type):

        summary = {
            "odf": self._get_params(data.get("odf")),
            "vqf": self._get_params(data.get("vqf")),
            "vcf": self._get_params(data.get("vcf")),
            "cqf": self._get_params(data.get("cqf")),
        }

        template = loader.get_template("protocolo/rpc/plid-protocol.html")

        params = {
            "interessado": data["person"],
            "assunto": data["base"].get("subject"),
            "orgao_geral_origem": workplace.orgaogeral_ptr,
            "servidor_origem": workplace.responsavel,
            "tipo_documento": doc_type,
            "resumo": template.render(summary),
        }

        return params

    def _create_protocol(self, data):

        channel = Channel.objects.get(slug=data["base"].get("channel_slug"))
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

    def _get_citizen_params(self, data):
        return {
            "nome": data["name"],
            "email": data["email"],
            "sexo": data["genre"],
        }

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

    def _create_disappeared_person(self, data):
        response_data = {"success": False}

        base = PLIDBaseForm(json.loads(self.request.POST.get("base")))
        odf = PLIDOccorrenceDataForm(json.loads(self.request.POST.get("odf")))
        vqf = PLIDVictimQualificationForm(json.loads(self.request.POST.get("vqf")))
        vcf = PLIDVictimCharacteristicsForm(json.loads(self.request.POST.get("vcf")))
        cqf = PLIDCommunicatorQualificationForm(
            json.loads(self.request.POST.get("cqf"))
        )

        if (
            base.is_valid()
            and odf.is_valid()
            and vqf.is_valid()
            and vcf.is_valid()
            and cqf.is_valid()
        ):

            base = base.cleaned_data
            odf = odf.cleaned_data
            vqf = vqf.cleaned_data
            vcf = vcf.cleaned_data
            cqf = cqf.cleaned_data

            form_data = {"base": base, "odf": odf, "vqf": vqf, "vcf": vcf, "cqf": cqf}

            try:
                with transaction.atomic():
                    person = self._create_citizen_person(cqf)
                    form_data.update(person=person)
                    protocol = self._create_protocol(form_data)

            except Exception as e:
                response_data["message"] = str(e)
                self.log.exception(
                    "ERRO EM PLID: %s. Exception => %s." % (SAVE_FAILURE_MESSAGE, e)
                )
            else:
                response_data.update(
                    success=True, message=SAVE_SUCCESS_MESSAGE, protocol=protocol.codigo
                )
        else:
            errors = {}
            errors.update(base.errors)
            errors.update(odf.errors)
            errors.update(vqf.errors)
            errors.update(vcf.errors)
            errors.update(cqf.errors)
            response_data.update(message=FORM_FILL_ERROR_MESSAGE, errors=errors)

        return response_data

    def create_disappeared_person(self, args=[]):
        response_data = self._create_disappeared_person(self.request.POST)
        self.render(response_data)
