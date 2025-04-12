# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("protocolo", "0004_auto_20150826_1640"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalSign",
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
                ("when", models.DateTimeField()),
                ("plain_content", models.TextField()),
                ("content", models.TextField()),
                ("content_sign", models.CharField(max_length=100)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MovimentLegalSign",
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
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "moviment",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="protocolo.Movimentacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("protocolo.legalsign",),
        ),
        migrations.CreateModel(
            name="ProtocolLegalSign",
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
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "protocol",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="protocolo.Protocolo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("protocolo.legalsign",),
        ),
        migrations.AddField(
            model_name="legalsign",
            name="who",
            field=models.ForeignKey(
                related_name="sign_documents",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="protocolo",
            name="cache_rendered",
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
