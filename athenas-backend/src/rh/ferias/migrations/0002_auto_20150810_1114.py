# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0001_initial"),
        ("rh", "0002_auto_20150810_1114"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0001_initial"),
        ("gfp", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoaquisitivoservidorusufruto",
            name="autorizado_por",
            field=models.ForeignKey(
                related_name="ferias_autorizadas",
                blank=True,
                to="rh.Servidor",
                help_text="O servidor (Chefe) que autorizou essa parcela",
                null=True,
                verbose_name="Autorizado por",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivoservidorusufruto",
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
            model_name="periodoaquisitivoservidorusufruto",
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
            model_name="periodoaquisitivoservidorusufruto",
            name="periodo_aquisitivo_servidor",
            field=models.ForeignKey(
                related_name="usufrutos",
                verbose_name="Per\xc3\xadodo aquisitivo",
                to="ferias.PeriodoAquisitivoServidor",
                help_text="O per\xc3\xadodo aquisitivo refente a que o servidor tem direito.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
            name="content_type",
            field=models.ForeignKey(
                to="contenttypes.ContentType", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
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
            model_name="periodoaquisitivoservidor",
            name="folha_evento_terco_constitucional",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="gfp.FolhaEvento",
                help_text="Refer\xc3\xaancia \xc3\xa0 folha e evento que gerou o pagamento do ter\xc3\xa7o constitucional para o per\xc3\xadodo aquisitivo.",
                null=True,
                verbose_name="Folha Evento",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
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
            model_name="periodoaquisitivoservidor",
            name="periodo_aquisitivo",
            field=models.ForeignKey(
                related_name="paservidores",
                verbose_name="Per\xc3\xadodo aquisitivo",
                to="ferias.PeriodoAquisitivo",
                help_text="O per\xc3\xadodo aquisitivo refente a que o servidor tem direito.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
            name="servidor",
            field=models.ForeignKey(
                related_name="periodos_aquisitivos",
                verbose_name="Servidor",
                to="rh.Servidor",
                help_text="O servidor que pode marcar f\xc3\xa9rias para o per\xc3\xadodo aquisitivo solicitado.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="periodoaquisitivoservidor",
            unique_together=set([("servidor", "periodo_aquisitivo")]),
        ),
        migrations.AddField(
            model_name="periodoaquisitivo",
            name="configuracao",
            field=models.ForeignKey(
                verbose_name="Configura\xc3\xa7\xc3\xa3o de f\xc3\xa9rias",
                to="ferias.Configuracao",
                help_text="A configura\xc3\xa7\xc3\xa3o de f\xc3\xa9rias utilizado para esse per\xc3\xadodo aquisitivo.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="periodoaquisitivo",
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
            model_name="periodoaquisitivo",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="periodoaquisitivo",
            unique_together=set([("ano_aquisicao", "configuracao", "periodo")]),
        ),
        migrations.AddField(
            model_name="pasualteracao",
            name="pasu_alterado",
            field=models.ForeignKey(
                related_name="pasu_alteracao",
                verbose_name="Usufruto alterado",
                to="ferias.PeriodoAquisitivoServidorUsufruto",
                help_text="O usufruto que foi alterado por esse.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="configuracao",
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
            model_name="configuracao",
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
            model_name="alteracaopasu",
            name="anotacao",
            field=models.ForeignKey(
                related_name="alteracoes_ferias",
                blank=True,
                to="rh.AnotacaoFerias",
                help_text="Anota\xc3\xa7\xc3\xa3o de Altera\xc3\xa7\xc3\xa3o.",
                null=True,
                verbose_name="Anota\xc3\xa7\xc3\xa3o",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="alteracaopasu",
            name="antigos_pasus",
            field=models.ManyToManyField(
                related_name="alteracao_out",
                verbose_name="Antigos",
                to="ferias.PeriodoAquisitivoServidorUsufruto",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="alteracaopasu",
            name="autorizado_por",
            field=models.ForeignKey(
                related_name="autorizacoes_ferias",
                blank=True,
                to="rh.Servidor",
                help_text="O servidor (Chefe) que autorizaou essa parcela",
                null=True,
                verbose_name="Autorizado por",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="alteracaopasu",
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
            model_name="alteracaopasu",
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
            model_name="alteracaopasu",
            name="novos_pasus",
            field=models.ManyToManyField(
                related_name="alteracao_in",
                verbose_name="Novos",
                to="ferias.PeriodoAquisitivoServidorUsufruto",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="alteracaopasu",
            name="pas",
            field=models.ForeignKey(
                related_name="alteracoes",
                blank=True,
                to="ferias.PeriodoAquisitivoServidor",
                help_text="Altera\xc3\xa7\xc3\xa3o de parcelas de um servidor em um determinado per\xc3\xadodo aquisitivo.",
                null=True,
                verbose_name="Altera\xc3\xa7\xc3\xa3o",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
