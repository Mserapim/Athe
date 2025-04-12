# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0040_populate_orgaogeral_numero"),
    ]

    operations = [
        migrations.AddField(
            model_name="lotacao",
            name="orgao_arquimedes",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
