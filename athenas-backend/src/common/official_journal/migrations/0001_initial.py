# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0003_auto_20151014_1609"),
    ]

    operations = [
        migrations.CreateModel(
            name="JournalBase",
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
                ("UID", models.CharField(max_length=50, db_index=True)),
                ("name", models.CharField(max_length=150)),
                ("published_date", models.DateTimeField(null=True, db_index=True)),
                ("text", models.TextField()),
            ],
            options={
                "ordering": ["published_date"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Journal",
            fields=[
                (
                    "journalbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="official_journal.JournalBase",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("code", models.IntegerField(db_index=True)),
            ],
            options={
                "ordering": ["-code"],
            },
            bases=("official_journal.journalbase",),
        ),
        migrations.CreateModel(
            name="Suplement",
            fields=[
                (
                    "journalbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="official_journal.JournalBase",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "journal",
                    models.ForeignKey(
                        related_name="suplements",
                        to="official_journal.Journal",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("official_journal.journalbase",),
        ),
        migrations.AddField(
            model_name="journalbase",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="journalbase",
            name="ged",
            field=models.ForeignKey(
                related_name="official_journals",
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="journalbase",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
    ]
