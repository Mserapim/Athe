# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0015_notificationhistory_responded"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notificationhistory",
            options={
                "verbose_name": "Hist\xf3rio de notifica\xe7\xf5es por atraso.",
                "permissions": (
                    (
                        "notification_deadline_monitor",
                        "Monitor de Notifica\xe7\xe3o Vencidas",
                    ),
                ),
            },
        ),
    ]
