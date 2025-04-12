# -*- coding: utf-8 -*-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.utils import getLogger
from rh.gfp.models import Evento, FolhaEvento
from rh.models import PessoaFisica
from django.db.models import Sum, Q

from rh.models import Servidor

log = getLogger(__name__)

RD = "\033[0;31m"
GR = "\033[0;32m"
OR = "\033[0;33m"
WT = "\033[1;37m"
YL = "\033[1;33m"
BL = "\033[0;34m"
NC = "\033[0m"  # No Color

MAP = {
    "RTRT": (
        Q(
            as_token__dialect__calendar_year=2022,
            as_token__slug="rendimentos-tributaveis",
        ),
        "value",
        lambda x: x,
    ),
    "RTPO": (
        Q(as_token__dialect__calendar_year=2022, as_token__slug="previdencia-social"),
        "value",
        lambda x: x,
    ),
    "RTDP": (
        Q(as_token__dialect__calendar_year=2022, as_token__slug="deducao-dependentes"),
        "qnt",
        lambda x: float(x) * 189.59,
    ),
    "RTPA": (
        Q(as_token__dialect__calendar_year=2022, as_token__slug="pensao-alimenticia"),
        "value",
        lambda x: x,
    ),
    "RTIRF": (
        Q(
            as_token__dialect__calendar_year=2022,
            as_token__slug="imposto-retido-na-fonte",
        ),
        "value",
        lambda x: x,
    ),
    "RIDAC": (
        Q(
            as_token__dialect__calendar_year=2022,
            as_token__slug="diarias-e-ajuda-de-custo",
        ),
        "value",
        lambda x: x,
    ),
    "RIIRP": (
        Q(
            as_token__dialect__calendar_year=2022,
            as_token__slug="indenizacoes-por-rescisao-de-contrato-de-trabalho",
        ),
        "value",
        lambda x: x,
    ),
    "RIAP": (
        Q(as_token__dialect__calendar_year=2022, as_token__slug="abono-pecuniario"),
        "value",
        lambda x: x,
    ),
    "RIO": (
        Q(as_token__dialect__calendar_year=2022, as_token__slug__startswith="outros-"),
        "value",
        lambda x: x,
    ),
}


def sum_tot(totals):
    return sum([totals[f"m{x:02d}"] for x in range(1, 13)])


def get_from_file_dirf(file_path, cpf, code="0561"):
    idrec = False
    person = False
    totals = {}
    keys = list(MAP.keys()) + ["INFPA"]
    with open(file_path, "r") as ifile:
        for line in ifile:
            split_line = line.split("|")
            if not idrec:
                if split_line[0] == "IDREC" and split_line[1] == code:
                    # print(split_line)
                    idrec = True
            elif not person:
                if split_line[0] == "BPFDEC" and split_line[1] == cpf:
                    # print(split_line)
                    person = True
            else:
                # print(split_line)
                if split_line[0] not in keys:
                    break
                else:
                    if split_line[0] == "INFPA":
                        continue
                    if split_line[0] not in totals:
                        totals[split_line[0]] = {
                            "m01": 0,
                            "m02": 0,
                            "m03": 0,
                            "m04": 0,
                            "m05": 0,
                            "m06": 0,
                            "m07": 0,
                            "m08": 0,
                            "m09": 0,
                            "m10": 0,
                            "m11": 0,
                            "m12": 0,
                            "m13": 0,
                            "tot": 0,
                        }
                    for x in range(1, 14):
                        idx = f"m{x:02d}"
                        totals[split_line[0]][idx] += (
                            int(split_line[x]) / 100 if split_line[0] != "RIO" else 0
                        )
                    totals[split_line[0]]["tot"] = (
                        sum_tot(totals[split_line[0]])
                        if split_line[0] != "RIO"
                        else int(split_line[1]) / 100
                    )
    return totals


