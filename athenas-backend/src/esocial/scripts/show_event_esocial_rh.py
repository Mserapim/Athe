# -.- coding: utf-8 -.-
import django
import os
import time


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from esocial.const import PROCESS_STATUS_EVENT_VALIDS_SENT
from contrib.middleware import set_current_user
from esocial.extractors.s1200 import ExtractorPayroll, S1200Extractor
from esocial.models import (
    S1200,
    S1202,
    S1207,
    S1210,
    S1299,
    S2200,
    S2298,
    S2300,
    S2400,
    DemonstrativeItem,
    Event,
)
from rh.gfp.models import FolhaEvento, Periodo
from rh.models import Servidor


set_current_user("gustavodettenborn")


def run():
    while True:
        print(
            f"FolhaEvento sem event_esocial: {FolhaEvento.objects.filter(event_esocial__isnull=True).count()}"
        )
        print(
            f"FolhaEvento com event_esocial: {FolhaEvento.objects.filter(event_esocial__isnull=False).count()}"
        )
        total_dmi = DemonstrativeItem.objects.count()
        print(f"DemonstrativeItem total: {total_dmi}")
        total_dmi_not_sent = DemonstrativeItem.objects.not_sent().count()
        total_dmi_sent_error = DemonstrativeItem.objects.sent_error().count()
        print(f"DemonstrativeItem not sent total: {total_dmi_not_sent}")
        print(f"DemonstrativeItem sent error: {total_dmi_sent_error}")
        print(
            f"DemonstrativeItem total + FolhaEvento prenchido: {FolhaEvento.objects.filter(event_esocial__isnull=False).count() + total_dmi_not_sent}"
        )
        print(
            f"Servidor sem event_esocial: {Servidor.objects.filter(event_esocial__isnull=True).count()}"
        )
        print(
            f"Servidor com event_esocial: {Servidor.objects.filter(event_esocial__isnull=False).count()}"
        )
        print(
            f"S2200 total: {S2200.objects.count()} {S2200.objects.valids_by_status().count()}"
        )
        print(
            f"S2300 total: {S2300.objects.count()} {S2300.objects.valids_by_status().count()}"
        )
        print(
            f"S2400 total: {S2400.objects.count()} {S2400.objects.valids_by_status().count()}"
        )
        print(
            f"S2298 total: {S2298.objects.count()} {S2298.objects.valids_by_status().count()}"
        )
        print(
            f'S1200.objects.with_problems: {S1200.objects.with_problems("2022-05").count()}'
        )
        print(
            f'S1202.objects.with_problems: {S1202.objects.with_problems("2022-05").count()}'
        )
        print(
            f'S1207.objects.with_problems: {S1207.objects.with_problems("2022-05").count()}'
        )
        print(
            f'S1210.objects.with_problems: {S1210.objects.with_problems("2022-05").count()}'
        )
        if S1299.objects.exists():
            s1299 = S1299.objects.last()
            try:
                print(f"S1299.can_close: {s1299.can_close()}")
            except Exception as err:
                print(err)
            try:
                print(
                    f"S1299.check_can_close_s1200: {s1299.check_can_close_s1200(s1299.ide_evento_per_apur)}"
                )
            except Exception as err:
                print(err)
            try:
                print(
                    f"S1299.check_can_close_s1202: {s1299.check_can_close_s1202(s1299.ide_evento_per_apur)}"
                )
            except Exception as err:
                print(err)
            try:
                print(
                    f"S1299.check_can_close_s1207: {s1299.check_can_close_s1207(s1299.ide_evento_per_apur)}"
                )
            except Exception as err:
                print(err)
            try:
                print(
                    f"S1299.check_can_close_s1210: {s1299.check_can_close_s1210(s1299.ide_evento_per_apur)}"
                )
            except Exception as err:
                print(err)
            try:
                total = s1299.check_can_close_entry(
                    per_apur=s1299.ide_evento_per_apur,
                    period=Periodo.objects.get(
                        mes=s1299.competence_month, ano=s1299.competence_year
                    ),
                )
                print(f"S1299.check_can_close_entry: {total}")
            except Exception as err:
                print(err)
        print(
            f"ExtractorPayroll.all_entries_by_reference_esocial: {ExtractorPayroll.all_entries_by_reference_esocial(5, 2022).count()}"
        )
        print(
            f"ExtractorPayroll.all_entries_by_reference_esocial sem esocial: {ExtractorPayroll.entries_not_in_demonstrative_item(5, 2022).count()}"
        )
        oids = (
            oid
            for oid in DemonstrativeItem.objects.demonstrative_item_all(
                per_apur=s1299.ide_evento_per_apur
            ).values_list("oid", flat=True)
        )
        entries_without_esocial = ExtractorPayroll.entries_not_in_demonstrative_item(
            5, 2022
        )
        entries_without_esocial_not_in_demonstrative_itens = (
            ExtractorPayroll.all_entries_by_reference_esocial(5, 2022).exclude(
                pk__in=oids
            )
        )
        print(f"entries_without_esocial: {entries_without_esocial.count()}")
        print(
            f"entries_without_esocial_not_in_demonstrative_itens: {entries_without_esocial_not_in_demonstrative_itens.count()}"
        )
        entries_registry_in_registration = Event.objects.filter(
            oid__in=(
                str(reg)
                for reg in entries_without_esocial_not_in_demonstrative_itens.values_list(
                    "contracheque__servidor__matricula", flat=True
                )
            ),
            acronym__in=("s2200", "s2300", "s2400", "s2298"),
            is_invalid_cache=False,
            process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
        )
        print(
            f"entries_registry_in_registration: {entries_registry_in_registration.count()}"
        )
        entries_registry_not_in_registration = (
            len(
                set(
                    entries_without_esocial_not_in_demonstrative_itens.values_list(
                        "contracheque__servidor__matricula", flat=True
                    )
                )
            )
            - entries_registry_in_registration.count()
        )
        print(
            f"entries_registry_not_in_registration: {entries_registry_not_in_registration}"
        )
        registrys = set(
            entries_without_esocial_not_in_demonstrative_itens.values_list(
                "contracheque__servidor__matricula", flat=True
            )
        ) - set(
            [
                int(oid)
                for oid in entries_registry_in_registration.values_list(
                    "oid", flat=True
                )
            ]
        )
        for employee in Servidor.objects.filter(matricula__in=registrys):
            print(employee.type_by_possession, employee)
        # for entry in ExtractorPayroll.all_entries_by_reference_esocial(5, 2022).filter(event_esocial__isnull=True):
        #     print(entry.event_esocial, entry.folha.periodo.mes, entry.folha.periodo.ano, entry.status, entry.valor, entry.evento.numero, entry)
        print("-------------------------------------------")
        time.sleep(10)


if __name__ == "__main__":
    run()
