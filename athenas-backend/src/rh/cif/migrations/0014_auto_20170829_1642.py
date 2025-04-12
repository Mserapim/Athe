# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0003_auto_20151014_1609"),
        ("rh", "0050_auto_20170725_1836"),
        ("cif", "0013_auto_20170123_1729"),
    ]

    operations = [
        migrations.CreateModel(
            name="AddressCif",
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
                    "start_date",
                    models.DateField(
                        null=True,
                        verbose_name="Data In\xedcio Resid\xeancia",
                        blank=True,
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        null=True, verbose_name="Data Fim Resid\xeancia", blank=True
                    ),
                ),
                (
                    "type_residence",
                    models.SmallIntegerField(
                        default=0,
                        null=True,
                        verbose_name="Tipo de Resid\xeancia",
                        blank=True,
                        choices=[(1, "CASA"), (2, "APARTAMENTO")],
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status",
                        blank=True,
                        choices=[(1, "N\xc3O ALTERADO"), (2, "ALTERADO")],
                    ),
                ),
                (
                    "status_pendency",
                    models.SmallIntegerField(
                        default=1,
                        null=True,
                        verbose_name="Status Pend\xeancia",
                        blank=True,
                        choices=[(1, "SEM PEND\xcaNCIA"), (2, "COM PEND\xcaNCIA")],
                    ),
                ),
                (
                    "block_change",
                    models.BooleanField(
                        default=False,
                        verbose_name="Bloqueia a altera\xe7\xe3o da informa\xe7\xe3o",
                    ),
                ),
                (
                    "authorization_reside_outside",
                    models.BooleanField(
                        default=False,
                        verbose_name="Autoriza\xe7\xe3o para residir fora da comarca",
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
                (
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Anexo",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "member",
                    models.ForeignKey(
                        related_name="address",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Membro",
                        to="cif.ControlInformationMember",
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
                    "previus_addres",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Endere\xe7o Anterior",
                        blank=True,
                        to="cif.AddressCif",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ref_address",
                    models.ForeignKey(
                        related_name="cif_address",
                        verbose_name="Endere\xe7o",
                        blank=True,
                        to="rh.Endereco",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RemoveField(
            model_name="address",
            name="endereco_ptr",
        ),
        migrations.RemoveField(
            model_name="address",
            name="file_document",
        ),
        migrations.RemoveField(
            model_name="address",
            name="member",
        ),
        migrations.RemoveField(
            model_name="address",
            name="previus_addres",
        ),
        migrations.RemoveField(
            model_name="address",
            name="refperiod_address",
        ),
        migrations.AddField(
            model_name="referenceperiod",
            name="status_period",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Status do per\xedodo",
                blank=True,
                choices=[(1, "ATIVO"), (2, "INATIVO")],
            ),
        ),
        migrations.DeleteModel(
            name="Address",
        ),
        migrations.AddField(
            model_name="addresscif",
            name="refperiod_address",
            field=models.ForeignKey(
                related_name="ref_address",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                blank=True,
                to="cif.ReferencePeriod",
                null=True,
            ),
        ),
    ]
