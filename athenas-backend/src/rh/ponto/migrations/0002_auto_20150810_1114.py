# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("ponto", "0001_initial"),
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="feriado",
            name="localidades",
            field=models.ManyToManyField(
                related_name="feriados", null=True, to="rh.Localidade", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="feriado",
            unique_together=set([("data", "parte_dia")]),
        ),
        migrations.AddField(
            model_name="falta",
            name="anotacao_geral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Anota\xe7\xe3o Geral",
                blank=True,
                to="rh.AnotacaoGeral",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="falta",
            name="carga_horaria",
            field=models.ForeignKey(
                related_name="faltas",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.CargaHoraria",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="falta",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="falta",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="falta",
            name="servidor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="falta",
            unique_together=set([("data", "servidor")]),
        ),
    ]
