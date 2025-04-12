# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db.models import Count, Q
from rh.models import Servidor
from rh.gfp.models import ContraCheque, FolhaEvento
from esocial.models import Event, Demonstrative, Demonstrative1202, Demonstrative1207


def _update_dm_dev(acronym, dm_dev):
    dm_class = Demonstrative

    paycheck = ContraCheque.objects.filter(pk=dm_dev.oid).last()
    if paycheck:
        dt = paycheck.folha.dt_pagamento

    total_net = 0
    registry_employee = None

    """S1200"""
    if acronym == "1200":
        """PER_APUR"""
        for info_per_apur_ide_estab_lot in dm_dev.info_per_apur_ide_estab_lot.filter():
            for remun_period in info_per_apur_ide_estab_lot.remun_period.filter():
                registry_employee = remun_period.matricula
                for itens_remun in remun_period.itens_remun.filter():
                    if itens_remun.oid.isdigit():
                        entry = FolhaEvento.objects.filter(pk=itens_remun.oid).last()
                        if entry:
                            # print(itens_remun, entry.value, entry)
                            total_net += entry.value

        for ide_adc in dm_dev.ide_adc.filter():
            for ide_period in ide_adc.ide_period.filter():
                for (
                    info_per_ant_ide_estab_lot
                ) in ide_period.info_per_ant_ide_estab_lot.filter():
                    for (
                        remun_period
                    ) in info_per_ant_ide_estab_lot.remun_period.filter():
                        registry_employee = remun_period.matricula
                        for itens_remun in remun_period.itens_remun.filter():
                            if itens_remun.oid.isdigit():
                                entry = FolhaEvento.objects.filter(
                                    pk=itens_remun.oid
                                ).last()
                                if entry:
                                    # print(itens_remun, entry.value, entry)
                                    total_net += entry.value

    """S1202"""
    if acronym == "1202":
        dm_class = Demonstrative1202
        for info_per_apur_ide_estab_lot in dm_dev.info_per_apur_ide_estab_lot.filter():
            for remun_period in info_per_apur_ide_estab_lot.remun_period.filter():
                registry_employee = remun_period.matricula
                for itens_remun in remun_period.itens_remun.filter():
                    if itens_remun.oid.isdigit():
                        entry = FolhaEvento.objects.filter(pk=itens_remun.oid).last()
                        if entry:
                            # print(itens_remun, entry.value, entry)
                            total_net += entry.value

        for ide_period in dm_dev.ide_period.filter():
            for (
                info_per_ant_ide_estab_lot
            ) in ide_period.info_per_ant_ide_estab_lot.filter():
                for remun_period in info_per_ant_ide_estab_lot.remun_period.filter():
                    registry_employee = remun_period.matricula
                    for itens_remun in remun_period.itens_remun.filter():
                        if itens_remun.oid.isdigit():
                            entry = FolhaEvento.objects.filter(
                                pk=itens_remun.oid
                            ).last()
                            if entry:
                                # print(itens_remun, entry.value, entry)
                                total_net += entry.value

    """S1207"""
    if acronym == "1207":
        dm_class = Demonstrative1207
        registry_employee = Servidor.objects.filter(
            pessoa_fisica__cpf=dm_dev.registry_person,
            type_by_possession__in=("BFP", "SAP", "MAP"),
        ).last()
        if registry_employee:
            registry_employee = registry_employee.matricula
        for info_per_apur_ide_estab_lot in dm_dev.info_per_apur_ide_estab_lot.filter():
            for itens_remun in info_per_apur_ide_estab_lot.itens_remun.filter():
                if itens_remun.oid.isdigit():
                    entry = FolhaEvento.objects.filter(pk=itens_remun.oid).last()
                    if entry:
                        # print(itens_remun, entry.value, entry)
                        total_net += entry.value

        for ide_period in dm_dev.ide_period.filter():
            for (
                info_per_ant_ide_estab_lot
            ) in ide_period.info_per_ant_ide_estab_lot.filter():
                for itens_remun in info_per_ant_ide_estab_lot.itens_remun.filter():
                    if itens_remun.oid.isdigit():
                        entry = FolhaEvento.objects.filter(pk=itens_remun.oid).last()
                        if entry:
                            # print(itens_remun, entry.value, entry)
                            total_net += entry.value

    if not registry_employee:
        registry_employee = Servidor.objects.filter(
            pessoa_fisica__cpf=dm_dev.registry_person, type_by_possession="COE"
        ).last()
        if registry_employee:
            registry_employee = registry_employee.matricula

    dm_class.objects.filter(pk=dm_dev).update(
        info_pgto_dt_pgto=dt,
        info_pgto_vr_liq=total_net,
        registry_employee=registry_employee,
    )
    message = f"{dm_dev.ide_evento_per_apur} | {dm_class.__name__} | {dm_dev.pk} | {dm_dev.oid} | {registry_employee}"
    message += f" | {dm_dev.info_pgto_vr_liq} => {total_net} | {dm_dev.info_pgto_dt_pgto} => {dt}\n"
    print(message)
    return 1


def run_datamigration():
    events = (
        Event.objects.filter(acronym__in=("s1200", "s1202", "s1207"))
        .exclude(is_invalid_cache=True)
        .exclude(process_status=401)
    )

    total = 0
    count = 0
    print()
    per_refs = (
        events.values("ide_evento_per_apur")
        .order_by("ide_evento_per_apur")
        .annotate(count_rra_employee=Count("ide_evento_per_apur"))
    )
    for per_ref in (value.get("ide_evento_per_apur") for value in per_refs):
        print(per_ref)
        for event in events.filter(ide_evento_per_apur=per_ref).order_by(
            "competence_year", "competence_month", "pk"
        ):
            query = Demonstrative.objects.filter(s1200=event).filter(
                Q(info_pgto_dt_pgto__isnull=True)
                | Q(info_pgto_vr_liq__isnull=True)
                | Q(registry_employee__isnull=True)
            )
            for dm_dev in query:
                total += 1
                count += _update_dm_dev("1200", dm_dev)

            query = Demonstrative1202.objects.filter(s1202=event).filter(
                Q(info_pgto_dt_pgto__isnull=True)
                | Q(info_pgto_vr_liq__isnull=True)
                | Q(registry_employee__isnull=True)
            )
            for dm_dev in query:
                total += 1
                count += _update_dm_dev("1202", dm_dev)

            query = Demonstrative1207.objects.filter(s1207=event).filter(
                Q(info_pgto_dt_pgto__isnull=True)
                | Q(info_pgto_vr_liq__isnull=True)
                | Q(registry_employee__isnull=True)
            )
            for dm_dev in query:
                total += 1
                count += _update_dm_dev("1207", dm_dev)

    print(f"Finalizado {count} de {total}.")


if __name__ == "__main__":
    print(
        """Este scritp atualiza info_pgto_dt_pgto e info_pgto_vr_liq dos demonstrativos que possuem estes valores."""
    )
    run_datamigration()
