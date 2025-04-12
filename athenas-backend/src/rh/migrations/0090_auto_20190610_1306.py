# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0089_auto_20190513_1410"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cargahoraria",
            options={"ordering": ("servidor",)},
        ),
        migrations.AlterModelOptions(
            name="pessoafisica",
            options={
                "ordering": ("nome", "cpf"),
                "permissions": (
                    (
                        "can_manage_person_employee",
                        "Permiss\xe3o para gerenciar Servidor",
                    ),
                    (
                        "can_merge_naturalperson",
                        "Permiss\xe3o para mesclar Pessoa F\xedsica",
                    ),
                ),
                "verbose_name": "Pessoa F\xedsica",
            },
        ),
    ]
