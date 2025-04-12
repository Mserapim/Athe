# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0010_auto_20160222_1059"),
    ]

    operations = [
        migrations.AlterField(
            model_name="groupgeneralorgan",
            name="level_access",
            field=models.PositiveSmallIntegerField(
                verbose_name="Acesso", choices=[(1, "Global"), (2, "Departamental")]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="groupperson",
            name="level_access",
            field=models.PositiveSmallIntegerField(
                verbose_name="Acesso", choices=[(1, "Global"), (2, "Departamental")]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="movimentacao",
            name="child_of",
            field=models.ForeignKey(
                related_name="derivative_for",
                on_delete=django.db.models.deletion.PROTECT,
                to="protocolo.Movimentacao",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
