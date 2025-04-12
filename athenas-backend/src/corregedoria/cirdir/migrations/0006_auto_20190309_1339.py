# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cirdir", "0005_auto_20190224_2156"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrivateLog",
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
                ("information", models.TextField(null=True, blank=True)),
            ],
            options={
                "verbose_name": "Regirsto de Log Privado",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="controlinformation",
            options={
                "ordering": ["-year", "employee__pessoa_fisica__nome"],
                "verbose_name": "Controle de Informa\xe7\xf5es sobre Doc\xeancia, Resid\xeancia e Finan\xe7as",
                "permissions": (
                    ("can_management_member", "Pode gerenciar o CIRDIR dos Membros"),
                    (
                        "can_management_employee",
                        "Pode gerenciar o CIRDIR dos Servidores",
                    ),
                ),
            },
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="authorization_health",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="privatelog",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="privatelogs",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AddField(
            model_name="privatelog",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="privatelog",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
