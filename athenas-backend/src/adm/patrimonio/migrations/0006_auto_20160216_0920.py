# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0005_auto_20151127_1450"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaixaMudancaClassificacao",
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
            name="ClassificacaoContabil",
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
                ("title", models.CharField(max_length=60)),
                ("classfication", models.CharField(max_length=20, db_index=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="grupocontabil",
            name="contabil_classification",
            field=models.ForeignKey(
                related_name="groups",
                to="patrimonio.ClassificacaoContabil",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
