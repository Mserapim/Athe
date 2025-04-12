# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0063_change_from_of_pouch"),
    ]

    operations = [
        migrations.CreateModel(
            name="JudicialChoice",
            fields=[
                (
                    "choice_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="standard.Choice",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "classification",
                    models.ForeignKey(
                        related_name="has_judicial_choices",
                        blank=True,
                        to="judicial.LegalClassification",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("standard.choice",),
        ),
        migrations.AddField(
            model_name="legalclass",
            name="instauration",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "DOCUMENTO DE INSTAURA\xc7\xc3O"),
                    (2, "PORTARIA DE INSTAURA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tag",
            name="classification",
            field=models.OneToOneField(
                related_name="has_tags",
                null=True,
                blank=True,
                to="judicial.LegalClassification",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunSQL(
            "INSERT INTO judicial_judicialchoice(choice_ptr_id) SELECT id FROM standard_choice WHERE app_label IN ('judicial', 'tac', 'council')",
            "SELECT 1",
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="main_tag",
            field=models.ForeignKey(
                related_name="has_main_tag_in_lawsuits",
                to="judicial.Tag",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="outcourtlawsuitlog",
            name="main_tag",
            field=models.ForeignKey(
                related_name="has_main_tag_in_lawsuit_log",
                to="judicial.Tag",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
