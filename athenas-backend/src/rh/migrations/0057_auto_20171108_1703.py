# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


def up(apps, schema_editor):
    pass


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0056_datamigration_refactoring"),
    ]

    operations = [
        migrations.CreateModel(
            name="Replacement",
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
                ("order", models.PositiveIntegerField(default=1)),
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
                    "document",
                    models.ForeignKey(
                        related_name="replacement",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Publicacao",
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
                    "replaced",
                    models.ForeignKey(
                        related_name="replacement_replaceds",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Lotacao",
                    ),
                ),
                (
                    "substitute",
                    models.ForeignKey(
                        related_name="substitutes",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Lotacao",
                    ),
                ),
            ],
            options={
                "ordering": ("replaced__nome",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RunPython(up, down),
    ]
