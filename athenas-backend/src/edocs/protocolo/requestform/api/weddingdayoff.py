# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import WeddingDayOff
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormWeddingDayOff(EDOCManage):

    _model = WeddingDayOff

    def prepare_params(self, querydict):
        params = super(RequestFormWeddingDayOff, self).prepare_params(querydict)

        try:
            params.update(start_date=DateUtils.str_to_date(params.get("start_date")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo Data de início.")

        try:
            params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo Data de término.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormWeddingDayOff, self).model_to_dict(instance)

        form = instance.protocolo.weddingdayoff

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                ),
                "start_date": (
                    DateUtils.date_to_str(form.start_date)
                    if form.start_date is not None
                    else ""
                ),
                "end_date": (
                    DateUtils.date_to_str(form.end_date)
                    if form.end_date is not None
                    else ""
                ),
            }
        )

        return data
