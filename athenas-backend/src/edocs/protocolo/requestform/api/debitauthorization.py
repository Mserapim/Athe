# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import DebitAuthorization
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormDebitAuthorization(EDOCManage):

    _model = DebitAuthorization

    def model_to_dict(self, instance):
        data = super(RequestFormDebitAuthorization, self).model_to_dict(instance)

        debit_percentage = 0
        if instance.protocolo.debitauthorization.debit_percentage is not None:
            debit_percentage = float(
                instance.protocolo.debitauthorization.debit_percentage
            )

        data.update({"debit_percentage": debit_percentage})

        return data