def get_totals(calendar_year, entries, identifier, rra=False):
    totals = {}
    config = MAP.get(identifier, [])
    q_filter = config[0] if config else Q()
    sum_field = config[1] if config else "value"
    func = config[2] if config else lambda x: x
    entries_wrra = entries.filter(
        rra_employee__isnull=True, contracheque__pensioner__isnull=True
    )
    # entries_rra = entries.filter(rra_employee__isnull=False)
    entries_wrra_w13 = entries_wrra.exclude(
        reference_month=13
    )  # , reference_year=calendar_year)
    events = Evento.objects.filter(q_filter).values_list("numero", flat=True)
    entries_totals = entries_wrra_w13.filter(evento__numero__in=events)
    totals["Q"] = {}
    for x in range(1, 13):
        query = entries_totals.filter(folha__dt_pagamento__month=x)
        totals[f"m{x:02d}"] = func(abs(query.aggregate(t=Sum(sum_field)).get("t") or 0))
        totals["Q"][x] = query
    query_tot = entries_totals.filter(folha__dt_pagamento__year=calendar_year)
    totals["tot"] = func(abs(query_tot.aggregate(t=Sum(sum_field)).get("t") or 0))
    totals["Q"]["tot"] = query_tot
    query_13 = entries_wrra.filter(
        evento__numero__in=events, reference_year=calendar_year, reference_month=13
    )
    totals["m13"] = func(abs(query_13.aggregate(t=Sum(sum_field)).get("t") or 0))
    totals["Q"][13] = query_13
    return totals


def print_dirf(totals, dirf, diffs, only_diff=False):
    def p(i, idx):
        k = f"m{idx:02d}" if type(idx) == int else idx
        tv = totals[i][k]
        dv = dirf[i].get(k, 0)
        same = not (i in diffs and idx in diffs[i])
        txt = f'{tv}{f"/{dv}" if not same else ""}'

        return f"{GR if same else RD}{str(txt):20s}{NC}"

    print("REF  ", end="", flush=True)
    for k in MAP.keys():
        # totals[k] = get_totals(calendar_year, entries, k)
        if k not in dirf:
            dirf[k] = {}
        print(f"{YL}{k:20s}{NC}", end="", flush=True)
    print("")

    ids = [x for x in range(1, 14)] + ["tot"]
    for x in ids:
        kk = f"{x:02d}   " if type(x) == int else f"{x:5s}"
        print(kk, end="", flush=True)
        for k in MAP.keys():
            print(p(k, x), end="", flush=True)
        print("")

    print(f'{"*"*30} DIFFS {"*"*30}')
    for identifier in diffs:
        for idx in diffs[identifier]:
            print(f'>>>>>>>>> {identifier} {idx} {"-"*30}')
            for fe in totals[identifier]["Q"][idx]:
                print(f">> {fe.evento.numero} {fe.value} {fe.folha}")

    _ = input(" Continuar...")


def type_diff(diffs):
    if not diffs:
        return 0  # Sem diferenças
    else:
        for k in diffs:
            if "tot" not in diffs[k]:
                return 1  # Sem diferenças nos totais
        return 2  # Diferenças inclusive nos totais


