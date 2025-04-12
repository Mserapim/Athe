# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0003_auto_20151014_1609"),
        ("mq", "0002_auto_20151204_0806"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskMessages",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("message", models.CharField(max_length=400, verbose_name="Message")),
                (
                    "type_of",
                    models.PositiveSmallIntegerField(
                        default=1,
                        db_index=True,
                        verbose_name="Type",
                        choices=[(1, "INFO"), (2, "WARN"), (3, "ERROR")],
                    ),
                ),
                (
                    "file_ged",
                    models.ForeignKey(
                        related_name="mq_tasks_messages",
                        verbose_name="Arquivo",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "tasker",
                    models.ForeignKey(
                        related_name="messages",
                        verbose_name="Task",
                        to="mq.Task",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("id",),
            },
        ),
    ]
