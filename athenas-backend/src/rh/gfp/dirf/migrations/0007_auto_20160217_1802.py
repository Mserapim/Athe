# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0013_auto_20160217_1748"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dirf", "0006_auto_20160212_0807"),
    ]

    operations = [
        migrations.AddField(
            model_name="demonstrativo",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 2, 17, 18, 2, 3, 596199),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=845,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="modified_at",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 2, 17, 18, 2, 14, 253404), auto_now=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=845,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="rra",
            field=models.ForeignKey(
                related_name="demonstrativos",
                to="gfp.RRA",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
