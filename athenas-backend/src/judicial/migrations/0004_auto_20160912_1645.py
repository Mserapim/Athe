# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0003_auto_20160905_1608"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attached",
            name="title",
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.RemoveField(
            model_name="partlawsuit",
            name="shared_with_lawsuit",
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="shared_with_lawsuit",
            field=models.ManyToManyField(
                related_name="shared_parts", to="judicial.OutCourtLawsuit"
            ),
        ),
    ]
