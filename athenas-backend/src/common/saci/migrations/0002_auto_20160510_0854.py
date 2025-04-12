# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendance",
            name="content",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="department",
            field=models.ForeignKey(
                related_name="in_attendance_department",
                verbose_name="departamento",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="destination",
            field=models.ForeignKey(
                related_name="in_attendance_destination",
                verbose_name="destina\xe7\xe3o",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="protocol",
            field=models.ForeignKey(
                related_name="in_attendance_protocol",
                verbose_name="protocolo",
                blank=True,
                to="protocolo.Protocolo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="represented",
            field=models.ForeignKey(
                related_name="in_attendance_represented",
                verbose_name="representado",
                blank=True,
                to="rh.Pessoa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="signed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="signed_content",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="story",
            field=models.TextField(
                null=True, verbose_name="relato do cidad\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="subject",
            field=models.CharField(
                max_length=200, null=True, verbose_name="assunto", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="typology",
            field=models.ForeignKey(
                related_name="in_attendance",
                verbose_name="Tipologia",
                blank=True,
                to="saci.Typology",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
