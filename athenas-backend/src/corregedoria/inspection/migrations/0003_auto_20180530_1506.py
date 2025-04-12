# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0063_auto_20180529_2058"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inspection", "0002_auto_20180522_1242"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sign",
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
                ("dispatch", models.TextField(null=True, blank=True)),
                (
                    "profile",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="TIPO",
                        blank=True,
                        choices=[(1, "CORREGEDOR-GERAL"), (2, "PROMOTOR-CORREGEDOR")],
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Assinaturas do Promotor-corregedor e do Corregedor-geral",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="recommendations",
            options={"verbose_name": "Recomenda\xe7\xf5es gerais na inspe\xe7\xe3o"},
        ),
        migrations.RenameField(
            model_name="outcourtlawsuitcount",
            old_name="number_of_tac_administrative_dishonesty",
            new_name="number_of_acp_administrative_dishonesty",
        ),
        migrations.AddField(
            model_name="inspection",
            name="responsible",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attachments",
            name="attachment_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="TIPO DE ANEXO",
                blank=True,
                choices=[
                    (1, "Editais"),
                    (2, "Portaria de Delega\xe7\xe3o"),
                    (3, "Certid\xf5es"),
                    (4, "Ata"),
                    (5, "Pe\xe7as"),
                    (6, "Audi\xeancias"),
                    (7, "Tabelas Extrajudiciais"),
                    (8, "Impugna\xe7\xf5es"),
                    (9, "Cumprimento de Senten\xe7as"),
                    (10, "Relat\xf3rios e-Proc"),
                    (11, "Imagens"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="employee",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="sign",
            name="inspection",
            field=models.ForeignKey(
                related_name="signs",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="sign",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
