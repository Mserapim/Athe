# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0018_auto_20171113_1824"),
    ]

    operations = [
        migrations.AddField(
            model_name="subitem",
            name="productivity",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Produtividade",
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Fator I"),
                    (3, "Fator II"),
                    (4, "Fator III"),
                    (5, "Fator IV"),
                ],
            ),
        ),
    ]
