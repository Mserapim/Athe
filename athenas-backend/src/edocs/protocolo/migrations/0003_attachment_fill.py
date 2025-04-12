# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def attachment_fill(apps, schama_editor):
    Anexo = apps.get_model("protocolo", "Anexo")
    Attachment = apps.get_model("protocolo", "Attachment")

    for anexo in Anexo.objects.exclude(movimentacao=None).exclude(arquivo=None):
        moviment = anexo.movimentacao.first()

        attach = Attachment(
            moviment=moviment,
            protocol=moviment.protocolo,
            title=anexo.nome,
            attach=anexo.arquivo,
            observation=anexo.descricao if anexo.descricao else "",
            created_by=anexo.arquivo.user,
            modified_by=anexo.arquivo.user,
            created_at=moviment.data_encaminhamento,
            modified_at=moviment.data_encaminhamento,
        )

        attach.save()


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0002_auto_20150810_1114"),
    ]

    operations = [migrations.RunPython(attachment_fill)]
