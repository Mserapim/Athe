# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0005_regularwebuser_password_expires"),
    ]

    operations = [
        migrations.AlterField(
            model_name="regularwebuser",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
