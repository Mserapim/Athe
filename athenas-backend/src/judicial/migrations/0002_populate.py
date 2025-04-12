# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations, models
from django.core.management import call_command
from django.conf import settings


FIXTURES = (
    "fixtures/0000-menu.json",
    "fixtures/0001-tags-of-system.json",
    "fixtures/0002-taxonomy.json",
    "fixtures/0003-legalclassification.json",
    "fixtures/0004-legalmatter.json",
    "fixtures/0005-legalmoviment.json",
    "fixtures/0006-legalprocedure.json",
    "fixtures/0007-county.json",
    "fixtures/0008-executionorgan.json",
    "fixtures/0009-glosarytemplate.json",
    "fixtures/0010-choices.json",
    "fixtures/0011-group.json",
    "fixtures/0012-controllerpermission.json",
    # 'fixtures/0013-ejud-site.json',
    "fixtures/0014-ws-ejud.json",
    "fixtures/0015-application-expediente.json",
    "fixtures/0016-controller-expediente.json",
    "fixtures/0017-controllerpermission-expediente.json",
    "fixtures/0018-users-expediente.json",
)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "judicial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0001_initial"),
    ]

    operations = [migrations.RunPython(forward, backward)]
