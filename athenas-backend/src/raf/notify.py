# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("peding_adjustment_activity")
def raf_notify_appraiser():
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user
    from raf.models import ActivityAdjustment
    from standard.models import Configuration

    cfg = Configuration.get_or_create("raf")
    count = 0
    employee = employee_from_user(get_current_user())
    workerlocations = []
    try:
        if employee:
            location = int(cfg.get("location", 0))
            workerlocations = [p.pk for p in employee.work_locations]
        if (
            get_current_user().has_perm("raf.can_sign_adjustment")
            and location in workerlocations
        ):
            count = ActivityAdjustment.objects.filter(situation__in=[0, 1]).count()
    except Exception:
        pass
    return {
        "title": "RAF - Solicitação de ajuste",
        "count": count,
        "type": "Solicitações" if count > 1 else "Solicitação",
        "controller": "RAFActivityAdjustmentInternalControl",
    }


@reg_waiting_work("raf_analyzed_for_submission")
def raf_notify_analyzed_for_submission():
    from raf.models import FunctionalActivityReport, ActivityAdjustment, DataAdjustment
    from standard.models import Configuration
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user

    employee = employee_from_user(get_current_user())
    try:
        msg = ""
        count = 0
        months = (
            ActivityAdjustment.objects.filter(
                activity__workerlocation__raf__employee=employee,
                activity__workerlocation__raf__submitted_by__isnull=True,
                activity__workerlocation__raf__year__gte=2017,
                situation__in=[2, 3, 4, 6],
            )
            .values("activity__workerlocation__raf")
            .distinct("activity__workerlocation__raf")
            .order_by()
        )
        for m in months:
            raf = FunctionalActivityReport.objects.get(
                pk=m.get("activity__workerlocation__raf")
            )
            adjs = ActivityAdjustment.objects.filter(
                activity__workerlocation__raf=raf,
                activity__workerlocation__raf__submitted_by__isnull=True,
                activity__workerlocation__raf__year__gte=2017,
                situation__in=[0, 1],
            ).count()
            if adjs == 0:
                msg = msg + str(raf.month) + "/" + str(raf.year) + ", "
                count = count + 1
        msg = msg[:-2]
        msg2 = ""
        count2 = 0
        rafs = FunctionalActivityReport.objects.filter(
            employee=employee, submitted_by__isnull=True, year__gte=2017
        ).order_by("year", "month")
        for raf in rafs:
            adjs = ActivityAdjustment.objects.filter(
                activity__workerlocation__raf=raf,
                activity__workerlocation__raf__year__gte=2017,
            ).count()
            if adjs == 0:
                msg2 = msg2 + str(raf.month) + "/" + str(raf.year) + ", "
                count2 = count2 + 1
        msg2 = msg2[:-2]
        msg3 = ""
        count3 = 0
        months = (
            ActivityAdjustment.objects.filter(
                activity__workerlocation__raf__employee=employee,
                activity__workerlocation__raf__submitted_by__isnull=True,
                activity__workerlocation__raf__year__gte=2017,
                situation__in=[0, 1],
            )
            .values("activity__workerlocation__raf")
            .distinct("activity__workerlocation__raf")
            .order_by()
        )
        for m in months:
            raf = FunctionalActivityReport.objects.get(
                pk=m.get("activity__workerlocation__raf")
            )
            adjs = ActivityAdjustment.objects.filter(
                activity__workerlocation__raf=raf,
                activity__workerlocation__raf__submitted_by__isnull=True,
                activity__workerlocation__raf__year__gte=2017,
                situation__in=[0, 1],
            ).count()
            if adjs > 0:
                msg3 = msg3 + str(raf.month) + "/" + str(raf.year) + ", "
                count3 = count3 + 1
        msg3 = msg3[:-2]
        count4 = count + count2 + count3
    except AttributeError:
        count = 0
    return {
        "title": "<b>Relatórios de Atividades Funcionais</b>"
        + ("" if count2 == 0 else "<br/><br/>- Não submetidos:<br/><b>" + msg2 + "</b>")
        + (
            ""
            if count == 0
            else "<br/><br/>- Liberados após análise:<br/><b>" + msg + "</b>"
        )
        + ("" if count3 == 0 else "<br/><br/>- Em análise:<br/><b>" + msg3 + "</b>"),
        "count": count4,
        # 'type': u'meses pendentes' if count4 > 1 else u'mês pendente',
        "controller": "RAFFunctionalActivityReport",
    }


@reg_waiting_work("solicitation_raf")
def solicitation_raf_notify():
    from contrib.middleware import get_current_user
    from raf.models import Solicitation

    try:
        count = 0
        if get_current_user().has_perm("raf.can_management_raf"):
            count = Solicitation.objects.filter(
                status=Solicitation.STATUS_UNVALUED
            ).count()
    except Exception:
        count = 0

    return {
        "title": "RAF - Solicitação",
        "count": count,
        "type": "Abertura de prazo",
        "controller": "RAFSolicitation",
    }
