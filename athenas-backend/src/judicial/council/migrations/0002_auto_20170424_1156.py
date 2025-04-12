# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import judicial.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0014_movimentacao_physical"),
        ("council", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConvocationNoticeLegalSign",
            fields=[
                (
                    "legalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.LegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(judicial.models.JudicialLegalSign, "protocolo.legalsign"),
        ),
        migrations.AlterField(
            model_name="colegialdecision",
            name="cached_number",
            field=models.CharField(
                db_index=True, unique=True, max_length=10, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="colegialdecision",
            name="number",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="colegialdecision",
            name="part_origin",
            field=models.ForeignKey(
                related_name="has_origin_for_colegial_decision",
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="colegialdecision",
            name="year",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="cached_convocation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="cached_number",
            field=models.CharField(
                db_index=True, unique=True, max_length=10, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="convocation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="convocation_state",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Editando"),
                    (2, "Publicando"),
                    (3, "Publicado"),
                    (4, "Descartado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="deadline_date",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="number",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="publication",
            field=models.ForeignKey(
                related_name="convocation_notices",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="signed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="convocationnotice",
            name="year",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="councillor",
            name="cache_formated_comment",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="councillor",
            name="comment",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="councillor",
            name="councillor_type",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (None, b"Nenhum"),
                    (1, "Presidente"),
                    (2, "Corregedor"),
                    (3, "Membro"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="councillor",
            name="incident_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (101, "Conex\xe3o"),
                    (102, "Preven\xe7\xe3o"),
                    (201, "Impedimento"),
                    (202, "Suspei\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="councillor",
            name="substitute",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="distributionrapporteur",
            name="cached_number",
            field=models.CharField(
                db_index=True, unique=True, max_length=10, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="distributionrapporteur",
            name="number",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="distributionrapporteur",
            name="part_origin",
            field=models.ForeignKey(
                related_name="has_origin_for_distribution_rapporteur",
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="distributionrapporteur",
            name="year",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="rapporteurdocument",
            name="content",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="rapporteurdocument",
            name="rapporteur_vote_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "A favor do pedido"),
                    (2, "Contra o pedido"),
                    (201, "Declarar Impedimento"),
                    (202, "Declarar Suspei\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="cached_number",
            field=models.CharField(
                db_index=True, unique=True, max_length=10, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="expected_date",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="session",
            name="file_document",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="session",
            name="number",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="session",
            name="session_status",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="session",
            name="session_type",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="session",
            name="year",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="sessionitem",
            name="title",
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="switchexecutionorgan",
            name="execution_organ",
            field=models.ForeignKey(
                related_name="delegations",
                blank=True,
                to="judicial.ExecutionOrgan",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="switchexecutionorgan",
            name="legal_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="vote",
            name="observation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="vote",
            name="rendered_cache",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="vote",
            name="signed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="vote",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="vote",
            name="vote_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Homologado"),
                    (2, "N\xe3o homologado"),
                    (3, "Absten\xe7\xe3o"),
                    (4, "Homologado parcialmente"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="convocationnoticelegalsign",
            name="convocation",
            field=models.ForeignKey(
                related_name="legal_signs",
                to="council.ConvocationNotice",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
