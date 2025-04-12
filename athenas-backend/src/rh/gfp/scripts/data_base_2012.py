# -.- coding: utf-8 -.-
import os
import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


def entry_differencies(entry):
    from rh.gfp.models import FolhaEvento, PaycheckDifferenceItem, PaycheckDifference

    diff = PaycheckDifferenceItem.objects.filter(
        entry_difference__pk=entry
    ).values_list("difference__pk", flat=True)
    diff_pks = PaycheckDifference.objects.filter(pk__in=diff).values_list(
        "pk", flat=True
    )
    return [fe for fe in FolhaEvento.objects.filter(paycheck_difference__in=diff_pks)]


def get_diff_text(diffs):
    diffs_txt = ""
    for e in set(diffs):
        diffs_txt += f"{e.valor}({e.folha.periodo}),"
    if diffs_txt:
        diffs_txt = diffs_txt[:-1]
    return diffs_txt


def run(register):
    from rh.gfp.models import FolhaEvento, Periodo

    query = FolhaEvento.objects.filter(servidor__matricula=register)

    q_periods = (
        Periodo.objects.filter()
        .exclude(ano__lt=2012)
        .exclude(ano=2012, mes__lt=5)
        .exclude(ano=2022, mes__gt=9)
        .exclude(ano__gt=2022)
        .order_by("ano", "mes")
    )
    for p in q_periods:

        remun_base = 0
        diffs = []
        for fe in query.filter(
            folha__periodo=p,
            evento__numero__in=["0001", "1305", "00100", "01500", "10400"],
        ):
            remun_base += (
                fe.correct_value
            )  # .aggregate(base=Sum('correct_value'))['base'] or 0
            diffs += entry_differencies(fe.pk)
        diffs_txt = get_diff_text(diffs)
        text = f'{"RM" if p.mes != 13 else "R13"};{(p.mes if p.mes <=12 else 12):02d}/{p.ano:04d};{remun_base};{diffs_txt}'
        print(text)

        for fe in query.filter(
            folha__periodo=p, evento__numero__in=["0236", "0234", "05000", "08300"]
        ):
            adicional = fe.correct_value
            f_adicional = adicional / remun_base * 100
            diffs = entry_differencies(fe.pk)
            diffs_txt = get_diff_text(diffs)
            text1 = f'{"I" if fe.evento.numero == "08300" else ""}AF{f_adicional:2.0f};{p.mes:02d}/{p.ano:04d};{adicional};{diffs_txt}'
            if f_adicional:
                print(text1)

        for fe in query.filter(folha__periodo=p, evento__numero__in=["05700"]):
            idenizacao = fe.correct_value
            f_adicional = adicional / remun_base * 100
            diffs = entry_differencies(fe.pk)
            diffs_txt = get_diff_text(diffs)
            text1 = f"IF;{p.mes:02d}/{p.ano:04d};{idenizacao};{diffs_txt}"
            print(text1)
        # print(ret)


if __name__ == "__main__":
    # run()
    run(91108)
