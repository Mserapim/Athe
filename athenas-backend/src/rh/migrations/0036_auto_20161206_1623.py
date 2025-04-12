# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0035_auto_20161201_1606"),
    ]

    operations = [
        migrations.CreateModel(
            name="CharacteristicWorkplace",
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
                ("name", models.CharField(max_length=200, verbose_name="Nome")),
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
                "verbose_name": "Propriedade da Lota\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="cargoquadro",
            name="carga_horaria",
            field=models.IntegerField(default=40, verbose_name="Carga Hor\xe1ria"),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="dado_bancario",
            field=models.ManyToManyField(
                related_name="dados_bancarios_pessoas",
                verbose_name="Dado Banc\xe1rio",
                to="rh.DadoBancario",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="documento",
            field=models.ManyToManyField(to="rh.Documento", blank=True),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="necessidades_especiais",
            field=models.ManyToManyField(
                related_name="pessoafisica", to="rh.NecessidadeEspecial", blank=True
            ),
        ),
        migrations.AddField(
            model_name="lotacao",
            name="characteristic",
            field=models.ForeignKey(
                verbose_name="Caracter\xedstica",
                blank=True,
                to="rh.CharacteristicWorkplace",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
