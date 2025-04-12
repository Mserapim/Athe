# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0006_auto_20160219_0925"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="block_change",
            field=models.BooleanField(
                default=False,
                verbose_name="Bloqueia a altera\xe7\xe3o da informa\xe7\xe3o",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="code",
            field=models.ForeignKey(
                related_name="debtsencumbrances",
                verbose_name="C\xf3digo",
                to="cif.CodeDebtsEncumbrances",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="member",
            field=models.ForeignKey(
                related_name="debtsencumbrances",
                verbose_name="Membro",
                to="cif.ControlInformationMember",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="code",
            field=models.ForeignKey(
                related_name="property",
                verbose_name="C\xf3digo",
                to="cif.CodeProperty",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="country",
            field=models.ForeignKey(
                verbose_name="Pa\xeds",
                to="rh.Pais",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="member",
            field=models.ForeignKey(
                related_name="property",
                verbose_name="Membro",
                to="cif.ControlInformationMember",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
