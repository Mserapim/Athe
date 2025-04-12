# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0030_auto_20160808_1526"),
        ("saci", "0002_auto_20160510_0854"),
    ]

    operations = [
        migrations.CreateModel(
            name="Step",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("annotation", models.TextField(verbose_name="Anota\xe7\xe3o")),
            ],
            options={
                "ordering": ["created_at"],
                "verbose_name": "Passo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="department",
            field=models.ForeignKey(
                related_name="in_attendance_department",
                verbose_name="departamento",
                to="rh.OrgaoGeral",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="protocol",
            field=models.OneToOneField(
                null=True,
                blank=True,
                to="protocolo.Protocolo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attendance",
            name="subject",
            field=models.CharField(max_length=200, verbose_name="assunto"),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="typology",
            field=models.ForeignKey(
                related_name="in_attendance",
                verbose_name="Tipologia",
                to="saci.Typology",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="step",
            name="attendance",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="steps", to="saci.Attendance", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="step",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="step",
            name="destination",
            field=models.ForeignKey(
                related_name="step_destination",
                verbose_name="Destino",
                to="rh.OrgaoGeral",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="step",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="step",
            name="origin",
            field=models.ForeignKey(
                related_name="step_origin",
                verbose_name="Origem",
                to="rh.OrgaoGeral",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
