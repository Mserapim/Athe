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
            name="Application",
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
                ("title", models.CharField(unique=True, max_length=50)),
                ("app_key", models.CharField(max_length=32)),
                ("valid_at", models.DateTimeField(null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserPermission",
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
                ("user_token", models.CharField(max_length=32, blank=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "application",
                    models.ForeignKey(
                        related_name="users",
                        to="ws.Application",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "user",
                    models.ForeignKey(
                        related_name="ws_permissions",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
