# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0034_county_for_judicial_diligence"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attached",
            options={"ordering": ("created_at",)},
        ),
        migrations.AlterModelOptions(
            name="judicialdiligence",
            options={
                "ordering": ("formated_number", "-delivery_status"),
                "permissions": (
                    ("admin_dilig", "Vis\xe3o Administrador"),
                    ("manager_dilig", "Vis\xe3o Central de Dilig\xeancias"),
                    ("oficial_dilig", "Vis\xe3o Oficial de Diligencias"),
                    ("promotor_dilig", "Vis\xe3o Promotor"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="cause",
            field=models.SmallIntegerField(
                choices=[(1, "O fato j\xe1 encontra-se solucionado")]
            ),
        ),
        migrations.AlterField(
            model_name="dearchivingdispatch",
            name="dearchiving_type",
            field=models.SmallIntegerField(choices=[(1, "Surgimento de novas provas")]),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="decision_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Reconsiderar Indeferimento"),
                    (2, "Manter o Indeferimento"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="triage_part",
            field=models.ForeignKey(
                related_name="as_triage_concurrences",
                to="judicial.TriagePart",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="triagepartlocation",
            name="triagepart",
            field=models.ForeignKey(
                related_name="+", to="judicial.TriagePart", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
