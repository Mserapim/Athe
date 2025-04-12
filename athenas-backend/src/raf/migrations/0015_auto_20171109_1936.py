# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0014_auto_20171018_1501"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="nonproceduralactivities",
            options={
                "ordering": ["-date"],
                "verbose_name": "Atividades n\xe3o procedimentais",
            },
        ),
        migrations.AlterField(
            model_name="conversation",
            name="last_content",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="raf.ConversationContent",
            ),
        ),
    ]
