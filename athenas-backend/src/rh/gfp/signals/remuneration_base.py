# -*- coding: utf-8 -*-

from collections import namedtuple
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.gfp.models import (
    EstruturaTabelaSalarial,
    ExtraPaymentPeriod,
    MovimentacaoProgressao,
    Periodo,
    ReferenciaSalario,
    RemunerationBase,
    RemunerationPeriod,
)
from rh.models import (
    Cargo,
    EncargoFinanceiro,
    MovimentacaoAposentadoria,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
)

log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


# FIXME: @receiver comentado pois ainda não está em uso.


# @receiver(post_save, sender=MovimentacaoPosse)
def update_base_posse(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.servidor))
    update = instance.diff
    log.debug(update)
    if kwargs.get("created") or ("data_exercicio" in update):
        resolve_generators(instance.data_exercicio, instance.servidor)
    return True


# @receiver(post_save, sender=EncargoFinanceiro)
def update_base_encargo(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.request_move.servidor))
    update = instance.diff
    log.debug(update)
    if kwargs.get("created") or (
        "data_fim" in update or "data_fim" in update or "remuneracao" in update
    ):
        resolve_generators(instance.data_inicio, instance.request_move.servidor)
    return True


# @receiver(post_save, sender=MovimentacaoProgressao)
def update_base_progressao(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.servidor))
    update = instance.diff
    log.debug(update)
    if kwargs.get("created") or (
        "data_inicio_vigencia" in update
        or "data_fim_vigencia" in update
        or "referencia_nivel2d" in update
    ):
        resolve_generators(instance.data_inicio_vigencia, instance.servidor)
    return True


# @receiver(post_save, sender=ExtraPaymentPeriod)
def update_base_extra(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.employee))
    update = instance.diff
    log.debug(update)
    if (
        kwargs.get("created")
        or ("value" in update or "start_validity" in update or "end_validity" in update)
    ) and instance.extra_payment.slug == "VPI":
        resolve_generators(instance.start_validity, instance.employee)
    return True


# @receiver(post_save, sender=MovimentacaoDesligamento)
# @receiver(post_save, sender=MovimentacaoAposentadoria)
def update_base_desligamento(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.servidor))
    update = instance.diff
    log.debug(update)
    if kwargs.get("created") or "data_desligamento" in update:
        resolve_generators(instance.data_desligamento, instance.servidor)
    return True


# @receiver(post_delete, sender=MovimentacaoDesligamento)
# @receiver(post_delete, sender=MovimentacaoAposentadoria)
def delete_base_desligamento(sender, instance, **kwargs):
    """Gera bases de remuneração conforme cadastros"""
    log.info("LOAD SIGNAL REMUNERATION BASE for %s" % (instance.servidor))
    resolve_generators(instance.data_desligamento, instance.servidor)
    return True


def resolve_generators(date, employee):
    periods = Periodo.objects.starting_in(date)
    for p in periods:
        generate_remunerations_by_employee(employee, p)


Period = namedtuple("Period", ["range", "remuneration"])

LinkPeriod = namedtuple("LinkPeriod", ["range", "left", "right"])


