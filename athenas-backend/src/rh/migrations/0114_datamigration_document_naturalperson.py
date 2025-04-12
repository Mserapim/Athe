# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


def migrate_document_natural_person(apps, schema_editor):
    DocumentModel = apps.get_model("rh", "Documento")
    updated = 0
    documents = DocumentModel.objects.filter(natural_person=None)
    total = documents.count()
    print("\Documento UPDATED: %d" % updated)
    for document in documents:
        DocumentModel.objects.filter(pk=document.pk).update(
            natural_person=document.naturalpersons.last()
        )
        updated += 1
        print("\Documento UPDATED: %d -> %d" % (updated, total))

    print("\Documento UPDATED: %d -> %d" % (updated, total))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0113_auto_20200313_1557"),
    ]

    operations = [
        migrations.RunPython(migrate_document_natural_person, _null_function),
    ]
