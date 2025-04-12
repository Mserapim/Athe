# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
        ("rh", "0002_auto_20150810_1114"),
        ("profile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobprofile",
            name="linked_workplaces",
            field=models.ManyToManyField(
                related_name="in_linked_job_profile", to="rh.Lotacao"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="jobprofile",
            name="permissions",
            field=models.ManyToManyField(
                related_name="in_job_profiles", to="auth.Permission"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="jobprofile",
            name="workplace",
            field=models.ForeignKey(
                related_name="in_job_profiles",
                verbose_name="Lota\xe7\xe3o",
                to="rh.Lotacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
