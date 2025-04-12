# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work

from contrib.utils import getLogger

log = getLogger(__name__)


@reg_waiting_work("inspection_recommendations_delayoftime")
def inspection_recommendations_delayoftime():
    try:
        from contrib.utils import employee_from_user
        from contrib.middleware import get_current_user
        from datetime import date
        from corregedoria.inspection.models import Recommendations

        employee = employee_from_user(get_current_user())
        count = Recommendations.objects.filter(
            finalized=False,
            waiting_response=True,
            inspection__employee=employee,
            deadline__lt=date.today(),
        ).count()

    except Exception:
        log.debug("Falha na notificação: Inspection Recomendation")
    else:
        return {
            "title": "CRGMPE - Gestor de Inspeções<br /> - <b>Recomendações em atraso</b>",
            "count": count,
            "controller": "INSPECTIONFollowRecommendation",
        }


@reg_waiting_work("inspection_notification_deadline")
def inspection_notification_deadline():
    try:
        from contrib.utils import employee_from_user
        from contrib.middleware import get_current_user
        from corregedoria.inspection.models import Inspection
        from datetime import date

        count = 0
        user = get_current_user()
        employee = employee_from_user(user)

        if user and employee:
            has_perm = user.has_perm("inspection.notification_deadline_monitor")
            in_location = employee.work_locations.filter(pk=457).exists()

            if in_location and has_perm:
                count = Inspection.objects.filter(
                    notificationhistory__deadline__lt=date.today(),
                    notificationhistory__responded=False,
                ).count()

    except Exception:
        log.debug("Falha na notificação: Inspection Notification")
    else:
        return {
            "title": "CRGMPE - Gestor de Inspeções<br /> - <b>Notificações Vencidas</b>",
            "count": count,
            "controller": "INSPECTIONFollowRecommendationCorregedoria",
        }
