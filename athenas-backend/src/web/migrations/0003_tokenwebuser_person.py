# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0004_auto_20150911_1731"),
        ("web", "0002_auto_20150609_1013"),
    ]

    operations = [
        migrations.AddField(
            model_name="tokenwebuser",
            name="person",
            field=models.OneToOneField(
                related_name="anonymous_web_user",
                null=True,
                to="rh.AnonymousPerson",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
