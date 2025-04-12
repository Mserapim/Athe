# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0006_auto_20160216_0920"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avaliacao",
            name="ano",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="ate",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="data_execucao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="de",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="executor",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="mes",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="numero",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="tabela",
            field=models.ForeignKey(
                related_name="avaliacoes",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.TabelaAvaliacao",
            ),
        ),
        migrations.AlterField(
            model_name="baixaitem",
            name="observacao",
            field=models.TextField(default="", blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="conta",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.Conta",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="data_compra",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="data_nota",
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="descricao",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="empenho",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="contabilidade.NE",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="execucao_orcamentaria",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                db_index=True,
                blank=True,
                choices=[
                    (1, "DEO - Dependente da Execu\xe7\xe3o Or\xe7ament\xe1ria"),
                    (2, "IEO - Independente da Execu\xe7\xe3o Or\xe7ament\xe1ria"),
                    (3, "DOA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="fornecedor",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Pessoa",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="por",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="processo",
            field=models.CharField(db_index=True, max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="respondido_por",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="respondido_quando",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="criticarnotaentrada",
            name="resposta",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="especie",
            name="codigo_cache",
            field=models.CharField(db_index=True, max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="grupocontabil",
            name="cache_number",
            field=models.CharField(
                db_index=True, unique=True, max_length=10, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="grupocontabil",
            name="contabil_classification",
            field=models.ForeignKey(
                related_name="groups",
                blank=True,
                to="patrimonio.ClassificacaoContabil",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="itemavaliacao",
            name="especie",
            field=models.ForeignKey(
                related_name="itens_avaliacao",
                blank=True,
                to="patrimonio.Especie",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="localizacao",
            name="dentro_de",
            field=models.ForeignKey(
                related_name="sub_espacos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.Localizacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="localizacao",
            name="folder_index",
            field=models.CharField(db_index=True, max_length=45, blank=True),
        ),
        migrations.AlterField(
            model_name="localizacao",
            name="lotacao_relacionada",
            field=models.ForeignKey(
                related_name="localizacoes_patrimoniais",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="localizacao",
            name="path_cache",
            field=models.CharField(
                db_index=True, max_length=300, null=True, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="ano",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="destino",
            field=models.ForeignKey(
                related_name="como_destino_em_movimentos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.Localizacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="movimentado",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="movimentado_por",
            field=models.ForeignKey(
                related_name="movimentos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="numero",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="numero_cache",
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="origem",
            field=models.ForeignKey(
                related_name="como_origem_em_movimentos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.Localizacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="recebido",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="recebido_por",
            field=models.ForeignKey(
                related_name="recebimentos",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="responsavel_destino",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Servidor",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="responsavel_origem",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Servidor",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="validado",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="movimento",
            name="validado_por",
            field=models.ForeignKey(
                related_name="validacoes",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="ano",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="cache_numero",
            field=models.CharField(db_index=True, max_length=10, blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="cache_type",
            field=models.CharField(db_index=True, max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="data_baixa",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="data_liquidacao",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="liquidacao",
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="numero",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="pre_baixa",
            field=models.ForeignKey(
                related_name="notas_baixa",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.PreBaixa",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="cache_type",
            field=models.CharField(db_index=True, max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="data_compra",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="data_liquidacao",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="data_nota",
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="empenho",
            field=models.ForeignKey(
                related_name="movimentos_entrada_patrimonio",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="contabilidade.NE",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="formated_number",
            field=models.CharField(db_index=True, max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="liquidacao",
            field=models.CharField(db_index=True, max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="note_number",
            field=models.SmallIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="note_year",
            field=models.SmallIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="processo",
            field=models.CharField(db_index=True, max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="tombado",
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaentrada",
            name="tombado_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="aberto_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="data_fim",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="data_inicio",
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="fechado_por",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="item_entrada",
            field=models.ForeignKey(
                related_name="suspensoes",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.ItemEntrada",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="suspensao",
            name="justificativa",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="tabelaavaliacao",
            name="ano",
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="tabelaavaliacao",
            name="data_fim_vigencia",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="tabelaavaliacao",
            name="numero",
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="tabelaavaliacao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
    ]
