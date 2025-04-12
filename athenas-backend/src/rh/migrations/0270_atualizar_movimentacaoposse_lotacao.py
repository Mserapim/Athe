# -*- coding: utf-8 -*-
from django.db import migrations
from contrib.utils import getLogger
from rh.models import MovimentacaoTeletrabalho


log = getLogger(__name__)


def up(apps, schema_editor):

    print("Running forward...")

    log.info("Iniciando processo para Vincular lotação atual no plano de tele atual")
    q_mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(ativo=True)

    for teletrabalho in q_mov_teletrabalho:

        log.info(f"Processando as dados do Servidor - {teletrabalho.servidor}")
        lotacao = teletrabalho.servidor.servidor_lotacao.filter(
            ativo=True, designacao=False
        ).first()
        if lotacao:
            teletrabalho.lotacao = lotacao
            teletrabalho.save()


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("rh", "0269_movimentacaoteletrabalho_lotacao")]

    operations = [
        migrations.RunPython(up, down),
    ]
