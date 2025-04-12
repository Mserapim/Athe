# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("questionario", "0001_initial"),
        ("rh", "0031_auto_20160818_0946"),
    ]

    operations = [
        migrations.CreateModel(
            name="Commission",
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
                    "start_date",
                    models.DateField(verbose_name="Data In\xedcio", blank=True),
                ),
                (
                    "end_date",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
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
                    "previus_commission",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Comiss\xe3o Anterior",
                        blank=True,
                        to="apd.Commission",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "publication",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Publica\xe7\xe3o",
                        to="rh.Publicacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Configuration",
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
                    "start_date",
                    models.DateField(verbose_name="Data In\xedcio", blank=True),
                ),
                (
                    "end_date",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "porcentage_approval",
                    models.DecimalField(
                        verbose_name="Porcentagem de Aprova\xe7\xe3o",
                        max_digits=5,
                        decimal_places=2,
                    ),
                ),
                (
                    "deadline_appeal",
                    models.SmallIntegerField(
                        default="0", verbose_name="Dias para Interpor Recurso"
                    ),
                ),
                (
                    "deadline_judge_resource",
                    models.SmallIntegerField(
                        default="0", verbose_name="Dias para comiss\xe3o julgar recurso"
                    ),
                ),
                (
                    "deadline_reconsideration",
                    models.SmallIntegerField(
                        default="0",
                        verbose_name="Dias para Solicitar a Reconsidera\xe7\xe3o de Avalia\xe7\xe3o",
                    ),
                ),
                (
                    "deadline_rectify_evaluation",
                    models.SmallIntegerField(
                        default="0",
                        verbose_name="Dias para o chefe retificar Avalia\xe7\xe3o",
                    ),
                ),
                (
                    "deadline_rectification_commission",
                    models.SmallIntegerField(
                        default="0",
                        verbose_name="Dias para Comiss\xe3o realizar retifica\xe7\xe3o da nota",
                    ),
                ),
                (
                    "deadline_science_resul_evaluation",
                    models.SmallIntegerField(
                        default="0",
                        verbose_name="Dias para avaliado dar ciente do resultado da avalia\xe7\xe3o",
                    ),
                ),
                (
                    "interval_periodic_evaluation",
                    models.SmallIntegerField(
                        default="0",
                        verbose_name="Intervalo de Avalia\xe7\xf5es em Meses",
                    ),
                ),
                (
                    "instructions",
                    models.TextField(
                        default="", verbose_name="Instru\xe7\xf5es da APD"
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
                    "previus_configuration",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Configura\xe7\xe3o Anterior",
                        blank=True,
                        to="apd.Configuration",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "publication",
                    models.ForeignKey(
                        related_name="publication_apd",
                        verbose_name="Publica\xe7\xe3o",
                        to="rh.Publicacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "questionnaire_boss",
                    models.ForeignKey(
                        related_name="boss_apd",
                        verbose_name="Question\xe1rio Avalidor",
                        to="questionario.Questionario",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "questionnaire_subordinate",
                    models.ForeignKey(
                        related_name="subordinate_apd",
                        verbose_name="Question\xe1rio Avaliado",
                        blank=True,
                        to="questionario.Questionario",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DecisionCommission",
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
                    "decision",
                    models.CharField(
                        max_length=1,
                        verbose_name="Decis\xe3o do Recurso",
                        choices=[
                            ("1", "DAR PROVIDO RECURSO"),
                            ("2", "N\xc3O DAR PROVIDO RECURSO"),
                        ],
                    ),
                ),
                (
                    "text",
                    models.TextField(default="", verbose_name="Observa\xe7\xf5es"),
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
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Evaluation",
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
                    "start_period_evaluation",
                    models.DateField(
                        verbose_name="Data In\xedcio Per\xedodo", blank=True
                    ),
                ),
                (
                    "end_period_evaluation",
                    models.DateField(verbose_name="Data Fim Per\xedodo", blank=True),
                ),
                (
                    "days_suspended_evaluation",
                    models.DecimalField(
                        default=0, null=True, max_digits=5, decimal_places=2
                    ),
                ),
                ("reconsideration_flag", models.BooleanField(default=False)),
                (
                    "repetition_flag",
                    models.BooleanField(
                        default=False,
                        verbose_name="Nota repetida de outra avalia\xe7\xe3o",
                    ),
                ),
                (
                    "text_reconsideration",
                    models.TextField(
                        default="",
                        verbose_name="Texto do pedido de reconsidera\xe7\xe3o",
                    ),
                ),
                (
                    "date_reconsideration",
                    models.DateField(
                        null=True,
                        verbose_name="Data solicitada a reconsidera\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "opinion_request_reconsideration",
                    models.TextField(
                        default="",
                        verbose_name="Parecer do avaliador quanto ao pedido de reconsidera\xe7\xe3o do avaliado",
                    ),
                ),
                (
                    "date_opinion_request_reconsideration",
                    models.DateField(
                        null=True,
                        verbose_name="Data do parecer do avaliador quanto ao pedido de reconsidera\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "text_justification_repetition",
                    models.TextField(
                        default="",
                        verbose_name="Texto do motivo da repeti\xe7\xe3o de avalia\xe7\xe3o",
                    ),
                ),
                (
                    "external_evaluator",
                    models.TextField(
                        null=True,
                        verbose_name="Avaliador de \xd3rg\xe3o Externo",
                        blank=True,
                    ),
                ),
                (
                    "external_registration",
                    models.TextField(
                        null=True,
                        verbose_name="Matricula do Avaliador de \xd3rg\xe3o Externo",
                        blank=True,
                    ),
                ),
                (
                    "external_jobposition",
                    models.TextField(
                        null=True,
                        verbose_name="Cargo do Avaliador de \xd3rg\xe3o Externo",
                        blank=True,
                    ),
                ),
                (
                    "external_workplace",
                    models.TextField(
                        null=True,
                        verbose_name="Lota\xe7\xe3o do Avaliador de \xd3rg\xe3o Externo",
                        blank=True,
                    ),
                ),
                (
                    "date_external_evaluation",
                    models.DateField(
                        null=True,
                        verbose_name="Data da Avalia\xe7\xe3o Externa",
                        blank=True,
                    ),
                ),
                (
                    "boss",
                    models.ForeignKey(
                        related_name="evaluation_apd",
                        verbose_name="Avaliador",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "questionnaire_response",
                    models.ForeignKey(
                        related_name="evaluation_apd",
                        verbose_name="Question\xe1rio Resposta",
                        to="questionario.QuestionarioResposta",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Homologation",
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
                    "status",
                    models.CharField(
                        default=1,
                        max_length=1,
                        verbose_name="Status da Homologacao",
                        choices=[
                            ("1", "AGUARDANDO HOMOLOGA\xc7\xc3O"),
                            ("2", "HOMOLOGADO"),
                        ],
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        default="",
                        null=True,
                        verbose_name="Observa\xe7\xf5es",
                        blank=True,
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
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Manifestation",
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
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        related_name="manifestation_apd",
                        verbose_name="Avalia\xe7\xe3o de APD",
                        to="apd.Evaluation",
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
                    "questionnaire_response",
                    models.ForeignKey(
                        related_name="manifestation_apd",
                        verbose_name="Question\xe1rio Resposta",
                        to="questionario.QuestionarioResposta",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MemberCommission",
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
                    "type_participant",
                    models.CharField(
                        default=4,
                        max_length=1,
                        verbose_name="Tipo de Membro",
                        choices=[
                            ("1", "PRESIDENTE"),
                            ("3", "INTEGRANTE"),
                            ("2", "SECRET\xc1RIO"),
                            ("4", "SUPLENTE"),
                        ],
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Ordem", blank=True
                    ),
                ),
                (
                    "impediment",
                    models.BooleanField(default=False, verbose_name="Impedimento"),
                ),
                (
                    "commission",
                    models.ForeignKey(
                        verbose_name="Comiss\xe3o",
                        to="apd.Commission",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "member",
                    models.ForeignKey(
                        verbose_name="Membro",
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
            ],
            options={
                "ordering": ("order",),
                "permissions": (("apd_commission", "Comiss\xe3o de APD"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PeriodicEvaluationPerformance",
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
                    "status",
                    models.CharField(
                        default=1,
                        max_length=1,
                        verbose_name="Status da APD",
                        choices=[("1", "ATIVA"), ("2", "INATIVA ")],
                    ),
                ),
                (
                    "start_date",
                    models.DateField(verbose_name="Data In\xedcio", blank=True),
                ),
                ("end_date", models.DateField(verbose_name="Data Fim", blank=True)),
                (
                    "days_suspended",
                    models.DecimalField(
                        default=0, null=True, max_digits=5, decimal_places=2
                    ),
                ),
                (
                    "state_evaluation",
                    models.CharField(
                        default=1,
                        max_length=1,
                        blank=True,
                        choices=[
                            ("1", "NOVO"),
                            ("3", "MANIFESTADO"),
                            ("2", "AVALIADO"),
                            ("4", "FINALIZADO"),
                        ],
                    ),
                ),
                (
                    "date_science_evaluation",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Data Ci\xeancia do resultado da avalia\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "commission",
                    models.ForeignKey(
                        verbose_name="Comiss\xe3o de Avalia\xe7\xe3o",
                        to="apd.Commission",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "configuration",
                    models.ForeignKey(
                        verbose_name="Configura\xe7\xe3o",
                        to="apd.Configuration",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "employee",
                    models.ForeignKey(
                        related_name="apd",
                        to="rh.MovimentacaoPosse",
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
                    "previous_apd",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="APD Anterior",
                        blank=True,
                        to="apd.PeriodicEvaluationPerformance",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("end_date",),
                "permissions": (
                    ("apd_admin", "Administrador de APD"),
                    ("apd_boss", "Avaliador de APD"),
                    ("apd_subordinate", "Avaliado APD"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Resource",
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
                    "status",
                    models.CharField(
                        default=1,
                        max_length=1,
                        verbose_name="Status do Recurso",
                        choices=[("1", "AGUARDANDO"), ("2", "CONCLU\xcdDO")],
                    ),
                ),
                (
                    "decision",
                    models.CharField(
                        max_length=1,
                        verbose_name="Decis\xe3o do Recurso",
                        choices=[
                            ("1", "PROVIDO RECURSO"),
                            ("2", "N\xc3O PROVIDO RECURSO"),
                        ],
                    ),
                ),
                (
                    "date_science_decision",
                    models.DateTimeField(
                        null=True, verbose_name="Data Ci\xeancia do Recurso", blank=True
                    ),
                ),
                ("text", models.TextField(default="", verbose_name="Texto do Recurso")),
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
                    "evaluation",
                    models.ForeignKey(
                        related_name="resource_apd",
                        verbose_name="Avalia\xe7\xe3o de APD",
                        to="apd.Evaluation",
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
            ],
            options={
                "ordering": ("-created_at",),
                "permissions": (("apd_resource", "Comiss\xe3o de Recursos"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ScoreEvaluation",
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
                    "score_obtained",
                    models.DecimalField(default=0, max_digits=5, decimal_places=2),
                ),
                (
                    "top_score",
                    models.DecimalField(default=0, max_digits=5, decimal_places=2),
                ),
                (
                    "final_score",
                    models.DecimalField(default=0, max_digits=5, decimal_places=2),
                ),
                (
                    "date_modified",
                    models.DateField(
                        null=True,
                        verbose_name="Data modifica\xe7\xe3o da pontua\xe7\xe3o",
                        blank=True,
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
                    "element",
                    models.ForeignKey(
                        related_name="element_score",
                        to="questionario.Elemento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "evaluation",
                    models.ForeignKey(
                        related_name="score_evaluation",
                        verbose_name="Avalia\xe7\xe3o de APD",
                        to="apd.Evaluation",
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
                    "user_modified",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.Servidor",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="manifestation",
            name="subordinate",
            field=models.ForeignKey(
                related_name="manifestation_apd",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Avaliado",
                to="apd.PeriodicEvaluationPerformance",
            ),
        ),
        migrations.AddField(
            model_name="homologation",
            name="periodic_evaluation",
            field=models.ForeignKey(
                related_name="homologation_apd",
                verbose_name="Avalia\xe7\xe3o Peri\xf3dica de Desempenho",
                to="apd.PeriodicEvaluationPerformance",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="homologation",
            name="publication",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="Publica\xe7\xe3o",
                to="rh.Publicacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="evaluation",
            name="subordinate",
            field=models.ForeignKey(
                related_name="evaluation_apd",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Avaliado",
                to="apd.PeriodicEvaluationPerformance",
            ),
        ),
        migrations.AddField(
            model_name="decisioncommission",
            name="member_commission",
            field=models.ForeignKey(
                related_name="+", to="apd.MemberCommission", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="decisioncommission",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="decisioncommission",
            name="resource_evaluation",
            field=models.ForeignKey(
                related_name="decision_resource",
                verbose_name="Recurso de Avalia\xe7\xe3o",
                to="apd.Resource",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
