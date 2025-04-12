# -*- coding: utf-8 -*-

from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger
from edocs.protocolo.requestform.models import VacationDaySell
from edocs.protocolo.api.manage import EDOCManage
from rh.ferias.api.pas import FRSEmployeeAcquisitionPeriod


log = getLogger(__name__)


class RequestFormVacationDaySell(EDOCManage):

    _model = VacationDaySell

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("days", ""):
            raise Exception("Por favor, preencha corretamente o campo DIA.")

        return params

    def model_to_dict(self, inst):
        data = super(RequestFormVacationDaySell, self).model_to_dict(inst)
        data.update({"days": inst.protocolo.vacationdaysell.days})
        return data


class RequestFormEmployeeAcquisitionPeriod(FRSEmployeeAcquisitionPeriod):

    def get_query(self):
        employee = employee_from_user(get_current_user())
        return (
            super(RequestFormEmployeeAcquisitionPeriod, self)
            .get_query()
            .filter(servidor=employee)
            .exclude(employee.query_pas_day_sell)
        )
