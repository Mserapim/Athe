# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0050_auto_20170725_1836"),
    ]

    operations = [
        migrations.CreateModel(
            name="Relationship",
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
                ("date_start", models.DateField(verbose_name="In\xedcio")),
                (
                    "date_end",
                    models.DateField(null=True, verbose_name="Fim", blank=True),
                ),
                ("app", models.IntegerField(default=1, verbose_name="Aplicativo")),
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
                    "giver",
                    models.ForeignKey(
                        related_name="relationship_giver",
                        verbose_name="Quem d\xe1",
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
                    "receiver",
                    models.ForeignKey(
                        related_name="relationship_receiver",
                        verbose_name="Quem recebe",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "workplace",
                    models.ForeignKey(
                        verbose_name="Lota\xe7\xe3o concedida",
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Rela\xe7\xe3o de Confian\xe7a",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="grau_instrucao",
            field=models.IntegerField(
                default=8,
                verbose_name="Grau de Instru\xe7\xe3o",
                choices=[
                    (1, "ANALFABETO"),
                    (2, "ALFABETIZADO SEM CURSOS REGULARES"),
                    (3, "SERA EXCLUIDO 4"),
                    (4, "FUNDAMENTAL COMPLETO"),
                    (5, "M\xc9DIO INCOMPLETO"),
                    (6, "MEDIO COMPLETO OU EQUIVALENTE LEGAL"),
                    (7, "SUPERIOR INCOMPLETO"),
                    (8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"),
                    (9, "ESPECIALIZA\xc7\xc3O/P\xd3S"),
                    (10, "MESTRADO"),
                    (11, "DOUTORADO"),
                    (12, "SERA EXCLUIDO"),
                    (13, "SERA EXCLUIDO 1"),
                    (14, "SERA EXCLUIDO 2"),
                    (15, "AT\xc9 O 5o ANO INCOMPLETO DO ENSINO FUNDAMENTAL"),
                    (16, "5o ANO COMPLETO DO ENSINO FUNDAMENTAL"),
                    (17, "DO 6o AO 9o ANO DO ENSINO FUNDAMENTAL INCOMPLETO"),
                    (18, "N\xc3O INFORMADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="telefone",
            name="tipo_telefone",
            field=models.IntegerField(
                verbose_name="Tipo de Telefone",
                choices=[
                    (1, "RESIDENCIAL"),
                    (2, "COMERCIAL"),
                    (3, "CELULAR"),
                    (4, "FAX"),
                    (5, "INSTITUCIONAL"),
                    (6, "EMERGENCIAL"),
                ],
            ),
        ),
    ]
