# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0048_personhasaccess_controlled"),
        ("inspection", "0003_auto_20180530_1506"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProceduralMovement",
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
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "MOviemnta\xe7\xe3o processual da Procuradoria",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProceduralMovementOutCourtLawsuit",
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
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Recebidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProceduralMovementReceived",
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
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Recebidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProceduralMovementReturned",
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
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Recebidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcForQualAnalysisOfThePartsProcuratorate",
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
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("report", models.CharField(max_length=2000)),
                ("basis", models.CharField(max_length=2000)),
                ("proof", models.CharField(max_length=2000)),
                ("convincily", models.CharField(max_length=2000)),
                ("redaction", models.CharField(max_length=2000)),
                (
                    "score",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Processos para An\xe1lise qualitativa das pe\xe7as de Procuradorias",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="inspection",
            name="collegiate_organ_session",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="inspection",
            name="commissions_session",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="inspection",
            name="number_collegiate_organ_session",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inspection",
            name="tj_session",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="inspection",
            name="tj_sessions_administrative",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inspection",
            name="tj_sessions_civil",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inspection",
            name="tj_sessions_criminal",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="inspector_prosecutor",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="processesforanalysisperformanceinaudiences",
            name="audience_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Audi\xeancia",
                blank=True,
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Concilia\xe7\xe3o"),
                    (3, "Instru\xe7\xe3o"),
                    (4, "Julgamento"),
                    (5, "Instru\xe7\xe3o e Julgamento"),
                    (6, "Preliminar"),
                    (7, "Interrogat\xf3rio"),
                    (8, "Inquiri\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="part_type",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMoviment",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="proceduralmovementreturned",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="proceduralmovementreturned",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="proceduralmovementreceived",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="proceduralmovementreceived",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="proceduralmovementoutcourtlawsuit",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="proceduralmovementoutcourtlawsuit",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="proceduralmovement",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="proceduralmovement",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
