# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0007_auto_20160328_1728"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="file_document",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Anexo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="address",
            name="refperiod_address",
            field=models.ForeignKey(
                related_name="ref_address",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                blank=True,
                to="cif.ReferencePeriod",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status",
                blank=True,
                choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="status_pendency",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status Pend\xeancia",
                blank=True,
                choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="type_residence",
            field=models.SmallIntegerField(
                default=0,
                null=True,
                verbose_name="Tipo de Resid\xeancia",
                blank=True,
                choices=[(1, "CASA"), (2, "APARTAMENTO")],
            ),
        ),
        migrations.AlterField(
            model_name="codedebtsencumbrances",
            name="code",
            field=models.SmallIntegerField(
                default="0", null=True, verbose_name="C\xf3digo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="codedebtsencumbrances",
            name="title",
            field=models.CharField(
                default="",
                max_length=300,
                null=True,
                verbose_name="T\xedtulo",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="codeproperty",
            name="code",
            field=models.SmallIntegerField(
                default="0", null=True, verbose_name="C\xf3digo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="codeproperty",
            name="title",
            field=models.CharField(
                default="",
                max_length=300,
                null=True,
                verbose_name="T\xedtulo",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="controlinformationmember",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status",
                blank=True,
                choices=[(1, "ATIVO"), (2, "FINALIZADO")],
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="code",
            field=models.ForeignKey(
                related_name="debtsencumbrances",
                verbose_name="C\xf3digo",
                blank=True,
                to="cif.CodeDebtsEncumbrances",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="description",
            field=models.TextField(
                default="", null=True, verbose_name="Descri\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="file_document",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Anexo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="kind",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="TIPO DE BEM",
                blank=True,
                choices=[(1, "INDIVIDUAL"), (2, "C\xd4NJUGE"), (3, "DEPENDENTE")],
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="last_value",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=18,
                blank=True,
                null=True,
                verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="member",
            field=models.ForeignKey(
                related_name="debtsencumbrances",
                verbose_name="Membro",
                blank=True,
                to="cif.ControlInformationMember",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="refperiod_debts",
            field=models.ForeignKey(
                related_name="ref_debts",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                blank=True,
                to="cif.ReferencePeriod",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status",
                blank=True,
                choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
            ),
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="status_pendency",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status Pend\xeancia",
                blank=True,
                choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="code",
            field=models.ForeignKey(
                related_name="property",
                verbose_name="C\xf3digo",
                blank=True,
                to="cif.CodeProperty",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="property",
            name="country",
            field=models.ForeignKey(
                verbose_name="Pa\xeds",
                blank=True,
                to="rh.Pais",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="property",
            name="description",
            field=models.TextField(
                default="", null=True, verbose_name="Descri\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="file_document",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Anexo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="property",
            name="kind",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="TIPO DE BEM",
                blank=True,
                choices=[(1, "INDIVIDUAL"), (2, "C\xd4NJUGE"), (3, "DEPENDENTE")],
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="last_value",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=18,
                blank=True,
                null=True,
                verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="member",
            field=models.ForeignKey(
                related_name="property",
                verbose_name="Membro",
                blank=True,
                to="cif.ControlInformationMember",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="property",
            name="refperiod_property",
            field=models.ForeignKey(
                related_name="ref_property",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                blank=True,
                to="cif.ReferencePeriod",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status",
                blank=True,
                choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="status_pendency",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status Pend\xeancia",
                blank=True,
                choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="exercise",
            field=models.CharField(
                default="0",
                max_length=50,
                null=True,
                verbose_name="Per\xedodo de Exerc\xedcio",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="exercise_year",
            field=models.IntegerField(
                default=0,
                null=True,
                verbose_name="Per\xedodo de Exerc\xedcio",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="day_week",
            field=models.SmallIntegerField(
                default=0,
                null=True,
                verbose_name="Dia da Semana",
                blank=True,
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
        migrations.AlterField(
            model_name="teaching",
            name="discipline",
            field=models.ForeignKey(
                related_name="teaching",
                verbose_name="Disciplina",
                blank=True,
                to="cif.Discipline",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="teaching",
            name="educational_institution",
            field=models.ForeignKey(
                related_name="teaching",
                verbose_name="Institui\xe7\xe3o de Ensino",
                blank=True,
                to="cif.EducationalInstitution",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="teaching",
            name="file_document",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Anexo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="teaching",
            name="refperiod_teaching",
            field=models.ForeignKey(
                related_name="ref_teaching",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                blank=True,
                to="cif.ReferencePeriod",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="schedule",
            field=models.ManyToManyField(
                related_name="teaching",
                null=True,
                verbose_name="Hor\xe1rios",
                to="cif.Schedule",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status",
                blank=True,
                choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="status_pendency",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status Pend\xeancia",
                blank=True,
                choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="work_hours",
            field=models.SmallIntegerField(
                default="0", null=True, verbose_name="Carga Hor\xe1ria", blank=True
            ),
        ),
    ]
