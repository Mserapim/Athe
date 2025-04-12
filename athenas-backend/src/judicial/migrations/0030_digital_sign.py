# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
from contrib.middleware import set_current_user


def pp(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()
    sys.stderr.flush()


def sync_part_legal_sign():
    from judicial.models import PartLawsuit, PartLegalSign

    def up(apps, schema_editor):
        query = PartLawsuit.objects.filter(legal_signs__isnull=True).exclude(
            signed_by=None
        )

        pp(" ", end="")
        for part in query:
            try:
                set_current_user(part.signed_by)
                sign = PartLegalSign.sign(part)
                PartLegalSign.objects.filter(pk=sign.pk).update(when=part.signed_at)
                set_current_user(None)
            except Exception:
                pp("\033[1m\033[32m!\033[0m", end="")
            else:
                pp("\033[1m\033[33m*\033[0m", end="")

    def down(apps, schema_editor):
        pass

    return migrations.RunPython(up, down)


def sync_denunciation_legal_sign():
    from judicial.models import Denunciation, PartLegalSign

    def up(apps, schema_editor):
        query = Denunciation.objects.filter(legal_signs__isnull=True)

        pp(" ", end="")
        for part in query:
            try:
                set_current_user(part.created_by)
                part.signed_at = part.created_at
                sign = PartLegalSign.sign(part)
                PartLegalSign.objects.filter(pk=sign.pk).update(when=part.created_at)
                set_current_user(None)
            except Exception:
                pp("\033[1m\033[32m~\033[0m", end="")
            else:
                pp("\033[1m\033[33m*\033[0m", end="")

    def down(apps, schema_editor):
        pass

    return migrations.RunPython(up, down)


def sync_judicial_diligence_legal_sign():
    from judicial.models import JudicialDiligence, JudicialDiligenceLegalSign

    def up(apps, schema_editor):
        query = JudicialDiligence.objects.filter(legal_signs__isnull=True).exclude(
            signed_by=None
        )

        pp(" ", end="")
        for part in query:
            try:
                set_current_user(part.signed_by)
                sign = JudicialDiligenceLegalSign.sign(part)
                JudicialDiligenceLegalSign.objects.filter(pk=sign.pk).update(
                    when=part.signed_at
                )
                set_current_user(None)
            except Exception:
                pp("\033[1m\033[32m!\033[0m", end="")
            else:
                pp("\033[1m\033[33m*\033[0m", end="")

    def down(apps, schema_editor):
        pass

    return migrations.RunPython(up, down)


def sync_manifestation_legal_sign():
    from judicial.models import Manifestation, ManifestationLegalSign
    from django.contrib.auth.models import User

    def up(apps, schema_editor):
        query = Manifestation.objects.filter(legal_signs__isnull=True).exclude(
            signed_by=None
        )

        pp(" ", end="")
        for manifestation in query:
            try:
                user = User.objects.get(servidor__pessoa_fisica=manifestation.signed_by)
                set_current_user(user)
                sign = ManifestationLegalSign.sign(manifestation)
                ManifestationLegalSign.objects.filter(pk=sign.pk).update(
                    when=manifestation.signed_at
                )
                set_current_user(None)
                user = None
            except Exception:
                pp("\033[1m\033[32m!\033[0m", end="")
            else:
                pp("\033[1m\033[33m*\033[0m", end="")

    def down(apps, schema_editor):
        pass

    return migrations.RunPython(up, down)


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0029_attached_moment_at"),
    ]

    operations = [
        sync_denunciation_legal_sign(),
        sync_part_legal_sign(),
        sync_judicial_diligence_legal_sign(),
        sync_manifestation_legal_sign(),
    ]
