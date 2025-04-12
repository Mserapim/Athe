# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0001_initial"),
        ("dirf", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="token",
            name="eventos",
            field=models.ManyToManyField(related_name="as_token", to="gfp.Evento"),
            preserve_default=True,
        ),
    ]
