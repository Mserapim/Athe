# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0020_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pessoajuridica",
            name="razao_social",
            field=models.CharField(
                max_length=255, verbose_name="Raz\xe3o Social", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="confirm_publication_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="confirm_publication_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="document",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="sent_to_publication_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="sent_to_publication_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="publicconcurrence",
            name="number_mpe",
            field=models.CharField(max_length=4, verbose_name="N\xfamero MPE"),
        ),
        migrations.AlterField(
            model_name="publicconcurrence",
            name="number_tce",
            field=models.CharField(
                max_length=20, null=True, verbose_name="N\xfamero TCE", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="publicconcurrence",
            name="year_mpe",
            field=models.CharField(max_length=4, verbose_name="Ano MPE"),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="data_vigencia",
            field=models.DateField(
                null=True, verbose_name="Data Vig\xeancia", blank=True
            ),
        ),
    ]
