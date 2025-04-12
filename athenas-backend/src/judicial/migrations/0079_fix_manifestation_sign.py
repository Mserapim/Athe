# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from contrib.middleware import set_current_user
from contrib.utils import person_from_user
from django.db import transaction
from django.db import migrations, models
from judicial.models import AttachedDocument, Manifestation, ManifestationLegalSign


def log(message, end="\n", *args, **kwargs):
    output = message % args
    output = output % kwargs

    sys.stdout.write(output)
    sys.stdout.write(end)
    sys.stdout.flush()


def up_fix_sign_manifestation(apps, schema_editor):
    query = AttachedDocument.objects.filter(
        diligence__isnull=False, signed_by__isnull=False
    ).filter(diligence__judicialdiligence__has_manifestations__signed_by__isnull=True)

    with transaction.atomic():
        for doc in query:
            set_current_user(doc.signed_by)

            Manifestation.objects.filter(diligence=doc.diligence).update(
                signed_by=person_from_user(doc.signed_by),
                signed_at=doc.signed_at,
                manifestation_type=2,
                who_type=4,
            )

            ManifestationLegalSign.sign(
                Manifestation.objects.get(diligence=doc.diligence)
            )

            log(".", end="")
    log(" pronto")


def down_fake(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0078_fix_executionorgan_diligence"),
    ]

    operations = [migrations.RunPython(up_fix_sign_manifestation, down_fake)]
