# -*- coding: utf-8 -*-

from django import forms

from contrib import extjs
from contrib.decorator import tab
from contrib.utils import get_json_engine, getLogger
from rh.models import (
    Banco,
    Capacidade,
    Cbo,
    Circunscricao,
    Entrancia,
    GrupoComarca,
    InCapacidade,
    Instancia,
    MesoRegiao,
    Mpas,
    NecessidadeEspecial,
    Pais,
    Patrocinador,
    Penalidade,
    TempoServicoFinalidade,
    TipoOrigem,
    PessoaJuridica,
)
from standard.views import AutoCompleteField

json = get_json_engine()

log = getLogger


class RHCodigoMpas(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Mpas
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Código MPAS",
        "LIST": "Gerenciador de Código MPAS",
        "NEW": "Novo(a) Código MPAS",
        "EDIT": "Editando um(a) Código MPAS",
        "DELETE": "Removendo um(a) Código MPAS",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Código",
                "sortable": "true",
                "dataIndex": "codigo",
                "key": "codigo",
                "width": 150,
            },
        ]
        self.response.write(json.encode(obj))


class RHTempoServicoFinalidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = TempoServicoFinalidade
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Tipos de Tempo Serviço Finalidades",
        "LIST": "Gerenciador de Tempo Serviço Finalidade",
        "NEW": "Novo(a) Tempo Serviço Finalidade",
        "EDIT": "Editando um(a) Tempo Serviço Finalidade",
        "DELETE": "Removendo um(a) Tempo Serviço Finalidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHPatrocinador(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Patrocinador
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Tipos de Patrocinadores",
        "LIST": "Gerenciador de Patrocinador",
        "NEW": "Novo(a) Patrocinador",
        "EDIT": "Editando um(a) Patrocinador",
        "DELETE": "Removendo um(a) Patrocinador",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHPenalidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Penalidade
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Tipos de Penalidade",
        "LIST": "Gerenciador de Tipo de Penalidade",
        "NEW": "Novo(a) Tipo de Penalidade",
        "EDIT": "Editando um(a) Tipo de Penalidade",
        "DELETE": "Removendo um(a) Tipo de Penalidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHInCapacidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = InCapacidade
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Incapacidade",
        "LIST": "Gerenciador de Incapacidade",
        "NEW": "Novo(a) Incapacidade",
        "EDIT": "Editando um(a) Incapacidade",
        "DELETE": "Removendo um(a) Incapacidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHPais(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Pais
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "País",
        "LIST": "Gerenciador de País",
        "NEW": "Novo(a) País",
        "EDIT": "Editando um(a) País",
        "DELETE": "Removendo um(a) País",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Nome Completo",
                "sortable": "true",
                "dataIndex": "nome_completo",
                "key": "nome_completo",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
            {
                "header": "Nacionalidade",
                "sortable": "true",
                "dataIndex": "nacionalidade",
                "key": "nacionalidade",
                "width": 200,
            },
            {
                "header": "DDI",
                "sortable": "true",
                "dataIndex": "ddi",
                "key": "ddi",
                "width": 70,
            },
        ]
        self.response.write(json.encode(obj))


