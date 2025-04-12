# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from django.conf import settings
from django.core.management import call_command

import os


FIXTURES = ("fixtures/rh_can_merge_naturalperson.json",)


def down_fake(apps, schema_editor):
    pass


def up_load_data(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def update_person_kind(apps, schema_editor):
    print("Correção do campo kind de Pessoa.")
    Person = apps.get_model("rh", "Pessoa")
    for person in Person.objects.filter():
        kind_old = person.kind

        kind_new = specialized_instance(person)._meta.model_name
        if (
            specialized_instance(person)._meta.model_name
            == "naturalpersonspecializedemployee"
        ):
            kind_new = "pessoafisica"
        elif specialized_instance(person)._meta.model_name in (
            "educationalinstitution",
            "institution",
        ):
            kind_new = "pessoajuridica"

        if kind_new != kind_old:
            print(
                "Pessoa: {} - kind antigo:{} - kind novo:{}".format(
                    person.nome, kind_old, kind_new
                )
            )
            Person.objects.filter(pk=person.pk).update(kind=kind_new)


def specialized_instance(person):
    inst = person
    if hasattr(inst, "pessoafisica"):
        inst = inst.pessoafisica
        if hasattr(inst, "lawyer"):
            inst = inst.lawyer
    elif hasattr(inst, "pessoajuridica"):
        inst = inst.pessoajuridica
        if hasattr(inst, "educationalinstitution"):
            inst = inst.educationalinstitution
        elif hasattr(inst, "institution"):
            inst = inst.institution
    elif hasattr(inst, "anonymousperson"):
        inst = inst.anonymousperson
    return inst


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0090_auto_20190610_1306"),
    ]

    operations = [
        migrations.RunPython(up_load_data, down_fake),
        migrations.RunPython(update_person_kind, down_fake),
    ]
