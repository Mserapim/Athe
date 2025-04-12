# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0026_auto_20160725_1256"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pessoafisica",
            name="renda_familiar",
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="genero",
            field=models.CharField(
                max_length=100, null=True, verbose_name="G\xeanero", blank=True
            ),
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="nacionalidade",
            field=models.CharField(
                max_length=80, null=True, verbose_name="Nacionalidade", blank=True
            ),
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="profissao",
            field=models.CharField(
                max_length=100, null=True, verbose_name="Profiss\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(verbose_name="Tipo Documento"),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Inst\xe2ncia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Entr\xe2ncia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="poder",
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="turno",
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="publication_state",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(verbose_name="Tipo de Publica\xe7\xe3o"),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="veiculo_publicacao",
            field=models.IntegerField(
                null=True, verbose_name="Ve\xedculo Publica\xe7\xe3o", blank=True
            ),
        ),
    ]
