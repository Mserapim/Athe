# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0009_auto_20151201_1213"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="irrffaixa",
            options={"ordering": ["irrf", "limite_inferior"]},
        ),
        migrations.AddField(
            model_name="rraemployee",
            name="factor",
            field=models.DecimalField(
                default=0, verbose_name="Fator", max_digits=8, decimal_places=4
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="folha",
            field=models.ForeignKey(
                related_name="paychecks",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Folha",
                to="gfp.Folha",
            ),
            preserve_default=True,
        ),
    ]
