# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ("mq", "0003_taskmessages"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="description",
            field=models.CharField(
                default="", max_length=255, verbose_name="Description"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="finished_task",
            field=models.DateTimeField(
                null=True, verbose_name="Finished", db_index=True
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="started_task",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 11, 21, 9, 40, 51, 776456),
                auto_now_add=True,
                verbose_name="Started",
                db_index=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="task",
            name="visualized",
            field=models.BooleanField(default=False, verbose_name="Visualized"),
        ),
        migrations.AlterField(
            model_name="taskmessages",
            name="type_of",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Type", db_index=True
            ),
        ),
    ]
