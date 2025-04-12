# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        # ('ged', '0003_auto_20150901_1428'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0006_auto_20150921_1434"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "endereco_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Endereco",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "start_date",
                    models.DateField(
                        null=True,
                        verbose_name="Data In\xedcio Resid\xeancia",
                        blank=True,
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        null=True, verbose_name="Data Fim Resid\xeancia", blank=True
                    ),
                ),
                (
                    "type_residence",
                    models.SmallIntegerField(
                        default=0,
                        null=True,
                        verbose_name="Tipo de Resid\xeancia",
                        choices=[(1, "CASA"), (2, "APARTAMENTO")],
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status",
                        choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
                    ),
                ),
                (
                    "status_pendency",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status Pend\xeancia",
                        choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
                    ),
                ),
                (
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Anexo",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
            },
            bases=("rh.endereco",),
        ),
        migrations.CreateModel(
            name="CodeDebtsEncumbrances",
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
                    "code",
                    models.SmallIntegerField(default="0", verbose_name="C\xf3digo"),
                ),
                (
                    "title",
                    models.CharField(
                        default="", max_length=300, verbose_name="T\xedtulo"
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
                "ordering": ("code",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CodeProperty",
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
                    "code",
                    models.SmallIntegerField(default="0", verbose_name="C\xf3digo"),
                ),
                (
                    "title",
                    models.CharField(
                        default="", max_length=300, verbose_name="T\xedtulo"
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
                "ordering": ("code",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ControlInformationMember",
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
                        verbose_name="Status",
                        choices=[(1, "ATIVO"), (2, "FINALIZADO")],
                    ),
                ),
                (
                    "flag_not_exercise_teaching",
                    models.BooleanField(
                        default=False,
                        verbose_name="N\xe3o exerce atividade de doc\xeancia",
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
                    "employee",
                    models.ForeignKey(
                        related_name="controlinformation",
                        verbose_name="Membro",
                        to="rh.MovimentacaoPosse",
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
                        verbose_name="Controle Anterior",
                        blank=True,
                        to="cif.ControlInformationMember",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("employee__servidor",),
                "permissions": (
                    ("cif_admin", "Administrador de Informa\xe7\xf5es Membros"),
                    ("cif_membro", "Membro usu\xe1rio"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DebtsEncumbrances",
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
                    "description",
                    models.TextField(default="", verbose_name="Descri\xe7\xe3o"),
                ),
                (
                    "kind",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="TIPO DE BEM",
                        choices=[
                            (1, "INDIVIDUAL"),
                            (2, "C\xd4NJUGE"),
                            (3, "DEPENDENTE"),
                        ],
                    ),
                ),
                (
                    "last_value",
                    models.DecimalField(
                        default=0,
                        null=True,
                        verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "current_value",
                    models.DecimalField(
                        verbose_name="Situa\xe7\xe3o Atual (R$)",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status",
                        choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
                    ),
                ),
                (
                    "status_pendency",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status Pend\xeancia",
                        choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
                    ),
                ),
                (
                    "code",
                    models.ForeignKey(
                        related_name="debtsencumbrances",
                        verbose_name="C\xf3digo",
                        to="cif.CodeDebtsEncumbrances",
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
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Anexo",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "member",
                    models.ForeignKey(
                        related_name="debtsencumbrances",
                        verbose_name="Membro",
                        to="cif.ControlInformationMember",
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
                "ordering": ("-id",),
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
                (
                    "name",
                    models.CharField(unique=True, max_length=350, verbose_name="Nome"),
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
            options={},
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="EducationalInstitution",
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
                        to="rh.Localidade", null=True, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("rh.pessoajuridica",),
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
                (
                    "description",
                    models.TextField(default="", verbose_name="Descri\xe7\xe3o"),
                ),
                (
                    "kind",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="TIPO DE BEM",
                        choices=[
                            (1, "INDIVIDUAL"),
                            (2, "C\xd4NJUGE"),
                            (3, "DEPENDENTE"),
                        ],
                    ),
                ),
                (
                    "last_value",
                    models.DecimalField(
                        default=0,
                        null=True,
                        verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "current_value",
                    models.DecimalField(
                        verbose_name="Situa\xe7\xe3o Atual (R$)",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status",
                        choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
                    ),
                ),
                (
                    "status_pendency",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status Pend\xeancia",
                        choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
                    ),
                ),
                (
                    "code",
                    models.ForeignKey(
                        related_name="property",
                        verbose_name="C\xf3digo",
                        to="cif.CodeProperty",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "country",
                    models.ForeignKey(
                        verbose_name="Pa\xeds", to="rh.Pais", on_delete=models.CASCADE
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
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Anexo",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "member",
                    models.ForeignKey(
                        related_name="property",
                        verbose_name="Membro",
                        to="cif.ControlInformationMember",
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
                "ordering": ("-id",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ReferencePeriod",
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
                    "exercise",
                    models.CharField(
                        default="0",
                        max_length=50,
                        verbose_name="Per\xedodo de Exer\xedcio",
                    ),
                ),
                (
                    "exercise_year",
                    models.IntegerField(
                        default=0, verbose_name="Per\xedodo de Exer\xedcio"
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio Exer\xedcio", blank=True
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        null=True, verbose_name="Data Fim Exer\xedcio", blank=True
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
                (
                    "previous_referenceperiod",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Per\xedodo Anterior",
                        blank=True,
                        to="cif.ReferencePeriod",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
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
                        default=0,
                        null=True,
                        verbose_name="Dia da Semana",
                        choices=[
                            (0, "N\xe3o informado"),
                            (1, "SEGUNDA-FEIRA"),
                            (2, "TER\xc7A-FEIRA"),
                            (3, "QUARTA-FEIRA"),
                            (4, "QUINTA-FEIRA"),
                            (5, "SEXTA-FEIRA"),
                            (6, "S\xc1BADO"),
                            (7, "DOMINGO"),
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
                "ordering": ("day_week",),
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
                (
                    "work_hours",
                    models.SmallIntegerField(
                        default="0", verbose_name="Carga Hor\xe1ria"
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio Doc\xeancia", blank=True
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        null=True, verbose_name="Data Fim Doc\xeancia", blank=True
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status",
                        choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
                    ),
                ),
                (
                    "status_pendency",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status Pend\xeancia",
                        choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
                    ),
                ),
                (
                    "authorization",
                    models.BooleanField(
                        default=True,
                        verbose_name="Autoriza\xe7\xe3o para dar aula fora da comarca",
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
                        related_name="teaching",
                        verbose_name="Disciplina",
                        to="cif.Discipline",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "educational_institution",
                    models.ForeignKey(
                        related_name="teaching",
                        verbose_name="Institui\xe7\xe3o de Ensino",
                        to="cif.EducationalInstitution",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Anexo",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "member",
                    models.ForeignKey(
                        related_name="teaching",
                        verbose_name="Membro",
                        to="cif.ControlInformationMember",
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
                        related_name="teaching",
                        null=True,
                        verbose_name="Hor\xe1rios",
                        to="cif.Schedule",
                    ),
                ),
            ],
            options={
                "ordering": ("-id",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="referenceperiod",
            field=models.ForeignKey(
                related_name="controlinformation",
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="address",
            name="member",
            field=models.ForeignKey(
                related_name="address",
                verbose_name="Membro",
                to="cif.ControlInformationMember",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="address",
            name="previus_addres",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Endere\xe7o Anterior",
                blank=True,
                to="cif.Address",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
