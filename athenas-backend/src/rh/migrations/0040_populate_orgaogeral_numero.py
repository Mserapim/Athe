# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def igeprev_code_generator(cls):
    code = 1
    general_organs = cls.objects.filter().exclude(codigo_igeprev=None)
    if general_organs.exists():
        code = general_organs.order_by("-codigo_igeprev")[0].codigo_igeprev
    while cls.objects.filter(codigo_igeprev=code).exists():
        code += 1
    return code


def update_general_organ(apps, schema_editor):

    OrgaoGeral = apps.get_model("rh", "OrgaoGeral")
    print("""Populando campo código igeprev de Órgão Geral...""")

    for og in OrgaoGeral.objects.filter(codigo_igeprev=None):
        og.codigo_igeprev = (
            igeprev_code_generator(OrgaoGeral)
            if not og.codigo_igeprev
            else og.codigo_igeprev
        )
        og.save()

    print("""Finalizado.""")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0039_auto_20170213_1757"),
    ]

    operations = [migrations.RunPython(update_general_organ)]
