# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0034_auto_20161111_1000"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("planoconta", "0006_auto_20161111_0957"),
        ("standard", "0003_auto_20161028_1055"),
        ("gfp", "0026_auto_20160919_1455"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinancialReportPayroll",
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
                    "quantity",
                    models.PositiveIntegerField(default=0, verbose_name="Quantidade"),
                ),
                (
                    "value",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor total",
                        max_digits=19,
                        decimal_places=2,
                    ),
                ),
                (
                    "account_plan",
                    models.ForeignKey(
                        related_name="financial_summary",
                        verbose_name="PlanoConta",
                        to="planoconta.PlanoConta",
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
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OverviewReport",
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
                    "type_of_employee",
                    models.PositiveSmallIntegerField(default=1, verbose_name="Tipo"),
                ),
                (
                    "value",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor total",
                        max_digits=19,
                        decimal_places=2,
                    ),
                ),
                (
                    "employer_contribution",
                    models.DecimalField(
                        default=0,
                        verbose_name="Patronal total",
                        max_digits=19,
                        decimal_places=2,
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=0, verbose_name="Quantidade"),
                ),
                (
                    "type_of_entry",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Tipo de Lan\xe7amento"
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
                    "event",
                    models.ForeignKey(
                        related_name="overview_summary",
                        verbose_name="Evento",
                        to="gfp.Evento",
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RemoveField(
            model_name="historicoservidorverbaadicional",
            name="evento",
        ),
        migrations.RemoveField(
            model_name="historicoservidorverbaadicional",
            name="publicacao",
        ),
        migrations.RemoveField(
            model_name="historicoservidorverbaadicional",
            name="servidor",
        ),
        migrations.RemoveField(
            model_name="nivelsalarial",
            name="categoria",
        ),
        migrations.RemoveField(
            model_name="nivelsalarial",
            name="estrutura_salarial",
        ),
        migrations.RemoveField(
            model_name="perfilprevidencia",
            name="evento",
        ),
        migrations.RemoveField(
            model_name="perfilprevidencia",
            name="pessoa_juridica",
        ),
        migrations.RemoveField(
            model_name="servidorverbaadicional",
            name="evento",
        ),
        migrations.RemoveField(
            model_name="servidorverbaadicional",
            name="publicacao",
        ),
        migrations.RemoveField(
            model_name="servidorverbaadicional",
            name="servidor",
        ),
        migrations.AlterModelOptions(
            name="contracheque",
            options={"ordering": ("folha", "servidor", "-pensioner")},
        ),
        migrations.AlterModelOptions(
            name="folhamodelo",
            options={"ordering": ["titulo"]},
        ),
        migrations.RemoveField(
            model_name="referencianiveis2d",
            name="cargos",
        ),
        migrations.RemoveField(
            model_name="referencianiveis2d",
            name="estrutura_salarial",
        ),
        migrations.RemoveField(
            model_name="referencianiveis2d",
            name="nivel_horizontal",
        ),
        migrations.RemoveField(
            model_name="referencianiveis2d",
            name="nivel_vertical",
        ),
        migrations.AddField(
            model_name="contracheque",
            name="classification",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Classifica\xe7\xe3o"
            ),
        ),
        migrations.AddField(
            model_name="contracheque",
            name="employee_pays_pension",
            field=models.PositiveIntegerField(default=0, verbose_name="Pens\xe3o"),
        ),
        migrations.AddField(
            model_name="contracheque",
            name="employee_source",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Tipo de servidor"
            ),
        ),
        migrations.AddField(
            model_name="contracheque",
            name="error_validations",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Erro de valida\xc3\xa7\xc3\xb5es", blank=True
            ),
        ),
        migrations.AddField(
            model_name="contracheque",
            name="pensioner",
            field=models.ForeignKey(
                related_name="pension_paychecks",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Pensionista",
                blank=True,
                to="rh.PessoaFisica",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="calculation",
            field=models.ForeignKey(
                related_name="entries",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="C\xe1lculo",
                blank=True,
                to="standard.ClassCode",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="correct_base_value",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="correct_pct",
            field=models.DecimalField(
                null=True, max_digits=10, decimal_places=6, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="correct_qnt",
            field=models.DecimalField(
                default=0, max_digits=10, decimal_places=6, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="entry_pension",
            field=models.ForeignKey(
                related_name="entries_pay_pension",
                blank=True,
                to="gfp.FolhaEvento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="folhamensagem",
            name="entry",
            field=models.ForeignKey(
                related_name="messages",
                verbose_name="Lan\xe7amento",
                blank=True,
                to="gfp.FolhaEvento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="folhamensagem",
            name="label",
            field=models.PositiveSmallIntegerField(
                default=0, null=True, verbose_name="Refer\xc3\xaancia", blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhamensagem",
            name="paycheck",
            field=models.ForeignKey(
                related_name="messages",
                verbose_name="Contracheque",
                blank=True,
                to="gfp.ContraCheque",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="referencia_comissao_cache",
            field=models.CharField(default="", max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="referencia_efetivo_cache",
            field=models.CharField(default="", max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="referencia_eletivo_cache",
            field=models.CharField(default="", max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="status",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Status", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="folha",
            name="status",
            field=models.SmallIntegerField(
                default=1, verbose_name="Status", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="evento",
            field=models.ForeignKey(
                related_name="lancamentos",
                blank=True,
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="folha",
            field=models.ForeignKey(
                related_name="lancamentos",
                blank=True,
                to="gfp.Folha",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="lancamento",
            field=models.CharField(
                blank=True,
                max_length=1,
                choices=[("T", "TEMPOR\xc1RIO"), ("F", "FIXO")],
            ),
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="rra_employee",
            field=models.ForeignKey(
                related_name="entries",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="RRA Servidor",
                blank=True,
                to="gfp.RRAEmployee",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="servidor",
            field=models.ForeignKey(
                related_name="com_evento_folha",
                blank=True,
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhamensagem",
            name="folha",
            field=models.ForeignKey(
                related_name="messages",
                verbose_name="Folha",
                blank=True,
                to="gfp.Folha",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhamensagem",
            name="servidor",
            field=models.ForeignKey(
                related_name="messages",
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhatipo",
            name="titulo",
            field=models.CharField(max_length=30, verbose_name="T\xedtluo"),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
                    (39, "VERBAS EXERCICIOS ANTERIORES"),
                    (1, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                    (3, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o"),
                    (4, "REMUNERA\xc7\xc3O: VPI"),
                    (5, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                    (6, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                    (7, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                    (8, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                    (9, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                    (10, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                    (11, "EFEITOS NEGATIVOS: Redutor de Teto"),
                    (12, "DEDU\xc7\xd4ES: IRRF"),
                    (13, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                    (14, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                    (15, "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio"),
                    (16, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                    (17, "INDENIZAT\xd3RIAS: Aux. Creche"),
                    (18, "INDENIZAT\xd3RIAS: Aux. Moradia"),
                    (19, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                    (20, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                    (21, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                    (22, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                    (23, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                    (24, "INDENIZAT\xd3RIAS: IRRF"),
                    (25, "Remunera\xe7\xe3o do Cargo Efetivo"),
                    (26, "Outras Verbas Remunerat\xf3rias, Legais ou Judiciais"),
                    (27, "Fun\xe7\xe3o de Confian\xe7a"),
                    (28, "Vencimento"),
                    (29, "Gratifica\xe7\xe3o"),
                    (30, "Gratifica\xe7\xe3o Natalina"),
                    (31, "F\xe9rias Constitucionais"),
                    (32, "Abono Perman\xeancia"),
                    (33, "Contribui\xe7\xe3o Previdenci\xe1ria"),
                    (34, "Imposto de Renda"),
                    (35, "Reten\xe7\xe3o por Teto Constitucional"),
                    (36, "Outros Redutores/Descontos"),
                    (37, "INDENIZA\xc7\xd5ES"),
                    (38, "OUTRAS REMUNERA\xc7\xd5ES RETROATIVAS/TEMPOR\xc1RIAS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="status",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Status"),
        ),
        migrations.AlterField(
            model_name="movimentacaoprogressao",
            name="months_progression",
            field=models.PositiveSmallIntegerField(
                default=12, verbose_name="Meses progress\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao",
            field=models.SmallIntegerField(default=1, verbose_name="Gratif. Servidor"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao_membro",
            field=models.SmallIntegerField(default=1, verbose_name="Gratif. Membro"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor",
            field=models.SmallIntegerField(default=1, verbose_name="Valor Servidor"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor_membro",
            field=models.SmallIntegerField(default=1, verbose_name="Valor Membro"),
        ),
        migrations.AlterUniqueTogether(
            name="contracheque",
            unique_together=set([("servidor", "folha", "pensioner")]),
        ),
        migrations.AlterUniqueTogether(
            name="folhamensagem",
            unique_together=set([]),
        ),
        migrations.DeleteModel(
            name="HistoricoServidorVerbaAdicional",
        ),
        migrations.DeleteModel(
            name="NivelSalarial",
        ),
        migrations.DeleteModel(
            name="PerfilPrevidencia",
        ),
        migrations.DeleteModel(
            name="ServidorVerbaAdicional",
        ),
        migrations.AddField(
            model_name="overviewreport",
            name="payroll",
            field=models.ForeignKey(
                related_name="overview_summary",
                verbose_name="Folha",
                to="gfp.Folha",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="financialreportpayroll",
            name="payroll",
            field=models.ForeignKey(
                related_name="financial_summary",
                verbose_name="Folha",
                to="gfp.Folha",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterUniqueTogether(
            name="financialreportpayroll",
            unique_together=set([("payroll", "account_plan")]),
        ),
    ]
