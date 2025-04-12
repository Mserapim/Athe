# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0006_auto_20160923_0807"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                    (6, "Entrega pelo \xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="diligence_file",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="who_type",
            field=models.SmallIntegerField(
                blank=True,
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
    ]
