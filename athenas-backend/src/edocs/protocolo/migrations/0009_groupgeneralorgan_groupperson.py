# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0008_auto_20151120_1117"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupGeneralOrgan",
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
                ("title", models.CharField(max_length=100, verbose_name="T\xedtulo")),
                (
                    "level_access",
                    models.PositiveSmallIntegerField(
                        verbose_name="Acesso",
                        choices=[(1, "Global"), (2, "Departamental")],
                    ),
                ),
                (
                    "all_work_location",
                    models.BooleanField(
                        default=False, verbose_name="Todos Locais de Trabalho"
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        related_name="group_general_organ",
                        verbose_name="Departamento",
                        to="rh.Lotacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "general_organ",
                    models.ManyToManyField(
                        related_name="in_group_general_organ",
                        verbose_name="Org\xe3o Geral",
                        to="rh.OrgaoGeral",
                    ),
                ),
            ],
            options={
                "ordering": ["title"],
                "verbose_name": "Grupo de \xd3rg\xe3o Geral",
                "permissions": (
                    (
                        "group_general_organ_admin_global_distribution",
                        "Pode administrar lista de distribui\xe7\xe3o global",
                    ),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GroupPerson",
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
                ("title", models.CharField(max_length=100, verbose_name="T\xedtulo")),
                (
                    "level_access",
                    models.PositiveSmallIntegerField(
                        verbose_name="Acesso",
                        choices=[(1, "Global"), (2, "Departamental")],
                    ),
                ),
                (
                    "all_employees",
                    models.BooleanField(default=False, verbose_name="Servidores"),
                ),
                (
                    "all_members",
                    models.BooleanField(default=False, verbose_name="Membros"),
                ),
                (
                    "department",
                    models.ForeignKey(
                        related_name="group_person",
                        verbose_name="Departamento",
                        to="rh.Lotacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "persons",
                    models.ManyToManyField(
                        related_name="in_group_person",
                        verbose_name="Pessoas",
                        to="rh.Pessoa",
                    ),
                ),
            ],
            options={
                "ordering": ["title"],
                "verbose_name": "Grupo de Pessoas",
                "permissions": (
                    (
                        "group_person_admin_global_distribution",
                        "Pode administrar lista de distribui\xe7\xe3o global",
                    ),
                ),
            },
            bases=(models.Model,),
        ),
    ]
