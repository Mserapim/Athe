# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("cnmp_status_send_information")
def cnmp_status_send_information():
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user
    from corregedoria.cnmp.models import Communication

    count = 0
    pendding = 0
    warning = 0
    error = 0
    fail = 0
    msg = ""
    try:

        # todo admin do athenas vai possuir as permissoes adicionadas no models.
        # deveria haver subniveis, seguimentar essas permissoes.
        employee = employee_from_user(get_current_user())
        if employee:
            location = employee.work_locations.filter(pk=457)
            if employee.user.has_perm("cnmp.is_administrator") and location.exists():
                pendding = Communication.objects.filter(status=1).count()
                warning = Communication.objects.filter(status=3).count()
                error = Communication.objects.filter(status=4).count()
                fail = Communication.objects.filter(status=5).count()

                msg = "<b>SCMMP</b>"

                if pendding > 0:
                    count += 1
                    msg = (
                        msg
                        + "<br/><br/>- Envios pendentes:<br/><b>"
                        + str(pendding)
                        + "</b>"
                    )
                if warning > 0:
                    count += 1
                    msg = (
                        msg
                        + "<br/><br/>- Envios com apontamentos :<br/><b>"
                        + str(warning)
                        + "</b>"
                    )
                if error > 0:
                    count += 1
                    msg = (
                        msg
                        + "<br/><br/>- Envios com erros:<br/><b>"
                        + str(error)
                        + "</b>"
                    )
                if fail > 0:
                    count += 1
                    msg = (
                        msg
                        + "<br/><br/>- Envios que falharam:<br/><b>"
                        + str(fail)
                        + "</b>"
                    )

    except Exception as e:
        raise e
    return {"title": msg, "count": count, "controller": "CNMPManage"}
