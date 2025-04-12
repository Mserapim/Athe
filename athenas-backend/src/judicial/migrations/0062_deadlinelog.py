# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0061_create_event_control"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeadlineLog",
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
                ("observation", models.TextField(blank=True)),
                ("days", models.SmallIntegerField()),
                ("executed_at", models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name="outcourtlawsuit",
            options={
                "ordering": ("remaining_days",),
                "permissions": (
                    ("outcourtlawsuitadmin", "Pode administrar os OutCourtLawsuit"),
                ),
            },
        ),
        migrations.AddField(
            model_name="deadlinelog",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.OutCourtLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="deadlinelog",
            name="manifestation",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.Manifestation",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
