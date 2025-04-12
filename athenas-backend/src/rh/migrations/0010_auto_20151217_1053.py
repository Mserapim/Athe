# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_instances_on_cargo(apps, schema_editor):
    JobPosition = apps.get_model("rh", "Cargo")
    e1 = JobPosition.objects.filter(entrancia__nome="PRIMEIRA ENTRÂNCIA").update(
        level_instance=1
    )
    e2 = JobPosition.objects.filter(entrancia__nome="SEGUNDA ENTRÂNCIA").update(
        level_instance=2
    )
    e3 = JobPosition.objects.filter(entrancia__nome="TERCEIRA ENTRÂNCIA").update(
        level_instance=3
    )
    e4 = JobPosition.objects.filter(entrancia__nome="PROCURADORIA ENTRÂNCIA").update(
        level_instance=4
    )

    i1 = JobPosition.objects.filter(instancia__nome="PRIMEIRA INSTÂNCIA").update(
        instance=1
    )
    i2 = JobPosition.objects.filter(instancia__nome="SEGUNDA INSTÂNCIA").update(
        instance=2
    )
    print(
        "UPDATING 1E: %d 2E: %d 3E: %d 4E: %d 1I: %d 2I: %d" % (e1, e2, e3, e4, i1, i2)
    )


def backward(apps, schema_editor):
    JobPosition = apps.get_model("rh", "Cargo")
    JobPosition.objects.update(instance=None, level_instance=None)


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0009_auto_20151217_1047"),
    ]

    operations = [migrations.RunPython(update_instances_on_cargo, backward)]
