# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_vacancy_number_filled_cache(apps, schema_editor):
    Possession = apps.get_model("rh", "MovimentacaoPosse")
    JobPositionChart = apps.get_model("rh", "CargoQuadro")
    Chart = apps.get_model("rh", "Quadro")
    updated = 0
    date = datetime.now().date()
    for chart in Chart.objects.filter():
        vacancy_number_filled_cache = Possession.objects.filter(
            models.Q(quadro=chart)
            & models.Q(
                models.Q(data_exercicio__lte=date)
                & (
                    models.Q(data_desligamento__gte=date)
                    | models.Q(data_desligamento=None)
                )
            )
        ).count()
        jobpositionchart = JobPositionChart.objects.filter(
            cargo=chart.cargo, especialidade=chart.especialidade
        )
        if jobpositionchart.exists():
            jobpositionchart.update(
                vacancy_number_filled_cache=vacancy_number_filled_cache
            )
            updated += 1
    print("\nCargoQuadro UPDATED: %d" % updated)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0093_auto_20190822_2040"),
    ]

    operations = [
        migrations.RunPython(migrate_vacancy_number_filled_cache, _null_function),
    ]
