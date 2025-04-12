# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations, models
from django.conf import settings
from django.core.management import call_command


def up(apps, schema_editor):
    FIXTURES = (
        "fixtures/0025-choices-votes-type-fix.json",
        "fixtures/0026-choices-delivery-attempy-cancel-type.json",
    )

    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("loading fixtures ...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "judicial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0066_auto_20190212_1348"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliveryattempt",
            name="cancel_delivery",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="cancel_delivery_type",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                    (6, "Publica\xe7\xe3o em di\xe1rio Oficial"),
                    (7, "Entrega pelo \xd3rg\xe3o de Execu\xe7\xe3o"),
                    (8, "Devolvido ao \xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.RunPython(up, down),
        migrations.RunSQL(
            "INSERT INTO judicial_judicialchoice(choice_ptr_id) SELECT id FROM standard_choice WHERE app_label='judicial' AND name='DELIVERY_CANCELATION_REASON'",
            "SELECT 1",
        ),
    ]
