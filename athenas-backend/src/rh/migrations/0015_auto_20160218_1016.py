# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0014_substitutionsendarquimedes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cargo",
            name="indicativo",
            field=models.CharField(
                default="S",
                max_length=1,
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
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Inst\xe2ncia", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Entr\xe2ncia", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="cargo",
            name="poder",
            field=models.IntegerField(default=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="cargo",
            name="tipo_lei_cargo",
            field=models.CharField(
                default="EF",
                max_length=2,
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
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="turno",
            field=models.IntegerField(default=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servidor",
            name="tipo",
            field=models.CharField(
                default="S",
                max_length=1,
                blank=True,
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
            model_name="substitutionsendarquimedes",
            name="substitution",
            field=models.ForeignKey(
                related_name="sended_arquimedes",
                to="rh.MovimentacaoSubstituicaoMembro",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="tiposervidor",
            name="indicativo",
            field=models.CharField(
                max_length=1,
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
    ]
