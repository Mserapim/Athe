# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import CompensateExpense, CompensateExpenseItem

log = getLogger(__name__)


class RequestCompensateExpense(EDOCManage):
    _model = CompensateExpense

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("finality", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Finalidade'.")

        try:
            params.update(output_date=DateUtils.str_to_date(params.get("output_date")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo 'Data de saída.'")

        try:
            params.update(return_date=DateUtils.str_to_date(params.get("return_date")))
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Data de retorno.'"
            )

        if not params.get("total_compensate", ""):
            raise Exception(
                "Por favor, preencha corretamente o campo 'Total a ressarcir'."
            )

        if not params.get("material", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Material'.")

        if not params.get("service", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Serviço'.")

        if not params.get("combustible", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Combustível'.")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        report = instance.protocolo.compensateexpense

        data.update(
            {
                "finality": report.finality or "",
                "output_date": (
                    DateUtils.date_to_str(report.output_date)
                    if report.output_date
                    else ""
                ),
                "return_date": (
                    DateUtils.date_to_str(report.return_date)
                    if report.return_date
                    else ""
                ),
                "total_compensate": float(report.total_compensate or 0),
                "material": report.material or "",
                "service": report.service or "",
                "combustible": float(report.combustible or 0),
                "note": report.note or "Não informado",
            }
        )

        return data


class RequestCompensateExpenseItem(RestfulDRY):

    _model = CompensateExpenseItem

    def get_params(self, querydict=None, **kargs):
        params = super().get_params(querydict, **kargs)

        if not params.get("nota", ""):
            params.update(nota="")

        if not params.get("company", ""):
            params.update(company="")

        if not params.get("value", ""):
            params.update(value=0)

        return params
