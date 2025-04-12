# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def updatedata(apps, schema_editor):
    # from rh.models import User
    from django.contrib.auth.models import User
    from contrib.middleware import set_current_user

    set_current_user(User.objects.get(username="athenas"))

    from edocs.protocolo.models import Protocolo

    for p in Protocolo.objects.filter(com_workflow=True):
        p.movimentacoes.filter().update(with_workflow=True)


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0016_auto_20180109_1016"),
    ]

    operations = [migrations.RunPython(updatedata)]
