from django.core.exceptions import ValidationError
from django.db import transaction

from edocs.protocolo.apiprotocol.api.baseprotocol import (
    BaseProtocolAPI,
    BaseProtocolRestfulAPI,
)
from edocs.protocolo.apiprotocol.forms import (
    ONLINE_PROTOCOL_CHOICES,
    CitizenProtocolForm,
    LegalPersonProtocolForm,
)
from edocs.protocolo.apiprotocol.models import (
    OnlineProtocolCitizen,
    OnlineProtocolLegalPerson,
)


class POPCitizenAPI(BaseProtocolAPI):

    _model = OnlineProtocolCitizen

    def _get_protocol_params(self, data):
        params = super()._get_protocol_params(data)
        params.update(
            {
                "live_in_referenced_city": data["live_in_referenced_city"],
                "referenced_city": data["referenced_city"],
                "subject_detail": data["subject_detail"],
                "document_number": data["document_number"],
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


class POPLegalPersonAPI(BaseProtocolAPI):

    _model = OnlineProtocolLegalPerson

    def _get_protocol_params(self, data):
        params = super()._get_protocol_params(data)
        params.update(
            {
                "subject_detail": data["subject_detail"],
                "document_number": data["document_number"],
            }
        )

        return params

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


class POPRestfulAPI(BaseProtocolRestfulAPI):
    def fetch_choices(self, args=[]):
        rst = {
            "success": False,
            "message": "Ainda não foi processado!",
            "collection": {},
        }

        choices = ONLINE_PROTOCOL_CHOICES
        rst.update(
            {
                "success": True,
                "message": "Processado com sucesso",
                "collection": choices,
            }
        )

        self.renderer(rst)
