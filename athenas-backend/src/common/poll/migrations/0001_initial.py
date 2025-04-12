# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BlackList",
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
                    "blocked_users",
                    models.ManyToManyField(
                        related_name="safe_poll_blacklists", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Choice",
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
                    "choice",
                    models.CharField(max_length=300, verbose_name="Alternativa"),
                ),
                (
                    "meta",
                    models.BooleanField(
                        default=False,
                        db_index=True,
                        verbose_name="Meta op\xc3\xa7\xc3\xa3o de voto",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Poll",
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
                    "title",
                    models.CharField(
                        max_length=300,
                        verbose_name="T\xc3\xadtulo da vota\xc3\xa7\xc3\xa3o",
                    ),
                ),
                (
                    "max_of_choices",
                    models.IntegerField(
                        default=1,
                        verbose_name="Quantidade de votos permitidos",
                        db_index=True,
                    ),
                ),
                (
                    "publication_start",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Inicio da publica\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "publication_end",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Fim da publica\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Data de cria\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativa"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PollConditions",
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
                ("expression", models.CharField(max_length=300)),
                ("value", models.CharField(max_length=300, null=True)),
                ("description", models.CharField(max_length=300)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Votes",
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
                ("counted", models.BooleanField(default=False, db_index=True)),
                ("authentic", models.BooleanField(default=False, db_index=True)),
                ("signature", models.CharField(max_length=300)),
                (
                    "choice",
                    models.ForeignKey(
                        related_name="votes", to="poll.Choice", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "poll",
                    models.ForeignKey(
                        related_name="votes", to="poll.Poll", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="poll",
            name="conditions",
            field=models.ManyToManyField(
                related_name="polls", to="poll.PollConditions"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="poll",
            name="users_who_voted",
            field=models.ManyToManyField(
                related_name="safe_poll_voted", to=settings.AUTH_USER_MODEL
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="choice",
            name="poll",
            field=models.ForeignKey(
                related_name="choices",
                verbose_name="Enquete",
                to="poll.Poll",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="blacklist",
            name="poll",
            field=models.OneToOneField(
                related_name="blacklist",
                null=True,
                to="poll.Poll",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
