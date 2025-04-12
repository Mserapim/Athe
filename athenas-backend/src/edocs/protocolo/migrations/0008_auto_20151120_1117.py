# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("protocolo", "0007_auto_20151008_1430"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacao",
            name="reopen_at",
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="movimentacao",
            name="reopen_by",
            field=models.ForeignKey(
                related_name="moviment_reopen",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
            preserve_default=True,
        ),
    ]
