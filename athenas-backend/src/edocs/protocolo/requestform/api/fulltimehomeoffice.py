# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import FullTimeHomeOffice
from edocs.protocolo.api.manage import EDOCManage
from rh.models import Servidor as Employee


log = getLogger(__name__)


class RequestFormFullTimeHomeOffice(EDOCManage):

    _model = FullTimeHomeOffice

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        try:
            params.update(start_date=DateUtils.str_to_date(params.get("start_date")))
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Início do período de teletrabalho'."
            )

        params.update(elderly=params.get("elderly", "off") == "on")
        params.update(pregnant=params.get("pregnant", "off") == "on")
        params.update(chronic_diseases=params.get("chronic_diseases", "off") == "on")
        params.update(
            pneumopathy_diseases=params.get("pneumopathy_diseases", "off") == "on"
        )
        params.update(kidney_diseases=params.get("kidney_diseases", "off") == "on")
        params.update(
            cardiovascular_diseases=params.get("cardiovascular_diseases", "off") == "on"
        )
        params.update(obese=params.get("obese", "off") == "on")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        obj = instance.protocolo.fulltimehomeoffice

        data.update(
            {
                "start_date": (
                    DateUtils.date_to_str(obj.start_date) if obj.start_date else ""
                ),
                "boss": obj.boss.pk if obj.boss else "",
                "elderly": obj.elderly,
                "pregnant": obj.pregnant,
                "chronic_diseases": obj.chronic_diseases,
                "pneumopathy_diseases": obj.pneumopathy_diseases,
                "kidney_diseases": obj.kidney_diseases,
                "cardiovascular_diseases": obj.cardiovascular_diseases,
                "obese": obj.obese,
            }
        )

        return data
