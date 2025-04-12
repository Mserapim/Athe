# -*- coding: utf-8 -*-
from django.db import migrations

from common.services.scripts.create_job_users import cria_usuarios


def forward(apps, schema_editor):
    print("Running forward...")
    cria_usuarios()


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("diarias", "0066_load_fixtures_convenio_bb")]

    operations = [
        migrations.RunPython(forward, backward),
    ]
