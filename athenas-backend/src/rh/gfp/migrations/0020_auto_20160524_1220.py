# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0021_auto_20160512_1034"),
        ("gfp", "0019_auto_20160510_0854"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankingEmployeeTypePayroll",
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
                    "banking_person",
                    models.ForeignKey(
                        related_name="bankings_employee_payroll",
                        to="rh.DadoBancarioPessoa",
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
                    "person",
                    models.ForeignKey(
                        related_name="bankings_employee_payroll",
                        verbose_name="Pessoa",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "type_of_payroll",
                    models.ForeignKey(
                        related_name="bankings_employee_payroll",
                        verbose_name="Tipo de folha",
                        to="gfp.FolhaTipo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["banking_person__pessoa", "type_of_payroll"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="evento",
            name="active",
            field=models.BooleanField(default=True, verbose_name="Ativo?"),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="automated",
            field=models.BooleanField(default=False, verbose_name="Automatizado?"),
        ),
        migrations.AlterField(
            model_name="evento",
            name="numero",
            field=models.CharField(
                unique=True, max_length=5, verbose_name="N\xfamero", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="transparencychoice",
            name="group",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Grupos",
                choices=[
                    (3, "Rendimento L\xedquido Total"),
                    (38, "Outras remuneracoes/Temporarias"),
                ],
            ),
        ),
        migrations.AlterUniqueTogether(
            name="bankingemployeetypepayroll",
            unique_together=set([("person", "type_of_payroll")]),
        ),
    ]
