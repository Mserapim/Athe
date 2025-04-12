# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0036_scientifyworkplace_content"),
        ("raf", "0013_auto_20171011_0832"),
    ]

    operations = [
        migrations.CreateModel(
            name="NonProceduralActivities",
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
                ("date", models.DateField(verbose_name="Data")),
                (
                    "description",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("title", models.CharField(max_length=128, verbose_name="T\xedtulo")),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "legal_procedure",
                    models.ForeignKey(
                        related_name="nonproceduralactivities",
                        verbose_name="Procedimento Legal",
                        to="judicial.LegalProcedure",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "member",
                    models.ForeignKey(
                        related_name="nonproceduralactivities",
                        verbose_name="Membro",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Atividades n\xe3o procedimentais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="situation",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (0, "N\xe3o avaliado"),
                    (1, "Aguardando informa\xe7\xf5es"),
                    (2, "Deferido"),
                    (3, "Indeferido"),
                    (4, "Cancelado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="autoreference",
            name="process_number",
            field=models.TextField(verbose_name="Numero de identifica\xe7\xe3o"),
        ),
        migrations.AlterField(
            model_name="autoreference",
            name="source",
            field=models.TextField(verbose_name="Origem da informa\xe7\xe3o"),
        ),
        migrations.AlterField(
            model_name="subitem",
            name="typesubitem",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="Tipo",
                choices=[
                    (0, "N\xe3o informado"),
                    (1, "Estat\xedsticas/Quantidade"),
                    (2, "Movimentos"),
                ],
            ),
        ),
    ]
