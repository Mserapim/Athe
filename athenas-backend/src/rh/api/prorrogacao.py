# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Prorrogacao
from rh.afastamento.models import BaseLicencaAfastamento
from contrib.utils import getLogger, DateUtils

log = getLogger(__name__)


class RHProrrogacaoRestful(RestfulDRY):

    _model = Prorrogacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.prorrogacao.Manage")')

    def validate_departure_period(self, args=[]):
        rst = {"success": True, "message": ""}
        try:
            departure = self.request.POST.get("departure", 0)
            start_date = DateUtils.str_to_date(self.request.POST.get("start_date", 0))
            end_date = DateUtils.str_to_date(self.request.POST.get("end_date", 0))

            if not departure:
                raise Exception("Afastamento não informada.")

            departure = BaseLicencaAfastamento.objects.get(pk=departure)
            departure.instancia_modelo.verifica_sobreposicao_periodo(
                departure.servidor, start_date, end_date, departure.pk
            )

        except Exception as err:
            log.exception(err)
            rst.update({"success": False})
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
