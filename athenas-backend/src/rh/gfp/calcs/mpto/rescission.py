# -*- coding: utf-8 -*-
from django.db import models

from contrib.utils import getLogger
from rh.gfp.calcs.mpto.remuneracao import BaseSalary
from rh.ponto.models import Falta

log = getLogger(__name__)


class BaseRescission(BaseSalary):

    def _get_query(self):
        query = Falta.objects.filter(models.Q(servidor=self.employee))
