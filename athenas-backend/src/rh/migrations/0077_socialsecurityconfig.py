# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models


def up_mass_segregation(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath1 = os.path.join(BASE_DIR, "rh", "fixtures", "segregationplan.json")
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath1)
    call_command("loaddata", filepath1)


def up_ss_configs(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath2 = os.path.join(BASE_DIR, "rh", "fixtures", "socialsecurityconfig.json")
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath2)
    call_command("loaddata", filepath2)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0076_auto_20190108_1343"),
    ]

    operations = [
        migrations.RunPython(up_mass_segregation, down),
        migrations.CreateModel(
            name="SocialSecurityConfig",
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
                (
                    "regime",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Regime previdenci\xc3\xa1rio",
                        choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
                    ),
                ),
                (
                    "mass_segregation_plan",
                    models.PositiveSmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Sem segrega\xe7\xe3o da massa"),
                            (2, "Fundo em capitaliza\xe7\xe3o"),
                            (3, "Fundo em reparti\xe7\xe3o"),
                            (4, "Mantido pelo Tesouro"),
                        ],
                    ),
                ),
                ("start", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "end",
                    models.DateField(null=True, verbose_name="Data fim", blank=True),
                ),
                (
                    "organ",
                    models.ForeignKey(to="rh.PessoaJuridica", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
        ),
        migrations.AddField(
            model_name="servidor",
            name="public_service_entry",
            field=models.DateField(
                null=True,
                verbose_name="Data de entrada no servi\xe7o p\xfablico",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="stay_allowance",
            field=models.DateField(
                null=True,
                verbose_name="Data de vig\xeancia de abono de perman\xeancia",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="social_security",
            field=models.ForeignKey(
                blank=True,
                to="rh.SocialSecurityConfig",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up_ss_configs, down),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="judicial_decision",
            field=models.BooleanField(
                default=False, verbose_name="Decorrente de decis\xc3\xa3o judicial"
            ),
        ),
    ]
