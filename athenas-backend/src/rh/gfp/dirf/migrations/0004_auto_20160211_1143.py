# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from standard.models import Configuration


def update_demonstrativo_defauls(apps, schema_editor):
    cfg = Configuration.get_or_create("gfp")

    Demonstrativo = apps.get_model("dirf", "Demonstrativo")
    print("")
    count = Demonstrativo.objects.filter(declaracao=None).count()
    Demonstrativo.objects.filter(declaracao=None).delete()
    print("DELETING Demonstrativo without declaracao_id (%d) OK" % count)

    count = Demonstrativo.objects.filter(pessoa_fisica=None).count()
    for d in Demonstrativo.objects.filter(pessoa_fisica=None):
        Demonstrativo.objects.filter(pk=d.pk).update(
            pessoa_fisica=d.servidor.pessoa_fisica
        )
    print("UPDATING demonstrativo with pessoa_fisica=None (%d) OK" % count)

    count = Demonstrativo.objects.filter(responsavel=None).count()
    Demonstrativo.objects.filter(responsavel=None).update(
        responsavel=int(cfg.get("responsavel_gfp"))
    )
    print("UPDATING demonstrativo with responsavel=None (%d)" % count)


def null_method(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0003_auto_20150810_1114"),
    ]

    operations = [
        migrations.RunPython(update_demonstrativo_defauls, null_method),
    ]
