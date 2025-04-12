# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


def up(apps, schema_editor):
    Lawsuit = apps.get_model("judicial", "OutCourtLawsuit")
    Interested = apps.get_model("judicial", "Interested")
    ConnectionLawsuit = apps.get_model("judicial", "ConnectionLawsuit")

    print(" ", end="")

    for lawsuit in Lawsuit.objects.filter():
        if not Interested.objects.filter(
            lawsuit=lawsuit, person=lawsuit.origin.interessado
        ).exists():
            Interested(
                direct=True,
                lawsuit=lawsuit,
                person=lawsuit.origin.interessado,
                created_by=lawsuit.origin.created_by,
                created_at=lawsuit.origin.created_at,
                modified_by=lawsuit.origin.modified_by,
                modified_at=lawsuit.origin.modified_at,
            ).save()

        print("\033[1m\033[32m+\033[0m", end="")

    for connection in ConnectionLawsuit.objects.exclude(signed_by=None):
        lawsuit = connection.lawsuit
        connected = connection.lawsuit_connected

        query = Interested.objects.filter(lawsuit=connected)
        for secundary in query.filter():
            if not Interested.objects.filter(
                lawsuit=lawsuit, person=secundary.person
            ).exists():
                Interested(
                    direct=True,
                    lawsuit=lawsuit,
                    person=secundary.person,
                    created_by=secundary.created_by,
                    created_at=secundary.created_at,
                    modified_by=secundary.modified_by,
                    modified_at=secundary.modified_at,
                ).save()
                print("\033[1m\033[33m+\033[0m", end="")


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0018_auto_20170118_1031"),
    ]

    operations = [migrations.RunPython(up, down)]
