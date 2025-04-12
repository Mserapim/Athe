# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import MedicalLicenseFamiliar


log = getLogger(__name__)


class RFMedicalLicenseFamiliar(EDOCManage):

    _model = MedicalLicenseFamiliar

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("grade_familiar", ""):
            raise Exception("Por favor, preencha corretamente o PARENTESCO.")

        return params

    def model_to_dict(self, instance):
        report = super(RFMedicalLicenseFamiliar, self).model_to_dict(instance)

        form = instance.protocolo.medicallicensefamiliar

        report.update({"grade_familiar": form.grade_familiar or ""})
        return report
