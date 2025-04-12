# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("estagio", "0002_auto_20150810_1114"),
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("questionario", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="integrantescomissao",
            name="servidor_id",
            field=models.ForeignKey(
                to="rh.Servidor", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="fatoravaliacao",
            name="configuracao",
            field=models.ForeignKey(
                related_name="fator_avaliacao",
                to="estagio.Configuracao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioprobatorioservidor",
            name="configuracao",
            field=models.ForeignKey(
                verbose_name="Configuracao",
                to="estagio.Configuracao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioprobatorioservidor",
            name="posse_servidor",
            field=models.ForeignKey(
                related_name="estagio_probatorio",
                to="rh.MovimentacaoPosse",
                unique=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioprobatorioservidor",
            name="publicacao_homologacao",
            field=models.ForeignKey(
                related_name="+",
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagiocomissaoservidor",
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
            model_name="estagiocomissaoservidor",
            name="estagio_prob_servidor",
            field=models.ForeignKey(
                related_name="comissao_estagio",
                to="estagio.EstagioProbatorioServidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagiocomissaoservidor",
            name="integrante_comissao_avaliadora",
            field=models.ManyToManyField(
                related_name="comissao_estagio", to="estagio.IntegrantesComissao"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagiocomissaoservidor",
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
            model_name="estagioavaliacao",
            name="avaliado",
            field=models.ForeignKey(
                related_name="avaliacoes",
                on_delete=django.db.models.deletion.PROTECT,
                to="estagio.EstagioProbatorioServidor",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="avaliador",
            field=models.ForeignKey(
                related_name="avaliacao_estagio",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="cargo_avaliado",
            field=models.ForeignKey(
                related_name="+", to="rh.Cargo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="cargo_avaliador",
            field=models.ForeignKey(
                related_name="+", to="rh.Cargo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="finalizado_por",
            field=models.ForeignKey(
                related_name="+", to="rh.Servidor", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="lotacao_avaliado",
            field=models.ForeignKey(
                related_name="+", to="rh.Lotacao", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="lotacao_avaliador",
            field=models.ForeignKey(
                related_name="+", to="rh.Lotacao", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="estagioavaliacao",
            name="questionario_resposta",
            field=models.ForeignKey(
                related_name="estagio_avaliacao",
                to="questionario.QuestionarioResposta",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="decisaochefeorgao",
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
            model_name="decisaochefeorgao",
            name="estagio_comissao_servidor",
            field=models.ForeignKey(
                related_name="decisao_chefe_orgao",
                to="estagio.EstagioComissaoServidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="decisaochefeorgao",
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
            model_name="configuracao",
            name="conceitos",
            field=models.ManyToManyField(
                related_name="configuracao", to="estagio.Conceito"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="configuracao",
            name="configuracao_anterior",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="estagio.Configuracao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="configuracao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="estagio_configuracao",
                to="rh.Publicacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="configuracao",
            name="questionario",
            field=models.ForeignKey(
                related_name="estagio_configuracao",
                to="questionario.Questionario",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="configuracao",
            name="questionario_manifestacao_servidor",
            field=models.ForeignKey(
                related_name="manifestacao_servidor",
                blank=True,
                to="questionario.Questionario",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="comissaoavaliadora",
            name="comissao_anterior",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="estagio.ComissaoAvaliadora",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="comissaoavaliadora",
            name="integrantes",
            field=models.ManyToManyField(
                to="rh.Servidor", through="estagio.IntegrantesComissao"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="comissaoavaliadora",
            name="publicacao",
            field=models.ForeignKey(
                related_name="+", to="rh.Publicacao", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="apreciacaocomissao",
            name="comissao_servidor",
            field=models.ForeignKey(
                related_name="apreciacao_comissao",
                to="estagio.EstagioComissaoServidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="apreciacaocomissao",
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
            model_name="apreciacaocomissao",
            name="integrante_avaliador",
            field=models.ForeignKey(
                related_name="+",
                to="estagio.IntegrantesComissao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="apreciacaocomissao",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
    ]
