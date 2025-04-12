# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0024_auto_20160616_1753"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servidorlotacao",
            name="anotacao_geral_lotacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="rh.AnotacaoGeral",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="lotacao",
            field=models.ForeignKey(
                related_name="servidores_lotacao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Lota\xe7\xe3o/Designa\xe7\xe3o",
                blank=True,
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="movimentacao_posse",
            field=models.ForeignKey(
                related_name="lotacoes",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.MovimentacaoPosse",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="publicacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="servidor",
            field=models.ForeignKey(
                related_name="servidor_lotacao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Servidor",
                to="rh.Servidor",
            ),
        ),
    ]
