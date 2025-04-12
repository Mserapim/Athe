# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Common",
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
                ("name", models.CharField(max_length=200)),
                ("description", models.CharField(max_length=500, null=True)),
                ("active", models.BooleanField(default=True, db_index=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Edge",
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
                ("slug", models.SlugField(max_length=200)),
                ("edge_hash", models.CharField(max_length=32, db_index=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Joker",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.common",),
        ),
        migrations.CreateModel(
            name="Vertex",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("acronym", models.CharField(max_length=40)),
                ("kind", models.CharField(max_length=200)),
                ("beginning", models.BooleanField(default=False, db_index=True)),
            ],
            options={},
            bases=("workflow.common",),
        ),
        migrations.CreateModel(
            name="ServidorVertex",
            fields=[
                (
                    "vertex_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Vertex",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "objective",
                    models.ForeignKey(
                        related_name="vertices",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.vertex",),
        ),
        migrations.CreateModel(
            name="PessoaVertex",
            fields=[
                (
                    "vertex_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Vertex",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "objective",
                    models.ForeignKey(
                        related_name="vertices",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.vertex",),
        ),
        migrations.CreateModel(
            name="LotacaoVertex",
            fields=[
                (
                    "vertex_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Vertex",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "objective",
                    models.ForeignKey(
                        related_name="vertices",
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.vertex",),
        ),
        migrations.CreateModel(
            name="JokerVertex",
            fields=[
                (
                    "vertex_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Vertex",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "objective",
                    models.ForeignKey(
                        related_name="vertices",
                        to="workflow.Joker",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.vertex",),
        ),
        migrations.CreateModel(
            name="Workflow",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("workflow.common",),
        ),
        migrations.AddField(
            model_name="vertex",
            name="vertices",
            field=models.ManyToManyField(
                related_name="backward_vertices",
                null=True,
                through="workflow.Edge",
                to="workflow.Vertex",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="vertex",
            name="workflow",
            field=models.ForeignKey(
                related_name="vertices",
                to="workflow.Workflow",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="edge",
            name="source",
            field=models.ForeignKey(
                related_name="source_edge",
                to="workflow.Vertex",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="edge",
            name="target",
            field=models.ForeignKey(
                related_name="target_edge",
                to="workflow.Vertex",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="edge",
            unique_together=set([("slug", "source", "target")]),
        ),
    ]
