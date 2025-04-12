# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import judicial.models
import django

from django.db import migrations, models
from django.conf import settings
from django.core.management import call_command

FIXTURES = (
    "fixtures/0027-choices-new-delivery-status.json",
    "fixtures/0028-choices-who-type.json",
)


def up_load_data(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "judicial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def up_update_data(apps, schema_editor):
    print("Running update diligence...")
    Manifestation = apps.get_model("judicial", "Manifestation")
    JudicialDiligence = apps.get_model("judicial", "JudicialDiligence")

    print("Update status aguardando resposta...")
    aguardando_resposta = Manifestation.objects.filter(
        remaining_days__gte=0, signed_at=None
    )
    quantidade_diligences_atualizadas = JudicialDiligence.objects.filter(
        has_manifestations__in=aguardando_resposta
    ).update(delivery_status=9)
    print("%d registros atualizados" % quantidade_diligences_atualizadas)

    print("Update status atrasados...")
    atrasados = Manifestation.objects.filter(remaining_days__lt=0, signed_at=None)
    quantidade_diligences_atualizadas = JudicialDiligence.objects.filter(
        has_manifestations__in=atrasados
    ).update(delivery_status=10)
    print("%d registros atualizados" % quantidade_diligences_atualizadas)

    print("Update status finalizados...")
    finalizados = Manifestation.objects.exclude(signed_at=None)
    quantidade_diligences_atualizadas = JudicialDiligence.objects.filter(
        has_manifestations__in=finalizados
    ).update(delivery_status=99)
    print("%d registros atualizados" % quantidade_diligences_atualizadas)


def down_fake(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0068_fix_django19"),
        ("protocolo", "0019_groupperson_locality"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="ordinacereformulated",
            name="ordinance_supplemented",
            field=models.OneToOneField(
                related_name="supplement",
                null=True,
                blank=True,
                to="judicial.OrdinaceReformulated",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="diligence",
            name="is_copy_of",
            field=models.ForeignKey(
                related_name="is_copy_by",
                blank=True,
                to="judicial.Diligence",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.CreateModel(
            name="DeliveryAttemptLegalSign",
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
                ),  # Parametro "on_delete" adicionado. (Django 2))
            ],
            bases=(judicial.models.JudicialLegalSign, "protocolo.legalsign"),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="signed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
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
            model_name="deliveryattempt",
            name="cancel_delivery_type",
            field=models.SmallIntegerField(
                blank=True, null=True, choices=[(1, "Local n\xe3o encontrado")]
            ),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                    (6, "Publica\xe7\xe3o em di\xe1rio Oficial"),
                    (7, "Entrega pelo \xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="deliveryattemptlegalsign",
            name="delivery_attempt",
            field=models.ForeignKey(
                related_name="legal_signs",
                to="judicial.DeliveryAttempt",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="cache_rendered",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="deliveryattempt",
            name="is_signed_by_system",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="attacheddocument",
            name="diligence",
            field=models.ForeignKey(
                related_name="as_diligence_answer",
                blank=True,
                to="judicial.Diligence",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.CreateModel(
            name="ResponseOfficer",
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
                ("text", models.TextField()),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "ordering": ("signed_at",),
            },
        ),
        migrations.AlterField(
            model_name="attacheddocument",
            name="attached_title",
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="attacheddocument",
            name="attached_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                blank=True,
                choices=[
                    (1, "Documentos"),
                    (2, "Galeria de Fotos"),
                    (3, "Galeria de Videos"),
                    (4, "Galeria de \xc1udio"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="responseofficer",
            name="diligence",
            field=models.ForeignKey(
                related_name="has_responses",
                on_delete=django.db.models.deletion.PROTECT,
                to="judicial.JudicialDiligence",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="responseofficer",
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
            model_name="attached",
            name="attached_response_officer",
            field=models.ForeignKey(
                related_name="attaches",
                blank=True,
                to="judicial.ResponseOfficer",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up_load_data, down_fake),
        migrations.RunPython(up_update_data, down_fake),
    ]
