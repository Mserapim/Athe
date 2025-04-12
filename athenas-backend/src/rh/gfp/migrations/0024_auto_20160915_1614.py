# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0023_auto_20160906_1417"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transparencychoice",
            name="type_event",
        )
    ]
