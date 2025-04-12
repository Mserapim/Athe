# -*- coding: utf-8 -*-

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from rh.gfp.models import Evento

log = getLogger(__name__)


# @RunCodeManager.register('gfp-mpto-irrf')
class ConsignableMargin(BaseCalculation):
    title = "Devolve a margem consignada total do servidor!"

    @property
    @cache_return
    def focuses_on(self):
        return [ev.numero for ev in Evento.objects.filter(aplica_consignavel=True)]

    def percentage(self):
        return float(self.payroll.tipo_folha.margem)
