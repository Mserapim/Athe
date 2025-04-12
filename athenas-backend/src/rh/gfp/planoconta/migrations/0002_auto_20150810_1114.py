# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0002_auto_20150810_1114"),
        ("planoconta", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="provisionemployee",
            name="employee",
            field=models.ForeignKey(
                related_name="provisions",
                verbose_name="Servidor",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="provisionemployee",
            name="provision_plan",
            field=models.ForeignKey(
                related_name="provisions_employee",
                verbose_name="Plano de Provis\xe3o",
                to="planoconta.ProvisionPlan",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="provision",
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
            model_name="provision",
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
            model_name="provision",
            name="provision_employee",
            field=models.ForeignKey(
                related_name="provisions",
                verbose_name="Provis\xe3o do Servidor",
                to="planoconta.ProvisionEmployee",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="provision",
            name="provision_manager",
            field=models.ForeignKey(
                related_name="provisions",
                verbose_name="Gertor de Provis\xe3o",
                to="planoconta.ProvisionManager",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="planoconta",
            name="plano",
            field=models.ForeignKey(
                related_name="contas",
                to="planoconta.Plano",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="planoconta",
            unique_together=set(
                [
                    (
                        "inscricao_ne",
                        "evento_nld",
                        "evento_nlc",
                        "classificacao_nld",
                        "classificacao_nlc",
                        "plano",
                        "tipo",
                        "finalidade",
                        "regime_previdenciario",
                    )
                ]
            ),
        ),
        migrations.AddField(
            model_name="plano",
            name="banco",
            field=models.ForeignKey(
                related_name="em_plano",
                to="rh.Banco",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="plano",
            name="eventos",
            field=models.ManyToManyField(related_name="em_plano", to="gfp.Evento"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="plano",
            name="folha_tipo",
            field=models.ForeignKey(
                related_name="planos", to="gfp.FolhaTipo", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="plano",
            name="genre_events",
            field=models.ManyToManyField(related_name="em_plano", to="gfp.GenreEvent"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="plano",
            name="pessoa_juridica",
            field=models.ForeignKey(
                related_name="planos", to="rh.PessoaJuridica", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="plano",
            unique_together=set([("folha_tipo", "ano_calendario", "tipo", "titulo")]),
        ),
    ]
