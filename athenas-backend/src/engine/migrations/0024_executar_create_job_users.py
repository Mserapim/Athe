# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings
from django.core.management import call_command

from common.services.scripts.create_job_users import cria_usuarios


def forward(apps, schema_editor):
    print("Running forward...")
    cria_usuarios()


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("engine", "0023_executar_create_job_users")]

    operations = [
        migrations.RunPython(forward, backward),
    ]
