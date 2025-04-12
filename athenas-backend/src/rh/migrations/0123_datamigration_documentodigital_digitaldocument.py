# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


def migrate_documentodigital_digitaldocument(apps, schema_editor):
    DocumentoDigitalModel = apps.get_model("rh", "DocumentoDigital")
    DigitalDocumentModel = apps.get_model("rh", "DigitalDocument")
    created = 0
    file_not_found = 0
    documents = DocumentoDigitalModel.objects.filter()
    total = documents.count()
    print("\Documento digital migrado para Digital Document: %d" % created)
    for document in documents:
        if document.arquivo:
            DigitalDocumentModel.objects.get_or_create(
                created_by=document.created_by,
                modified_by=document.modified_by,
                name=document.name,
                file=document.arquivo,
                employee=document.servidor.first(),
                document_type=58,
            )
            created += 1
            print(
                "\Documento digital migrado para Digital Document: %d -> %d"
                % (created, total)
            )
        else:
            file_not_found += 1

    print(
        "\Documento digital migrado para Digital Document: %d -> %d" % (created, total)
    )
    print("\Documento digital sem arquivo: %d" % file_not_found)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0122_add_person_digitaldocument"),
    ]

    operations = [
        migrations.RunPython(migrate_documentodigital_digitaldocument, _null_function),
    ]
