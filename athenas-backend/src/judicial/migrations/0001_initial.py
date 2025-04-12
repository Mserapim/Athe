# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0014_movimentacao_physical"),
        ("rh", "0025_auto_20160711_1502"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notification", "0002_auto_20160229_1715"),
        ("ged", "0003_auto_20151014_1609"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attached",
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
                ("title", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Bloke",
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
                ("my_type", models.CharField(db_index=True, max_length=60, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="BlokeAddress",
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
                ("district", models.CharField(max_length=200)),
                ("address", models.CharField(max_length=200)),
                ("complement", models.CharField(max_length=200, null=True, blank=True)),
                ("observation", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="BlokeDocument",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("appeal", models.TextField(null=True)),
                ("appeal_deadline", models.DateTimeField(null=True)),
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Character",
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
                        unique=True, max_length=60, verbose_name="T\xedtulo"
                    ),
                ),
                ("slug", models.SlugField(unique=True, max_length=60, blank=True)),
                (
                    "users",
                    models.ManyToManyField(
                        related_name="has_character", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="County",
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
                    "locations",
                    models.ManyToManyField(related_name="counties", to="rh.Localidade"),
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
                "ordering": ("title",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DeliveryAttempt",
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
                ("observation", models.TextField()),
                (
                    "exit_date",
                    models.DateTimeField(
                        null=True, verbose_name="data e hora de saida para entrega"
                    ),
                ),
                (
                    "return_date",
                    models.DateTimeField(
                        null=True, verbose_name="data e hora de retorno da entrega"
                    ),
                ),
                (
                    "delivery_date",
                    models.DateTimeField(null=True, verbose_name="Momento da entrega"),
                ),
                (
                    "attempt",
                    models.SmallIntegerField(
                        null=True, verbose_name="tentativas de entrega"
                    ),
                ),
                (
                    "delivered",
                    models.SmallIntegerField(
                        null=True,
                        verbose_name="a diligencia foi entregue ao destinatario ou nao",
                    ),
                ),
                (
                    "type_vehicle",
                    models.SmallIntegerField(
                        null=True,
                        verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
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
                "ordering": ("diligence", "-attempt"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Diligence",
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
                ("diligence_year", models.SmallIntegerField(null=True, blank=True)),
                ("diligence_number", models.SmallIntegerField(null=True, blank=True)),
                (
                    "formated_number",
                    models.CharField(
                        db_index=True, max_length=10, null=True, blank=True
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=100, null=True, verbose_name="T\xedtulo", blank=True
                    ),
                ),
                ("text", models.TextField(blank=True)),
                (
                    "date_receipt_diligence",
                    models.DateTimeField(
                        null=True,
                        verbose_name="data de recebimento da diligencia",
                        blank=True,
                    ),
                ),
                (
                    "date_delivery",
                    models.DateTimeField(
                        null=True,
                        verbose_name="data da entrega da diligencia",
                        blank=True,
                    ),
                ),
                (
                    "delivery_status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="status da entrega",
                        blank=True,
                    ),
                ),
                (
                    "priority",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        blank=True,
                        choices=[(1, "Normal"), (2, "Urgente")],
                    ),
                ),
                ("observation", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DiligenceTemplate",
            fields=[
                (
                    "message_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="notification.Message",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("notification.message",),
        ),
        migrations.CreateModel(
            name="DistributionScore",
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
                ("score", models.PositiveIntegerField(default=0)),
                ("total", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="DistributionTable",
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
                ("factor", models.DecimalField(max_digits=12, decimal_places=4)),
                (
                    "document",
                    models.ForeignKey(
                        related_name="in_distribution_tables",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Publicacao",
                    ),
                ),
                (
                    "end_document",
                    models.ForeignKey(
                        related_name="in_distribution_table_has_end",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="rh.Publicacao",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-document__data_vigencia", "-factor"),
            },
        ),
        migrations.CreateModel(
            name="ExecutionOrgan",
            fields=[
                (
                    "lotacao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("general_distribution", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("rh.lotacao",),
        ),
        migrations.CreateModel(
            name="Glosary",
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
                ("title", models.CharField(max_length=120, null=True)),
                ("app_label", models.CharField(max_length=200, db_index=True)),
                ("model_name", models.CharField(max_length=200, db_index=True)),
                ("icon_class", models.CharField(max_length=200)),
                ("classification_type", models.SmallIntegerField(null=True)),
                (
                    "allowed_for",
                    models.ManyToManyField(
                        related_name="permissions", to="judicial.Character"
                    ),
                ),
            ],
            options={
                "ordering": ("title", "app_label", "model_name"),
                "permissions": (
                    ("can_admin_glosary", "Pode administrar os tipos de documentos"),
                ),
            },
        ),
        migrations.CreateModel(
            name="GlosaryTemplate",
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
                ("title", models.CharField(max_length=60)),
                ("template", models.TextField(blank=True)),
                ("active", models.BooleanField(default=False)),
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
                    "glosary",
                    models.ForeignKey(
                        related_name="templates",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="judicial.Glosary",
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
                "ordering": ("-active", "-pk"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="LegalClassification",
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
                ("cnmp_code", models.IntegerField(null=True, db_index=True)),
                ("title", models.CharField(max_length=200, db_index=True)),
                ("path_cache", models.CharField(max_length=400, db_index=True)),
                (
                    "taxonomy_type",
                    models.CharField(default="", max_length=30, null=True),
                ),
            ],
            options={
                "ordering": ("path_cache", "title"),
            },
        ),
        migrations.CreateModel(
            name="LegalGround",
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
                ("title", models.CharField(max_length=300)),
                ("text", models.TextField()),
            ],
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
                ("who_type", models.SmallIntegerField()),
                ("deadline", models.DateField(null=True, blank=True)),
                (
                    "manifestation_type",
                    models.SmallIntegerField(
                        blank=True, null=True, choices=[(1, "Direta"), (2, "Indireta")]
                    ),
                ),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
                ("content", models.TextField()),
            ],
            options={
                "ordering": ("signed_at",),
            },
        ),
        migrations.CreateModel(
            name="NotifyStack",
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
                ("notfied", models.BooleanField(default=False)),
                (
                    "employee",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Servidor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OfficerDiligence",
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
                ("score", models.SmallIntegerField(default=0, blank=True)),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1, null=True, choices=[(1, "Ativo"), (2, "Inativo")]
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
                    "officer_diligence",
                    models.OneToOneField(to="rh.Servidor", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("officer_diligence__pessoa_fisica__nome",),
                "permissions": (("office_geral", "Gestor geral de diligencias"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="OutCourtLawsuit",
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
                    "type_lawsuit",
                    models.SmallIntegerField(
                        default=1, verbose_name="Tipo do Processo"
                    ),
                ),
                ("title", models.CharField(max_length=160, null=True)),
                ("year", models.SmallIntegerField(verbose_name="Ano")),
                ("number_lawsuit", models.IntegerField(verbose_name="N\xfamero")),
                (
                    "cache_number",
                    models.CharField(max_length=10, verbose_name="N\xfamero/Ano"),
                ),
                ("deadline_cache", models.DateField(null=True)),
                ("is_criminal", models.BooleanField(default=False)),
                ("closed_at", models.DateTimeField(null=True)),
                (
                    "closed_by",
                    models.ForeignKey(
                        related_name="closeds_lawsuit",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "location",
                    models.ForeignKey(
                        related_name="lawsuit",
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "origin",
                    models.ForeignKey(
                        related_name="out_court_lawsuits",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="protocolo.Protocolo",
                    ),
                ),
            ],
            options={
                "ordering": ("deadline_cache",),
                "permissions": (
                    ("outcourtlawsuitadmin", "Pode administrar os OutCourtLawsuit"),
                ),
            },
        ),
        migrations.CreateModel(
            name="PartLawsuit",
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
                ("cache_rendered", models.TextField(null=True, blank=True)),
                ("type_part", models.CharField(max_length=60, null=True, blank=True)),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PartLawsuitAccess",
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
                ("motivation", models.SmallIntegerField(null=True, blank=True)),
                ("justification", models.TextField()),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
                ("suspended_at", models.DateTimeField(null=True, blank=True)),
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
                "ordering": ("-signed_at", "-created_at"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PersonHasAccess",
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
                ("state", models.SmallIntegerField()),
                (
                    "access",
                    models.ForeignKey(
                        related_name="authorization",
                        to="judicial.PartLawsuitAccess",
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
                    "person",
                    models.ForeignKey(
                        related_name="+", to="rh.Pessoa", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        # migrations.CreateModel(
        #     name='Replacement',
        #     fields=[
        #         ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
        #         ('created_at', models.DateTimeField(auto_now_add=True)),
        #         ('modified_at', models.DateTimeField(auto_now=True)),
        #         ('order', models.PositiveIntegerField(default=1)),
        #         ('created_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL)),
        #         ('document', models.ForeignKey(related_name='replacement', on_delete=django.db.models.deletion.PROTECT, to='rh.Publicacao')),
        #         ('modified_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL)),
        #         ('replaced', models.ForeignKey(related_name='replaceds', on_delete=django.db.models.deletion.PROTECT, to='judicial.ExecutionOrgan')),
        #         ('substitute', models.ForeignKey(related_name='substitutes', on_delete=django.db.models.deletion.PROTECT, to='judicial.ExecutionOrgan')),
        #     ],
        #     options={
        #         'ordering': ('replaced__nome',),
        #     },
        #     bases=(standard.models.AuditableMixins, models.Model),
        # ),
        migrations.CreateModel(
            name="Sectional",
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
                        max_length=120, verbose_name="T\xedtulo", db_index=True
                    ),
                ),
                (
                    "county",
                    models.ForeignKey(
                        related_name="in_sections",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Comarca",
                        to="judicial.County",
                    ),
                ),
            ],
            options={
                "ordering": ("county__title", "title"),
            },
        ),
        migrations.CreateModel(
            name="Tag",
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
                ("title", models.CharField(max_length=40, verbose_name="T\xedtulo")),
                (
                    "slug",
                    models.CharField(max_length=40, verbose_name="Abrevia\xe7\xe3o"),
                ),
                (
                    "tag_type",
                    models.SmallIntegerField(
                        verbose_name="Acesso", choices=[(1, "SYSTEM"), (2, "WORK")]
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "work_place",
                    models.ForeignKey(
                        related_name="tags",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Lotacao",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Taxonomy",
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
                ("version", models.CharField(max_length=20, db_index=True)),
                ("efective_date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="TriageConcurrence",
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
                ("direct", models.BooleanField(default=True)),
                ("incident_type", models.SmallIntegerField(default=1, blank=True)),
                ("incident", models.SmallIntegerField(null=True, blank=True)),
                ("argumentation", models.TextField(null=True)),
                (
                    "reason_for_suspension",
                    models.SmallIntegerField(
                        default=None,
                        null=True,
                        blank=True,
                        choices=[
                            (0, "Nenhum"),
                            (1, "Ativo"),
                            (2, "Motivo 2"),
                            (3, "Motivo 3"),
                        ],
                    ),
                ),
                (
                    "execution_organ",
                    models.ForeignKey(
                        related_name="as_triage_concurrences",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="judicial.ExecutionOrgan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TriagePart",
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
                ("effected_at", models.DateTimeField(null=True, blank=True)),
                ("text", models.TextField(blank=True)),
                (
                    "concurrence",
                    models.ManyToManyField(
                        related_name="as_concurrences",
                        through="judicial.TriageConcurrence",
                        to="judicial.ExecutionOrgan",
                    ),
                ),
                (
                    "distributed",
                    models.ForeignKey(
                        related_name="as_distributeds",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="judicial.ExecutionOrgan",
                        null=True,
                    ),
                ),
                (
                    "effected_by",
                    models.ForeignKey(
                        related_name="effected_parts_of_triage",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TriagePartLocation",
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
                    "location",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Localidade",
                    ),
                ),
                (
                    "sectional",
                    models.ForeignKey(
                        related_name="in_triage_part_locations",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="judicial.Sectional",
                        null=True,
                    ),
                ),
                (
                    "triagepart",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="judicial.TriagePart",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdditionalDiligence",
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
                ("justification", models.TextField(null=True, blank=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="AdministrativeDiligence",
            fields=[
                (
                    "diligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Diligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.diligence",),
        ),
        migrations.CreateModel(
            name="Archivement",
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
                ("despatch", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="AssessmentNoticeOffice",
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
                ("is_criminal", models.BooleanField(default=False)),
                ("is_anonymus", models.BooleanField(default=False)),
                ("notice_title", models.CharField(max_length=200)),
                ("notice", models.TextField()),
                ("annotation", models.TextField(blank=True)),
                (
                    "at_where",
                    models.ForeignKey(
                        to="rh.Localidade", null=True, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "interested",
                    models.ForeignKey(
                        related_name="in_assessment_notice_office",
                        blank=True,
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "location",
                    models.ForeignKey(
                        related_name="has_assessment_notice_office",
                        to="rh.Lotacao",
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
            name="Association",
            fields=[
                (
                    "bloke_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Bloke",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "bloke",
                    models.ForeignKey(
                        related_name="has_bloke_association",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.PessoaJuridica",
                    ),
                ),
            ],
            bases=("judicial.bloke",),
        ),
        migrations.CreateModel(
            name="AttachedDocument",
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
                ("attached_title", models.CharField(max_length=150)),
                ("resume", models.TextField()),
                ("attached_type", models.SmallIntegerField(default=1)),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "bloke_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Bloke",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "bloke",
                    models.ForeignKey(
                        related_name="has_bloke_company",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.PessoaJuridica",
                    ),
                ),
            ],
            bases=("judicial.bloke",),
        ),
        migrations.CreateModel(
            name="ConnectionLawsuit",
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
                ("text", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Denunciation",
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
                (
                    "protocol",
                    models.ForeignKey(
                        related_name="has_deunciation",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="protocolo.Protocolo",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="DilationPeriod",
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
                ("older_deadline", models.DateTimeField(null=True, blank=True)),
                ("justification", models.TextField()),
                (
                    "type_lawsuit",
                    models.SmallIntegerField(
                        null=True, verbose_name="Tipo do Processo", blank=True
                    ),
                ),
                ("days", models.IntegerField(null=True, blank=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="DismembermentProcess",
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
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="GovernmentPublic",
            fields=[
                (
                    "bloke_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Bloke",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "bloke",
                    models.ForeignKey(
                        related_name="has_bloke_government",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.PessoaFisica",
                    ),
                ),
            ],
            bases=("judicial.bloke",),
        ),
        migrations.CreateModel(
            name="JudicialDiligence",
            fields=[
                (
                    "diligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Diligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("deadline", models.SmallIntegerField(null=True, blank=True)),
                ("who_type", models.SmallIntegerField(null=True, blank=True)),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "ordering": ("formated_number", "-delivery_status"),
                "permissions": (
                    ("admin_dilig", "Vis\xe3o Administrador"),
                    ("oficial_dilig", "Vis\xe3o Oficial de Diligencias"),
                    ("promotor_dilig", "Vis\xe3o Promotor"),
                ),
            },
            bases=("judicial.diligence",),
        ),
        migrations.CreateModel(
            name="Judicialization",
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
                ("code", models.CharField(max_length=100)),
                ("court", models.CharField(max_length=200)),
                ("observation", models.TextField(null=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="LegalMatter",
            fields=[
                (
                    "legalclassification_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.LegalClassification",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.legalclassification",),
        ),
        migrations.CreateModel(
            name="LegalMoviment",
            fields=[
                (
                    "legalclassification_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.LegalClassification",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.legalclassification",),
        ),
        migrations.CreateModel(
            name="LegalProcedure",
            fields=[
                (
                    "legalclassification_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.LegalClassification",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.legalclassification",),
        ),
        migrations.CreateModel(
            name="Ordinace",
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
                ("number", models.SmallIntegerField(blank=True)),
                ("type_ordinace", models.SmallIntegerField()),
                ("year", models.SmallIntegerField(blank=True)),
                (
                    "cache_formated_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("object_of_proccess", models.TextField(null=True)),
                ("consideration", models.TextField(null=True, blank=True)),
                (
                    "legalgrounds",
                    models.ManyToManyField(
                        related_name="in_ordinaces", to="judicial.LegalGround"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "bloke_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Bloke",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "bloke",
                    models.ForeignKey(
                        related_name="has_bloke_person",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.PessoaFisica",
                    ),
                ),
            ],
            bases=("judicial.bloke",),
        ),
        migrations.CreateModel(
            name="PreInvestigationFact",
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
                ("justify", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="RejectionFact",
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
                ("despatch", models.TextField()),
                ("rejection_fact_type", models.SmallIntegerField()),
                ("decision_type", models.SmallIntegerField(null=True, blank=True)),
                ("decision_text_cache", models.TextField(null=True, blank=True)),
                ("decision_text", models.TextField(null=True, blank=True)),
                ("decided_at", models.DateTimeField(null=True, blank=True)),
                ("type_ordinace", models.SmallIntegerField(null=True, blank=True)),
                (
                    "decided_by",
                    models.ForeignKey(
                        related_name="in_reconsideration_rejection_facts",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "ordinace",
                    models.ForeignKey(
                        related_name="in_rejection_fact",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="judicial.Ordinace",
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="RejectionLinkOther",
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
                ("despatch", models.TextField()),
                (
                    "other_lawsuit",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Processo Extrajudicial"),
                            (2, "Processo Judicial"),
                        ]
                    ),
                ),
                ("other_lawsuit_number", models.CharField(max_length=100)),
                (
                    "other_lawsuit_organ",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.OrgaoGeral",
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="RemittanceExternal",
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
                ("text", models.TextField()),
                (
                    "organ",
                    models.SmallIntegerField(
                        default=0,
                        choices=[
                            (1, "MINIST\xc9RIO P\xdaBLICO FEDERAL"),
                            (2, "MINIST\xc9RIO P\xdaBLICO DO TRABALHO"),
                            (3, "MINIST\xc9RIO P\xdaBLICO ELEITORAL"),
                            (4, "MINIST\xc9RIO P\xdaBLICO MILITAR"),
                            (5, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO ACRE"),
                            (6, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO ALAGOAS"),
                            (7, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO AMAZONAS"),
                            (8, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO AMAP\xc1"),
                            (9, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DA BAHIA"),
                            (10, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO CEAR\xc1"),
                            (
                                11,
                                "MINIST\xc9RIO P\xdaBLICO DO DISTRITO FEDERAL E TERRIT\xd3RIOS",
                            ),
                            (
                                12,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO ESP\xcdRITO SANTO",
                            ),
                            (13, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE GOI\xc1S"),
                            (14, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO MARANH\xc3O"),
                            (15, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE MINAS GERAIS"),
                            (
                                16,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE MATO GROSSO DO SUL",
                            ),
                            (17, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO MATO GROSSO"),
                            (18, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO PAR\xc1"),
                            (19, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DA PARA\xcdBA"),
                            (20, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE PERNAMBUCO"),
                            (21, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO PIAU\xcd"),
                            (22, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO PARAN\xc1"),
                            (
                                23,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO RIO DE JANEIRO",
                            ),
                            (
                                24,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO RIO GRANDE DO NORTE",
                            ),
                            (25, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE ROND\xd4NIA"),
                            (26, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE RORAIMA"),
                            (
                                27,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO RIO GRANDE DO SUL",
                            ),
                            (
                                28,
                                "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE SANTA CATARINA",
                            ),
                            (29, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DO SERGIPE"),
                            (30, "MINIST\xc9RIO P\xdaBLICO DO ESTADO DE S\xc3O PAULO"),
                        ],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="RemittanceInternal",
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
                ("text", models.TextField()),
                ("conflict", models.BooleanField(default=False)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="SupplementOrdinace",
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
                    "ordinace",
                    models.ForeignKey(
                        related_name="supplementations",
                        to="judicial.Ordinace",
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
            name="Triage",
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
                ("triage_number", models.IntegerField()),
                ("triage_year", models.IntegerField()),
                ("effected_at", models.DateTimeField(null=True, blank=True)),
                (
                    "effected_by",
                    models.ForeignKey(
                        related_name="effected_triages",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AddField(
            model_name="triagepart",
            name="locations",
            field=models.ManyToManyField(
                related_name="as_triage_parts",
                through="judicial.TriagePartLocation",
                to="rh.Localidade",
            ),
        ),
        migrations.AddField(
            model_name="triageconcurrence",
            name="triage_part",
            field=models.ForeignKey(
                related_name="as_triage_concurrences",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.TriagePart",
            ),
        ),
        migrations.AddField(
            model_name="partlawsuitaccess",
            name="part",
            field=models.ForeignKey(
                related_name="access_controls",
                to="judicial.PartLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuitaccess",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuitaccess",
            name="suspended_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="create_location",
            field=models.ForeignKey(
                related_name="created_parts_lawsuit",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="parts",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="shared_with_lawsuit",
            field=models.ForeignKey(
                related_name="shared_parts",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.OutCourtLawsuit",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="signed_by",
            field=models.ForeignKey(
                related_name="as_signed_by_in_part",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="tags",
            field=models.ManyToManyField(
                related_name="out_court_lawsuits", to="judicial.Tag"
            ),
        ),
        migrations.AddField(
            model_name="notifystack",
            name="out_court_lawsuits",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="manifestation",
            name="reference",
            field=models.ForeignKey(
                related_name="manifestations",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.PartLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="manifestation",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Pessoa",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="manifestation",
            name="who",
            field=models.ForeignKey(
                related_name="manifestations",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Pessoa",
            ),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="father",
            field=models.ForeignKey(
                related_name="children",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalClassification",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="version",
            field=models.ForeignKey(
                related_name="classifications",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.Taxonomy",
            ),
        ),
        migrations.AddField(
            model_name="glosary",
            name="legal_classification",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalClassification",
                null=True,
            ),
        ),
        # migrations.AddField(
        #     model_name='executionorgan',
        #     name='replacements',
        #     field=models.ManyToManyField(to='judicial.ExecutionOrgan', through='judicial.Replacement'),
        # ),
        migrations.AddField(
            model_name="distributiontable",
            name="execution_organ",
            field=models.ForeignKey(
                related_name="in_distribution_tables",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.ExecutionOrgan",
            ),
        ),
        migrations.AddField(
            model_name="distributiontable",
            name="sectional",
            field=models.ForeignKey(
                related_name="in_distribution_tables",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.Sectional",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="distributionscore",
            name="execution_organ",
            field=models.ForeignKey(
                related_name="in_distribution_scores",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.ExecutionOrgan",
            ),
        ),
        migrations.AddField(
            model_name="diligence",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="diligence",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="diligence",
            name="responsible_delivering",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="responsavel pela entrega",
                blank=True,
                to="judicial.OfficerDiligence",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="diligence",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.Diligence",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="file_delivery",
            field=models.OneToOneField(
                related_name="+", null=True, to="ged.Arquivo", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="blokedocument",
            name="bloke",
            field=models.ForeignKey(
                related_name="documents",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.Bloke",
            ),
        ),
        migrations.AddField(
            model_name="blokedocument",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="blokedocument",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="blokeaddress",
            name="bloke",
            field=models.ForeignKey(
                related_name="addresses", to="judicial.Bloke", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="blokeaddress",
            name="location",
            field=models.ForeignKey(
                related_name="+", to="rh.Localidade", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="bloke",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="blokes",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="attached",
            name="attached_document",
            field=models.ForeignKey(
                related_name="attaches",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attached",
            name="attached_manifestation",
            field=models.ForeignKey(
                related_name="attaches",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.Manifestation",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attached",
            name="attached_part_access",
            field=models.ForeignKey(
                related_name="attaches",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.PartLawsuitAccess",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attached",
            name="file_descriptor",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                to="ged.Arquivo",
            ),
        ),
        migrations.CreateModel(
            name="Citation",
            fields=[
                (
                    "judicialdiligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.judicialdiligence",),
        ),
        migrations.CreateModel(
            name="DiligenceRequest",
            fields=[
                (
                    "judicialdiligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.judicialdiligence",),
        ),
        migrations.CreateModel(
            name="Intimation",
            fields=[
                (
                    "judicialdiligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.judicialdiligence",),
        ),
        migrations.CreateModel(
            name="NotificationDiligence",
            fields=[
                (
                    "judicialdiligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.judicialdiligence",),
        ),
        migrations.CreateModel(
            name="Scientization",
            fields=[
                (
                    "judicialdiligence_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.judicialdiligence",),
        ),
        migrations.AlterUniqueTogether(
            name="triagepartlocation",
            unique_together=set([("triagepart", "location")]),
        ),
        migrations.AddField(
            model_name="triagepart",
            name="matter",
            field=models.ForeignKey(
                related_name="triages",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalMatter",
            ),
        ),
        migrations.AddField(
            model_name="triagepart",
            name="triage",
            field=models.ForeignKey(
                related_name="parts",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.Triage",
            ),
        ),
        migrations.AddField(
            model_name="triageconcurrence",
            name="with_matter",
            field=models.ForeignKey(
                related_name="as_with_matter",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalMatter",
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sectional",
            unique_together=set([("county", "title")]),
        ),
        migrations.AlterUniqueTogether(
            name="notifystack",
            unique_together=set([("employee", "out_court_lawsuits")]),
        ),
        migrations.AddField(
            model_name="manifestation",
            name="diligence",
            field=models.ForeignKey(
                related_name="has_manifestations",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.JudicialDiligence",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="diligence_file",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                blank=True,
                to="ged.Arquivo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="execution_organ",
            field=models.ForeignKey(
                related_name="diligences",
                blank=True,
                to="judicial.ExecutionOrgan",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="part",
            field=models.ForeignKey(
                related_name="diligences",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.PartLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="publication",
            field=models.ForeignKey(
                related_name="diligences_publications",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="who",
            field=models.ForeignKey(
                related_name="with_judicial_diligences",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Pessoa",
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="glosary",
            unique_together=set([("app_label", "model_name")]),
        ),
        migrations.AddField(
            model_name="distributiontable",
            name="matter",
            field=models.ForeignKey(
                related_name="in_distribution_tables",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalMatter",
            ),
        ),
        migrations.AddField(
            model_name="distributionscore",
            name="matter",
            field=models.ForeignKey(
                related_name="in_distribution_scores",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.LegalMatter",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="connectionlawsuit",
            name="lawsuit_connected",
            field=models.ForeignKey(
                related_name="connections",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="blokedocument",
            name="rejection_fact",
            field=models.ForeignKey(
                related_name="as_appeal_against",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.RejectionFact",
            ),
        ),
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="matter",
            field=models.ForeignKey(
                to="judicial.LegalMatter", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="protocol_origin",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="protocolo.Protocolo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterUniqueTogether(
            name="blokedocument",
            unique_together=set([("bloke", "rejection_fact")]),
        ),
    ]
