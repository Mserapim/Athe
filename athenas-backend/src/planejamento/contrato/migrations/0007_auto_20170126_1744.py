# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings

from planejamento.contrato.models import Contrato, ValorContrato

# from django.contrib.auth.models import User
# from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger(__name__)
# set_current_user(User.objects.get(username='athenas'))


def update_contrato(apps, schema_editor):
    Contrato.objects.filter(tipo_medicao=0).update(tipo_medicao=100)
    Contrato.objects.filter(dias_para_aviso=0).update(dias_para_aviso=100)
    Contrato.objects.filter(tipo_licitacao=0).update(tipo_licitacao=100)
    ValorContrato.objects.filter(ordem=0).update(ordem=100)
    log.debug("Atualizacao do campo tipo_medicao")


def revert_contrato(apps, schema_editor):
    Contrato.objects.filter(tipo_medicao=100).update(tipo_medicao=0)
    Contrato.objects.filter(dias_para_aviso=100).update(dias_para_aviso=0)
    Contrato.objects.filter(tipo_licitacao=100).update(tipo_licitacao=0)
    ValorContrato.objects.filter(ordem=100).update(ordem=0)
    log.debug("Backward da funcao de atualizacao de contrato")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contrato", "0006_auto_20160510_1457"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicao",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 1, 26, 17, 41, 5, 602774),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="medicao",
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
            model_name="medicao",
            name="modified_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 1, 26, 17, 43, 10, 763511),
                auto_now=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="medicao",
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
            model_name="medicao",
            name="tempst",
            field=models.IntegerField(default=1, blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notaempenho",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 1, 26, 17, 43, 46, 144082),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notaempenho",
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
            model_name="notaempenho",
            name="modified_at",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 1, 26, 17, 44, 0, 156265), auto_now=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notaempenho",
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
        migrations.AlterField(
            model_name="acaocontrato",
            name="tipo",
            field=models.SmallIntegerField(
                choices=[
                    (0, "Cadastro do contrato"),
                    (1, "Pedir prorroga\xe7\xe3o"),
                    (2, "Aceitar pedido de prorroga\xe7\xe3o"),
                    (3, "Negar pedido de prorroga\xe7\xe3o"),
                    (4, "Pedir Licita\xe7\xe3o"),
                    (5, "Negar Licita\xe7\xe3o"),
                    (6, "Licitar"),
                    (7, "Finalizar contrato"),
                    (8, "Pedir rescis\xe3o contratual"),
                    (9, "Aceitar pedido de rescis\xe3o contratual"),
                    (10, "Negar pedido de rescis\xe3o contratual"),
                    (11, "Alertar vencimento do Contrato"),
                    (12, "Solicita\xe7\xe3o de pagamento"),
                    (13, "Lan\xe7ar pagamento"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="dias_para_aviso",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (90, "3 meses antes do vencimento"),
                    (100, "N\xe3o avisar"),
                    (120, "4 meses antes do vencimento"),
                    (180, "6 meses antes do vencimento"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    (0, "Em Execu\xe7\xe3o"),
                    (1, "Solicitada Prorroga\xe7\xe3o"),
                    (2, "Solicitada a Licita\xe7\xe3o"),
                    (3, "Solicitada a Rescis\xe3o"),
                    (4, "Finalizado"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="tipo_contrato",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Contrato"),
                    (2, "SRP"),
                    (3, "NE"),
                    (4, "Loca\xe7\xe3o"),
                    (5, "Servi\xe7os Cont\xednuos"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="tipo_licitacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Dispensa de Licita\xe7\xe3o"),
                    (2, "Inexigibilidade de Licita\xe7\xe3o"),
                    (3, "Preg\xe3o Eletr\xf4nico"),
                    (4, "Preg\xe3o Presencial"),
                    (5, "Ades\xe3o a Ata SRP"),
                    (6, "Concorr\xeancia"),
                    (100, "Registro de Pre\xe7o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="tipo_medicao",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[(1, "Etapa"), (2, "Mensal"), (100, "Contrato")],
            ),
        ),
        migrations.AlterField(
            model_name="medicao",
            name="user",
            field=models.ForeignKey(
                related_name="minhas_medicoes",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="notaempenho",
            name="classificacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Material de Consumo"),
                    (2, "Material Permanente"),
                    (3, "Servi\xe7o"),
                    (4, "Obras e Instala\xe7\xf5es"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="notaempenho",
            name="criado_por",
            field=models.ForeignKey(
                related_name="minhas_nes",
                default=845,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="notaempenho",
            name="fornecedor",
            field=models.ForeignKey(
                related_name="notas_empenhos",
                blank=True,
                to="rh.Pessoa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="valorcontrato",
            name="ordem",
            field=models.IntegerField(default=100),
        ),
        migrations.RunPython(update_contrato, revert_contrato),
    ]
