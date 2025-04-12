# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0009_dataeproc_instancia"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activityadjustment",
            options={
                "ordering": ["created_at"],
                "verbose_name": "Ajuste de Atividade",
                "permissions": (
                    ("can_sign_adjustment", "Pode aceitar/rejeitar pedido de ajuste"),
                ),
            },
        ),
    ]
