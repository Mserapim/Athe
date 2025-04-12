# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0049_auto_20170725_1043"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0035_auto_20170725_1043"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
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
                ("amount_athenas", models.IntegerField(null=True, blank=True)),
                ("amount_submitted", models.IntegerField(null=True, blank=True)),
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
            options={
                "verbose_name": "Atividade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ActivityAdjustment",
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
                ("amount", models.PositiveSmallIntegerField()),
                (
                    "situation",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Situa\xe7\xe3o"
                    ),
                ),
                (
                    "activity",
                    models.OneToOneField(
                        related_name="adjustment",
                        to="raf.Activity",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Ajuste de Atividade",
                "permissions": (
                    ("can_sign_adjustment", "Pode aceitar/rejeitar pedido de ajuste"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AutoReference",
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
                    "source",
                    models.TextField(verbose_name="Origem da informa\xc3\xa7\xc3\xa3o"),
                ),
                (
                    "process_number",
                    models.TextField(
                        verbose_name="Numero de identifica\xc3\xa7\xc3\xa3o"
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(null=True, verbose_name="Data da atividade"),
                ),
                ("obj", models.TextField(verbose_name="JSON de referencia")),
                (
                    "activity",
                    models.ForeignKey(
                        related_name="autoreference",
                        to="raf.Activity",
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
            ],
            options={
                "verbose_name": "Auto Refer\xeancia",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Conversation",
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
                ("finalized", models.BooleanField(default=False)),
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
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ConversationContent",
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
                ("message", models.TextField()),
                ("step", models.PositiveSmallIntegerField()),
                (
                    "conversation",
                    models.ForeignKey(
                        related_name="contents",
                        to="raf.Conversation",
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
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
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
                    "origin",
                    models.ForeignKey(
                        related_name="+", to="rh.Lotacao", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["created_at"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DataEProc",
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
                ("processo", models.CharField(max_length=100, null=True)),
                ("dataintimacao", models.CharField(max_length=100, null=True)),
                ("intimacao", models.CharField(max_length=250, null=True)),
                ("dataabriuprazo", models.CharField(max_length=100, null=True)),
                ("manifestacaoabertura", models.CharField(max_length=250, null=True)),
                ("datafechouprazo", models.CharField(max_length=100, null=True)),
                ("manifestacaofechamento", models.CharField(max_length=250, null=True)),
                (
                    "codmanifestacaofechamento",
                    models.CharField(max_length=100, null=True),
                ),
                (
                    "datamanifestacaodecurso",
                    models.CharField(max_length=100, null=True),
                ),
                ("manifestacaodecurso", models.CharField(max_length=250, null=True)),
                ("codmanifestacaodecurso", models.CharField(max_length=100, null=True)),
                ("classe", models.CharField(max_length=350, null=True)),
                ("codclasse", models.CharField(max_length=100, null=True)),
                ("assuntoprincipal", models.CharField(max_length=350, null=True)),
                ("codassuntoprincipal", models.CharField(max_length=100, null=True)),
                ("assuntosecundario", models.CharField(max_length=350, null=True)),
                ("codassuntosecundario", models.CharField(max_length=100, null=True)),
                ("promotoria", models.CharField(max_length=150)),
                ("promotoria_slugfy", models.CharField(max_length=150)),
                ("orgao", models.CharField(max_length=150, null=True)),
                ("membro", models.CharField(max_length=100, null=True)),
                ("analise", models.CharField(max_length=100, null=True)),
            ],
            options={
                "ordering": ["promotoria", "datafechouprazo"],
                "verbose_name": "DataEproc",
            },
        ),
        migrations.CreateModel(
            name="FunctionalActivityReport",
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
                ("month", models.PositiveSmallIntegerField()),
                ("year", models.PositiveSmallIntegerField()),
                ("closed", models.BooleanField(default=False)),
                ("submitted_at", models.DateTimeField(null=True, blank=True)),
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
                        related_name="functionalactivityreports",
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
                    "submitted_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["-year", "month"],
                "verbose_name": "RAF",
                "permissions": (("can_management_raf", "Pode abrir/fechar o RAF"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Item",
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
                ("title", models.CharField(max_length=100)),
                ("activated", models.BooleanField(default=True)),
                ("cnmp", models.BooleanField(default=True)),
                (
                    "number_order",
                    models.PositiveSmallIntegerField(null=True, blank=True),
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
            options={
                "ordering": ["number_order"],
                "verbose_name": "Item/Assunto",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Quiz",
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
                ("activated", models.BooleanField(default=True)),
                (
                    "number_order",
                    models.PositiveSmallIntegerField(null=True, blank=True),
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
                    "exclude_classes",
                    models.ManyToManyField(
                        related_name="exclude_quizzez", to="judicial.LegalClass"
                    ),
                ),
                (
                    "legalclasses",
                    models.ManyToManyField(
                        related_name="quizzes", to="judicial.LegalClass"
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
                "ordering": ["yearbase", "number_order", "typequiz__title"],
                "verbose_name": "Question\xe1rio",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SubItem",
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
                ("title", models.CharField(max_length=100)),
                ("activated", models.BooleanField(default=True)),
                ("cnmp", models.BooleanField(default=True)),
                (
                    "number_order",
                    models.PositiveSmallIntegerField(null=True, blank=True),
                ),
                ("manual_amount", models.BooleanField(default=False)),
                (
                    "description",
                    models.TextField(
                        default="Sem descri\xe7\xe3o cadastrada.",
                        null=True,
                        verbose_name="Descri\xe7\xe3o",
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
            ],
            options={
                "ordering": ["number_order"],
                "verbose_name": "SubItem/Movimento",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SubItemCalculate",
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
                    "affectation",
                    models.PositiveSmallIntegerField(default=1, verbose_name="Afetar"),
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
                    "from_the_sum",
                    models.ForeignKey(
                        related_name="for_calculation",
                        verbose_name="subitem para calculo",
                        to="raf.SubItem",
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
                    "subitem",
                    models.ForeignKey(
                        related_name="be_calculated",
                        verbose_name="subitem_a ser calculado",
                        to="raf.SubItem",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["subitem", "from_the_sum"],
                "verbose_name": "Calculo para Subitem",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TaxonomyClassification",
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
                    "classification",
                    models.ForeignKey(
                        blank=True,
                        to="judicial.LegalClassification",
                        null=True,
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
                    "exclude_classification",
                    models.ForeignKey(
                        related_name="itembase_exclude_classification",
                        blank=True,
                        to="judicial.LegalClassification",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "item",
                    models.ForeignKey(
                        blank=True, to="raf.Item", null=True, on_delete=models.CASCADE
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
                    "subitem",
                    models.ForeignKey(
                        blank=True,
                        to="raf.SubItem",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TrustRelationship",
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
                ("activated", models.BooleanField(default=True)),
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
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
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
                    "trust_employee",
                    models.ForeignKey(
                        related_name="+", to="rh.Servidor", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["employee"],
                "verbose_name": "Rela\xe7\xe3o de confian\xe7a",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TypeQuiz",
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
                ("title", models.CharField(unique=True, max_length=100)),
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
                "verbose_name": "Tipo de Question\xe1rio",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="WorkerLocation",
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
                    "location",
                    models.ForeignKey(
                        related_name="workerlocations",
                        to="rh.Lotacao",
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
                    "raf",
                    models.ForeignKey(
                        related_name="workerlocations",
                        to="raf.FunctionalActivityReport",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["location"],
                "verbose_name": "Promotoria",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="YearBase",
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
                ("title", models.CharField(unique=True, max_length=4)),
                ("activated", models.BooleanField(default=True)),
                ("valid_of", models.DateField(null=True, blank=True)),
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
                "ordering": ["-title", "-valid_of"],
                "verbose_name": "Ano Base",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="subitem",
            name="legal_classification",
            field=models.ManyToManyField(
                to="judicial.LegalClassification", through="raf.TaxonomyClassification"
            ),
        ),
        migrations.AddField(
            model_name="subitem",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="subitem",
            name="quiz",
            field=models.ForeignKey(
                to="raf.Quiz", on_delete=django.db.models.deletion.PROTECT
            ),
        ),
        migrations.AddField(
            model_name="quiz",
            name="typequiz",
            field=models.ForeignKey(
                related_name="quizzes",
                on_delete=django.db.models.deletion.PROTECT,
                to="raf.TypeQuiz",
            ),
        ),
        migrations.AddField(
            model_name="quiz",
            name="yearbase",
            field=models.ForeignKey(
                related_name="quizzes",
                on_delete=django.db.models.deletion.PROTECT,
                to="raf.YearBase",
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="legal_classification",
            field=models.ManyToManyField(
                to="judicial.LegalClassification", through="raf.TaxonomyClassification"
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="quiz",
            field=models.ForeignKey(
                to="raf.Quiz", on_delete=django.db.models.deletion.PROTECT
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="subitems",
            field=models.ManyToManyField(related_name="items", to="raf.SubItem"),
        ),
        migrations.AddField(
            model_name="functionalactivityreport",
            name="yearbase",
            field=models.ForeignKey(
                related_name="functionalactivityreports",
                to="raf.YearBase",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="conversation",
            name="last_content",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                blank=True,
                to="raf.ConversationContent",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="conversation",
            name="locations",
            field=models.ManyToManyField(to="rh.Lotacao"),
        ),
        migrations.AddField(
            model_name="conversation",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activityadjustment",
            name="conversation",
            field=models.OneToOneField(
                null=True, blank=True, to="raf.Conversation", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="activityadjustment",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activityadjustment",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="item",
            field=models.ForeignKey(
                related_name="activities", to="raf.Item", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="activity",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="subitem",
            field=models.ForeignKey(
                related_name="activities", to="raf.SubItem", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="activity",
            name="workerlocation",
            field=models.ForeignKey(
                related_name="activities",
                to="raf.WorkerLocation",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterUniqueTogether(
            name="workerlocation",
            unique_together=set([("location", "raf")]),
        ),
        migrations.AlterUniqueTogether(
            name="trustrelationship",
            unique_together=set([("employee", "trust_employee")]),
        ),
        migrations.AlterUniqueTogether(
            name="quiz",
            unique_together=set([("typequiz", "yearbase", "activated")]),
        ),
        migrations.AlterUniqueTogether(
            name="functionalactivityreport",
            unique_together=set([("employee", "year", "month")]),
        ),
        migrations.AlterUniqueTogether(
            name="activity",
            unique_together=set([("workerlocation", "item", "subitem")]),
        ),
    ]
