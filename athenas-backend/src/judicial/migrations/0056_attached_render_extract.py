# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0055_dismembermentmultiprocesschunk_generated_lawsuit"),
    ]

    operations = [
        migrations.AddField(
            model_name="attached",
            name="render_extract",
            field=models.BooleanField(default=True),
        ),
    ]
