# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
        ("engine", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobProfile",
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
                (
                    "codename",
                    models.CharField(
                        unique=True,
                        max_length=100,
                        verbose_name="Identificador",
                        db_index=True,
                    ),
                ),
                (
                    "for_leadership",
                    models.BooleanField(default=False, verbose_name="Para chefia"),
                ),
                (
                    "for_workplace",
                    models.BooleanField(
                        default=False, verbose_name="Para lota\xe7\xe3o"
                    ),
                ),
                (
                    "for_work_assignment",
                    models.BooleanField(
                        default=False, verbose_name="Para designa\xe7\xe3o"
                    ),
                ),
                (
                    "features",
                    models.ManyToManyField(
                        related_name="in_job_profiles", to="engine.ControllerPermission"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        related_name="in_job_profiles", to="auth.Group"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
