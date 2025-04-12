# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0027_denunciation_attachments"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attached",
            options={"ordering": ("file_descriptor__created",)},
        ),
        migrations.AddField(
            model_name="attached",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 5, 25, 9, 49, 37, 782525),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="attached",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=1,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="attached",
            name="modified_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 5, 25, 9, 49, 55, 856611), auto_now=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="attached",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=1,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
