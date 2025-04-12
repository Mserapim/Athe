# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("protocolo", "0012_auto_20160510_0854"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalsign",
            name="invalidated_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="legalsign",
            name="invalidated_by",
            field=models.ForeignKey(
                related_name="sign_invalided_documents",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="assunto",
            field=models.CharField(db_index=True, max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="cache_rendered",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="codigo",
            field=models.CharField(
                db_index=True, unique=True, max_length=50, blank=True
            ),
        ),
    ]
