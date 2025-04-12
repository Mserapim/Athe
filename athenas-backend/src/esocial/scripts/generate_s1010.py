# -.- coding: utf-8 -.-
import os
import codecs
import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from esocial.models import S1010, ItemTable
from contrib.utils import getLogger
from rh.gfp.models import Evento, ConfigEvent
from rh.models import ProcessSuspension
from django.db.models import Count
from django.conf import settings


log = getLogger(__name__)


set_current_user("athenas")


def dados_rubrica_cod_inc_cp(cod_rubr):
    rs = (
        S1010.objects.filter(ide_rubrica_cod_rubr=cod_rubr)
        .filter(dados_rubrica_cod_inc_cp__isnull=False)
        .last()
    )
    if rs:
        return rs.dados_rubrica_cod_inc_cp
    return "00"


def dados_rubrica_cod_inc_irrf(cod_rubr):
    rs = (
        S1010.objects.filter(ide_rubrica_cod_rubr=cod_rubr)
        .filter(dados_rubrica_cod_inc_irrf__isnull=False)
        .last()
    )
    if rs:
        return rs.dados_rubrica_cod_inc_irrf
    return "00"


def dados_rubrica_cod_inc_fgts(cod_rubr):
    rs = (
        S1010.objects.filter(ide_rubrica_cod_rubr=cod_rubr)
        .filter(dados_rubrica_cod_inc_fgts__isnull=False)
        .last()
    )
    if rs:
        return rs.dados_rubrica_cod_inc_fgts
    return "00"


def dados_rubrica_cod_inc_cprp(cod_rubr):
    rs = (
        S1010.objects.filter(ide_rubrica_cod_rubr=cod_rubr)
        .filter(dados_rubrica_cod_inc_cprp__isnull=False)
        .last()
    )
    if rs:
        return rs.dados_rubrica_cod_inc_cprp
    return "00"


def dados_rubrica_nat_rubr(cod_rubr):
    rs = (
        S1010.objects.filter(ide_rubrica_cod_rubr=cod_rubr)
        .filter(dados_rubrica_nat_rubr__isnull=False)
        .last()
    )
    if rs:
        item = ItemTable.objects.by_code_table(rs.dados_rubrica_nat_rubr, 3)
        return f"{item.code} - {item.title}"
    return "-"


def run():
    text = "número evento | nome evento | cp | irrf | fgts | cprp | natureza esocial\n".upper()
    events = (
        S1010.objects.filter()
        .values("ide_rubrica_cod_rubr")
        .annotate(count_rubr=Count("ide_rubrica_cod_rubr"))
        .order_by("ide_rubrica_cod_rubr")
    )
    for event in events:
        cp = dados_rubrica_cod_inc_cp(event.get("ide_rubrica_cod_rubr"))
        irrf = dados_rubrica_cod_inc_irrf(event.get("ide_rubrica_cod_rubr"))
        fgts = dados_rubrica_cod_inc_fgts(event.get("ide_rubrica_cod_rubr"))
        cprp = dados_rubrica_cod_inc_cprp(event.get("ide_rubrica_cod_rubr"))
        nat_rubr = dados_rubrica_nat_rubr(event.get("ide_rubrica_cod_rubr"))
        evt = Evento.objects.get(numero=f'{event.get("ide_rubrica_cod_rubr")}')
        text += f"{evt.numero} | {evt.titulo} | {cp} | {irrf} | {fgts} | {cprp} | {nat_rubr}\n"
    print(text)

    CACHE_PATH = getattr(settings, "CACHE_PATH", None)
    nm = f"{CACHE_PATH}/s1010.csv"
    print(f"Escrito em {nm}")
    with codecs.open(nm, "w") as fwrite:
        fwrite.write(text)


def run1():
    for ce in ConfigEvent.objects.filter():
        try:
            ce.save()
            if ce.diff:
                print(f"EVENTO: {ce.event}")
                print(f"CONFIG: {ce}")
                print(ce.diff)
                print("------------------")
        except Exception as err:
            # print(ce.pk, ce)
            # print(err)
            pass

    # for ce in ConfigEvent.objects.filter(event__numero='05002'):
    #     try:
    #         ce.set_esocial_cp()
    #         ce.set_esocial_irrf()
    #         ce.set_esocial_cprp()

    #         query_suspensions = ProcessSuspension.objects.by_event(
    #             ce.event.numero,
    #             drange=NewDateRange(ce.start_validity, ce.start_validity if not ce.end_validity else ce.end_validity)
    #         ).filter(scope_decision=1)
    #         print('query_suspensions')
    #         print(query_suspensions)

    #         focuses_on_monthly = ce.event.aplica_em.filter(
    #             event__carater__in=(
    #                 4,   # IMPORTO MENSAL
    #                 16,  # IMPOSTO RRA
    #                 20   # IMPOSTO 13
    #             )
    #         ).validity_in(start_date=ce.start_validity, end_date=ce.end_validity)
    #         print(focuses_on_monthly)
    #         ce.save()
    #     except Exception as err:
    #         print(ce.pk, ce)
    #         print(err)


if __name__ == "__main__":
    # run()
    run1()
