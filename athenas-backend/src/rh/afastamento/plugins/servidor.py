# -*- coding: utf-8 -*-

from contrib.daterange import NewDateRange
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import Servidor


def afastamento_no_periodo(self, data_inicial, data_final):
    licensas = []

    for data in NewDateRange(data_inicial, data_final).iter():
        afastamentos = BaseLicencaAfastamento.verifica_interseccao_periodo(
            self, data, data
        )
        afastamentos is not None and licensas.append([data, afastamentos])

    return (len(licensas) > 0, licensas)


"""
Adicioanndo o metodo ao Servidor
"""
Servidor.afastamento_no_periodo = afastamento_no_periodo
