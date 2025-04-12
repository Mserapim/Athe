# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0008_auto_20161003_1544"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="partlawsuit",
            options={"ordering": ("page_number", "created_at")},
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="page_number",
            field=models.PositiveIntegerField(unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="type_vehicle",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                choices=[
                    (1, "Ve\xedculo Oficial"),
                    (2, "Ve\xedculo Particular"),
                    (3, "Correios ou outro terceiro"),
                ],
            ),
        ),
    ]
