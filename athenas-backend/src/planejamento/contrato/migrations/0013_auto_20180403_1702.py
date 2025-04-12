# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0062_auto_20180309_1645"),
        ("contrato", "0012_auto_20180122_1612"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgreementSupervisor",
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
                ("kind", models.PositiveSmallIntegerField(verbose_name="Tipo")),
                (
                    "publication_document",
                    models.CharField(
                        max_length=250, null=True, verbose_name="Portaria", blank=True
                    ),
                ),
                ("publication_document_date", models.DateField(null=True, blank=True)),
                (
                    "begin",
                    models.DateField(null=True, verbose_name="In\xedcio", blank=True),
                ),
                ("end", models.DateField(null=True, verbose_name="Fim", blank=True)),
                (
                    "observation",
                    models.TextField(
                        null=True, verbose_name="Observa\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "hiring_agreementsupervisor",
                "permissions": (
                    ("can_close_supervisor", "Pode encerrar atua\xe7\xe3o de fiscal"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SupervisorClassification",
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
                ("kind", models.PositiveSmallIntegerField()),
                ("active", models.BooleanField(default=True)),
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
                "db_table": "hiring_supervisorclassification",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="contrato",
            options={
                "permissions": (
                    ("can_view_all_agreement", "Pode visualizar todos os contratos"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="medicao",
            options={
                "ordering": ("-id",),
                "permissions": (
                    ("can_do_payment", "Pode lan\xe7ar pagamento"),
                    ("can_undo_payment", "Pode desfazer pagamento"),
                ),
            },
        ),
        migrations.AlterModelOptions(
            name="notaempenho",
            options={
                "ordering": ("-id",),
                "permissions": (
                    ("can_request_reinforcement", "Pode solicitar refor\xe7o"),
                    ("can_request_reversal", "Pode solicitar estorno"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="contrato",
            name="gestor",
            field=models.ForeignKey(
                related_name="contratos",
                blank=True,
                to="contrato.Gestor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="agreementsupervisor",
            name="agreement",
            field=models.ForeignKey(
                related_name="agreementsupervisors",
                verbose_name="Contrato",
                to="contrato.Contrato",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="agreementsupervisor",
            name="classifications",
            field=models.ManyToManyField(
                related_name="%(class)ss",
                verbose_name="Classifica\xe7\xf5es",
                to="contrato.SupervisorClassification",
            ),
        ),
        migrations.AddField(
            model_name="agreementsupervisor",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="agreementsupervisor",
            name="employee",
            field=models.ForeignKey(
                related_name="%(class)s",
                verbose_name="Servidor",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="agreementsupervisor",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="supervisorclassification",
            unique_together=set([("kind", "active")]),
        ),
        migrations.AlterUniqueTogether(
            name="agreementsupervisor",
            unique_together=set([("agreement", "employee")]),
        ),
    ]
