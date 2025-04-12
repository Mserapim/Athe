# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Anexo",
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
                    "arquivo",
                    models.OneToOneField(
                        related_name="+", to="ged.Arquivo", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "siatu_anexo",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Atendente",
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
                ("notificacao_receber_chamado", models.BooleanField(default=False)),
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "usuario",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("usuario__username",),
                "db_table": "siatu_atendente",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AtendentesServicos",
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
                ("distribuicao_automatica", models.BooleanField(default=True)),
                (
                    "atendente",
                    models.ForeignKey(
                        related_name="relacaoAt_Serv",
                        to="siatu.Atendente",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("atendente__usuario__username", "servico__nome"),
                "db_table": "siatu_atendentes_servicos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Avaliacao",
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
                    "presteza",
                    models.SmallIntegerField(
                        default=0,
                        choices=[
                            (1, "P\xe9ssimo"),
                            (2, "Ruim"),
                            (3, "Regular"),
                            (4, "Bom"),
                            (5, "\xd3timo"),
                        ],
                    ),
                ),
                (
                    "esclarecimento",
                    models.SmallIntegerField(
                        default=0,
                        choices=[
                            (1, "P\xe9ssimo"),
                            (2, "Ruim"),
                            (3, "Regular"),
                            (4, "Bom"),
                            (5, "\xd3timo"),
                        ],
                    ),
                ),
                (
                    "tempo",
                    models.SmallIntegerField(
                        default=0,
                        choices=[
                            (1, "P\xe9ssimo"),
                            (2, "Ruim"),
                            (3, "Regular"),
                            (4, "Bom"),
                            (5, "\xd3timo"),
                        ],
                    ),
                ),
                (
                    "satisfacao",
                    models.SmallIntegerField(
                        choices=[
                            (1, "P\xe9ssimo"),
                            (2, "Ruim"),
                            (3, "Regular"),
                            (4, "Bom"),
                            (5, "\xd3timo"),
                        ]
                    ),
                ),
                ("sugestao", models.CharField(max_length=250, null=True)),
                ("replica", models.CharField(max_length=2000, null=True)),
            ],
            options={
                "db_table": "siatu_avaliacao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BaseConhecimento",
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
                ("problema", models.CharField(max_length=500)),
                ("solucao", models.TextField()),
                (
                    "arquivo",
                    models.OneToOneField(
                        related_name="+",
                        null=True,
                        to="ged.Arquivo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("objeto__descricao",),
                "db_table": "siatu_base_conhecimento",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Chamado",
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
                ("data_fila_atendimento", models.DateTimeField(null=True)),
                ("numero", models.SmallIntegerField()),
                ("ano", models.SmallIntegerField()),
                ("cache_numero", models.CharField(max_length=10, db_index=True)),
                ("cancelado", models.BooleanField(default=False)),
                ("nao_institucional", models.BooleanField(default=False)),
                ("motivo_cancelado", models.CharField(max_length=200, null=True)),
                ("urgente", models.BooleanField(default=False)),
                ("rank", models.IntegerField(default=0, db_index=True)),
                ("motivo_urgencia", models.CharField(max_length=200, null=True)),
                ("relatorio", models.TextField(null=True, blank=True)),
                (
                    "atendentes",
                    models.ManyToManyField(
                        related_name="chamados", to="siatu.Atendente"
                    ),
                ),
            ],
            options={
                "ordering": ("-pk",),
                "db_table": "siatu_chamado",
                "permissions": (
                    ("admin", "Vis\xe3o administrativa"),
                    ("gerente", "Vis\xe3o de gerente"),
                    ("atendente", "Vis\xe3o de atendente"),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ConfigEmailAtendente",
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
                ("transferido_atendente", models.BooleanField(default=True)),
                ("apos_avaliacao", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "siatu_configemailatendente",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ConfigEmailSolicitante",
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
                ("aguardando_avaliacao", models.BooleanField(default=True)),
                ("transferido_atendente", models.BooleanField(default=True)),
                ("garantia", models.BooleanField(default=True)),
                ("terceirizada", models.BooleanField(default=True)),
                ("viagem", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "siatu_configemailsolicitante",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DistribuicaoAutomatica",
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
                ("tipo_atendimento", models.CommaSeparatedIntegerField(max_length=15)),
            ],
            options={
                "db_table": "siatu_distribuicao_automatica",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FilaUnica",
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
                ("localidade", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "siatu_fila_unica",
            },
            bases=(models.Model,),
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
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "usuario",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("usuario__username",),
                "db_table": "siatu_gerente",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ItemBaseConhecimento",
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
                ("info", models.CharField(max_length=100, null=True)),
                (
                    "base_conhecimento",
                    models.ForeignKey(
                        related_name="itens_base_conhecimento",
                        to="siatu.BaseConhecimento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "chamado",
                    models.ForeignKey(
                        related_name="itens_base_conhecimento",
                        to="siatu.Chamado",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("base_conhecimento__objeto__descricao",),
                "db_table": "siatu_item_base_conhecimento",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Modelo",
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
                ("descricao", models.CharField(unique=True, max_length=100)),
                ("informatica", models.NullBooleanField()),
            ],
            options={
                "ordering": ("descricao",),
                "db_table": "siatu_modelo",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Objeto",
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
                ("descricao", models.CharField(unique=True, max_length=100)),
                ("informatica", models.BooleanField(default=False)),
                (
                    "modelos",
                    models.ManyToManyField(related_name="objetos", to="siatu.Modelo"),
                ),
            ],
            options={
                "ordering": ("descricao",),
                "db_table": "siatu_objeto",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Reincidencia",
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
                ("opiniao_atendente", models.CharField(max_length=300, null=True)),
                ("confirm_atendente", models.BooleanField(default=True)),
                ("motivo_gerente", models.CharField(max_length=300, null=True)),
                ("parecer", models.NullBooleanField()),
            ],
            options={
                "db_table": "siatu_reincidencia",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Servico",
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
                ("nome", models.CharField(max_length=150)),
                (
                    "lista_atendentes",
                    models.ManyToManyField(
                        related_name="servicos_vinculados",
                        through="siatu.AtendentesServicos",
                        to="siatu.Atendente",
                    ),
                ),
                (
                    "lista_gerentes",
                    models.ManyToManyField(
                        related_name="servicos_vinculados", to="siatu.Gerente"
                    ),
                ),
                (
                    "servico_superior",
                    models.ForeignKey(
                        related_name="subservicos",
                        to="siatu.Servico",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("nome",),
                "db_table": "siatu_servico",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Solicitacao",
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
                        default=0,
                        choices=[
                            (0, "Sistema"),
                            (1, "Email"),
                            (2, "Telefone"),
                            (3, "Documento"),
                            (4, "Verbal"),
                        ],
                    ),
                ),
                ("telefone", models.CharField(max_length=25)),
                ("descricao_problema", models.CharField(max_length=600)),
                ("reincidencia", models.BooleanField(default=False)),
                (
                    "chamado_anterior",
                    models.ForeignKey(
                        related_name="+",
                        to="siatu.Chamado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "servico",
                    models.ForeignKey(
                        related_name="solicitacoes",
                        to="siatu.Servico",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "solicitante",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "usuario",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-pk",),
                "db_table": "siatu_solicitacao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Status",
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
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Aberto"),
                            (2, "Aguardando atendimento"),
                            (3, "Em atendimento"),
                            (4, "Aguardando avalia\xe7\xe3o"),
                            (5, "Transferido para outro atendente"),
                            (6, "Terceirizada"),
                            (7, "Garantia"),
                            (8, "Em Viagem"),
                            (9, "Conclu\xeddo"),
                            (10, "Aguardando entrega"),
                            (11, "Em manuten\xe7\xe3o"),
                        ]
                    ),
                ),
                ("data_inicio", models.DateTimeField()),
                ("previsao_fim", models.DateField(null=True)),
                ("motivo", models.CharField(max_length=300, null=True)),
                (
                    "chamado",
                    models.ForeignKey(
                        related_name="historico_status",
                        to="siatu.Chamado",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("data_inicio",),
                "db_table": "siatu_status",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Terceirizada",
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
                ("nome", models.CharField(max_length=80)),
                ("cnpj", models.CharField(max_length=50)),
            ],
            options={
                "ordering": ("nome",),
                "db_table": "siatu_terceirizada",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TerceiroInterno",
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
                ("nome", models.CharField(max_length=80)),
                ("cpf", models.CharField(max_length=50)),
                ("telefone", models.CharField(max_length=50)),
                ("endereco", models.CharField(max_length=150)),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1, choices=[(1, "ATIVO"), (2, "INATIVO")]
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "db_table": "siatu_terceirointerno",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Transferencia",
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
                ("motivo", models.CharField(max_length=300)),
                ("data_pedido", models.DateTimeField()),
                ("data_aceite", models.DateTimeField(null=True)),
                ("cancelado", models.BooleanField(default=False)),
                (
                    "aceito_por",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "atendente_anterior",
                    models.ManyToManyField(
                        related_name="transferencias_como_remetente",
                        to="siatu.Atendente",
                    ),
                ),
                (
                    "atendente_posterior",
                    models.ManyToManyField(
                        related_name="transferencias_como_destinatario",
                        to="siatu.Atendente",
                    ),
                ),
                (
                    "chamado",
                    models.ForeignKey(
                        related_name="transferencias",
                        to="siatu.Chamado",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pedido_por",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("pk",),
                "db_table": "siatu_transferencia",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="status",
            name="terceirizada",
            field=models.ForeignKey(
                related_name="+",
                to="siatu.Terceirizada",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="itembaseconhecimento",
            unique_together=set([("chamado", "base_conhecimento")]),
        ),
        migrations.AddField(
            model_name="filaunica",
            name="servico",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="filas", to="siatu.Servico", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="filaunica",
            unique_together=set([("servico", "localidade")]),
        ),
        migrations.AddField(
            model_name="distribuicaoautomatica",
            name="servico",
            field=models.OneToOneField(
                related_name="distribuicao_automatica",
                to="siatu.Servico",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="distribuicaoautomatica",
            name="solicitantes",
            field=models.ManyToManyField(related_name="+", to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="base_conhecimento",
            field=models.ManyToManyField(
                related_name="chamados",
                null=True,
                through="siatu.ItemBaseConhecimento",
                to="siatu.BaseConhecimento",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="cfg_email_atendente",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                to="siatu.ConfigEmailAtendente", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="cfg_email_solicitante",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                to="siatu.ConfigEmailSolicitante", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="chamado_anterior",
            field=models.OneToOneField(
                related_name="chamado_reincidente",
                null=True,
                to="siatu.Chamado",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="fila",
            field=models.ForeignKey(
                related_name="chamados",
                to="siatu.FilaUnica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="reincidencia",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.OneToOneField(
                null=True, to="siatu.Reincidencia", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="servico",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="chamados", to="siatu.Servico", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="solicitacao",
            field=models.OneToOneField(
                to="siatu.Solicitacao", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="status_atual",
            field=models.OneToOneField(
                related_name="+", null=True, to="siatu.Status", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="terceirizada",
            field=models.ManyToManyField(
                related_name="chamados", to="siatu.Terceirizada"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="terceiro_interno",
            field=models.ManyToManyField(
                related_name="chamados", to="siatu.TerceiroInterno"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baseconhecimento",
            name="modelo",
            field=models.ForeignKey(
                to="siatu.Modelo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="baseconhecimento",
            name="objeto",
            field=models.ForeignKey(
                to="siatu.Objeto", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="avaliacao",
            name="chamado",
            field=models.OneToOneField(
                to="siatu.Chamado", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="atendentesservicos",
            name="servico",
            field=models.ForeignKey(
                related_name="relacaoAt_Serv",
                to="siatu.Servico",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="atendentesservicos",
            unique_together=set([("servico", "atendente")]),
        ),
        migrations.AddField(
            model_name="anexo",
            name="chamado",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="anexos", to="siatu.Chamado", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
