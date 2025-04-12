# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0004_auto_20160211_1143"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dialect",
            options={"ordering": ("dirf", "nome")},
        ),
        migrations.AlterModelOptions(
            name="dirfresumos",
            options={"ordering": ("-ano", "pessoa", "mes")},
        ),
        migrations.AlterModelOptions(
            name="token",
            options={"ordering": ["dialect", "slug"]},
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="declaracao",
            field=models.ForeignKey(
                related_name="demonstrativos",
                default=1,
                to="dirf.Declaracao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="natureza",
            field=models.ForeignKey(
                related_name="demonstrativos",
                default=1,
                to="dirf.NaturezaRendimento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="pessoa_fisica",
            field=models.ForeignKey(
                related_name="dirfs_pessoa_fisica",
                default=1,
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="responsavel",
            field=models.ForeignKey(
                related_name="como_responsavel",
                default=1,
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
    ]
