# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("srdir_notification_opening")
def srdir_notification_opening():
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user
    from corregedoria.cirdir.models import ControlInformation

    count = 0
    msg = ""
    controller = ""
    title = ""

    try:
        employee = employee_from_user(get_current_user())
        list_srdir = ControlInformation.get_all_controlinformation_not_submitted(
            employee=employee
        )

        if employee:
            if employee.tipo in ["M"]:
                title = (
                    "<b>CRGMPE - SRDIR</b><br />SRDIR aberto para preenchimento:<br />"
                )
            else:
                title = "<b>RH - DBVR</b><br />DBVR aberto para preenchimento:<br />"

        for srdir in list_srdir:
            if (
                (
                    srdir.closed_address == False
                    and srdir.check_access_criteria("address")
                )
                or (
                    srdir.closed_teaching_1st_semestry == False
                    and srdir.check_access_criteria("teaching")
                )
                or (
                    srdir.closed_teaching_2nd_semestry == False
                    and srdir.check_access_criteria("teaching")
                )
                or (
                    srdir.closed_property == False
                    and srdir.check_access_criteria("property")
                )
                or (
                    srdir.closed_debits == False
                    and srdir.check_access_criteria("debits")
                )
                or (
                    srdir.closed_health == False
                    and srdir.check_access_criteria("health")
                )
            ):
                if (
                    srdir.closed_address == False
                    and srdir.address_submitted_by is None
                    and srdir.check_access_criteria("address")
                ):
                    msg = msg + "   - <b>Residência (" + str(srdir.year) + ")</b><br />"
                if (
                    srdir.closed_teaching_1st_semestry == False
                    and srdir.teaching_1st_semestry_submitted_by is None
                    and srdir.check_access_criteria("teaching")
                ):
                    msg = (
                        msg
                        + "   - <b>Docência 1º Semestre ("
                        + str(srdir.year)
                        + ")</b><br />"
                    )
                if (
                    srdir.closed_teaching_2nd_semestry == False
                    and srdir.teaching_2nd_semestry_submitted_by is None
                    and srdir.check_access_criteria("teaching")
                ):
                    msg = (
                        msg
                        + "   - <b>Docência 2º Semestre ("
                        + str(srdir.year)
                        + ")</b><br />"
                    )
                if (
                    srdir.closed_property == False
                    and srdir.property_submitted_by is None
                    and srdir.check_access_criteria("property")
                ):
                    msg = (
                        msg
                        + "   - <b>Bens e Direitos ("
                        + str(srdir.year)
                        + ")</b><br />"
                    )
                if (
                    srdir.closed_debits == False
                    and srdir.debits_submitted_by is None
                    and srdir.check_access_criteria("debits")
                ):
                    msg = (
                        msg
                        + "   - <b>Dívidas e Ônus Reais ("
                        + str(srdir.year)
                        + ")</b><br />"
                    )
                if (
                    srdir.closed_health == False
                    and srdir.health_submitted_by is None
                    and srdir.check_access_criteria("health")
                ):
                    msg = msg + "   - <b>Saúde (" + str(srdir.year) + ")</b><br />"
                count += 1
    except Exception as e:
        raise e
    return {
        "title": title + msg,
        "count": count,
        "controller": "CIRDIRControlInformation",
    }


@reg_waiting_work("srdir_health_assessement_notification")
def srdir_health_assessement_notification():
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user
    from corregedoria.cirdir.models import HealthAssessment

    count = 0
    msg = ""
    try:
        employee = employee_from_user(get_current_user())
        health_assessment = HealthAssessment.query_all_recommendation_pending(
            employee=employee
        )

    except Exception as e:
        raise e
    return {
        "title": "<b>CRGMPE - SRDIR</b><br />Seu questionário foi avaliado pelo setor de saúde<br />"
        + msg,
        "count": health_assessment.count(),
        "controller": "CIRDIRControlInformation",
    }
