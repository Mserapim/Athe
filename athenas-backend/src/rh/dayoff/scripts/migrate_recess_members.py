# -.- coding: utf-8 -.-
"""
    Este script períodos aquisitivos criados automaticamente(que não possuem usufruto), e faz a migração dos períodos aquisitivos dos membros
    que estão na configuração de servidor.
    Também fará atualização das anotações do período aquisitivo e das atividades.
"""
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.dayoff.models import *
from rh.dayoff.const import *

from contrib.utils import getLogger

log = getLogger(__name__)

set_current_user("athenas")


def update_annotation(pks):
    print("Atualizando anotações.")
    for aq in AcquisitionPeriod.objects.filter(pk__in=pks):
        for act in aq.activities.filter():
            act = act.my_origin
            act.update_annotation()
        aq.update_annotation()


def migrate():
    pks = []
    for aq in (
        AcquisitionPeriod.objects.filter(
            group_period__configuration__type_of_usufruct=CONF_RECESS,
            employee__tipo="M",
        )
        .exclude(
            group_period__configuration__type_employees__cvalue__in=[
                "MBR",
                "MEL",
                "MCM",
                "MEC",
                "MBR2",
                "MEL2",
                "MCM2",
                "MEC2",
                "MAP",
            ]
        )
        .order_by("group_period__year_reference", "employee")
    ):
        group = (
            GroupPeriod.objects.filter(
                year_reference=aq.group_period.year_reference,
                period=aq.group_period.period,
                configuration__type_of_usufruct=aq.group_period.configuration.type_of_usufruct,
                configuration__type_employees__cvalue__in=[
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "MAP",
                ],
            )
            .exclude(pk=aq.group_period.pk)
            .last()
        )
        if group:
            to_delete = (
                AcquisitionPeriod.objects.filter(
                    group_period=group, employee=aq.employee
                )
                .exclude(pk=aq.pk)
                .last()
            )
            if to_delete:
                if to_delete.usufructs.filter().exists():
                    raise Exception(
                        f"Não é possível apagar {to_delete} pois possui usufrutos vinculados!"
                    )
                to_delete.delete()
            print(f"MIGRANDO: {aq} | PARA | {group}")
            AcquisitionPeriod.objects.filter(pk=aq.pk).update(group_period=group)
            pks.append(aq.pk)
            print("--------------------------------------")

    update_annotation(pks)


def run():
    migrate()


if __name__ == "__main__":
    run()
