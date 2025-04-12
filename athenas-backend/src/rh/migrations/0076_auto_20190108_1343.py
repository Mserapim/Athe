# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0075_datamigration_organizational_classification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cargo",
            name="cbo",
            field=models.ForeignKey(
                blank=True, to="rh.Cbo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="configjobposition",
            name="cbo",
            field=models.ForeignKey(
                to="rh.Cbo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="configjobposition",
            name="code",
            field=models.CharField(
                default="", max_length=12, verbose_name="C\xf3digo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="lotacao",
            name="organizational_classification",
            field=models.IntegerField(
                default=1,
                verbose_name="Classifica\xe7\xe3o do Organograma",
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Primeira Entr\xe2ncia"),
                    (3, "Segunda Entrancia"),
                    (4, "Sede Terceira Entrancia"),
                    (5, "Terceira Entrancia"),
                    (6, "Sede  & Promotoria"),
                    (
                        7,
                        "\xd3rg\xe3os de Administra\xe7\xe3o Superior e Execu\xe7\xe3o",
                    ),
                    (
                        8,
                        "\xd3rg\xe3os de Administra\xe7\xe3o Superior e Execu\xe7\xe3o Nivel 2",
                    ),
                    (9, "Org\xe3o Auxiliares - Diretoria Geral"),
                    (10, "Org\xe3o Auxiliares - Diretoria Geral  Nivel 2"),
                    (11, "Primeira Entr\xe2ncia N\xedvel 2"),
                    (12, "Segunda Entrancia N\xedvel 2"),
                    (13, "Org\xe3o Auxiliares - Diretoria Geral  Nivel 3"),
                    (14, "Org\xe3o Auxiliares - Diretoria Geral  Nivel 4"),
                ],
            ),
        ),
    ]
