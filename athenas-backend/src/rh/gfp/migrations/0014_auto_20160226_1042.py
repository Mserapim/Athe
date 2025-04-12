# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0013_auto_20160217_1748"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="order",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Ordem", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="para_indicativo",
            field=models.CharField(
                default=None,
                max_length=1,
                null=True,
                verbose_name="Para os",
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="perfilprevidencia",
            name="lei_cargo",
            field=models.CharField(
                max_length=10,
                verbose_name="Tipo de Lei",
                choices=[
                    ("EF", "EFETIVO"),
                    ("CM", "COMISS\xc3O"),
                    ("FC", "FUN\xc7\xc3O DE CONFIAN\xc7A"),
                    ("AC", "ACORDO DE COOPERA\xc7\xc3O T\xc9CNICA"),
                    ("ES", "ESTAGI\xc1RIO"),
                    ("EL", "ELETIVO"),
                    ("TE", "TERCEIRIZADO"),
                ],
            ),
            preserve_default=True,
        ),
    ]
