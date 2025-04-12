# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0006_auto_20160510_1054"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avaliacao",
            name="neutralizado_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="replica",
            field=models.CharField(max_length=2000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="sugestao",
            field=models.CharField(max_length=2000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="baseconhecimento",
            name="arquivo",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                blank=True,
                to="ged.Arquivo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="baseconhecimento",
            name="modelo",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                blank=True, to="siatu.Modelo", null=True, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="chamado_anterior",
            field=models.OneToOneField(
                related_name="chamado_reincidente",
                null=True,
                blank=True,
                to="siatu.Chamado",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="data_fila_atendimento",
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="fila",
            field=models.ForeignKey(
                related_name="chamados",
                blank=True,
                to="siatu.FilaUnica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="motivo_cancelado",
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="motivo_urgencia",
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="nao_urgente_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="reincidencia",
            field=models.OneToOneField(
                null=True, blank=True, to="siatu.Reincidencia", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="chamado",
            name="status_atual",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                blank=True,
                to="siatu.Status",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="itembaseconhecimento",
            name="info",
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="reincidencia",
            name="motivo_gerente",
            field=models.CharField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="reincidencia",
            name="opiniao_atendente",
            field=models.CharField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servico",
            name="servico_superior",
            field=models.ForeignKey(
                related_name="subservicos",
                blank=True,
                to="siatu.Servico",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="transferencia",
            name="aceito_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="transferencia",
            name="data_aceite",
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
