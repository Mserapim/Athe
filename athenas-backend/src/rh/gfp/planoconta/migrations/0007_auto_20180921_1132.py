# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planoconta", "0006_auto_20161111_0957"),
    ]

    operations = [
        migrations.AddField(
            model_name="planoconta",
            name="equity_note_classification",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="planoconta",
            name="equity_note_item",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="planoconta",
            name="equity_note_operation",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="classificacao_nlc",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="evento_nlc",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="evento_nld",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="finalidade",
            field=models.SmallIntegerField(
                default=1, choices=[(1, "LIQUIDA\xc7\xc3O"), (2, "DESEMBOLSO")]
            ),
        ),
        migrations.AlterField(
            model_name="provisionmanager",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                blank=True,
                verbose_name="Status",
                choices=[
                    (1, "EM PRODU\xc7\xc3O"),
                    (2, "EM ANALISE"),
                    (3, "FECHADO"),
                    (4, "PROCESSADO"),
                ],
            ),
        ),
    ]
