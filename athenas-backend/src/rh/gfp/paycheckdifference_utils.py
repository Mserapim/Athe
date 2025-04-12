from contrib.utils import getLogger

from rh.models import Servidor as Employee
from rh.gfp.models import (
    FolhaModelo as PayrollModel,
    Folha as Payroll,
    FolhaEvento as Entry,
    Evento as Event,
    ContraCheque as Paycheck,
    DifferencePayroll,
)

log = getLogger(__name__)


def get_employees_to_compare():
    payroll_model = PayrollModel.objects.get(titulo="NORMAL")
    types_possession = [
        x["cvalue"] for x in payroll_model.types_of_employee.values("cvalue").all()
    ]
    employees = [
        x
        for x in Employee.objects.filter(type_by_possession__in=types_possession)
        if x.ativo
    ]

    return [e.pk for e in employees]


def get_events_to_compare(period):
    events = []
    for payroll in Payroll.objects.filter(
        periodo__ano=period.folha.periodo.ano, periodo__mes=period.folha.periodo.mes
    ):
        model = payroll.tipo_folha.modelo
        if model and model.principais:
            [
                events.append(event)
                for event in model.principais.all()
                if event.evaluate_difference and event.automated
            ]
    events = set(events)

    return [e.pk for e in events]


def clean_differences():
    DifferencePayroll.objects.filter(
        status="AVAL",
        event__evaluate_difference=False,
    ).delete()


def calc_from_period(employee, payroll, event, params={}):
    classcode = event.calculation_at(payroll.date_range.first)
    cls = classcode.cls

    calc = cls(employee, payroll, event, params=params)
    ret = calc.calculate()

    ret["valor_diff"] = ret["valor"]

    return ret


def get_difference(period, employee, event, info):
    return DifferencePayroll.objects.filter(
        period=period,
        employee=employee,
        event=event,
        info_event=info,
    )


def check_diff_for_diff_exists_and_values_calc(diff_exists, values_calc):
    return int(values_calc["qnt"]) != int(diff_exists.qtd_diff) or float(
        values_calc["valor_diff"]
    ) != float(diff_exists.value_diff)


def check_diff_for_entry_and_values_calc(entry, values_calc):
    if entry.automated is False:
        return False
    else:
        return int(values_calc["qnt"]) != int(entry.qnt) or float(
            values_calc["valor_diff"]
        ) != float(entry.correct_valor)


def update_values_calc_from_diff(values_calc, diffs_applicated, entry):
    qtd_total = 0
    valor_total = 0
    for diff in diffs_applicated:
        qtd_total += diff.qtd_diff
        valor_total += diff.value_diff
    qtd_total += entry.qnt
    valor_total += entry.correct_valor

    values_calc["qnt"] = float(values_calc["qnt_max"]) - float(qtd_total)

    values_calc["valor_diff"] = float(values_calc["valor_base"]) - float(valor_total)

    return values_calc


def update_values_calc_from_entry(values_calc, entry):
    if int(values_calc["qnt"]) != int(entry.qnt):
        values_calc["qnt"] = int(values_calc["qnt"]) - int(entry.qnt)

    if float(values_calc["valor_diff"]) != float(entry.correct_valor):
        values_calc["valor_diff"] = float(values_calc["valor_diff"]) - float(
            entry.correct_valor
        )
    if values_calc["valor_diff"] < 0:
        values_calc["valor_diff"] = values_calc["valor_diff"] * -1

    return values_calc


def update_values_calc_from_choice(values_calc, entry):
    if int(values_calc["qnt"]) != int(entry.qnt):
        values_calc["qnt"] = int(values_calc["qnt"]) - int(entry.qnt)
    if values_calc["qnt"] < 0:
        values_calc["qnt"] = values_calc["qnt"] * -1

    if float(values_calc["valor_diff"]) != float(entry.correct_valor):
        values_calc["valor_diff"] = float(values_calc["valor_diff"]) - float(
            entry.correct_valor
        )
    if values_calc["valor_diff"] < 0:
        values_calc["valor_diff"] = values_calc["valor_diff"] * -1

    values_calc["base_previdencia"] = values_calc["valor_diff"]

    return values_calc


def calc_from_choices(values_calc, values_calc_with_params):
    values_calc["qnt"] += values_calc_with_params["qnt"]
    values_calc["valor_diff"] += values_calc_with_params["valor"]
    values_calc["valor"] += values_calc_with_params["valor"]
    values_calc["valor_base"] += values_calc_with_params["valor"]

    if int(values_calc["qnt_max"]) != int(values_calc_with_params["qnt_max"]):
        values_calc["qnt_max"] = values_calc_with_params["qnt_max"]

    if values_calc_with_params["info"]:
        prefix = "," if values_calc["info"] else ""
        values_calc["info"] = (
            f"{values_calc['info']}{prefix}{values_calc_with_params['info']}"
        )

    return values_calc


