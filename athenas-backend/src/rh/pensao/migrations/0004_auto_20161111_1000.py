# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations


def updating_pensions(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Pension = apps.get_model("pensao", "Pensao")
    Event = apps.get_model("gfp", "Evento")
    print("")
    print("UPDATING Pensao: ", end=" ")
    cont = 0

    for p in Pension.objects.all():
        if hasattr(p, "pensaoalimenticia"):
            p.event_employee = Event.objects.get(numero="70100")
            p.type_of_pension = 1
            p1 = p.pensaoalimenticia
        else:
            p.event_employee = Event.objects.get(numero="70500")
            p.type_of_pension = 2
            p1 = p.pensaomorte

        p.event_pensioner = Event.objects.get(numero="70600")
        for pe in p1.eventos.all():
            if pe.evento not in p.events.all():
                p.events.add(pe.evento)
        p.save()
        cont += 1
    print(cont)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pensao", "0003_auto_20161111_0959"),
    ]

    operations = [
        migrations.RunPython(updating_pensions, _null_function),
    ]
