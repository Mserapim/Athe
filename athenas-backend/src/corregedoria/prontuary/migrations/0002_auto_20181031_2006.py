# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("afastamento", "0006_auto_20180207_1659"),
        ("ged", "0004_auto_20180201_1933"),
        ("prontuary", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttachmentsDetailCoursesParticipation",
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
                        related_name="+",
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
                "verbose_name": "Anexos referentes as participa\xe7\xf5es em cursos do membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AttachmentsDetailInstitutionalParticipation",
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
                        related_name="+",
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
                "verbose_name": "Anexos referentes as participa\xe7\xf5es instituicionais do membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AttachmentsListIndication",
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
                        related_name="+",
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
                "verbose_name": "Anexos referentes \xe0s Inscri\xe7\xf5es em concursos, bem como as indica\xe7\xf5es em lista de Promo\xe7\xe3o e Remo\xe7\xe3o para o membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CoursesParticipation",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "prontuary",
                    models.OneToOneField(
                        to="prontuary.Prontuary", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Representa\xe7\xe3o do que foi alcan\xe7ado pelo membro no item Frequ\xeancia e Aproveitamento em Cursos",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DetailCoursesParticipation",
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
                    "course_level",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Crit\xe9rio de Merecimento",
                        blank=True,
                        choices=[
                            (1, "DOUTORADO"),
                            (2, "MESTRADO"),
                            (3, "ESPECIALIZA\xc7\xc3O"),
                            (4, "CURSOS/EVENTOS - CESAF"),
                            (5, "APERFEI\xc7OAMENTO"),
                        ],
                    ),
                ),
                ("course", models.CharField(max_length=1000, null=True, blank=True)),
                ("date_course", models.DateField(null=True, blank=True)),
                ("workload", models.IntegerField(default=0, null=True, blank=True)),
                (
                    "validated",
                    models.SmallIntegerField(default=2, null=True, blank=True),
                ),
                ("score", models.SmallIntegerField(default=0, null=True, blank=True)),
                (
                    "coursesparticipation",
                    models.ForeignKey(
                        related_name="+",
                        to="prontuary.CoursesParticipation",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "studydepartures",
                    models.ManyToManyField(
                        related_name="departures", to="afastamento.AfastamentoEstudar"
                    ),
                ),
            ],
            options={
                "ordering": ["course_level", "-date_course"],
                "verbose_name": "Cursos registrados para o membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DetailInstitutionalParticipation",
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
                    "contribution",
                    models.CharField(max_length=1000, null=True, blank=True),
                ),
                ("score", models.IntegerField(default=0, null=True, blank=True)),
                (
                    "validated",
                    models.SmallIntegerField(default=1, null=True, blank=True),
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
                "verbose_name": "Participa\xe7\xf5es instituicionais registradas para o membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DetailListIndication",
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
                ("edital", models.CharField(max_length=100, null=True, blank=True)),
                ("date_edital", models.DateField(null=True, blank=True)),
                (
                    "list_figuration",
                    models.SmallIntegerField(default=1, null=True, blank=True),
                ),
                (
                    "criteria",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Crit\xe9rio de Merecimento",
                        blank=True,
                        choices=[(1, "PROMO\xc7\xc3O")],
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
                "ordering": ["-date_edital"],
                "verbose_name": "Inscri\xe7\xf5es em concursos, bem como as indica\xe7\xf5es em lista de Promo\xe7\xe3o e Remo\xe7\xe3o para o membro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="InstitutionalParticipation",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "prontuary",
                    models.OneToOneField(
                        to="prontuary.Prontuary", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Representa\xe7\xe3o do que foi alcan\xe7ado pelo membro no item Participa\xe7\xe3o Institucional",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ListIndication",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "prontuary",
                    models.OneToOneField(
                        to="prontuary.Prontuary", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Representa\xe7\xe3o do que foi alcan\xe7ado pelo membro no item Indica\xe7\xe3o em Lista",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="detaillistindication",
            name="listindication",
            field=models.ForeignKey(
                related_name="+",
                to="prontuary.ListIndication",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="detaillistindication",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="detailinstitutionalparticipation",
            name="institutionalparticipation",
            field=models.ForeignKey(
                related_name="+",
                to="prontuary.InstitutionalParticipation",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="detailinstitutionalparticipation",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="detailinstitutionalparticipation",
            name="used_edital",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="prontuary.DetailListIndication",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="detailcoursesparticipation",
            name="used_edital",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="prontuary.DetailListIndication",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachmentslistindication",
            name="detaillistindication",
            field=models.ForeignKey(
                related_name="attachments",
                to="prontuary.DetailListIndication",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachmentslistindication",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attachmentsdetailinstitutionalparticipation",
            name="detailinstitutionalparticipation",
            field=models.ForeignKey(
                related_name="attachments",
                to="prontuary.DetailInstitutionalParticipation",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachmentsdetailinstitutionalparticipation",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attachmentsdetailcoursesparticipation",
            name="detailcoursesparticipation",
            field=models.ForeignKey(
                related_name="attachments",
                to="prontuary.DetailCoursesParticipation",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="attachmentsdetailcoursesparticipation",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
