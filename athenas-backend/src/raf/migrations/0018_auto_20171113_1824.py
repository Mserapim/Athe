# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0017_remove_dataeproc_analise"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dataeproc",
            old_name="analise_tmp",
            new_name="analise",
        ),
    ]
