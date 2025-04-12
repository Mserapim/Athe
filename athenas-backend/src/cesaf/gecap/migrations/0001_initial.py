# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AreaConhecimento",
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
                ("titulo", models.CharField(max_length=200)),
                ("codigo_cnpq", models.SmallIntegerField(null=True, blank=True)),
                (
                    "cache_codigo_cnpq",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
            ],
            options={
                "ordering": ["titulo", "codigo_cnpq"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Capacitacao",
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
                ("nome", models.CharField(max_length=60, verbose_name="Nome")),
                (
                    "dt_inicio",
                    models.DateField(
                        null=True, verbose_name="Data de inicio", blank=True
                    ),
                ),
                (
                    "dt_fim",
                    models.DateField(null=True, verbose_name="Data de fim", blank=True),
                ),
                ("carga_horaria", models.IntegerField(null=True, blank=True)),
                (
                    "promovido_por",
                    models.IntegerField(
                        choices=[(1, "CESAF"), (2, "CESAF E TERCEIRO"), (3, "TERCEIRO")]
                    ),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                (
                    "ementa",
                    models.TextField(null=True, verbose_name="Ementa", blank=True),
                ),
                (
                    "publicar",
                    models.BooleanField(default=False, verbose_name="Publicar no site"),
                ),
                (
                    "descricao",
                    models.TextField(
                        null=True,
                        verbose_name="Descri\xe7\xe3o para o Site",
                        blank=True,
                    ),
                ),
                ("inscricao_inicio", models.DateTimeField(null=True, blank=True)),
                ("inscricao_fim", models.DateTimeField(null=True, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Congresso",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Curso",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Evento",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Feira",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Inscricao",
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
                ("homologado", models.DateTimeField(null=True, blank=True)),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Investimento",
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
                ("descricao", models.CharField(max_length=60)),
                ("valor", models.DecimalField(max_digits=18, decimal_places=2)),
                ("previsao", models.BooleanField(default=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Oficina",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Reuniao",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.CreateModel(
            name="Seminario",
            fields=[
                (
                    "capacitacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="gecap.Capacitacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("gecap.capacitacao",),
        ),
        migrations.AddField(
            model_name="investimento",
            name="capacitacao",
            field=models.ForeignKey(
                related_name="investimentos",
                blank=True,
                to="gecap.Capacitacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="investimento",
            name="inscricao",
            field=models.ForeignKey(
                related_name="investimentos",
                blank=True,
                to="gecap.Inscricao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="inscricao",
            name="capacitacao",
            field=models.ForeignKey(
                related_name="inscricoes",
                to="gecap.Capacitacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
