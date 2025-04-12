# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


def migrate_movimentacao_substituicao_place(apps, schema_editor):
    Move = apps.get_model("rh", "MovimentacaoSubstituicao")
    updated = 0
    moves = Move.objects.exclude(designation_substituted=None)
    total = moves.count()
    print("\nMovimentacaoSubstituicao UPDATED: %d" % updated)
    for move in moves:
        Move.objects.filter(pk=move.pk).update(
            place=move.designation_substituted.lotacao
        )
        updated += 1
        print("\nMovimentacaoSubstituicao UPDATED: %d -> %d" % (updated, total))

    print("\nMovimentacaoSubstituicao UPDATED: %d -> %d" % (updated, total))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0109_auto_20191219_1535"),
    ]

    operations = [
        migrations.RunPython(migrate_movimentacao_substituicao_place, _null_function),
    ]
