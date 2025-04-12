# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0007_auto_20160929_1615"),
    ]

    operations = [
        migrations.AddField(
            model_name="diligence",
            name="assumed_delivery_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="diligence",
            name="assumed_delivery_by",
            field=models.ForeignKey(
                related_name="diligences_assumed",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="diligence",
            name="prevent_delivery_in_executionorgan",
            field=models.BooleanField(default=False),
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
    ]
