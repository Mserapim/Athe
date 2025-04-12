# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0013_auto_20161201_0800"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="only_notice",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="dilationperiod",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                ],
            ),
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
                    (5, "\xd3rg\xe3o P\xfablico"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="manifestation",
            name="who_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                    (5, "\xd3rg\xe3o P\xfablico"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="partlawsuitaccess",
            name="motivation",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Envolve menor indefeso"),
                    (2, "Quebra de sigilo banc\xe1rio"),
                    (3, "Preserva\xe7\xe3o da intimidade"),
                ],
            ),
        ),
    ]
