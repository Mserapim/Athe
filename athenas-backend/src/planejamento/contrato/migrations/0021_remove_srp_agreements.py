# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

from planejamento.contrato.models import Contrato as Agreement


def forwards_data_migration(apps, schema_editor):
    """
    Remove os contratos do tipo SRP da tabela de contratos
    """
    try:
        agreements_to_exclude = Agreement.objects.filter(tipo_contrato=2)
        agreements_to_exclude_count = agreements_to_exclude.count()
        agreements_to_exclude.delete()
        print("Foram excluídos {} contratos".format(agreements_to_exclude_count))
    except Agreement.DoesNotExist:
        print("Não foram encontrados contratos do tipo SRP")


def reverse_data_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("contrato", "0020_auto_20181112_1229"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="minutesolicitationcommitmentnote",
            options={
                "ordering": ("-id",),
                "verbose_name": "Nota de Empenho da Ata",
                "permissions": (
                    (
                        "request_minutesolicitationcommitmentnote_reinforcement",
                        "Can request a commitmentnote reinforcement of the solicitation.",
                    ),
                    (
                        "request_minutesolicitationcommitmentnote_reversal",
                        "Can request a commitmentnote reversal of the solicitation",
                    ),
                ),
            },
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="classification",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Classifica\xe7\xe3o",
                choices=[
                    (1, "Material de Consumo"),
                    (2, "Material Permanente"),
                    (3, "Servi\xe7o"),
                    (4, "Obras e Instala\xe7\xf5es"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="kind",
            field=models.IntegerField(
                verbose_name="Tipo de NE",
                choices=[(1, "Ordin\xe1rio"), (2, "Estimativo"), (3, "Global")],
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="number",
            field=models.CharField(max_length=20, verbose_name="N\xfamero"),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="origin",
            field=models.SmallIntegerField(
                verbose_name="Origem do Empenho", choices=[(1, "PGJ"), (2, "FUNDO")]
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="reinforcement_reversal",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Refor\xe7o/Estorno",
                choices=[(1, "Estorno"), (100, "Refor\xe7o")],
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="solicitation",
            field=models.ForeignKey(
                related_name="minutesolicitationcommitmentnotes",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Pedido",
                to="contrato.MinuteSolicitation",
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="value",
            field=models.DecimalField(
                verbose_name="Valor", max_digits=18, decimal_places=2
            ),
        ),
        migrations.RunPython(forwards_data_migration, reverse_data_migration),
    ]
