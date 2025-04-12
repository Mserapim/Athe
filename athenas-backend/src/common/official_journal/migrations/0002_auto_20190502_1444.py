# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("official_journal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="journal",
            name="extra",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="journal",
            name="code",
            field=models.IntegerField(db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name="journal",
            name="journalbase_ptr",
            field=models.OneToOneField(
                parent_link=True,
                related_name="journal_child",
                primary_key=True,
                serialize=False,
                to="official_journal.JournalBase",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="journalbase",
            name="UID",
            field=models.CharField(db_index=True, max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name="journalbase",
            name="ged",
            field=models.ForeignKey(
                related_name="official_journals",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="journalbase",
            name="name",
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.AlterField(
            model_name="journalbase",
            name="published_date",
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="journalbase",
            name="text",
            field=models.TextField(blank=True),
        ),
    ]
