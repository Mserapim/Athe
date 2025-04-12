# -*- coding: utf-8 -*-
from django.db import migrations
from unicodedata import normalize


def migrate_name_cache(apps, schema_editor):
    print("ATUALIZACAO DE PESSOA name_cache")
    PessoaModel = apps.get_model("rh", "Pessoa")
    updated = 1
    psm = PessoaModel.objects.filter()
    total = psm.count()
    for ps in psm:
        PessoaModel.objects.filter(pk=ps.pk).update(
            name_cache=normalize("NFKD", ps.nome).encode("ASCII", "ignore")
        )
        print("ATUALIZACAO DE PESSOA name_cache:  %s de %s" % (updated, total))
        updated += 1


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0106_pessoa_name_cache"),
    ]

    operations = [
        migrations.RunPython(migrate_name_cache, _null_function),
    ]
