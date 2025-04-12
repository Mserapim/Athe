# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0004_auto_20150923_0741"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="separate_for_competencies",
            field=models.BooleanField(
                default=True, verbose_name="Separar por compet\xeancias?"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="evento",
            name="separate_for_info_event",
            field=models.BooleanField(default=False, verbose_name="Separar por info?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="evento",
            name="quantidade_max",
            field=models.DecimalField(
                default=0,
                verbose_name="Quantidade m\xe1xima",
                max_digits=10,
                decimal_places=2,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="folhaevento",
            unique_together=set(
                [
                    (
                        "contracheque",
                        "evento",
                        "info",
                        "servidor",
                        "reference_year",
                        "reference_month",
                    )
                ]
            ),
        ),
    ]
