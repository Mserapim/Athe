# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0009_groupgeneralorgan_groupperson"),
    ]

    operations = [
        migrations.AddField(
            model_name="impressora",
            name="driver",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo da Impressora",
                choices=[(1, "Zebra"), (2, "TSC M240")],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="groupgeneralorgan",
            name="level_access",
            field=models.PositiveSmallIntegerField(verbose_name="Acesso"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="groupperson",
            name="level_access",
            field=models.PositiveSmallIntegerField(verbose_name="Acesso"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="impressora",
            name="host",
            field=models.CharField(max_length=100, verbose_name="Endere\xe7o"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="impressora",
            name="lotacao",
            field=models.ForeignKey(
                verbose_name="Localiza\xe7\xe3o",
                to="rh.Lotacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="impressora",
            name="nome",
            field=models.CharField(max_length=100, verbose_name="Nome"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="impressora",
            name="port",
            field=models.IntegerField(verbose_name="Porta"),
            preserve_default=True,
        ),
    ]
