# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0049_auto_20180424_1442"),
    ]

    operations = [
        migrations.AddField(
            model_name="bankingconvenant",
            name="excluded_bank",
            field=models.ManyToManyField(
                related_name="excluded_bank",
                verbose_name="Bancos exclu\xeddos",
                to="rh.Banco",
            ),
        ),
        migrations.AlterField(
            model_name="bankingconvenant",
            name="type_convenant",
            field=models.PositiveSmallIntegerField(
                default=2,
                verbose_name="Tipo Con\xeanio",
                choices=[
                    (1, "Exclusivo para clientes do banco"),
                    (2, "Servidores de outros bancos via TED/DOC"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="classification",
            field=models.PositiveIntegerField(
                default=1,
                verbose_name="Classifica\xe7\xe3o",
                choices=[
                    (1, "EFETIVO"),
                    (2, "MEMBRO"),
                    (3, "COMISSIONADO"),
                    (4, "A DISPOSI\xc7\xc3O"),
                    (5, "ESTAGI\xc1RIO"),
                    (6, "PENSIONISTA"),
                    (7, "PARTILHA"),
                    (8, "SEM V\xcdNCULO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="employee_pays_pension",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Pens\xe3o",
                choices=[
                    (0, "N\xc3O PAGA"),
                    (1, "PENS\xc3O ALIMENT\xcdCIA"),
                    (2, "PENS\xc3O POR MORTE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="employee_source",
            field=models.PositiveIntegerField(
                default=1,
                verbose_name="Tipo de servidor",
                choices=[
                    (1, "SERVIDOR DA CASA"),
                    (2, "SERVIDOR CEDIDO"),
                    (3, "SERVIDOR REQUISITADO"),
                    (4, "ESTAGI\xc1RIO"),
                    (5, "SEM V\xcdNCULO"),
                    (6, "PENSIONISTA - ALIMENT\xcdCIA"),
                    (7, "PARTILHA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="status",
            field=models.PositiveIntegerField(
                default=1,
                blank=True,
                verbose_name="Status",
                choices=[
                    (1, "PRODU\xc7\xc3O"),
                    (2, "ENVIADO"),
                    (3, "PAGAMENTO EFETUADO"),
                    (4, "PAGAMENTO RECUSADO"),
                    (5, "CANCELADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="estruturatabelasalarial",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, choices=[(1, "PADR\xc3O")]
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="base_de_calculo",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Base de c\xe1lculo",
                choices=[
                    (0, "SEM BASE"),
                    (1, "REMUNERA\xc7\xc3O BRUTA"),
                    (2, "PREVIDENCI\xc1RIA"),
                    (3, "REMUNERA\xc7\xc3O BASE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="carater",
            field=models.PositiveIntegerField(
                default=0,
                null=True,
                verbose_name="Car\xe1ter",
                choices=[
                    (0, "OUTROS"),
                    (1, "REMUNERAT\xd3RIO"),
                    (2, "INDENIZAT\xd3RIO"),
                    (3, "DE AUX\xcdLIO"),
                    (4, "IMPOSTO"),
                    (5, "PENS\xc3O"),
                    (6, "MENSALIDADE"),
                    (7, "CONSIGNA\xc7\xc3O"),
                    (8, "PREVIDENCI\xc1RIO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="nature_of_event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Natureza (eSocial)",
                blank=True,
                to="gfp.NatureEvent",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="tipo_calculo",
            field=models.PositiveIntegerField(
                verbose_name="Tipo C\xe1lculo",
                choices=[
                    (1, "PERCENTUAL"),
                    (2, "VALOR BASE"),
                    (3, "QUANTIDADE"),
                    (4, "LIVRE"),
                    (5, "QUANTIDADE/PERCENTUAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="extrapaymentperiod",
            name="type_value",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
            ),
        ),
        migrations.AlterField(
            model_name="folha",
            name="status",
            field=models.SmallIntegerField(
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
        migrations.AlterField(
            model_name="folhatipo",
            name="titulo",
            field=models.CharField(max_length=30, verbose_name="T\xedtulo"),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="character",
            field=models.PositiveIntegerField(
                default=0,
                null=True,
                verbose_name="Car\xe1ter",
                choices=[
                    (0, "OUTROS"),
                    (1, "REMUNERAT\xd3RIO"),
                    (2, "INDENIZAT\xd3RIO"),
                    (3, "DE AUX\xcdLIO"),
                    (4, "IMPOSTO"),
                    (5, "PENS\xc3O"),
                    (6, "MENSALIDADE"),
                    (7, "CONSIGNA\xc7\xc3O"),
                    (8, "PREVIDENCI\xc1RIO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
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
                    (37, "VERBAS INDENIZAT\xd3RIAS"),
                    (38, "OUTRAS REMUNERA\xc7\xd5ES RETROATIVAS/TEMPOR\xc1RIAS"),
                    (39, "VERBAS EXERCICIOS ANTERIORES"),
                    (40, "OUTRAS REMUNERA\xc7\xd5ES TEMPOR\xc1RIAS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Status",
                choices=[
                    (1, "Carregado com sucesso"),
                    (2, "N\xe3o carregado - matr\xedcula n\xe3o encontrada"),
                    (3, "N\xe3o carregado - servidor exonerado"),
                    (4, "N\xe3o carregado - servidor afastado"),
                    (5, "N\xe3o carregado - evento inexistente"),
                    (6, "Erro - lan\xe7amento inexistente no contracheque"),
                    (9, "N\xe3o carregado - erro desconhecido"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (1, "ABERTO"),
                    (2, "PAGANDO PARCELADO"),
                    (3, "PARCIALMENTE PAGO"),
                    (4, "PAGO SEM INFORMA\xc7\xc3O"),
                    (5, "PAGO"),
                    (6, "IGNORADO"),
                    (7, "AGUARDANDO DECIS\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifferenceconfig",
            name="typeof",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Base",
                choices=[(1, "Valor Fixo"), (2, "Percentual"), (3, "Sal. m\xednimo")],
            ),
        ),
        migrations.AlterField(
            model_name="periodo",
            name="mes",
            field=models.PositiveIntegerField(
                verbose_name="M\xeas",
                choices=[
                    (1, "JANEIRO"),
                    (2, "FEVEREIRO"),
                    (3, "MAR\xc7O"),
                    (4, "ABRIL"),
                    (5, "MAIO"),
                    (6, "JUNHO"),
                    (7, "JULHO"),
                    (8, "AGOSTO"),
                    (9, "SETEMBRO"),
                    (10, "OUTUBRO"),
                    (11, "NOVEMBRO"),
                    (12, "DEZEMBRO"),
                    (13, "13\xba SAL\xc1RIO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador", choices=[(1, "1")]
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="regime_previdenciario",
            field=models.PositiveSmallIntegerField(
                default=2,
                verbose_name="Regime previdenci\xc3\xa1rio",
                choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Gratif. Servidor",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao_membro",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Gratif. Membro",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Valor Servidor",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor_membro",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Valor Membro",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
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
                    (38, "OUTRAS REMUNERACOES/TEMPORARIAS"),
                    (101, "VERBAS REMUNERAT\xd3RIAS"),
                    (102, "VERBAS INDENIZAT\xd3RIAS"),
                    (119, "TOTAL GERAL"),
                ],
            ),
        ),
    ]
