# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AcaoContrato",
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
                ("data_acao", models.DateTimeField(auto_now_add=True)),
                (
                    "tipo",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Cadastro do contrato"),
                            (1, "Pedir prorroga\xe7\xe3o"),
                            (2, "Aceitar pedido de prorroga\xe7\xe3o"),
                            (3, "Negar pedido de prorroga\xe7\xe3o"),
                            (4, "Pedir Licita\xe7\xe3o"),
                            (5, "Negar Licita\xe7\xe3o"),
                            (6, "Licitar"),
                            (7, "Finalizar contrato"),
                            (8, "Pedir recis\xe3o contratual"),
                            (9, "Aceitar pedido de recis\xe3o contratual"),
                            (10, "Negar pedido de recis\xe3o contratual"),
                            (11, "Alertar vencimento do Contrato"),
                            (12, "Solicita\xe7\xe3o de pagamento"),
                            (13, "Lan\xe7ar pagamento"),
                        ]
                    ),
                ),
                ("observacao", models.TextField(null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Adtivo",
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
                ("horario", models.DateTimeField(auto_now_add=True)),
                ("observacao", models.TextField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Contrato",
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
                ("numero", models.CharField(max_length=20)),
                ("objeto_contrato", models.CharField(max_length=80)),
                ("numero_processo", models.CharField(max_length=20)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Em Execu\xe7\xe3o"),
                            (1, "Solicitada Prorroga\xe7\xe3o"),
                            (2, "Solicitada a Licita\xe7\xe3o"),
                            (3, "Solicitada a Recis\xe3o"),
                            (4, "Finalizado"),
                        ]
                    ),
                ),
                ("data_inicio", models.DateField()),
                ("data_vencimento", models.DateField()),
                ("data_vencimento_original", models.DateField(null=True, blank=True)),
                ("dias_para_aviso", models.SmallIntegerField()),
                ("prorrogado", models.SmallIntegerField(default=0, blank=True)),
                ("max_mes", models.SmallIntegerField(default=60, blank=True)),
                (
                    "tipo_licitacao",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (0, "Registro de Pre\xe7o"),
                            (1, "Dispensa de Licita\xe7\xe3o"),
                            (2, "Inexigibilidade de Licita\xe7\xe3o"),
                            (3, "Preg\xe3o Eletr\xf4nico"),
                            (4, "Preg\xe3o Presencial"),
                            (5, "Ades\xe3o a Ata SRP"),
                            (6, "Concorr\xeancia"),
                        ],
                    ),
                ),
                (
                    "numero_licitacao",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "valor",
                    models.DecimalField(
                        null=True, max_digits=18, decimal_places=2, blank=True
                    ),
                ),
                (
                    "tipo_medicao",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[(0, "Contrato"), (1, "Etapa"), (2, "Mensal")],
                    ),
                ),
                ("dia_pagamento", models.SmallIntegerField(null=True, blank=True)),
                (
                    "tipo_contrato",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Contrato"),
                            (2, "SRP"),
                            (3, "NE"),
                            (4, "Loca\xe7\xe3o"),
                            (5, "Servi\xe7os Continuos"),
                        ],
                    ),
                ),
                (
                    "numero_pasta",
                    models.CharField(default="", max_length=150, null=True),
                ),
                ("data_publicacao", models.DateField(null=True, blank=True)),
                ("data_publicacao_fiscal", models.DateField(null=True, blank=True)),
                ("data_vencimento_flag", models.DateField(null=True, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EnvioNEFornecedor",
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
                    "data_envio",
                    models.DateField(null=True, verbose_name="Data envio fornecedor"),
                ),
                (
                    "prorrogacao",
                    models.IntegerField(
                        blank=True, null=True, choices=[(0, "Sim"), (1, "N\xe3o")]
                    ),
                ),
                ("dias_prorrogacao", models.SmallIntegerField(null=True, blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Gestor",
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
                    "tipo",
                    models.SmallIntegerField(
                        verbose_name="Tipo",
                        choices=[
                            (1, "Fiscal do Contrato"),
                            (2, "Gestor Geral"),
                            (3, "Departamento de Contrato"),
                            (4, "Departamento de Licita\xe7\xe3o"),
                            (5, "Departamento Financeiro"),
                        ],
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Medicao",
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
                ("horario", models.DateTimeField(auto_now_add=True)),
                ("observacao", models.TextField()),
                ("valor", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "inicio_periodo_referencia",
                    models.DateField(
                        null=True, verbose_name="Inicio do periodo referencia"
                    ),
                ),
                (
                    "fim_periodo_referencia",
                    models.DateField(
                        null=True, verbose_name="Fim do periodo de referencia"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default=1,
                        max_length=1,
                        blank=True,
                        choices=[
                            (1, "AGUARDANDO PAGAMENTO"),
                            (2, "PAGO"),
                            (3, "N\xc3O PAGO"),
                        ],
                    ),
                ),
                (
                    "ordem_bancaria",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "data_pagamento",
                    models.DateField(
                        null=True, verbose_name="Data do pagamento", blank=True
                    ),
                ),
                ("modificado_em", models.DateTimeField(auto_now=True)),
                (
                    "nota_fiscal",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
            ],
            options={
                "ordering": ("-id",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotaEmpenho",
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
                ("numero_ne", models.CharField(unique=True, max_length=20)),
                ("valor", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "tipo",
                    models.IntegerField(
                        choices=[(1, "Ordin\xe1rio"), (2, "Estimativo"), (3, "Global")]
                    ),
                ),
                (
                    "prazo_entrega",
                    models.SmallIntegerField(
                        default=0, verbose_name="Prazo de entrega do produto"
                    ),
                ),
                (
                    "classificacao",
                    models.IntegerField(
                        null=True,
                        choices=[
                            (1, "Material de Consumo"),
                            (2, "Material Permanente"),
                            (3, "Servi\xe7os"),
                            (4, "Obras e Instala\xe7\xf5es"),
                        ],
                    ),
                ),
                (
                    "reforco_estorno",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[(0, "Refor\xe7o"), (1, "Estorno")],
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
                (
                    "contrato",
                    models.ForeignKey(
                        related_name="ne",
                        to="contrato.Contrato",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "criado_por",
                    models.ForeignKey(
                        related_name="minhas_nes",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ValorContrato",
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
                    "data_ref_inicio",
                    models.DateField(null=True, verbose_name="Data Referencia Inicio"),
                ),
                (
                    "data_ref_fim",
                    models.DateField(null=True, verbose_name="Data Referencia Fim"),
                ),
                (
                    "valor",
                    models.DecimalField(
                        null=True, max_digits=18, decimal_places=2, blank=True
                    ),
                ),
                ("ordem", models.IntegerField(default=0)),
                ("data_publicacao", models.DateField(null=True, blank=True)),
                (
                    "contrato",
                    models.ForeignKey(
                        related_name="valores_contrato",
                        to="contrato.Contrato",
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
                "ordering": ("ordem",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
