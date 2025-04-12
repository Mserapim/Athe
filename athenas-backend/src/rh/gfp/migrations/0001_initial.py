# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Enquadramento",
            fields=[
                (
                    "matricula",
                    models.IntegerField(
                        default=0,
                        serialize=False,
                        verbose_name="Matricula",
                        primary_key=True,
                        blank=True,
                    ),
                ),
                (
                    "cargo",
                    models.CharField(
                        max_length=400, null=True, verbose_name="Cargo", blank=True
                    ),
                ),
                (
                    "classe_padrao_atual",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="classe_padrao",
                        blank=True,
                    ),
                ),
                (
                    "classe_padrao_prox",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="classe_padrao",
                        blank=True,
                    ),
                ),
                ("data_exercicio", models.DateField(null=True)),
                ("prox_progressao", models.DateField(null=True)),
                ("data_referencia", models.DateField(null=True)),
                (
                    "dias_sem_contar",
                    models.IntegerField(default=0, verbose_name="dias_neg", blank=True),
                ),
                (
                    "status",
                    models.CharField(
                        max_length=1, null=True, verbose_name="status", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "enquadramento",
                "managed": False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Calculo",
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
                ("slug", models.CharField(max_length=128, unique=True, null=True)),
                ("path", models.CharField(max_length=128, unique=True, null=True)),
                ("titulo", models.CharField(max_length=128, blank=True)),
                ("descricao", models.CharField(max_length=128, null=True)),
                ("objeto", models.CharField(max_length=128)),
                (
                    "typeof",
                    models.CharField(
                        default="CALCULO",
                        max_length=20,
                        db_index=True,
                        choices=[
                            ("CALCULO", "C\xc3\xa1lculos para FOPAG"),
                            ("LOADER", "Carregadores de arquivos"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": ("path",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CargosEstrutura",
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
                    "data_vigencia_inicio",
                    models.DateField(verbose_name="In\xedcio vig\xeancia", blank=True),
                ),
                (
                    "data_vigencia_fim",
                    models.DateField(
                        null=True, verbose_name="Fim vig\xeancia", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "gfp_cargosestrutura",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CategoriaSalarial",
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
                ("titulo", models.CharField(max_length=50, verbose_name="Nome")),
                (
                    "tipo",
                    models.CharField(
                        max_length=1,
                        verbose_name="N\xedvel Salarial",
                        choices=[("H", "HORIZONTAL"), ("V", "VERTICAL")],
                    ),
                ),
            ],
            options={
                "ordering": ["tipo", "titulo"],
                "db_table": "gfp_categoriasalarial",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CNAE",
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
                ("chave", models.CharField(unique=True, max_length=8)),
                ("descricao", models.CharField(max_length=60)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CNJRais",
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
                ("chave", models.CharField(unique=True, max_length=8)),
                (
                    "descricao",
                    models.CharField(max_length=60, verbose_name="Descri\xe7\xe3o"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ContraCheque",
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
                    "situacao_funcional",
                    models.CharField(max_length=250, null=True, blank=True),
                ),
                (
                    "situacao_previdenciaria",
                    models.CharField(max_length=250, null=True, blank=True),
                ),
                (
                    "referencia_efetivo_cache",
                    models.CharField(default="", max_length=100),
                ),
                (
                    "referencia_comissao_cache",
                    models.CharField(default="", max_length=100),
                ),
                (
                    "referencia_eletivo_cache",
                    models.CharField(default="", max_length=100),
                ),
                (
                    "data_admissao",
                    models.DateField(
                        null=True, verbose_name="Data Admiss\xe3o", blank=True
                    ),
                ),
                (
                    "dependentes_ir",
                    models.SmallIntegerField(
                        default=0, verbose_name="Dep. IR", blank=True
                    ),
                ),
                (
                    "dependentes_sf",
                    models.SmallIntegerField(
                        default=0, verbose_name="Dep. SF", blank=True
                    ),
                ),
                (
                    "margem_consignada_total",
                    models.DecimalField(
                        default=0,
                        verbose_name="Margem Total",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "margem_consignada_livre",
                    models.DecimalField(
                        default=0,
                        verbose_name="Margem Livre",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "base_previdenciaria",
                    models.DecimalField(
                        default=0,
                        verbose_name="Base Previd\xeancia",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "base_ir",
                    models.DecimalField(
                        default=0,
                        verbose_name="Base IR",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_bruto",
                    models.DecimalField(
                        default=0,
                        verbose_name="Total bruto",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "total_liquido",
                    models.DecimalField(
                        default=0,
                        verbose_name="Total l\xedquido",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "alterado",
                    models.BooleanField(default=False, verbose_name="Alterado"),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        default=1,
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
            ],
            options={
                "db_table": "gfp_contracheque",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ContraChequeAuditoria",
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
                    "contracheque_info",
                    models.CharField(
                        default="", max_length=250, verbose_name="Contracheque"
                    ),
                ),
                ("resumo", models.CharField(max_length=250, verbose_name="T\xedtulo")),
                ("texto", models.TextField()),
                (
                    "conferido",
                    models.BooleanField(default=False, verbose_name="Conferido"),
                ),
            ],
            options={
                "ordering": ("-contracheque__folha", "-created_at"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ContraChequePensionista",
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
            ],
            options={
                "db_table": "gfp_contrachequepensionista",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DadoBancarioServidorFolha",
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
                    "data_vigencia",
                    models.DateTimeField(
                        null=True, verbose_name="In\xedcio Vig\xeancia", blank=True
                    ),
                ),
                (
                    "data_inicio_vigencia",
                    models.DateField(null=True, verbose_name="In\xedcio Vig\xeancia"),
                ),
                (
                    "data_fim_vigencia",
                    models.DateField(
                        null=True, verbose_name="Fim Vig\xeancia", blank=True
                    ),
                ),
            ],
            options={
                "ordering": [
                    "dado_bancario_pessoa__pessoa",
                    "tipo_folha",
                    "-data_inicio_vigencia",
                ],
                "db_table": "gfp_dadobancariopessoafolha",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="EstruturaTabelaSalarial",
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
                    "titulo",
                    models.CharField(
                        max_length=100, verbose_name="T\xedtulo", blank=True
                    ),
                ),
                (
                    "codigo",
                    models.CharField(
                        max_length=10, null=True, verbose_name="C\xf3digo", blank=True
                    ),
                ),
                (
                    "formatacao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Formata\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "descricao",
                    models.CharField(
                        max_length=400,
                        null=True,
                        verbose_name="Descri\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "meses_progressao_inicial",
                    models.SmallIntegerField(
                        default=0, verbose_name="Progress\xf5es inicial", blank=True
                    ),
                ),
                (
                    "meses_progressao",
                    models.SmallIntegerField(
                        default=0, verbose_name="Progress\xf5es", blank=True
                    ),
                ),
                (
                    "data_vigencia_inicio",
                    models.DateField(
                        null=True, verbose_name="In\xedcio vig\xeancia", blank=True
                    ),
                ),
                (
                    "data_vigencia_fim",
                    models.DateField(
                        null=True, verbose_name="Fim vig\xeancia", blank=True
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["-ativo", "-data_vigencia_inicio", "codigo"],
                "db_table": "gfp_estruturasalarial",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Evento",
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
                    "numero",
                    models.CharField(
                        unique=True, max_length=5, verbose_name="N\xfamero"
                    ),
                ),
                (
                    "lancamento",
                    models.CharField(
                        max_length=1,
                        verbose_name="Lan\xe7amento",
                        choices=[("T", "TEMPOR\xc1RIO"), ("F", "FIXO")],
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        max_length=1, choices=[("P", "PROVENTO"), ("D", "DESCONTO")]
                    ),
                ),
                (
                    "tipo_calculo",
                    models.PositiveIntegerField(
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
                (
                    "carater",
                    models.PositiveIntegerField(
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
                        ],
                    ),
                ),
                ("titulo", models.CharField(max_length=50, verbose_name="T\xedtulo")),
                (
                    "automatico",
                    models.BooleanField(default=False, verbose_name="Autom\xe1tico"),
                ),
                (
                    "calculo_invertido",
                    models.BooleanField(
                        default=False, verbose_name="C\xe1lculo invertido"
                    ),
                ),
                (
                    "quantidade_max",
                    models.DecimalField(
                        null=True,
                        verbose_name="Quantidade m\xe1xima",
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                (
                    "quantidade",
                    models.DecimalField(
                        null=True,
                        verbose_name="Quantidade",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "porcentagem",
                    models.DecimalField(
                        null=True,
                        verbose_name="Porcentagem",
                        max_digits=10,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "valor_base",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor base",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "teto",
                    models.DecimalField(
                        null=True,
                        verbose_name="Teto",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "piso",
                    models.DecimalField(
                        null=True,
                        verbose_name="Piso",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "aplica_consignado",
                    models.BooleanField(default=False, verbose_name="Consignado"),
                ),
                (
                    "aplica_consignavel",
                    models.BooleanField(default=False, verbose_name="Consignavel"),
                ),
                (
                    "config_transparencia",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Portal Transpar\xeancia",
                        choices=[
                            (3101, "DEDU\xc7\xd4ES: IRRF"),
                            (3102, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                            (3103, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                            (
                                3104,
                                "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio",
                            ),
                            (4001, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                            (4002, "INDENIZAT\xd3RIAS: Aux. Creche"),
                            (4003, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                            (4004, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                            (4005, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                            (4006, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                            (4007, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                            (4008, "INDENIZAT\xd3RIAS: IRRF"),
                            (3001, "EFEITOS NEGATIVOS: Redutor de Teto"),
                            (2001, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                            (2002, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                            (2003, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                            (1001, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                            (1002, "REMUNERA\xc7\xc3O: Vencimento"),
                            (
                                1003,
                                "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o",
                            ),
                            (1004, "REMUNERA\xc7\xc3O: VPI"),
                            (1005, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                            (1006, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                            (1007, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                        ],
                    ),
                ),
                (
                    "base_de_calculo",
                    models.PositiveIntegerField(
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
                (
                    "evaluate_difference",
                    models.BooleanField(
                        default=False, verbose_name="Avaliar diferen\xe7a?"
                    ),
                ),
                (
                    "config_difference_value",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Diferen\xc3\xa7a de valor",
                    ),
                ),
                (
                    "config_return_value",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Devolu\xc3\xa7\xc3\xa3o de valor",
                    ),
                ),
                (
                    "config_difference_contrib",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Diferen\xc3\xa7a de patronal",
                    ),
                ),
                (
                    "config_return_contrib",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Devolu\xc3\xa7\xc3\xa3o de patronal",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Decri\xc3\xa7\xc3\xa3o",
                    ),
                ),
            ],
            options={
                "ordering": ("numero", "titulo"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ExtensionSalaryProgression",
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
                ("days", models.PositiveIntegerField(default=0, verbose_name="Dias")),
                (
                    "start_date_extension",
                    models.DateField(
                        verbose_name="Data in\xedcio prorroga\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "purpose",
                    models.CharField(default="", max_length=400, verbose_name="Motivo"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ExtraPayment",
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
                ("slug", models.SlugField(verbose_name="slug")),
                ("name", models.CharField(max_length=64, verbose_name="Nome")),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ExtraPaymentPeriod",
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
                    "value",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
                ),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(null=True, verbose_name="Fim vig\xeancia"),
                ),
            ],
            options={
                "ordering": ("extra_payment", "-start_validity", "employee"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="FatorFap",
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
                    "valor",
                    models.DecimalField(
                        verbose_name="Fator", max_digits=8, decimal_places=4
                    ),
                ),
                ("dt_inicio", models.DateField(verbose_name="In\xedcio Vig\xeancia")),
                (
                    "dt_fim",
                    models.DateField(
                        null=True, verbose_name="Fim Vig\xeancia", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["dt_inicio"],
                "db_table": "gfp_fatorfat",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FatorRat",
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
                    "valor",
                    models.DecimalField(
                        verbose_name="Fator", max_digits=5, decimal_places=2
                    ),
                ),
                ("dt_inicio", models.DateField(verbose_name="In\xedcio Vig\xeancia")),
                (
                    "dt_fim",
                    models.DateField(
                        null=True, verbose_name="Fim Vig\xeancia", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["dt_inicio"],
                "db_table": "gfp_fatorrat",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Folha",
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
                ("fechado", models.BooleanField(default=False, verbose_name="Fechado")),
                (
                    "processado",
                    models.BooleanField(default=False, verbose_name="processado"),
                ),
                ("ci", models.BooleanField(default=False, verbose_name="Conferido")),
                (
                    "dt_fechamento",
                    models.DateTimeField(
                        null=True, verbose_name="Data do Fechamento", blank=True
                    ),
                ),
                (
                    "dt_processado",
                    models.DateTimeField(
                        null=True, verbose_name="Data da Execu\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "dt_ci",
                    models.DateTimeField(
                        null=True, verbose_name="Data da Confer\xeancia", blank=True
                    ),
                ),
                (
                    "dt_pagamento",
                    models.DateField(
                        null=True, verbose_name="Data de Pagamento", blank=True
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
                ("dt_criacao", models.DateTimeField(auto_now_add=True)),
                ("unicode_cache", models.CharField(max_length=200, db_index=True)),
            ],
            options={
                "ordering": ("-periodo__ano", "-periodo__mes", "tipo_folha__titulo"),
                "permissions": (
                    ("can_process_payroll", 'Mudar estado da folha para "processada"'),
                    ("can_close_payroll", 'Mudar estado da folha para "fechada"'),
                    (
                        "can_change_status_payroll",
                        "Mudar estado da folha entre produ\xe7\xe3o/an\xe1lise",
                    ),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="FolhaAuditoria",
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
                ("resumo", models.CharField(max_length=250, verbose_name="T\xedtulo")),
                ("texto", models.TextField()),
                (
                    "conferido",
                    models.BooleanField(default=False, verbose_name="Conferido"),
                ),
            ],
            options={
                "ordering": ("-folha", "-created_at"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="FolhaEvento",
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
                    "lancamento",
                    models.CharField(
                        max_length=1, choices=[("T", "TEMPOR\xc1RIO"), ("F", "FIXO")]
                    ),
                ),
                (
                    "qnt",
                    models.DecimalField(
                        default=0, max_digits=10, decimal_places=6, blank=True
                    ),
                ),
                (
                    "qnt_max",
                    models.DecimalField(default=0, max_digits=10, decimal_places=6),
                ),
                ("parcela", models.PositiveIntegerField(default=0, blank=True)),
                ("prazo", models.PositiveIntegerField(default=0, blank=True)),
                (
                    "pct",
                    models.DecimalField(
                        null=True, max_digits=10, decimal_places=6, blank=True
                    ),
                ),
                (
                    "valor",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "valor_base",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "patronal",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info",
                    models.CharField(default="", max_length=150, null=True, blank=True),
                ),
                (
                    "base_previdencia",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                ("dt_criado", models.DateTimeField(auto_now_add=True)),
                ("dt_confirma_folha", models.DateTimeField(null=True, blank=True)),
                ("dt_confirma_controle", models.DateTimeField(null=True, blank=True)),
                (
                    "value",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "employer_contribution",
                    models.DecimalField(
                        default=0, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "correct_value",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "diff_value_provisioned",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "correct_employer_contribution",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "diff_employer_contribution_provisioned",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "correct_contribution_base",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "reference_year",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Ano Refer\xeancia", blank=True
                    ),
                ),
                (
                    "reference_month",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="M\xeas Refer\xeancia", blank=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default="CT",
                        max_length=2,
                        db_index=True,
                        blank=True,
                        choices=[
                            ("NC", "N\xc3O CONTABILIZADO"),
                            ("RB", "RECUSADO PELO BANCO"),
                            ("CT", "CONTABILIZADO"),
                        ],
                    ),
                ),
                ("json_calc_vars", models.CharField(default="{}", max_length=256)),
            ],
            options={
                "ordering": [
                    "contracheque__folha",
                    "contracheque__servidor",
                    "evento__numero",
                ],
                "permissions": (
                    (
                        "can_validate_event_payroll",
                        "Validar eventos pendentes na folha de pagamento",
                    ),
                    (
                        "can_validate_event_internal_control",
                        "Validar eventos pendentes no controle interno",
                    ),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="FolhaMensagem",
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
                ("texto", models.CharField(max_length=400, verbose_name="Texto")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FolhaModelo",
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
                ("titulo", models.CharField(max_length=120, verbose_name="T\xedtulo")),
                (
                    "slug",
                    models.SlugField(
                        unique=True,
                        max_length=120,
                        verbose_name="Identificador",
                        blank=True,
                    ),
                ),
                (
                    "para_indicativo",
                    models.CharField(
                        default=None,
                        max_length=1,
                        null=True,
                        verbose_name="Para os",
                        choices=[
                            ("I", "INDEFINIDO"),
                            ("E", "ESTAGI\xc1RIO"),
                            ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                            ("P", "MILITAR"),
                            ("S", "SERVIDOR"),
                        ],
                    ),
                ),
                (
                    "previdencia",
                    models.BooleanField(default=False, verbose_name="Previd\xeancia"),
                ),
                (
                    "somente_ativo",
                    models.BooleanField(
                        default=False, verbose_name="Somente para ativos"
                    ),
                ),
                (
                    "somente_folha",
                    models.BooleanField(
                        default=False, verbose_name="Somente servidores da folha"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FolhaTipo",
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
                ("titulo", models.CharField(max_length=30, verbose_name="T\xedtulo")),
                ("ativo", models.BooleanField(default=True)),
                (
                    "carater",
                    models.SmallIntegerField(
                        default=1,
                        choices=[
                            (1, "REMUNERAT\xd3RIO"),
                            (2, "INDENIZAT\xd3RIO"),
                            (3, "DE AUX\xcdLIO"),
                        ],
                    ),
                ),
                ("principal", models.BooleanField(default=False)),
                (
                    "processo",
                    models.CharField(
                        max_length=50, null=True, verbose_name="Processo", blank=True
                    ),
                ),
                (
                    "margem",
                    models.DecimalField(
                        default=0,
                        verbose_name="Margem Consign\xe1vel",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "abreviatura",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Abreviatura", blank=True
                    ),
                ),
                (
                    "numero",
                    models.CharField(
                        max_length=4, unique=True, null=True, verbose_name="N\xfamero"
                    ),
                ),
            ],
            options={
                "ordering": ("titulo",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GenreEvent",
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
                    "genre_number",
                    models.CharField(
                        unique=True, max_length=3, verbose_name="N\xfamero"
                    ),
                ),
                (
                    "type_event",
                    models.CharField(
                        max_length=1, choices=[("P", "PROVENTO"), ("D", "DESCONTO")]
                    ),
                ),
                (
                    "character",
                    models.PositiveIntegerField(
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
                        ],
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        unique=True, max_length=50, verbose_name="T\xedtulo"
                    ),
                ),
                (
                    "config_transparency",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Portal Transpar\xeancia",
                        choices=[
                            (3101, "DEDU\xc7\xd4ES: IRRF"),
                            (3102, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                            (3103, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                            (
                                3104,
                                "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio",
                            ),
                            (4001, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                            (4002, "INDENIZAT\xd3RIAS: Aux. Creche"),
                            (4003, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                            (4004, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                            (4005, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                            (4006, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                            (4007, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                            (4008, "INDENIZAT\xd3RIAS: IRRF"),
                            (3001, "EFEITOS NEGATIVOS: Redutor de Teto"),
                            (2001, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                            (2002, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                            (2003, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                            (1001, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                            (1002, "REMUNERA\xc7\xc3O: Vencimento"),
                            (
                                1003,
                                "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o",
                            ),
                            (1004, "REMUNERA\xc7\xc3O: VPI"),
                            (1005, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                            (1006, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                            (1007, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": ("genre_number",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Gerente",
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
                    "nivel",
                    models.PositiveIntegerField(
                        choices=[
                            (1, "Folha de Pagamento"),
                            (2, "Controle Iterno"),
                            (3, "Financeiro"),
                            (4, "Outros"),
                        ]
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GestorProgressoes",
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
                    "data_referencia",
                    models.DateField(null=True, verbose_name="Data Refer\xeancia"),
                ),
                (
                    "data_prox_progressao_prevista",
                    models.DateField(null=True, verbose_name="Data Prevista"),
                ),
                (
                    "data_prox_progressao",
                    models.DateField(
                        null=True, verbose_name="Pr\xf3xima Progress\xe3o"
                    ),
                ),
                (
                    "bloqueado",
                    models.BooleanField(default=False, verbose_name="Bloqueado"),
                ),
                (
                    "dias_bloqueio",
                    models.IntegerField(default=0, verbose_name="Dias bloqueio"),
                ),
                ("requisitos", models.BooleanField(default=False)),
            ],
            options={
                "ordering": [
                    "data_prox_progressao",
                    "posse_servidor__servidor__pessoa_fisica__nome",
                ],
                "db_table": "gfp_gestorprogressoes",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricoServidorVerbaAdicional",
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
                    "valor",
                    models.DecimalField(max_digits=10, decimal_places=2, blank=True),
                ),
                (
                    "dt_inicio",
                    models.DateField(verbose_name="Inicio da virg\xeancia", blank=True),
                ),
                (
                    "dt_fim",
                    models.DateField(
                        null=True, verbose_name="Fim da virg\xeancia", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["servidor", "evento"],
                "db_table": "gfp_servidoradicionaishistoric",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IRRF",
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
                    "valor_dependente",
                    models.DecimalField(max_digits=16, decimal_places=2),
                ),
                ("dt_lancamento", models.DateTimeField(auto_now_add=True)),
                (
                    "ano_calendario",
                    models.PositiveIntegerField(verbose_name="Ano Calend\xe1rio"),
                ),
                ("data_vigencia", models.DateField(null=True)),
            ],
            options={
                "ordering": ["-ano_calendario"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IRRFFaixa",
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
                    "limite_inferior",
                    models.DecimalField(
                        verbose_name="Limite Inferior", max_digits=16, decimal_places=2
                    ),
                ),
                (
                    "limite_superior",
                    models.DecimalField(
                        verbose_name="Limite Superior", max_digits=16, decimal_places=2
                    ),
                ),
                (
                    "percentual",
                    models.DecimalField(
                        verbose_name="Aliquota", max_digits=6, decimal_places=3
                    ),
                ),
                (
                    "desconto",
                    models.DecimalField(
                        verbose_name="Dedu\xe7\xe3o", max_digits=16, decimal_places=2
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ModeloTabelaSalarial",
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
                ("titulo", models.CharField(max_length=255)),
                (
                    "quantidade_horizontal",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="Quantidade n\xc3\xadveis horizontais",
                        blank=True,
                    ),
                ),
                (
                    "quantidade_vertical",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="Quantidade n\xc3\xadveis verticais",
                        blank=True,
                    ),
                ),
                (
                    "titulo_horizontal",
                    models.CharField(default="REFER\xcaNCIA", max_length=100),
                ),
                ("titulo_vertical", models.CharField(default="CLASSE", max_length=100)),
                ("labels_horizontal", models.CharField(default="", max_length=100)),
                ("labels_vertical", models.CharField(default="", max_length=100)),
                (
                    "formatacao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Formata\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "gfp_modelotabelasalarial",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
