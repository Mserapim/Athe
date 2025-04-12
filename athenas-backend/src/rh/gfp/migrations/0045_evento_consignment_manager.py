# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_events(apps, schema_editor):
    Evento = apps.get_model("gfp", "Evento")

    ups = Evento.objects.filter(carater__in=[6, 7]).update(consignment_manager=True)
    print("UPDATEDS EVENTS: %d" % ups)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0044_auto_20171019_1231"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.AddField(
            model_name="evento",
            name="consignment_manager",
            field=models.BooleanField(default=False, verbose_name="Gerenciar Consig?"),
        ),
        migrations.RunPython(update_events, _null_function),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
