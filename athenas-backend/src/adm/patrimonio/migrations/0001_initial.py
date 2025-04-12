# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import standard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
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
                ("ano", models.SmallIntegerField()),
                ("mes", models.SmallIntegerField()),
                ("numero", models.SmallIntegerField()),
                (
                    "tipo",
                    models.SmallIntegerField(
                        db_index=True,
                        choices=[
                            (1, "Deprecia\xe7\xe3o de Rotina"),
                            (2, "Deprecia\xe7\xe3o"),
                            (3, "Reavalia\xe7\xe3o"),
                        ],
                    ),
                ),
                ("data_execucao", models.DateTimeField(null=True)),
                ("de", models.DateTimeField(null=True)),
                ("ate", models.DateTimeField(null=True)),
            ],
            options={
                "ordering": ("-ano", "-mes", "numero"),
                "permissions": (
                    (
                        "executa_auto_depreciacao",
                        "Pode executar deprecia\xe7\xe3o autom\xe1tica",
                    ),
                    ("executa_avalicao", "Pode executar avaliacao"),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AvaliacaoItem",
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
                ("valor_atual", models.DecimalField(max_digits=20, decimal_places=6)),
                (
                    "valor_avaliado",
                    models.DecimalField(default=0.0, max_digits=20, decimal_places=6),
                ),
                ("vida_util", models.SmallIntegerField(null=True)),
                (
                    "depreciacao",
                    models.DecimalField(default=0.0, max_digits=20, decimal_places=6),
                ),
                (
                    "residual",
                    models.DecimalField(default=0.0, max_digits=20, decimal_places=6),
                ),
                ("quantidade_dias", models.SmallIntegerField(default=0)),
                (
                    "taxa_pro_rata",
                    models.DecimalField(default=0.0, max_digits=20, decimal_places=6),
                ),
                (
                    "conservacao",
                    models.SmallIntegerField(
                        db_index=True,
                        choices=[
                            (1, "Novo"),
                            (2, "Bom"),
                            (3, "Regular"),
                            (4, "Inservivel"),
                        ],
                    ),
                ),
                ("discarded", models.BooleanField(default=False)),
                ("discarded_justify", models.TextField(null=True)),
                ("discarded_at", models.DateTimeField(null=True)),
            ],
            options={
                "permissions": (
                    ("can_discard_review", "Pode descartar avalia\xe7\xe3o."),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BaixaItem",
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
                    "valor_atual",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "valor_baixa",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "valor_avaliacao",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("observacao", models.TextField(default="")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Conta",
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
                        default=1,
                        db_index=True,
                        verbose_name="Tipo",
                        choices=[(1, "Controlado"), (2, "Relacionado")],
                    ),
                ),
                (
                    "principal",
                    models.BooleanField(default=False, verbose_name="Principal"),
                ),
                ("titulo", models.CharField(max_length=100, verbose_name="T\xedtulo")),
                ("sufix", models.CharField(max_length=10, null=True, blank=True)),
                ("prefix", models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                "ordering": ("tipo", "titulo"),
                "permissions": (("can_change_sequence", "Pode mudar a sequencia"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CriticarNotaEntrada",
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
                ("quando", models.DateTimeField(auto_now_add=True)),
                ("respondido_quando", models.DateTimeField(null=True)),
                ("resposta", models.TextField(null=True)),
                (
                    "state",
                    models.SmallIntegerField(
                        default=1,
                        choices=[(1, "Aberto"), (2, "Deferido"), (3, "Indeferido")],
                    ),
                ),
                ("data_nota", models.DateTimeField(null=True, db_index=True)),
                ("data_compra", models.DateTimeField(null=True)),
                ("processo", models.CharField(max_length=20, null=True, db_index=True)),
                (
                    "execucao_orcamentaria",
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        choices=[
                            (
                                1,
                                "DEO - Dependente da Execu\xe7\xe3o Or\xe7ament\xe1ria",
                            ),
                            (
                                2,
                                "IEO - Independente da Execu\xe7\xe3o Or\xe7ament\xe1ria",
                            ),
                            (3, "DOA\xc7\xc3O"),
                        ],
                    ),
                ),
                ("descricao", models.TextField()),
            ],
            options={
                "ordering": ("-quando", "-respondido_quando"),
                "permissions": (
                    ("entrada_julgar_critica", "Julgar criticas de notas de entrada."),
                ),
            },
            bases=(models.Model,),
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
                ("titulo", models.CharField(max_length=100)),
                ("criado", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("criado", "titulo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Especie",
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
                ("codigo", models.SmallIntegerField(db_index=True)),
                (
                    "codigo_cache",
                    models.CharField(max_length=30, null=True, db_index=True),
                ),
                ("titulo", models.CharField(max_length=200)),
            ],
            options={
                "ordering": ("codigo", "titulo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GrupoEspecie",
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
                ("codigo", models.SmallIntegerField(db_index=True)),
                ("titulo", models.CharField(max_length=200)),
            ],
            options={
                "ordering": ("codigo", "titulo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ItemAvaliacao",
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
                ("vida_util", models.SmallIntegerField()),
                ("depreciacao", models.DecimalField(max_digits=5, decimal_places=2)),
                ("residual", models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
                "ordering": ("tabela", "grupo__titulo", "id", "especie__titulo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ItemEntrada",
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
                ("descricao", models.TextField()),
                (
                    "conservacao",
                    models.IntegerField(
                        db_index=True,
                        choices=[
                            (1, "Novo"),
                            (2, "Bom"),
                            (3, "Regular"),
                            (4, "Inservivel"),
                        ],
                    ),
                ),
                (
                    "valor_unitario",
                    models.DecimalField(max_digits=16, decimal_places=2),
                ),
                ("quantidade", models.IntegerField()),
                ("meses_garantia", models.IntegerField()),
            ],
            options={
                "ordering": ("especie__titulo", "valor_unitario"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Localizacao",
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
                ("titulo", models.CharField(max_length=150)),
                ("endereco", models.TextField(null=True, blank=True)),
                ("ativo", models.BooleanField(default=True)),
                ("folder_index", models.CharField(max_length=45, db_index=True)),
                ("height", models.SmallIntegerField(default=0)),
                (
                    "path_cache",
                    models.CharField(max_length=300, null=True, db_index=True),
                ),
            ],
            options={
                "ordering": ("titulo",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Movimento",
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
                ("numero", models.SmallIntegerField()),
                ("ano", models.SmallIntegerField()),
                ("movimentado", models.DateTimeField(null=True)),
                ("recebido", models.DateTimeField(null=True)),
                ("validado", models.DateTimeField(null=True)),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        choices=[
                            (1, "Aberto"),
                            (2, "Aguardando recebimento"),
                            (3, "Recebido"),
                            (4, "Ci\xeancia"),
                            (6, "Autorizado"),
                            (5, "Cancelado"),
                        ],
                    ),
                ),
                ("numero_cache", models.CharField(max_length=20)),
            ],
            options={
                "ordering": ("-ano", "-numero"),
                "permissions": (
                    ("admin_movimento", "Visualiza\xe7\xe3o administrativa."),
                    (
                        "auth_movimento_view",
                        "Visualiza\xe7\xe3o de pendentes de autoriza\xe7\xe3o.",
                    ),
                    ("validate_movimento", "Valida movimenta\xe7\xf5es."),
                    ("authorize_has_pgj", "Autoriza como Procurador Geral."),
                    ("authorize_has_cgpgj", "Autoriza como Chefe de Gabinete."),
                    ("authorize_has_dg", "Autoriza como Diretor Geral."),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MovimentoAssinatura",
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
                ("quando", models.DateTimeField(auto_now_add=True)),
                (
                    "score",
                    models.IntegerField(
                        choices=[(9, "Diretor Geral"), (10, "Procurador Geral")]
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MovimentoItem",
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
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MovimentoLogStatus",
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
                        db_index=True,
                        choices=[
                            (1, "Aberto"),
                            (2, "Aguardando recebimento"),
                            (3, "Recebido"),
                            (4, "Ci\xeancia"),
                            (6, "Autorizado"),
                            (5, "Cancelado"),
                        ],
                    ),
                ),
                ("atribuido", models.DateTimeField(auto_now_add=True)),
                ("comentario", models.TextField(blank=True)),
            ],
            options={
                "ordering": ("-atribuido",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotaBaixa",
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
                ("numero", models.SmallIntegerField()),
                ("ano", models.SmallIntegerField()),
                ("cache_numero", models.CharField(max_length=10, db_index=True)),
                ("liquidacao", models.CharField(max_length=20)),
                ("data_liquidacao", models.DateField(null=True)),
                ("processo", models.CharField(max_length=40)),
                ("documento", models.CharField(max_length=50)),
                ("data_documento", models.DateField(null=True)),
                ("data_baixa", models.DateField(null=True)),
                ("data_cadastro", models.DateField(auto_now_add=True)),
                (
                    "state",
                    models.SmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Nota Aberta"),
                            (2, "Nota Finalizada"),
                            (3, "Nota Cancelada"),
                        ],
                    ),
                ),
                (
                    "cache_type",
                    models.CharField(max_length=30, null=True, db_index=True),
                ),
            ],
            options={
                "ordering": ("-ano", "-numero"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BaixaTransferencia",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaSinistro",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaObsolescencia",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaInservibilidade",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaExtravio",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaDoacao",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaDeterioracao",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="BaixaAlienacao",
            fields=[
                (
                    "notabaixa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaBaixa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notabaixa",),
        ),
        migrations.CreateModel(
            name="NotaEntrada",
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
                ("note_number", models.SmallIntegerField(null=True, db_index=True)),
                ("note_year", models.SmallIntegerField(null=True, db_index=True)),
                (
                    "formated_number",
                    models.CharField(max_length=12, null=True, db_index=True),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                ("data_nota", models.DateTimeField(null=True, db_index=True)),
                ("data_compra", models.DateTimeField(null=True)),
                ("processo", models.CharField(max_length=20, null=True, db_index=True)),
                (
                    "execucao_orcamentaria",
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        choices=[
                            (
                                1,
                                "DEO - Dependente da Execu\xe7\xe3o Or\xe7ament\xe1ria",
                            ),
                            (
                                2,
                                "IEO - Independente da Execu\xe7\xe3o Or\xe7ament\xe1ria",
                            ),
                            (3, "DOA\xc7\xc3O"),
                        ],
                    ),
                ),
                (
                    "state",
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        choices=[
                            (1, "Nota Aberta"),
                            (2, "Nota Finalizada"),
                            (3, "Nota Cancelada"),
                        ],
                    ),
                ),
                (
                    "liquidacao",
                    models.CharField(max_length=15, null=True, db_index=True),
                ),
                ("data_liquidacao", models.DateField(null=True)),
                (
                    "cache_type",
                    models.CharField(max_length=30, null=True, db_index=True),
                ),
                ("tombado", models.DateTimeField(null=True, db_index=True)),
            ],
            options={
                "ordering": ("-note_year", "-note_number"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotaDoacao",
            fields=[
                (
                    "notaentrada_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaEntrada",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("patrimonio.notaentrada",),
        ),
        migrations.CreateModel(
            name="NotaFiscal",
            fields=[
                (
                    "notaentrada_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaEntrada",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("numero", models.CharField(max_length=100, db_index=True)),
            ],
            options={},
            bases=("patrimonio.notaentrada",),
        ),
        migrations.CreateModel(
            name="NotaConvenio",
            fields=[
                (
                    "notafiscal_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="patrimonio.NotaFiscal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("codigo_convenio", models.CharField(max_length=100, db_index=True)),
                ("data_convenio", models.DateField()),
                ("data_fim_convenio", models.DateField()),
            ],
            options={},
            bases=("patrimonio.notafiscal",),
        ),
        migrations.CreateModel(
            name="ParametroAvaliacao",
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
                ("valor", models.SmallIntegerField()),
                ("variavel", models.CharField(max_length=100)),
                (
                    "tipo",
                    models.SmallIntegerField(
                        db_index=True,
                        choices=[
                            (1, "Conserva\xe7\xe3o"),
                            (2, "Utiliza\xe7\xe3o"),
                            (3, "Vida \xfatil futura"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": ("tipo", "valor", "variavel"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Patrimonio",
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
                    "plaqueta",
                    models.CharField(db_index=True, max_length=10, blank=True),
                ),
                (
                    "conservacao",
                    models.IntegerField(
                        db_index=True,
                        choices=[
                            (1, "Novo"),
                            (2, "Bom"),
                            (3, "Regular"),
                            (4, "Inservivel"),
                        ],
                    ),
                ),
                (
                    "utilizacao",
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        choices=[(1, "1 Turno"), (2, "2 Turnos"), (3, "3 Turnos")],
                    ),
                ),
                ("descricao", models.TextField()),
                ("valor_atual", models.DecimalField(max_digits=20, decimal_places=6)),
                ("prazo_garantia", models.DateField()),
                ("vida_util", models.DateField(null=True)),
                ("data_baixa", models.DateField(null=True, db_index=True)),
                ("data_tombo", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("suspenso", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("-data_tombo",),
                "permissions": (
                    ("admin", "Vis\xe3o administrativa"),
                    ("control", "Vis\xe3o de Controle"),
                ),
            },
            bases=(models.Model, standard.models.AuditableMixins),
        ),
        migrations.CreateModel(
            name="PatrimonioHistorico",
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
                    "conservacao",
                    models.IntegerField(
                        db_index=True,
                        null=True,
                        choices=[
                            (1, "Novo"),
                            (2, "Bom"),
                            (3, "Regular"),
                            (4, "Inservivel"),
                        ],
                    ),
                ),
                ("utilizacao", models.SmallIntegerField(null=True)),
                (
                    "valor_atual",
                    models.DecimalField(null=True, max_digits=20, decimal_places=6),
                ),
                ("prazo_garantia", models.DateField(null=True)),
                ("vida_util", models.DateField(null=True)),
                ("data_baixa", models.DateField(null=True)),
                ("data_tombo", models.DateField(null=True)),
                ("suspenso", models.NullBooleanField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PreBaixa",
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
                ("memorando", models.CharField(max_length=100)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Sequencia",
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
                ("titulo", models.CharField(unique=True, max_length=100)),
                ("proximo", models.IntegerField(default=1)),
            ],
            options={
                "ordering": ("titulo", "proximo"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Suspensao",
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
                ("data_inicio", models.DateTimeField()),
                ("data_fim", models.DateTimeField(null=True)),
                ("ativo", models.BooleanField(default=True)),
                ("justificativa", models.TextField()),
            ],
            options={
                "ordering": ("-ativo", "-pk"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TabelaAvaliacao",
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
                ("numero", models.IntegerField()),
                ("ano", models.IntegerField()),
                ("data_vigencia", models.DateField()),
                ("data_fim_vigencia", models.DateField(null=True)),
            ],
            options={
                "ordering": ("-data_vigencia",),
            },
            bases=(models.Model, standard.models.AuditableMixins),
        ),
    ]
