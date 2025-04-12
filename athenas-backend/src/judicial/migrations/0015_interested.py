# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


def up(apps, schema_editor):
    Lawsuit = apps.get_model("judicial", "OutCourtLawsuit")
    Interested = apps.get_model("judicial", "Interested")
    ConnectionLawsuit = apps.get_model("judicial", "ConnectionLawsuit")

    print(" ", end="")

    for lawsuit in Lawsuit.objects.filter():
        if not Interested.objects.filter(
            lawsuit=lawsuit, person=lawsuit.origin.interessado
        ).exists():
            Interested(
                direct=True,
                lawsuit=lawsuit,
                person=lawsuit.origin.interessado,
                created_by=lawsuit.origin.created_by,
                created_at=lawsuit.origin.created_at,
                modified_by=lawsuit.origin.modified_by,
                modified_at=lawsuit.origin.modified_at,
            ).save()

        print("\033[1m\033[32m+\033[0m", end="")

    for connection in ConnectionLawsuit.objects.exclude(signed_by=None):
        lawsuit = connection.lawsuit
        connected = connection.lawsuit_connected

        query = Interested.objects.filter(lawsuit=connected)
        for secundary in query.filter():
            if not Interested.objects.filter(
                lawsuit=lawsuit, person=secundary.person
            ).exists():
                Interested(
                    direct=True,
                    lawsuit=lawsuit,
                    person=secundary.person,
                    created_by=secundary.created_by,
                    created_at=secundary.created_at,
                    modified_by=secundary.modified_by,
                    modified_at=secundary.modified_at,
                ).save()
                print("\033[1m\033[33m+\033[0m", end="")


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0014_auto_20161205_1107"),
    ]

    operations = [
        migrations.CreateModel(
            name="Interested",
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
                ("direct", models.BooleanField(default=False)),
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
                        related_name="has_interested_of_lawsuits",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "lawsuit",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.OutCourtLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RunPython(up, down),
    ]
