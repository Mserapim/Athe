# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0011_attachment"),
    ]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="member",
            field=models.ForeignKey(
                related_name="attachment",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Membro",
                blank=True,
                to="cif.ControlInformationMember",
                null=True,
            ),
        ),
    ]
