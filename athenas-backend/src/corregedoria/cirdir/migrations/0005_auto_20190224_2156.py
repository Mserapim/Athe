# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cirdir", "0004_auto_20190218_1333"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="health",
            name="description",
        ),
        migrations.AddField(
            model_name="health",
            name="better_at_work",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="conducted_examinations",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="conducted_examinations_which",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="dental_evaluation",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="depression_or_frustration_major_problem",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="difficulty_sleeping",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="enjoyed_the_vacation",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="family_health_problems",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="family_health_problems_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="has_pain",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="health_problems",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="health_problems_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="immunization",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_beef",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_candy",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_fruit",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_fry",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_pasta",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_supplement",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="ingestion_vegetable",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="job_exhaustion",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="job_relationship",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="job_relationship_boss",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="job_satisfaction",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="leisure_actions",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="less_at_work",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="life_habits",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="life_habits_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="local_pain",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="local_pain_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medical_consultation",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medical_consultation_specialty",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medicament",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medicament_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="observations",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_activity",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_exam_abdominal_circumference",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_exam_blood_pressure",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_exam_imc",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_exam_other",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="physical_exam_pulse",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="planning_future",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="satisfied_service",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="satisfied_service_justify",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="stress_or_anxiety_major_problem",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="topics_of_interest",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_foot_support",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_has_rod",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_height_adjustment",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_regulates_when_sitting",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_seat_adjustment",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_supports_back",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_tilt_adjustment",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="work_chair_use_rods",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
