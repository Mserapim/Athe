# -*- coding: utf-8 -*-

from contrib.utils import DateUtils, getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import Evaluation
from rh.models import Employee


log = getLogger(__name__)


class RequestFormEvaluation(EDOCManage):

    _model = Evaluation

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        try:
            params.update(employee=Employee.objects.get(pk=params.get("employee")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo 'Servidor'.")

        if not params.get("cumpliance_activities_goals", ""):
            raise Exception(
                "Por favor, preencha corretamente o campo 'Cumprimento das atividades e metas'."
            )

        try:
            params.update(
                employee_date_established=int(
                    params.get("employee_date_established", "")
                )
            )
        except Exception:
            raise Exception("Por favor, preencha o campo corretamente.")

        try:
            params.update(
                employee_working_established=int(
                    params.get("employee_working_established", "")
                )
            )
        except Exception:
            raise Exception("Por favor, preencha o campo corretamente.")

        try:
            params.update(employee_available=int(params.get("employee_available", "")))
        except Exception:
            raise Exception("Por favor, preencha o campo corretamente.")

        try:
            params.update(
                employee_addaption_working=int(
                    params.get("employee_addaption_working", "")
                )
            )
        except Exception:
            raise Exception("Por favor, preencha o campo corretamente.")

        try:
            params.update(
                employee_disobey_working=int(params.get("employee_disobey_working", ""))
            )
        except Exception:
            raise Exception("Por favor, preencha o campo corretamente.")

        # params.update(employee_date_established=params.get('employee_date_established', 'off') == 'on')
        # params.update(employee_working_established=params.get('employee_working_established', 'off') == 'on')
        # params.update(employee_available=params.get('employee_available', 'off') == 'on')
        # params.update(employee_addaption_working=params.get('employee_addaption_working', 'off') == 'on')
        # params.update(employee_disobey_working=params.get('employee_disobey_working', 'off') == 'on')

        if not params.get("ask_affirmation_working", "") and params.get(
            "employee_disobey_working", ""
        ):
            raise Exception(
                "Por favor, preencha corretamente o campo 'Em caso afirmativo da pergunta acima, elencar quais deveres foram descumpridos:'."
            )

        # if not params.get('note', ''):
        #     raise Exception("Por favor, preencha corretamente o campo 'Observações'.")

        try:
            params.update(start_date=DateUtils.str_to_date(params.get("start_date")))
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Data de inicio.'"
            )

        try:
            params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
        except Exception:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Data de término.'"
            )

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        questionnaire = instance.protocolo.evaluation

        data.update(
            {
                "employee": questionnaire.employee.pk if questionnaire.employee else 0,
                "cumpliance_activities_goals": questionnaire.cumpliance_activities_goals
                or "",
                "employee_date_established": (
                    questionnaire.employee_date_established
                    if questionnaire.employee_date_established is not None
                    else ""
                ),
                "employee_working_established": (
                    questionnaire.employee_working_established
                    if questionnaire.employee_date_established is not None
                    else ""
                ),
                "employee_available": (
                    questionnaire.employee_available
                    if questionnaire.employee_available is not None
                    else ""
                ),
                "employee_addaption_working": (
                    questionnaire.employee_addaption_working
                    if questionnaire.employee_addaption_working is not None
                    else ""
                ),
                "employee_disobey_working": (
                    questionnaire.employee_disobey_working
                    if questionnaire.employee_disobey_working is not None
                    else ""
                ),
                "ask_affirmation_working": questionnaire.ask_affirmation_working or "",
                "note": questionnaire.note or "",
                "start_date": (
                    DateUtils.date_to_str(questionnaire.start_date)
                    if questionnaire.start_date is not None
                    else ""
                ),
                "end_date": (
                    DateUtils.date_to_str(questionnaire.end_date)
                    if questionnaire.end_date is not None
                    else ""
                ),
            }
        )

        return data
