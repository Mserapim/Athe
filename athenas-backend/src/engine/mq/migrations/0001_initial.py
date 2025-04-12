# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
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
                ("uuid", models.CharField(max_length=36, db_index=True)),
                ("state", models.CharField(default="initializing", max_length=15)),
                ("message", models.TextField()),
                ("data", models.TextField()),
                ("params", models.TextField(default="{}")),
                (
                    "owner",
                    models.ForeignKey(
                        related_name="my_tasks_in_mq",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-pk",),
            },
            bases=(models.Model,),
        ),
    ]