def generate_periods_remuneration(period, base, range_base):
    remuneration = RemunerationPeriod.objects.get_or_create(
        remuneration=base, start=period.first, end=period.last, days=period.days
    )[0]
    remuneration.period = Periodo.objects.get(
        ano=period.first.year, mes=period.first.month
    )
    factor_quantity = round(
        float(remuneration.days) / float(remuneration.period.range.days), 8
    )
    remuneration.gratification = float(base.base_gratification) * factor_quantity
    remuneration.value = float(base.base_value) * factor_quantity
    base_value = base.base_value
    base_gratification = base.base_gratification
    # normatizator
    normatize_days = 0
    if range_base.left:
        normatize_days += (
            abs(range_base.left) if period.first == range_base.range.first else 0
        )
    if range_base.right:
        normatize_days += (
            abs(range_base.right) if period.last == range_base.range.last else 0
        )
    # percentuais
    if base.percentage:
        rem_base = (
            RemunerationBase.objects.of_employee(base.employee)
            .filter(
                periods__days=remuneration.days,
                periods__period=remuneration.period,
                link__in=("EF", "AC", "CM", "SM"),
            )
            .exclude(pk=base.pk)
            .distinct()
        )
        if (
            rem_base.filter(link="CM").exists()
            and rem_base.filter(link__in=["EF", "AC"]).exists()
        ):
            main = rem_base.filter(link__in=["EF", "AC"]).get()
            cm = rem_base.get(link="CM")
            if cm.base_value > main.base_value:
                rem_base = rem_base.exclude(pk=main.pk)
            else:
                rem_base = rem_base.exclude(pk=cm.pk)
        base_value = (
            float(rem_base.aggregate(Sum("base_value"))["base_value__sum"]) or 0.0
        )
        base_gratification = (
            float(
                rem_base.aggregate(Sum("base_gratification"))["base_gratification__sum"]
            )
            or 0.0
        )
        remuneration.gratification = (
            float(base_value) * (float(base.base_gratification) / 100.0)
        ) * factor_quantity
        if base.link == "EX":
            remuneration.gratification = (
                float(base_gratification) * (float(base.base_gratification) / 100.0)
            ) * factor_quantity
            remuneration.value = (
                float(base_value) * (float(base.base_value) / 100.0)
            ) * factor_quantity
            normatize_days = 0
    normal_factor_qt = round(
        float(remuneration.days + normatize_days) / remuneration.period.range.days, 8
    )
    remuneration.normal_gratification = float(base_gratification) * normal_factor_qt
    remuneration.normal_value = float(base_value) * normal_factor_qt
    remuneration.base_value = base_value
    remuneration.base_gratification = base_gratification
    remuneration.save()
    return remuneration


def create_base(reference, employee, identifier):
    try:
        base = RemunerationBase.objects.get_or_create(
            employee=employee,
            identifier=identifier[2:],
            link=identifier[:2],
            salary=reference.pk,
        )[0]
    except RemunerationBase.MultipleObjectsReturned:
        print("encontrados mais de um obj")
        RemunerationBase.objects.filter(
            employee=employee,
            identifier=identifier[2:],
            link=identifier[:2],
            salary=reference.pk,
        ).last().delete()
        base = RemunerationBase.objects.get_or_create(
            employee=employee,
            identifier=identifier[2:],
            link=identifier[:2],
            salary=reference.pk,
        )[0]
    percentage = False
    gratificacao_base = 0
    onus = True
    if isinstance(reference, ReferenciaSalario):
        valor_base = reference.valor
        gratificacao_base = reference.gratificacao
        if reference.referencia_nivel2d.tipo_gratificacao == 2:
            percentage = True
        if employee.member_type_by_possession:
            valor_base = reference.valor_membro
            gratificacao_base = reference.gratificacao_membro
            if reference.referencia_nivel2d.tipo_gratificacao_membro == 2:
                percentage = True
    elif isinstance(reference, EncargoFinanceiro):
        valor_base = reference.remuneracao
        onus = reference.request_move.onus == 2
    elif isinstance(reference, ExtraPaymentPeriod):
        valor_base = reference.value if reference.main_salary else 0
        gratificacao_base = reference.value if reference.gratification else 0
        if reference.type_value == 2:
            percentage = True

    base.base_value = valor_base
    base.base_gratification = gratificacao_base
    base.percentage = percentage
    base.onus = onus
    base.save()
    return base


