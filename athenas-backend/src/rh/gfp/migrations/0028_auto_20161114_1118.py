# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def updating_old_messages(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    FolhaMensagem = apps.get_model("gfp", "FolhaMensagem")
    print("")
    print("UPDATING FolhaMensagem: ")
    cont = 0

    for fm in FolhaMensagem.objects.exclude(servidor__isnull=True):
        cont += FolhaMensagem.objects.filter(pk=fm.pk).update(
            paycheck=fm.folha.paychecks.get(pensioner=None, servidor=fm.servidor)
        )
    print(cont)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0027_auto_20161111_0957"),
    ]

    operations = [
        migrations.RunPython(updating_old_messages, _null_function),
    ]
