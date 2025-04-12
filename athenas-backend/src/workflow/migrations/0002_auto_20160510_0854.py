# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vertex",
            name="vertices",
            field=models.ManyToManyField(
                related_name="backward_vertices",
                through="workflow.Edge",
                to="workflow.Vertex",
            ),
        ),
    ]
