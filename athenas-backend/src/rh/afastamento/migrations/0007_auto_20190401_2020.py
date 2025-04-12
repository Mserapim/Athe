# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0080_auto_20190401_2020"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("afastamento", "0006_auto_20180207_1659"),
    ]

    operations = [
        migrations.CreateModel(
            name="HealthCertificate",
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
                    "cid",
                    models.CharField(
                        max_length=4, null=True, verbose_name="CID", blank=True
                    ),
                ),
                ("days_granted", models.IntegerField(verbose_name="Dias concedidos")),
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
                    "healthcare_professional",
                    models.ForeignKey(
                        related_name="healthcertificate",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Profissional Sa\xfade",
                        blank=True,
                        to="rh.ProfissionalSaude",
                        null=True,
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="licencamandatoclassista",
            name="onus_payment",
            field=models.IntegerField(default=1, verbose_name="\xd4nus"),
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="consequence_of",
            field=models.ForeignKey(
                related_name="license_consequence_of",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="afastamento.Licenca",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="process_rectification",
            field=models.ForeignKey(
                related_name="health_lisense",
                verbose_name="Processo de Retifica\xe7\xe3o",
                blank=True,
                to="rh.LegalProcess",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="related_work",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="licencasaude",
            name="acidente_transito",
            field=models.IntegerField(
                default=3, blank=True, choices=[(1, "ATROPELAMENTO"), (2, "COLIS\xc3O")]
            ),
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="health_certificate",
            field=models.ManyToManyField(
                related_name="health_lisense",
                verbose_name="Atestados",
                to="afastamento.HealthCertificate",
            ),
        ),
    ]
