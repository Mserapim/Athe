# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        ("gecap", "0002_inscricao_certificado"),
    ]

    operations = [
        migrations.AddField(
            model_name="inscricao",
            name="servidor",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="inscricoes", to="rh.Servidor", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="inscricao",
            unique_together=set([("capacitacao", "servidor")]),
        ),
        migrations.AddField(
            model_name="capacitacao",
            name="area_conhecimento",
            field=models.ManyToManyField(
                related_name="capacitacoes",
                null=True,
                to="gecap.AreaConhecimento",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="capacitacao",
            name="cidade_evento",
            field=models.ForeignKey(
                related_name="capacitacoes",
                to="rh.Localidade",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="capacitacao",
            name="promotores",
            field=models.ManyToManyField(
                related_name="capacitacoes", null=True, to="rh.OrgaoGeral", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="areaconhecimento",
            name="sub_area_de",
            field=models.ForeignKey(
                related_name="sub_areas",
                blank=True,
                to="gecap.AreaConhecimento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
