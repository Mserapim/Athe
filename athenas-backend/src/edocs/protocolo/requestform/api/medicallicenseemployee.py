# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import MedicalLicenseEmployee


log = getLogger(__name__)


class RFMedicalLicenseEmployee(EDOCManage):

    _model = MedicalLicenseEmployee

    def model_to_dict(self, instance):
        report = super(RFMedicalLicenseEmployee, self).model_to_dict(instance)
        return report
