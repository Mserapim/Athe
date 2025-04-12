# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0006_auto_20150921_1434"),
    ]

    operations = [
        migrations.AddField(
            model_name="orgaogeral",
            name="old",
            field=models.ForeignKey(
                verbose_name="\xd3rg\xe3o antigo",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="orgaogeral",
            name="publication",
            field=models.ForeignKey(
                related_name="generalorgan_creating",
                verbose_name="Publica\xe7\xe3o cria\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
