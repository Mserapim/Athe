# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cirdir", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Health",
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
                ("description", models.TextField(null=True, blank=True)),
            ],
            options={
                "verbose_name": "Registros das Informa\xe7\xf5es de Sa\xfade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="irscode",
            options={
                "ordering": ["type_irscode", "code"],
                "verbose_name": "C\xf3digo de classifica\xe7\xe3o da Receita Federal",
            },
        ),
        migrations.RemoveField(
            model_name="address",
            name="submitted_at",
        ),
        migrations.RemoveField(
            model_name="address",
            name="submitted_by",
        ),
        migrations.RemoveField(
            model_name="debits",
            name="submitted_at",
        ),
        migrations.RemoveField(
            model_name="debits",
            name="submitted_by",
        ),
        migrations.RemoveField(
            model_name="property",
            name="submitted_at",
        ),
        migrations.RemoveField(
            model_name="property",
            name="submitted_by",
        ),
        migrations.RemoveField(
            model_name="teaching",
            name="submitted_at",
        ),
        migrations.RemoveField(
            model_name="teaching",
            name="submitted_by",
        ),
        migrations.AddField(
            model_name="address",
            name="type_residence",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[(1, "Casa"), (2, "Apartamento"), (3, "Hotel")],
            ),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="address_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="address_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="close_date_health",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="closed_health",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="debits_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="debits_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="health_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="health_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="open_date_health",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="property_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="property_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="teaching_1st_semestry_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="teaching_1st_semestry_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="teaching_2nd_semestry_submitted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="teaching_2nd_semestry_submitted_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="schedule",
            name="date_module",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="schedule",
            name="type_schedule",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                blank=True,
                choices=[(1, "Regular"), (2, "Modular")],
            ),
        ),
        migrations.AddField(
            model_name="teaching",
            name="modality",
            field=models.SmallIntegerField(
                blank=True, null=True, choices=[(1, "Presencial"), (2, "EAD")]
            ),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="end_time",
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="start_time",
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="schedule",
            field=models.ManyToManyField(
                related_name="teachings", to="cirdir.Schedule"
            ),
        ),
        migrations.AddField(
            model_name="health",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AddField(
            model_name="health",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="health",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
