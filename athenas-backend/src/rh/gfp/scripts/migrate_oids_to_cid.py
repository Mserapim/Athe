# -*- coding: utf-8 -*-
import datetime

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from rh.gfp.models import (
    ConfigEvent,
    Evento,
    ExtraPaymentPeriod,
    FolhaEvento,
    PaycheckDifference,
    ReferenciaSalario,
)
from rh.models import EncargoFinanceiro
from standard.models import ClassCode, RunCodeManager


def get_ref_salario_comp(ref, per):
    return (
        ReferenciaSalario.objects.currents_in(range=per.range)
        .filter(referencia_nivel2d__sigla_cache=ref)
        .first()
    )


def get_ref_salario(base_value, ref, pct=None, per=None):
    ref_s = ReferenciaSalario.objects.filter(referencia_nivel2d__sigla_cache=ref)
    rs = ref_s.filter(
        Q(valor=base_value)
        | Q(valor_membro=base_value)
        | Q(gratificacao=base_value)
        | Q(gratificacao_membro=base_value)
    ).first()
    if not rs and pct:
        rs = (
            ref_s.filter(Q(gratificacao=pct) | Q(gratificacao_membro=pct))
            .currents_in(range=per.range)
            .first()
        )
    if not rs:
        print(f"NAO ENCONTRADA REF. SALARIO: {ref} {base_value}")
    return rs


def get_encargos_financeiro(base_value, employee):
    # print(base_value, employee)
    ef = (
        EncargoFinanceiro.objects.filter(requisicao__servidor=employee)
        .filter(remuneracao=base_value)
        .first()
    )
    if not ef:
        print("NAO ENCONTRADO ENCARGO FIN.: ", employee, base_value)
    return ef


def get_verba_extra(slug, employee, base_value):
    epp = ExtraPaymentPeriod.objects.filter(
        extra_payment__slug=slug, employee=employee, value=base_value
    ).first()
    if not epp:
        print("VERBA EXTRA: ", slug, employee, base_value)
    return epp


def migrate(year=2019, show=[]):
    not_migrated = []
    not_found = []
    ups = 0
    period = None
    for (
        fe
    ) in FolhaEvento.objects.filter(  # folha__periodo__mes=8, servidor__matricula=4191,
        folha__periodo__ano=year, automated=True
    ).order_by(
        "-folha__periodo__ano", "-folha__periodo__mes"
    ):

        if period != fe.folha.periodo:
            if period:
                print(ups)
            ups = 0
            period = fe.folha.periodo
            print(">>>>>>>>> %s >>>>>>>>>" % period)
        # print(fe.oIds)
        # print(len(fe.oIds))
        if len(fe.oIds) == 1:
            # print('deveria entrar aqui e migrar')
            # print fe.oIds[0], type(fe.oIds[0])
            if isinstance(fe.oIds[0], int) or fe.oIds[0].isdigit():
                # ev_str.add(fe.evento)
                # print('entrou no e digito')
                ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                    cid=int(fe.oIds[0]),
                    json_calc_vars='{"oIds": [%s]}' % int(fe.oIds[0]),
                )
                # print 'STR: ', fe, fe.oIds
            elif fe.evento.numero == "00100":
                rs = get_ref_salario(
                    fe.correct_base_value or fe.valor_base,
                    fe.oIds[0][2:],
                    fe.folha.periodo,
                )
                if fe.oIds[0] != "EF%s" % rs:
                    print(
                        rs,
                        fe.contracheque.referencia_salario_efetivo,
                        fe.contracheque.referencia_salario_efetivo.pk,
                        fe.oIds[0],
                    )

                if rs:
                    ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                        cid=rs.pk, json_calc_vars='{"oIds": [%s]}' % rs.pk
                    )
            elif fe.evento.numero in ["00700", "00500", "00600"]:
                rs = get_ref_salario(
                    fe.valor_base or fe.correct_valor_base,
                    fe.oIds[0][2:],
                    fe.pct or fe.correct_pct,
                    fe.folha.periodo,
                )
                if rs:
                    # print rs, fe.oIds[0], fe.valor_base or fe.correct_valor_base
                    ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                        cid=rs.pk, json_calc_vars='{"oIds": [%s]}' % rs.pk
                    )
                else:
                    not_found.append(fe)
            elif fe.evento.numero in ["00400"]:
                rs = get_encargos_financeiro(
                    fe.valor_base or fe.correct_valor_base, fe.servidor
                )
                if rs:
                    # print rs, fe.oIds[0], fe.valor_base or fe.correct_valor_base
                    ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                        cid=rs.pk, json_calc_vars='{"oIds": [%s]}' % rs.pk
                    )
                else:
                    not_found.append(fe)
            elif fe.evento.numero in ["05100"]:
                epp = get_verba_extra(
                    "VPI", fe.servidor, fe.valor_base or fe.correct_valor_base
                )
                if epp:
                    ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                        cid=epp.pk, json_calc_vars='{"oIds": [%s]}' % epp.pk
                    )
                else:
                    not_found.append(fe)

        elif len(fe.oIds) > 1:
            if fe.evento.numero == "00400":
                rs = get_encargos_financeiro(
                    fe.valor_base or fe.correct_valor_base, fe.servidor
                )
                if rs:
                    ups += FolhaEvento.objects.filter(pk=fe.pk).update(
                        cid=rs.pk, json_calc_vars='{"oIds": [%s]}' % rs.pk
                    )
                else:
                    not_found.append(fe)
        else:
            not_migrated.append(fe)

    print(ups)

    print("NOT MIGRATED .........")
    for m in not_migrated:
        if fe.evento.numero in show:
            print(m.pk, m.oIds, m.cid, m)
    print("NOT FOUND .........")
    print("")
    for f in not_found:
        print(f)


