# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

import django.db.models.deletion
from django.db import migrations, models


def up_fn(apps, schema_editor):
    from adm.patrimonio.models import Patrimonio, AvaliacaoItem

    query = Patrimonio.objects.filter(valor_residual=None)
    total = query.count()
    pos = 0
    message = ""

    for pat in query:
        pos += 1
        sys.stdout.write("\b" * len(message))
        message = " (%d de %d) [%3.1f%%] " % (
            pos,
            total,
            ((pos * 100.0) / (total * 1.0)),
        )
        sys.stdout.write(message)
        sys.stdout.flush()
        avi = AvaliacaoItem.objects.filter(patrimonio=pat).first()
        pat.valor_residual = avi.residual if avi else None
        pat.save()


def down_fn(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0010_auto_20180807_1851"),
    ]

    operations = [
        migrations.AddField(
            model_name="patrimonio",
            name="valor_residual",
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.AddField(
            model_name="patrimoniohistorico",
            name="valor_residual",
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name="especie",
            name="status",
            field=models.SmallIntegerField(
                default=1, db_index=True, choices=[(1, "ATIVO"), (2, "INATIVO")]
            ),
        ),
        migrations.AlterField(
            model_name="grupoespecie",
            name="grupo_contabil",
            field=models.ForeignKey(
                related_name="grupo_especies",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.GrupoContabil",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="notabaixa",
            name="subtype",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Subtipo",
                choices=[
                    (1, "Obsolesc\xeancia"),
                    (2, "Deteriora\xe7\xe3o"),
                    (11, "Perda"),
                    (12, "Furto"),
                    (13, "Roubo"),
                    (1000, "N\xe3o informado"),
                ],
            ),
        ),
        migrations.RunPython(up_fn, down_fn),
    ]
