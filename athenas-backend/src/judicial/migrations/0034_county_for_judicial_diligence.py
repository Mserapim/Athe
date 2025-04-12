# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models


def pp(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def up(apps, schema_editor):
    from judicial.models import County

    JudicialDiligence = apps.get_model("judicial.JudicialDiligence")

    pp(" ", end="")
    for jd in JudicialDiligence.objects.filter(county=None).filter(
        delivery_status__in=(2, 3, 4, 7)
    ):
        if (
            jd.who.address.exists()
            and County.objects.filter(
                locations=jd.who.address.values("municipio")
            ).exists()
        ):
            JudicialDiligence.objects.filter(pk=jd.pk).update(
                county=County.objects.filter(
                    locations=jd.who.address.values("municipio")
                ).first()
            )
            pp("\033[1m\033[33m+\033[0m", end="")
        else:
            pp("!(%s)" % jd.formated_number, end="")


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0033_denunciation_attachments_regression"),
    ]

    operations = [migrations.RunPython(up, down)]
