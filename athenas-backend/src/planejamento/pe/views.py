# -.- coding: utf-8 -.-
from django.db.models.query_utils import Q
from rh import models as rh_models
from standard.views import AutoCompleteField
from planejamento.pe import models as pe_models
from contrib import extjs
from contrib.decorator import *
from django import forms
from django.forms.fields import DateField

from contrib.utils import get_json_engine

json = get_json_engine()


@tab(
    [
        {
            "title": "Planejamento",
            "field": [
                "descricao",
                "data_inicio",
                "data_termino",
            ],
        },
        {
            "title": "Metodologia",
            "field": [
                "metodo_analise",
                "limite_alta",
                "limite_baixa",
            ],
        },
        {
            "title": "Objetivos",
            "field": [
                "objetivo",
            ],
        },
    ]
)
class PEPlanejamento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        descricao = forms.CharField(
            label="Descrição", max_length=4000, required=False, widget=forms.Textarea
        )

        class Meta:
            exclude = []
            model = pe_models.Planejamento

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Descrição", "sortable": true, "dataIndex": "descricao", "key": "descricao"},
         {"header": "Início", "sortable": true, "dataIndex": "data_inicio", "key": "data_inicio"},
         {"header": "Término", "sortable": true, "dataIndex": "data_termino", "key": "data_termino"},
         {"header": "Método de Análise", "sortable": true, "dataIndex": "metodo_analise", "key": "metodo_analise"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Planejamento Estratégico",
        "LIST": "Gerenciador de Planejamentos Estratégicos",
        "NEW": "Novo Planejamento Estratégico",
        "EDIT": "Editando um Planejamento Estratégico",
        "DELETE": "Removendo um Planejamento Estratégico",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {"title": "Objetivo", "field": ["nome", "descricao"]},
        {"title": "Projetos", "field": ["projeto"]},
        {"title": "Indicador", "field": ["indicador"]},
    ]
)
class PEObjetivo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        descricao = forms.CharField(
            label="Descrição", max_length=4000, required=False, widget=forms.Textarea
        )

        class Meta:
            exclude = []
            model = pe_models.Objetivo

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Nome", "sortable": true, "dataIndex": "nome", "key": "nome"},
         {"header": "Descrição", "sortable": true, "dataIndex": "descricao", "key": "descricao"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Objetivos",
        "LIST": "Gerenciador de Objetivos",
        "NEW": "Novo Objetivo",
        "EDIT": "Editando um Objetivo",
        "DELETE": "Removendo um Objetivo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Cadastro",
            "field": ["objetivo", "data", "responsavel", "tendencia"],
        },
        {"title": "Análise", "field": ["analise"]},
        {"title": "Recomendações", "field": ["recomendacoes"]},
    ]
)
class PEAnalise(extjs.ExtCrud):
    class Form(forms.ModelForm):
        objetivo = AutoCompleteField(
            model=pe_models.Objetivo,
            # father = "PEAnalise",
            label="Objetivo",
        )
        responsavel = AutoCompleteField(
            model=rh_models.Servidor,
            # father = "PEAnalise",
            label="Responsável",
        )
        analise = forms.CharField(
            label="Análise", max_length=4000, required=False, widget=forms.Textarea
        )
        recomendacoes = forms.CharField(
            label="Recomendações",
            max_length=4000,
            required=False,
            widget=forms.Textarea,
        )

        class Meta:
            exclude = []
            model = pe_models.Analise

    def autocomplete(self, args=[]):
        if args[0] == "Servidor":
            obj = {"result": []}

            for row in rh_models.Servidor.objects.filter(
                Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                | Q(matricula__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEAnalise, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Objetivo", "sortable": true, "dataIndex": "objetivo", "key": "objetivo"},
         {"header": "Análise", "sortable": true, "dataIndex": "analise", "key": "analise"},
         {"header": "Data de Referência", "sortable": true, "dataIndex": "data", "key": "data"},
         {"header": "Tendência", "sortable": true, "dataIndex": "tendencia", "key": "tendencia"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Análises",
        "LIST": "Gerenciador de Análises",
        "NEW": "Nova Análise",
        "EDIT": "Editando uma Análise",
        "DELETE": "Removendo uma Análise",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PEPeriodo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = pe_models.Periodo

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Nome", "sortable": true, "dataIndex": "nome", "key": "nome"},
         {"header": "Dias", "sortable": true, "dataIndex": "dias", "key": "dias"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Períodos",
        "LIST": "Gerenciador de Períodos",
        "NEW": "Novo Período",
        "EDIT": "Editando um Período",
        "DELETE": "Removendo um Período",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Indicador",
            "field": ["nome", "descricao", "tipo", "periodo", "peso"],
        },
        {"title": "Metas", "field": ["indicadormeta"]},
    ]
)
class PEIndicador(extjs.ExtCrud):
    class Form(forms.ModelForm):
        descricao = forms.CharField(
            label="Descrição", max_length=4000, required=False, widget=forms.Textarea
        )

        class Meta:
            exclude = []
            model = pe_models.Indicador

        def save(self, **Kargs):
            self.log = getLogger("PEIndicador")
            try:
                self.log.debug(Kargs)
                forms.ModelForm.save(self, **Kargs)
            except Exception as e:
                self.log.exception(e)
                raise Exception(
                    "Intervalo das datas em Metas está fora do Período especificado."
                )

    def get_columns_grid(self, args):
        #        {"header": "Descrição", "sortable": true, "dataIndex": "descricao", "key": "descricao"},
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Nome", "sortable": true, "dataIndex": "nome", "key": "nome"},
         {"header": "Tipo", "sortable": true, "dataIndex": "tipo", "key": "tipo"},
         {"header": "Período", "sortable": true, "dataIndex": "periodo", "key": "periodo"},
         {"header": "Peso", "sortable": true, "dataIndex": "peso", "key": "peso"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Indicadores",
        "LIST": "Gerenciador de Indicadores",
        "NEW": "Novo Indicador",
        "EDIT": "Editando um Indicador",
        "DELETE": "Removendo um Indicador",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PEIndicadorValor(extjs.ExtCrud):
    class Form(forms.ModelForm):
        indicador = AutoCompleteField(
            model=pe_models.Indicador,
            # father = "PEIndicadorValor",
            label="Indicador",
        )

        class Meta:
            exclude = []
            model = pe_models.IndicadorValor

    def autocomplete(self, args=[]):
        if args[0] == "Indicador":
            obj = {"result": []}

            for row in pe_models.Indicador.objects.filter(
                Q(objetivo__descricao__icontains=self.request.POST["query"])
                | Q(descricao__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEIndicadorValor, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Indicador", "sortable": true, "dataIndex": "indicador", "key": "indicador"},
         {"header": "Data", "sortable": true, "dataIndex": "data", "key": "data"},
         {"header": "Valor", "sortable": true, "dataIndex": "valor", "key": "valor"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Indicadores",
        "LIST": "Gerenciador de Indicadores",
        "NEW": "Novo Indicador",
        "EDIT": "Editando um Indicador",
        "DELETE": "Removendo um Indicador",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PEIndicadorMeta(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = pe_models.IndicadorMeta

    def autocomplete(self, args=[]):
        if args[0] == "Indicador":
            obj = {"result": []}

            for row in pe_models.Indicador.objects.filter(
                Q(objetivo__descricao__icontains=self.request.POST["query"])
                | Q(descricao__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEIndicadorMeta, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Data", "sortable": true, "dataIndex": "data", "key": "data"},
         {"header": "Meta", "sortable": true, "dataIndex": "valor", "key": "valor"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Metas de Indicadores",
        "LIST": "Gerenciador de Metas de Indicadores",
        "NEW": "Nova Meta de Indicador",
        "EDIT": "Editando uma Meta de Indicador",
        "DELETE": "Removendo uma Meta de Indicador",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Cadastro",
            "field": ["indicador", "data", "responsavel", "tendencia"],
        },
        {"title": "Análise", "field": ["analise"]},
        {"title": "Recomendações", "field": ["recomendacoes"]},
    ]
)
class PEAnaliseIndicador(extjs.ExtCrud):
    class Form(forms.ModelForm):
        indicador = AutoCompleteField(
            model=pe_models.Indicador,
            # father = "PEAnaliseIndicador",
            label="Indicador",
        )
        responsavel = AutoCompleteField(
            model=rh_models.Servidor,
            # father = "PEAnalise",
            label="Responsável",
        )
        analise = forms.CharField(
            label="Análise", max_length=4000, required=False, widget=forms.Textarea
        )
        recomendacoes = forms.CharField(
            label="Recomendações",
            max_length=4000,
            required=False,
            widget=forms.Textarea,
        )

        class Meta:
            exclude = []
            model = pe_models.AnaliseIndicador

    def autocomplete(self, args=[]):
        if args[0] == "Servidor":
            obj = {"result": []}

            for row in rh_models.Servidor.objects.filter(
                Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                | Q(matricula__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEAnaliseIndicador, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Indicador", "sortable": true, "dataIndex": "indicador", "key": "indicador"},
         {"header": "Análise", "sortable": true, "dataIndex": "analise", "key": "analise"},
         {"header": "Data de Referência", "sortable": true, "dataIndex": "data", "key": "data"},
         {"header": "Tendência", "sortable": true, "dataIndex": "tendencia", "key": "tendencia"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Análises",
        "LIST": "Gerenciador de Análises de Indicadores",
        "NEW": "Nova Análise de Indicador",
        "EDIT": "Editando uma Análise de Indicador",
        "DELETE": "Removendo uma Análise de Indicador",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PEProjeto(extjs.ExtCrud):
    class Form(forms.ModelForm):
        responsavel = AutoCompleteField(
            model=rh_models.Servidor,
            # father = "PEProjeto",
            label="Responsável",
        )
        descricao = forms.CharField(
            label="Descrição", max_length=4000, required=False, widget=forms.Textarea
        )

        class Meta:
            exclude = []
            model = pe_models.Projeto
            exclude = ["andamento"]

    def autocomplete(self, args=[]):
        if args[0] == "Servidor":
            obj = {"result": []}

            for row in rh_models.Servidor.objects.filter(
                Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                | Q(matricula__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEProjeto, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Nome", "sortable": true, "dataIndex": "nome", "key": "nome"},
         {"header": "Status", "sortable": true, "dataIndex": "status", "key": "status"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Projetos",
        "LIST": "Gerenciador de Projetos",
        "NEW": "Novo Projeto",
        "EDIT": "Editando um Projeto",
        "DELETE": "Removendo um Projeto",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PEAndamentoProjeto(extjs.ExtCrud):
    class Form(forms.ModelForm):
        projeto = AutoCompleteField(
            model=pe_models.Projeto,
            # father = "PEAndamentoProjeto",
            label="Projeto",
        )

        class Meta:
            exclude = []
            model = pe_models.AndamentoProjeto

    def autocomplete(self, args=[]):
        if args[0] == "Projeto":
            obj = {"result": []}

            for row in pe_models.Projeto.objects.filter(
                Q(objetivo__descricao__icontains=self.request.POST["query"])
                | Q(nome__icontains=self.request.POST["query"])
            ):
                obj["result"].append({"id": row.pk, "description": str(row)})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(PEAndamentoProjeto, self).autocomplete(args)

    def get_columns_grid(self, args):
        buf = """
        [{"header": "Chave", "sortable": true, "dataIndex": "id", "key": "id"},
         {"header": "Projeto", "sortable": true, "dataIndex": "projeto", "key": "projteo"},
         {"header": "Data", "sortable": true, "dataIndex": "data", "key": "data"},
         {"header": "Concluído", "sortable": true, "dataIndex": "concluido", "key": "concluido"}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    titles = {
        "PANEL": "Andamentos de Projetos",
        "LIST": "Gerenciador de Andamentos de Projetos",
        "NEW": "Novo Andamento de Projeto",
        "EDIT": "Editando um Andamento de Projeto",
        "DELETE": "Removendo um Andamento de Projeto",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class PERelatorioAnalitico(extjs.ExtReportBuild):

    report_src = "/to/mpe/pe/geral/geral"
    filename = "RelatorioAnalitico.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/pe/geral/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatório Analítico"}

    class Form(forms.Form):
        data_referencia = DateField(label="Referência", required=True)
        obj = forms.ChoiceField(
            label="Objetivo",
            required=True,
            choices=[(0, "TODOS")]
            + [(p.pk, str(p)) for p in pe_models.Objetivo.objects.filter()],
            initial=0,
        )


class PEPrintMapaEstrategico(extjs.ExtReportBuild):

    report_src = "/to/mpe/pe/mapa_estrategico/mapa_estrategico"
    filename = "MapaEstrategico.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/pe/mapa_estrategico/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Mapa Estratégico"}

    class Form(forms.Form):
        data_referencia = DateField(label="Data Referência")
