# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import standard.models
import django.db.models.deletion

from django.db import migrations, models
from django.conf import settings


def up_populate(apps, schema_editor):
    from judicial.models import OutCourtLawsuit

    EventControl = apps.get_model("judicial.EventControl")

    count = OutCourtLawsuit.objects.count()
    current = 0
    message = ""

    for lawsuit in OutCourtLawsuit.objects.filter():
        number = 1
        current += 1
        sys.stdout.write("\b" * len(message))
        message = " [%d de %d (%0.1f%%)] " % (
            current,
            count,
            ((float(current) / float(count)) * 100.0),
        )
        sys.stdout.write(message)
        sys.stdout.flush()

        bulk = []
        for part in lawsuit._all_signed_documents(False):
            bulk.append(
                EventControl(
                    lawsuit_id=lawsuit.pk, part_id=part.pk, number_control=number
                )
            )
            number += 1
        EventControl.objects.bulk_create(bulk)


def down_populate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        # migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0060_add_remaining_days"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthorizationExternalAccess",
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
                ("justification", models.TextField(blank=True)),
                (
                    "state",
                    models.SmallIntegerField(
                        verbose_name="Acesso",
                        choices=[(1, "DEFERIDO"), (2, "REVOGADO"), (3, "INDEFERIDO")],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="EventControl",
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
                ("number_control", models.SmallIntegerField()),
            ],
            options={
                "ordering": ("lawsuit", "number_control"),
            },
        ),
        migrations.CreateModel(
            name="RequestExternalAccess",
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
                ("request", models.TextField(null=True, blank=True)),
                ("rendered_request_cache", models.TextField(null=True, blank=True)),
                ("authorized_at", models.DateTimeField(null=True, blank=True)),
                ("revoked_at", models.DateTimeField(null=True, blank=True)),
                ("denied_at", models.DateTimeField(null=True, blank=True)),
                (
                    "state",
                    models.SmallIntegerField(
                        default=1,
                        verbose_name="Situa\xe7\xe3o",
                        choices=[
                            (1, "N\xc3\x83O AVALIADO"),
                            (2, "AUTORIZADO"),
                            (3, "REVOGADO"),
                            (4, "NEGADO"),
                        ],
                    ),
                ),
                (
                    "as_representative_of",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Pessoa",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "authorized_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "denied_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "person",
                    models.ForeignKey(
                        related_name="with_external_access_lawsuit",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "revoked_by",
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
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="RequestExternalPartLegalSign",
            fields=[
                (
                    "partlegalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.partlegalsign",),
        ),
        migrations.AddField(
            model_name="judicialdiligence",
            name="count_type",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Contagem",
                choices=[(1, "DIAS CORRIDOS"), (2, "DIAS UTEIS")],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="eventcontrol",
            name="discarded_by",
            field=models.ForeignKey(
                related_name="has_discard_event",
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="eventcontrol",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="+",
                to="judicial.OutCourtLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="eventcontrol",
            name="part",
            field=models.ForeignKey(
                related_name="has_event_controls",
                to="judicial.PartLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="authorizationexternalaccess",
            name="request_external_access",
            field=models.ForeignKey(
                related_name="in_authorization_external_access",
                to="judicial.RequestExternalAccess",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up_populate, down_populate),
    ]
