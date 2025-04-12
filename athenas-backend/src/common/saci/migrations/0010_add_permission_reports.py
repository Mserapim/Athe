# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0009_attendance_confidential"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attendance",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Atendimento",
                "permissions": (
                    ("can_sign_attendance", "Pode assinar atendimento"),
                    (
                        "can_generate_reports_all_location",
                        "Pode gerar relat\xf3rio de todos os locais",
                    ),
                ),
            },
        ),
    ]