def generate_dirf_employee(
    calendar_year, person=None, register=None, cpf="", file_path="", print_error=1
):
    diffs = {}
    if not cpf:
        if person:
            cpf = person.cpf
        elif register:
            cpf = Servidor.objects.filter(matricula=register).last().pessoa_fisica.cpf
    if not person:
        person = PessoaFisica.objects.filter(cpf=cpf).last()

    entries = (
        FolhaEvento.objects.filter(
            status__in=("CT", "CE", "BS"), servidor__pessoa_fisica__cpf=cpf
        )
        .filter(
            Q(folha__dt_pagamento__year=calendar_year)
            | Q(reference_year=calendar_year, reference_month=13)
        )
        .exclude(contracheque__employee_pays_pension=2)
    )

    def evaluate_diff(identifier):
        if identifier != "RIO":
            ids = [x for x in range(1, 14)] + ["tot"]
            for idx in ids:
                k = f"m{idx:02d}" if type(idx) == int else idx
                tv = totals[identifier][k]
                dv = dirf[identifier].get(k, 0)
                same = f"{tv:0.2f}" == f"{dv:0.2f}"
                if not same:
                    if identifier not in diffs:
                        diffs[identifier] = []

                    diffs[identifier].append(idx)

    totals = {}
    dirf = get_from_file_dirf(file_path, cpf) if file_path else {}
    for k in MAP.keys():
        totals[k] = get_totals(calendar_year, entries, k)
        if k not in dirf:
            dirf[k] = {}
        evaluate_diff(k)
    tdiff = type_diff(diffs)
    collor = {0: GR, 1: YL, 2: RD}.get(tdiff)
    print(f">> {collor}{person}{NC}", end="")
    if tdiff:
        errors_ids = ", ".join([k for k in diffs if diffs[k]])
        print(f" > {WT}{errors_ids}{NC}")
        if tdiff == 2 and print_error:
            print_dirf(totals, dirf, diffs)
    else:
        print("")

    return diffs, tdiff


def evaluate_dirf(
    calendar_year, file_path="dirf_2022_2023 (25).txt", init=1, print_error=1
):
    # print(f'PRINT ERROR: {print_error}')
    persons = []
    q_employeers = Servidor.objects.filter(
        (
            Q(entries__contracheque__folha__dt_pagamento__year=calendar_year)
            | Q(entries__reference_month=13, entries__reference_year=calendar_year)
        )
    ).distinct()
    count = 1
    for employee in q_employeers:
        if count < init:
            count += 1
            continue
        if employee.pessoa_fisica.cpf not in persons:
            print(f"{count:04d} ", end="")
            count += 1
            persons.append(employee.pessoa_fisica.cpf)
            diffs, tdiff = generate_dirf_employee(
                calendar_year,
                cpf=employee.pessoa_fisica.cpf,
                file_path=file_path,
                print_error=print_error,
            )


def update_13_entries_with_other_reference_month(
    year,
    advance_13_genres=[
        "016",
    ],
):
    """Esta rotina atualiza os lançamentos de 13º que foram pagas durante o ano e que não foram
    indicadas com reference_month=13 e com isso ficariam de fora dos totalizadores de 13º da DIRF

    Arguments:
        year {int} -- ano calendário

    Keyword Arguments:
        advance_13_genres {list} -- Gêneros de adiantamento de 13º ou de verbas que possuem 13 no titulo
                                    mas não são contabilizadas pela DIRF (default: {['016', ]})
    """
    q = FolhaEvento.objects.filter(
        evento__titulo__icontains="13º", reference_year=year
    ).exclude(evento__genre_event__genre_number__in=advance_13_genres)
    for fe in q.exclude(reference_month=13):
        print(
            fe.reference_month, fe.info, fe, fe.servidor, fe.servidor.pessoa_fisica.pk
        )
        count = q.filter(servidor=fe.servidor, evento=fe.evento).count()
        info = ""
        if count > 1:
            print("********** %d" % count)
            info = "%02d/%04d" % (fe.reference_month, fe.reference_year)
        print(
            FolhaEvento.objects.filter(pk=fe.pk).update(reference_month=13, info=info)
        )


def run():
    print(f"{WT}SCRIPT DE AVALIAÇÃO DA DIRF{NC}")
    year = input("Digite o ano (2022): ") or 2022
    init = input("Registro inicial (1): ") or 1
    errors = input("Mostrar erros [S]/N? ):") or "S"
    print_error = 1 if errors.upper() == "S" else 0
    print(f"PRINT ERROR: {print_error}")
    evaluate_dirf(year, init=int(init), print_error=print_error)


if __name__ == "__main__":
    run()
