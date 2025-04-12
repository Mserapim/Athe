# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0041_remove_replacement"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("raf", "0022_auto_20180201_1349"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchByNumber",
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
                ("contenttype", models.CharField(max_length=100)),
                ("source", models.SmallIntegerField()),
                ("process_number", models.CharField(max_length=100)),
                ("process_number_formatted", models.CharField(max_length=100)),
                ("matricula", models.IntegerField()),
                ("membro", models.CharField(max_length=200)),
                ("month", models.IntegerField()),
                ("year", models.IntegerField()),
                ("date", models.DateField()),
                (
                    "analisys",
                    models.PositiveSmallIntegerField(
                        null=True,
                        verbose_name="An\xe1lise",
                        choices=[
                            (0, "N\xe3o analisado"),
                            (1, "Processo classificado com sucesso"),
                            (2, "Sem promotoria registrada para o processo"),
                            (3, "N\xe3o encontrou question\xe1rio para o processo"),
                            (4, "N\xe3o encontrou linha para o processo"),
                            (5, "N\xe3o encontrou coluna para o processo"),
                            (6, "Sem classe registrada para o processo"),
                            (7, "Sem assunto registrado para o processo"),
                            (8, "Sem movimento registrado para o processo"),
                        ],
                    ),
                ),
                ("situation", models.IntegerField(null=True)),
                (
                    "operation",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="A\xe7\xe3o da Solicita\xe7\xe3o de Ajuste",
                        choices=[(1, "ADICIONAR"), (2, "REMOVER")],
                    ),
                ),
            ],
            options={
                "ordering": ["process_number_formatted", "date"],
                "db_table": "raf_searchbynumber_vw",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DataAdjustment",
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
                (
                    "operation",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="A\xe7\xe3o da Solicita\xe7\xe3o de Ajuste",
                        choices=[(1, "ADICIONAR"), (2, "REMOVER")],
                    ),
                ),
                (
                    "process_number",
                    models.TextField(verbose_name="Numero de identifica\xe7\xe3o"),
                ),
                (
                    "source",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Origem",
                        blank=True,
                        choices=[
                            (1, "E-PROC"),
                            (2, "E-EXT"),
                            (3, "SIACMP"),
                            (4, "REGISTRO INTERNO"),
                        ],
                    ),
                ),
                ("date", models.DateField(null=True, verbose_name="Data da atividade")),
                ("initial_message", models.TextField(blank=True)),
                (
                    "situation",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Situa\xe7\xe3o",
                        choices=[
                            (0, "N\xe3o avaliado"),
                            (1, "Aguardando informa\xe7\xf5es"),
                            (2, "Deferido"),
                            (3, "Indeferido"),
                            (4, "Cancelado"),
                            (5, "N\xe3o enviado"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": ["operation", "date"],
                "verbose_name": "Listagem de processos/procedimentos a serem adicionados em atividade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="autoreference",
            name="is_adjustment",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="autoreference",
            name="removed",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="autoreference",
            name="source_add",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                blank=True,
                choices=[
                    (1, "E-PROC"),
                    (2, "E-EXT"),
                    (3, "SIACMP"),
                    (4, "REGISTRO INTERNO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="amount",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="initial_message",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="situation",
            field=models.PositiveSmallIntegerField(
                default=5,
                null=True,
                verbose_name="Situa\xe7\xe3o",
                blank=True,
                choices=[
                    (0, "N\xe3o avaliado"),
                    (1, "Aguardando informa\xe7\xf5es"),
                    (2, "Deferido"),
                    (3, "Indeferido"),
                    (4, "Cancelado"),
                    (5, "N\xe3o enviado"),
                    (6, "Avaliado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="subitem",
            name="productivity",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Produtividade", blank=True
            ),
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="activityadjustment",
            field=models.ForeignKey(
                related_name="dataadjustment",
                to="raf.ActivityAdjustment",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="conversation",
            field=models.OneToOneField(
                null=True, blank=True, to="raf.Conversation", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="legalclass",
            field=models.ForeignKey(
                related_name="dataadjustment_legalclass",
                blank=True,
                to="judicial.LegalClass",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="legalmatter",
            field=models.ForeignKey(
                related_name="dataadjustment_legalmatter",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="dataadjustment",
            name="movement",
            field=models.ForeignKey(
                related_name="dataadjustment_movement",
                to="judicial.LegalMoviment",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
