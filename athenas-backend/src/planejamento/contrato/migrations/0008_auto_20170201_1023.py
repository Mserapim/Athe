# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from planejamento.contrato.models import Medicao
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

set_current_user(User.objects.get(username="athenas"))
log = getLogger(__name__)


def copy_to_tempst(apps, schema_editor):
    for m in Medicao.objects.filter():
        Medicao.objects.filter(id=m.id).update(tempst=int(m.status))
    log.debug("Backup do campo 'status' para 'tempst' realizada com sucesso")


def restore_from_tempst(apps, schema_editor):
    for m in Medicao.objects.filter():
        Medicao.objects.filter(id=m.id).update(status=m.tempst)
    log.debug("Restauracao do campo 'tempst' para 'status' realizada com sucesso")


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0007_auto_20170126_1744"),
    ]

    operations = [
        migrations.RunPython(copy_to_tempst),
        migrations.RemoveField(
            model_name="medicao",
            name="status",
        ),
        migrations.AddField(
            model_name="medicao",
            name="status",
            field=models.IntegerField(
                default=1,
                choices=[(1, "Aguardando Pagamento"), (2, "Pago"), (3, "N\xe3o pago")],
            ),
        ),
        migrations.RunPython(restore_from_tempst),
    ]
