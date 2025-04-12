# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.db.models import Q
from django.template.defaultfilters import slugify

from contrib import extjs
from contrib.decorator import login_required
from contrib.utils import get_json_engine
from rh.ferias.models import TIPO_SERVIDOR, PeriodoAquisitivo
from rh.models import Servidor
from standard.views import AutoCompleteField

json = get_json_engine()


class FRSReportHomologacaoServidores(extjs.ExtReportBuild):

    titles = {"TITLE": "Homologação", "SUB_TITLE": "Ato de Homologação"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    #    datasource= 'pgjadmin3'

    report_src = "/to/mpe/rh/ferias/ato_ferias_alfabetico_athenas"

    class Form(forms.Form):
        pa = forms.ModelChoiceField(
            queryset=PeriodoAquisitivo.objects.filter(configuracao__tipo_servidor="S"),
            label="Período Aquisitivo",
        )
        numero_doc = forms.CharField(
            label="ATO n°",
        )
        ordenacao = forms.ChoiceField(
            label="Ordenação",
            choices=(("rp.nome", "Alfabética"), ("fpu.data_inicio", "Cronológica")),
        )

    def get_generated_filename(self):
        title = "undefined"

        try:
            PeriodoAquisitivo.objects.get(pk=int(self.request.GET["pa"]))  # pa
            title = "ato_%s_homologacao_escala_ferias_servidores" % (
                self.request.GET["numero_doc"]
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    @login_required(type="JSON")
    def run_report(self, args=[]):
        pa = PeriodoAquisitivo.objects.get(pk=int(self.request.POST["pa"]))
        self.params.append(
            {"nome": "ato", "valor": self.request.POST["numero_doc"], "tipo": "string"}
        )
        self.params.append(
            {
                "nome": "data",
                "valor": (
                    pa.data_publicacao.strftime("%d/%m/%Y")
                    if pa.data_publicacao
                    else datetime.datetime.now().strftime("%d/%m/%Y")
                ),
                "tipo": "string",
            }
        )
        self.params.append({"nome": "ano", "valor": pa.ano_aquisicao, "tipo": "string"})
        self.params.append({"nome": "ordenacao", "valor": "rp.nome", "tipo": "string"})
        self.params.append(
            {
                "nome": "tipo_relatorio",
                "valor": (
                    "0"
                    if pa.data_homologacao_prev > datetime.datetime.now().date()
                    else "1"
                ),
                "tipo": "string",
            }
        )
        super(FRSReportHomologacaoServidores, self).run_report(args)


class FRSReportHomologacaoMembros(extjs.ExtReportBuild):

    titles = {"TITLE": "Homologação", "SUB_TITLE": "Portaria de Homologação"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    #    datasource= 'pgjadmin3'

    report_src = "/to/mpe/rh/ferias/portaria_ferias_membros"

    class Form(forms.Form):
        pa = forms.ModelChoiceField(
            queryset=PeriodoAquisitivo.objects.filter(configuracao__tipo_servidor="M"),
            label="Período Aquisitivo",
        )
        portaria = forms.CharField(
            label="PORTARIA n°",
        )
        tipo_membro = forms.ChoiceField(
            label="Classe", choices=(("PROM", "Promotores"), ("PROC", "Procuradores"))
        )
        tipo_relatorio = forms.ChoiceField(
            label="Provisório", choices=(("0", "SIM"), ("1", "NÃO"))
        )

    def get_generated_filename(self):
        title = "undefined"

        try:
            PeriodoAquisitivo.objects.get(pk=int(self.request.GET["pa"]))  # pa
            title = "portaria_%s_homologacao_escala_ferias_%s" % (
                self.request.GET["portaria"],
                (
                    "promotores"
                    if self.request.GET["tipo_membro"] == "PROM"
                    else "procuradores"
                ),
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    @login_required(type="JSON")
    def run_report(self, args=[]):
        pa = PeriodoAquisitivo.objects.get(pk=int(self.request.POST["pa"]))
        self.params.append(
            {
                "nome": "data",
                "valor": (
                    pa.data_publicacao.strftime("%d/%m/%Y")
                    if pa.data_publicacao
                    else datetime.datetime.now().strftime("%d/%m/%Y")
                ),
                "tipo": "string",
            }
        )
        self.params.append({"nome": "ano", "valor": pa.ano_aquisicao, "tipo": "string"})
        super(FRSReportHomologacaoMembros, self).run_report(args)


class FRSReportFeriasMes(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Fruições do mês"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/fruicao_ferias"

    class Form(forms.Form):
        ano = forms.IntegerField(
            label="Ano", initial=datetime.datetime.now().date().year
        )
        mes = forms.IntegerField(
            label="Mês", initial=datetime.datetime.now().date().month
        )
        tipo = forms.ChoiceField(label="Tipo", choices=list(TIPO_SERVIDOR.items()))

    def get_generated_filename(self):
        title = "undefined"
        try:
            title = "%s com fruição em %s-%s" % (
                (TIPO_SERVIDOR[self.request.GET["tipo"]]),
                self.request.GET["mes"],
                self.request.GET["ano"],
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"


class FRSReportPASsPendentes(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Períodos Aquisitivos Pendentes"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/ferias_pendentes_MATRICULA"

    class Form(forms.Form):
        id_servidor = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            father=b"FRSReportPASsPendentes",
            # controller = RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        title = "undefined"
        try:
            title = "Ferias-pendentes-%s" % (
                Servidor.objects.get(pk=self.request.GET["id_servidor"]).matricula
                if "id_servidor" in self.request.GET
                else "geral"
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    def autocomplete(self, args=[]):
        obj = {"result": []}

        for row in Servidor.objects.filter(
            Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
            | Q(matricula__icontains=self.request.POST["query"])
        ):
            obj["result"].append({"id": row.pk, "description": "%s" % row})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class FRSReportPASsUsufruidas(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Períodos Aquisitivos Usufruídos"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/ferias_usufruidas_MATRICULA"

    class Form(forms.Form):
        id_servidor = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            father=b"FRSReportPASsUsufruidas",
            # controller = RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        title = "undefined"
        try:
            title = "Ferias-usufruidas-%s" % (
                Servidor.objects.get(pk=self.request.GET["id_servidor"]).matricula
                if "id_servidor" in self.request.GET
                else "geral"
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    def autocomplete(self, args=[]):
        obj = {"result": []}

        for row in Servidor.objects.filter(
            Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
            | Q(matricula__icontains=self.request.POST["query"])
        ):
            obj["result"].append({"id": row.pk, "description": "%s" % row})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class FRSReportHistoricoFerias(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Históricos de Férias"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/historico_ferias"

    class Form(forms.Form):
        matricula = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            father=b"FRSReportHistoricoFerias",
            required=False,
            display_field="description",
            value_field="id",
        )
        tipo = forms.ChoiceField(
            label="Tipo", choices=list(TIPO_SERVIDOR.items()), required=False
        )

    def get_generated_filename(self):
        title = "undefined"
        try:
            title = "Ferias-historico%s" % (
                "-%s" % self.request.GET.get("matricula")
                if "matricula" in self.request.GET
                else "geral%s"
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    def autocomplete(self, args=[]):
        obj = {"result": []}

        for row in Servidor.objects.filter(
            Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
            | Q(matricula__icontains=self.request.POST["query"])
        ):
            obj["result"].append({"id": row.matricula, "description": "%s" % row})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class FRSReportAtividadesFerias(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Atividade de Férias"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/atividades_ferias"

    class Form(forms.Form):
        data_inicial = forms.DateField(label="Data Início", required=True)
        data_final = forms.DateField(label="Data Fim", required=False)
        tipo = forms.ChoiceField(
            label="Tipo", choices=list(TIPO_SERVIDOR.items()), required=False
        )
        matricula = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            father=b"FRSReportAtividadesFerias",
            required=False,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        title = "undefined"
        try:
            title = "Atividade_de_ferias"
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    def autocomplete(self, args=[]):
        obj = {"result": []}

        for row in Servidor.objects.filter(
            Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
            | Q(matricula__icontains=self.request.POST["query"])
        ):
            obj["result"].append({"id": row.matricula, "description": "%s" % row})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def run_report(self, args=[]):
        self.dt_inicial = (
            self.request.POST.get("data_inicial")
            if "data_inicial" in self.request.POST
            else datetime.datetime.now().date().strftime("%Y-%m-%d")
        )
        self.dt_final = (
            self.request.POST.get("data_final")
            if "data_final" in self.request.POST and self.request.POST.get("data_final")
            else datetime.datetime.now().date().strftime("%Y-%m-%d")
        )
        if (
            "matricula" in self.request.POST
            and not self.request.POST.get("matricula") is None
        ):
            self.params.append(
                {
                    "nome": "mat",
                    "valor": self.request.POST.get("matricula"),
                    "tipo": "string",
                }
            )
        if "tipo" in self.request.POST and not self.request.POST.get("tipo") is None:
            self.params.append(
                {
                    "nome": "tipo_ser",
                    "valor": self.request.POST.get("tipo"),
                    "tipo": "string",
                }
            )
        self.params.append(
            {"nome": "dt_inicial", "valor": self.dt_inicial, "tipo": "string"}
        )
        self.params.append(
            {"nome": "dt_final", "valor": self.dt_final, "tipo": "string"}
        )
        self.log.debug(self.params)
        super(FRSReportAtividadesFerias, self).run_report(args)


class FRSReportHomologacaoMembros2(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Homologação de Férias - Membros"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/portaria_ferias_membros"

    @login_required(type="JSON")
    def run_report(self, args=[]):
        self.params.append(
            {
                "nome": "data",
                "valor": datetime.datetime.now().date().strftime("%Y-%m-%d"),
                "tipo": "string",
            }
        )
        self.params.append({"nome": "ano", "valor": "2012", "tipo": "string"})
        self.params.append({"nome": "portaria", "valor": "0001", "tipo": "string"})
        self.params.append({"nome": "periodo", "valor": "1", "tipo": "string"})
        super(FRSReportAtividadesFerias, self).run_report(args)


class FRSReportAcompanhamentoEscalaFerias(extjs.ExtReportBuild):

    titles = {"TITLE": "Férias", "SUB_TITLE": "Acompanhamento de Escala de férias"}

    params = [{"nome": "SUBREPORT_DIR", "valor": "to/mpe/rh/ferias/", "tipo": "string"}]

    report_src = "/to/mpe/rh/ferias/escala_nao_marcada"

    class Form(forms.Form):

        periodo = forms.ModelChoiceField(
            queryset=PeriodoAquisitivo.objects.filter(
                data_publicacao=None, periodo_anterior=False
            ),
            label="Período Aquisitivo",
        )

    def get_generated_filename(self):
        title = "undefined"
        try:
            pa = PeriodoAquisitivo.objects.get(pk=self.request.GET["periodo"])
            title = "acompanhamento_escala_%s_%s" % (
                pa,
                datetime.datetime.now().date().strftime("%d%m%Y"),
            )
        except Exception as e:
            self.log.exception(e)
        return slugify(title) + ".pdf"

    def autocomplete(self, args=[]):
        obj = {"result": []}

        for row in PeriodoAquisitivo.objects.filter(
            Q(ano_aquisicao=self.request.POST["query"])
        ):
            obj["result"].append({"id": row.matricula, "description": row})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
