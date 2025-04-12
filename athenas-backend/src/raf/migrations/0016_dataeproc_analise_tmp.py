# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0015_auto_20171109_1936"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataeproc",
            name="analise_tmp",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="An\xe1lise",
                choices=[
                    (0, "N\xe3o analisado"),
                    (1, "Processo classificado com sucesso"),
                    (2, "Sem promotoria registrada para o processo"),
                    (3, "N\xe3o encontrou question\xe1rio para o processo"),
                    (4, "N\xe3o encontrou linha para o processo"),
                    (5, "N\xe3o encontrou coluna para o processo"),
                    (6, "Sem classe registrada para o processo"),
                    (7, "Sem assunto registrado para o processo"),
                    (8, "Sem movimento registrado para o processo"),
                ],
            ),
        ),
    ]
