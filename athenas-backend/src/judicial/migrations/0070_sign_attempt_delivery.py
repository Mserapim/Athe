# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import time

from datetime import datetime
from multiprocessing import Pool
from django.db import migrations, models
from django.contrib.auth.models import User
from contrib.middleware import set_current_user, get_current_user
from celery import group


def _generator(query):
    for attempt in query.values("pk"):
        yield attempt.get("pk")


def up_update_sign_delivery(apps, schema_editor):
    from judicial.models import DeliveryAttemptLegalSign, DeliveryAttempt
    from judicial.tasks import migrate_sign_attempt

    query = DeliveryAttempt.objects.filter(
        signed_by=None, return_date__isnull=False
    ).exclude(diligence__judicialdiligence=None)

    tasks = group(
        [
            migrate_sign_attempt.s(attempt.get("pk"), "athenas")
            for attempt in query.values("pk")
        ]
    )

    tasks().join()


def down_fake(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0069_refactory_in_diligence_and_delivery"),
    ]

    operations = [migrations.RunPython(up_update_sign_delivery, down_fake)]
