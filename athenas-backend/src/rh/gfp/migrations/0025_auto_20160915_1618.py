# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0024_auto_20160915_1614"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupEvents",
            fields=[
                (
                    "transparencychoice_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gfp.TransparencyChoice",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "type_event",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[("D", "D\xc3\x89BITO"), ("C", "CR\xc3\x89DITO")],
                    ),
                ),
                (
                    "events",
                    models.ManyToManyField(
                        related_name="_groupevents_events_+",
                        verbose_name="Eventos",
                        to="gfp.Evento",
                    ),
                ),
            ],
            bases=("gfp.transparencychoice",),
        )
    ]
