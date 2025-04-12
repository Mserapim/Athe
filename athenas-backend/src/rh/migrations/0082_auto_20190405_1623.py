# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0081_auto_20190403_1834"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="lotacao",
            options={
                "ordering": ["nome"],
                "verbose_name": "Lota\xe7\xe3o",
                "permissions": (
                    (
                        "can_allow_lawsuit",
                        "Pode habilitar tramita\xe7\xe3o de procedimentos extrajudiciais",
                    ),
                ),
            },
        )
    ]
