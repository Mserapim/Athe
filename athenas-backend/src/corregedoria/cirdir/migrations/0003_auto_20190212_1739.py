# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cirdir", "0002_auto_20190201_0012"),
    ]

    operations = [
        migrations.RenameField(
            model_name="controlinformation",
            old_name="close_date_debts",
            new_name="close_date_debits",
        ),
        migrations.RenameField(
            model_name="controlinformation",
            old_name="closed_debts",
            new_name="closed_debits",
        ),
        migrations.RenameField(
            model_name="controlinformation",
            old_name="open_date_debts",
            new_name="open_date_debits",
        ),
    ]
