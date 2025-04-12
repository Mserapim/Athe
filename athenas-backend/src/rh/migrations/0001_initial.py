# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0001_initial"),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArqDesignacaoExercicio",
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
                ("matricula", models.IntegerField(verbose_name="Matr\xedcula")),
                ("cargo", models.IntegerField(verbose_name="Cargo")),
            ],
            options={
                "db_table": "DESIG_EXERCICIO_ARQUIMEDES",
                "managed": False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ArqTabelaSubstituicao",
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
                    "cargo",
                    models.CharField(max_length=20, null=True, verbose_name="Cargo"),
                ),
                (
                    "cargo_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo nome"
                    ),
                ),
                (
                    "cargo_exerc_matricula",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Matr\xedcula Titular"
                    ),
                ),
                (
                    "cargo_exerc_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo exerc nome"
                    ),
                ),
                (
                    "cargo_exerc_plena",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo exerc plena"
                    ),
                ),
                (
                    "cargo_afast_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo afast matr\xedcula",
                    ),
                ),
                (
                    "cargo_afast_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo afast nome"
                    ),
                ),
                (
                    "cargo_tit_matricula",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo tit matr\xedcula"
                    ),
                ),
                (
                    "cargo_tit_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo tit nome"
                    ),
                ),
                (
                    "cargo_subs_1",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1"
                    ),
                ),
                (
                    "cargo_subs_1_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 nome"
                    ),
                ),
                (
                    "cargo_subs_1_exerc_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs1 exerc matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_1_exerc_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 exerc nome"
                    ),
                ),
                (
                    "cargo_subs_1_exerc_plena",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 exerc plena"
                    ),
                ),
                (
                    "cargo_subs_1_afast_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs1 afast matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_1_afast_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 afast nome"
                    ),
                ),
                (
                    "cargo_subs_1_tit_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs1 tit matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_1_tit_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 tit nome"
                    ),
                ),
                (
                    "cargo_subs_2",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs2"
                    ),
                ),
                (
                    "cargo_subs_2_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs2 nome"
                    ),
                ),
                (
                    "cargo_subs_2_exerc_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs2 exerc matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_2_exerc_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs2 exerc nome"
                    ),
                ),
                (
                    "cargo_subs_2_exerc_plena",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs1 exerc plena"
                    ),
                ),
                (
                    "cargo_subs_2_afast_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs2 afast matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_2_afast_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs2 afast nome"
                    ),
                ),
                (
                    "cargo_subs_2_tit_matricula",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Cargo subs2 tit matr\xedcula",
                    ),
                ),
                (
                    "cargo_subs_2_tit_nome",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Cargo subs2 tit nome"
                    ),
                ),
            ],
            options={
                "db_table": "VW_TABELA_SUBSTITUICAO_NEW",
                "managed": False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AnotacaoGeral",
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
                    "tipo_documento",
                    models.IntegerField(
                        verbose_name="Tipo Documento",
                        choices=[
                            (1, "ATO"),
                            (3, "PORTARIA"),
                            (4, "OF\xcdCIO"),
                            (5, "DESPACHO"),
                            (6, "TERMO"),
                            (7, "MEMORANDO"),
                            (8, "REQUERIMENTO"),
                            (9, "CONCESS\xc3O"),
                            (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                            (12, "APOSTILA"),
                            (99, "OUTROS"),
                            (100, "DOCUMENTO DIGITAL"),
                        ],
                    ),
                ),
                (
                    "numero_documento",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="N\xfamero Documento",
                        blank=True,
                    ),
                ),
                (
                    "data_documento",
                    models.DateField(
                        auto_now_add=True, verbose_name="Data Documento", null=True
                    ),
                ),
                (
                    "data_portaria_inicio",
                    models.DateField(
                        null=True, verbose_name="Data Portaria In\xedcio", blank=True
                    ),
                ),
                ("resumo", models.CharField(max_length=150, null=True, blank=True)),
                ("texto", models.CharField(max_length=2000, null=True, blank=True)),
                ("ativa", models.BooleanField(default=True)),
                (
                    "numero_processo",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="N\xfamero Processo",
                        blank=True,
                    ),
                ),
                ("indireto", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("-id",),
                "db_table": "rh_anotgeral",
                "verbose_name": "Anota\xe7\xe3o Geral",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AnotacaoFolgaEleitoral",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotfolgaeleitoral",
                "verbose_name": "Anota\xe7\xe3o Folga Eleitoral",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoFolgaCompensacao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotfolgacompensacao",
                "verbose_name": "Anota\xe7\xe3o Folga Compensa\xe7\xe3o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoFolgaAniversario",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotfolgaaniversario",
                "verbose_name": "Anota\xe7\xe3o Folga Anivers\xe1rio",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoFerias",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tipo",
                    models.CharField(
                        default="HOMOLOGACAO",
                        max_length=20,
                        verbose_name="Tipo",
                        blank=True,
                        choices=[
                            ("INTERRUPCAO", "Interrup\xc3\xa7\xc3\xa3o"),
                            ("HOMOLOGACAO", "Homologa\xc3\xa7\xc3\xa3o"),
                            ("ALTERACAO", "Altera\xc3\xa7\xc3\xa3o"),
                            ("SUSPENSAO", "Suspens\xc3\xa3o"),
                            ("MARCACAO", "Marca\xc3\xa7\xc3\xa3o"),
                        ],
                    ),
                ),
                (
                    "identificador",
                    models.CharField(
                        max_length=20, verbose_name="Identificador", blank=True
                    ),
                ),
                (
                    "periodo",
                    models.CharField(
                        default="---",
                        max_length=50,
                        verbose_name="Per\xedodo",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotferias",
                "verbose_name": "Anota\xe7\xe3o F\xe9rias",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoFalta",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                ("abonada", models.BooleanField(default=False)),
                ("dias", models.IntegerField(null=True, blank=True)),
            ],
            options={
                "db_table": "rh_anotfalta",
                "verbose_name": "Anota\xe7\xe3o Falta",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoEvento",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "nome_evento",
                    models.CharField(max_length=100, verbose_name="Nome Evento"),
                ),
                (
                    "tipo_participacao",
                    models.IntegerField(
                        verbose_name="Tipo de Participa\xe7\xe3o",
                        choices=[
                            (1, "CONVIDADO"),
                            (2, "CONVOCADO"),
                            (3, "PARTICIPANTE"),
                        ],
                    ),
                ),
                (
                    "tipo_evento",
                    models.IntegerField(
                        verbose_name="Tipo de Evento",
                        choices=[
                            (3, "OUTROS"),
                            (2, "SEMIN\xc1RIO"),
                            (1, "CURSO DE CAPACITA\xc7\xc3O PROFISSIONAL"),
                        ],
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "carga_horaria",
                    models.IntegerField(
                        null=True, verbose_name="Carga Hor\xe1ria", blank=True
                    ),
                ),
                (
                    "instituicao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Institui\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "efeito_progressao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Efeito Progress\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotevento",
                "verbose_name": "Anota\xe7\xe3o Evento",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoEnquadramento",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "complemento_cargo",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                ("lei", models.CharField(max_length=30, null=True, blank=True)),
            ],
            options={
                "db_table": "rh_anotenquadramento",
                "verbose_name": "Anota\xe7\xe3o Enquadramento",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoElogio",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotelogio",
                "verbose_name": "Anota\xe7\xe3o Elogio",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoComunicacao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tipo_comunicacao",
                    models.IntegerField(
                        verbose_name="Tipo Comunica\xe7\xe3o",
                        choices=[
                            (3, "F\xc9RIAS"),
                            (1, "RECESSO"),
                            (2, "LICEN\xc7A"),
                            (4, "AUS\xcaNCIA DA COMARCA"),
                        ],
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotcomunicacao",
                "verbose_name": "Anota\xe7\xe3o Comunica\xe7\xe3o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoCarreira",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
                "db_table": "rh_anotcarreira",
                "verbose_name": "Anota\xe7\xe3o Carreira",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoAusencia",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotausencia",
                "verbose_name": "Anota\xe7\xe3o Afastamento",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoAfastamento",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotafastamento",
                "verbose_name": "Anota\xe7\xe3o Afastamento",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoGratificacao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("data_inicio", models.DateField(null=True, blank=True)),
                ("data_fim", models.DateField(null=True, blank=True)),
            ],
            options={
                "db_table": "rh_anotgratificacao",
                "verbose_name": "Anota\xe7\xe3o Gratifica\xe7\xe3o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoHorarioEspecial",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_anothorarioespecial",
                "verbose_name": "Anota\xe7\xe3o Hor\xe1rio Especial (AHE)",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoLicenca",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "prazo_dias",
                    models.IntegerField(
                        null=True, verbose_name="Prazo Dias", blank=True
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                ("remunerada", models.BooleanField(default=True)),
                (
                    "quinquenio",
                    models.IntegerField(
                        null=True, verbose_name="Quinqu\xeanio", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotlicenca",
                "verbose_name": "Anota\xe7\xe3o Licen\xe7a",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoPenaDisciplinar",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "data_decisao",
                    models.DateField(
                        null=True, verbose_name="Data Decis\xe3o", blank=True
                    ),
                ),
                (
                    "texto_decisao",
                    models.TextField(
                        null=True, verbose_name="Texto Decis\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotpenadisciplinar",
                "verbose_name": "Anota\xe7\xe3o Pena Disciplinar",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoPlantao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("ano", models.IntegerField(null=True, blank=True)),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "data_reassuncao",
                    models.DateField(
                        null=True, verbose_name="Data Reassun\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "periodo",
                    models.CharField(
                        max_length=10,
                        verbose_name="Per\xedodo",
                        choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
                    ),
                ),
                (
                    "situacao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Situa\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotplantao",
                "verbose_name": "Anota\xe7\xe3o Folga Eleitoral",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoRecesso",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("ano", models.IntegerField(null=True, blank=True)),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "data_reassuncao",
                    models.DateField(
                        null=True, verbose_name="Data Reassun\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "periodo",
                    models.CharField(
                        max_length=10,
                        verbose_name="Per\xedodo",
                        choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
                    ),
                ),
                (
                    "situacao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Situa\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "rh_anotrecesso",
                "verbose_name": "Anota\xe7\xe3o Recesso",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoRemocao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_anotremocao",
                "verbose_name": "Anota\xe7\xe3o Remo\xe7\xe3o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoTempoDobro",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ano_ferias",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Ano F\xe9rias",
                        blank=True,
                    ),
                ),
                (
                    "periodo",
                    models.CharField(
                        max_length=10,
                        verbose_name="Per\xedodo",
                        choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
                    ),
                ),
                (
                    "total_dias",
                    models.IntegerField(
                        null=True, verbose_name="Total Dias", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "rh_anottempodobro",
                "verbose_name": "Anota\xe7\xe3o Tempo em Dobro",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoTempoServico",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tempo_liquido",
                    models.IntegerField(
                        null=True, verbose_name="Tempo L\xedquido", blank=True
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "responsavel",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Respons\xe1vel",
                        blank=True,
                    ),
                ),
                ("parecer", models.CharField(max_length=100, null=True, blank=True)),
                ("anos", models.IntegerField(null=True, blank=True)),
                ("meses", models.IntegerField(null=True, blank=True)),
                ("dias", models.IntegerField(null=True, blank=True)),
            ],
            options={
                "db_table": "rh_anottemposervico",
                "verbose_name": "Anota\xe7\xe3o Tempo de Servi\xe7o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoTransposicao",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_opcao",
                    models.DateField(
                        null=True, verbose_name="Data Op\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "rh_anottransposicao",
                "verbose_name": "Anota\xe7\xe3o Transposi\xe7\xe3o",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotacaoViagem",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotviagem",
                "verbose_name": "Anota\xe7\xe3o Viagem",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.CreateModel(
            name="AnotHorEspDados",
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
                    "dia_semana",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Dia da Semana",
                        choices=[
                            (1, "DOMINGO"),
                            (2, "SEGUNDA"),
                            (3, "TER\xc7A"),
                            (4, "QUARTA"),
                            (5, "QUINTA"),
                            (6, "SEXTA"),
                            (7, "S\xc1BADO"),
                        ],
                    ),
                ),
                (
                    "turno",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Turno",
                        choices=[
                            (1, "MATUTINO"),
                            (2, "VESPERTINO"),
                            (3, "NOTURNO"),
                            (4, "DIA INTEIRO"),
                        ],
                    ),
                ),
                (
                    "ent_saida",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Entrada/Sa\xedda",
                        choices=[(1, "ENTRADA"), (2, "SA\xcdDA")],
                    ),
                ),
                (
                    "horario",
                    models.CharField(
                        max_length=5, null=True, verbose_name="Hor\xe1rio", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Dados espec\xedficos de AHE",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Banco",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "numero",
                    models.CharField(
                        unique=True, max_length=3, verbose_name="N\xfamero"
                    ),
                ),
                ("sigla", models.CharField(max_length=6, null=True, blank=True)),
                (
                    "tem_convenio",
                    models.PositiveIntegerField(
                        null=True,
                        verbose_name="Tem Conv\xeanio?",
                        choices=[
                            (0, "N\xc3O"),
                            (1, "SIM"),
                            (2, "DOCUMENTO ELETR\xd4NICO DE CR\xc9DITO (DOC)"),
                        ],
                    ),
                ),
                (
                    "numero_convenio",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="N\xfamero Conv\xeanio",
                        blank=True,
                    ),
                ),
                (
                    "agencia",
                    models.CharField(
                        max_length=10, null=True, verbose_name="Ag\xeancia", blank=True
                    ),
                ),
                (
                    "dv_agencia",
                    models.CharField(
                        max_length=2,
                        null=True,
                        verbose_name="DV Ag\xeancia",
                        blank=True,
                    ),
                ),
                ("conta", models.CharField(max_length=20, null=True, blank=True)),
                (
                    "dv_conta",
                    models.CharField(
                        max_length=2, null=True, verbose_name="DV Conta", blank=True
                    ),
                ),
                (
                    "principal",
                    models.BooleanField(default=False, verbose_name="Banco Principal"),
                ),
                (
                    "sequencial_arquivo",
                    models.IntegerField(default=0, verbose_name="Sequencial"),
                ),
            ],
            options={
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Capacidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CargaHoraria",
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
                ("texto", models.TextField(null=True, blank=True)),
                (
                    "anota",
                    models.BooleanField(
                        default=True, verbose_name="Gera Anota\xe7\xe3o"
                    ),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        default=1, choices=[(1, "SEMANAL"), (2, "MENSAL")]
                    ),
                ),
                ("quantidade", models.DecimalField(max_digits=3, decimal_places=1)),
                ("data_inicio", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Cargo",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "indicativo",
                    models.CharField(
                        default="S",
                        max_length=1,
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
                    "tipo_lei_cargo",
                    models.CharField(
                        default="EF",
                        max_length=2,
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
                ("codigo", models.CharField(max_length=12, verbose_name="C\xf3digo")),
                (
                    "acumulavel",
                    models.BooleanField(default=False, verbose_name="Acumul\xe1vel"),
                ),
                ("professor", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "designa_exercicio",
                    models.BooleanField(
                        default=True, verbose_name="Designa Exerc\xedcio"
                    ),
                ),
                (
                    "poder",
                    models.IntegerField(
                        default=5,
                        choices=[
                            (1, "EXECUTIVO"),
                            (2, "LEGISLATIVO"),
                            (3, "JUDICI\xc1RIO"),
                            (4, "MINIST\xc9RIO P\xdaBLICO"),
                            (5, "DESCONHECIDO"),
                            (6, "TRIBUNAL DE CONTAS"),
                        ],
                    ),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                ("chefia", models.BooleanField(default=False)),
                (
                    "substituivel",
                    models.BooleanField(default=False, verbose_name="Substitu\xedvel"),
                ),
                ("cargo_arquimedes", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["nome"],
                "verbose_name": "Cargo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CargoQuadro",
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
                    "quantidade_vagas",
                    models.IntegerField(verbose_name="Quantidade de Vagas"),
                ),
                (
                    "nivel_escolaridade",
                    models.IntegerField(
                        null=True,
                        verbose_name="N\xedvel de Escolaridade",
                        choices=[
                            (1, "FUNDAMENTAL"),
                            (2, "M\xc9DIO"),
                            (3, "SUPERIOR"),
                            (4, "ELEMENTAR"),
                        ],
                    ),
                ),
                ("carga_horaria", models.IntegerField(verbose_name="Carga Hor\xe1ria")),
                (
                    "tipo_carga_horaria",
                    models.IntegerField(
                        verbose_name="Tipo Carga Hor\xe1ria",
                        choices=[(1, "SEMANAL"), (2, "MENSAL")],
                    ),
                ),
            ],
            options={
                "verbose_name": "Quadro do cargo e especialidade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Carreira",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("codigo", models.CharField(max_length=10, verbose_name="C\xf3digo")),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                ("data_fim", models.DateField(null=True, blank=True)),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
            ],
            options={
                "verbose_name": "Carreira",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Cbo",
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
                ("codigo", models.CharField(max_length=10, verbose_name="C\xf3digo")),
                (
                    "descricao",
                    models.CharField(max_length=250, verbose_name="Descri\xe7\xe3o"),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CensoEstudo",
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
                    "nivel_escolaridade",
                    models.IntegerField(
                        default=0,
                        choices=[
                            (1, "M\xc9DIO"),
                            (2, "T\xc9CNICO"),
                            (3, "SUPERIOR"),
                            (4, "P\xd3S-GRADUA\xc7\xc3O"),
                            (5, "MESTRADO"),
                            (6, "DOUTORADO"),
                            (7, "P\xd3S-DOUTORADO"),
                        ],
                    ),
                ),
                ("instituicao", models.TextField(null=True, blank=True)),
                ("curso", models.TextField(null=True, blank=True)),
                ("ano_conclusao", models.SmallIntegerField(default=0)),
            ],
            options={
                "permissions": (("escol_admin", "administra escolaridade"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CensoPrevidenciario",
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
                    "tipo_regime",
                    models.IntegerField(
                        default=0,
                        choices=[
                            (1, "REGIME GERAL DE PREVID\xcaNCIA"),
                            (2, "REGIME PR\xd3PRIO DE PREVID\xcaNCIA"),
                        ],
                    ),
                ),
                ("empresa_orgao", models.TextField(null=True, blank=True)),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                ("dias", models.SmallIntegerField(default=0)),
            ],
            options={
                "ordering": ("servidor",),
                "permissions": (("previd_adm", "Adm Censo Prev"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Circunscricao",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Comarca",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "validacao",
                    models.BooleanField(default=True, verbose_name="Valida\xe7\xe3o"),
                ),
            ],
            options={
                "verbose_name": "Comarca",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Curso",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "grau_instrucao",
                    models.IntegerField(
                        default=1,
                        null=True,
                        verbose_name="Grau de Instru\xe7\xe3o",
                        blank=True,
                        choices=[
                            (1, "ANALFABETO"),
                            (2, "ALFABETIZADO SEM CURSOS REGULARES"),
                            (3, "FUNDAMENTAL INCOMPLETO"),
                            (4, "FUNDAMENTAL COMPLETO"),
                            (5, "M\xc9DIO INCOMPLETO"),
                            (6, "M\xc9DIO COMPLETO"),
                            (7, "SUPERIOR INCOMPLETO"),
                            (8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"),
                            (9, "ESPECIALIZA\xc7\xc3O/P\xd3S-GRADUA\xc7\xc3O"),
                            (10, "MESTRADO"),
                            (11, "DOUTORADO"),
                            (12, "P\xd3S-DOUTORADO"),
                            (13, "T\xc9CNICO"),
                        ],
                    ),
                ),
            ],
            options={
                "verbose_name": "Curso",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DadoBancario",
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
                    "tipo_conta",
                    models.IntegerField(
                        verbose_name="Tipo de Conta",
                        choices=[
                            (1, "CORRENTE"),
                            (2, "POUPAN\xc7A"),
                            (3, "INVESTIMENTO"),
                        ],
                    ),
                ),
                (
                    "agencia",
                    models.CharField(max_length=15, verbose_name="Ag\xeancia com DV"),
                ),
                (
                    "conta_corrente_completa",
                    models.CharField(
                        max_length=15, verbose_name="Conta Corrente com DV"
                    ),
                ),
            ],
            options={
                "ordering": ["banco"],
                "verbose_name": "Dado Banc\xe1rio",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DadoBancarioConsignatario",
            fields=[
                (
                    "dadobancario_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.DadoBancario",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_dadobancariocons",
                "verbose_name": "Dado banc\xe1rio de consignat\xe1rio",
            },
            bases=("rh.dadobancario",),
        ),
        migrations.CreateModel(
            name="DadoBancarioPessoa",
            fields=[
                (
                    "dadobancario_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.DadoBancario",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "principal",
                    models.BooleanField(default=False, verbose_name="Principal"),
                ),
            ],
            options={
                "db_table": "rh_dadobancariopessoa",
                "verbose_name": "Dado banc\xe1rio de pessoa",
            },
            bases=("rh.dadobancario",),
        ),
        migrations.CreateModel(
            name="Dependencia",
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
                    "tipo",
                    models.SmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Imposto de Renda"),
                            (2, "PlanSa\xfade"),
                            (3, "Sal\xe1rio Fam\xedlia"),
                            (4, "Aux\xedlio Creche"),
                            (5, "Previd\xeancia"),
                            (6, "Aux\xedlio Especial"),
                        ],
                    ),
                ),
                ("data_inicio", models.DateField(verbose_name="Data de In\xedcio")),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data de Fim", blank=True),
                ),
                (
                    "idade_limite",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Idade limite", blank=True
                    ),
                ),
                (
                    "estudante",
                    models.BooleanField(default=False, verbose_name="Estudante"),
                ),
                (
                    "suspenso",
                    models.BooleanField(default=False, verbose_name="Suspenso"),
                ),
            ],
            options={
                "db_table": "rh_dependencia",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Dependente",
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
                    "motivo_inicio_dependencia",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Motivo In\xedcio Depend\xeancia",
                        choices=[
                            (0, "OUTROS"),
                            (1, "NASCIMENTO"),
                            (2, "ADO\xc7\xc3O"),
                            (3, "FILHO P\xd3STUMO"),
                            (4, "TUTELA DO MENOR"),
                            (5, "DECIS\xc3O JUDICIAL"),
                            (6, "INVALIDEZ"),
                            (7, "CASAMENTO"),
                            (8, "UNI\xc3O EST\xc1VEL"),
                            (9, "DEPEND\xcaNCIA ECON\xd4MICA"),
                        ],
                    ),
                ),
                (
                    "motivo_fim_dependencia",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Motivo Fim Depend\xeancia",
                        choices=[
                            (0, "OUTROS"),
                            (1, "MAIORIDADE"),
                            (2, "EMANCIPA\xc7\xc3O"),
                            (3, "DECIS\xc3O JUDICIAL"),
                            (4, "\xd3BITO"),
                            (5, "SEPARA\xc7\xc3O JUDICIAL"),
                            (6, "INDEPEND\xcaNCIA ECON\xd4MICA"),
                            (7, "CESSA\xc7\xc3O DE INVALIDEZ"),
                        ],
                    ),
                ),
                (
                    "grau_parentesco",
                    models.IntegerField(
                        verbose_name="Tipo de Parentesco",
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
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data de In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data de Fim", blank=True),
                ),
                (
                    "dep_ir",
                    models.BooleanField(default=False, verbose_name="Imposto de Renda"),
                ),
                (
                    "dep_sf",
                    models.BooleanField(
                        default=False, verbose_name="Sal\xe1rio Fam\xedlia"
                    ),
                ),
                (
                    "dependente_direto",
                    models.BooleanField(
                        default=False, verbose_name="Dependente Direto"
                    ),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                (
                    "auxilio_creche",
                    models.BooleanField(
                        default=False, verbose_name="Recebe Aux\xedlio Creche"
                    ),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                (
                    "tipo",
                    models.IntegerField(
                        null=True,
                        verbose_name="Tipo",
                        choices=[
                            (1, "C\xd4NJUGE"),
                            (2, "COMPANHEIRO(A)"),
                            (3, "FILHO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS"),
                            (4, "FILHO INV\xc1LIDO(A)"),
                            (5, "PAI(M\xc3E) COM DEPEND\xcaNCIA ECON\xd4MICA"),
                            (
                                6,
                                "IRM\xc3O N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                            ),
                            (7, "IRM\xc3O INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA"),
                            (
                                8,
                                "ENTEADO N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                            ),
                            (9, "ENTEADO INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA"),
                            (
                                10,
                                "MENOR TUTELADO N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                            ),
                            (
                                11,
                                "MENOR TUTELADO INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA",
                            ),
                        ],
                    ),
                ),
                (
                    "capacidade",
                    models.IntegerField(
                        default=1,
                        null=True,
                        choices=[(1, "V\xc1LIDO"), (2, "INV\xc1LIDO")],
                    ),
                ),
            ],
            options={
                "verbose_name": "Dependente",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DocsDadosEspecificos",
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
                    "especificidade",
                    models.IntegerField(
                        verbose_name="Especificidade",
                        choices=[
                            (1, "T\xcdTULO DE ELEITOR.ZONA"),
                            (2, "T\xcdTULO DE ELEITOR.SE\xc7\xc3O"),
                            (3, "T\xcdTULO DE ELEITOR.UF"),
                            (7, "T\xcdTULO DE ELEITOR.MUNICIPIO"),
                            (4, "CNH.CATEGORIA"),
                            (5, "RESERVISTA.CLASSE"),
                            (6, "CTPS.SERIE"),
                        ],
                    ),
                ),
                ("valor", models.CharField(max_length=30, verbose_name="Valor")),
            ],
            options={
                "verbose_name": "Documentos de dados espec\xedficos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Documento",
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
                    "tipo_documento",
                    models.IntegerField(
                        verbose_name="Tipo de Documento",
                        choices=[
                            (1, "T\xcdTULO DE ELEITOR"),
                            (2, "CNH"),
                            (3, "CTPS"),
                            (4, "PIS/PASEP"),
                            (5, "NIS"),
                            (7, "IPSEP"),
                            (8, "INSS"),
                            (9, "RESERVISTA"),
                            (10, "CONSELHO PROFISSIONAL"),
                        ],
                    ),
                ),
                ("numero", models.CharField(max_length=30, verbose_name="N\xfamero")),
                (
                    "data_expedicao",
                    models.DateField(
                        null=True, verbose_name="Data da Expedi\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "data_validade",
                    models.DateField(
                        null=True, verbose_name="Data de Validade", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DocumentoDigital",
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
                "verbose_name": "Pessoa",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="EncargoFinanceiro",
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
                    "remuneracao",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "base_previdenciaria",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("data_inicio", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "verbose_name": "Encargo Financeiro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Endereco",
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
                    "tipo_endereco",
                    models.IntegerField(
                        verbose_name="Tipo do Endere\xe7o",
                        choices=[
                            (1, "Residencial"),
                            (2, "Comercial"),
                            (3, "Institucional"),
                            (4, "Profissional"),
                            (5, "Via p\xfablica"),
                            (6, "N\xe3o informado"),
                        ],
                    ),
                ),
                (
                    "tipo_logradouro",
                    models.IntegerField(
                        verbose_name="Tipo do Logradouro",
                        choices=[
                            (8, "RUA"),
                            (9, "QUADRA"),
                            (1, "AVENIDA"),
                            (2, "PRA\xc7A"),
                            (3, "VIELA"),
                            (4, "PONTO"),
                            (5, "VIADUTO"),
                            (6, "ALAMEDA"),
                            (7, "OUTROS"),
                        ],
                    ),
                ),
                ("cep", models.CharField(max_length=10, null=True, verbose_name="CEP")),
                ("logradouro", models.CharField(max_length=100, null=True)),
                (
                    "numero",
                    models.CharField(
                        max_length=12, null=True, verbose_name="N\xfamero", blank=True
                    ),
                ),
                ("bairro", models.CharField(max_length=50, null=True, blank=True)),
                (
                    "complemento",
                    models.CharField(max_length=2000, null=True, blank=True),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
            ],
            options={
                "verbose_name": "Endere\xe7o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Entrancia",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Especialidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("sigla", models.CharField(max_length=3, null=True)),
            ],
            options={
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Estado",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("sigla", models.CharField(max_length=2)),
                (
                    "siafi",
                    models.CharField(
                        max_length=12, null=True, verbose_name="SIAFI", blank=True
                    ),
                ),
                (
                    "tse",
                    models.CharField(
                        max_length=12, null=True, verbose_name="TSE", blank=True
                    ),
                ),
                (
                    "ibge",
                    models.IntegerField(null=True, verbose_name="IBGE", blank=True),
                ),
            ],
            options={
                "ordering": ["nome"],
                "verbose_name": "Estado",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="GrauInstrucao",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("label", models.CharField(max_length=100, null=True)),
                ("ordem", models.IntegerField(null=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="GrupoComarca",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="InativacaoCargoMembro",
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
                ("cargo_arquimedes", models.IntegerField(default=0)),
                ("data_inicio", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "data_prevista",
                    models.DateField(
                        null=True, verbose_name="Data Prevista Fim", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Inativa\xe7\xe3o de Cargo de Membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="InCapacidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Instancia",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Localidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("sigla", models.CharField(max_length=6, null=True, blank=True)),
                ("siafi", models.CharField(max_length=12, null=True, blank=True)),
                (
                    "ibge",
                    models.IntegerField(null=True, verbose_name="IBGE", blank=True),
                ),
                (
                    "valor_vale_transporte",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor vale transporte",
                        max_digits=6,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                ("cep", models.CharField(max_length=9, null=True, blank=True)),
                (
                    "distancia_capital",
                    models.DecimalField(
                        null=True,
                        verbose_name="Dist\xe2ncia Capital",
                        max_digits=6,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "indicador_municipio",
                    models.BooleanField(
                        default=False, verbose_name="Indicador Munic\xedpio"
                    ),
                ),
                ("sede_termo", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Localidade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MesoRegiao",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MicroRegiao",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Micro Regi\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Molestia",
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
                ("data_laudo", models.DateField(verbose_name="Data do laudo")),
            ],
            options={
                "verbose_name": "Pessoa",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MovimentacaoPessoal",
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
                ("texto", models.TextField(null=True, blank=True)),
                (
                    "anota",
                    models.BooleanField(
                        default=True, verbose_name="Gera Anota\xe7\xe3o"
                    ),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
            ],
            options={
                "db_table": "rh_movpessoal",
                "verbose_name": "Movimenta\xe7\xe3o Pessoal",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MovimentacaoEstabilizacao",
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
                (
                    "data_vigencia",
                    models.DateField(
                        null=True,
                        verbose_name="In\xc3\xadcio vig\xc3\xaancia",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "rh_movestabilizacao",
                "verbose_name": "Movimenta\xe7\xe3o de Estabiliza\xe7\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoDesligamento",
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
                (
                    "tipo_desligamento",
                    models.IntegerField(
                        verbose_name="Tipo de Desligamento",
                        choices=[
                            (1, "EXONERA\xc7\xc3O EFETIVO"),
                            (2, "EXONERA\xc7\xc3O COMISSIONADO"),
                            (3, "EXONERA\xc7\xc3O ESTABILIZADO"),
                            (6, "POSSE EM OUTRO CARGO"),
                            (7, "FALECIMENTO"),
                            (8, "RESCIS\xc3O"),
                            (9, "DEMISS\xc3O"),
                            (10, "RESERVA REFORMA"),
                            (11, "DISPONIBILIDADE"),
                            (12, "PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                            (13, "FIM REQUISI\xc7\xc3O/ACORDO COOPERA\xc7\xc3O"),
                            (15, "APOSENTADORIA ESPECIAL"),
                            (16, "APOSENTADORIA POR TEMPO DE CONTRIBUI\xc7\xc3O"),
                            (17, "APOSENTADORIA POR IDADE"),
                        ],
                    ),
                ),
                (
                    "opcao",
                    models.IntegerField(
                        default=2,
                        blank=True,
                        verbose_name="Op\xe7\xe3o",
                        choices=[(1, "A PEDIDO"), (2, "OF\xcdCIO")],
                    ),
                ),
                ("data_desligamento", models.DateField(null=True, blank=True)),
                (
                    "vacancia",
                    models.BooleanField(default=False, verbose_name="Vac\xe2ncia"),
                ),
            ],
            options={
                "db_table": "rh_movdesligamento",
                "verbose_name": "Movimenta\xe7\xe3o de Desligamento",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoAposentadoria",
            fields=[
                (
                    "movimentacaodesligamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoDesligamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tipo_aposentadoria",
                    models.IntegerField(
                        choices=[
                            (1, "COMPULS\xd3RIA"),
                            (2, "ESPECIAL"),
                            (3, "IMPLEMENTO DE IDADE"),
                            (4, "INVALIDEZ"),
                            (5, "TEMPO DE CONTRIBUI\xc7\xc3O"),
                            (6, "VOLUNT\xc1RIA"),
                        ]
                    ),
                ),
                (
                    "reversao",
                    models.IntegerField(
                        default=2,
                        verbose_name="Revers\xe3o",
                        choices=[(1, "SIM"), (2, "N\xc3O")],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("rh.movimentacaodesligamento",),
        ),
        migrations.CreateModel(
            name="MovimentacaoDescontoLegal",
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
                (
                    "desconto",
                    models.IntegerField(
                        choices=[(1, "REPOSI\xc7\xc3O"), (2, "INDENIZA\xc7\xc3O")]
                    ),
                ),
                ("valor", models.DecimalField(max_digits=16, decimal_places=2)),
                ("parcela", models.IntegerField()),
            ],
            options={
                "db_table": "rh_movdesclegal",
                "verbose_name": "Movimenta\xe7\xe3o de Desconto Legal",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoConcessao",
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
            ],
            options={
                "db_table": "rh_movconcessao",
                "verbose_name": "Movimenta\xe7\xe3o de Concess\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="DeclaracaoAtividade",
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
                ("data_exercicio", models.DateField(verbose_name="Exerc\xedcio")),
                ("data_encerramento", models.DateField(null=True, blank=True)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "turno",
                    models.IntegerField(
                        null=True,
                        choices=[
                            (1, "MATUTINO"),
                            (2, "VESPERTINO"),
                            (3, "NOTURNO"),
                            (4, "DIA INTEIRO"),
                        ],
                    ),
                ),
            ],
            options={
                "verbose_name": "Declara\xe7\xe3o de Atividade",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoPosse",
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
                (
                    "data_posse",
                    models.DateField(null=True, verbose_name="Data Posse", blank=True),
                ),
                (
                    "data_exercicio",
                    models.DateField(
                        null=True, verbose_name="Data Exerc\xedcio", blank=True
                    ),
                ),
                (
                    "data_desligamento",
                    models.DateField(
                        null=True, verbose_name="Data Desligamento", blank=True
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
                (
                    "tipo_movcarreira",
                    models.CharField(
                        default="NOMEACAO",
                        max_length=30,
                        verbose_name="Provimento",
                        choices=[
                            ("PREGRESSAO", "Progress\xe3o"),
                            ("TITULARIZACAO", "Titulariza\xe7\xe3o"),
                            ("REVERSAO", "Revers\xe3o"),
                            ("READAPTACAO", "Readapta\xe7\xe3o"),
                            ("NOMEACAO", "Nomea\xe7\xe3o"),
                            ("PROMOCAO", "Promo\xe7\xe3o"),
                            ("APROVEITAMENTO", "Aproveitamento"),
                            ("REMOCAO", "Remo\xe7\xe3o"),
                            ("RECONDUCAO", "Recondu\xe7\xe3o"),
                            ("REINTEGRACAO", "Reintegra\xe7\xe3o"),
                            ("ENQUADRAMENTO", "Enquadramento"),
                        ],
                    ),
                ),
                (
                    "bond",
                    models.BooleanField(default=True, verbose_name="Gerar v\xednculo"),
                ),
            ],
            options={
                "db_table": "rh_movposse",
                "verbose_name": "Movimenta\xe7\xe3o de Posse",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoAproveitamento",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movaproveitamento",
                "verbose_name": "Movimenta\xe7\xe3o de Aprovietamento",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoPromocao",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "criterio",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, "ANTIGUIDADE"),
                            (2, "MERECIMENTO"),
                            (3, "PERMUTA"),
                        ],
                    ),
                ),
            ],
            options={
                "db_table": "rh_movpromocao",
                "verbose_name": "Movimenta\xe7\xe3o de Promo\xe7\xe3o",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoReadaptacao",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movreadaptacao",
                "verbose_name": "Movimenta\xe7\xe3o de Readapta\xe7\xe3o",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoReconducao",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movreconducao",
                "verbose_name": "Movimenta\xe7\xe3o de Recondu\xe7\xe3o",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoRedistribuicao",
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
                (
                    "redistribuicao",
                    models.IntegerField(
                        verbose_name="Redistribui\xe7\xe3o",
                        choices=[
                            (1, "OF\xcdCIO"),
                            (2, "DISPONIBILIDADE"),
                            (3, "DISPONIBILIDADE PROVIS\xd3RIA"),
                        ],
                    ),
                ),
            ],
            options={
                "db_table": "rh_movredistribuicao",
                "verbose_name": "Movimenta\xe7\xe3o de Redistribui\xe7\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoReintegracao",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movreintegracao",
                "verbose_name": "Movimenta\xe7\xe3o de Reintegra\xe7\xe3o",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoRemocao",
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
                (
                    "remocao",
                    models.IntegerField(
                        verbose_name="Remo\xe7\xe3o",
                        choices=[(1, "OF\xcdCIO"), (2, "REQUERIMENTO"), (3, "PERMUTA")],
                    ),
                ),
                ("data_vigencia", models.DateField(null=True)),
            ],
            options={
                "db_table": "rh_movremocao",
                "verbose_name": "Movimenta\xe7\xe3o de Remo\xe7\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoRemocaoMembro",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "criterio",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, "ANTIGUIDADE"),
                            (2, "MERECIMENTO"),
                            (3, "PERMUTA"),
                        ],
                    ),
                ),
            ],
            options={
                "db_table": "rh_movremocaomembro",
                "verbose_name": "Movimenta\xe7\xe3o de Remo\xe7\xe3o de Membro",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoRequisicao",
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
                (
                    "onus",
                    models.IntegerField(
                        default=2,
                        verbose_name="\xd4nus",
                        choices=[(1, "ORIGEM"), (2, "REQUISITANTE")],
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_movrequisicao",
                "verbose_name": "Movimenta\xe7\xe3o de Requisi\xe7\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoReversao",
            fields=[
                (
                    "movimentacaoposse_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPosse",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movreversao",
                "verbose_name": "Movimenta\xe7\xe3o de Revers\xe3o",
            },
            bases=("rh.movimentacaoposse",),
        ),
        migrations.CreateModel(
            name="MovimentacaoSubstituicao",
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
                ("data_inicio", models.DateField(verbose_name="In\xedcio")),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "data_prevista",
                    models.DateField(
                        null=True, verbose_name="Data Prevista Fim", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "rh_movsubstituicao",
                "verbose_name": "Movimenta\xe7\xe3o de Substitui\xe7\xe3o",
            },
            bases=("rh.movimentacaopessoal",),
        ),
        migrations.CreateModel(
            name="MovimentacaoSubstituicaoMembro",
            fields=[
                (
                    "movimentacaosubstituicao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoSubstituicao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("cargo_arquimedes", models.IntegerField(default=0)),
            ],
            options={
                "db_table": "rh_movsubsmembro",
                "verbose_name": "Movimenta\xe7\xe3o Substitui\xe7\xe3o Membro",
            },
            bases=("rh.movimentacaosubstituicao",),
        ),
        migrations.CreateModel(
            name="MovimentacaoTitularizacao",
            fields=[
                (
                    "movimentacaopromocao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.MovimentacaoPromocao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "rh_movtitularizacao",
                "verbose_name": "Movimenta\xe7\xe3o de Titulariza\xe7\xe3o",
            },
            bases=("rh.movimentacaopromocao",),
        ),
        migrations.CreateModel(
            name="Mpas",
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
                ("codigo", models.IntegerField(verbose_name="C\xf3digo")),
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
            name="NecessidadeEspecial",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
            name="OrgaoGeral",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "abreviacao",
                    models.CharField(
                        max_length=60,
                        null=True,
                        verbose_name="Abrevia\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "esfera_governamental",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[(1, "FEDERAL"), (2, "ESTADUAL"), (3, "MUNICIPAL")],
                    ),
                ),
                (
                    "poder",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "EXECUTIVO"),
                            (2, "LEGISLATIVO"),
                            (3, "JUDICI\xc1RIO"),
                            (4, "MINIST\xc9RIO P\xdaBLICO"),
                            (5, "DESCONHECIDO"),
                            (6, "TRIBUNAL DE CONTAS"),
                        ],
                    ),
                ),
                ("sigla", models.CharField(max_length=10, null=True, blank=True)),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "codigo_igeprev",
                    models.IntegerField(
                        null=True, verbose_name="C\xf3digo igeprev", blank=True
                    ),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                (
                    "publica_doc",
                    models.BooleanField(default=False, verbose_name="Publica"),
                ),
                ("habilita_protocolo", models.BooleanField(default=False)),
                ("order_nome", models.SlugField(max_length=100, null=True, blank=True)),
            ],
            options={
                "ordering": ["nome"],
                "verbose_name": "\xd3rg\xe3o Geral",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Lotacao",
            fields=[
                (
                    "orgaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.OrgaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("andar", models.CharField(max_length=3, null=True, blank=True)),
                ("sala", models.CharField(max_length=6, null=True, blank=True)),
                (
                    "codigo",
                    models.CharField(
                        max_length=15, null=True, verbose_name="C\xf3digo", blank=True
                    ),
                ),
                (
                    "executivo",
                    models.BooleanField(default=False, verbose_name="Executivo"),
                ),
                (
                    "administrativo",
                    models.BooleanField(default=False, verbose_name="Administrativo"),
                ),
                (
                    "grupo_lotacao",
                    models.BooleanField(
                        default=False, verbose_name="Grupo de Lota\xe7\xf5es"
                    ),
                ),
                (
                    "acesso_protocolo_geral",
                    models.BooleanField(
                        default=False, verbose_name="Ver todos Protocolos"
                    ),
                ),
                ("organograma", models.BooleanField(default=False)),
                ("designacao", models.BooleanField(default=False)),
                ("ouvidoria", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["nome"],
                "verbose_name": "Lota\xe7\xe3o",
            },
            bases=("rh.orgaogeral",),
        ),
        migrations.CreateModel(
            name="Pais",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("ddi", models.CharField(max_length=12, null=True, verbose_name="DDI")),
                ("nome_completo", models.CharField(max_length=100, null=True)),
                (
                    "nacionalidade",
                    models.CharField(max_length=100, null=True, blank=True),
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
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Patrocinador",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
            name="Penalidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
            name="PeriodoRequisicao",
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
                    "data_inicio",
                    models.DateField(verbose_name="Data In\xedcio", blank=True),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "anotacao_geral",
                    models.ForeignKey(
                        related_name="periodo_requisicao",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="Anota\xe7\xe3o Geral",
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
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
                "verbose_name": "Per\xedodo de requisi\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Pessoa",
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
                ("nome", models.CharField(max_length=100, verbose_name="Nome")),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "Pessoa",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PessoaFisica",
            fields=[
                (
                    "pessoa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cpf",
                    models.CharField(
                        max_length=14, null=True, verbose_name="CPF", blank=True
                    ),
                ),
                (
                    "rg",
                    models.CharField(
                        max_length=20, null=True, verbose_name="RG", blank=True
                    ),
                ),
                (
                    "sexo",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[("M", "MASCULINO"), ("F", "FEMININO")],
                    ),
                ),
                (
                    "sangue",
                    models.IntegerField(
                        default=4,
                        blank=True,
                        choices=[(4, "A"), (1, "B"), (2, "AB"), (3, "O")],
                    ),
                ),
                (
                    "estado_civil",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, "SOLTEIRO"),
                            (2, "CASADO"),
                            (3, "VIUVO"),
                            (4, "SEPARADO JUDICIALMENTE"),
                            (5, "DIVORCIADO"),
                            (6, "UNIAO ESTAVEL"),
                            (7, "N\xc3O FOI DEFINIDO NO CADASTRO"),
                        ],
                    ),
                ),
                (
                    "raca_cor",
                    models.IntegerField(
                        default=6,
                        verbose_name="Ra\xe7a/Cor",
                        choices=[
                            (6, "BRANCA"),
                            (1, "PARDA"),
                            (2, "AMARELA"),
                            (3, "NEGRA"),
                            (4, "IND\xcdGENA"),
                            (5, "N\xc3O INFORMADO"),
                        ],
                    ),
                ),
                (
                    "email_pessoal",
                    models.EmailField(max_length=75, null=True, blank=True),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True, null=True)),
                ("data_nascimento", models.DateField(null=True, blank=True)),
                (
                    "data_obito",
                    models.DateField(
                        null=True, verbose_name="Data \xd3bito", blank=True
                    ),
                ),
                (
                    "rg_orgao",
                    models.CharField(
                        max_length=10,
                        null=True,
                        verbose_name="RG \xd3rg\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "rg_data_expedicao",
                    models.DateField(
                        null=True, verbose_name="RG Data Expedi\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "fator_rh",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Fator RH",
                        blank=True,
                        choices=[(2, "+"), (1, "-")],
                    ),
                ),
                (
                    "doador",
                    models.BooleanField(
                        default=True, verbose_name="Doador de \xf3rg\xe3os"
                    ),
                ),
                (
                    "nome_pai",
                    models.CharField(
                        max_length=80, null=True, verbose_name="Nome Pai", blank=True
                    ),
                ),
                (
                    "nome_mae",
                    models.CharField(
                        max_length=80, null=True, verbose_name="Nome M\xe3e", blank=True
                    ),
                ),
                (
                    "nome_conjuge",
                    models.CharField(
                        max_length=80,
                        null=True,
                        verbose_name="Nome C\xf4njuge",
                        blank=True,
                    ),
                ),
                (
                    "necessidade_especial",
                    models.BooleanField(
                        default=False, verbose_name="Necessidade Especial"
                    ),
                ),
                (
                    "grau_instrucao",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Grau de Instru\xe7\xe3o",
                        choices=[
                            (1, "ANALFABETO"),
                            (2, "ALFABETIZADO SEM CURSOS REGULARES"),
                            (3, "FUNDAMENTAL INCOMPLETO"),
                            (4, "FUNDAMENTAL COMPLETO"),
                            (5, "M\xc9DIO INCOMPLETO"),
                            (6, "M\xc9DIO COMPLETO"),
                            (7, "SUPERIOR INCOMPLETO"),
                            (8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"),
                            (9, "ESPECIALIZA\xc7\xc3O/P\xd3S-GRADUA\xc7\xc3O"),
                            (10, "MESTRADO"),
                            (11, "DOUTORADO"),
                            (12, "P\xd3S-DOUTORADO"),
                            (13, "T\xc9CNICO"),
                        ],
                    ),
                ),
                (
                    "documento",
                    models.ManyToManyField(to="rh.Documento", null=True, blank=True),
                ),
                (
                    "foto",
                    models.ForeignKey(
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "municipio_naturalidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "necessidades_especiais",
                    models.ManyToManyField(
                        related_name="pessoafisica",
                        null=True,
                        to="rh.NecessidadeEspecial",
                        blank=True,
                    ),
                ),
                (
                    "rg_uf",
                    models.ForeignKey(
                        verbose_name="RG UF",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("nome", "cpf"),
                "verbose_name": "Pessoa F\xedsica",
            },
            bases=("rh.pessoa",),
        ),
        migrations.CreateModel(
            name="PessoaJuridica",
            fields=[
                (
                    "pessoa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("cnpj", models.CharField(max_length=14)),
                (
                    "razao_social",
                    models.CharField(max_length=255, verbose_name="Raz\xe3o Social"),
                ),
            ],
            options={
                "ordering": ("nome", "cnpj"),
                "verbose_name": "Pessoa Jur\xeddica",
            },
            bases=("rh.pessoa",),
        ),
        migrations.CreateModel(
            name="ProfissionalSaude",
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
                    "conselho_regional",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="Conselho regional",
                        blank=True,
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
                    "pessoa_fisica",
                    models.ForeignKey(
                        related_name="profissionalsaude",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Pessoa",
                        to="rh.PessoaFisica",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Prorrogacao",
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
                    "data_inicio",
                    models.DateField(verbose_name="Data In\xedcio", blank=True),
                ),
                ("data_fim", models.DateField(verbose_name="Data Fim", blank=True)),
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
                "db_table": "rh_prorrogacao",
                "verbose_name": "Prorroga\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Publicacao",
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
                    "publication_state",
                    models.SmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Em Aberto"),
                            (2, "P\xc3\xbablica\xc3\xa7\xc3\xa3o Solicitada"),
                            (3, "P\xc3\xbablica\xc3\xa7\xc3\xa3o Realizada"),
                            (4, "P\xc3\xbablica\xc3\xa7\xc3\xa3o Cancelada"),
                        ],
                    ),
                ),
                ("indirect", models.BooleanField(default=False)),
                ("document", models.TextField(null=True)),
                ("document_read_only", models.BooleanField(default=False)),
                ("sent_to_publication_at", models.DateTimeField(null=True)),
                ("confirm_publication_at", models.DateTimeField(null=True)),
                ("vehicle_page", models.SmallIntegerField(null=True)),
                (
                    "tipo",
                    models.IntegerField(
                        verbose_name="Tipo de Publica\xe7\xe3o",
                        choices=[
                            (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                            (12, "APOSTILA"),
                            (1, "ATO"),
                            (16, "CIRCULAR"),
                            (9, "CONCESS\xc3O"),
                            (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                            (2, "DECRETO"),
                            (14, "DECRETO LEGISLATIVO"),
                            (5, "DESPACHO"),
                            (100, "DOCUMENTO DIGITAL"),
                            (11, "LEI"),
                            (7, "MEMORANDO"),
                            (4, "OF\xcdCIO"),
                            (99, "OUTROS"),
                            (3, "PORTARIA"),
                            (17, "PROCESSO"),
                            (8, "REQUERIMENTO"),
                            (15, "RESOLU\xc7\xc3O"),
                            (6, "TERMO"),
                            (97, "TERMO EXERC\xcdCIO"),
                            (96, "TERMO LOTA\xc7\xc3O"),
                            (98, "TERMO POSSE"),
                        ],
                    ),
                ),
                (
                    "numero",
                    models.CharField(
                        max_length=20, null=True, verbose_name="N\xfamero", blank=True
                    ),
                ),
                ("ano", models.CharField(max_length=4, verbose_name="Ano", blank=True)),
                (
                    "data_expedicao",
                    models.DateField(null=True, verbose_name="Data da Expedi\xe7\xe3o"),
                ),
                ("lei_autorizativa", models.BooleanField(default=False)),
                (
                    "veiculo_publicacao",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Ve\xedculo Publica\xe7\xe3o",
                        choices=[
                            (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                            (30, "DIARIO OFICIAL DA UNIAO"),
                            (28, "DIARIO JUSTICA"),
                            (29, "DIARIO JUSTICA ELEITORAL"),
                            (1, "DOE ACRE"),
                            (2, "DOE AMAPA"),
                            (3, "DOE AMAZONAS"),
                            (13, "DOE BAHIA"),
                            (8, "DOE CEARA"),
                            (26, "DOE DISTRITO FEDERAL"),
                            (18, "DOE ESPIRITO SANTO"),
                            (25, "DOE GOIAS"),
                            (6, "DOE PARA"),
                            (21, "DOE PARANA"),
                            (11, "DOE PARAIBA"),
                            (10, "DOE PERNAMBUCO"),
                            (15, "DOE PIAUI"),
                            (27, "DOE MATO GROSSO"),
                            (24, "DOE MATO GROSSO DO SUL"),
                            (14, "DOE MARANHAO"),
                            (16, "DOE MINAS GERAIS"),
                            (19, "DOE RIO DE JANEIRO"),
                            (9, "DOE RIO GRANDE DO NORTE"),
                            (23, "DOE RIO GRANDE DO SUL"),
                            (4, "DOE RORAIMA"),
                            (5, "DOE RONDONIA"),
                            (22, "DOE SANTA CATARINA"),
                            (17, "DOE SAO PAULO"),
                            (12, "DOE SERGIPE"),
                            (7, "DOE TOCANTINS"),
                            (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                            (33, "PLACAR"),
                        ],
                    ),
                ),
                (
                    "numero_publicacao",
                    models.CharField(
                        max_length=22,
                        null=True,
                        verbose_name="N\xfamero Publica\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "data_publicacao",
                    models.DateField(
                        null=True, verbose_name="Data da Publica\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "data_vigencia",
                    models.DateField(null=True, verbose_name="Data da Vig\xeancia"),
                ),
                (
                    "observacao",
                    models.CharField(
                        max_length=300,
                        null=True,
                        verbose_name="Observa\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("interno", models.BooleanField(default=False)),
                (
                    "interessado_nome",
                    models.CharField(
                        max_length=200,
                        null=True,
                        verbose_name="Interessado",
                        blank=True,
                    ),
                ),
                (
                    "cache_unicode",
                    models.CharField(
                        max_length=200, null=True, verbose_name="Cache", blank=True
                    ),
                ),
                (
                    "arquivo",
                    models.ForeignKey(
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "confirm_publication_by",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
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
            ],
            options={
                "ordering": ["-data_expedicao", "origem", "numero"],
                "verbose_name": "Publica\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PublicConcurrence",
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
                    "number_mpe",
                    models.CharField(max_length=4, verbose_name="N\xfamero"),
                ),
                ("year_mpe", models.CharField(max_length=4, verbose_name="Ano")),
                (
                    "number_tce",
                    models.CharField(
                        max_length=20, null=True, verbose_name="N\xfamero", blank=True
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Nome")),
                ("resume", models.TextField(null=True, blank=True)),
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
                "ordering": ("number_mpe", "year_mpe"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Quadro",
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
                    "cargo",
                    models.ForeignKey(to="rh.Cargo", on_delete=models.CASCADE),
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
                    "especialidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Especialidade",
                        null=True,
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
                "ordering": ("cargo", "especialidade"),
                "verbose_name": "Quadro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RacaCor",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
                "ordering": ["nome"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Servidor",
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
                    "matricula",
                    models.IntegerField(
                        help_text="Apenas n\xfameros",
                        unique=True,
                        verbose_name="Matr\xedcula",
                    ),
                ),
                (
                    "matricula_origem",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="Matr\xedcula de Origem",
                        blank=True,
                    ),
                ),
                (
                    "numero_cartao_ponto",
                    models.IntegerField(
                        null=True, verbose_name="N\xb0 Cart\xe3o de Ponto", blank=True
                    ),
                ),
                (
                    "classificacao",
                    models.IntegerField(
                        null=True, verbose_name="Classifica\xe7\xe3o", blank=True
                    ),
                ),
                ("data_registro", models.DateField(auto_now_add=True, null=True)),
                (
                    "vpi",
                    models.DecimalField(
                        default=0, max_digits=18, decimal_places=2, blank=True
                    ),
                ),
                ("data_referencia_ferias", models.DateField(null=True, blank=True)),
                (
                    "tipo",
                    models.CharField(
                        default="S",
                        max_length=1,
                        blank=True,
                        choices=[
                            ("I", "INDEFINIDO"),
                            ("E", "ESTAGI\xc1RIO"),
                            ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                            ("P", "MILITAR"),
                            ("S", "SERVIDOR"),
                        ],
                    ),
                ),
                ("ativo", models.BooleanField(default=False)),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                (
                    "situacao_funcional_cache",
                    models.CharField(
                        default="NOT_FOUND",
                        max_length=40,
                        choices=[
                            ("ATIVO_FOLGA_ELEITORAL", "Ativo: Fruindo Folga Eleitoral"),
                            (
                                "ATIVO_AFA_OUT_ORG_ONUS_MP",
                                "Ativo: Afastado - Servir a outro \xd3rg\xe3o com \xf4nus para o MP",
                            ),
                            (
                                "INATIVO_DEVOLVIDO",
                                "Inativo: Devolvido ao \xd3rg\xe3o de Origem",
                            ),
                            ("ATIVO_AFA_PRISAO", "Ativo: Afastado - Pris\xe3o"),
                            (
                                "INATIVO_OUTRO_CARGO",
                                "Inativo: Posse em outro cargo inacumul\xe1vel",
                            ),
                            (
                                "ATIVO_AFA_ESTUDAR",
                                "Ativo: Afastado - Estudar no Pa\xeds/Exterior",
                            ),
                            (
                                "ATIVO_LIC_SAUDE",
                                "Ativo: Licenciado - Tratamento de Sa\xfade",
                            ),
                            ("ATIVO_AFA_SUSPENSAO", "Ativo: Afastado - Suspens\xe3o"),
                            ("ATIVO_AUS_FALECIMENTO", "Ativo: Ausente - Falecimento"),
                            (
                                "ATIVO_AFA_CURSO_CONCURSO",
                                "Ativo: Afastado - Curso de forma\xe7\xe3o de etapa de concurso p\xfablico",
                            ),
                            (
                                "ATIVO_AFA_MISSAO",
                                "Ativo: Afastado - Miss\xe3o Oficial no Exterior",
                            ),
                            (
                                "ATIVO_ATUACAO_GRUPO_TRAB",
                                "Ativo: Atua\xe7\xe3o em Grupo de Trabalho",
                            ),
                            (
                                "ATIVO_AFA_ELETIVO",
                                "Ativo: Afastado - Exerc\xedcio de Mandato Eletivo",
                            ),
                            ("ATIVO_FERIAS", "Ativo: Fruindo F\xe9rias"),
                            (
                                "ATIVO_LIC_DOENCA",
                                "Ativo: Licenciado - Doen\xe7a em Pessoa da Fam\xedlia",
                            ),
                            (
                                "ATIVO_LIC_AFAST_CONJUGE",
                                "Ativo: Licenciado - Afastamento do Conjuge/Companheiro",
                            ),
                            ("ATIVO_RECESSO", "Ativo: Fruindo Recesso"),
                            (
                                "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
                                "Ativo: Afastado - Servir a outro \xd3rg\xe3o sem \xf4nus para o MP",
                            ),
                            (
                                "ATIVO_AUS_SANGUE",
                                "Ativo: Ausente - Doa\xe7\xe3o de sangue",
                            ),
                            ("ATIVO_VIAGEM", "Ativo: Viagem a Servi\xe7o"),
                            (
                                "ATIVO_AUS_ELEITOR",
                                "Ativo: Ausente - Alistamento como eleitor",
                            ),
                            ("INATIVO_APO_IDADE", "Inativo: Aposentado - Por idade"),
                            ("ATIVO_AUS_CASAMENTO", "Ativo: Ausente - Casamento"),
                            ("INATIVO_DEMITIDO", "Inativo: Demitido"),
                            (
                                "ATIVO_LIC_INTERESSE",
                                "Ativo: Licenciado - Tratar de Interesse Particular",
                            ),
                            ("INATIVO_FALECIDO", "Inativo: Falecido"),
                            (
                                "ATIVO_AFA_JURI",
                                "Ativo: Afastado - Servir no Tribunal do Juri",
                            ),
                            (
                                "INATIVO_APO_VOLUNTARIO",
                                "Inativo: Aposentado - Volunt\xe1rio",
                            ),
                            (
                                "ATIVO_LIC_CAPACITACAO",
                                "Ativo: Licenciado - Capacita\xe7\xe3o ou Especializa\xe7\xe3o (3 meses por quinqu\xeanio)",
                            ),
                            (
                                "ATIVO_FOLGA_COMPENSACAO",
                                "Ativo: Fruindo Folga Compensa\xe7\xe3o",
                            ),
                            ("ATIVO", "Ativo: Em atividade"),
                            (
                                "ATIVO_AFA_DESLOCAMENTO",
                                "Ativo: Afastado - Deslocamento at\xe9 a nova sede",
                            ),
                            (
                                "ATIVO_AUS_CONCLUSAO",
                                "Ativo: Ausente - Finaliza\xe7\xe3o de trabalho de conclus\xe3o de curso",
                            ),
                            (
                                "ATIVO_AFA_TREINAMENTO",
                                "Ativo: Afastado - Treinamento (Palestras/Congressos/Semin\xe1rios/Outros)",
                            ),
                            (
                                "ATIVO_LIC_POLITICA",
                                "Ativo: Licenciado - Atividade Pol\xedtica",
                            ),
                            (
                                "ATIVO_AFA_COMPETICAO",
                                "Ativo: Afastado - Competi\xe7\xe3o desportiva ou representa\xe7\xe3o cultural",
                            ),
                            (
                                "ATIVO_LIC_ADOCAO",
                                "Ativo: Licenciado - Tutoria ou Ado\xe7\xe3o",
                            ),
                            (
                                "ATIVO_DESEMPENHO_FUNCAO",
                                "Ativo: Desempenho de Fun\xe7\xe3o",
                            ),
                            (
                                "ATIVO_AFA_ELEITORAL",
                                "Ativo: Afastado - Convoca\xe7\xe3o da Justi\xe7a Eleitoral",
                            ),
                            (
                                "INATIVO_APO_COMPULSORIO",
                                "Inativo: Aposentado - Compuls\xf3rio",
                            ),
                            (
                                "ATIVO_LIC_MATERNIDADE",
                                "Ativo: Licenciado - Maternidade",
                            ),
                            (
                                "ATIVO_LIC_MILITAR",
                                "Ativo: Licenciado - Servi\xe7o Militar",
                            ),
                            (
                                "INATIVO_APO_INVALIDEZ",
                                "Inativo: Aposentado - Por invalidez",
                            ),
                            ("NOT_FOUND", "N\xe3o encontrado"),
                            ("INATIVO_APO_ESPECIAL", "Inativo: Aposentado - Especial"),
                            (
                                "ATIVO_AFA_COMPJUIZO",
                                "Ativo: Afastado - Comparecer a ju\xedzo",
                            ),
                            (
                                "INATIVO_APO_TEMPO_CONTRIBUICAO",
                                "Inativo: Aposentado - Por tempo de contribui\xe7\xe3o",
                            ),
                            (
                                "ATIVO_DISPONIBILIDADE",
                                "Ativo: - Em disponibilidade(com onus para origem ou para requisitante?)",
                            ),
                            (
                                "INATIVO_EXONERADO_OFICIO",
                                "Inativo: Exonerado - De of\xedcio",
                            ),
                            ("ATIVO_PLANTAO", "Ativo: Fruindo Plant\xe3o de Feriado"),
                            (
                                "ATIVO_LIC_CLASSISTA",
                                "Ativo: Licenciado - Desempenho de Mandato Classista",
                            ),
                            (
                                "ATIVO_FOLGA_ANIVERSARIO",
                                "Ativo: Fruindo Folga Anivers\xe1rio",
                            ),
                            (
                                "ATIVO_AUS_NASCIMENTO",
                                "Ativo: Ausente - Nascimento/ado\xe7\xe3o de filho",
                            ),
                            (
                                "INATIVO_EXONERADO_PEDIDO",
                                "Inativo: Exonerado - A pedido",
                            ),
                        ],
                    ),
                ),
                (
                    "categoria_cache",
                    models.CharField(
                        default="SERVIDOR_QUADRO",
                        max_length=40,
                        choices=[
                            (
                                "MEMBRO_1ENT",
                                "Membro - Promotor de Justi\xe7a 1\xaa Entr\xe2ncia",
                            ),
                            (
                                "MEMBRO_3ENT",
                                "Membro - Promotor de Justi\xe7a 3\xaa Entr\xe2ncia",
                            ),
                            ("SERVIDOR_EXTRAQUADRO", "Servidor - Extraquadro"),
                            (
                                "SERVIDOR_EXTRA_REQUISITADO_AC_ONUS",
                                "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica com \xf4nus",
                            ),
                            (
                                "SERVIDOR_EXTRA_REQUISITADO_ONUS",
                                "Servidor - Extraquadro requisitado com \xf4nus",
                            ),
                            (
                                "MEMBRO_2ENT",
                                "Membro - Promotor de Justi\xe7a 2\xaa Entr\xe2ncia",
                            ),
                            ("MEMBRO", "Membro"),
                            ("MEMBRO_PROCURADOR", "Membro - Procurador de Justi\xe7a"),
                            (
                                "MEMBRO_SUBS",
                                "Membro - Promotor de Justi\xe7a Substituto",
                            ),
                            (
                                "SERVIDOR_EXTRA_REQUISITADO_AC",
                                "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica sem \xf4nus",
                            ),
                            ("SERVIDOR_QUADRO", "Servidor - Quadro"),
                            ("ESTAGIARIO", "Estagi\xe1rio"),
                            (
                                "SERVIDOR_EXTRA_REQUISITADO",
                                "Servidor - Extraquadro requisitado",
                            ),
                        ],
                    ),
                ),
                (
                    "regime_previdenciario",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Regime previdenci\xc3\xa1rio",
                        choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
                    ),
                ),
                (
                    "bond",
                    models.BooleanField(default=False, verbose_name="Cria V\xednculo?"),
                ),
                (
                    "capacidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Capacidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "chefe_imediato",
                    models.ForeignKey(
                        related_name="subordinados",
                        verbose_name="Chefe imediato",
                        blank=True,
                        to="rh.Servidor",
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
                ("curso", models.ManyToManyField(to="rh.Curso", null=True, blank=True)),
                (
                    "documento_digital",
                    models.ManyToManyField(
                        related_name="servidor",
                        null=True,
                        verbose_name="Documentos digitais",
                        to="rh.DocumentoDigital",
                        blank=True,
                    ),
                ),
                (
                    "incapacidade",
                    models.ForeignKey(
                        blank=True,
                        to="rh.InCapacidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("pessoa_fisica__nome", "pessoa_fisica__cpf", "matricula"),
                "verbose_name": "Servidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ServidorLocalizacao",
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
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                ("conferido", models.BooleanField(default=False)),
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
                    "localizacao",
                    models.ForeignKey(
                        related_name="servidor_localizacao",
                        verbose_name="Localiza\xe7\xe3o",
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
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
                    "servidor",
                    models.ForeignKey(
                        related_name="servidor_localizacao",
                        verbose_name="Servidor",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Localiza\xe7\xe3o do servidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ServidorLotacao",
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
                ("ativo", models.BooleanField(default=True)),
                (
                    "designacao",
                    models.BooleanField(default=False, verbose_name="Designa\xe7\xe3o"),
                ),
                (
                    "provisorio",
                    models.BooleanField(
                        default=False, verbose_name="Lota\xe7\xe3o Provis\xf3ria"
                    ),
                ),
                (
                    "data_vigencia",
                    models.DateField(null=True, verbose_name="Data Vig\xeancia"),
                ),
                (
                    "data_vigencia_inicio",
                    models.DateField(
                        null=True, verbose_name="Data Vig\xeancia In\xedcio"
                    ),
                ),
                (
                    "data_vigencia_fim",
                    models.DateField(
                        null=True, verbose_name="Data Vig\xeancia Fim", blank=True
                    ),
                ),
                ("data_cadastro", models.DateField(auto_now_add=True)),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                (
                    "anotacao_geral_lotacao",
                    models.ForeignKey(
                        blank=True,
                        to="rh.AnotacaoGeral",
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
                    "lotacao",
                    models.ForeignKey(
                        related_name="servidores_lotacao",
                        verbose_name="Lota\xe7\xe3o/Designa\xe7\xe3o",
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
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
                    "movimentacao_posse",
                    models.ForeignKey(
                        related_name="lotacoes",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="rh.MovimentacaoPosse",
                        null=True,
                    ),
                ),
                (
                    "publicacao",
                    models.ForeignKey(
                        blank=True,
                        to="rh.Publicacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "servidor",
                    models.ForeignKey(
                        related_name="servidor_lotacao",
                        verbose_name="Servidor",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Lota\xe7\xe3o do servidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ServidorVinculo",
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
                    "vinculo",
                    models.IntegerField(
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
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
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
                    "servidor",
                    models.ForeignKey(
                        related_name="servidor_vinculo",
                        verbose_name="Servidor",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "servidor_vinculado",
                    models.ForeignKey(
                        related_name="servidor_vinculado",
                        verbose_name="Servidor vinculado",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Vinculo do Servidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SituacaoFuncional",
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
                    "situacao",
                    models.CharField(
                        default="ATIVO",
                        max_length=30,
                        choices=[
                            ("ATIVO_FOLGA_ELEITORAL", "Ativo: Fruindo Folga Eleitoral"),
                            (
                                "ATIVO_AFA_OUT_ORG_ONUS_MP",
                                "Ativo: Afastado - Servir a outro \xd3rg\xe3o com \xf4nus para o MP",
                            ),
                            (
                                "INATIVO_DEVOLVIDO",
                                "Inativo: Devolvido ao \xd3rg\xe3o de Origem",
                            ),
                            ("ATIVO_AFA_PRISAO", "Ativo: Afastado - Pris\xe3o"),
                            (
                                "INATIVO_OUTRO_CARGO",
                                "Inativo: Posse em outro cargo inacumul\xe1vel",
                            ),
                            (
                                "ATIVO_AFA_ESTUDAR",
                                "Ativo: Afastado - Estudar no Pa\xeds/Exterior",
                            ),
                            (
                                "ATIVO_LIC_SAUDE",
                                "Ativo: Licenciado - Tratamento de Sa\xfade",
                            ),
                            ("ATIVO_AFA_SUSPENSAO", "Ativo: Afastado - Suspens\xe3o"),
                            ("ATIVO_AUS_FALECIMENTO", "Ativo: Ausente - Falecimento"),
                            (
                                "ATIVO_AFA_CURSO_CONCURSO",
                                "Ativo: Afastado - Curso de forma\xe7\xe3o de etapa de concurso p\xfablico",
                            ),
                            (
                                "ATIVO_AFA_MISSAO",
                                "Ativo: Afastado - Miss\xe3o Oficial no Exterior",
                            ),
                            (
                                "ATIVO_ATUACAO_GRUPO_TRAB",
                                "Ativo: Atua\xe7\xe3o em Grupo de Trabalho",
                            ),
                            (
                                "ATIVO_AFA_ELETIVO",
                                "Ativo: Afastado - Exerc\xedcio de Mandato Eletivo",
                            ),
                            ("ATIVO_FERIAS", "Ativo: Fruindo F\xe9rias"),
                            (
                                "ATIVO_LIC_DOENCA",
                                "Ativo: Licenciado - Doen\xe7a em Pessoa da Fam\xedlia",
                            ),
                            (
                                "ATIVO_LIC_AFAST_CONJUGE",
                                "Ativo: Licenciado - Afastamento do Conjuge/Companheiro",
                            ),
                            ("ATIVO_RECESSO", "Ativo: Fruindo Recesso"),
                            (
                                "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
                                "Ativo: Afastado - Servir a outro \xd3rg\xe3o sem \xf4nus para o MP",
                            ),
                            (
                                "ATIVO_AUS_SANGUE",
                                "Ativo: Ausente - Doa\xe7\xe3o de sangue",
                            ),
                            ("ATIVO_VIAGEM", "Ativo: Viagem a Servi\xe7o"),
                            (
                                "ATIVO_AUS_ELEITOR",
                                "Ativo: Ausente - Alistamento como eleitor",
                            ),
                            ("INATIVO_APO_IDADE", "Inativo: Aposentado - Por idade"),
                            ("ATIVO_AUS_CASAMENTO", "Ativo: Ausente - Casamento"),
                            ("INATIVO_DEMITIDO", "Inativo: Demitido"),
                            (
                                "ATIVO_LIC_INTERESSE",
                                "Ativo: Licenciado - Tratar de Interesse Particular",
                            ),
                            ("INATIVO_FALECIDO", "Inativo: Falecido"),
                            (
                                "ATIVO_AFA_JURI",
                                "Ativo: Afastado - Servir no Tribunal do Juri",
                            ),
                            (
                                "INATIVO_APO_VOLUNTARIO",
                                "Inativo: Aposentado - Volunt\xe1rio",
                            ),
                            (
                                "ATIVO_LIC_CAPACITACAO",
                                "Ativo: Licenciado - Capacita\xe7\xe3o ou Especializa\xe7\xe3o (3 meses por quinqu\xeanio)",
                            ),
                            (
                                "ATIVO_FOLGA_COMPENSACAO",
                                "Ativo: Fruindo Folga Compensa\xe7\xe3o",
                            ),
                            ("ATIVO", "Ativo: Em atividade"),
                            (
                                "ATIVO_AFA_DESLOCAMENTO",
                                "Ativo: Afastado - Deslocamento at\xe9 a nova sede",
                            ),
                            (
                                "ATIVO_AUS_CONCLUSAO",
                                "Ativo: Ausente - Finaliza\xe7\xe3o de trabalho de conclus\xe3o de curso",
                            ),
                            (
                                "ATIVO_AFA_TREINAMENTO",
                                "Ativo: Afastado - Treinamento (Palestras/Congressos/Semin\xe1rios/Outros)",
                            ),
                            (
                                "ATIVO_LIC_POLITICA",
                                "Ativo: Licenciado - Atividade Pol\xedtica",
                            ),
                            (
                                "ATIVO_AFA_COMPETICAO",
                                "Ativo: Afastado - Competi\xe7\xe3o desportiva ou representa\xe7\xe3o cultural",
                            ),
                            (
                                "ATIVO_LIC_ADOCAO",
                                "Ativo: Licenciado - Tutoria ou Ado\xe7\xe3o",
                            ),
                            (
                                "ATIVO_DESEMPENHO_FUNCAO",
                                "Ativo: Desempenho de Fun\xe7\xe3o",
                            ),
                            (
                                "ATIVO_AFA_ELEITORAL",
                                "Ativo: Afastado - Convoca\xe7\xe3o da Justi\xe7a Eleitoral",
                            ),
                            (
                                "INATIVO_APO_COMPULSORIO",
                                "Inativo: Aposentado - Compuls\xf3rio",
                            ),
                            (
                                "ATIVO_LIC_MATERNIDADE",
                                "Ativo: Licenciado - Maternidade",
                            ),
                            (
                                "ATIVO_LIC_MILITAR",
                                "Ativo: Licenciado - Servi\xe7o Militar",
                            ),
                            (
                                "INATIVO_APO_INVALIDEZ",
                                "Inativo: Aposentado - Por invalidez",
                            ),
                            ("NOT_FOUND", "N\xe3o encontrado"),
                            ("INATIVO_APO_ESPECIAL", "Inativo: Aposentado - Especial"),
                            (
                                "ATIVO_AFA_COMPJUIZO",
                                "Ativo: Afastado - Comparecer a ju\xedzo",
                            ),
                            (
                                "INATIVO_APO_TEMPO_CONTRIBUICAO",
                                "Inativo: Aposentado - Por tempo de contribui\xe7\xe3o",
                            ),
                            (
                                "ATIVO_DISPONIBILIDADE",
                                "Ativo: - Em disponibilidade(com onus para origem ou para requisitante?)",
                            ),
                            (
                                "INATIVO_EXONERADO_OFICIO",
                                "Inativo: Exonerado - De of\xedcio",
                            ),
                            ("ATIVO_PLANTAO", "Ativo: Fruindo Plant\xe3o de Feriado"),
                            (
                                "ATIVO_LIC_CLASSISTA",
                                "Ativo: Licenciado - Desempenho de Mandato Classista",
                            ),
                            (
                                "ATIVO_FOLGA_ANIVERSARIO",
                                "Ativo: Fruindo Folga Anivers\xe1rio",
                            ),
                            (
                                "ATIVO_AUS_NASCIMENTO",
                                "Ativo: Ausente - Nascimento/ado\xe7\xe3o de filho",
                            ),
                            (
                                "INATIVO_EXONERADO_PEDIDO",
                                "Inativo: Exonerado - A pedido",
                            ),
                        ],
                    ),
                ),
                ("data_inicio", models.DateField()),
                ("data_fim", models.DateField(null=True)),
                ("data_alteracao", models.DateField(auto_now_add=True)),
                ("objeto_pk", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
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
                    "servidor",
                    models.ForeignKey(
                        related_name="historico_situacao_funcional",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Servidor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Situa\xe7\xe3o funcional",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Telefone",
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
                    "tipo_telefone",
                    models.IntegerField(
                        verbose_name="Tipo de Telefone",
                        choices=[
                            (1, "RESIDENCIAL"),
                            (2, "COMERCIAL"),
                            (3, "CELULAR"),
                            (4, "FAX"),
                            (5, "INSTITUCIONAL"),
                        ],
                    ),
                ),
                ("numero", models.CharField(max_length=15, verbose_name="N\xfamero")),
                (
                    "publico",
                    models.BooleanField(default=False, verbose_name="P\xfablico"),
                ),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
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
                "verbose_name": "Telefone",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TempoServicoFinalidade",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
            name="TipoOrigem",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
            name="TipoServidor",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "indicativo",
                    models.CharField(
                        max_length=1,
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
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "entrancia",
                    models.ForeignKey(
                        verbose_name="Entr\xe2ncia",
                        blank=True,
                        to="rh.Entrancia",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "instancia",
                    models.ForeignKey(
                        verbose_name="Inst\xe2ncia",
                        blank=True,
                        to="rh.Instancia",
                        null=True,
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
                "ordering": ["nome"],
                "verbose_name": "Tipo de servidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="UnidadeAdministrativa",
            fields=[
                (
                    "orgaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.OrgaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "numero",
                    models.CharField(
                        max_length=3, null=True, verbose_name="N\xfamero", blank=True
                    ),
                ),
                ("email", models.EmailField(max_length=75, null=True, blank=True)),
                (
                    "pessoa_juridica",
                    models.ForeignKey(
                        verbose_name="Pessoa Jur\xeddica",
                        blank=True,
                        to="rh.PessoaJuridica",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "previdencia",
                    models.ForeignKey(
                        related_name="como_previdencia_de_unidade_administrativa",
                        blank=True,
                        to="rh.PessoaJuridica",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "responsavel",
                    models.ForeignKey(
                        null=True,
                        blank=True,
                        to="rh.PessoaFisica",
                        unique=True,
                        verbose_name="Respons\xe1vel",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Unidade Administrativa",
            },
            bases=("rh.orgaogeral",),
        ),
        migrations.AlterUniqueTogether(
            name="situacaofuncional",
            unique_together=set(
                [("servidor", "situacao", "data_inicio", "content_type", "objeto_pk")]
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="lotacoes",
            field=models.ManyToManyField(to="rh.Lotacao", through="rh.ServidorLotacao"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
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
            model_name="servidor",
            name="molestia",
            field=models.OneToOneField(
                null=True,
                blank=True,
                to="rh.Molestia",
                verbose_name="Mol\xe9stia",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
            name="organ_social_security",
            field=models.ForeignKey(
                related_name="employees_organ_social_security",
                verbose_name="\xd3rg\xe3o previdenci\xe1rio",
                blank=True,
                to="rh.PessoaJuridica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
            name="pessoa_fisica",
            field=models.ForeignKey(
                verbose_name="Pessoa F\xedsica",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
            name="user",
            field=models.ForeignKey(
                related_name="servidor",
                null=True,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                unique=True,
                verbose_name="Usu\xe1rio",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="quadro",
            unique_together=set([("cargo", "especialidade")]),
        ),
        migrations.AlterUniqueTogether(
            name="publicconcurrence",
            unique_together=set([("number_mpe", "year_mpe")]),
        ),
        migrations.AddField(
            model_name="publicacao",
            name="origem",
            field=models.ForeignKey(
                verbose_name="Origem",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="publicacao",
            name="sent_to_publication_by",
            field=models.ForeignKey(
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="prorrogacao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="prorrogacao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoa",
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
            model_name="pessoa",
            name="dado_bancario",
            field=models.ManyToManyField(
                related_name="dados_bancarios_pessoas",
                null=True,
                verbose_name="Dado Banc\xe1rio",
                to="rh.DadoBancario",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoa",
            name="endereco",
            field=models.ManyToManyField(
                to="rh.Endereco", null=True, verbose_name="Endere\xe7o", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoa",
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
            model_name="pessoa",
            name="telefone",
            field=models.ManyToManyField(to="rh.Telefone", null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodorequisicao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="periodo_requisicao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodorequisicao",
            name="requisicao",
            field=models.ForeignKey(
                related_name="periodo",
                to="rh.MovimentacaoRequisicao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="orgaogeral",
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
            model_name="orgaogeral",
            name="endereco",
            field=models.ManyToManyField(
                to="rh.Endereco", null=True, verbose_name="Endere\xe7o", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="orgaogeral",
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
            model_name="orgaogeral",
            name="telefone",
            field=models.ManyToManyField(to="rh.Telefone", null=True, blank=True),
            preserve_default=True,
        ),
    ]
