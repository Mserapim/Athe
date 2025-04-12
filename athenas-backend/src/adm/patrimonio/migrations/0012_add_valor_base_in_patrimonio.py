# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from adm.patrimonio.models import Patrimonio
from django.db import migrations, models


def forwards_data_migration(apps, schema_editor):
    """
    Atualiza o campo valor_base com o valor de item_entrada
    """
    try:
        assets = Patrimonio.objects.all()

        qtd_assets = assets.count()
        current = 0
        message = ""

        for patrimony in assets:
            current += 1
            sys.stdout.write("\b" * len(message))
            message = " [%d de %d (%0.1f%%)] " % (
                current,
                qtd_assets,
                ((float(current) / float(qtd_assets)) * 100.0),
            )
            sys.stdout.write(message)
            sys.stdout.flush()

            patrimony.valor_base = patrimony.item_entrada.valor_unitario
            patrimony.save()

    except Patrimonio.DoesNotExist:
        print("Não foram encontrados registros em Patrimônio")

    except Exception as e:
        print(e)


def reverse_data_migration(apps, schema_editor):
    try:
        assets = Patrimonio.objects.all()
        for patrimony in assets:
            patrimony.valor_base = None
            patrimony.save()

    except Patrimonio.DoesNotExist:
        print("Não foram encontrados registros em Patrimônio")

    except Exception as e:
        print(e)


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0011_residual_value_in_item"),
    ]

    operations = [
        migrations.AddField(
            model_name="patrimonio",
            name="valor_base",
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.AddField(
            model_name="patrimoniohistorico",
            name="valor_base",
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.RunPython(forwards_data_migration, reverse_data_migration),
    ]
