# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0066_auto_20180830_1454"),
        ("contrato", "0018_auto_20180814_1733"),
    ]

    operations = [
        migrations.CreateModel(
            name="MinuteSolicitationRequisition",
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
                    "number",
                    models.CharField(
                        max_length=10,
                        null=True,
                        verbose_name="N\xfamero da Requisi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "object_execution",
                    models.TextField(verbose_name="Execu\xc3\xa7\xc3\xa3o do Objeto"),
                ),
                (
                    "signature_date",
                    models.DateField(
                        null=True, verbose_name="Data da Assinatura", blank=True
                    ),
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
                (
                    "expense_approver",
                    models.ForeignKey(
                        related_name="minutesolicitationrequisitions",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Cargo",
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        related_name="minutesolicitationrequisitions",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Servidor",
                    ),
                ),
                (
                    "solicitation",
                    models.ForeignKey(
                        related_name="minutesolicitationrequisitions",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contrato.MinuteSolicitation",
                    ),
                ),
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitationrequisition",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="contrato",
            name="solicitation",
            field=models.ForeignKey(
                related_name="contratos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="contrato.MinuteSolicitation",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="minuteitemaction",
            name="action",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Reativar"),
                    (2, "Desativar"),
                    (3, "Revogar"),
                    (4, "Aditivar"),
                    (5, "Invalido"),
                ]
            ),
        ),
    ]
