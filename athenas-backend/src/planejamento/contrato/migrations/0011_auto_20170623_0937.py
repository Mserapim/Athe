# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from planejamento.contrato.models import ValorContrato
from django.db import migrations


def fix_agree_48_2016(apps, schema_editor):
    ValorContrato.objects.filter(
        contrato__numero__icontains="48/2016",
        contrato__numero_processo__icontains="00192",
        ordem=2,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0010_auto_20170525_1426"),
    ]

    operations = [migrations.RunPython(fix_agree_48_2016)]
