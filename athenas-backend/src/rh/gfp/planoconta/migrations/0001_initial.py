# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("standard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plano",
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
                ("titulo", models.CharField(max_length=60, null=True)),
                ("ano_calendario", models.IntegerField()),
                (
                    "tipo",
                    models.SmallIntegerField(
                        choices=[
                            (1, "CONSIGNA\xc7\xc3O"),
                            (2, "L\xcdQUIDO"),
                            (3, "PATRONAL"),
                            (4, "SAL\xc1RIO FAMILIA"),
                            (5, "AUX\xcdLIO TRANSPORTE"),
                            (6, "PENS\xc3O ALIMENTICIA"),
                            (7, "AUX\xcdLIO CRECHE"),
                            (8, "DEP. JUDICIAL"),
                        ]
                    ),
                ),
                ("agencia", models.CharField(max_length=15, null=True)),
                ("conta", models.CharField(max_length=15, null=True)),
                ("fonte", models.CharField(max_length=10, null=True, blank=True)),
                (
                    "invert_negative",
                    models.BooleanField(
                        default=False, verbose_name="Inverter caso negativo"
                    ),
                ),
            ],
            options={
                "ordering": ("ano_calendario", "folha_tipo", "pessoa_juridica", "tipo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PlanoConta",
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
                    "finalidade",
                    models.SmallIntegerField(
                        default=1, choices=[(1, "LIQUIDA\xc7\xc3O"), (2, "DESEMBOLSO")]
                    ),
                ),
                (
                    "tipo",
                    models.SmallIntegerField(
                        default=1,
                        blank=True,
                        choices=[(1, "ATIVO"), (2, "INATIVO"), (3, "PENSIONISTA")],
                    ),
                ),
                ("inscricao_ne", models.CharField(max_length=12)),
                ("evento_nld", models.CharField(max_length=12)),
                ("evento_nld_two", models.CharField(max_length=12, null=True)),
                ("evento_nlc", models.CharField(max_length=12)),
                ("classificacao_nld", models.CharField(max_length=12)),
                ("vpd", models.CharField(max_length=12, null=True)),
                ("classificacao_nlc", models.CharField(max_length=12)),
                (
                    "regime_previdenciario",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="Regime previdenci\xc3\xa1rio",
                        choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
                    ),
                ),
            ],
            options={
                "ordering": ("finalidade", "plano", "regime_previdenciario"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Provision",
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
                    "acquired",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Quantidade max."
                    ),
                ),
                (
                    "base_salary",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Base salarial",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "provisioned_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Valor aprovisionado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "paid_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Valor liquidado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "provisioned_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Patronal provisionado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "paid_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Patronal pago",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "previous_balance_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Saldo anterior valor",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "previous_balance_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Saldo anterior patronal",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "manual_balance_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Balan\xc3\xa7o valor",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "manual_balance_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Balan\xc3\xa7o patronal",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
            ],
            options={
                "ordering": (
                    "provision_manager__reference_year",
                    "provision_manager__reference_month",
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProvisionEmployee",
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
                    "info",
                    models.CharField(
                        default="", max_length=50, verbose_name="Info", db_index=True
                    ),
                ),
                (
                    "quantity",
                    models.PositiveSmallIntegerField(
                        default=12, verbose_name="Quantidade max."
                    ),
                ),
                (
                    "start_acquisition",
                    models.DateField(verbose_name="In\xedcio Aquisi\xe7\xe3o"),
                ),
                (
                    "end_acquisition",
                    models.DateField(verbose_name="Fim Aquisi\xe7\xe3o"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ProvisionManager",
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
                    "reference_year",
                    models.PositiveSmallIntegerField(
                        verbose_name="Ano de refer\xeancia"
                    ),
                ),
                (
                    "reference_month",
                    models.PositiveSmallIntegerField(
                        verbose_name="M\xeas de refer\xeancia"
                    ),
                ),
                (
                    "total_provisioned_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Valor aprovisionado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_paid_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Valor liquidado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_provisioned_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Patronal provisionado",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_paid_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Patronal pago",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_previous_balance_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Saldo anterior valor",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_previous_balance_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Saldo anterior patronal",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_manual_balance_value",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Balan\xe7o valor",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_manual_balance_employer",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Balan\xe7o patronal",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        blank=True,
                        verbose_name="Status",
                        choices=[
                            (1, "EM PRODU\xc7\xc3O"),
                            (2, "EM ANALISE"),
                            (3, "FECHADO"),
                            (4, "PROCESSADO"),
                        ],
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProvisionPlan",
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
                ("title", models.CharField(max_length=120, blank=True)),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(null=True, verbose_name="Fim vig\xeancia"),
                ),
                (
                    "type_provision",
                    models.IntegerField(
                        choices=[(1, "F\xc9RIAS"), (2, "13\xba SAL\xc1RIO")]
                    ),
                ),
                (
                    "update_previous_balance",
                    models.BooleanField(default=False, verbose_name="Atualiza saldo?"),
                ),
                (
                    "auto_balance_at_end_period",
                    models.BooleanField(
                        default=False, verbose_name="Zerar balan\xc3\xa7o?"
                    ),
                ),
                (
                    "paid_events_employer",
                    models.ManyToManyField(
                        related_name="plans_provisions_employer", to="gfp.Evento"
                    ),
                ),
                (
                    "paid_events_value",
                    models.ManyToManyField(
                        related_name="plans_provisions_value", to="gfp.Evento"
                    ),
                ),
                (
                    "provision_calc",
                    models.ForeignKey(
                        related_name="plans_provisions",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="C\xe1lculo",
                        blank=True,
                        to="standard.ClassCode",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("type_provision", "start_validity"),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="provisionmanager",
            name="provision_plan",
            field=models.ForeignKey(
                related_name="summaries",
                verbose_name="Plano de Provis\xe3o",
                to="planoconta.ProvisionPlan",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
