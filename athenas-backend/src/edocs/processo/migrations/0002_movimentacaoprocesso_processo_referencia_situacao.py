# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0001_initial"),
        ("processo", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MovimentacaoProcesso",
            fields=[
                (
                    "movimentacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.Movimentacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("paginas", models.SmallIntegerField(default=0, null=True)),
                ("volume", models.SmallIntegerField(null=True)),
            ],
            options={
                "db_table": "epad_movimentacao",
            },
            bases=("protocolo.movimentacao",),
        ),
        migrations.CreateModel(
            name="Processo",
            fields=[
                (
                    "protocolo_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.Protocolo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("codigo_processo", models.CharField(unique=True, max_length=50)),
                ("numero", models.IntegerField()),
                ("ano", models.SmallIntegerField()),
                ("paginas", models.SmallIntegerField()),
                ("volume", models.SmallIntegerField()),
                ("motivo_excluido", models.TextField(null=True)),
                ("manual", models.BooleanField(default=False)),
                ("caixa", models.CharField(max_length=200, null=True)),
                (
                    "assunto_processo",
                    models.ForeignKey(to="processo.Assunto", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "epad_processo",
                "permissions": (("admin", "Vis\xe3o administrativa"),),
            },
            bases=("protocolo.protocolo",),
        ),
        migrations.CreateModel(
            name="Referencia",
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
                    "tipo",
                    models.SmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Anexa\xe7\xe3o"),
                            (2, "Apensa\xe7\xe3o"),
                            (3, "Desapensa\xe7\xe3o"),
                        ],
                    ),
                ),
                ("data", models.DateField()),
                ("descricao", models.CharField(max_length=300)),
                (
                    "processo",
                    models.ForeignKey(
                        related_name="proc_referencias",
                        to="processo.Processo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "referenciado",
                    models.ForeignKey(
                        related_name="proc_referenciado_por",
                        to="processo.Processo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("data",),
                "db_table": "epad_referencia",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Situacao",
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
                ("nome", models.CharField(max_length=200)),
            ],
            options={
                "ordering": ("nome",),
                "db_table": "epad_situacao",
            },
            bases=(models.Model,),
        ),
    ]
