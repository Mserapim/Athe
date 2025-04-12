# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0046_bankingconvenant"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bankingconvenant",
            options={"ordering": ("bank__numero", "identification")},
        ),
        migrations.RenameField(
            model_name="transparencychoice",
            old_name="active",
            new_name="active1",
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="servidor",
            field=models.ForeignKey(
                related_name="paychecks",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Servidor",
                to="rh.Servidor",
            ),
        ),
        migrations.AlterField(
            model_name="contrachequepensionista",
            name="contracheque_servidor",
            field=models.ForeignKey(
                related_name="paychecks",
                verbose_name="Contrachque",
                to="gfp.ContraCheque",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                null=True, verbose_name="Portal Transpar\xeancia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="source_differences",
            field=models.BooleanField(
                default=False, verbose_name="Gestor de diferen\xc3\xa7as?"
            ),
        ),
        migrations.AlterField(
            model_name="rra",
            name="slug",
            field=models.SlugField(verbose_name="Identifica\xe7\xe3o", blank=True),
        ),
    ]