def link_period(employee, range_salary):
    last_day = (
        (employee.termination_date - relativedelta(days=1))
        if employee.termination_date
        else None
    )
    exercise = employee.exercise_date
    if employee.requested:
        employee_posses = employee.get_posses_ativas(
            range_salary.first, range_salary.last
        ).filter(requestmove__isnull=False)
        req = (
            employee_posses.assets_in(range=range_salary).last()
            if employee_posses
            else None
        )
        if req is not None:
            exercise = req.data_exercicio
    try:
        interval = range_salary.intersect(NewDateRange(exercise, last_day))
    except Exception:
        print(employee)
        interval = NewDateRange()
    if interval.first:
        left, right = (interval.first - range_salary.first).days, (
            interval.last - range_salary.last
        ).days
        return LinkPeriod(interval, left, right)


def get_remunerations_by_period(salarys):
    ranges = {}
    for sal in salarys:
        interval = sal.range.copy()
        r = 0
        while r < len(ranges) and interval.days:
            inter = ranges[r]["range"].intersect(interval)
            if inter.days:
                if inter == ranges[r]["range"]:
                    ranges[r]["salaries"].update({sal.remuneration})
                else:
                    ranges[r]["range"] = ranges[r]["range"] - inter
                    # Criando o novo range da intersecao
                    idx = len(ranges)
                    salaries_copy = ranges[r]["salaries"].copy()
                    salaries_copy.update({sal.remuneration})
                    ranges[idx] = {"salaries": salaries_copy, "range": inter}
                    # Retirando o interseçao do AUX
                interval -= inter
            r += 1
        idx = len(ranges)
        if interval.days:
            ranges[idx] = {"salaries": {sal.remuneration}, "range": interval}
    return ranges


def extract_range_afastamentos(posse, range_salary):
    range_absences = NewDateRange()
    cessions = (
        posse.afastamento.currents_in(range=range_salary)
        .not_through_payroll()
        .not_canceled()
    )
    absences = (
        BaseLicencaAfastamento.objects.of_employee(posse.servidor)
        .currents_in(range=range_salary)
        .unpaid()
        .not_canceled()
        .no_cession()
    )
    for ab in list(chain(cessions, absences)):
        range_absences.add_range(ab.data_inicio, ab.data_fim)
    return range_absences


def delete_unvalid(salaries, valid, period):
    for sal in list(salaries.values()):
        periods_rem = RemunerationPeriod.objects.filter(Q(period=period)).exclude(
            pk__in=[v.pk for v in valid]
        )
        for s in sal["salaries"]:
            unvalids = periods_rem.filter(
                (Q(remuneration=s) & ~Q(days=sal["range"].days))
                | (Q(remuneration__employee=s.employee) & ~Q(remuneration=s))
            )
            if unvalids.exists():
                unvalids.delete()


def ranges_to_evaluate_by_employee(employee, period):
    ranges = set([])
    range_salary = period.range
    ranges.add(range_salary.first)
    ranges.add(range_salary.last)
    current_possessions = (
        employee.get_posses_ativas(range_salary.first, range_salary.last)
        .with_office_valid_in(range_salary)
        .order_by("-quadro__cargo__tipo_lei_cargo")
    )
    for p in current_possessions:
        if range_salary.first <= p.data_exercicio <= range_salary.last:
            ranges.add(p.data_exercicio)
        if (
            p.data_desligamento
            and range_salary.first
            <= (p.data_desligamento - relativedelta(days=1))
            <= range_salary.last
        ):
            ranges.add(p.data_desligamento - relativedelta(days=1))
    return ranges


