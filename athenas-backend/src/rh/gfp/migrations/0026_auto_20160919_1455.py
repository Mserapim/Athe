# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0025_auto_20160915_1618"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupevents",
            name="genre_events",
            field=models.ManyToManyField(
                related_name="_groupevents_genre_events_+",
                verbose_name="G\xeaneros",
                to="gfp.GenreEvent",
            ),
        )
    ]
