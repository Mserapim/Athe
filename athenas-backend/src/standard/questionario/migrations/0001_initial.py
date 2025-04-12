# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Alternativa",
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
                ("label", models.CharField(default="", max_length=100, null=True)),
                ("texto", models.TextField(blank=True)),
                ("valor", models.CharField(max_length=5, blank=True)),
                ("grupo", models.CharField(max_length=50, null=True, blank=True)),
                ("ordem", models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                "ordering": ("ordem",),
                "db_table": "qst_alternativa",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Elemento",
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
                ("object_id", models.PositiveIntegerField()),
                ("ordem", models.PositiveSmallIntegerField(null=True)),
                ("label", models.CharField(max_length=50)),
                ("grupo", models.CharField(max_length=50, null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "elemento_pai",
                    models.ForeignKey(
                        related_name="pai_elemento",
                        blank=True,
                        to="questionario.Elemento",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("ordem",),
                "db_table": "qst_elemento",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Questao",
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
                ("enunciado", models.TextField()),
                ("mista", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "qst_questao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="QuestaoAberta",
            fields=[
                (
                    "questao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="questionario.Questao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_questaoaberta",
            },
            bases=("questionario.questao",),
        ),
        migrations.CreateModel(
            name="QuestaoMS",
            fields=[
                (
                    "questao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="questionario.Questao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_questaoms",
            },
            bases=("questionario.questao",),
        ),
        migrations.CreateModel(
            name="QuestaoEnum",
            fields=[
                (
                    "questaoms_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="questionario.QuestaoMS",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("valores", models.CharField(default="1:1", max_length=100)),
            ],
            options={
                "db_table": "qst_questaoenum",
            },
            bases=("questionario.questaoms",),
        ),
        migrations.CreateModel(
            name="Questionario",
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
                ("titulo", models.CharField(max_length=50)),
                ("descricao", models.TextField(default="")),
                ("data_inicio", models.DateField()),
                ("data_fim", models.DateField(null=True, blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modificado_em", models.DateTimeField(auto_now=True)),
                ("ativo", models.BooleanField(default=True)),
                ("unico", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["-ativo", "titulo"],
                "db_table": "qst_questionario",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="QuestionarioChave",
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
                ("chave", models.CharField(max_length=100)),
                (
                    "questionario",
                    models.ForeignKey(
                        to="questionario.Questionario", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_questionariochave",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="QuestionarioResposta",
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
                ("chave", models.CharField(max_length=64)),
                ("criado_em", models.DateField(auto_now_add=True)),
                (
                    "questionario",
                    models.ForeignKey(
                        to="questionario.Questionario", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_questionarioresposta",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenciaTextual",
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
                ("label", models.CharField(max_length=100)),
                ("conteudo", models.TextField(default="")),
            ],
            options={
                "ordering": ("label",),
                "db_table": "qst_referenciatextual",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Resposta",
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
                ("texto", models.TextField(default="")),
                ("peso", models.IntegerField(default=0)),
                (
                    "alternativa",
                    models.ForeignKey(
                        blank=True,
                        to="questionario.Alternativa",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "questao",
                    models.ForeignKey(
                        to="questionario.Questao", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "questionario_resposta",
                    models.ForeignKey(
                        to="questionario.QuestionarioResposta", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_resposta",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="RespostaQuestao",
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
                ("texto", models.TextField(default="")),
            ],
            options={
                "db_table": "qst_respostaquestao",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="RespostaQuestaoAberta",
            fields=[
                (
                    "respostaquestao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="questionario.RespostaQuestao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_resposta_questao_aberta",
            },
            bases=("questionario.respostaquestao",),
        ),
        migrations.CreateModel(
            name="RespostaQuestaoMS",
            fields=[
                (
                    "respostaquestao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="questionario.RespostaQuestao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "qst_resposta_questao_ms",
            },
            bases=("questionario.respostaquestao",),
        ),
        migrations.AddField(
            model_name="respostaquestao",
            name="content_type",
            field=models.ForeignKey(
                to="contenttypes.ContentType", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="respostaquestao",
            name="questao",
            field=models.ForeignKey(
                to="questionario.Questao", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="respostaquestao",
            name="questionario_resposta",
            field=models.ForeignKey(
                to="questionario.QuestionarioResposta", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="respostaquestao",
            unique_together=set([("questao", "questionario_resposta")]),
        ),
        migrations.AlterUniqueTogether(
            name="questionariochave",
            unique_together=set([("chave", "questionario")]),
        ),
        migrations.AddField(
            model_name="questao",
            name="content_type",
            field=models.ForeignKey(
                to="contenttypes.ContentType", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="elemento",
            name="questionario",
            field=models.ForeignKey(
                to="questionario.Questionario", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="elemento",
            unique_together=set([("object_id", "content_type")]),
        ),
        migrations.AddField(
            model_name="alternativa",
            name="questao",
            field=models.ForeignKey(
                related_name="alternativas",
                to="questionario.Questao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
