# -.- coding: utf-8 -.-
from adm.contabilidade.models import (
    NE,
    Categoria,
    FonteRecurso,
    GrupoContabil,
    PPAAcao,
    Produto,
    Unidade,
)
from adm.mto.models import ElementoDespesaSubItem
from contrib import extjs
from contrib.utils import get_json_engine
from django import forms
from standard.views import AutoCompleteField

json = get_json_engine()


class ContabGrupoContabil(extjs.ExtCrud):
    class InstallMeta:
        controller = "ContabGrupoContabil"
        title = "Grupo Contábil"
        node_menu = "contabilidade"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = GrupoContabil

    titles = {
        "PANEL": "Grupos de Contábeis",
        "LIST": "Gerenciador de Grupo Contábil",
        "NEW": "Novo(a) Grupo Contábil",
        "EDIT": "Editando um(a) Grupo Contábil",
        "DELETE": "Removendo um(a) Grupo Contábil",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class ContabUnidade(extjs.ExtCrud):
    class InstallMeta:
        controller = "ContabUnidade"
        title = "Unidade"
        node_menu = "contabilidade"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Unidade

    titles = {
        "PANEL": "Unidades",
        "LIST": "Gerenciador de Unidade",
        "NEW": "Novo(a) Unidade",
        "EDIT": "Editando um(a) Unidade",
        "DELETE": "Removendo um(a) Unidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class ContabCategoria(extjs.ExtCrud):
    class InstallMeta:
        controller = "ContabCategoria"
        title = "Categoria"
        node_menu = "contabilidade"
        install = True

    class Form(forms.ModelForm):
        elemento_despesa_subitem = AutoCompleteField(
            model=ElementoDespesaSubItem,
            father="ContabCategoria",
            label="SubItem de Elemento de Despesa",
        )
        grupo_contabil = AutoCompleteField(
            model=GrupoContabil, father="ContabCategoria", label="Grupo Contábil"
        )

        class Meta:
            exclude = []
            model = Categoria

    titles = {
        "PANEL": "Categorias",
        "LIST": "Gerenciador de Categoria",
        "NEW": "Novo(a) Categoria",
        "EDIT": "Editando um(a) Categoria",
        "DELETE": "Removendo um(a) Categoria",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "toSearch": True,
            },
            {
                "header": "SubItem Elemento Despesa",
                "sortable": True,
                "dataIndex": "elemento_despesa_subitem",
                "toSearch": True,
            },
            {
                "header": "Grupo Contabil",
                "sortable": True,
                "dataIndex": "grupo_contabil",
                "toSearch": True,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class ContabProduto(extjs.ExtCrud):
    class Form(forms.ModelForm):
        unidade = AutoCompleteField(
            model=Unidade, father="ContabProduto", label="Unidade"
        )

        class Meta:
            exclude = []
            model = Produto

    titles = {
        "PANEL": "Produtos",
        "LIST": "Gerenciador de Produto",
        "NEW": "Novo(a) Produto",
        "EDIT": "Editando um(a) Produto",
        "DELETE": "Removendo um(a) Produto",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "toSearch": False,
            },
            {
                "header": "Fração",
                "sortable": True,
                "dataIndex": "fracao",
                "toSearch": False,
            },
            {
                "header": "Quantidade",
                "sortable": True,
                "dataIndex": "quantidade",
                "toSearch": False,
            },
            {
                "header": "Unidade",
                "sortable": True,
                "dataIndex": "unidade",
                "toSearch": False,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class ContabFonteRecurso(extjs.ExtCrud):

    class Form(forms.ModelForm):

        class Meta:
            exclude = []
            model = FonteRecurso

    titles = {
        "PANEL": "Fonte de Recurso",
        "LIST": "Gerenciador de Fontes de Recursos",
        "NEW": "Novo(a) Fonte",
        "EDIT": "Editando um(a) Fonte",
        "DELETE": "Removendo um(a) Fonte",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class ContabPPAAcao(extjs.ExtCrud):

    class Form(forms.ModelForm):

        class Meta:
            exclude = []
            model = PPAAcao

    titles = {
        "PANEL": "Ações do PPA",
        "LIST": "Gerenciador de Ações do PPA",
        "NEW": "Nova",
        "EDIT": "Editar",
        "DELETE": "Remover",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class ContabNotaEmpenho(extjs.ExtCrud):

    class Form(forms.ModelForm):

        class Meta:
            exclude = []
            model = NE

    titles = {
        "PANEL": "Notas de Empenho",
        "LIST": "Gerenciador de Notas de Empenho",
        "NEW": "Nova",
        "EDIT": "Editar",
        "DELETE": "Remover",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }
