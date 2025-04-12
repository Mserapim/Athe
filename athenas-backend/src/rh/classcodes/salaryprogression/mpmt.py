# -*- coding: utf-8 -*-
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from contrib.utils import getLogger
from contrib.daterange import NewDateRange
from rh.classcodes.salaryprogression.base import SalaryProgressionBase
from rh.gfp.models import ExtensionSalaryProgression
from standard.models import RunCodeManager
from rh.const import CANCELADO
from rh.ponto.models import Falta as Lack
from rh.afastamento.models import AfastamentoSuspensao

from datetime import datetime

log = getLogger(__name__)


@RunCodeManager.register("mpmt-salaryprogression")
class MPMTSalaryProgression(SalaryProgressionBase):
    typeof = "LOADER"
    title = "Código de validações de progressão do MPMT"
    description = ""

    def requirements(self, *args, **kwargs):
        """
        Função para verificar condições para a progressão
        """
        self._requirements = {"wait": [], "unfit": [], "block": []}

        return self._requirements
