# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tac", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activity",
            options={
                "ordering": ("created_at",),
                "permissions": (("activity_tac", "Vis\xe3o Atividade da TAC"),),
            },
        ),
        migrations.AddField(
            model_name="activity",
            name="deadline",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="activity",
            name="realized",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (0, "Em andamento"),
                    (1, "Cumprido"),
                    (2, "N\xe3o cumprido"),
                    (3, "Executado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="activity",
            name="time_type",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (0, "N\xe3o informado"),
                    (1, "em dias"),
                    (2, "em m\xeases"),
                    (3, "em anos"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="activityhistory",
            name="realized",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (0, "Em andamento"),
                    (1, "Cumprido"),
                    (2, "N\xe3o cumprido"),
                    (3, "Executado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="activityhistory",
            name="time_type",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (0, "N\xe3o informado"),
                    (1, "em dias"),
                    (2, "em m\xeases"),
                    (3, "em anos"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="accepted",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (0, "N\xe3o informado"),
                    (1, "Cumprido"),
                    (2, "N\xe3o cumprido"),
                ],
            ),
        ),
    ]
