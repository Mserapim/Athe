# -*- coding: utf-8 -*-

from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.models import (
    FatorFap as FapFactor,
    FatorRat as RatFactor,
    RRAServidorFolhaTipo as RRAEmployeePayrollType,
    CNJRais,
    CNAE,
    RRAEmployee,
    RRA,
)
from rh.gfp.models import NatureEvent
from engine.mq.models import Task
from rh.gfp.tasks import importar_processos_rra


log = getLogger(__name__)


class GFPCNAERestful(RestfulDRY):

    _model = CNAE

    force_upper = False

    full_text_index = ("descricao__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.CNAEManage")')


class GFPFapFactor(RestfulDRY):

    _model = FapFactor

    full_text_index = ("id__iexact",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.FapFactorManage")')


class GFPRatFactor(RestfulDRY):

    _model = RatFactor

    full_text_index = ("id__iexact",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.RatFactorManage")')


class GFPRRAEmployeePayrollType(RestfulDRY):

    _model = RRAEmployeePayrollType

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "id__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.parameters.RRAEmployeePayrollTypeManage")'
        )


class GFPCNJRaisRestful(RestfulDRY):

    _model = CNJRais

    force_upper = False

    full_text_index = ("descricao__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.CNJRaisManage")')


class GFPRRAEmployee(RestfulDRY):

    full_text_index = ("employee__pessoa_fisica__nome__icontains",)

    _model = RRAEmployee

    @login_required("JSON")
    def importar_processo(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            Task.start(
                importar_processos_rra,
                processo_id=self.request.POST.get("processo_id"),
                arquivo_id=self.request.POST.get("arquivo_id"),
                user=self.request.user.id,
            )
            rst.update(
                {
                    "success": True,
                    "message": "Importação de processo de rra em andamento.",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class GFPRRA(RestfulDRY):

    full_text_index = (
        "title__icontains",
        "slug__icontains",
        "id__iexact",
        "process__iexact",
    )

    _model = RRA

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.RRAManage")')


class GFPNatureEvent(RestfulDRY):

    _model = NatureEvent

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "title__icontains",
        "code__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.parameters.NatureEventManage")')
