# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0003_tokenwebuser_person"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pollconditions",
            name="polls",
        ),
        migrations.DeleteModel(
            name="PollConditions",
        ),
        migrations.RemoveField(
            model_name="poll",
            name="restricted",
        ),
        migrations.RemoveField(
            model_name="poll",
            name="users_who_voted",
        ),
    ]
