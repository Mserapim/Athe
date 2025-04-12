from django.core.exceptions import ValidationError
from django.db import transaction

from edocs.protocolo.apiprotocol.api.baseprotocol import (
    BaseProtocolAPI,
    BaseProtocolRestfulAPI,
)
from edocs.protocolo.apiprotocol.forms import (
    CitizenCertificateForm,
    LegalPersonCertificateForm,
)
from edocs.protocolo.apiprotocol.models import (
    OnlineCertificateCitizen,
    OnlineCertificateLegalPerson,
)


class POCCitizenAPI(BaseProtocolAPI):

    _model = OnlineCertificateCitizen

    def _get_citizen_params(self, data):
        params = self._get_base_person_params(data)

        return params

    def prepare_params(self, querydict):
        params = {}

        form = CitizenCertificateForm(querydict)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_citizen_person(form_data)
                    form_data.update(person=person)
                    params = self._get_protocol_params(form_data)
            except Exception as e:
                self.log.exception(f"ERRO EM CERTIDÃO ONLINE. Exception => {e}.")
                raise e
        else:
            raise ValidationError(dict(form.errors))

        return params


class POCLegalPersonAPI(BaseProtocolAPI):

    _model = OnlineCertificateLegalPerson

    def _get_legal_person_params(self, data):
        params = self._get_base_person_params(data)

        return params

    def prepare_params(self, querydict):
        params = {}

        form = LegalPersonCertificateForm(querydict)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with transaction.atomic():
                    person = self._create_legal_person(form_data)
                    form_data.update(person=person)
                    params = self._get_protocol_params(form_data)
            except Exception as e:
                self.log.exception(f"ERRO EM CERTIDÃO ONLINE. Exception => {e}.")
                raise e
        else:
            raise ValidationError(dict(form.errors))

        return params


class POCRestfulAPI(BaseProtocolRestfulAPI):
    pass
