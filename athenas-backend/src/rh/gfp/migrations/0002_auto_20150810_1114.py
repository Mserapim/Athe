# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0001_initial"),
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("standard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MovimentacaoProgressao",
            fields=[
                (
                    "movimentacaopessoal_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPessoal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("titulo", models.CharField(max_length=60, null=True, blank=True)),
                (
                    "data_referencia_inicial",
                    models.DateField(verbose_name="Data Refer\xeancia", blank=True),
                ),
                (
                    "data_referencia",
                    models.DateField(verbose_name="Data Refer\xeancia", blank=True),
                ),
                (
                    "data_inicio_vigencia",
                    models.DateField(verbose_name="In\xedcio Vig\xeancia"),
                ),
                (
                    "data_fim_vigencia",
                    models.DateField(
                        null=True, verbose_name="Fim Vig\xeancia", blank=True
                    ),
                ),
                (
                    "dias_suspenso",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Dias suspensos"
                    ),
                ),
                (
                    "dias_suspenso_afastamento",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Dias suspensos afastamento"
                    ),
                ),
                ("indireto", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "expected_date",
                    models.DateField(
                        null=True, verbose_name="Data Prevista", blank=True
                    ),
                ),
                (
                    "initial_expected_date",
                    models.DateField(verbose_name="Data Prevista", blank=True),
                ),
                (
                    "months_progression",
                    models.PositiveSmallIntegerField(
                        default=12, verbose_name="Meses progress\xe3o"
                    ),
                ),
                (
                    "period_absences",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Faltas no per\xedodo"
                    ),
                ),
                ("data_vigencia", models.DateField(verbose_name="Data Vig\xeancia")),
            ],
            options={
                "ordering": ["-data_inicio_vigencia"],
                "verbose_name": "Movimenta\xe7\xe3o Pessoal",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoEnquadramento",
            fields=[
                (
                    "movimentacaoprogressao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gfp.MovimentacaoProgressao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Movimenta\xe7\xe3o de Enquadramento",
            },
            bases=("gfp.movimentacaoprogressao",),
        ),
        migrations.CreateModel(
            name="NivelSalarial",
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
                    "ordem",
                    models.SmallIntegerField(
                        null=True, verbose_name="Ordem", blank=True
                    ),
                ),
                ("valor", models.CharField(max_length=3, verbose_name="Valor")),
                (
                    "categoria",
                    models.ForeignKey(
                        related_name="niveis_categoria",
                        verbose_name="N\xedvel Salarial",
                        to="gfp.CategoriaSalarial",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "estrutura_salarial",
                    models.ForeignKey(
                        related_name="niveis_estrutura",
                        verbose_name="N\xedvel Salarial",
                        blank=True,
                        to="gfp.EstruturaTabelaSalarial",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "gfp_nivelsalarial",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PaycheckDifference",
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
                ("title", models.CharField(max_length=256, verbose_name="T\xedtulo")),
                (
                    "identifier",
                    models.CharField(
                        max_length=32, verbose_name="Identificador", db_index=True
                    ),
                ),
                (
                    "installments",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Parcelas"
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="Situa\xe7\xe3o",
                        choices=[
                            (1, "ABERTO"),
                            (2, "PAGANDO"),
                            (3, "PARCIALMENTE PAGO"),
                            (4, "PAGO SEM INFORMA\xc7\xc3O"),
                            (5, "PAGO"),
                            (6, "IGNORADO"),
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
                    "employee",
                    models.ForeignKey(
                        related_name="paycheck_differences",
                        verbose_name="Servidor",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "event",
                    models.ForeignKey(
                        related_name="paycheck_differences",
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
            options={},
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PaycheckDifferenceItem",
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
                    "employer_contribution",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
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
                    "difference",
                    models.ForeignKey(
                        related_name="difference_items",
                        to="gfp.PaycheckDifference",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "entry_difference",
                    models.ForeignKey(
                        related_name="difference_items",
                        to="gfp.FolhaEvento",
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
            options={},
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PerfilPrevidencia",
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
                    "lei_cargo",
                    models.CharField(
                        max_length=10,
                        verbose_name="Tipo de Lei",
                        choices=[
                            ("EF", "EFETIVO"),
                            ("CM", "COMISS\xc3O"),
                            ("FC", "FUN\xc7\xc3O DE CONFIAN\xc7A"),
                            ("AC", "ACORDO DE COOPERA\xc7\xc3O T\xc9CNICA"),
                            ("ES", "ESTAGI\xc1RIO"),
                            ("EL", "ELETIVO"),
                        ],
                    ),
                ),
                (
                    "prioridade",
                    models.SmallIntegerField(
                        verbose_name="Prioridade",
                        choices=[
                            (1, "MUITO ALTA"),
                            (2, "ALTA"),
                            (3, "MODERADA"),
                            (4, "BAIXA"),
                            (5, "MUITO BAIXA"),
                        ],
                    ),
                ),
                (
                    "evento",
                    models.OneToOneField(
                        verbose_name="Evento Principal",
                        to="gfp.Evento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pessoa_juridica",
                    models.OneToOneField(
                        verbose_name="Pessoa Jur\xeddica",
                        to="rh.PessoaJuridica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Periodo",
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
                    "mes",
                    models.PositiveIntegerField(
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
                ("ano", models.PositiveIntegerField()),
                (
                    "auxilio_alimentacao",
                    models.DecimalField(
                        null=True,
                        verbose_name="Aux. Alimenta\xe7\xe3o",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "auxilio_creche",
                    models.DecimalField(
                        null=True,
                        verbose_name="Aux. Creche",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "salario_minimo",
                    models.DecimalField(
                        null=True,
                        verbose_name="Sal\xe1rio M\xednimo",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "salario_familia",
                    models.DecimalField(
                        null=True,
                        verbose_name="Sal\xe1rio Fam\xedlia",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "salario_teto_adm",
                    models.DecimalField(
                        null=True,
                        verbose_name="Sal\xe1rio Teto Adm",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "salario_teto_membros",
                    models.DecimalField(
                        null=True,
                        verbose_name="Sal\xe1rio Teto Membros",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
            ],
            options={
                "ordering": ("-ano", "-mes"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PeriodoPrevidencia",
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
                    "periodo",
                    models.ForeignKey(to="gfp.Periodo", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Previdencia",
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
                ("dt_lancamento", models.DateTimeField(auto_now_add=True)),
                (
                    "ano_calendario",
                    models.PositiveIntegerField(verbose_name="Ano Calend\xe1rio"),
                ),
                ("data_vigencia", models.DateField(verbose_name="Vig\xeancia")),
                (
                    "regime_previdenciario",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Regime previdenci\xc3\xa1rio",
                        choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
                    ),
                ),
                (
                    "pessoa_juridica",
                    models.ForeignKey(
                        related_name="como_previdencia",
                        verbose_name="Previd\xc3\xaancia",
                        to="rh.PessoaJuridica",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "publicacao",
                    models.ForeignKey(to="rh.Publicacao", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["-ano_calendario", "-data_vigencia"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PrevidenciaFaixa",
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
                    "pct",
                    models.DecimalField(
                        verbose_name="Porcentagem do Empregado",
                        max_digits=5,
                        decimal_places=2,
                    ),
                ),
                (
                    "pct_patronal",
                    models.DecimalField(
                        verbose_name="Porcentagem do Patr\xe3o",
                        max_digits=5,
                        decimal_places=2,
                    ),
                ),
                (
                    "previdencia",
                    models.ForeignKey(
                        related_name="faixas",
                        verbose_name="Previd\xeancia",
                        to="gfp.Previdencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["previdencia", "limite_inferior"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenciaNiveis2D",
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
                    "horizontal",
                    models.CharField(
                        max_length=6, null=True, verbose_name="Valor", blank=True
                    ),
                ),
                (
                    "vertical",
                    models.CharField(
                        max_length=6, null=True, verbose_name="Valor", blank=True
                    ),
                ),
                ("sigla_cache", models.CharField(max_length=30, null=True, blank=True)),
                ("ordem", models.SmallIntegerField(default=0, verbose_name="Ordem")),
                (
                    "tipo_valor",
                    models.SmallIntegerField(
                        default=1,
                        verbose_name="Valor Servidor",
                        choices=[(1, "VALOR"), (2, "PERCENTUAL")],
                    ),
                ),
                (
                    "tipo_gratificacao",
                    models.SmallIntegerField(
                        default=1,
                        verbose_name="Gratif. Servidor",
                        choices=[(1, "VALOR"), (2, "PERCENTUAL")],
                    ),
                ),
                (
                    "tipo_valor_membro",
                    models.SmallIntegerField(
                        default=1,
                        verbose_name="Valor Membro",
                        choices=[(1, "VALOR"), (2, "PERCENTUAL")],
                    ),
                ),
                (
                    "tipo_gratificacao_membro",
                    models.SmallIntegerField(
                        default=1,
                        verbose_name="Gratif. Membro",
                        choices=[(1, "VALOR"), (2, "PERCENTUAL")],
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
                (
                    "fator_atualizacao",
                    models.DecimalField(
                        null=True,
                        verbose_name="Fator de atualiza\xe7\xe3o",
                        max_digits=16,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "cargos",
                    models.ManyToManyField(
                        related_name="referencias_salariais",
                        null=True,
                        to="rh.Cargo",
                        blank=True,
                    ),
                ),
                (
                    "estrutura_salarial",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="N\xedvel Salarial",
                        to="gfp.EstruturaTabelaSalarial",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modelo_tabela",
                    models.ForeignKey(
                        related_name="referencias",
                        verbose_name="Modelo",
                        to="gfp.ModeloTabelaSalarial",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "nivel_horizontal",
                    models.ForeignKey(
                        related_name="estrutura_niveis_horizontais",
                        verbose_name="N\xedvel Horizontal",
                        blank=True,
                        to="gfp.NivelSalarial",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "nivel_vertical",
                    models.ForeignKey(
                        related_name="estrutura_niveis_verticais",
                        verbose_name="N\xedvel Vertical",
                        blank=True,
                        to="gfp.NivelSalarial",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "referencia_anterior",
                    models.ForeignKey(
                        verbose_name="Refer\xc3\xaancia anterior",
                        blank=True,
                        to="gfp.ReferenciaNiveis2D",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("modelo_tabela", "ordem"),
                "db_table": "gfp_referencianiveis2d",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenciaSalario",
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
                    "valor",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor Servidor",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "gratificacao",
                    models.DecimalField(
                        default=0,
                        verbose_name="Gratif. Servidor",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "valor_membro",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor Membro",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                (
                    "gratificacao_membro",
                    models.DecimalField(
                        default=0,
                        verbose_name="Gratif. Membro",
                        max_digits=16,
                        decimal_places=2,
                    ),
                ),
                ("sigla_cache", models.CharField(max_length=30, null=True, blank=True)),
                (
                    "dt_criacao",
                    models.DateField(
                        auto_now_add=True, verbose_name="Data Cria\xe7\xe3o"
                    ),
                ),
                (
                    "dt_alteracao",
                    models.DateField(
                        auto_now=True, verbose_name="Data Altera\xe7\xe3o"
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
                (
                    "referencia_nivel2d",
                    models.ForeignKey(
                        related_name="referencias_salarios",
                        verbose_name="Refer\xeancia N\xedveis",
                        to="gfp.ReferenciaNiveis2D",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("tabela_salarial", "referencia_nivel2d__ordem"),
                "db_table": "gfp_referenciasalarial",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RRA",
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
                    "title",
                    models.CharField(
                        unique=True, max_length=50, verbose_name="T\xedtulo"
                    ),
                ),
                ("slug", models.SlugField(verbose_name="Identifica\xe7\xe3o")),
                (
                    "process",
                    models.CharField(
                        max_length=50, null=True, verbose_name="Processo", blank=True
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
                    "events",
                    models.ManyToManyField(
                        related_name="rra_event",
                        verbose_name="Eventos",
                        to="gfp.Evento",
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
                "ordering": ["title"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RRAEmployee",
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
                    "months",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Quantidade de meses"
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
                    "employee",
                    models.ForeignKey(
                        related_name="rra_reference",
                        verbose_name="Servidor",
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
                (
                    "rra",
                    models.ForeignKey(
                        related_name="employeers",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="RRA",
                        to="gfp.RRA",
                    ),
                ),
            ],
            options={
                "ordering": ["employee", "rra__title", "months"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RRAServidorFolhaTipo",
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
                ("quantidade", models.DecimalField(max_digits=7, decimal_places=2)),
                (
                    "folha_tipo",
                    models.ForeignKey(
                        related_name="rra_servidores",
                        to="gfp.FolhaTipo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "servidor",
                    models.ForeignKey(
                        related_name="com_rra_folhatipo",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["-folha_tipo", "servidor__pessoa_fisica__nome"],
                "db_table": "gfp_rraservidorfolhatipo",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ServidorVerbaAdicional",
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
                (
                    "evento",
                    models.ForeignKey(
                        related_name="adicionais_dos_servidores",
                        to="gfp.Evento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "publicacao",
                    models.ForeignKey(
                        related_name="adicionais_servidores",
                        verbose_name="Publica\xe7\xe3o",
                        blank=True,
                        to="rh.Publicacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "servidor",
                    models.ForeignKey(
                        related_name="adicionais",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["servidor", "evento"],
                "db_table": "gfp_servidoradicionais",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SpecieEvent",
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
                    "specie_number",
                    models.CharField(
                        unique=True, max_length=2, verbose_name="N\xfamero"
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        unique=True, max_length=50, verbose_name="T\xedtulo"
                    ),
                ),
                (
                    "invert_type",
                    models.BooleanField(default=False, verbose_name="Inverter Tipo"),
                ),
                (
                    "concatenate_name",
                    models.BooleanField(default=True, verbose_name="Concatenar Nome?"),
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
                "ordering": ("specie_number",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TabelaSalarial",
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
                    "info_adicional",
                    models.CharField(default="", max_length=30, blank=True),
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
                    "estrutura_salarial",
                    models.ForeignKey(
                        related_name="tabelas_vigentes",
                        verbose_name="Estrutura Salarial",
                        to="gfp.EstruturaTabelaSalarial",
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
                (
                    "publicacao",
                    models.ForeignKey(
                        related_name="tabelas_salariais",
                        verbose_name="Publica\xe7\xe3o",
                        to="rh.Publicacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tabela_anterior",
                    models.ForeignKey(
                        related_name="tabela_atualizada",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="Tabela Salarial",
                        blank=True,
                        to="gfp.TabelaSalarial",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("estrutura_salarial", "-data_vigencia_inicio"),
                "db_table": "gfp_tabelasalarialsalario",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name="tabelasalarial",
            unique_together=set(
                [("estrutura_salarial", "info_adicional", "publicacao")]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="rraservidorfolhatipo",
            unique_together=set([("servidor", "folha_tipo", "quantidade")]),
        ),
        migrations.AlterUniqueTogether(
            name="rraemployee",
            unique_together=set([("employee", "rra")]),
        ),
        migrations.AddField(
            model_name="referenciasalario",
            name="tabela_salarial",
            field=models.ForeignKey(
                related_name="salarios",
                verbose_name="Tabela Salarial",
                to="gfp.TabelaSalarial",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="referenciasalario",
            unique_together=set([("tabela_salarial", "referencia_nivel2d")]),
        ),
        migrations.AlterUniqueTogether(
            name="referencianiveis2d",
            unique_together=set([("modelo_tabela", "horizontal", "vertical")]),
        ),
        migrations.AddField(
            model_name="periodoprevidencia",
            name="previdencia",
            field=models.ForeignKey(
                to="gfp.Previdencia", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="periodo",
            unique_together=set([("mes", "ano")]),
        ),
        migrations.AlterUniqueTogether(
            name="paycheckdifferenceitem",
            unique_together=set([("difference", "entry_difference")]),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="rra_employee",
            field=models.ForeignKey(
                related_name="differences",
                verbose_name="RRA Servidor",
                blank=True,
                to="gfp.RRAEmployee",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="paycheckdifference",
            unique_together=set([("identifier", "employee", "event")]),
        ),
        migrations.AddField(
            model_name="movimentacaoprogressao",
            name="movimentacao_posse",
            field=models.ForeignKey(
                related_name="progressoes",
                blank=True,
                to="rh.MovimentacaoPosse",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="movimentacaoprogressao",
            name="progressao_anterior",
            field=models.ForeignKey(
                related_name="progressoes",
                blank=True,
                to="gfp.MovimentacaoProgressao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="movimentacaoprogressao",
            name="referencia_nivel2d",
            field=models.ForeignKey(
                related_name="referencia_progressoes",
                verbose_name="Refer\xeancia N\xedveis",
                blank=True,
                to="gfp.ReferenciaNiveis2D",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="movimentacaoprogressao",
            unique_together=set([("movimentacao_posse", "referencia_nivel2d")]),
        ),
        migrations.AddField(
            model_name="modelotabelasalarial",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="modelotabelasalarial",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="irrffaixa",
            name="irrf",
            field=models.ForeignKey(
                related_name="faixas",
                verbose_name="IRRF",
                to="gfp.IRRF",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="irrf",
            name="publicacao",
            field=models.ForeignKey(
                verbose_name="Publica\xe7\xe3o",
                to="rh.Publicacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="historicoservidorverbaadicional",
            name="evento",
            field=models.ForeignKey(
                related_name="adicionais_dos_servidores_historico",
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="historicoservidorverbaadicional",
            name="publicacao",
            field=models.ForeignKey(
                related_name="adicionais_servidores_historico",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="historicoservidorverbaadicional",
            name="servidor",
            field=models.ForeignKey(
                related_name="adicionais_historico",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gestorprogressoes",
            name="posse_servidor",
            field=models.ForeignKey(
                related_name="+",
                to="rh.MovimentacaoPosse",
                unique=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gestorprogressoes",
            name="progressao_atual",
            field=models.ForeignKey(
                related_name="managers",
                to="gfp.MovimentacaoProgressao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gestorprogressoes",
            name="ref_atual",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Atual",
                to="gfp.ReferenciaNiveis2D",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gestorprogressoes",
            name="ref_progressao",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Pr\xf3xima",
                to="gfp.ReferenciaNiveis2D",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gerente",
            name="servidor",
            field=models.ForeignKey(
                to="rh.Servidor", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="genreevent",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="genreevent",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhatipo",
            name="modelo",
            field=models.ForeignKey(
                related_name="folhas",
                verbose_name="Modelo",
                blank=True,
                to="gfp.FolhaModelo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhatipo",
            name="publicacao_processo",
            field=models.ForeignKey(
                verbose_name="Publica\xe7\xe3o do Processo",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhamodelo",
            name="acessorios",
            field=models.ManyToManyField(
                related_name="come_acessorio",
                null=True,
                verbose_name="Verbas acess\xf3rio",
                to="gfp.Evento",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhamodelo",
            name="principais",
            field=models.ManyToManyField(
                related_name="como_principal",
                verbose_name="Verbas principais",
                to="gfp.Evento",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhamodelo",
            name="servidores",
            field=models.ManyToManyField(
                related_name="nos_modelos", null=True, to="rh.Servidor", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhamensagem",
            name="folha",
            field=models.ForeignKey(
                related_name="gfp_mensagens",
                verbose_name="Folha",
                to="gfp.Folha",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhamensagem",
            name="servidor",
            field=models.ForeignKey(
                related_name="gfp_mensagens",
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="folhamensagem",
            unique_together=set([("folha", "servidor")]),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="confirma_controle",
            field=models.ForeignKey(
                related_name="confirma_controle_set",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="confirma_folha",
            field=models.ForeignKey(
                related_name="confirma_folha_set",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="contracheque",
            field=models.ForeignKey(
                related_name="lancamentos",
                blank=True,
                to="gfp.ContraCheque",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="copia_de",
            field=models.ForeignKey(
                related_name="origem_para",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="gfp.FolhaEvento",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="evento",
            field=models.ForeignKey(
                related_name="lancamentos", to="gfp.Evento", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="folha",
            field=models.ForeignKey(
                related_name="lancamentos", to="gfp.Folha", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="paycheck_difference",
            field=models.ForeignKey(
                related_name="entries_payment",
                to="gfp.PaycheckDifference",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="rra_employee",
            field=models.ForeignKey(
                related_name="entries",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="RRA Servidor",
                to="gfp.RRAEmployee",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="servidor",
            field=models.ForeignKey(
                related_name="com_evento_folha",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="folhaevento",
            unique_together=set(
                [("contracheque", "evento", "info", "servidor", "folha")]
            ),
        ),
        migrations.AddField(
            model_name="folhaauditoria",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaauditoria",
            name="folha",
            field=models.ForeignKey(
                related_name="changes", to="gfp.Folha", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folhaauditoria",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="ci_por",
            field=models.ForeignKey(
                related_name="folhas_validadas",
                verbose_name="Respons\xe1vel pelo valida\xe7\xe3o",
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="fechado_por",
            field=models.ForeignKey(
                related_name="folhas_fechadas",
                verbose_name="Respons\xe1vel pelo fechamento",
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="folha_anterior",
            field=models.ForeignKey(
                related_name="folhas_copiadas",
                verbose_name="Folha anterior",
                blank=True,
                to="gfp.Folha",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="periodo",
            field=models.ForeignKey(
                related_name="folhas",
                verbose_name="Per\xedodo",
                to="gfp.Periodo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="processado_por",
            field=models.ForeignKey(
                related_name="folhas_executadas",
                verbose_name="Respons\xe1vel pela execu\xe7\xe3o",
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="folha",
            name="tipo_folha",
            field=models.ForeignKey(
                related_name="folhas",
                verbose_name="Tipo de Folha",
                to="gfp.FolhaTipo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="folha",
            unique_together=set([("periodo", "tipo_folha")]),
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="employee",
            field=models.ForeignKey(
                related_name="extrapaymentperiods",
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="extra_payment",
            field=models.ForeignKey(
                related_name="periods",
                verbose_name="Pagamento",
                to="gfp.ExtraPayment",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extrapayment",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extrapayment",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="extensionsalaryprogression",
            name="progression",
            field=models.ForeignKey(
                related_name="extensions",
                to="gfp.MovimentacaoProgressao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="calculo",
            field=models.ForeignKey(
                related_name="eventos",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="C\xe1lculo",
                blank=True,
                to="standard.ClassCode",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="consignatario",
            field=models.ForeignKey(
                related_name="eventos_consignacoes",
                blank=True,
                to="rh.PessoaJuridica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="genre_event",
            field=models.ForeignKey(
                related_name="events",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="G\xeanero do evento",
                blank=True,
                to="gfp.GenreEvent",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="incide_sobre",
            field=models.ManyToManyField(
                related_name="aplica_em",
                null=True,
                verbose_name="Incide sobre",
                to="gfp.Evento",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="previous_event",
            field=models.ForeignKey(
                related_name="replacement_events",
                verbose_name="Evento anterior",
                blank=True,
                to="gfp.Evento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="publicacao",
            field=models.ForeignKey(
                related_name="publicacao",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="specie_event",
            field=models.ForeignKey(
                related_name="events",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Esp\xe9cie do evento",
                blank=True,
                to="gfp.SpecieEvent",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="evento",
            unique_together=set([("genre_event", "specie_event")]),
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="estrutura_revogacao",
            field=models.ForeignKey(
                related_name="estrutura_revogadas",
                verbose_name="Revogado por",
                blank=True,
                to="gfp.EstruturaTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="modelo_tabela",
            field=models.ForeignKey(
                related_name="estruturas",
                verbose_name="Modelo",
                to="gfp.ModeloTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="publicacao",
            field=models.ForeignKey(
                related_name="estruturas_salariais",
                verbose_name="Publica\xe7\xe3o",
                to="rh.Publicacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="estruturatabelasalarial",
            unique_together=set([("codigo", "publicacao")]),
        ),
        migrations.AddField(
            model_name="dadobancarioservidorfolha",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dadobancarioservidorfolha",
            name="dado_bancario_pessoa",
            field=models.ForeignKey(
                related_name="dado_bancario_folhas",
                to="rh.DadoBancarioPessoa",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dadobancarioservidorfolha",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dadobancarioservidorfolha",
            name="tipo_folha",
            field=models.ForeignKey(
                related_name="banco_servidores",
                blank=True,
                to="gfp.FolhaTipo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequepensionista",
            name="contracheque_servidor",
            field=models.ForeignKey(
                related_name="servidor_contracheques",
                verbose_name="Contrachque",
                to="gfp.ContraCheque",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequepensionista",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequepensionista",
            name="dado_bancario_pessoa",
            field=models.ForeignKey(
                related_name="contracheques_pensionista",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Dado Banc\xe1rio",
                blank=True,
                to="rh.DadoBancarioPessoa",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequepensionista",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequepensionista",
            name="pensionista",
            field=models.ForeignKey(
                related_name="contracheque_pensionista",
                verbose_name="Pensionista",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="contrachequepensionista",
            unique_together=set([("contracheque_servidor", "pensionista")]),
        ),
        migrations.AddField(
            model_name="contrachequeauditoria",
            name="contracheque",
            field=models.ForeignKey(
                related_name="audit_changes",
                to="gfp.ContraCheque",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequeauditoria",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequeauditoria",
            name="folha_aplicada",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="gfp.Folha",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrachequeauditoria",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="cargo_comissao",
            field=models.ForeignKey(
                related_name="contra_cheques_cargo_comissao",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Cargo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="cargo_efetivo",
            field=models.ForeignKey(
                related_name="contra_cheques_cargo_efetivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Cargo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="cargo_eletivo",
            field=models.ForeignKey(
                related_name="contra_cheques_cargo_eletivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Cargo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="dado_bancario_pessoa",
            field=models.ForeignKey(
                related_name="contracheques",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Dado Banc\xe1rio",
                blank=True,
                to="rh.DadoBancarioPessoa",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="folha",
            field=models.ForeignKey(
                related_name="folha_contracheques",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Folha",
                to="gfp.Folha",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="lotacao",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Lota\xe7\xe3o",
                blank=True,
                to="rh.Lotacao",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salarial_comissao",
            field=models.ForeignKey(
                related_name="contracheques_comissao",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaNiveis2D",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salarial_efetivo",
            field=models.ForeignKey(
                related_name="contracheques_efetivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaNiveis2D",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salarial_eletivo",
            field=models.ForeignKey(
                related_name="contracheques_eletivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaNiveis2D",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salario_comissao",
            field=models.ForeignKey(
                related_name="contracheques_comissao",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaSalario",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salario_efetivo",
            field=models.ForeignKey(
                related_name="contracheques_efetivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaSalario",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="referencia_salario_eletivo",
            field=models.ForeignKey(
                related_name="contracheques_eletivo",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="gfp.ReferenciaSalario",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contracheque",
            name="servidor",
            field=models.ForeignKey(
                related_name="servidor_contracheques",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Servidor",
                to="rh.Servidor",
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="contracheque",
            unique_together=set([("servidor", "folha")]),
        ),
        migrations.AddField(
            model_name="cargosestrutura",
            name="cargo",
            field=models.ForeignKey(
                related_name="cargos_estrutura",
                verbose_name="Cargo",
                to="rh.Cargo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="cargosestrutura",
            name="estrutura_salarial",
            field=models.ForeignKey(
                related_name="cargos_estrutura",
                verbose_name="Estrutura Salarial",
                to="gfp.EstruturaTabelaSalarial",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="cargosestrutura",
            name="publicacao",
            field=models.ForeignKey(
                related_name="cargos_estrutura",
                verbose_name="Publica\xe7\xe3o",
                to="rh.Publicacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="cargosestrutura",
            name="referencias",
            field=models.ManyToManyField(
                related_name="cargos_estrutura",
                null=True,
                to="gfp.ReferenciaNiveis2D",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="cargosestrutura",
            unique_together=set(
                [("estrutura_salarial", "cargo", "data_vigencia_inicio")]
            ),
        ),
    ]