def get_entry_from_choices(cid, payroll):
    entry = Entry.objects.filter(cid=cid, folha=payroll)

    return entry.first() if entry else False


def get_entry(event, paychecks_ids):
    entry = [
        cc.lancamentos.filter(evento=event).first()
        for cc in Paycheck.objects.filter(pk__in=paychecks_ids)
        if cc.lancamentos.filter(evento=event).exists()
    ]

    return entry[0] if entry else False


def get_payroll(entry, period):
    if entry:
        return entry.contracheque.folha
    else:
        return Payroll.objects.get(pk=period.folha.pk, tipo_folha__titulo="NORMAL")


def check_and_create_difference(
    employee, period, event, entry, values_calc, update_value=True
):
    values_calc_gt_zero = values_calc["qnt"] > 0 and values_calc["valor"] > 0

    diff_exists = get_difference(period, employee, event, values_calc["info"])

    if entry is False and values_calc_gt_zero:
        if diff_exists.exists() and diff_exists.filter(status="AVAL").exists():
            diff_for_diff_exists = check_diff_for_diff_exists_and_values_calc(
                diff_exists.first(), values_calc
            )
            if diff_for_diff_exists:
                diff_exists.filter(status="AVAL").update(status="IGNO")
                create_difference(period, employee, event, values_calc)
        else:
            create_difference(period, employee, event, values_calc)
    elif entry and values_calc["validate"]["message"] == "":
        diff_entry_values_calc = check_diff_for_entry_and_values_calc(
            entry, values_calc
        )

        if diff_entry_values_calc:
            if update_value:
                values_calc = update_values_calc_from_entry(values_calc, entry)

            if diff_exists.exists() is False:
                create_difference(period, employee, event, values_calc, entry)
            else:
                if diff_exists.filter(status="APLI").exists():
                    values_calc = update_values_calc_from_diff(
                        values_calc, diff_exists.filter(status="APLI"), entry
                    )
                    values_calc["from_others_diffs"] = True

                if diff_exists.filter(status="AVAL").exists() is False:
                    create_difference(period, employee, event, values_calc, entry)
                elif check_diff_for_diff_exists_and_values_calc(
                    diff_exists.first(), values_calc
                ):
                    diff_exists.filter(status="AVAL").update(status="IGNO")
                    create_difference(period, employee, event, values_calc, entry)
        elif diff_exists.filter(status="AVAL").exists():
            diff_exists.filter(status="AVAL").update(status="IGNO")


def set_diff_exists_to_ignored(diff_exists):
    diff_exists.status = "IGNO"
    diff_exists.save()


def create_difference(period, employee, event, values_calc, entry_origin=None):
    type_diff = "PROV"
    if values_calc["qnt"] < 0:
        type_diff = "DESC"
        values_calc["qnt"] = values_calc["qnt"] * -1

    if values_calc["qnt"] != 0 and values_calc["valor_diff"] != 0:
        different_payroll = DifferencePayroll(
            period=period,
            employee=employee,
            event=event,
            qtd_diff=values_calc["qnt"],
            qtd_max_diff=values_calc["qnt_max"],
            correct_value_diff=values_calc["valor_diff"],
            value_diff=values_calc["valor_diff"],
            base_value_diff=values_calc["valor_base"],
            installment_paid_diff=values_calc["parcela"],
            installments_diff=values_calc["prazo"],
            pct_event_diff=values_calc["pct"],
            contribution_base_diff=values_calc["base_previdencia"],
            employer_value_diff=values_calc["patronal"],
            type_diff=type_diff,
        )

        if entry_origin:
            different_payroll.paycheck_event = entry_origin.contracheque
            different_payroll.qtd_event = entry_origin.qnt
            different_payroll.qtd_max_event = entry_origin.qnt_max
            different_payroll.correct_value_event = entry_origin.correct_valor
            different_payroll.base_value_event = entry_origin.valor_base
            different_payroll.installment_paid_event = entry_origin.parcela
            different_payroll.installments_event = entry_origin.prazo
            different_payroll.pct_event = entry_origin.pct
            different_payroll.contribution_base_event = (
                entry_origin.correct_base_previdencia
            )
            different_payroll.employer_value_event = entry_origin.patronal
            different_payroll.info_event = values_calc["info"]

        if "from_others_diffs" in values_calc.keys():
            different_payroll.from_others_diffs = values_calc["from_others_diffs"]

        different_payroll.save()


def get_event_to_apply(genre_number, specie_number):
    q = Event.objects.filter(
        genre_event__genre_number=genre_number,
        specie_event__specie_number=specie_number,
    )

    return q.first() if q.exists() else None


def update_diff_payroll_to_applied(paycheck_to_apply, diff_payroll, event_to_apply):
    diff_payroll.paycheck_applied = paycheck_to_apply
    diff_payroll.event_diff = event_to_apply
    diff_payroll.status = "APLI"
    diff_payroll.save()
