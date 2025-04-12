# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations, models


def update_root(root, administrative_classification=True):
    root.administrative_classification = administrative_classification
    root.save()
    print("+" if administrative_classification else "-", end="")

    for child in root.children.filter():
        update_root(child, administrative_classification)


def up(*args, **kwargs):
    from judicial.models import LegalMatter

    older = LegalMatter.objects.filter(administrative_classification=True).count()

    root = LegalMatter.objects.get(cnmp_code=930001)
    update_root(root, True)

    now = LegalMatter.objects.filter(administrative_classification=True).count()

    print("\nTotal updated %d" % (now - older))


def down(*args, **kwargs):
    from judicial.models import LegalMatter

    older = LegalMatter.objects.filter(administrative_classification=False).count()

    root = LegalMatter.objects.get(cnmp_code=930001)
    update_root(root, False)

    now = LegalMatter.objects.filter(administrative_classification=False).count()

    print("\nTotal updated %d" % (now - older))


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0016_auto_20161222_1618"),
    ]

    operations = [migrations.RunPython(up, down)]
