# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import judicial.models
import django.db.models.deletion
from django.conf import settings
import judicial.council.models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0025_auto_20160711_1502"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0003_auto_20151014_1609"),
        ("judicial", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ColegialDecision",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("number", models.SmallIntegerField()),
                ("year", models.SmallIntegerField()),
                (
                    "cached_number",
                    models.CharField(unique=True, max_length=10, db_index=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                judicial.council.models.with_number_for_year,
                "judicial.partlawsuit",
            ),
        ),
        migrations.CreateModel(
            name="ConvocationNotice",
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
                ("number", models.SmallIntegerField()),
                ("year", models.SmallIntegerField()),
                (
                    "cached_number",
                    models.CharField(unique=True, max_length=10, db_index=True),
                ),
                ("convocation_state", models.SmallIntegerField(default=1)),
                ("convocation", models.TextField(null=True)),
                ("cached_convocation", models.TextField(null=True)),
                ("deadline_date", models.DateField(null=True)),
                ("signed_at", models.DateTimeField(null=True)),
            ],
            options={
                "ordering": ("-year", "-number"),
            },
            bases=(
                judicial.models.templated,
                judicial.council.models.with_number_for_year,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Councillor",
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
                    "councillor_type",
                    models.SmallIntegerField(default=1, choices=[(None, b"Nenhum")]),
                ),
                ("incident_type", models.SmallIntegerField(null=True)),
                ("comment", models.TextField(null=True)),
                ("cache_formated_comment", models.TextField(null=True)),
            ],
            options={
                "ordering": (
                    "councillor_type",
                    "possession__servidor__pessoa_fisica__nome",
                ),
            },
        ),
        migrations.CreateModel(
            name="DevolutionRecommendation",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("justification", models.TextField()),
                (
                    "devolution_to",
                    models.ForeignKey(
                        related_name="in_devolution_recommendation",
                        verbose_name="Devolvido para",
                        to="judicial.ExecutionOrgan",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="DistributionRapporteur",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("number", models.SmallIntegerField()),
                ("year", models.SmallIntegerField()),
                (
                    "cached_number",
                    models.CharField(unique=True, max_length=10, db_index=True),
                ),
            ],
            options={
                "permissions": (
                    (
                        "prepare_distribution_rapporteur",
                        "Pode preparar distribui\xe7\xe3o de relatoria",
                    ),
                    (
                        "can_sign_distribution_rapporteur",
                        "Pode assinar distribui\xe7\xe3o",
                    ),
                ),
            },
            bases=(
                judicial.council.models.with_number_for_year,
                "judicial.partlawsuit",
            ),
        ),
        migrations.CreateModel(
            name="DistributionRepporteurScore",
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
                ("total", models.SmallIntegerField(default=0)),
                ("score", models.SmallIntegerField(default=0)),
                (
                    "possession",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.MovimentacaoPosse",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RapporteurDocument",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("rapporteur_vote_type", models.SmallIntegerField(null=True)),
                ("content", models.TextField(null=True)),
                (
                    "from_distribution",
                    models.ForeignKey(
                        related_name="rapporteur_document",
                        to="council.DistributionRapporteur",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Session",
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
                ("number", models.SmallIntegerField()),
                ("year", models.SmallIntegerField()),
                (
                    "cached_number",
                    models.CharField(unique=True, max_length=10, db_index=True),
                ),
                ("session_type", models.SmallIntegerField(null=True)),
                ("session_status", models.SmallIntegerField(null=True)),
                ("expected_date", models.DateField(null=True)),
                (
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(judicial.council.models.with_number_for_year, models.Model),
        ),
        migrations.CreateModel(
            name="SessionItem",
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
                ("title", models.CharField(max_length=200, null=True)),
                ("text", models.TextField()),
                ("flag", models.BooleanField(default=False)),
                (
                    "session",
                    models.ForeignKey(
                        related_name="session_items",
                        to="council.Session",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
        ),
        migrations.CreateModel(
            name="SwitchExecutionOrgan",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("observation", models.TextField()),
                (
                    "execution_organ",
                    models.ForeignKey(
                        related_name="delegations",
                        to="judicial.ExecutionOrgan",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "from_colegial_decision",
                    models.OneToOneField(
                        to="council.ColegialDecision", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "legal_matter",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.LegalMatter",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Vote",
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
                ("invalide", models.BooleanField(default=False)),
                ("vote_type", models.SmallIntegerField(null=True)),
                ("observation", models.TextField(null=True)),
                ("signed_at", models.DateTimeField(null=True)),
                ("rendered_cache", models.TextField(null=True)),
            ],
            options={
                "ordering": ("councillor__possession__servidor__pessoa_fisica__nome",),
            },
        ),
        migrations.CreateModel(
            name="VoteAttached",
            fields=[
                (
                    "attached_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Attached",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.attached",),
        ),
        migrations.CreateModel(
            name="Rapporteur",
            fields=[
                (
                    "vote_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="council.Vote",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("council.vote",),
        ),
        migrations.AddField(
            model_name="voteattached",
            name="vote",
            field=models.ForeignKey(
                related_name="attaches", to="council.Vote", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="vote",
            name="councillor",
            field=models.OneToOneField(
                to="council.Councillor", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="vote",
            name="from_distribution",
            field=models.ForeignKey(
                related_name="rapporteur_votes",
                to="council.DistributionRapporteur",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="vote",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="distributionrapporteur",
            name="part_origin",
            field=models.ForeignKey(
                related_name="has_origin_for_distribution_rapporteur",
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="councillor",
            name="distribution_rapporteur",
            field=models.ForeignKey(
                related_name="votes",
                to="council.DistributionRapporteur",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="councillor",
            name="possession",
            field=models.ForeignKey(
                related_name="+", to="rh.MovimentacaoPosse", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="councillor",
            name="substitute",
            field=models.ForeignKey(
                related_name="+", to="rh.Servidor", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="convocationnotice",
            name="distribution_rapporteur",
            field=models.ForeignKey(
                related_name="convocation_notices",
                on_delete=django.db.models.deletion.PROTECT,
                to="council.DistributionRapporteur",
            ),
        ),
        migrations.AddField(
            model_name="convocationnotice",
            name="publication",
            field=models.ForeignKey(
                related_name="convocation_notices",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="convocationnotice",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="colegialdecision",
            name="from_distribution",
            field=models.OneToOneField(
                to="council.DistributionRapporteur", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="colegialdecision",
            name="part_origin",
            field=models.ForeignKey(
                related_name="has_origin_for_colegial_decision",
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="rapporteurdocument",
            name="rapporteur",
            field=models.OneToOneField(
                related_name="document",
                to="council.Rapporteur",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
