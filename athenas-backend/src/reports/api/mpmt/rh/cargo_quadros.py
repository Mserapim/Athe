import ast
import json as js

from django.db.models import F

from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from rh.models import CargoQuadro
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.cargo_quadros import get_data_report, get_analitico_data

log = getLogger(__name__)
json = get_json_engine()


class CargoQuadroRelatorioSintetico(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        nome_relatorio = "Relatório Sintético"
        template = ("portrait/mpmt/rh/cargos_quadros/sintetico.html",)
        formato = self.request.GET.get("formato")
        if self.request.user.servidor.pessoa_fisica.social_name:
            user = self.request.user.servidor.pessoa_fisica.social_name
        else:
            user = self.request.user.username.servidor.pessoa_fisica.nome
        params = {
            "cargos": self.request.GET.getlist("cargos", []),
            "keyword": self.request.GET.get("keyword", ""),
            "filtros": ast.literal_eval(self.request.GET.get("filtros")),
            "user": user,
            "outfile": template,
            "report_name": nome_relatorio,
            "name": nome_relatorio,
            "output_format": "PDF" if formato != "XLS" else "XLS",
        }
        try:
            if formato == "XLS":
                self.generates_xls(template, params)
            else:
                self.generates_pdf(template, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório Sintético: {e}")

    @login_required("JSON")
    def lista_cargos(self, *args):
        collection = CargoQuadro.objects.annotate(
            value=F("cargo__id"), description=F("cargo__nome")
        )

        keyword = self.request.GET.get("keyword")
        filtros = ast.literal_eval(self.request.GET.get("filtros", "[]"))

        if keyword and keyword != "":
            collection = collection.filter(cargo__nome__icontains=keyword)

        if filtros:
            values = ast.literal_eval((filtros))[0].get("value")
            collection = collection.filter(cargo__tipo_lei_cargo__in=values)

        collection = collection.values("value", "description").order_by("description")

        result = {
            "success": True,
            "message": "Dados encontrados com sucesso.",
            "count": collection.count(),
            "collection": list(collection),
        }

        self.response["content-type"] = "text/json"
        self.response.write(js.dumps(result))


class CargoQuadroRelatorioAnalitico(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        result = get_analitico_data(params)
        return result

    @login_required("JSON")
    def generate_report(self, *args):
        nome_relatorio = "Relatório Analítico"
        template = ("portrait/mpmt/rh/cargos_quadros/analitico.html",)
        formato = self.request.GET.get("formato")
        if self.request.user.servidor.pessoa_fisica.social_name:
            user = self.request.user.servidor.pessoa_fisica.social_name
        else:
            user = self.request.user.username.servidor.pessoa_fisica.nome
        params = {
            "cargos": self.request.GET.getlist("cargos", []),
            "keyword": self.request.GET.get("keyword", ""),
            "filtros": ast.literal_eval(self.request.GET.get("filtros")),
            "user": user,
            "outfile": template,
            "report_name": nome_relatorio,
            "name": nome_relatorio,
            "output_format": "PDF" if formato != "XLS" else "XLS",
        }
        try:
            if formato == "XLS":
                self.generates_xls(template, params)
            else:
                self.generates_pdf(template, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório Analítico: {e}")
