# -.- coding: utf-8 -.-
import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.extractors.s1200 import S1200Extractor
from rh.models import Servidor
from rh.gfp.models import FolhaEvento


set_current_user("gustavodettenborn")


def dm_dev(month, year):
    print(f"\n----------MONTH: {month} YEAR: {year}-------------\n")
    for cc in (
        S1200Extractor.paychecks(
            month, year, Servidor.objects.get(matricula=65507).pessoa_fisica.cpf
        )
        .distinct()
        .order_by("folha__periodo__mes")
    ):
        print(f"CONTRACHEQUE: {cc.pk} => {cc}")
        print("EVENTOS:")
        for entry in cc.lancamentos.filter():
            print(
                entry.reason_difference,
                entry.reference_year,
                entry.reference_month,
                entry.pk,
                entry,
            )

        print("===========> PER APUR")
        for entry in S1200Extractor.entries_by_reference_esocial(
            cc, month, year, ide_adc=None, per_apur=True
        ):
            print(
                entry.reason_difference,
                entry.reference_month,
                entry.reference_year,
                entry.pk,
                entry,
            )

        # print('===========> PER ANT')
        # for entry in S1200Extractor.entries_by_reference_esocial(cc, month, year, ide_adc=None, per_apur=False):
        #     print(entry.reason_difference, entry.reference_month, entry.reference_year, entry.pk, entry)

        # # print('===========> IDE_ADC 1')
        # # for entry in S1200Extractor.entries_by_reference_esocial(cc, month, year, ide_adc=1, per_apur=False):
        # #     print(entry.reason_difference, entry.reference_month, entry.reference_year, entry.pk, entry)

        # print('===========> PER ANT IDE_ADC 2')
        # for entry in S1200Extractor.entries_by_reference_esocial(cc, month, year, ide_adc=2, per_apur=False):
        #     print(entry.reason_difference, entry.reference_month, entry.reference_year, entry.pk, entry)

        # print('===========> PER ANT IDE_ADC 3')
        # for entry in S1200Extractor.entries_by_reference_esocial(cc, month, year, ide_adc=3, per_apur=False):
        #     print(entry.reason_difference, entry.reference_month, entry.reference_year, entry.pk, entry)


def run():
    # FolhaEvento.objects.filter(reference_year=2022).update(reason_difference=1)
    # FolhaEvento.objects.filter(reference_year=2022).update(reason_difference=2)
    FolhaEvento.objects.filter(
        folha__periodo__ano=2022,
        folha__periodo__mes=6,
        evento__numero__in=("00501", "00601", "91001"),
    ).update(reason_difference=2)
    # FolhaEvento.objects.filter(reference_year=2022, evento__numero__in=('09400', '05301')).update(reason_difference=4)

    # dm_dev(7, 2022)
    # dm_dev(6, 2022)
    # dm_dev(5, 2022)


if __name__ == "__main__":
    run()
