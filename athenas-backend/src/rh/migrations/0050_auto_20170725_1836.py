# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0049_auto_20170725_1043"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacaoposse",
            name="publication_exercise",
            field=models.ForeignKey(
                related_name="possessions_publication_exercise",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Publica\xe7\xe3o de Exerc\xedcio",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="publication_possession",
            field=models.ForeignKey(
                related_name="possessions_publication_possession",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Publica\xe7\xe3o de Posse",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
    ]
