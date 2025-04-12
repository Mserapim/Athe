# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaseLicencaAfastamento",
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
                ("remunerado", models.BooleanField(default=True)),
                ("concessao_durante_estagio_prob", models.BooleanField(default=True)),
                ("efetivo_exercicio", models.BooleanField(default=True)),
                ("suspensao_estagio_prob", models.BooleanField(default=False)),
                ("suspensao_contagem_ferias", models.BooleanField(default=False)),
                ("prorroga_progressao", models.BooleanField(default=False)),
                (
                    "data_inicio",
                    models.DateField(verbose_name="Data In\xedcio", db_index=True),
                ),
                (
                    "data_fim",
                    models.DateField(
                        db_index=True, null=True, verbose_name="Data Fim", blank=True
                    ),
                ),
                (
                    "data_prevista",
                    models.DateField(
                        db_index=True,
                        null=True,
                        verbose_name="Data Prevista Fim",
                        blank=True,
                    ),
                ),
                (
                    "motivo",
                    models.IntegerField(
                        default=2,
                        choices=[
                            (1, "F\xc9RIAS"),
                            (2, "LICEN\xc7A"),
                            (3, "RECESSO NATALINO"),
                            (4, "PLANT\xc3O"),
                            (5, "VIAGEM A TRABALHO"),
                            (6, "DESEMPENHO DE FUN\xc7\xc3O"),
                            (7, "DISPOSI\xc7\xc3O DE OUTRO \xd3RG\xc3O"),
                            (8, "REPRESENTA\xc7\xc3O DE CLASSE"),
                            (9, "ATUA\xc7\xc3O DE GRUPO DE TRABALHO"),
                            (10, "TR\xc2NSITO/PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                            (12, "SUSPENS\xc3O"),
                        ],
                    ),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        default=1,
                        blank=True,
                        db_index=True,
                        choices=[
                            (1, "BaseLicencaAfastamento"),
                            (2, "Afastamento"),
                            (3, "Licenca"),
                            (4, "Ausencia"),
                            (5, "FeriasAfastamento"),
                            (6, "Viagem"),
                            (7, "Recesso"),
                            (8, "LicencaSaude"),
                            (9, "LicencaSaude3Dias"),
                            (10, "LicencaSaudeJuntaMedica"),
                            (11, "LicencaDoencaPessoaFamilia"),
                            (12, "LicencaMaternidade"),
                            (13, "LicencaAdocao"),
                            (14, "LicencaAfastamentoConjuge"),
                            (15, "LicencaServicoMilitar"),
                            (16, "LicencaAtividadePolitica"),
                            (17, "LicencaCapacitacao"),
                            (18, "LicencaInteresseParticular"),
                            (19, "LicencaMandatoClassista"),
                            (20, "AfastamentoOutroOrgao"),
                            (21, "AfastamentoMandatoEletivo"),
                            (22, "AfastamentoEstudar"),
                            (23, "AfastamentoMissao"),
                            (24, "AfastamentoEleitoral"),
                            (25, "AfastamentoServirJuri"),
                            (26, "AfastamentoTreinamento"),
                            (27, "AfastamentoDeslocamento"),
                            (28, "AfastamentoCompeticao"),
                            (29, "AfastamentoCursoConcurso"),
                            (30, "AfastamentoPrisao"),
                            (31, "AusenciaDoacaoSangue"),
                            (32, "AusenciaEleitor"),
                            (33, "AusenciaCasamento"),
                            (34, "AusenciaNascimento"),
                            (35, "AusenciaFalecimento"),
                            (36, "AusenciaConclusao"),
                            (37, "LicencaSaude30Dias"),
                            (38, "FolgaEleitoral"),
                            (39, "AtuacaoGrupoTrabalho"),
                            (40, "DesempenhoFuncao"),
                            (41, "Plantao"),
                            (42, "FolgaCompensacao"),
                            (43, "FolgaAniversario"),
                            (44, "AfastamentoSuspensao"),
                            (45, "AfastamentoComparecimentoJuizo"),
                        ],
                    ),
                ),
                (
                    "estado",
                    models.IntegerField(
                        default=1,
                        blank=True,
                        db_index=True,
                        choices=[
                            (1, "AGENDADO"),
                            (2, "ATIVO"),
                            (3, "ENCERRADO"),
                            (4, "CANCELADO"),
                        ],
                    ),
                ),
                (
                    "alteracao",
                    models.IntegerField(
                        default=None,
                        null=True,
                        verbose_name="Tipo Altera\xe7\xe3o",
                        blank=True,
                        choices=[
                            (1, "Revoga\xe7\xe3o"),
                            (2, "Altera\xe7\xe3o a pedido"),
                            (3, "Suspens\xe3o"),
                            (4, "Cancelado"),
                            (5, "Interrup\xe7\xe3o"),
                        ],
                    ),
                ),
                ("agendado_arquimedes", models.BooleanField(default=False)),
                (
                    "situation_unicode",
                    models.CharField(
                        max_length=255,
                        null=True,
                        verbose_name="Motivo Cache",
                        blank=True,
                    ),
                ),
                (
                    "annotation_class",
                    models.CharField(
                        max_length=255,
                        null=True,
                        verbose_name="Classe da Anota\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ["data_inicio", "-estado"],
                "db_table": "afastamento_baselicencaafast",
                "verbose_name": "BaseLicencaAfastamento",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="Ausencia",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_ausencia",
                "verbose_name": "Aus\xeancia",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="AusenciaNascimento",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "crianca",
                    models.ForeignKey(
                        related_name="ausencianascimento",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Filho(a)",
                        to="rh.PessoaFisica",
                        unique=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_ausencianascimento",
                "verbose_name": "Aus\xeancia Nascimento",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AusenciaFalecimento",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "vinculo",
                    models.IntegerField(
                        default=10,
                        verbose_name="Tipo de V\xednculo",
                        choices=[
                            (1, "C\xd4NJUGE"),
                            (2, "COMPANHEIRO"),
                            (3, "FILHO(A)"),
                            (4, "PAI/M\xc3E"),
                            (5, "IRM\xc3O"),
                            (6, "ENTEADO"),
                            (7, "MENOR TUTELADO"),
                            (8, "EX-C\xd4NJUGE"),
                            (9, "NETOS"),
                            (10, "OUTROS"),
                        ],
                    ),
                ),
                (
                    "pessoa",
                    models.ForeignKey(
                        related_name="ausenciafalecimento",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Pessoa",
                        to="rh.PessoaFisica",
                        unique=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_ausenciafalecimento",
                "verbose_name": "Aus\xeancia Falecimento",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AusenciaEleitor",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_ausenciaeleitor",
                "verbose_name": "Aus\xeancia Alistamento Eleitoral",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AusenciaDoacaoSangue",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_ausenciasangue",
                "verbose_name": "Aus\xeancia Doa\xe7\xe3o de Sangue",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AusenciaConclusao",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "curso",
                    models.ForeignKey(
                        related_name="ausenciaconclusao",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Curso",
                        to="rh.Curso",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_ausenciaconclusao",
                "verbose_name": "Aus\xeancia Conclus\xe3o",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AusenciaCasamento",
            fields=[
                (
                    "ausencia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Ausencia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("data_casamento", models.DateField(verbose_name="Data Casamento")),
                (
                    "conjuge",
                    models.ForeignKey(
                        related_name="ausenciacasamento",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Conjuge",
                        to="rh.PessoaFisica",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_ausenciacasamento",
                "verbose_name": "Aus\xeancia Casamento",
            },
            bases=("afastamento.ausencia",),
        ),
        migrations.CreateModel(
            name="AtuacaoGrupoTrabalho",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_atuacaogrupotrabalho",
                "verbose_name": "Atua\xe7\xe3o Grupo de Trabalho",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="Afastamento",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastamento",
                "verbose_name": "Afastamento",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoTreinamento",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("carga_horaria", models.IntegerField(null=True, blank=True)),
                (
                    "curso",
                    models.ForeignKey(
                        related_name="afastamentotreinamento",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="rh.Curso",
                        null=True,
                    ),
                ),
                (
                    "instituicao",
                    models.ManyToManyField(
                        related_name="afastamentotreinamento",
                        null=True,
                        to="rh.UnidadeAdministrativa",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_afasttreinamento",
                "verbose_name": "Afastamento Treinamento",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoSuspensao",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("prazo_dias", models.IntegerField(verbose_name="Prazo em dias")),
            ],
            options={
                "db_table": "afastamento_afastsuspensao",
                "verbose_name": "Afastamento Suspens\xe3o",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoServirJuri",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "localidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastjuri",
                "verbose_name": "Afastamento para Servir ao J\xfari",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoPrisao",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "prazo_anos",
                    models.IntegerField(
                        default=0, verbose_name="Prazo em anos", blank=True
                    ),
                ),
                (
                    "prazo_meses",
                    models.IntegerField(
                        default=0, verbose_name="Prazo em meses", blank=True
                    ),
                ),
                ("prazo_dias", models.IntegerField(verbose_name="Prazo em dias")),
                ("motivo_prisao", models.TextField(null=True, blank=True)),
            ],
            options={
                "db_table": "afastamento_afastprisao",
                "verbose_name": "Afastamento Pris\xe3o",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoOutroOrgao",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "onus",
                    models.IntegerField(
                        default=2,
                        verbose_name="\xd4nus",
                        choices=[(1, "ORIGEM"), (2, "REQUISITANTE")],
                    ),
                ),
                (
                    "contribuicao",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Op\xe7\xe3o de contribui\xe7\xe3o",
                        blank=True,
                        choices=[(1, "SIM"), (2, "N\xc3O")],
                    ),
                ),
                (
                    "transito_pela_folha",
                    models.BooleanField(
                        default=False, verbose_name="Tr\xe2nsito/FOPAG"
                    ),
                ),
                (
                    "orgao",
                    models.ForeignKey(
                        to="rh.UnidadeAdministrativa",
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
                (
                    "posse",
                    models.ForeignKey(
                        related_name="afastamento",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.MovimentacaoPosse",
                    ),
                ),
                (
                    "quadro_destino",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Cargo no destino",
                        blank=True,
                        to="rh.Quadro",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_afastoutroorgao",
                "verbose_name": "Afastamento para Outro \xd3rg\xe3o",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoMissao",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("objetivo", models.TextField(null=True, blank=True)),
                (
                    "orgao",
                    models.ForeignKey(
                        to="rh.UnidadeAdministrativa",
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_afastmissao",
                "verbose_name": "Afastamento para Miss\xe3o",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoMandatoEletivo",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cargo_eletivo",
                    models.IntegerField(
                        default=1,
                        verbose_name="Cargo Eletivo",
                        choices=[
                            (1, "Prefeito/Vice"),
                            (2, "Vereador"),
                            (3, "Deputado Estadual"),
                            (4, "Deputado Federal"),
                            (5, "Governador/Vice"),
                            (6, "Senador/Presidente Rep\xfablica/Vice"),
                        ],
                    ),
                ),
                (
                    "partido",
                    models.CharField(
                        default="", max_length=100, verbose_name="Partido Pol\xedtico"
                    ),
                ),
                (
                    "localidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastmandatoeletivo",
                "verbose_name": "Afastamento Mandato Eletivo",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoEstudar",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "curso",
                    models.ForeignKey(
                        to="rh.Curso", on_delete=django.db.models.deletion.PROTECT
                    ),
                ),
                (
                    "instituicao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Institui\xe7\xe3o",
                        to="rh.UnidadeAdministrativa",
                    ),
                ),
                (
                    "localidade",
                    models.ForeignKey(
                        to="rh.Localidade", on_delete=django.db.models.deletion.PROTECT
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_afastestudar",
                "verbose_name": "Afastamento para Estudar",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoEleitoral",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afasteleitoral",
                "verbose_name": "Afastamento Convoca\xe7\xe3o Eleitoral",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoDeslocamento",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "localidade_destino",
                    models.ForeignKey(
                        related_name="localidade_destino",
                        to="rh.Localidade",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "localidade_origem",
                    models.ForeignKey(
                        related_name="localidade_origem",
                        to="rh.Localidade",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastdeslocamento",
                "verbose_name": "Afastamento Deslocamento",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoCursoConcurso",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cargo",
                    models.ForeignKey(
                        blank=True, to="rh.Cargo", null=True, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "orgao",
                    models.ForeignKey(
                        to="rh.UnidadeAdministrativa",
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_afastcursoconcurso",
                "verbose_name": "Afastamento Curso de Concurso",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoCompeticao",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastcompeticao",
                "verbose_name": "Afastamento para Competi\xe7\xe3o",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="AfastamentoComparecimentoJuizo",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_afastcompjuizo",
                "verbose_name": "Afastamento comparecer a ju\xedzo",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.CreateModel(
            name="DesempenhoFuncao",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_desempenhofuncao",
                "verbose_name": "Desempenho de Fun\xe7\xe3o",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="FeriasAfastamento",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_feriasafastamento",
                "verbose_name": "F\xe9rias",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="FolgaAniversario",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_referencia",
                    models.DateField(verbose_name="Data de refer\xeancia"),
                ),
                ("ano", models.IntegerField()),
                (
                    "anotacao_aquisicao",
                    models.ForeignKey(
                        related_name="usufrutofolgaaniversario",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Anota\xe7\xe3o de Aquisi\xe7\xe3o",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_folgaaniversario",
                "verbose_name": "Folga Anivers\xe1rio",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="FolgaCompensacao",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "anotacao_aquisicao",
                    models.ForeignKey(
                        related_name="usufrutofolgacompensacao",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Anota\xe7\xe3o de Aquisi\xe7\xe3o",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_folgacompensacao",
                "verbose_name": "Folga Compensa\xe7\xe3o",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="FolgaEleitoral",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ano",
                    models.PositiveIntegerField(verbose_name="Ano de Elei\xe7\xe3o"),
                ),
                (
                    "turno",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[(1, "1\xba"), (2, "2\xba"), (3, "1\xba e 2\xba")],
                    ),
                ),
                (
                    "anotacao_aquisicao",
                    models.ForeignKey(
                        related_name="usufrutofolgaeleitoral",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Anota\xe7\xe3o de Aquisi\xe7\xe3o",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_folgaeleitoral",
                "verbose_name": "Folga Eleitoral",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="Licenca",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licenca",
                "verbose_name": "Licen\xe7a",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="LicencaAfastamentoConjuge",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "conjuge",
                    models.ForeignKey(
                        related_name="licencaafastamentoconjuge_conjuge",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="C\xf4njuge",
                        to="rh.PessoaFisica",
                        null=True,
                    ),
                ),
                (
                    "orgao",
                    models.ForeignKey(
                        related_name="afastamentoconjuge_orgaoconjuge",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Org\xe3o/Entidade do C\xf4njuge",
                        to="rh.UnidadeAdministrativa",
                    ),
                ),
                (
                    "orgao_destino",
                    models.ForeignKey(
                        related_name="afastamentoconjuge",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Destino da transfer\xeancia",
                        to="rh.UnidadeAdministrativa",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licafastamentoconj",
                "verbose_name": "Licen\xe7a Afastamento C\xf4njuge/Companheiro",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="LicencaAtividadePolitica",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cargo_eletivo",
                    models.IntegerField(
                        default=1,
                        verbose_name="Cargo Eletivo",
                        choices=[
                            (1, "Prefeito/Vice"),
                            (2, "Vereador"),
                            (3, "Deputado Estadual"),
                            (4, "Deputado Federal"),
                            (5, "Governador/Vice"),
                            (6, "Senador/Presidente Rep\xfablica/Vice"),
                        ],
                    ),
                ),
                (
                    "partido",
                    models.CharField(
                        default="", max_length=100, verbose_name="Partido Pol\xedtico"
                    ),
                ),
                (
                    "localidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licencapolitica",
                "verbose_name": "Licen\xe7a Atividade Pol\xedtica",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="LicencaCapacitacao",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "curso",
                    models.ForeignKey(
                        to="rh.Curso", on_delete=django.db.models.deletion.PROTECT
                    ),
                ),
                (
                    "instituicao",
                    models.ForeignKey(
                        to="rh.UnidadeAdministrativa",
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencacapacitacao",
                "verbose_name": "Licen\xe7a Capacita\xe7\xe3o",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="LicencaInteresseParticular",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licencainteresse",
                "verbose_name": "Licen\xe7a Interesse Particular",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="LicencaMandatoClassista",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cargo",
                    models.CharField(default="", max_length=100, verbose_name="Cargo"),
                ),
                (
                    "tipo_entidade",
                    models.IntegerField(
                        default=1,
                        verbose_name="Tipo Entidade",
                        choices=[
                            (1, "Confedera\xe7\xe3o"),
                            (2, "Federa\xe7\xe3o"),
                            (3, "Associa\xe7\xe3o Classe Nacional"),
                            (4, "Associa\xe7\xe3o Classe Estadual"),
                            (5, "Sindicato e Entidade Fiscalizadora da Profiss\xe3o"),
                        ],
                    ),
                ),
                (
                    "entidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Entidade",
                        to="rh.UnidadeAdministrativa",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencaclassista",
                "verbose_name": "Licen\xe7a Mandato Classista",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="LicencaSaude",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "prazo_solicitado",
                    models.IntegerField(verbose_name="Prazo Solicitado"),
                ),
                (
                    "prazo_concedido",
                    models.IntegerField(
                        null=True, verbose_name="Prazo Concedido", blank=True
                    ),
                ),
                (
                    "aprovacao",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[
                            (1, "N\xe3o informada"),
                            (2, "Deferida"),
                            (3, "Indeferida"),
                        ],
                    ),
                ),
                (
                    "codigo_internacional_doenca",
                    models.CharField(
                        max_length=20, null=True, verbose_name="CID", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencasaude",
                "verbose_name": "Licen\xe7a Sa\xfade",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="BaseLicencaSaudeJuntaMedica",
            fields=[
                (
                    "licencasaude_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.LicencaSaude",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_envio",
                    models.DateField(
                        null=True, verbose_name="Data envio Junta", blank=True
                    ),
                ),
                (
                    "data_retorno",
                    models.DateField(
                        null=True, verbose_name="Data retorno Junta", blank=True
                    ),
                ),
                (
                    "parecer",
                    models.TextField(null=True, verbose_name="Parecer", blank=True),
                ),
            ],
            options={
                "db_table": "afastamento_baselicsaudejuntamed",
                "verbose_name": "BaseLicencaAfastamentoJuntaMedica",
            },
            bases=("afastamento.licencasaude",),
        ),
        migrations.CreateModel(
            name="LicencaMaternidade",
            fields=[
                (
                    "baselicencasaudejuntamedica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaSaudeJuntaMedica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_parto",
                    models.DateField(
                        null=True, verbose_name="Data Parto/Aborto", blank=True
                    ),
                ),
                (
                    "natimorto",
                    models.BooleanField(
                        default=False, verbose_name="Natimorto/Neomorto ou Aborto"
                    ),
                ),
                (
                    "crianca",
                    models.ForeignKey(
                        related_name="licencamaternidade",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Filho(a)",
                        blank=True,
                        to="rh.PessoaFisica",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencamaternidade",
                "verbose_name": "Licen\xe7a Maternidade",
            },
            bases=("afastamento.baselicencasaudejuntamedica",),
        ),
        migrations.CreateModel(
            name="LicencaDoencaPessoaFamilia",
            fields=[
                (
                    "baselicencasaudejuntamedica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaSaudeJuntaMedica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "grau_parentesco",
                    models.IntegerField(
                        default=1,
                        verbose_name="Tipo de Parentesco",
                        choices=[
                            (1, "C\xf4njuge/Companheiro(a)"),
                            (2, "Pai/M\xe3e"),
                            (3, "Madrasta/Padrasto"),
                            (4, "Filho(a)"),
                            (5, "Enteado(a)"),
                            (6, "Dependente"),
                        ],
                    ),
                ),
                (
                    "acompanhado",
                    models.ForeignKey(
                        related_name="licencadoenca",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Acompanhado",
                        to="rh.PessoaFisica",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencadoenca",
                "verbose_name": "Licen\xe7a Doen\xe7a Pessoa da Fam\xedlia",
            },
            bases=("afastamento.baselicencasaudejuntamedica",),
        ),
        migrations.CreateModel(
            name="LicencaAdocao",
            fields=[
                (
                    "baselicencasaudejuntamedica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaSaudeJuntaMedica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "crianca",
                    models.ForeignKey(
                        related_name="licencaadocao",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Adotado(a)",
                        to="rh.PessoaFisica",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_licencaadocao",
                "verbose_name": "Licen\xe7a Ado\xe7\xe3o",
            },
            bases=("afastamento.baselicencasaudejuntamedica",),
        ),
        migrations.CreateModel(
            name="LicencaSaude30Dias",
            fields=[
                (
                    "licencasaude_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.LicencaSaude",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licencasaude30dias",
                "verbose_name": "Licen\xe7a Sa\xfade de at\xe9 30 Dias",
            },
            bases=("afastamento.licencasaude",),
        ),
        migrations.CreateModel(
            name="LicencaSaude3Dias",
            fields=[
                (
                    "licencasaude_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.LicencaSaude",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licencasaude3dias",
                "verbose_name": "Licen\xe7a Sa\xfade de at\xe9 3 Dias",
            },
            bases=("afastamento.licencasaude",),
        ),
        migrations.CreateModel(
            name="LicencaSaudeJuntaMedica",
            fields=[
                (
                    "baselicencasaudejuntamedica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaSaudeJuntaMedica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_licsaudejuntamed",
                "verbose_name": "Licen\xe7a Sa\xfade Junta M\xe9dica",
            },
            bases=("afastamento.baselicencasaudejuntamedica",),
        ),
        migrations.CreateModel(
            name="LicencaServicoMilitar",
            fields=[
                (
                    "licenca_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Licenca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio_servico",
                    models.DateField(verbose_name="Data In\xedcio Servi\xe7o"),
                ),
                (
                    "data_fim_servico",
                    models.DateField(verbose_name="Data Fim Seri\xe7o"),
                ),
            ],
            options={
                "db_table": "afastamento_licservicomil",
                "verbose_name": "Licen\xe7a Servi\xe7o Militar",
            },
            bases=("afastamento.licenca",),
        ),
        migrations.CreateModel(
            name="Plantao",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "anotacao_aquisicao",
                    models.ForeignKey(
                        related_name="usufrutoplantao",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Anota\xe7\xe3o de Aquisi\xe7\xe3o",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_plantao",
                "verbose_name": "Plant\xe3o",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="Recesso",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ano",
                    models.CharField(
                        default="", max_length=9, verbose_name="Ano do Recesso"
                    ),
                ),
                (
                    "anotacao_aquisicao",
                    models.ForeignKey(
                        related_name="usufrutorecesso",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Anota\xe7\xe3o de Aquisi\xe7\xe3o",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_recesso",
                "verbose_name": "Recesso",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.CreateModel(
            name="Viagem",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_viagem",
                "verbose_name": "Viagem",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="atestado_medico",
            field=models.ForeignKey(
                related_name="atestado_licensa_saude",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="ged.Arquivo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="profissional_saude",
            field=models.ForeignKey(
                related_name="licencasaude",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Profissional Sa\xfade",
                blank=True,
                to="rh.ProfissionalSaude",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baselicencasaudejuntamedica",
            name="atestado_junta_medica",
            field=models.ForeignKey(
                related_name="atestado_avaliacao_junta_medica",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="ged.Arquivo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baselicencasaudejuntamedica",
            name="documento",
            field=models.ManyToManyField(
                related_name="documentos_licencasaudejunta",
                null=True,
                verbose_name="Documenta\xe7\xe3o Complementar",
                to="ged.Arquivo",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baselicencasaudejuntamedica",
            name="documento_solicitacao",
            field=models.ForeignKey(
                related_name="documento_avaliacao_junta_medica",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="ged.Arquivo",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baselicencaafastamento",
            name="prorrogacao",
            field=models.ManyToManyField(
                related_name="afastamento",
                verbose_name="Prorroga\xe7\xe3o",
                to="rh.Prorrogacao",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baselicencaafastamento",
            name="publicacao_fim",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Documento Encerramento",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
