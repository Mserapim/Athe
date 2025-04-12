# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PasswordChangeRequest",
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
                ("key", models.CharField(max_length=64, db_index=True)),
                ("valid", models.BooleanField(default=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        related_name="password_change_requests",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
        ),
    ]
