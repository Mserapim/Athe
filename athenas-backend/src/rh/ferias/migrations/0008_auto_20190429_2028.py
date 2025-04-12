# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def _null_function(apps, schema_editor):
    pass


def migrar_mes_fruicao(apps, schema_editor):

    AcquisitionPeriod = apps.get_model("ferias", "PeriodoAquisitivo")

    query = AcquisitionPeriod.objects.filter(mes_fruicao=0)
    print("TOTAL ... %s - > %s" % (query.count(), query.update(mes_fruicao=14)))


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0007_periodoaquisitivoservidor_homologation_publication"),
    ]

    operations = [
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="mes_fruicao",
            field=models.SmallIntegerField(
                default=14,
                help_text="M\xc3\xaas para frui\xc3\xa7\xc3\xa3o coletiva, caso haja",
                verbose_name="M\xeas de frui\xe7\xe3o",
                choices=[
                    (1, "JANEIRO"),
                    (2, "FEVEREIRO"),
                    (3, "MAR\xc7O"),
                    (4, "ABRIL"),
                    (5, "MAIO"),
                    (6, "JUNHO"),
                    (7, "JULHO"),
                    (8, "AGOSTO"),
                    (9, "SETEMBRO"),
                    (10, "OUTUBRO"),
                    (11, "NOVEMBRO"),
                    (12, "DEZEMBRO"),
                    (14, "----------"),
                ],
            ),
        ),
        migrations.RunPython(migrar_mes_fruicao, _null_function),
    ]
