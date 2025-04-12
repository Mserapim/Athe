# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0065_use_of_legal_class_fix_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchivingRemittance",
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
                    "department",
                    models.ForeignKey(
                        related_name="+", to="rh.Lotacao", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="ResumeDeadline",
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
        migrations.CreateModel(
            name="SuspendDeadline",
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
                ("remaining_days", models.SmallIntegerField(blank=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AlterField(
            model_name="dilationperiod",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo do Procedimento",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="legalclass",
            name="instauration",
            field=models.SmallIntegerField(
                blank=True, null=True, choices=[(1, "Documento"), (2, "Portaria")]
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo do Procedimento",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuitlog",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                verbose_name="Tipo do Procedimento",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="rejectionlinkother",
            name="other_lawsuit",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Procedimento Extrajudicial"),
                    (2, "Procedimento Judicial"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="classification",
            field=models.OneToOneField(
                related_name="has_tag",
                null=True,
                blank=True,
                to="judicial.LegalClassification",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="resumedeadline",
            name="suspend_deadline",
            field=models.OneToOneField(
                blank=True, to="judicial.SuspendDeadline", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
