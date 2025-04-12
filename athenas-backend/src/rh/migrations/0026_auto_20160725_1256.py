# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0025_auto_20160711_1502"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orgaogeral",
            name="endereco",
        ),
        migrations.RemoveField(
            model_name="orgaogeral",
            name="telefone",
        ),
        migrations.RemoveField(
            model_name="pessoa",
            name="endereco",
        ),
        migrations.RemoveField(
            model_name="pessoa",
            name="telefone",
        ),
    ]
