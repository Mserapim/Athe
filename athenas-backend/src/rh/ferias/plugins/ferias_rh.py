# -*- coding: utf-8 -*-

from contrib.daterange import NewDateRange
from rh.ferias.models import (
    PASU_FRUINDO,
    PASU_HOMOLOGADO,
    PeriodoAquisitivoServidorUsufruto,
)
from rh.models import Servidor


def ferias_no_periodo(self, data_inicial, data_final):
    list_dates = []
    range_date = NewDateRange(data_inicial, data_final)
    for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
        periodo_aquisitivo_servidor__servidor=self,
        estado__in=[PASU_HOMOLOGADO, PASU_FRUINDO],
    ).exclude(data_inicio__gt=data_final):
        list_dates.extend(
            range_date.intersect(
                NewDateRange(pasu.data_inicio, pasu.data_fim)
            ).to_list()
        )

    return len(list_dates) > 0, list_dates


Servidor.ferias_no_periodo = ferias_no_periodo