@transaction.atomic
def generate_remunerations_by_employee(employee, period):
    log.debug(">> GEN REMUNERATIONS: %s - %s" % (employee, period))
    RemunerationBase.clear(employee, period)
    range_salary = period.range
    current_possessions = (
        employee.get_posses_ativas(range_salary.first, range_salary.last)
        .with_office_valid_in(range_salary)
        .order_by("-quadro__cargo__tipo_lei_cargo")
    )
    link_term = link_period(employee, range_salary)
    salarys = []
    type_employee = employee.tipo_servidor
    maternity = (
        BaseLicencaAfastamento.objects.of_employee(employee)
        .currents_in(range=range_salary)
        .maternitylicense()
        .not_canceled()
    )
    if link_term:
        for x, p in enumerate(current_possessions):
            desligamento = (
                p.data_desligamento - relativedelta(days=1)
                if p.data_desligamento
                else None
            )
            range_posse = NewDateRange(p.data_exercicio, desligamento).intersect(
                range_salary
            )
            range_ = range_posse - extract_range_afastamentos(p, range_salary)
            link = None
            if p.quadro:
                link = p.quadro.cargo.tipo_lei_cargo
            elif p.servidor.is_requested():
                link = "AC"
            for pr in p.progressoes.currents_in(range=range_salary).exclude(
                servidor__tipo="M"
            ):
                r = range_.intersect(
                    NewDateRange(pr.data_inicio_vigencia, pr.data_fim_vigencia)
                )
                ref = "{0}{1}".format(link, pr.referencia_nivel2d)
                estruturas = EstruturaTabelaSalarial.salarios(
                    p.quadro.cargo, r.first, r.last, pr.referencia_nivel2d
                )
                for estrutura in estruturas:
                    base = create_base(estrutura[1], employee, ref)
                    salarys.append(Period(r.intersect(estrutura[0]), base))
            financial_burden = EncargoFinanceiro.objects.of_possession(p).currents_in(
                range=range_salary
            )
            for req in financial_burden:
                r = range_.intersect(NewDateRange(req.data_inicio, req.data_fim))
                ref = "{0}{1}".format(link, "REQ")
                base = create_base(req, employee, ref)
                salarys.append(Period(r.intersect(range_posse), base))
            if link in ["CM", "FC"] or employee.member_type_by_possession:
                try:
                    estruturas = EstruturaTabelaSalarial.salarios(
                        p.quadro.cargo, range_.first, range_.last
                    )
                except Cargo.TabelaSalarialNotFound:
                    pass
                else:
                    for estrutura in estruturas:
                        ref = "{0}{1}".format(link, estrutura[1].referencia_nivel2d)
                        base = create_base(estrutura[1], employee, ref)
                        r = range_.intersect(estrutura[0])
                        maternity_range = NewDateRange()

                        if type_employee == "CM":
                            for ab in maternity:
                                maternity_range += NewDateRange(
                                    ab.data_inicio,
                                    min(
                                        ab.data_fim,
                                        ab.data_inicio + relativedelta(days=119),
                                    ),
                                )
                                basem = create_base(
                                    estrutura[1],
                                    employee,
                                    "SM%s" % estrutura[1].referencia_nivel2d,
                                )
                                rm = range_.intersect(
                                    NewDateRange(
                                        ab.data_inicio,
                                        min(
                                            ab.data_fim,
                                            ab.data_inicio + relativedelta(days=119),
                                        ),
                                    )
                                )
                                salarys.append(Period(rm, basem))
                            r = r - maternity_range
                        salarys.append(Period(r, base))
        extras = (
            employee.extrapaymentperiods.currents_in(range=link_term[0])
            .of_slugs(
                [
                    "VPI",
                ]
            )
            .no_cumulation()
        )  # 'URV-ADMIN-EMPLOYEE'
        for ext in extras:
            r = NewDateRange(ext.start_validity, ext.end_validity).intersect(
                range_salary
            ) - extract_range_afastamentos(p, range_salary)
            ref = "{0}{1}".format("EX", ext.extra_payment.slug[:3])
            base = create_base(ext, employee, ref)

            salarys.append(Period(r.intersect(link_term.range), base))

    remunerations = get_remunerations_by_period(salarys)
    valids = []
    for rem in list(remunerations.values()):
        salaries = RemunerationBase.objects.filter(
            pk__in=[rs.pk for rs in rem["salaries"]]
        ).ordered_by_link()
        for re in salaries:
            valids.append(generate_periods_remuneration(rem["range"], re, link_term))

    delete_unvalid(remunerations, valids, period)
