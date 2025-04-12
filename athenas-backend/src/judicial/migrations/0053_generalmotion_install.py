# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations, models
import standard.models
import judicial.models
import django.db.models.deletion
from django.conf import settings
from datetime import datetime


def up_acting_zone(apps, schema_editor):
    ActingZone = apps.get_model("judicial", "ActingZone")
    OutCourtLawsuitLog = apps.get_model("judicial", "OutCourtLawsuitLog")
    User = apps.get_model("auth", "User")

    print("")
    print("    Pegando usuário autor", end="")
    user = User.objects.get(username="athenas")
    print(" uid: %d" % user.pk)
    print("    Criando área de atuação", end=" ")
    zone = ActingZone(
        title="Não classificado",
        enabled=False,
        created_at=datetime.now(),
        created_by_id=user.pk,
        modified_at=datetime.now(),
        modified_by_id=user.pk,
    )
    zone.save()
    print(" done")

    print("    Iniciando update do campo acting_zone em OutCourtLawsuitLog", end=" ")
    OutCourtLawsuitLog.objects.filter().update(acting_zone=zone)
    print(" done")


def down_acting_zone(apps, schema_editor):
    pass


def up_legal_movement(apps, schema_editor):
    LegalMoviment = apps.get_model("judicial", "LegalMoviment")

    print(" ", end="")

    print("setando flags em LegalMoviment", end=" ")

    # Atos comuns
    LegalMoviment.objects.filter(
        path_cache__icontains="ATOS COMUNS", children=None
    ).update(administrative_classification=True, judicial_classification=True)

    # Atos finalisticos
    LegalMoviment.objects.filter(
        path_cache__icontains="ATOS FINALISTICOS", children=None
    ).update(administrative_classification=False, judicial_classification=True)

    print("Sucesso", end="")


def down_legal_movement(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        # migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0052_migration_occupation_area"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActingZone",
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
                ("title", models.CharField(unique=True, max_length=200)),
                ("enabled", models.BooleanField(default=True)),
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
                "ordering": ("-enabled", "title"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AdjustmentLawsuit",
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
                ("last_title", models.CharField(max_length=255, blank=True)),
                ("new_title", models.CharField(max_length=255, blank=True)),
                (
                    "last_acting_zone",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.ActingZone",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "last_matters",
                    models.ManyToManyField(
                        related_name="_adjustmentlawsuit_last_matters_+",
                        to="judicial.LegalMatter",
                    ),
                ),
                (
                    "new_acting_zone",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.ActingZone",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "new_matters",
                    models.ManyToManyField(
                        related_name="_adjustmentlawsuit_new_matters_+",
                        to="judicial.LegalMatter",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="DismembermentMultiProcess",
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
            ],
            options={
                "abstract": False,
            },
            bases=(judicial.models.DismembermentProcessMixin, "judicial.partlawsuit"),
        ),
        migrations.CreateModel(
            name="DismembermentMultiProcessChunk",
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
                ("change_title", models.CharField(max_length=255, blank=True)),
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
                    "dismemberment",
                    models.ForeignKey(
                        related_name="chunks",
                        to="judicial.DismembermentMultiProcess",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "matters",
                    models.ManyToManyField(
                        related_name="in_desmemberment_processes_chunk",
                        to="judicial.LegalMatter",
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
                "ordering": ["change_title"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="GeneralMotion",
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
                ("name", models.CharField(max_length=100)),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="GrantConfidentialAccess",
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
                    "apply_in",
                    models.SmallIntegerField(
                        default=100,
                        verbose_name="Aplicar no",
                        choices=[
                            (1, "OUTCOURTLAWSUIT"),
                            (2, "PARTLAWSUIT"),
                            (100, "UNDEFINED"),
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
            name="RevokeConfidentialAccess",
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
                    "apply_in",
                    models.SmallIntegerField(
                        default=100,
                        verbose_name="Aplicar no",
                        choices=[
                            (1, "OUTCOURTLAWSUIT"),
                            (2, "PARTLAWSUIT"),
                            (100, "UNDEFINED"),
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
            name="UnConnect",
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
                    "unconnect_lawsuit",
                    models.ForeignKey(
                        related_name="unconnections",
                        to="judicial.OutCourtLawsuit",
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
            name="Unfold",
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
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AddField(
            model_name="connectionlawsuit",
            name="unconnected_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="connectionlawsuit",
            name="unconnected_by",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="glosary",
            name="meaning_type",
            field=models.SmallIntegerField(
                default=100,
                choices=[
                    (2, "Documento"),
                    (1, "A\xe7\xe3o"),
                    (100, "N\xe3o classificado"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="helper_can_sign",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="judicial_classification",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="suspend_deadline",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="legal_classification",
            field=models.ForeignKey(
                related_name="generalmotion",
                blank=True,
                to="judicial.LegalClassification",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="unfolded_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="unfolded_by",
            field=models.ForeignKey(
                related_name="as_unfolded_by_in_part",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="cause",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "O fato j\xe1 encontra-se solucionado"),
                    (2, "N\xe3o houve recurso"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="content",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="connectionlawsuit",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="dearchivingdispatch",
            name="dearchiving_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Surgimento de novas provas"),
                    (2, "Arquivamento Indevido"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dilationperiod",
            name="justification",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="glosary",
            name="classification_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[(1, "Movimento"), (2, "N\xe3o Procedimental")],
            ),
        ),
        migrations.AlterField(
            model_name="glosary",
            name="legal_classification",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.LegalClassification",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="partlawsuitaccess",
            name="justification",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="remittanceexternal",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="remittanceinternal",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="remittanceitselforgan",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="remittanceitselforgan",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="specialremittanceinternal",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="unfold",
            name="unfold_document",
            field=models.ForeignKey(
                related_name="unfolder",
                to="judicial.PartLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="revokeconfidentialaccess",
            name="part_lawsuit_access",
            field=models.ManyToManyField(
                related_name="in_revokeconfidentialaccess",
                to="judicial.PartLawsuitAccess",
            ),
        ),
        migrations.AddField(
            model_name="grantconfidentialaccess",
            name="part_lawsuit_access",
            field=models.ManyToManyField(
                related_name="in_grantconfidentialaccess",
                to="judicial.PartLawsuitAccess",
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="acting_zone",
            field=models.ForeignKey(
                related_name="lawsuit_acting_zone",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.ActingZone",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuitlog",
            name="acting_zone",
            field=models.ForeignKey(
                related_name="in_log",
                blank=True,
                to="judicial.ActingZone",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="partlawsuit",
            name="acting_zone",
            field=models.ForeignKey(
                related_name="part_lawsuit_acting_zone",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.ActingZone",
                null=True,
            ),
        ),
        migrations.RunPython(up_acting_zone, down_acting_zone),
        migrations.RunPython(up_legal_movement, down_legal_movement),
        migrations.AlterField(
            model_name="dearchivingdispatch",
            name="content",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ordinacereformulated",
            name="ordinance_supplemented",
            field=models.ForeignKey(
                related_name="supplement",
                null=True,
                blank=True,
                to="judicial.OrdinaceReformulated",
                unique=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
