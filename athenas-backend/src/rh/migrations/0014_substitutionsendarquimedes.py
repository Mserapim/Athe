# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0013_auto_20160114_1341"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubstitutionSendArquimedes",
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
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
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
                    "substitution",
                    models.ForeignKey(
                        related_name="sended_arquimedes",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.MovimentacaoSubstituicaoMembro",
                    ),
                ),
            ],
            options={
                "db_table": "rh_subssendarquimedes",
                "verbose_name": "Movimenta\xe7\xe3o enviada ao Arquimedes",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
