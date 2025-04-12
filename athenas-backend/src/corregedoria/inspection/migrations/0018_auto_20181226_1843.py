# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0076_auto_20181226_1843'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('judicial', '0062_deadlinelog'),
        ("inspection", "0017_auto_20181123_2349"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdministrativeOrganizationArchivedProcedures",
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
                ("number", models.CharField(max_length=30, null=True, blank=True)),
                ("matter", models.TextField(null=True, blank=True)),
                ("observation", models.TextField(null=True, blank=True)),
                ("archived_date", models.DateField(null=True, blank=True)),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdministrativeOrganizationAttendanceHours",
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
                ("daily_attendance", models.NullBooleanField(default=False)),
                (
                    "days_of_attendance_per_week",
                    models.SmallIntegerField(default=0, null=True, blank=True),
                ),
                (
                    "attendance_schedule1_initial",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule1_final",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule2_initial",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "attendance_schedule2_final",
                    models.CharField(max_length=5, null=True, blank=True),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdministrativeOrganizationGeneralStatus",
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
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Estado",
                        blank=True,
                        choices=[
                            (1, "INSUFICIENTE"),
                            (2, "REGULAR"),
                            (3, "BOM"),
                            (4, "MUITO BOM"),
                            (5, "\xd3TIMO"),
                        ],
                    ),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdministrativeOrganizationOperatingHours",
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
                    "operate_schedule1_initial",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "operate_schedule1_final",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "operate_schedule2_initial",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "operate_schedule2_final",
                    models.CharField(max_length=5, null=True, blank=True),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdministrativeOrganizationProceduresInProgress",
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
                ("number", models.CharField(max_length=30, null=True, blank=True)),
                ("matter", models.TextField(null=True, blank=True)),
                ("observation", models.TextField(null=True, blank=True)),
                ("instauration_date", models.DateField(null=True, blank=True)),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdministrativeOrganizationRegistrationSystem",
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
                    "registration_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Registro",
                        blank=True,
                        choices=[(1, "Manual"), (2, "Informatizado")],
                    ),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ExistingRegisters",
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
                ("register", models.CharField(max_length=500, null=True, blank=True)),
                (
                    "registration_type",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Tipo de Registro",
                        blank=True,
                        choices=[(1, "Manual"), (2, "Informatizado")],
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MemberOrgan",
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
                    "member_role",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Papel",
                        blank=True,
                        choices=[
                            (1, "PRESIDENTE"),
                            (2, "COORDENADOR"),
                            (3, "INTEGRANTE"),
                        ],
                    ),
                ),
                ("exclusive", models.BooleanField(default=False)),
                ("needs_exclusivity", models.BooleanField(default=False)),
                ("justify", models.TextField(null=True, blank=True)),
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
                    "employee",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Servidor",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OperatingStructure",
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
                ("location", models.CharField(max_length=500)),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Performance",
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
                ("performance", models.TextField(null=True, blank=True)),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureEquipment",
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
                ("equipment", models.CharField(max_length=500)),
                ("amount", models.SmallIntegerField(null=True, blank=True)),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Estado",
                        blank=True,
                        choices=[
                            (1, "P\xc9SSIMO"),
                            (2, "RUIM"),
                            (3, "BOM"),
                            (4, "MUITO BOM"),
                            (5, "\xd3TIMO"),
                        ],
                    ),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="StructureGeneralStatus",
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
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Estado",
                        blank=True,
                        choices=[
                            (1, "INSUFICIENTE"),
                            (2, "REGULAR"),
                            (3, "BOM"),
                            (4, "MUITO BOM"),
                            (5, "\xd3TIMO"),
                        ],
                    ),
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
                "verbose_name": "",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="inspection",
            name="communicated_cpjcsmp",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="inspection",
            name="communicated_cpjcsmp_at",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="inspection",
            name="inspection_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Inspe\xe7\xe3o",
                blank=True,
                choices=[
                    (1, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                    (2, "Grupo Especial"),
                    (3, "\xd3rg\xe3o Auxiliar"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="attachments",
            name="area",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="\xc1REA",
                blank=True,
                choices=[
                    (1, "Regularidade dos Servi\xe7os"),
                    (2, "Estrutura"),
                    (3, "Desempenho Funcional"),
                    (4, "Observa\xe7\xf5es Gerais"),
                    (5, "Recomenda\xe7\xf5es"),
                    (6, "Anexos"),
                    (7, "Estrutura de Funcionamento"),
                    (8, "Organiza\xe7\xe3o Administrativa"),
                    (9, "Atua\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="accumulates",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="attendance",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="communicated_organ_execution",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="daily_attendance",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="electoral_applicable",
            field=models.SmallIntegerField(default=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="finalized",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="number_collegiate_organ_session",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="operability_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="promptness_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="replacements",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="teaching",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="titular_employee",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="tj_sessions_administrative",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="tj_sessions_civil",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="tj_sessions_criminal",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processesforanalysisperformanceinaudiences",
            name="audience_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Audi\xeancia",
                blank=True,
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Concilia\xe7\xe3o"),
                    (3, "Instru\xe7\xe3o"),
                    (4, "Julgamento"),
                    (5, "Instru\xe7\xe3o e Julgamento"),
                    (6, "Preliminar"),
                    (7, "Interrogat\xf3rio"),
                    (8, "Inquiri\xe7\xe3o"),
                    (9, "Diploma\xe7\xe3o"),
                    (10, "Justifica\xe7\xe3o"),
                    (11, "Apresenta\xe7\xe3o"),
                    (12, "Apresenta\xe7\xe3o/Remiss\xe3o"),
                    (13, "Audi\xeancias gerais da Inf\xe2ncia e Juventude"),
                    (14, "Suspens\xe3o condicional do processo"),
                    (15, "Conciclia\xe7\xe3o, Instru\xe7\xe3o e Julgamento"),
                    (16, "Admonit\xf3ria"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="structuregeneralstatus",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="structuregeneralstatus",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="structureequipment",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="structureequipment",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="performance",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="performance",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="operatingstructure",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="operatingstructure",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="memberorgan",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="memberorgan",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="existingregisters",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="existingregisters",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationregistrationsystem",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationregistrationsystem",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationproceduresinprogress",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationproceduresinprogress",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationproceduresinprogress",
            name="taxonomy_class",
            field=models.ForeignKey(
                related_name="+", to="judicial.LegalClass", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationproceduresinprogress",
            name="taxonomy_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationoperatinghours",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationoperatinghours",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationgeneralstatus",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationgeneralstatus",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationattendancehours",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationattendancehours",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationarchivedprocedures",
            name="inspection",
            field=models.ForeignKey(
                related_name="+", to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationarchivedprocedures",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="administrativeorganizationarchivedprocedures",
            name="taxonomy_class",
            field=models.ForeignKey(
                related_name="+", to="judicial.LegalClass", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="administrativeorganizationarchivedprocedures",
            name="taxonomy_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
