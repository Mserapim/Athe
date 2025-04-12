# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db import transaction

from contrib.utils import getLogger
from edocs.protocolo.apiprotocol.api.baseprotocol import (
    BaseProtocolAPI,
    BaseProtocolRestfulAPI,
)
from edocs.protocolo.apiprotocol.forms import (
    OMBUDSMAN_CHOICES,
    AnonymousProtocolForm,
    CitizenProtocolForm,
    LegalPersonProtocolForm,
)
from edocs.protocolo.apiprotocol.models import (
    OmbudsmanAnonymous,
    OmbudsmanCitizen,
    OmbudsmanLegalPerson,
)

log = getLogger(__name__)


class POOAnonymousAPI(BaseProtocolAPI):

    _model = OmbudsmanAnonymous

    def prepare_params(self, querydict):
        params = {}

        form = AnonymousProtocolForm(querydict)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    params = self._get_protocol_params(form_data)
            except Exception as e:
                self.log.exception(f"ERRO EM OUVIDORIA. Exception => {e}.")
                raise e
        else:
            raise ValidationError(
                "Preencha corretamente o formulário",
                code="invalid",
                params=dict(form.errors),
            )

        return params


class POOCitizenAPI(BaseProtocolAPI):

    _model = OmbudsmanCitizen

    def _get_protocol_params(self, data):
        params = super()._get_protocol_params(data)
        params.update(
            {
                "live_in_referenced_city": data["live_in_referenced_city"],
                "referenced_city": data["referenced_city"],
            }
        )

        return params

    def prepare_params(self, querydict):
        params = {}

        form = CitizenProtocolForm(querydict)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_citizen_person(form_data)
                    form_data.update(person=person)
                    self._create_address(form_data)
                    self._create_phone(form_data)
                    params = self._get_protocol_params(form_data)
            except Exception as e:
                self.log.exception(f"ERRO EM OUVIDORIA. Exception => {e}.")
                raise e
        else:
            raise ValidationError(
                "Preencha corretamente o formulário",
                code="invalid",
                params=dict(form.errors),
            )

        return params


class POOLegalPersonAPI(BaseProtocolAPI):

    _model = OmbudsmanLegalPerson

    def prepare_params(self, querydict):
        params = {}

        form = LegalPersonProtocolForm(querydict)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_legal_person(form_data)
                    form_data.update(person=person)
                    self._create_address(form_data)
                    self._create_phone(form_data)
                    params = self._get_protocol_params(form_data)
            except Exception as e:
                self.log.exception(f"ERRO EM OUVIDORIA. Exception => {e}.")
                raise e
        else:
            raise ValidationError(
                "Preencha corretamente o formulário",
                code="invalid",
                params=dict(form.errors),
            )

        return params


class POORestfulAPI(BaseProtocolRestfulAPI):
    def fetch_choices(self, args=[]):
        rst = {
            "success": False,
            "message": "Ainda não foi processado!",
            "collection": {},
        }

        choices = OMBUDSMAN_CHOICES
        rst.update(
            {
                "success": True,
                "message": "Processado com sucesso",
                "collection": choices,
            }
        )

        self.renderer(rst)
