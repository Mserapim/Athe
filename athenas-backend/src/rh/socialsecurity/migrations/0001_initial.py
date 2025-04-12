# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0006_auto_20150921_1434"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmploymentBond",
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
                    "employer",
                    models.CharField(max_length=256, verbose_name="Empregador"),
                ),
                (
                    "pension_system",
                    models.PositiveSmallIntegerField(
                        verbose_name="Regime previdenci\xe1rio",
                        choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
                    ),
                ),
                (
                    "public_employee",
                    models.BooleanField(
                        default=False, verbose_name="Servidor p\xfablico"
                    ),
                ),
                (
                    "contribution_double",
                    models.BooleanField(
                        default=False, verbose_name="Contribui\xe7\xe3o em dobro"
                    ),
                ),
                ("begin_date", models.DateField(verbose_name="In\xedcio")),
                ("end_date", models.DateField(null=True, verbose_name="T\xe9rmino")),
                (
                    "deduction",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Dedu\xe7\xf5es"
                    ),
                ),
                (
                    "liquid_days",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Tempo l\xedquido"
                    ),
                ),
                (
                    "archive",
                    models.CharField(
                        max_length=256, verbose_name="Arquivo", blank=True
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
                    "possession",
                    models.ForeignKey(
                        related_name="employmentbonds",
                        null=True,
                        verbose_name="Movimenta\xe7\xe3o de Posse",
                        to="rh.MovimentacaoPosse",
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["begin_date"],
                "db_table": "ss_employmentbond",
                "verbose_name": "V\xednculos empregat\xedcios",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="RetirementPrevision",
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
                (
                    "age_prevision_date",
                    models.DateField(verbose_name="Data da aposentadoria por idade"),
                ),
                (
                    "contribution_prevision_date",
                    models.DateField(
                        verbose_name="Data da aposentadoria por contribui\xe7\xe3o"
                    ),
                ),
                (
                    "integral_prevision_date",
                    models.DateField(verbose_name="Data da aposentadoria integral"),
                ),
                ("active", models.BooleanField(default=False, verbose_name="Ativo?")),
                (
                    "before_ec_20_98",
                    models.BooleanField(
                        default=False,
                        verbose_name="V\xednculo p\xfablico anterior a EC 20 de 1998",
                    ),
                ),
                (
                    "exercise_date",
                    models.DateField(null=True, verbose_name="Primeiro emprego"),
                ),
                (
                    "last_occupation",
                    models.ForeignKey(
                        related_name="retirementprevisions",
                        verbose_name="\xc3\x9altima ocupa\xc3\xa7\xc3\xa3o",
                        to="rh.Quadro",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "natural_person",
                    models.ForeignKey(
                        related_name="retirementprevisions",
                        verbose_name="Pessoa f\xedsica",
                        to="rh.PessoaFisica",
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["integral_prevision_date"],
                "db_table": "ss_retirementprevision",
                "verbose_name": "Previs\xe3o de Aposentadoria",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="employmentbond",
            name="retirement_prevision",
            field=models.ForeignKey(
                related_name="employmentbonds",
                verbose_name="Aposentadoria",
                to="socialsecurity.RetirementPrevision",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="employmentbond",
            unique_together=set([("employer", "pension_system", "possession")]),
        ),
    ]
