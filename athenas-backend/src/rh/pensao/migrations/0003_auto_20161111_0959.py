# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0027_auto_20161111_0957"),
        ("pensao", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pensao",
            name="dedutivel_irrf",
        ),
        migrations.RemoveField(
            model_name="pensao",
            name="degree_kinship",
        ),
        migrations.AddField(
            model_name="pensao",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 11, 11, 9, 58, 52, 312617),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=845,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="event_employee",
            field=models.ForeignKey(
                related_name="pensions_as_event_employee",
                default=1237,
                verbose_name="Evento no servidor",
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="event_pensioner",
            field=models.ForeignKey(
                related_name="pensions_as_event_pensioner",
                default=1498,
                verbose_name="Evento no pensionista",
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="events",
            field=models.ManyToManyField(
                related_name="pension_events",
                verbose_name="Eventos",
                to="gfp.Evento",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="pensao",
            name="modified_at",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 11, 11, 9, 59, 13, 937958),
                auto_now=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                default=845,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pensao",
            name="type_of_pension",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo",
                choices=[(1, "ALIMENT\xcdCIA"), (2, "MORTE")],
            ),
        ),
        migrations.AlterField(
            model_name="pensao",
            name="representante_legal",
            field=models.ForeignKey(
                related_name="pensao_representante_legal",
                blank=True,
                to="rh.PessoaFisica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="pensao",
            name="tipo",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo do Valor",
                choices=[
                    (1, "VALOR FIXO"),
                    (2, "PERCENTUAL"),
                    (3, "SAL\xc1RIO M\xcdNIMO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pensaoevento",
            name="tipo",
            field=models.SmallIntegerField(
                default=1,
                blank=True,
                verbose_name="Tipo do Valor",
                choices=[
                    (1, "VALOR FIXO"),
                    (2, "PERCENTUAL"),
                    (3, "SAL\xc1RIO M\xcdNIMO"),
                ],
            ),
        ),
    ]
