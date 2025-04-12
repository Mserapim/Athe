# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0003_auto_20150817_1114"),
    ]

    operations = [
        migrations.CreateModel(
            name="GrupoContabil",
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
                ("codigo_consolidacao", models.IntegerField()),
                ("codigo_classificacao", models.IntegerField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name="especie",
            options={
                "ordering": ("codigo", "titulo"),
                "permissions": (("mov_grupoespecie", "Movimentar Grupo Especie"),),
            },
        ),
        migrations.AddField(
            model_name="grupoespecie",
            name="grupo_contabil",
            field=models.ForeignKey(
                related_name="grupo_especies",
                on_delete=django.db.models.deletion.PROTECT,
                to="patrimonio.GrupoContabil",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="especie",
            name="codigo",
            field=models.SmallIntegerField(unique=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="grupoespecie",
            name="codigo",
            field=models.SmallIntegerField(unique=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="suspenso_tipo",
            field=models.SmallIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="patrimoniohistorico",
            name="suspenso_tipo",
            field=models.SmallIntegerField(default=1),
            preserve_default=True,
        ),
    ]