def change_calcs_and_focuses():
    # load classcodes
    RunCodeManager.discovery_in(
        [
            "rh.gfp.classcodes",
            "rh.gfp.classcodes.ferias",
            "rh.gfp.classcodes.aid",
            "rh.gfp.classcodes.covenant",
            "rh.gfp.classcodes.socialsecurity",
            "rh.gfp.classcodes.fault",
        ]
    )
    currency = NewDateRange(datetime.date(2018, 1, 1), datetime.date(2019, 12, 31))
    base = [
        "00100",
        "00400",
        "00500",
        "00600",
        "00700",
        "01100",
        "04000",
        "05100",
        "06000",
        "06100",
        "06200",
        "06300",
        "06400",
        "06500",
    ]
    num_events = base + [
        "05000",
        "06700",
        "51000",
        "90500",
        "90000",
        "04800",
        "91000",
        "91200",
        "91500",
        "90800",
        "05900",
        "04600",
        "10000",
        "05800",
        "70100",
    ]
    set_current_user("athenas")
    events = (
        ConfigEvent.objects.current_in(currency.first, currency.last)
        .filter(event__numero__in=num_events)
        .exclude(calculation=None)
    )
    for c in events:
        # print(c)
        calc = c.calculation
        new_path = str(
            calc.path.replace("calcs.mpto", "classcodes").replace(
                "remuneracao", "remuneration"
            )
        )
        # print(new_path)
        new_calc = ClassCode.objects.filter(path=new_path).last()
        print(new_calc)
        if new_calc:
            # print('achei o rapaz')
            c.calculation = new_calc
            c.save()
            if c.event.numero == "05000":
                focuses = Evento.objects.filter(numero__in=base)
                # print(focuses)
                list(map(lambda x: c.focuses_on.add(x), focuses))


def undo_new_calcs_and_focuses():
    currency = NewDateRange(datetime.date(2018, 1, 1), datetime.date(2019, 12, 31))
    base = ["00100", "00400", "00500", "00600", "00700", "01100", "04000", "05100"]
    urv = ["06000", "06100", "06200", "06300", "06400", "06500"]
    num_events = (
        base
        + urv
        + [
            "05000",
            "06700",
            "51000",
            "90500",
            "90000",
            "04800",
            "91000",
            "91200",
            "91500",
            "90800" "05900",
            "04600",
            "10000",
            "05800",
            "70100",
            "01500",
            "01600",
            "01700",
            "49900",
            "91700",
            "00800",
            "10100",
            "10200",
        ]
    )

    set_current_user("athenas")
    events = ConfigEvent.objects.current_in(currency.first, currency.last).filter(
        event__numero__in=num_events
    )
    for c in events:
        print(f"vai fazer o {c}")
        calc = c.calculation
        if calc:
            new_path = str(
                calc.path.replace("classcodes", "calcs.mpto").replace(
                    "remuneration", "remuneracao"
                )
            )
            # print(new_path)
            new_calc = ClassCode.objects.filter(path=new_path).last()
            print("achou")
            if new_calc:
                # print('achei o rapaz')
                c.calculation = new_calc
                c.save()
                if c.event.numero == "05000":
                    focuses = Evento.objects.filter(numero__in=base)
                    # print(focuses)
                    list(map(lambda x: c.focuses_on.remove(x), focuses))


def ignore_diff_cid(month, year=2019):
    num_events = [
        "00100",
        "00400",
        "00500",
        "00600",
        "00700",
        "01100",
        "04000",
        "05100",
    ]
    entries = FolhaEvento.with_differences.filter(
        folha__periodo__mes=month,
        folha__periodo__ano=year,
        evento__numero__in=num_events,
    )
    print(entries.distinct().count())
    if entries.count() > 0:
        title = "Ignora diferenças ocasionadas por mudança no unique together de FolhaEvento e uso do cid."
        payroll = entries.first().contracheque.folha
        set_current_user("athenas")
        try:
            PaycheckDifference.create_differences(
                payroll, entries=entries, title=title, status=6
            )
        except Exception as e:
            print(e)
    else:
        print("Tem nada pa fazer não")


def delete_ncs(year, month):
    num_events = ["00100", "00500", "00600", "00400", "05100", "00700"]
    set_current_user("athenas")
    entries = FolhaEvento.with_differences.filter(
        folha__periodo__mes=month,
        folha__periodo__ano=year,
        evento__numero__in=num_events,
        status="NC",
    )
    print(entries[0], entries.count())
    entries.delete()
