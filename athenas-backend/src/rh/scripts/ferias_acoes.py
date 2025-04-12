# -*- coding: utf-8 -*-
"""
    Este script migra Colaboradores para PossessionCollaborator e PossessionTraine.
    Este script migra Declaração de Atividade para Designação de Exercício.
"""

import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from datetime import date
from contrib.utils import getLogger
from contrib.middleware import set_current_user
from rh.ferias.models import (
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorUsufruto,
    notify,
)
from rh.models import Servidor


log = getLogger(__name__)


set_current_user("nataliabarbosa")


def _suspender(publicacao_id=0, anotar=True):
    responsavel = Servidor.objects.get(matricula=8767611)
    print(responsavel)

    pas = PeriodoAquisitivoServidor.objects.get(pk=17912)
    print(pas)

    pasu = pas.usufrutos.get(pk=32744)
    print(pasu)

    pas._suspender(pasu, True, {"publicacao": publicacao_id}, anotar)


def _alterar(publicacao_id=0, anotar=True):
    responsavel = Servidor.objects.get(matricula=8767611)
    print(responsavel)

    pas = PeriodoAquisitivoServidor.objects.get(pk=17912)
    print(pas)

    pasus = [pk for pk in pas.usufrutos.filter(pk=32744).values_list("pk", flat=True)]
    print(pasus)

    datas = {"data_inicio": date(2023, 2, 23), "data_fim": date(2023, 3, 9)}
    print(datas)

    alteracao = pas.solicitar_alteracao(
        pasus, datas, "", responsavel.id, publicacao_id, anotar
    )
    print(alteracao)
    pas.atualiza_estado()


def _marcar(publicacao_id=0, anotar=True):
    # pas: 18019
    # acao: marcar
    # datas: 01/09/2022,15/09/2022
    # justificativa: Digite a justificativa para a alteração...
    # publicacao:
    # anotacao: on
    # ext-comp-4761: 01/09/2022
    # ext-comp-4762: 15/09/2022

    responsavel = Servidor.objects.get(matricula=8767611)
    print(responsavel)

    pas = PeriodoAquisitivoServidor.objects.get(pk=17912)
    print(pas)

    datas = [{"data_inicio": date(2023, 2, 23), "data_fim": date(2023, 3, 9)}]
    print(datas)

    pasus = []
    pasu = None
    publicacao = None
    count_new_pasus = len(datas)
    dias_marcados = pas.dias_marcados
    print(f"count_new_pasus: {count_new_pasus}")
    print(f"dias_marcados: {dias_marcados}")
    count_pasus_changing = 0
    for parcela in datas:
        pasu = pas.adicionar_usufruto(
            parcela["data_inicio"],
            parcela["data_fim"],
            True,
            count_new_pasus=count_new_pasus,
            dias_marcados=dias_marcados,
            count_pasus_changing=count_pasus_changing,
        )
        dias_marcados += pasu.dias
        count_pasus_changing += 1
        pasus.append(pasu.id)
        notify("FRS_AUTORIZACAO", pas.servidor, pas, pasu=pasu)
    pas.homologado and pas.autorizar_usufruto(
        pasus, responsavel.pk, True, publicacao, True, anotar
    )
    pas.atualiza_estado(True)


def run():
    # _alterar()
    # _suspender()
    _marcar()


if __name__ == "__main__":
    run()


from rh.ferias.models import *
from django.db.models.expressions import F
from contrib.middleware import set_current_user

set_current_user("patriciacabral")

PeriodoAquisitivoServidorUsufruto.objects.filter(pk=35149).update(
    estado=PASU_FRUIDO, suspenso_em=None, suspenso_por=None, interrompido=False
)

pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=35149)
print(pasu, pasu.data_fim_cache, pasu.data_prevista_fim)
pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk=35149)
pasu.dias = NewDateRange(pasu.data_inicio, pasu.data_prevista_fim).days

pasu.save()

BaseLicencaAfastamento.objects.filter(pk=90479).update(
    alteracao=None, data_fim=F("data_prevista")
)
BaseLicencaAfastamento.objects.get(pk=90479).save()
