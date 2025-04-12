# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from rh.gfp.models import PaycheckDifference


def updating_differnces(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Event = apps.get_model("gfp", "Evento")
    # PaycheckDifference = apps.get_model("gfp", "PaycheckDifference")

    ups = Event.objects.filter(automatico=True, config_value="").update(
        config_value="""MEA:{GN}06.VALOR={DV},{GN}06.PATRONAL={DV};\n\
DIF:{GN}01.VALOR={DV},{GN}01.PATRONAL={DV};\n\
DEV:{GN}02.VALOR=-{DV},{GN}02.PATRONAL=-{DV};\n\
ESD:{GN}07.VALOR=-{DV},{GN}07.PATRONAL=-{DV};"""
    )
    print("")
    print("UPDATING Evento.config_value: %s" % ups)
    print("UPDATING PaycheckDifference.status: ")
    cont = 0
    for pd in PaycheckDifference.objects.filter():
        st = pd.status
        pd.save()
        if st != pd.status:
            cont += 1
    print(cont)


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0007_auto_20151021_1130"),
    ]

    operations = [
        migrations.RunPython(updating_differnces),
    ]