class RHCircunscricao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Circunscricao
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Circunscrição",
        "LIST": "Gerenciador de Circunscrição",
        "NEW": "Novo(a) Circunscrição",
        "EDIT": "Editando um(a) Circunscrição",
        "DELETE": "Removendo um(a) Circunscrição",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHGrupoComarca(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = GrupoComarca
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "GrupoComarca",
        "LIST": "Gerenciador de GrupoComarca",
        "NEW": "Novo(a) GrupoComarca",
        "EDIT": "Editando um(a) GrupoComarca",
        "DELETE": "Removendo um(a) GrupoComarca",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Principal",
            "field": ["pessoajuridica", "nome", "numero", "sigla", "descricao"],
        },
        {
            "title": "Convênio",
            "field": [
                "numero_convenio",
                "tem_convenio",
                "agencia",
                "dv_agencia",
                "conta",
                "dv_conta",
            ],
        },
    ]
)
class RHBanco(extjs.ExtCrud):
    class Form(forms.ModelForm):
        pessoajuridica = AutoCompleteField(
            model=PessoaJuridica, label="Pessoa Jurídica", required=False
        )

        class Meta:
            model = Banco
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Banco",
        "LIST": "Gerenciador de Banco",
        "NEW": "Novo(a) Banco",
        "EDIT": "Editando um(a) Banco",
        "DELETE": "Removendo um(a) Banco",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 70,
            },
            {
                "header": "Sigla",
                "sortable": True,
                "dataIndex": "sigla",
                "key": "sigla",
                "width": 70,
            },
            {
                "header": "Tem Convênio?",
                "sortable": True,
                "dataIndex": "tem_convenio",
                "key": "tem_convenio",
                "width": 120,
            },
            {
                "header": "Número Convênio",
                "sortable": True,
                "dataIndex": "numero_convenio",
                "key": "numero_convenio",
                "width": 130,
            },
            {
                "header": "Agência",
                "sortable": True,
                "dataIndex": "agencia",
                "key": "agencia",
                "width": 70,
            },
            {
                "header": "DV Agência",
                "sortable": True,
                "dataIndex": "dv_agencia",
                "key": "dv_agencia",
                "width": 100,
            },
            {
                "header": "Conta",
                "sortable": True,
                "dataIndex": "conta",
                "key": "conta",
                "width": 100,
            },
            {
                "header": "DV Conta",
                "sortable": True,
                "dataIndex": "dv_conta",
                "key": "dv_conta",
                "width": 100,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHCapacidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Capacidade
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Capacidade",
        "LIST": "Gerenciador de Capacidade",
        "NEW": "Novo(a) Capacidade",
        "EDIT": "Editando um(a) Capacidade",
        "DELETE": "Removendo um(a) Capacidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHMesoRegiao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = MesoRegiao
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Meso Região",
        "LIST": "Gerenciador de Meso Região",
        "NEW": "Novo(a) Meso Região",
        "EDIT": "Editando um(a) Meso Região",
        "DELETE": "Removendo um(a) Meso Região",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHInstancia(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Instancia
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Instância",
        "LIST": "Gerenciador de Instância",
        "NEW": "Novo(a) Instância",
        "EDIT": "Editando um(a) Instância",
        "DELETE": "Removendo um(a) Instância",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHEntrancia(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Entrancia
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Entrância",
        "LIST": "Gerenciador de Entrância",
        "NEW": "Novo(a) Entrância",
        "EDIT": "Editando um(a) Entrância",
        "DELETE": "Removendo um(a) Entrância",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHCbo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        descricao = forms.CharField(
            label="Descrição", max_length=250, widget=forms.Textarea
        )

        class Meta:
            model = Cbo
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "CBO",
        "LIST": "Gerenciador de CBO",
        "NEW": "Novo(a) CBO",
        "EDIT": "Editando um(a) CBO",
        "DELETE": "Removendo um(a) CBO",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Código",
                "sortable": "true",
                "dataIndex": "codigo",
                "key": "codigo",
                "width": 100,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 400,
            },
        ]
        self.response.write(json.encode(obj))


class RHTipoOrigem(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = TipoOrigem
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Tipos de Origens dos Servidores",
        "LIST": "Gerenciador de Tipo de Origem do Servidor",
        "NEW": "Novo(a) Tipo de Origem do Servidor",
        "EDIT": "Editando um(a) Tipo de Origem do Servidor",
        "DELETE": "Removendo um(a) Tipo de Origem do Servidor",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": "true",
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": "true",
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": "true",
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHNecessidadeEspecial(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = NecessidadeEspecial
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Necessidade Especial",
        "LIST": "Gerenciador de Necessidade Especial",
        "NEW": "Novo(a) Necessidade Especial",
        "EDIT": "Editando um(a) Necessidade Especial",
        "DELETE": "Removendo um(a) Necessidade Especial",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }
