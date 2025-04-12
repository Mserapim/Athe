# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0008_auto_20160510_1430"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="member",
            field=models.ForeignKey(
                related_name="address",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Membro",
                to="cif.ControlInformationMember",
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="member",
            field=models.ForeignKey(
                related_name="debtsencumbrances",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Membro",
                blank=True,
                to="cif.ControlInformationMember",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="member",
            field=models.ForeignKey(
                related_name="property",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Membro",
                blank=True,
                to="cif.ControlInformationMember",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="member",
            field=models.ForeignKey(
                related_name="teaching",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Membro",
                to="cif.ControlInformationMember",
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="schedule",
            field=models.ManyToManyField(
                related_name="teaching", verbose_name="Hor\xe1rios", to="cif.Schedule"
            ),
        ),
    ]
