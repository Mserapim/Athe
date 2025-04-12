# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estagio", "0003_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="posse_servidor",
            field=models.OneToOneField(
                related_name="estagio_probatorio",
                to="rh.MovimentacaoPosse",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="status",
            field=models.CharField(
                default=1,
                max_length=1,
                choices=[
                    (1, "Em Andamento"),
                    (2, "Aguardando Homologa\xe7\xe3o"),
                    (3, "Julgamento Comiss\xe3o"),
                    (4, "Homologado"),
                ],
            ),
        ),
    ]
