# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0015_interested"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="interested",
            options={"ordering": ("-direct", "person")},
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="title",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="rejection_fact_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "N\xe3o presente a legitimidade do MP"),
                    (
                        2,
                        "O fato n\xe3o constitui viola\xe7\xe3o de direito e interesses difuso",
                    ),
                    (3, "O fato j\xe1 se encontrar solucionado"),
                    (4, "O fato j\xe1 \xe9 objeto de investiga\xe7\xe3o ou ACP"),
                ]
            ),
        ),
    ]
