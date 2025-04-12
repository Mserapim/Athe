# -*- coding: utf-8 -*-

import datetime

from contrib.controller import ContentType
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.api.person import RHNaturalPersonRestful
from rh.pensao.models import Pensao as Pension

log = getLogger(__name__)


class PENPension(RestfulDRY):

    _model = Pension

    # force_persist_boolean_fields = ['dedutivel_irrf']

    exclude_fields = ["pensao_ptr"]

    full_text_index = (
        "pensionista__nome__icontains",
        "servidor__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
    )

    def model_to_dict(self, instance):
        today = datetime.datetime.today().date()
        values = super(PENPension, self).model_to_dict(instance)
        values["active"] = (
            True
            if (
                instance.data_inicio
                and instance.data_inicio <= today
                and (instance.data_fim is None or instance.data_fim >= today)
            )
            else False
        )
        return values

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.pension.Manager")')


class PENPensioner(RHNaturalPersonRestful):

    def get_query(self):
        query = super(PENPensioner, self).get_query()
        log.info(self.request.GET)
        if "employee" in self.request.GET:
            query = query.filter(
                pensao_pensionista__servidor=self.request.GET.get("employee")
            ).distinct()
        else:
            query = query.filter(pensao_pensionista__isnull=False).distinct()
        return query
