# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_configs_career(apps, schema_editor):
    start_date = datetime(1989, 1, 1).date()
    CarrerModel = apps.get_model("rh", "Carreira")
    CarrerConfigModel = apps.get_model("rh", "ConfigCareer")
    createds = 0
    for career in CarrerModel.objects.filter():
        cc, created = CarrerConfigModel.objects.get_or_create(
            start_validity=career.data_inicio or start_date,
            end_validity=career.data_fim,
            career=career,
            name=career.nome,
            code=career.codigo,
            created_at=career.created_at,
            modified_at=career.modified_at,
            created_by=career.created_by,
            modified_by=career.modified_by,
        )
        createds += 1 if created else 0
    print("\nCONFIG CAREER MIGRATEDS: %d" % createds)


def migrate_configs_job_position(apps, schema_editor):
    start_date = datetime(1989, 1, 1).date()
    JobPositionModel = apps.get_model("rh", "Cargo")
    ConfigJobPositionModel = apps.get_model("rh", "ConfigJobPosition")
    createds = 0
    for job_position in JobPositionModel.objects.filter():
        quarter = job_position.quadros.last()
        config_job_position, created = ConfigJobPositionModel.objects.get_or_create(
            start_validity=start_date,
            job_position=job_position,
            name=job_position.nome,
            code=job_position.codigo,
            teacher=job_position.professor,
            designates_exercise=job_position.designa_exercicio,
            boss=job_position.chefia,
            replaceable=job_position.substituivel,
            cbo=job_position.cbo,
            remunerated=job_position.remunerated,
            cumulative=job_position.cumulative or 1,
            educational_level=quarter.nivel_escolaridade if quarter else 3,
            level_instance=job_position.level_instance,
            instance=job_position.instance,
            quantity=job_position.quadros.aggregate(
                quantity=models.Sum("quantidade_vagas")
            ).get("quantity")
            or 0,
            workload=quarter.carga_horaria if quarter else 40,
            type_workload=quarter.tipo_carga_horaria if quarter else 2,
            created_at=job_position.created_at,
            modified_at=job_position.modified_at,
            created_by=job_position.created_by,
            modified_by=job_position.modified_by,
        )
        createds += 1 if created else 0
    print("\nCONFIG JOB POSITION MIGRATEDS: %d" % createds)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0067_auto_20180917_1501"),
    ]

    operations = [
        migrations.RunPython(migrate_configs_career, _null_function),
        migrations.RunPython(migrate_configs_job_position, _null_function),
    ]
