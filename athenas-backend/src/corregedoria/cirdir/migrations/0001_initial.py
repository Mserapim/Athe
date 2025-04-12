# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('ged', '0005_reorganization_of_storage_directory'),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("submitted_at", models.DateTimeField(null=True, blank=True)),
                ("start_date", models.DateField(null=True, blank=True)),
                ("end_date", models.DateField(null=True, blank=True)),
                ("authorization_reside_outside", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Cadstro de endere\xe7os de resid\xeancia",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Attachment",
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
                ("title", models.TextField()),
                (
                    "attach",
                    models.ForeignKey(
                        related_name="+", to="ged.Arquivo", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Anexos para o Controle de Informa\xe7\xf5es",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ControlInformation",
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
                ("year", models.PositiveSmallIntegerField()),
                ("closed_teaching_1st_semestry", models.NullBooleanField()),
                (
                    "open_date_teaching_1st_semestry",
                    models.DateTimeField(null=True, blank=True),
                ),
                (
                    "close_date_teaching_1st_semestry",
                    models.DateTimeField(null=True, blank=True),
                ),
                ("closed_teaching_2nd_semestry", models.NullBooleanField()),
                (
                    "open_date_teaching_2nd_semestry",
                    models.DateTimeField(null=True, blank=True),
                ),
                (
                    "close_date_teaching_2nd_semestry",
                    models.DateTimeField(null=True, blank=True),
                ),
                ("closed_address", models.NullBooleanField()),
                ("open_date_address", models.DateTimeField(null=True, blank=True)),
                ("close_date_address", models.DateTimeField(null=True, blank=True)),
                ("closed_property", models.NullBooleanField()),
                ("open_date_property", models.DateTimeField(null=True, blank=True)),
                ("close_date_property", models.DateTimeField(null=True, blank=True)),
                ("closed_debts", models.NullBooleanField()),
                ("open_date_debts", models.DateTimeField(null=True, blank=True)),
                ("close_date_debts", models.DateTimeField(null=True, blank=True)),
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
                        related_name="controlinformations",
                        to="rh.Servidor",
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
                    "previous_controlinformation",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="cirdir.ControlInformation",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["-year", "employee__pessoa_fisica__nome"],
                "verbose_name": "Controle de Informa\xe7\xf5es sobre Doc\xeancia, Resid\xeancia e Finan\xe7as",
                "permissions": (("can_management_cirdir", "Pode gerenciar o CIRDIR"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Debits",
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
                ("submitted_at", models.DateTimeField(null=True, blank=True)),
                ("description", models.TextField(null=True, blank=True)),
                (
                    "kind",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Individual"),
                            (2, "C\xf4njuge"),
                            (3, "Dependente"),
                        ],
                    ),
                ),
                (
                    "last_value",
                    models.DecimalField(
                        default=0,
                        null=True,
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                ("current_value", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "controlinformation",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cirdir.ControlInformation",
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
                "verbose_name": "Registros de D\xedvidas e \xd4nus em Reais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Discipline",
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
                ("name", models.TextField(unique=True)),
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
                "verbose_name": "Cadastro das Disciplinas",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Institution",
            fields=[
                (
                    "pessoajuridica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.PessoaJuridica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "county",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Cadastro das Institui\xe7\xf5es de Ensino",
            },
            bases=("rh.pessoajuridica",),
        ),
        migrations.CreateModel(
            name="IRSCode",
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
                ("code", models.SmallIntegerField(default="0", null=True, blank=True)),
                ("title", models.TextField(null=True, blank=True)),
                (
                    "type_irscode",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[(1, "Cr\xe9dito/Bens"), (2, "D\xe9bito")],
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
                "verbose_name": "C\xf3digo de classifica\xe7\xe3o da Receita Federal",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Property",
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
                ("submitted_at", models.DateTimeField(null=True, blank=True)),
                ("description", models.TextField(null=True, blank=True)),
                (
                    "kind",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Individual"),
                            (2, "C\xf4njuge"),
                            (3, "Dependente"),
                        ],
                    ),
                ),
                (
                    "last_value",
                    models.DecimalField(
                        default=0,
                        null=True,
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                ("current_value", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "controlinformation",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cirdir.ControlInformation",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Pais",
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
                    "irscode",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="cirdir.IRSCode",
                        null=True,
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
                    "submitted_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Regirsto de Bens, Rendas e Valores",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Schedule",
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
                    "day_week",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Segunda-feira"),
                            (2, "Ter\xe7a-feira"),
                            (3, "Quarta-feira"),
                            (4, "Quinta-feira"),
                            (5, "Sexta-feira"),
                            (6, "S\xe1bado"),
                            (7, "Domingo"),
                        ],
                    ),
                ),
                ("start_time", models.TimeField(verbose_name="Hora In\xedcio")),
                ("end_time", models.TimeField(verbose_name="Hora Fim")),
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
                "verbose_name": "Cadastro dos hor\xe1rios de doc\xeancia",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Teaching",
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
                ("submitted_at", models.DateTimeField(null=True, blank=True)),
                (
                    "work_hours",
                    models.SmallIntegerField(default="0", null=True, blank=True),
                ),
                ("start_date", models.DateField(null=True, blank=True)),
                ("end_date", models.DateField(null=True, blank=True)),
                ("authorization_teaching", models.BooleanField(default=True)),
                (
                    "period",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[(1, "1\xba Semestre"), (2, "2\xba Semestre")],
                    ),
                ),
                (
                    "controlinformation",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cirdir.ControlInformation",
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
                (
                    "discipline",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="cirdir.Discipline",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "institution",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="cirdir.Institution",
                        null=True,
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
                    "schedule",
                    models.ManyToManyField(
                        related_name="_teaching_schedule_+", to="cirdir.Schedule"
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Registro de doc\xeancias no per\xedodo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="debits",
            name="irscode",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="cirdir.IRSCode",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="debits",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="debits",
            name="submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachment",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="attachments",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="cirdir.ControlInformation",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="previous_address",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="cirdir.Address",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="address",
            name="ref_address",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Endereco",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
