# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("poll", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AllowedList",
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
                (
                    "allowed_users",
                    models.ManyToManyField(
                        related_name="safe_poll_allowed_lists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="poll",
            name="updating_allowed_list",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="allowedlist",
            name="poll",
            field=models.OneToOneField(
                related_name="allowed_list",
                null=True,
                to="poll.Poll",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
