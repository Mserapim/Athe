# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0012_populate_pessoa_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dependente",
            name="pessoa_fisica",
            field=models.ForeignKey(
                related_name="dependentes_pessoa",
                verbose_name="Pessoa F\xedsica",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="dependente",
            unique_together=set([("pessoa_fisica", "servidor")]),
        ),
    ]
