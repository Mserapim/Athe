# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations


def pp(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def up(apps, schema_editor):
    from judicial.models import OutCourtLawsuit

    pp(" ", end="")
    for lawsuit in OutCourtLawsuit.objects.filter(removed_at=None):
        pp(
            "%s - %s \n" % (lawsuit.cache_number, lawsuit.last_part_lawsuit_signed),
            end="",
        )


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0038_outcourtlawsuit_last_part_lawsuit"),
    ]

    operations = [migrations.RunPython(up, down)]
