# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0001_initial"),
        ("mto", "0001_initial"),
        ("contabilidade", "0001_initial"),
        ("eproc", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessoAquisicao",
            fields=[
                (
                    "processo_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="eproc.Processo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "orcamento",
                    models.IntegerField(
                        choices=[
                            (1, "NOTA DE DOTA\xc7\xc3O"),
                            (2, "IDENTIFICA\xc7\xc3O OR\xc7AMENT\xc1RIA"),
                        ]
                    ),
                ),
            ],
            options={},
            bases=("eproc.processo",),
        ),
        migrations.CreateModel(
            name="ProdutoProcesso",
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
                ("quantidade", models.IntegerField()),
                (
                    "valor_unitario_estimado",
                    models.DecimalField(max_digits=16, decimal_places=2),
                ),
                (
                    "valor_unitario_lance",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "valor_unitario_aditivo",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "valor_unitario",
                    models.DecimalField(max_digits=16, decimal_places=2),
                ),
                ("descricao", models.TextField(null=True, blank=True)),
                (
                    "nota_dotacao",
                    models.ManyToManyField(
                        related_name="produtos",
                        null=True,
                        to="compras.NotaDotacao",
                        blank=True,
                    ),
                ),
                (
                    "processo_aquisicao",
                    models.ForeignKey(
                        related_name="produtos",
                        to="compras.ProcessoAquisicao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "produto",
                    models.ForeignKey(
                        related_name="processos",
                        to="contabilidade.Produto",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="produtoprocesso",
            unique_together=set([("produto", "processo_aquisicao")]),
        ),
        migrations.AddField(
            model_name="notadotacao",
            name="fonte_recurso",
            field=models.ForeignKey(
                blank=True,
                to="contabilidade.FonteRecurso",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="notadotacao",
            name="natureza_despesa",
            field=models.ForeignKey(
                to="mto.NaturezaDespesa", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
