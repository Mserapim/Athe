# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gecap", "0003_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capacitacao",
            name="area_conhecimento",
            field=models.ManyToManyField(
                related_name="capacitacoes", to="gecap.AreaConhecimento"
            ),
        ),
        migrations.AlterField(
            model_name="capacitacao",
            name="promotores",
            field=models.ManyToManyField(
                related_name="capacitacoes", to="rh.OrgaoGeral"
            ),
        ),
    ]
