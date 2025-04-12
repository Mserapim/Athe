# -*- coding: utf-8 -*-

from rh.gfp.calcs.mpto.remuneracao import BaseSalary
from contrib.utils import getLogger
from django.db import models
from rh.ponto.models import Falta

log = getLogger(__name__)


class BaseRescission(BaseSalary):

    def _get_query(self):
        query = Falta.objects.filter(models.Q(servidor=self.employee))
