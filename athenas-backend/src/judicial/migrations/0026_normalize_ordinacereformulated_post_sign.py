# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
from contrib.middleware import set_current_user


def up_fn(apps, schema_editor):
    from judicial.models import OutCourtLawsuit

    print(" ", end="")

    for lawsuit in OutCourtLawsuit.objects.exclude(
        origin__movimentacoes__passo__gt=0
    ).filter(
        parts__ordinacereformulated__isnull=False,
        origin__isnull=False,
        number_lawsuit__isnull=False,
    ):
        ordinace = lawsuit.parts.get(ordinacereformulated__isnull=False)
        if ordinace.signed_by:
            current_moviment = lawsuit.origin.movimentacoes.last()
            old_fn = current_moviment.validate_possession_for_do_send

            def empty_fn(*a, **k):
                pass

            current_moviment.validate_possession_for_do_send = empty_fn

            set_current_user(ordinace.signed_by)
            lawsuit.send_to(to=lawsuit.location, force_current=current_moviment)
            set_current_user(None)

            current_moviment.validate_possession_for_do_send = old_fn
            print("\033[33m+\033[0m", end="")
        else:
            print("\033[33m~\033[0m", end="")
        sys.stdout.flush()

    print("")


def down_fn(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0025_update_templates"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
