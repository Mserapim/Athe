# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings
from datetime import datetime


def up(apps, schema_editor):
    OutCourtLawsuit = apps.get_model("judicial", "OutCourtLawsuit")
    LawsuitMatter = apps.get_model("judicial", "LawsuitMatter")
    User = apps.get_model("auth", "User")

    user = User.objects.get(username="athenas")

    query = OutCourtLawsuit.objects.filter(matters__isnull=False)
    print("TOTAL de procedimentos ... %s" % query.count())

    for lawsuit in query:
        if lawsuit.matters.count() == 1:
            LawsuitMatter(
                lawsuit=lawsuit,
                principal=True,
                matter=lawsuit.matters.first(),
                created_at=datetime.now(),
                created_by_id=user.pk,
                modified_at=datetime.now(),
                modified_by_id=user.pk,
            ).save()
        else:
            for matter in lawsuit.matters.filter():
                LawsuitMatter(
                    lawsuit=lawsuit,
                    principal=False,
                    matter=matter,
                    created_at=datetime.now(),
                    created_by_id=user.pk,
                    modified_at=datetime.now(),
                    modified_by_id=user.pk,
                ).save()

    print("Pronto!")


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0057_create_pouch_movement"),
    ]

    operations = [
        migrations.CreateModel(
            name="LawsuitMatter",
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
                ("principal", models.BooleanField(default=False)),
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
                    "lawsuit",
                    models.ForeignKey(
                        related_name="in_lawsuit_matter",
                        to="judicial.OutCourtLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "matter",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.LegalMatter",
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
                "ordering": ("-principal",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RenameField(
            model_name="assessmentnoticeoffice",
            old_name="matter",
            new_name="main_matter",
        ),
        migrations.RenameField(
            model_name="ordinacereformulated",
            old_name="matter",
            new_name="other_matters",
        ),
        migrations.AddField(
            model_name="adjustmentlawsuit",
            name="last_main_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="adjustmentlawsuit",
            name="new_main_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="other_matters",
            field=models.ManyToManyField(
                related_name="in_assessment_notice_office", to="judicial.LegalMatter"
            ),
        ),
        migrations.AddField(
            model_name="dismembermentmultiprocesschunk",
            name="main_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="ordinacereformulated",
            name="main_matter",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.LegalMatter",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up, down),
    ]
