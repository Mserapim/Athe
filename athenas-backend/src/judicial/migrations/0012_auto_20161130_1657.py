# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0035_auto_20161130_1653'),
        ("judicial", "0011_auto_20161124_1455"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpecialRemittanceInternal",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("text", models.TextField()),
                ("conflict", models.BooleanField(default=False)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="type_vehicle",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                choices=[
                    (1, "Ve\xedculo Oficial"),
                    (2, "Ve\xedculo Particular"),
                    (3, "Correios ou outro terceiro"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                    (6, "Publica\xe7\xe3o em di\xe1rio Oficial"),
                    (7, "Entrega pelo \xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="legalclassification",
            name="glossary",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="officerdiligence",
            name="status",
            field=models.SmallIntegerField(
                default=1, null=True, choices=[(1, "Ativo"), (2, "Inativo")]
            ),
        ),
    ]
