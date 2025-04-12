# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0022_auto_20170310_0903"),
    ]

    operations = [
        migrations.AddField(
            model_name="attached",
            name="published_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="attached",
            name="published_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
