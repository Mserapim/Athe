# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="arquivo",
            name="group",
            field=models.ForeignKey(
                blank=True, to="rh.Lotacao", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="arquivo",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="arquivo",
            unique_together=set([("file", "user")]),
        ),
    ]
