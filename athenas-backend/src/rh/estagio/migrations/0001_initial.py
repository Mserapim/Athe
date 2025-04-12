# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ApreciacaoComissao",
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
                    "decisao",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[(1, "RECOMENDA"), (2, "N\xc3O RECOMENDA")],
                    ),
                ),
            ],
            options={
                "ordering": ("comissao_servidor__estagio_prob_servidor__fim_estagio",),
                "db_table": "gep_apreciacao_comissao",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ComissaoAvaliadora",
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
                ("data_inicio", models.DateField(blank=True)),
                ("data_fim", models.DateField(null=True, blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("-id",),
                "db_table": "gep_comissao_avaliadora",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Conceito",
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
                ("valor_inicial", models.DecimalField(max_digits=5, decimal_places=2)),
                ("valor_final", models.DecimalField(max_digits=5, decimal_places=2)),
                ("descricao", models.CharField(default="", max_length=100, null=True)),
            ],
            options={
                "db_table": "gep_conceito",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Configuracao",
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
                ("data_inicio", models.DateField(blank=True)),
                ("data_fim", models.DateField(null=True, blank=True)),
                (
                    "qtde_avaliacoes",
                    models.SmallIntegerField(
                        default="3", verbose_name="Quantidade de Avalia\xe7\xf5es"
                    ),
                ),
                (
                    "qtde_meses_entre_avaliacao",
                    models.SmallIntegerField(
                        default="10",
                        verbose_name="Quantidade de meses entre avalia\xe7\xf5es",
                    ),
                ),
                (
                    "porc_aprovacao",
                    models.DecimalField(
                        verbose_name="Porcentagem de Aprova\xe7\xe3o",
                        max_digits=5,
                        decimal_places=2,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "gep_configuracao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DecisaoChefeOrgao",
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
                    "decisao",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[(1, "HOMOLOGA"), (2, "N\xc3O HOMOLOGA")],
                    ),
                ),
                ("fundamentacao", models.TextField(null=True, blank=True)),
            ],
            options={
                "ordering": (
                    "estagio_comissao_servidor__estagio_prob_servidor__fim_estagio",
                ),
                "db_table": "gep_decisao_chefe_orgao",
                "permissions": (
                    ("can_valid_stage_prob", "Validar permiss\xf5es para julgamento"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="EstagioAvaliacao",
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
                ("periodo_avaliado", models.SmallIntegerField(default=0)),
                ("status", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("data_inicio_etapa", models.DateField()),
                ("dias_interrompidos", models.SmallIntegerField(default=0)),
                ("data_fim_etapa", models.DateField()),
                ("finalizado_em", models.DateTimeField(auto_now=True)),
                (
                    "media_comissao",
                    models.DecimalField(null=True, max_digits=5, decimal_places=2),
                ),
                ("observacao_comissao", models.TextField(null=True, blank=True)),
                (
                    "avaliador_externo",
                    models.TextField(
                        null=True, verbose_name="Avaliador de \xd3rg\xe3o Externo"
                    ),
                ),
                (
                    "matricula_externo",
                    models.TextField(
                        null=True,
                        verbose_name="Matricula do Avaliador de \xd3rg\xe3o Externo",
                    ),
                ),
                (
                    "cargo_externo",
                    models.TextField(
                        null=True,
                        verbose_name="Cargo do Avaliador de \xd3rg\xe3o Externo",
                    ),
                ),
                (
                    "lotacao_externo",
                    models.TextField(
                        null=True,
                        verbose_name="Lota\xe7\xe3o do Avaliador de \xd3rg\xe3o Externo",
                    ),
                ),
                ("data_avaliacao_externa", models.DateField(null=True)),
            ],
            options={
                "db_table": "gep_estagio_avaliacao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EstagioComissaoServidor",
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
                "ordering": ("estagio_prob_servidor__fim_estagio",),
                "db_table": "gep_estagio_comissao_servidor",
                "permissions": (
                    ("estagio_comissao", "Comiss\xe3o de Est\xe1gio"),
                    ("estagio_decisao", "Decis\xe3o de Est\xe1gio"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="EstagioProbatorioServidor",
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
                    "ultima_avaliacao",
                    models.DateField(null=True, verbose_name="Data Ultima Avaliacao"),
                ),
                (
                    "proxima_avaliacao",
                    models.DateField(null=True, verbose_name="Data Proxima Avaliacao"),
                ),
                (
                    "bloqueada",
                    models.BooleanField(default=False, verbose_name="Bloqueada"),
                ),
                ("avaliacoes_realizadas", models.SmallIntegerField(default=0)),
                (
                    "media",
                    models.DecimalField(default=0, max_digits=5, decimal_places=2),
                ),
                (
                    "status",
                    models.CharField(
                        default=1,
                        max_length=1,
                        choices=[
                            (1, "Em Andamento"),
                            (2, "Finalizado"),
                            (3, "Julgamento Comiss\xe3o"),
                            (4, "Homologado"),
                        ],
                    ),
                ),
                (
                    "fim_estagio",
                    models.DateField(null=True, verbose_name="Data Fim Est\xe1gio"),
                ),
                (
                    "dias_falta",
                    models.DecimalField(
                        default=0, null=True, max_digits=5, decimal_places=2
                    ),
                ),
                (
                    "estado_avaliacao",
                    models.CharField(
                        default=1,
                        max_length=1,
                        blank=True,
                        choices=[
                            (1, "NOVO"),
                            (2, "AVALIADO"),
                            (3, "MANIFESTADO"),
                            (4, "FINALIZADO"),
                        ],
                    ),
                ),
                (
                    "ciencia_decisao_estagio",
                    models.DateField(
                        null=True,
                        verbose_name="Data da Ci\xeancia da Decis\xe3o do est\xe1gio",
                    ),
                ),
                (
                    "dado_legado",
                    models.CharField(
                        default=1,
                        max_length=1,
                        blank=True,
                        choices=[(1, "NOVO"), (2, "LEGADO")],
                    ),
                ),
            ],
            options={
                "ordering": ("proxima_avaliacao",),
                "db_table": "gep_estagio_prob_servidor",
                "permissions": (
                    ("estagio_admin", "Administrador de est\xe1gio"),
                    (
                        "estagio_avaliador",
                        "Avaliador de servidor em est\xe1gio probat\xf3rio",
                    ),
                    ("estagio_avaliado", "Avaliado em est\xe1gio probat\xf3rio"),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FatorAvaliacao",
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
                ("descricao", models.CharField(default="", max_length=300)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["descricao"],
                "db_table": "gep_fator_avaliacao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IntegrantesComissao",
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
                    "tipo_participante",
                    models.CharField(
                        default=4,
                        max_length=1,
                        choices=[
                            (1, "PRESIDENTE"),
                            (2, "SECRET\xc1RIO"),
                            (3, "INTEGRANTE"),
                            (4, "SUPLENTE"),
                        ],
                    ),
                ),
                ("ordem", models.PositiveSmallIntegerField(null=True)),
                (
                    "impedimento",
                    models.BooleanField(
                        default=False,
                        verbose_name="Impedido de participar do processo temporariamente",
                    ),
                ),
            ],
            options={
                "ordering": ("ordem",),
                "db_table": "gep_integrantes_comissao",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ManifestacaoEstagio",
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
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "gep_manifestacao_estagio",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="QuesitoAvaliacao",
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
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "gep_quesito_avaliacao",
            },
            bases=(models.Model,),
        ),
    ]
