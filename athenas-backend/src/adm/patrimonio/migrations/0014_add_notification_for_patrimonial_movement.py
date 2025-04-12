# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import django.db.models.deletion
import standard.models
from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models

FIXTURES = ("fixtures/choices.json",)


def up_load_fixtures(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "adm", "patrimonio", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def down_load_fixtures(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0019_groupperson_locality"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("patrimonio", "0013_reverse_incorrect_writeoff_assets"),
    ]

    operations = [
        migrations.RunPython(up_load_fixtures, down_load_fixtures),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("content", models.TextField(null=True, blank=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                db_index=True,
                choices=[
                    (1, "Aberto"),
                    (2, "Aguardando recebimento"),
                    (3, "Recebido"),
                    (4, "Ci\xeancia"),
                    (5, "Cancelado"),
                    (6, "Autorizado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentologstatus",
            name="status",
            field=models.SmallIntegerField(
                db_index=True,
                choices=[
                    (1, "Aberto"),
                    (2, "Aguardando recebimento"),
                    (3, "Recebido"),
                    (4, "Ci\xeancia"),
                    (5, "Cancelado"),
                    (6, "Autorizado"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="assets_movement",
            field=models.ForeignKey(
                related_name="notifications",
                verbose_name="Movimenta\xe7\xe3o Patrimonial",
                to="patrimonio.Movimento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="notification",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="destiny_location",
            field=models.ForeignKey(
                related_name="destiny_of_notifications",
                verbose_name="Local de destino",
                to="rh.Lotacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="notification",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="origin_location",
            field=models.ForeignKey(
                related_name="origin_of_notifications",
                verbose_name="Local de origem",
                to="rh.Lotacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="notification",
            name="protocol",
            field=models.ForeignKey(
                related_name="notifications",
                blank=True,
                to="protocolo.Protocolo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="notification",
            name="protocol_movement",
            field=models.ForeignKey(
                related_name="notifications",
                verbose_name="Movimenta\xe7\xe3o de Protocolo",
                blank=True,
                to="protocolo.Movimentacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="notification",
            name="notified_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="notified_by",
            field=models.ForeignKey(
                related_name="patrimony_movement_notification",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
    ]
