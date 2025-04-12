# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0062_auto_20180309_1645"),
        ("judicial", "0041_remove_replacement"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0004_auto_20180201_1933"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnalysisPerformanceInAudiences",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "processes_analyzed_in_the_previous_inspection",
                    models.NullBooleanField(),
                ),
                ("survey_in_randomly_chosen_processes", models.NullBooleanField()),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise da Atua\xe7\xe3o nas Audi\xeancias",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AnalysisPerformanceInPlenarySessionOfTheJury",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise da Atua\xe7\xe3o nas Audi\xeancias",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Attachments",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("description", models.CharField(max_length=2000)),
                (
                    "attached_file",
                    models.ForeignKey(
                        related_name="inspection_file",
                        verbose_name="Arquivo",
                        to="ged.Arquivo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Arquivo anexados na inspe\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="BookOfRegisterCourtLawsuitControl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("book", models.CharField(max_length=100)),
                ("opening_date", models.DateField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Controle de Registro dos Procedimentos Judiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="BookOfRegisterOutCourtLawsuitControl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("book", models.CharField(max_length=100)),
                ("opening_date", models.DateField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Controle de Registro dos Procedimentos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CourtLawsuitControl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "record_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Registro",
                        blank=True,
                        choices=[
                            (1, "N\xe3o informado"),
                            (2, "Informatizado"),
                            (3, "Livro Convencional"),
                            (4, "Fichas"),
                            (5, "Outros"),
                            (6, "N\xe3o possui"),
                        ],
                    ),
                ),
                ("opening_date", models.DateField(null=True, blank=True)),
                ("has_openind_term", models.NullBooleanField(default=True)),
                ("has_numeration", models.NullBooleanField(default=True)),
                ("has_signed_sheets", models.NullBooleanField(default=True)),
                ("ordered", models.NullBooleanField(default=True)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Controle de Procedimentos Judiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CourtLawsuitCount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "number_of_processes_pending_citation_urgent",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_processes_pending_citation",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_processes_pending_science",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "processes_with_open_deadline",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "expired_deadline_the_last_30_days",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "expired_deadline_more_than_30_days_ago",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "expired_deadline_in_the_period_of_inspection",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Quantidade de Processos Judiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ExecutionOrganManagement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Organiza\xe7\xe3o",
                        blank=True,
                        choices=[
                            (1, "N\xe3o informado"),
                            (2, "Adequada"),
                            (3, "Regular"),
                            (4, "Inadequada"),
                        ],
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Gest\xe3o do \xd3rg\xe3o de Execu\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Inspection",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("inspection_date_initial", models.DateField(null=True, blank=True)),
                ("inspection_date_final", models.DateField(null=True, blank=True)),
                ("notice", models.CharField(max_length=100)),
                ("publication", models.CharField(max_length=100)),
                (
                    "area_of_action",
                    models.CharField(max_length=500, null=True, blank=True),
                ),
                ("assignment", models.CharField(max_length=500, null=True, blank=True)),
                ("residence", models.BooleanField(default=True)),
                ("accumulates", models.BooleanField(default=True)),
                ("replacements", models.BooleanField(default=True)),
                ("attendance", models.BooleanField(default=True)),
                ("teaching", models.BooleanField(default=True)),
                ("last_inspection_date", models.DateField(null=True, blank=True)),
                ("titular_employee", models.BooleanField(default=True)),
                ("daily_attendance", models.BooleanField(default=True)),
                (
                    "days_of_attendance_per_week",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "attendance_schedule1_inital",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule1_final",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule2_inital",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule2_final",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "list_months",
                    models.CharField(max_length=300, null=True, blank=True),
                ),
                ("electoral_applicable", models.SmallIntegerField(default=2)),
                (
                    "electoral_electoralzone",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "electoral_designation",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "electoral_initialbiennium",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "electoral_finalbiennium",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "operability_score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "promptness_score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "execution_organ",
                    models.ForeignKey(
                        related_name="inspections",
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "inspector_general",
                    models.ForeignKey(
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "inspector_prosecutor",
                    models.ForeignKey(
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-inspection_date_initial", "execution_organ"],
                "verbose_name": "Inspe\xe7\xe3o/Correi\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OutCourtLawsuitControl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "record_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Registro",
                        blank=True,
                        choices=[
                            (1, "N\xe3o informado"),
                            (2, "Informatizado"),
                            (3, "Livro Convencional"),
                            (4, "Fichas"),
                            (5, "Outros"),
                            (6, "N\xe3o possui"),
                        ],
                    ),
                ),
                ("opening_date", models.DateField(null=True, blank=True)),
                ("has_openind_term", models.NullBooleanField(default=True)),
                ("has_numeration", models.NullBooleanField(default=True)),
                ("has_signed_sheets", models.NullBooleanField(default=True)),
                ("ordered", models.NullBooleanField(default=True)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Controle de Procedimentos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OutCourtLawsuitCount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "number_of_procedures_in_progress",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_procedures_in_arrears",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "correctly_registered_procedures",
                    models.NullBooleanField(default=True),
                ),
                (
                    "number_of_public_civil_actions_in_the_last_year",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_recommendations_issued_in_the_last_year",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_conduct_adjustment_terms_in_the_last_year",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_procedures_instituted_in_the_last_year",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_procedures_archived_in_the_last_year",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Quantidade de Processos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OutCourtLawsuitElectoralCount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "number_of_procedures_in_progress",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "number_of_procedures_in_arrears",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "correctly_registered_procedures",
                    models.NullBooleanField(default=True),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Quantidade de Processos Extrajudiciais Eleitorais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcessesForAnalysisPerformanceInAudiences",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "audience_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Audi\xeancia",
                        blank=True,
                        choices=[(1, "N\xe3o informado"), (2, "Concilia\xe7\xe3o")],
                    ),
                ),
                ("intimation", models.BooleanField(default=True)),
                ("presence", models.BooleanField(default=True)),
                ("questions", models.BooleanField(default=True)),
                ("oral_manifestation", models.BooleanField(default=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.LegalClass",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise da Atua\xe7\xe3o nas Audi\xeancias",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcForQualAnalysisOfThePartsCivilCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("report", models.CharField(max_length=2000)),
                ("basis", models.CharField(max_length=2000)),
                ("proof", models.CharField(max_length=2000)),
                ("convincily", models.CharField(max_length=2000)),
                ("redaction", models.CharField(max_length=2000)),
                (
                    "score",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "part_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalMoviment",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Processos para An\xe1lise qualitativa das pe\xe7as de Processos Judiciais C\xedveis",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcForQualAnalysisOfThePartsCriminalCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("report", models.CharField(max_length=2000)),
                ("basis", models.CharField(max_length=2000)),
                ("proof", models.CharField(max_length=2000)),
                ("convincily", models.CharField(max_length=2000)),
                ("redaction", models.CharField(max_length=2000)),
                (
                    "score",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "part_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalMoviment",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Processos para An\xe1lise qualitativa das pe\xe7as de Processos Judiciais Criminais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcForQualAnalysisOfThePartsElectoral",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("report", models.CharField(max_length=2000)),
                ("basis", models.CharField(max_length=2000)),
                ("proof", models.CharField(max_length=2000)),
                ("convincily", models.CharField(max_length=2000)),
                ("redaction", models.CharField(max_length=2000)),
                (
                    "score",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "part_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalMoviment",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Prorcessos para An\xe1lise qualitativa das pe\xe7as de Processos Eleitorais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcForQualAnalysisOfThePartsOutCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "action_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("report", models.CharField(max_length=2000)),
                ("basis", models.CharField(max_length=2000)),
                ("proof", models.CharField(max_length=2000)),
                ("convincily", models.CharField(max_length=2000)),
                ("redaction", models.CharField(max_length=2000)),
                (
                    "score",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "action_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "part_type",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalMoviment",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Processos para An\xe1lise qualitativa das pe\xe7as de Procedimentos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PromptnessCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "score_table",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Tabela de C\xe1lculo",
                        blank=True,
                    ),
                ),
                (
                    "percentual",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("score", models.SmallIntegerField(default=0)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Avaliacao de Presteza em feitos Judiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PromptnessOutCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "score_table",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Tabela de C\xe1lculo",
                        blank=True,
                    ),
                ),
                (
                    "percentual",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("score", models.SmallIntegerField(default=0)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Avaliacao de Presteza em feitos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PromptnessUpperManagement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "score_table",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Tabela de C\xe1lculo",
                        blank=True,
                    ),
                ),
                (
                    "percentual",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("score", models.SmallIntegerField(default=0)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Avaliacao de Presteza as determina\xe7\xf5es da Administra\xe7\xe3o Superior e da Ouvidoria",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PublicAttendance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "record_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Registro",
                        blank=True,
                        choices=[
                            (1, "N\xe3o informado"),
                            (2, "Informatizado"),
                            (3, "Livro Convencional"),
                            (4, "Fichas"),
                            (5, "Outros"),
                            (6, "N\xe3o possui"),
                        ],
                    ),
                ),
                ("opening_date", models.DateField(null=True, blank=True)),
                ("has_openind_term", models.NullBooleanField(default=True)),
                ("has_numeration", models.NullBooleanField(default=True)),
                ("has_signed_sheets", models.NullBooleanField(default=True)),
                ("ordered", models.NullBooleanField(default=True)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Atendimento ao P\xfablico",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="QualitativeAnalysisOfThePartsCivilCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("applicable", models.NullBooleanField(default=False)),
                (
                    "score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise qualitativa das pe\xe7as de Processos Judiciais C\xedveis",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="QualitativeAnalysisOfThePartsCriminalCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("applicable", models.NullBooleanField(default=False)),
                (
                    "score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise qualitativa das pe\xe7as de Processos Judiciais Criminais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="QualitativeAnalysisOfThePartsElectoral",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("applicable", models.NullBooleanField(default=False)),
                (
                    "score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise qualitativa das pe\xe7as de Processos Eleitorais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="QualitativeAnalysisOfThePartsOutCourtLawsuit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("applicable", models.NullBooleanField(default=False)),
                (
                    "score",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "An\xe1lise qualitativa das pe\xe7as de Procedimentos Extrajudiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegisteredPublicAttendanceNumber",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "score_table",
                    models.IntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tabela de C\xe1lculo",
                        blank=True,
                    ),
                ),
                (
                    "average",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("score", models.SmallIntegerField(default=0)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "C\xe1lculo da m\xe9dia do atendimentos por m\xeas",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegistrationCourtLawsuitElectoralReceived",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Eleitorais Recebidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegistrationCourtLawsuitElectoralReturned",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Eleitorais Devolvidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegistrationCourtLawsuitReceived",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Recebidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegistrationCourtLawsuitReturned",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de Processos Judiciais Devolvidos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RegistrationPublicAttendance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.SmallIntegerField()),
                ("amount_january", models.SmallIntegerField(null=True, blank=True)),
                ("amount_february", models.SmallIntegerField(null=True, blank=True)),
                ("amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("amount_august", models.SmallIntegerField(null=True, blank=True)),
                ("amount_september", models.SmallIntegerField(null=True, blank=True)),
                ("amount_october", models.SmallIntegerField(null=True, blank=True)),
                ("amount_november", models.SmallIntegerField(null=True, blank=True)),
                ("amount_december", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_january", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_february",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_march", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_april", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_may", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_june", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_july", models.SmallIntegerField(null=True, blank=True)),
                ("raf_amount_august", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_september",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                ("raf_amount_october", models.SmallIntegerField(null=True, blank=True)),
                (
                    "raf_amount_november",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "raf_amount_december",
                    models.SmallIntegerField(null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Atendimento ao P\xfablico",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureCommissionedEmployees",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "commissioned_employee",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.MovimentacaoPessoal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Descri\xe7\xe3o da Estrutura do \xd3rg\xe3o Inspecionado - Servidores Comissionados",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureDeficiency",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("deficiency", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inspection",
                    models.OneToOneField(
                        to="inspection.Inspection", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Descri\xe7\xe3o da Estrutura do \xd3rg\xe3o Inspecionado - Deficiencias",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureEffectiveEmployees",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "effective_employee",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.MovimentacaoPessoal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Descri\xe7\xe3o da Estrutura do \xd3rg\xe3o Inspecionado - Servidores Efetivos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureExternalEmployees",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "external_employee",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.MovimentacaoPessoal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Descri\xe7\xe3o da Estrutura do \xd3rg\xe3o Inspecionado - Servidores Externos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="executionorganmanagement",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="executionorganmanagement",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="courtlawsuitcount",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="courtlawsuitcount",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="courtlawsuitcontrol",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="courtlawsuitcontrol",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="bookofregisteroutcourtlawsuitcontrol",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="bookofregisteroutcourtlawsuitcontrol",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="bookofregistercourtlawsuitcontrol",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="bookofregistercourtlawsuitcontrol",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attachments",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachments",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="analysisperformanceinplenarysessionofthejury",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="analysisperformanceinplenarysessionofthejury",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="analysisperformanceinaudiences",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="analysisperformanceinaudiences",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
