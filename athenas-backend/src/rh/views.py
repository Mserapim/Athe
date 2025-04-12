# -*- coding: utf-8 -*-

import os
import threading
from datetime import date, datetime

from django import forms

# from contrib.decorator import *
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from localflavor.br.forms import BRCNPJField, BRCPFField, BRZipCodeField

from app.settings import CACHE_PATH
from contrib import extjs
from contrib.decorator import login_required, tab, update_timeout_session
from contrib.utils import DateUtils, employee_from_user, get_json_engine, getLogger
from ged.forms import FileUploadField, ImageUploadField
from rh.afastamento import models as afastamento_models
from rh.const import TIPO_ATO_SICAP
from rh.models import (
    AnotacaoAfastamento,
    AnotacaoAusencia,
    AnotacaoCarreira,
    AnotacaoComunicacao,
    AnotacaoElogio,
    AnotacaoEnquadramento,
    AnotacaoEvento,
    AnotacaoFalta,
    AnotacaoFerias,
    AnotacaoFolgaAniversario,
    AnotacaoFolgaCompensacao,
    AnotacaoFolgaEleitoral,
    AnotacaoGeral,
    AnotacaoGratificacao,
    AnotacaoHorarioEspecial,
    AnotacaoLicenca,
    AnotacaoPenaDisciplinar,
    AnotacaoPlantao,
    AnotacaoRecesso,
    AnotacaoRemocao,
    AnotacaoTempoDobro,
    AnotacaoTempoServico,
    AnotacaoTransposicao,
    AnotacaoViagem,
    AnotHorEspDados,
    Banco,
    Capacidade,
    CargaHoraria,
    Cargo,
    CargoQuadro,
    Carreira,
    Cbo,
    Circunscricao,
    Comarca,
    Curso,
    DadoBancario,
    DadoBancarioPessoa,
    DeclaracaoAtividade,
    Dependencia,
    Dependente,
    DocsDadosEspecificos,
    Documento,
    DocumentoDigital,
    Endereco,
    Especialidade,
    Estado,
    GrupoComarca,
    InativacaoCargoMembro,
    InCapacidade,
    Localidade,
    Lotacao,
    MesoRegiao,
    MicroRegiao,
    Molestia,
    MovimentacaoAposentadoria,
    MovimentacaoAproveitamento,
    MovimentacaoConcessao,
    MovimentacaoDescontoLegal,
    MovimentacaoDesligamento,
    MovimentacaoPessoal,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoRedistribuicao,
    MovimentacaoReintegracao,
    MovimentacaoRemocao,
    MovimentacaoRemocaoMembro,
    MovimentacaoRequisicao,
    MovimentacaoReversao,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    MovimentacaoTitularizacao,
    OrgaoGeral,
    Patrocinador,
    Penalidade,
    PeriodoRequisicao,
    Pessoa,
    PessoaFisica,
    PessoaJuridica,
    ProfissionalSaude,
    Prorrogacao,
    Publicacao,
    PublicConcurrence,
    Quadro,
    Servidor,
    ServidorLocalizacao,
    ServidorLotacao,
    ServidorVinculo,
    SituacaoFuncional,
    Telefone,
    TempoServicoFinalidade,
    UnidadeAdministrativa,
)
from rh.utils import format_situacao_funcional

# from rh.views_parametros import *
from rh.views_parametros import (
    RHBanco,
    RHCapacidade,
    RHCbo,
    RHCircunscricao,
    RHGrupoComarca,
    RHInCapacidade,
    RHMesoRegiao,
    RHPatrocinador,
    RHPenalidade,
    RHTempoServicoFinalidade,
)
from standard.views import AutoCompleteField

json = get_json_engine()

log = getLogger(__name__)


class CustomAutocomplete(extjs.ExtWidget):

    def autocomplete(self, args=[]):

        qs = []
        model = None
        obj = {}

        """"""
        if len(args) > 0:
            if args[0] == "Servidor":
                model = Servidor
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(matricula__icontains=self.request.POST.get("query", ""))
                    )
            elif args[0] == "BaseLicencaAfastamento":
                model = afastamento_models.BaseLicencaAfastamento
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__matricula__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
            elif args[0] == "MovimentacaoPosse":
                model = MovimentacaoPosse
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__matricula__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
            elif args[0] == "Lotacao":
                model = Lotacao
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(nome__icontains=self.request.POST.get("query", "")))
        """"""

        if model is not None and len(qs) > 0:
            q = None
            for qn in qs:
                q = qn if q is None else Q(q | qn)
            if args[0] == "MovimentacaoPosse" and "pk" not in self.request.POST:
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r}
                        for r in model.objects.filter(q).exclude(ativo=False)
                    ]
                )
            elif (
                args[0] == "BaseLicencaAfastamento"
                and isinstance(self, RHMovimentacaoSubstituicao)
                and "pk" not in self.request.POST
            ):
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r} for r in model.objects.filter(q)
                    ]
                )
            elif (
                args[0] == "BaseLicencaAfastamento"
                and isinstance(self, RHMovimentacaoSubstituicaoMembro)
                and "pk" not in self.request.POST
            ):
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r}
                        for r in model.objects.filter(q).exclude(servidor__tipo="S")
                    ]
                )
            else:
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r} for r in model.objects.filter(q)
                    ]
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHEspecialidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Especialidade
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Especialidades dos Cargos",
        "LIST": "Gerenciador de Especialidade do Cargo",
        "NEW": "Novo(a) Especialidade do Cargo",
        "EDIT": "Editando um(a) Especialidade do Cargo",
        "DELETE": "Removendo um(a) Especialidade do Cargo",
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
                "header": "Sigla",
                "sortable": True,
                "dataIndex": "sigla",
                "key": "sigla",
                "width": 60,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHMicroRegiao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        meso_regiao = AutoCompleteField(
            model=MesoRegiao, controller=RHMesoRegiao, label="Meso Região"
        )

        class Meta:
            model = MicroRegiao
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Micro Região",
        "LIST": "Gerenciador de Micro Região",
        "NEW": "Novo(a) Micro Região",
        "EDIT": "Editando um(a) Micro Região",
        "DELETE": "Removendo um(a) Micro Região",
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
                "width": 180,
            },
            {
                "header": "Meso Região",
                "sortable": True,
                "dataIndex": "meso_regiao",
                "key": "meso_regiao",
                "width": 150,
            },
        ]
        self.response.write(json.encode(obj))


class RHComarca(extjs.ExtCrud):
    class Form(forms.ModelForm):
        circunscricao = AutoCompleteField(
            model=Circunscricao, controller=RHCircunscricao, label="Circunscrição"
        )
        grupo_comarca = AutoCompleteField(
            model=GrupoComarca, controller=RHGrupoComarca, label="Grupo Comarca"
        )

        class Meta:
            model = Comarca
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Comarca",
        "LIST": "Gerenciador de Comarca",
        "NEW": "Novo(a) Comarca",
        "EDIT": "Editando um(a) Comarca",
        "DELETE": "Removendo um(a) Comarca",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "key": "id"},
            {"header": "Nome", "sortable": True, "dataIndex": "nome", "key": "nome"},
            {
                "header": "Circunscrição",
                "sortable": True,
                "dataIndex": "circunscricao",
                "key": "circunscricao",
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
            },
            {
                "header": "Grupo Comarca",
                "sortable": True,
                "dataIndex": "grupo_comarca",
                "key": "grupo_comarca",
            },
            {
                "header": "Validação",
                "sortable": True,
                "dataIndex": "validacao",
                "key": "validacao",
            },
        ]
        self.response.write(json.encode(obj))


class RHEstado(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Estado
            exclude = [
                "siafi",
                "tse",
                "ibge",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Estado",
        "LIST": "Gerenciador de Estado",
        "NEW": "Novo(a) Estado",
        "EDIT": "Editando um(a) Estado",
        "DELETE": "Removendo um(a) Estado",
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
                "width": 180,
            },
            {
                "header": "Sigla",
                "sortable": True,
                "dataIndex": "sigla",
                "key": "sigla",
                "width": 70,
            },
            {
                "header": "País",
                "sortable": True,
                "dataIndex": "pais",
                "key": "pais",
                "width": 180,
            },
            {
                "header": "IBGE",
                "sortable": True,
                "dataIndex": "ibge",
                "key": "ibge",
                "width": 70,
            },
            {
                "header": "SIAFI",
                "sortable": True,
                "dataIndex": "siafi",
                "key": "siafi",
                "width": 70,
            },
            {
                "header": "TSE",
                "sortable": True,
                "dataIndex": "tse",
                "key": "tse",
                "width": 70,
            },
        ]
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "nome",
                "estado",
                "sigla",
                "cep",
                "municipio",
                "indicador_municipio",
                "sede_termo",
            ],
        },
    ]
)
class RHLocalidade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        cep = BRZipCodeField(label="CEP")
        microregiao = AutoCompleteField(
            model=MicroRegiao,
            controller=RHMicroRegiao,
            label="Microregião",
            required=False,
        )
        comarca = AutoCompleteField(
            model=Comarca, controller=RHComarca, label="Comarca", required=False
        )

        class Meta:
            model = Localidade
            exclude = [
                "siafi",
                "ibge",
                "comarca",
                "microregiao",
                "descricao",
                "distancia_capital",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Localidade",
        "LIST": "Gerenciador de Localidade",
        "NEW": "Novo(a) Localidade",
        "EDIT": "Editando um(a) Localidade",
        "DELETE": "Removendo um(a) Localidade",
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
                "header": "Sigla",
                "sortable": True,
                "dataIndex": "sigla",
                "key": "sigla",
                "width": 120,
            },
            {
                "header": "Estado",
                "sortable": True,
                "dataIndex": "estado",
                "key": "estado",
                "width": 150,
            },
            {
                "header": "CEP",
                "sortable": True,
                "dataIndex": "cep",
                "key": "cep",
                "width": 90,
            },
            {
                "header": "Indicador Município",
                "sortable": True,
                "dataIndex": "indicador_municipio",
                "key": "indicador_municipio",
                "width": 150,
            },
            {
                "header": "Comarca",
                "sortable": True,
                "dataIndex": "comarca",
                "key": "comarca",
                "width": 240,
            },
            {
                "header": "IBGE",
                "sortable": True,
                "dataIndex": "ibge",
                "key": "ibge",
                "width": 90,
            },
            {
                "header": "Distância Capital",
                "sortable": True,
                "dataIndex": "distancia_capital",
                "key": "distancia_capital",
                "width": 150,
            },
            {
                "header": "Microregião",
                "sortable": True,
                "dataIndex": "microregiao",
                "key": "microregiao",
                "width": 90,
            },
            {
                "header": "Sede Termo",
                "sortable": True,
                "dataIndex": "sede_termo",
                "key": "sede_termo",
                "width": 90,
            },
            {
                "header": "SIAFI",
                "sortable": True,
                "dataIndex": "siafi",
                "key": "siafi",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHEndereco(extjs.ExtCrud):
    class Form(forms.ModelForm):
        cep = BRZipCodeField(label="CEP")
        municipio = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Município"
        )
        complemento = forms.CharField(
            label="Complemento", max_length=2000, required=False, widget=forms.Textarea
        )

        class Meta:
            model = Endereco
            exclude = [
                "data_alteracao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Endereço",
        "LIST": "Gerenciador de Endereço",
        "NEW": "Novo(a) Endereço",
        "EDIT": "Editando um(a) Endereço",
        "DELETE": "Removendo um(a) Endereço",
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
                "header": "Logradouro",
                "sortable": True,
                "dataIndex": "logradouro",
                "key": "logradouro",
                "width": 240,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 60,
            },
            {
                "header": "Complemento",
                "sortable": True,
                "dataIndex": "complemento",
                "key": "complemento",
                "width": 120,
            },
            {
                "header": "Bairro",
                "sortable": True,
                "dataIndex": "bairro",
                "key": "bairro",
                "width": 130,
            },
            {
                "header": "Município",
                "sortable": True,
                "dataIndex": "municipio",
                "key": "municipio",
                "width": 240,
            },
            {
                "header": "CEP",
                "sortable": True,
                "dataIndex": "cep",
                "key": "cep",
                "width": 70,
            },
            {
                "header": "Tipo Endereço",
                "sortable": True,
                "dataIndex": "tipo_endereco",
                "key": "tipo_endereco",
                "width": 120,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHTelefone(extjs.ExtCrud):
    class Form(forms.ModelForm):
        numero = forms.CharField(label="Número")

        class Meta:
            model = Telefone
            exclude = [
                "data_alteracao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Telefone",
        "LIST": "Gerenciador de Telefone",
        "NEW": "Novo(a) Telefone",
        "EDIT": "Editando um(a) Telefone",
        "DELETE": "Removendo um(a) Telefone",
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
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 90,
            },
            {
                "header": "Tipo Telefone",
                "sortable": True,
                "dataIndex": "tipo_telefone",
                "key": "tipo_telefone",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHDadoBancario(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = DadoBancario
            exclude = [
                "data_uso",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Dados Bancários",
        "LIST": "Gerenciador de Dados Bancários",
        "NEW": "Novo(a) Dado Bancário",
        "EDIT": "Editando um(a) Dado Bancário",
        "DELETE": "Removendo um(a) Dado Bancário",
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
                "header": "Banco",
                "sortable": True,
                "dataIndex": "banco",
                "key": "banco",
                "width": 240,
            },
            {
                "header": "Tipo Conta",
                "sortable": True,
                "dataIndex": "tipo_conta",
                "key": "tipo_conta",
                "width": 180,
            },
            {
                "header": "Agência com DV",
                "sortable": True,
                "dataIndex": "agencia",
                "key": "agencia",
                "width": 180,
            },
            {
                "header": "Conta Corrente com DV",
                "sortable": True,
                "dataIndex": "conta_corrente_completa",
                "key": "conta_corrente_completa",
                "width": 200,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab([{"title": "Principal", "field": ["nome", "endereco"]}])
class RHPessoa(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Pessoa
            exclude = [
                "data_alteracao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Pessoas",
        "LIST": "Pessoa",
        "NEW": "Novo(a) Pessoa",
        "EDIT": "Editando um(a) Pessoa",
        "DELETE": "Removendo um(a) Pessoa",
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
                "width": 350,
            },
            {
                "header": "Endereço",
                "sortable": True,
                "dataIndex": "endereco",
                "key": "endereco",
                "width": 350,
            },
            {
                "header": "Dado Bancário",
                "sortable": True,
                "dataIndex": "dado_bancario",
                "key": "dado_bancario",
                "width": 200,
            },
            {
                "header": "Telefone",
                "sortable": True,
                "dataIndex": "telefone",
                "key": "telefone",
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHDadoBancarioPessoa(extjs.ExtCrud):
    class Form(forms.ModelForm):
        pessoa = AutoCompleteField(model=Pessoa, controller=RHPessoa, label="Pessoa")
        banco = AutoCompleteField(model=Banco, controller=RHBanco, label="Banco")

        class Meta:
            model = DadoBancarioPessoa
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Dados Bancários",
        "LIST": "Gerenciador de Dados Bancários da Pessoa",
        "NEW": "Novo(a) Dado Bancário da Pessoa",
        "EDIT": "Editando um(a) Dado Bancário da Pessoa",
        "DELETE": "Removendo um(a) Dado Bancário da Pessoa",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHPessoaJuridica(extjs.ExtCrud):
    class Form(forms.ModelForm):
        cnpj = BRCNPJField(label="CNPJ")

        class Meta:
            model = PessoaJuridica
            exclude = [
                "endereco",
                "telefone",
                "data_alteracao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Pessoa Jurídica",
        "LIST": "Gerenciador de Pessoa Jurídica",
        "NEW": "Novo(a) Pessoa Jurídica",
        "EDIT": "Editando um(a) Pessoa Jurídica",
        "DELETE": "Removendo um(a) Pessoa Jurídica",
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
                "header": "Razão Social",
                "sortable": True,
                "dataIndex": "razao_social",
                "key": "razao_social",
                "width": 240,
            },
            {
                "header": "CNPJ",
                "sortable": True,
                "dataIndex": "cnpj",
                "key": "cnpj",
                "width": 120,
            },
            {
                "header": "Telefone",
                "sortable": True,
                "dataIndex": "telefone",
                "key": "telefone",
                "width": 90,
            },
            {
                "header": "Endereço",
                "sortable": True,
                "dataIndex": "endereco",
                "key": "endereco",
                "width": 240,
            },
            {
                "header": "Dado Bancário",
                "sortable": True,
                "dataIndex": "dado_bancario",
                "key": "dado_bancario",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHCarreira(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Carreira
            exclude = ["data_alteracao"]
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Carreira",
        "LIST": "Gerenciador de Carreira",
        "NEW": "Novo(a) Carreira",
        "EDIT": "Editando um(a) Carreira",
        "DELETE": "Removendo um(a) Carreira",
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
                "width": 230,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 230,
            },
            {
                "header": "Código",
                "sortable": True,
                "dataIndex": "codigo",
                "key": "codigo",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHCurso(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = Curso
            exclude = ["created_at", "modified_at", "created_by", "modified_by"]

    titles = {
        "PANEL": "Curso",
        "LIST": "Gerenciador de Curso",
        "NEW": "Novo(a) Curso",
        "EDIT": "Editando um(a) Curso",
        "DELETE": "Removendo um(a) Curso",
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
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
            {
                "header": "Grau Instrução",
                "sortable": True,
                "dataIndex": "grau_instrucao",
                "key": "grau_instrucao",
                "width": 150,
            },
            {
                "header": "Nível",
                "sortable": True,
                "dataIndex": "nivel",
                "key": "nivel",
                "width": 150,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHDocsDadosEspecificos(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = DocsDadosEspecificos
            exclude = ["created_at", "modified_at", "created_by", "modified_by"]

    titles = {
        "PANEL": "Dados Específicos de Documentos",
        "LIST": "Gerenciador de Dados Específicos de Documentos",
        "NEW": "Novo Dado Específico de Documento",
        "EDIT": "Editando um Dado Específico de Documento",
        "DELETE": "Removendo um Dado Específico de Documento",
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
                "header": "Especificidade",
                "sortable": True,
                "dataIndex": "especificidade",
                "key": "especificidade",
                "width": 320,
            },
            {
                "header": "Valor",
                "sortable": True,
                "dataIndex": "valor",
                "key": "valor",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


class RHDocumento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        arquivo = FileUploadField(label="Arquivo", required=False)

        class Meta:
            model = Documento
            exclude = ["created_at", "modified_at", "created_by", "modified_by"]

    titles = {
        "PANEL": "Documento",
        "LIST": "Gerenciador de Documento",
        "NEW": "Novo(a) Documento",
        "EDIT": "Editando um(a) Documento",
        "DELETE": "Removendo um(a) Documento",
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
                "header": "Tipo de Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 240,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 240,
            },
            {
                "header": "Data da Expedição",
                "sortable": True,
                "dataIndex": "data_expedicao",
                "key": "data_expedicao",
                "width": 140,
            },
            {
                "header": "Estado de Expedição",
                "sortable": True,
                "dataIndex": "estado_expedicao",
                "key": "estado_expedicao",
                "width": 150,
            },
            {
                "header": "Data de Validade",
                "sortable": True,
                "dataIndex": "data_validade",
                "key": "data_validade",
                "width": 140,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Pessoa",
            "field": [
                "nome",
                "data_nascimento",
                "cpf",
                "rg",
                "rg_orgao",
                "rg_uf",
                "rg_data_expedicao",
                "sexo",
                "municipio_naturalidade",
                "estado_civil",
                "nome_conjuge",
            ],
        },
        {
            "title": "Dados",
            "field": [
                "nome_pai",
                "nome_mae",
                "raca_cor",
                "doador",
                "sangue",
                "fator_rh",
                "email_institucional",
                "data_obito",
            ],
        },
        {"title": "Endereço e Telefone", "field": ["endereco", "telefone"]},
        {"title": "Documentos", "field": ["documento"]},
        {"title": "Dados Bancários", "field": ["dado_bancario"]},
        {
            "title": "Outros",
            "field": [
                "foto",
                "grau_instrucao",
                "necessidade_especial",
                "necessidades_especiais",
            ],
        },
    ]
)
class RHPessoaFisica(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        cpf = BRCPFField(label="CPF", required=False)
        municipio_naturalidade = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Naturalidade"
        )
        foto = ImageUploadField(label="Foto", required=False)

        class Meta:
            model = PessoaFisica
            exclude = [
                "data_cadastro",
                "pessoa_ptr",
                "pessoa_ptr_id",
                "data_alteracao",
                "municipio_naturalidade_id",
                "foto_id",
                "rg_uf_id",
                "social_program",
                "serious_diseases",
                "created_at",
                "modified_at",
                "created_by",
                "created_by_id",
                "modified_by",
                "modified_by_id",
            ]

    titles = {
        "PANEL": "Pessoa Física",
        "LIST": "Gerenciador de Pessoa Física",
        "NEW": "Novo(a) Pessoa Física",
        "EDIT": "Editando um(a) Pessoa Física",
        "DELETE": "Removendo um(a) Pessoa Física",
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
                "header": "Data Nascimento",
                "sortable": True,
                "dataIndex": "data_nascimento",
                "key": "data_nascimento",
                "width": 120,
            },
            {
                "header": "RG",
                "sortable": True,
                "dataIndex": "rg",
                "key": "rg",
                "width": 100,
            },
            {
                "header": "RG Órgão",
                "sortable": True,
                "dataIndex": "rg_orgao",
                "key": "rg_orgao",
                "width": 90,
            },
            {
                "header": "RG UF",
                "sortable": True,
                "dataIndex": "rg_uf",
                "key": "rg_uf",
                "width": 90,
            },
            {
                "header": "RG Data Expedição",
                "sortable": True,
                "dataIndex": "rg_data_expedicao",
                "key": "rg_data_expedicao",
                "width": 130,
            },
            {
                "header": "CPF",
                "sortable": True,
                "dataIndex": "cpf",
                "key": "cpf",
                "width": 120,
            },
            {
                "header": "Sexo",
                "sortable": True,
                "dataIndex": "sexo",
                "key": "sexo",
                "width": 100,
            },
            {
                "header": "Email Institucional",
                "sortable": True,
                "dataIndex": "email_institucional",
                "key": "email_institucional",
                "width": 150,
            },
            {
                "header": "Telefone",
                "sortable": True,
                "dataIndex": "telefone",
                "key": "telefone",
                "width": 90,
            },
            {
                "header": "Nome Pai",
                "sortable": True,
                "dataIndex": "nome_pai",
                "key": "nome_pai",
                "width": 240,
            },
            {
                "header": "Nome Mãe",
                "sortable": True,
                "dataIndex": "nome_mae",
                "key": "nome_mae",
                "width": 240,
            },
            {
                "header": "Estado Civil",
                "sortable": True,
                "dataIndex": "estado_civil",
                "key": "estado_civil",
                "width": 100,
            },
            {
                "header": "Nome Cônjuge",
                "sortable": True,
                "dataIndex": "nome_conjuge",
                "key": "nome_conjuge",
                "width": 240,
            },
            {
                "header": "Endereço",
                "sortable": True,
                "dataIndex": "endereco",
                "key": "endereco",
                "width": 240,
            },
            {
                "header": "Município Naturalidade",
                "sortable": True,
                "dataIndex": "municipio_naturalidade",
                "key": "municipio_naturalidade",
                "width": 240,
            },
            {
                "header": "Data Cadastro",
                "sortable": True,
                "dataIndex": "data_cadastro",
                "key": "data_cadastro",
                "width": 100,
            },
            {
                "header": "Dado Bancário",
                "sortable": True,
                "dataIndex": "dado_bancario",
                "key": "dado_bancario",
                "width": 200,
            },
            {
                "header": "Sangue",
                "sortable": True,
                "dataIndex": "sangue",
                "key": "sangue",
                "width": 90,
            },
            {
                "header": "Fator RH",
                "sortable": True,
                "dataIndex": "fator_rh",
                "key": "fator_rh",
                "width": 90,
            },
            {
                "header": "Doador",
                "sortable": True,
                "dataIndex": "doador",
                "key": "doador",
                "width": 70,
            },
            {
                "header": "Raça Cor",
                "sortable": True,
                "dataIndex": "raca_cor",
                "key": "raca_cor",
                "width": 90,
            },
            {
                "header": "Data Óbito",
                "sortable": True,
                "dataIndex": "data_obito",
                "key": "data_obito",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Pessoa Física",
            "field": [
                "nome",
                "cpf",
                "email_institucional",
                "rg",
                "rg_orgao",
                "rg_uf",
                "rg_data_expedicao",
                "sexo",
                "estado_civil",
                "nome_conjuge",
            ],
        },
    ]
)
class RHPessoaFisicaSimplificado(CustomAutocomplete, extjs.ExtCrud):
    """
    cpf = models.CharField(max_length = 14, null = True, blank = True, verbose_name='CPF')
    rg = models.CharField(max_length = 20, null = True, blank = True, verbose_name='RG')
    """

    class Form(forms.ModelForm):
        cpf = BRCPFField(label="CPF", required=True)

        class Meta:
            model = PessoaFisica
            exclude = [
                "data_cadastro",
                "pessoa_ptr",
                "data_alteracao",
                "data_nascimento",
                "nome_pai",
                "nome_mae",
                "raca_cor",
                "doador",
                "sangue",
                "fator_rh",
                "data_obito",
                "endereco",
                "telefone",
                "documento",
                "dado_bancario",
                "foto",
                "grau_instrucao",
                "necessidade_especial",
                "necessidades_especiais",
                "municipio_naturalidade",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
                "social_program",
                "serious_diseases",
            ]

    titles = {
        "PANEL": "Pessoa Física",
        "LIST": "Gerenciador de Pessoa Física",
        "NEW": "Novo(a) Pessoa Física",
        "EDIT": "Editando um(a) Pessoa Física",
        "DELETE": "Removendo um(a) Pessoa Física",
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
                "header": "Data Nascimento",
                "sortable": True,
                "dataIndex": "data_nascimento",
                "key": "data_nascimento",
                "width": 120,
            },
            {
                "header": "CPF",
                "sortable": True,
                "dataIndex": "cpf",
                "key": "cpf",
                "width": 120,
            },
            {
                "header": "Email Institucional",
                "sortable": True,
                "dataIndex": "email_institucional",
                "key": "email_institucional",
                "width": 150,
            },
            {
                "header": "RG",
                "sortable": True,
                "dataIndex": "rg",
                "key": "rg",
                "width": 100,
            },
            {
                "header": "RG Órgão",
                "sortable": True,
                "dataIndex": "rg_orgao",
                "key": "rg_orgao",
                "width": 90,
            },
            {
                "header": "RG UF",
                "sortable": True,
                "dataIndex": "rg_uf",
                "key": "rg_uf",
                "width": 90,
            },
            {
                "header": "RG Data Expedição",
                "sortable": True,
                "dataIndex": "rg_data_expedicao",
                "key": "rg_data_expedicao",
                "width": 130,
            },
            {
                "header": "Sexo",
                "sortable": True,
                "dataIndex": "sexo",
                "key": "sexo",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Pessoa Física",
            "field": [
                "nome",
                "cpf",
                "email_institucional",
                "rg",
                "rg_orgao",
                "rg_uf",
                "rg_data_expedicao",
                "sexo",
                "estado_civil",
                "nome_conjuge",
            ],
        },
    ]
)
class RHPessoaFisicaSimplificadoSemDocumento(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        cpf = BRCPFField(label="CPF", required=False)

        class Meta:
            model = PessoaFisica
            exclude = [
                "data_cadastro",
                "pessoa_ptr",
                "pessoa_ptr_id",
                "data_alteracao",
                "data_nascimento",
                "nome_pai",
                "nome_mae",
                "raca_cor",
                "doador",
                "sangue",
                "fator_rh",
                "data_obito",
                "endereco",
                "telefone",
                "documento",
                "dado_bancario",
                "foto",
                "foto_id",
                "grau_instrucao",
                "necessidade_especial",
                "necessidades_especiais",
                "municipio_naturalidade",
                "municipio_naturalidade_id",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
                "created_by_id",
                "modified_by_id",
                "rg_uf_id",
                "social_program",
                "serious_diseases",
            ]

    titles = {
        "PANEL": "Pessoa Física",
        "LIST": "Gerenciador de Pessoa Física",
        "NEW": "Novo(a) Pessoa Física",
        "EDIT": "Editando um(a) Pessoa Física",
        "DELETE": "Removendo um(a) Pessoa Física",
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
                "header": "Data Nascimento",
                "sortable": True,
                "dataIndex": "data_nascimento",
                "key": "data_nascimento",
                "width": 120,
            },
            {
                "header": "CPF",
                "sortable": True,
                "dataIndex": "cpf",
                "key": "cpf",
                "width": 120,
            },
            {
                "header": "Email Institucional",
                "sortable": True,
                "dataIndex": "email_institucional",
                "key": "email_institucional",
                "width": 150,
            },
            {
                "header": "RG",
                "sortable": True,
                "dataIndex": "rg",
                "key": "rg",
                "width": 100,
            },
            {
                "header": "RG Órgão",
                "sortable": True,
                "dataIndex": "rg_orgao",
                "key": "rg_orgao",
                "width": 90,
            },
            {
                "header": "RG UF",
                "sortable": True,
                "dataIndex": "rg_uf",
                "key": "rg_uf",
                "width": 90,
            },
            {
                "header": "RG Data Expedição",
                "sortable": True,
                "dataIndex": "rg_data_expedicao",
                "key": "rg_data_expedicao",
                "width": 130,
            },
            {
                "header": "Sexo",
                "sortable": True,
                "dataIndex": "sexo",
                "key": "sexo",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Informações",
            "field": [
                "nome",
                "abreviacao",
                "esfera_governamental",
                "poder",
                "codigo_igeprev",
                "sigla",
                "publica_doc",
                "habilita_protocolo",
                "descricao",
            ],
        },
        {"title": "Endereço e telefone", "field": ["endereco", "telefone"]},
    ]
)
class RHOrgaoGeral(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = OrgaoGeral
            exclude = [
                "ativo",
                "data_alteracao",
                "order_nome",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Órgão Geral",
        "LIST": "Gerenciador de Órgão Geral",
        "NEW": "Novo(a) Órgão Geral",
        "EDIT": "Editando um(a) Órgão Geral",
        "DELETE": "Removendo um(a) Órgão Geral",
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
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
            {
                "header": "Esfera Governamental",
                "sortable": True,
                "dataIndex": "esfera_governamental",
                "key": "esfera_governamental",
                "width": 180,
            },
            {
                "header": "Poder",
                "sortable": True,
                "dataIndex": "poder",
                "key": "poder",
                "width": 180,
            },
            {
                "header": "Sigla",
                "sortable": True,
                "dataIndex": "sigla",
                "key": "sigla",
                "width": 70,
            },
            {
                "header": "Habilita Protocolo",
                "sortable": True,
                "dataIndex": "habilita_protocolo",
                "key": "habilita_protocolo",
                "width": 70,
            },
        ]
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def query(self, args=[]):
        super(RHOrgaoGeral, self).query(args=args)


class RHOrgaoGeralBuscaEspecial(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = OrgaoGeral
            exclude = [
                "ativo",
                "data_alteracao",
                "order_nome",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Órgão Geral Busca Especial",
        "LIST": "Gerenciador de Órgão Geral Busca Especial",
        "NEW": "Novo(a) Órgão Geral Busca Especial",
        "EDIT": "Editando um(a) Órgão Geral Busca Especial",
        "DELETE": "Removendo um(a) Órgão Geral Busca Especial",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_query(self, args=[]):
        """ """
        return OrgaoGeral.objects.filter(~Q(lotacao=None)).filter(ativo=True)


class RHOrgaoGeralPublicacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = OrgaoGeral
            exclude = [
                "ativo",
                "data_alteracao",
                "order_nome",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Órgão Geral Publicação",
        "LIST": "Gerenciador de Órgão Geral Publicação",
        "NEW": "Novo(a) Órgão Geral Publicação",
        "EDIT": "Editando um(a) Órgão Geral Publicação",
        "DELETE": "Removendo um(a) Órgão Geral Publicação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_query(self, args=[]):
        """ """
        return OrgaoGeral.objects.exclude(Q(publica_doc=False))


@tab(
    [
        {
            "title": "Informações",
            "field": [
                "nome",
                "abreviacao",
                "esfera_governamental",
                "poder",
                "responsavel",
                "pessoa_juridica",
                "codigo_igeprev",
                "habilita_protocolo",
                "sigla",
            ],
        },
        {"title": "Telefone e Endereço", "field": ["telefone", "endereco"]},
    ]
)
class RHUnidadeAdministrativa(extjs.ExtCrud):
    class Form(forms.ModelForm):
        responsavel = AutoCompleteField(
            model=PessoaFisica,
            controller=RHPessoaFisica,
            label="Responsável",
            required=False,
        )
        pessoa_juridica = AutoCompleteField(
            model=PessoaJuridica, controller=RHPessoaJuridica, label="Pessoa Jurídica"
        )

        class Meta:
            model = UnidadeAdministrativa
            exclude = [
                "ativo",
                "data_alteracao",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Unidade Administrativa",
        "LIST": "Gerenciador de Unidade Administrativa",
        "NEW": "Novo(a) Unidade Administrativa",
        "EDIT": "Editando um(a) Unidade Administrativa",
        "DELETE": "Removendo um(a) Unidade Administrativa",
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
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
            {
                "header": "Esfera Governamental",
                "sortable": True,
                "dataIndex": "esfera_governamental",
                "key": "esfera_governamental",
                "width": 180,
            },
            {
                "header": "Poder",
                "sortable": True,
                "dataIndex": "poder",
                "key": "poder",
                "width": 240,
            },
            {
                "header": "Título Maior Autoridade",
                "sortable": True,
                "dataIndex": "titulo_maior_autoridade",
                "key": "titulo_maior_autoridade",
                "width": 180,
            },
            {
                "header": "Título Nome Maior Autoridade",
                "sortable": True,
                "dataIndex": "titulo_nome_maior_autoridade",
                "key": "titulo_nome_maior_autoridade",
                "width": 220,
            },
            {
                "header": "Pessoa Jurídica",
                "sortable": True,
                "dataIndex": "pessoa_juridica",
                "key": "pessoa_juridica",
                "width": 240,
            },
            {
                "header": "Responsável",
                "sortable": True,
                "dataIndex": "responsavel",
                "key": "responsavel",
                "width": 240,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 90,
            },
            {
                "header": "Email",
                "sortable": True,
                "dataIndex": "email",
                "key": "email",
                "width": 240,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "key": "ativo",
                "width": 70,
            },
            {
                "header": "Habilita Protocolo",
                "sortable": True,
                "dataIndex": "habilita_protocolo",
                "key": "habilita_protocolo",
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Pessoa", "field": ["pessoa_fisica"]},
        {
            "title": "Servidor",
            "field": [
                "matricula",
                "matricula_origem",
                "chefe_imediato",
                "capacidade",
                "incapacidade",
                "numero_cartao_ponto",
                "classificacao",
                "data_referencia_ferias",
                "molestia",
            ],
        },
    ]
)
class RHServidor(extjs.ExtCrud):
    class Form(forms.ModelForm):
        pessoa_fisica = AutoCompleteField(
            model=PessoaFisica, controller=RHPessoaFisica, label="Pessoa Física"
        )
        capacidade = AutoCompleteField(
            model=Capacidade,
            controller=RHCapacidade,
            label="Capacidade",
            required=False,
        )
        incapacidade = AutoCompleteField(
            model=InCapacidade,
            controller=RHInCapacidade,
            label="Incapacidade",
            required=False,
        )
        chefe_imediato = AutoCompleteField(
            model=Servidor, controller="RHServidor", label="Chefe Imediato"
        )

        class Meta:
            model = Servidor
            exclude = [
                "user",
                "data_registro",
                "vpi",
                "tipo",
                "ativo",
                "notificacoes",
                "data_alteracao",
                "curso",
                "lotacoes",
                "situacao_funcional_cache",
                "categoria_cache",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
                "bond",
                "graduation",
                "improvement_and_graduate",
                "published_works",
            ]

    titles = {
        "PANEL": "Servidor",
        "LIST": "Gerenciador de Servidor",
        "NEW": "Novo(a) Servidor",
        "EDIT": "Editando um(a) Servidor",
        "DELETE": "Removendo um(a) Servidor",
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
                "header": "Pessoa Física",
                "sortable": True,
                "dataIndex": "pessoa_fisica",
                "key": "pessoa_fisica",
                "width": 240,
            },
            {
                "header": "Matrícula",
                "sortable": True,
                "dataIndex": "matricula",
                "key": "matricula",
                "width": 90,
            },
            {
                "header": "Núm. Cartão de Ponto",
                "sortable": True,
                "dataIndex": "numero_cartao_ponto",
                "key": "numero_cartao_ponto",
                "width": 130,
            },
            {
                "header": "Curso",
                "sortable": True,
                "dataIndex": "curso",
                "key": "curso",
                "width": 180,
            },
            {
                "header": "Grau de Instrução",
                "sortable": True,
                "dataIndex": "grau_instrucao",
                "key": "grau_instrucao",
                "width": 110,
            },
            {
                "header": "Classificação",
                "sortable": True,
                "dataIndex": "classificacao",
                "key": "classificacao",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def work_locations(self, args=[]):
        rst = {"count": 0, "collection": []}

        try:
            servidor = employee_from_user(self.request.user)
            if not servidor:
                raise Exception("Servidor não foi encontrado.")
        except Servidor.DoesNotExist:
            rst.update(
                success=False, message="O usuário não tem nenhum servidor ativo."
            )
        except Exception as e:
            rst.update(success=False, message="{}".format(e.args[0]))
        else:
            work_locations = servidor.work_locations

            rst.update(
                success=True,
                count=len(work_locations),
                collection=[
                    {"pk": wl.pk, "description": "%s" % wl} for wl in work_locations
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(rst))

    @update_timeout_session(enable=False)
    def get_notificacoes(self, args=[]):
        result = {
            "result": [],
            "totalRows": 0,
        }

        try:
            servidor = self.request.user.servidor
        except Exception:
            pass
        else:
            query = servidor.notificacoes.filter(
                Q(status=2) & Q(type__in=("SYS", "ONTOP"))
            ).order_by("-created_at")
            for notif in query[:10]:
                result["result"].append(
                    {
                        "pk": notif.pk,
                        "type_msg": notif.msg.type,
                        "header_msg": "%s" % notif.msg.header,
                        "msg": "%s" % notif.formatMsg(),
                        "media_type": notif.type,
                    }
                )
            result["totalRows"] = query.count()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))

    #    def get_query(self):
    #        return Servidor.objects.filter(pk=179)

    @login_required(type="JSON")
    def query_rh(self, args=[]):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        from django.db.models import Model

        result = {
            "result": [],
            "totalRows": self.get_total_rows(),
        }

        query = self.get_query_filtred()

        collection = [
            {"pk": "TODOS", "description": "TODOS"},
            {"pk": "ATIVOS", "description": "ATIVOS"},
            {"pk": "INATIVOS", "description": "INATIVOS"},
            {"pk": "MEMBROS", "description": "MEMBROS"},
            {"pk": "PROCURADORES", "description": "PROCURADORES"},
            {
                "pk": "AME-DIREITO",
                "description": "ANALISTA MINISTERIAIS ESPECIALIDADE CIÊNCIAS JURIDICAS",
            },
            {
                "pk": "AMI-DIREITO",
                "description": "ANALISTA MINISTERIAL - CIÊNCIAS JURIDICAS",
            },
            {"pk": "COMISSIONADO", "description": "TODOS OS COMISSIONADOS"},
        ]

        for row in query:
            info = {}
            info["__description__"] = "%s" % row

            for field in list(self.get_fields().keys()):
                if field != "id" and field[len(field) - 3 :] == "_id":
                    field = field[0 : len(field) - 3]

                funcname = "get_{0}_display".format(field)
                func = getattr(row, funcname, None)
                value = getattr(row, field)

                if func is not None:
                    info[field] = func()
                elif isinstance(value, datetime):
                    info[field] = DateUtils.datetime_to_str(value)
                elif isinstance(value, date):
                    info[field] = DateUtils.date_to_str(value)
                elif isinstance(value, bool):
                    info[field] = value and "Sim" or "Não"
                elif value is None:
                    info[field] = ""
                elif isinstance(value, Model):
                    info[field] = "%s" % value
                    info["%s__pk" % field] = value.pk
                else:
                    info[field] = "%s" % value

            info["pk"] = row.pk
            info["description"] = "%s" % row
            info["controller"] = self.get_instance_controller(row)

            collection.append(info)

        result.update(result=collection)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(result))

    @login_required(type="JSON")
    def query_membro(self, args=[]):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        from django.db.models import Model

        result = {
            "result": [],
            "totalRows": self.get_total_rows(),
        }

        query = self.get_query_filtred().filter(tipo="M", ativo=True)

        matricula = self.request.POST.get("matricula", None)
        if (
            matricula
            and "pk" not in self.request.POST
            and (
                self.request.POST.get("keyword", None) is None
                or self.request.POST.get("keyword", None) == ""
            )
        ):
            servidor = Servidor.objects.get(matricula=matricula)
            q = None
            for substituto in servidor.my_substitute_employee():
                q = (
                    Q(matricula=substituto.matricula)
                    if q is None
                    else Q(q | Q(matricula=substituto.matricula))
                )
            if q:
                query = query.filter(q)

        for row in query:
            info = {}

            info["__description__"] = row

            for field in list(self.get_fields().keys()):
                if field != "id" and field[len(field) - 3 :] == "_id":
                    field = field[0 : len(field) - 3]

                funcname = "get_{0}_display".format(field)
                func = getattr(row, funcname, None)
                value = getattr(row, field)

                if func is not None:
                    info[field] = func()
                elif isinstance(value, datetime):
                    info[field] = DateUtils.datetime_to_str(value)
                elif isinstance(value, date):
                    info[field] = DateUtils.date_to_str(value)
                elif isinstance(value, bool):
                    info[field] = value and "Sim" or "Não"
                elif value is None:
                    info[field] = ""
                elif isinstance(value, Model):
                    info[field] = value
                    info["%s__pk" % field] = value.pk
                else:
                    info[field] = value

            info["pk"] = row.pk
            info["description"] = row
            info["controller"] = self.get_instance_controller(row)

            result["result"].append(info)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(result))

    def notifications(self, args=None):
        args = args or []

        result = {
            "message": "Nothing done yet",
            "success": False,
        }

        try:
            READ, UNREAD = 8, 2
            employee = employee_from_user(self.request.user)

            query = employee.notificacoes.filter(
                type__in=["SYS", "ONTOP"], status__in=[READ, UNREAD]
            ).order_by("status", "-created_at")

            totalUnread = query.filter(status=UNREAD).count()

            start = int(self.request.REQUEST.get("start", 0))
            end = start + int(self.request.REQUEST.get("limit", 30))
            count = query.count()
            query = query[start:end]

            result.update(
                {
                    "collection": [
                        {
                            "id": notification.pk,
                            "origin": (
                                str(notification.sender)
                                if notification.sender
                                else "Sistema"
                            ),
                            "destination": str(notification.target),
                            "subject": notification.msg.header,
                            "status": notification.status,
                            "media_type": notification.type,
                            "message_type": notification.msg.type,
                            "created_at": DateUtils.datetime_to_str(
                                notification.created_at
                            ),
                            "message": notification.formatMsg(),
                        }
                        for notification in query
                    ],
                    "count": count,
                    "totalUnread": totalUnread,
                }
            )
        except Exception as e:
            log.exception(e)
            result.update(
                {
                    "message": str(e),
                    "collection": [],
                    "count": 0,
                    "totalUnread": 0,
                }
            )
        else:
            result.update(
                {
                    "message": "Operação realizada com sucesso",
                    "success": True,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))


class RHServidorUser(extjs.ExtEditorCrud):

    titles = {
        "PANEL": "Servidor e Usuário",
        "LIST": "Relação Usuário e Servidor",
        "EDIT": "Editar informações do Servidor",
    }

    class Form(forms.ModelForm):
        class Meta:
            model = Servidor
            exclude = [
                "capacidade",
                "classificacao",
                "curso",
                "vpi",
                "incapacidade",
                "grau_instrucao",
                "matricula_origem",
                "numero_cartao_ponto",
                "pessoa_fisica",
                "data_referencia_ferias",
                "tipo",
                "ativo",
                "molestia",
                "lotacoes",
                "situacao_funcional_cache",
                "categoria_cache",
                "chefe_imediato",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
                "bond",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "key": "id"},
            {"header": "Usuário", "sortable": True, "dataIndex": "user", "key": "user"},
            {
                "header": "Pessoa Física",
                "width": 255,
                "sortable": True,
                "dataIndex": "pessoa_fisica",
                "key": "pessoa_fisica",
            },
            {
                "header": "Matrícula",
                "width": 65,
                "sortable": True,
                "dataIndex": "matricula",
                "key": "matricula",
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHServidorVinculo(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        servidor_vinculado = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor vinculado"
        )

        class Meta:
            model = ServidorVinculo
            exclude = [
                "data_alteracao",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Vínculo de Servidor",
        "LIST": "Gerenciador de Vínculo de Servidor",
        "NEW": "Novo(a) Vínculo de Servidor",
        "EDIT": "Editando um(a) Vínculo de Servidor",
        "DELETE": "Removendo um(a) Vínculo de Servidor",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados Básicos",
            "field": [
                "servidor",
                "pessoa_fisica",
                "grau_parentesco",
                "tipo",
                "capacidade",
                "mpas",
                "codigo_plansaude",
                "pensao_alimenticia",
                "pensao_alimenticia_pct",
                "auxilio_creche",
            ],
        },
        {
            "title": "Informações e Datas",
            "field": [
                "motivo_inicio_dependencia",
                "data_inicio",
                "motivo_fim_dependencia",
                "data_fim",
                "dep_ir",
                "dep_sf",
                "previdencia",
                "valido_plansaude",
            ],
        },
        {
            "title": "Outros Dados",
            "field": ["formalizado", "dependente_direto", "historico"],
        },
    ]
)
class RHDependente(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        pessoa_fisica = AutoCompleteField(
            model=PessoaFisica, controller=RHPessoaFisica, label="Dependente"
        )
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )

        class Meta:
            model = Dependente
            exclude = [
                "data_cadastro",
                "data_alteracao",
                "created_at",
                "modified_at",
                "created_by",
                "modified_by",
            ]

    titles = {
        "PANEL": "Dependente",
        "LIST": "Gerenciador de Dependente",
        "NEW": "Novo(a) Dependente",
        "EDIT": "Editando um(a) Dependente",
        "DELETE": "Removendo um(a) Dependente",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "pessoa_fisica",
                "toSearch": False,
                "width": 150,
            },
            {
                "header": "Recebe Aux. Creche",
                "sortable": True,
                "dataIndex": "auxilio_creche",
                "toSearch": False,
            },
            {
                "header": "Capacidade",
                "sortable": True,
                "dataIndex": "capacidade",
                "toSearch": False,
            },
            {
                "header": "PLANSAÚDE",
                "sortable": True,
                "dataIndex": "codigo_plansaude",
                "toSearch": True,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "toSearch": True,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "toSearch": True,
            },
            {
                "header": "Imposto de Renda",
                "sortable": True,
                "dataIndex": "dep_ir",
                "toSearch": False,
            },
            {
                "header": "Salário Família",
                "sortable": True,
                "dataIndex": "dep_sf",
                "toSearch": False,
            },
            {
                "header": "Dependente Direto",
                "sortable": True,
                "dataIndex": "dependente_direto",
                "toSearch": True,
            },
            {
                "header": "Formalizado",
                "sortable": True,
                "dataIndex": "formalizado",
                "toSearch": False,
            },
            {
                "header": "Parentesco",
                "sortable": True,
                "dataIndex": "grau_parentesco",
                "toSearch": True,
            },
            {
                "header": "Motivo Fim Dependência",
                "sortable": True,
                "dataIndex": "motivo_fim_dependencia",
                "toSearch": False,
            },
            {
                "header": "Motivo Início Dependência",
                "sortable": True,
                "dataIndex": "motivo_inicio_dependencia",
                "toSearch": False,
            },
            {
                "header": "MPAS",
                "sortable": True,
                "dataIndex": "mpas",
                "toSearch": False,
            },
            {
                "header": "Pensão Alimentícia",
                "sortable": True,
                "dataIndex": "pensao_alimenticia",
                "toSearch": False,
            },
            {
                "header": "Pensão Alimentícia (%)",
                "sortable": True,
                "dataIndex": "pensao_alimenticia_pct",
                "toSearch": False,
            },
            {
                "header": "Previdência",
                "sortable": True,
                "dataIndex": "previdencia",
                "toSearch": False,
            },
            {
                "header": "Tipo",
                "sortable": True,
                "dataIndex": "tipo",
                "toSearch": False,
            },
            {
                "header": "Válido PLANSAÚDE",
                "sortable": True,
                "dataIndex": "valido_plansaude",
                "toSearch": False,
            },
            {
                "header": "Vigência",
                "sortable": True,
                "dataIndex": "vigencia",
                "toSearch": False,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def get_list(self, args=[]):
        # self.log.info(self.request.POST)
        obj = {"collection": [], "count": 0}
        try:
            dependente = Dependente.objects.get(pk=self.request.POST["pk"])
            obj.update(
                {
                    "collection": {
                        "pk": dependente.pk,
                        "pessoa_fisica": dependente.pessoa_fisica.pk,
                        "servidor": dependente.servidor.pk,
                        "parentesco": (
                            dependente.grau_parentesco
                            if dependente.grau_parentesco
                            else None
                        ),
                        "tipo": dependente.tipo if dependente.tipo else None,
                        "capacidade": (
                            dependente.capacidade if dependente.capacidade else None
                        ),
                        "motivo_inicio_dependencia": (
                            dependente.motivo_inicio_dependencia
                            if dependente.motivo_inicio_dependencia
                            else None
                        ),
                        "motivo_fim_dependencia": (
                            dependente.motivo_fim_dependencia
                            if dependente.motivo_fim_dependencia
                            else None
                        ),
                        "data_inicio": (
                            DateUtils.date_to_str(dependente.data_inicio)
                            if dependente.data_inicio
                            else None
                        ),
                        "data_fim": (
                            DateUtils.date_to_str(dependente.data_fim)
                            if dependente.data_fim
                            else None
                        ),
                        "imposto_renda": dependente.dep_ir,
                        "salario_familia": dependente.dep_sf,
                        "dependente_direto": dependente.dependente_direto,
                        "auxilio_creche": dependente.auxilio_creche,
                    },
                    "success": True,
                }
            )
        except Exception as e:
            self.log.info(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        try:
            # self.log.info(self.request.POST)
            servidor = Servidor.objects.get(pk=self.request.POST["servidor"])
            pessoa_fisica = PessoaFisica.objects.get(
                pk=self.request.POST["pessoa_fisica"]
            )
            self.request.POST.getlist("motivo_fim_dependencia")
            dependente = Dependente(
                pessoa_fisica=pessoa_fisica,
                servidor=servidor,
                motivo_inicio_dependencia=(
                    self.request.POST["motivo_inicio_dependencia"]
                    if "motivo_inicio_dependencia" in self.request.POST
                    and self.request.POST["motivo_inicio_dependencia"]
                    else None
                ),
                motivo_fim_dependencia=(
                    self.request.POST["motivo_fim_dependencia"]
                    if "motivo_fim_dependencia" in self.request.POST
                    and self.request.POST["motivo_fim_dependencia"]
                    else None
                ),
                grau_parentesco=(
                    self.request.POST["parentesco"]
                    if "parentesco" in self.request.POST
                    else None
                ),
                data_inicio=(
                    DateUtils.str_to_date(self.request.POST["data_inicio"])
                    if "data_inicio" in self.request.POST
                    and self.request.POST["data_inicio"]
                    else None
                ),
                data_fim=(
                    DateUtils.str_to_date(self.request.POST["data_fim"])
                    if "data_fim" in self.request.POST and self.request.POST["data_fim"]
                    else None
                ),
                dep_ir=True if "imposto_renda" in self.request.POST else False,
                dep_sf=True if "salario_familia" in self.request.POST else False,
                dependente_direto=(
                    True if "dependente_direto" in self.request.POST else False
                ),
                auxilio_creche=True if "auxilio_creche" in self.request.POST else False,
                tipo=self.request.POST["tipo"] if "tipo" in self.request.POST else None,
                capacidade=(
                    self.request.POST["capacidade"]
                    if "capacidade" in self.request.POST
                    else None
                ),
            )
            dependente.save()

            obj.update(success=True)
            obj.update(message="Dependente salvo com sucesso!")
        except Exception as e:
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            obj.update(success=False)
            self.log.info(e)
        else:
            self.log.info("Dependente Salvo com sucesso")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)
        try:
            dependente = Dependente.objects.get(pk=self.request.POST["pk"])
            pessoa_fisica = PessoaFisica.objects.get(
                pk=self.request.POST["pessoa_fisica"]
            )
            dependente.pessoa_fisica = pessoa_fisica

            dependente.motivo_inicio_dependencia = (
                self.request.POST["motivo_inicio_dependencia"]
                if "motivo_inicio_dependencia" in self.request.POST
                and self.request.POST["motivo_inicio_dependencia"]
                else None
            )
            dependente.motivo_fim_dependencia = (
                self.request.POST["motivo_fim_dependencia"]
                if "motivo_fim_dependencia" in self.request.POST
                and self.request.POST["motivo_fim_dependencia"]
                else None
            )
            dependente.grau_parentesco = (
                self.request.POST["parentesco"]
                if "parentesco" in self.request.POST
                else None
            )
            dependente.data_inicio = (
                DateUtils.str_to_date(self.request.POST["data_inicio"])
                if "data_inicio" in self.request.POST
                and self.request.POST["data_inicio"]
                else None
            )
            dependente.data_fim = (
                DateUtils.str_to_date(self.request.POST["data_fim"])
                if "data_fim" in self.request.POST and self.request.POST["data_fim"]
                else None
            )
            dependente.dep_ir = True if "imposto_renda" in self.request.POST else False
            dependente.dep_sf = (
                True if "salario_familia" in self.request.POST else False
            )
            dependente.dependente_direto = (
                True if "dependente_direto" in self.request.POST else False
            )
            dependente.auxilio_creche = (
                True if "auxilio_creche" in self.request.POST else False
            )
            dependente.tipo = (
                self.request.POST["tipo"] if "tipo" in self.request.POST else None
            )
            dependente.capacidade = (
                self.request.POST["capacidade"]
                if "capacidade" in self.request.POST
                else None
            )

            dependente.save()
            obj.update(success=True)
        except Exception as e:
            obj.update(success=False)
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}
        # self.log.info(self.request.POST)
        try:
            dependentes = Dependente.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for dep in dependentes:
                dep.delete()
        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHDependencia(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        dependente = AutoCompleteField(
            model=Dependente, controller=RHDependente, label="Dependencia"
        )

        class Meta:
            model = Dependencia
            exclude = ["created_at", "modified_at", "created_by", "modified_by"]

    titles = {
        "PANEL": "Dependência",
        "LIST": "Dependências",
        "NEW": "Nova Dependência",
        "EDIT": "Editando uma Dependência",
        "DELETE": "Removendo um(a) Dependência",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Dependente",
                "sortable": True,
                "dataIndex": "dependente",
                "toSearch": True,
                "width": 350,
            },
            {
                "header": "Tipo",
                "sortable": True,
                "dataIndex": "tipo",
                "toSearch": True,
                "width": 120,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "toSearch": True,
                "width": 70,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Idade limite",
                "sortable": True,
                "dataIndex": "idade_limite",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Estudante",
                "sortable": True,
                "dataIndex": "estudante",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Suspenso",
                "sortable": True,
                "dataIndex": "suspenso",
                "toSearch": True,
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def get_list(self, args=[]):
        obj = {"collection": [], "count": 0}
        # self.log.info(self.request.POST)
        try:
            dependencia = Dependencia.objects.get(
                pk=self.request.POST["pk"],
                dependente__pk=self.request.POST["pk_dependente"],
            )

            obj.update(
                {
                    "collection": {
                        # 'pk': dependencia.pk,
                        "dependente": dependencia.pk,
                        "tipo": dependencia.tipo if dependencia.tipo else None,
                        "data_inicio": (
                            DateUtils.date_to_str(dependencia.data_inicio)
                            if dependencia.data_inicio
                            else None
                        ),
                        "data_fim": (
                            DateUtils.date_to_str(dependencia.data_fim)
                            if dependencia.data_fim
                            else None
                        ),
                        "idade_limite": dependencia.idade_limite,
                        "estudante": dependencia.estudante,
                        "suspenso": dependencia.suspenso,
                    },
                    "success": True,
                }
            )
        except Exception as e:
            self.log.info(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):
        obj = {
            "collection": [],
            "count": 0,
            "success": False,
            "message": "Nada aconteceu ainda",
        }
        self.log.info(self.request.POST)
        try:
            dependente = Dependente.objects.get(pk=self.request.POST["dependencia"])
            dependencia = Dependencia(
                dependente=dependente,
                tipo=self.request.POST["tipo"] if "tipo" in self.request.POST else None,
                data_inicio=(
                    DateUtils.str_to_date(self.request.POST["data_inicio"])
                    if "data_inicio" in self.request.POST
                    else None
                ),
                data_fim=(
                    DateUtils.str_to_date(self.request.POST["data_fim"])
                    if "data_fim" in self.request.POST and self.request.POST["data_fim"]
                    else None
                ),
                idade_limite=(
                    int(self.request.POST["idade_limite"])
                    if "idade_limite" in self.request.POST
                    and self.request.POST["idade_limite"]
                    else None
                ),
                estudante=True if "estudante" in self.request.POST else False,
                suspenso=True if "suspenso" in self.request.POST else False,
            )
            dependencia.save()
        except Dependente.DoesNotExist as e:
            self.log.info(e)
            obj.update(message="Dependente não econtrado!")
        except Exception as e:
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            self.log.info(e)
        else:
            self.log.info("Dependencia Salva com sucesso")
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            dependencia = Dependencia.objects.get(pk=self.request.POST["pk"])
            dependencia.data_inicio = (
                DateUtils.str_to_date(self.request.POST["data_inicio"])
                if self.request.POST["data_inicio"]
                else None
            )
            dependencia.data_fim = (
                DateUtils.str_to_date(self.request.POST["data_fim"])
                if self.request.POST["data_fim"]
                else None
            )
            dependencia.tipo = self.request.POST["tipo"]
            dependencia.idade_limite = (
                int(self.request.POST["idade_limite"])
                if self.request.POST["idade_limite"]
                else None
            )
            dependencia.estudante = True if "estudante" in self.request.POST else False
            dependencia.suspenso = True if "suspenso" in self.request.POST else False
            dependencia.save()

        except Dependencia.DoesNotExist as e:
            self.log.info(e)
            obj.update(message="Dependência não econtrada!")
        except Exception as e:
            obj.update(success=False)
            obj.update(message="Ocorreu um erro ao alterar os dados!")
            self.log.info(e)
        else:
            obj.update(success=True)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}
        # self.log.info(self.request.POST)
        try:
            dependencias = Dependencia.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for dep in dependencias:
                dep.delete()
        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "nome",
                "localidade",
                "responsible_substituted",
                "organograma",
                "designacao",
                "pai",
                "codigo",
                "sigla",
                "publica_doc",
                "abreviacao",
                "responsavel",
                "codigo_igeprev",
                "habilita_protocolo",
            ],
        },
        {
            "title": "Informações",
            "field": ["sala", "andar", "executivo", "administrativo", "grupo_lotacao"],
        },
        {"title": "Telefone e Endereço", "field": ["telefone", "endereco"]},
    ]
)
class RHLotacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        responsavel = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Responsável", required=False
        )
        localidade = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Localidade"
        )
        pai = AutoCompleteField(model=Lotacao, label="Lotação superior", required=False)

        class Meta:
            model = Lotacao
            exclude = [
                "orgaogeral_ptr",
                "titulo_nome_maior_autoridade",
                "titulo_maior_autoridade",
                "esfera_governamental",
                "ativo",
                "poder",
                "acesso_protocolo_geral",
                "data_alteracao",
                "instancia",
                "entrancia",
                "ouvidoria",
                "comarca",
                "grupo",
                "order_nome",
                "descricao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Lotação",
        "LIST": "Gerenciador de Lotação",
        "NEW": "Novo(a) Lotação",
        "EDIT": "Editando um(a) Lotação",
        "DELETE": "Removendo um(a) Lotação",
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
                "header": "Código",
                "sortable": True,
                "dataIndex": "codigo",
                "key": "codigo",
                "width": 70,
            },
            {
                "header": "Abreviação",
                "sortable": True,
                "dataIndex": "abreviacao",
                "key": "abreviacao",
                "width": 140,
            },
            {
                "header": "Superior",
                "sortable": True,
                "dataIndex": "pai",
                "key": "pai",
                "width": 140,
            },
            {
                "header": "Responsável",
                "sortable": True,
                "dataIndex": "responsavel",
                "key": "responsavel",
                "width": 240,
            },
            {
                "header": "Organograma",
                "sortable": True,
                "dataIndex": "organograma",
                "key": "organograma",
                "width": 50,
            },
            {
                "header": "Designação",
                "sortable": True,
                "dataIndex": "designacao",
                "key": "designacao",
                "width": 50,
            },
            {
                "header": "Andar",
                "sortable": True,
                "dataIndex": "andar",
                "key": "andar",
                "width": 70,
            },
            {
                "header": "Sala",
                "sortable": True,
                "dataIndex": "sala",
                "key": "sala",
                "width": 70,
            },
            {
                "header": "Habilita Protocolo",
                "sortable": True,
                "dataIndex": "habilita_protocolo",
                "key": "habilita_protocolo",
                "width": 70,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response["content-type"] = "text/javascript"
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def get_query_filtred(self, paginator=True):
        query = super(RHLotacao, self).get_query_filtred(paginator=paginator)
        return query.filter()


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "nome",
                "codigo",
                "carreira",
                "lotacao_responsavel",
                "cbo",
                "unidade_administrativa",
                "tipo_lei_cargo",
                "indicativo",
                "poder",
            ],
        },
        {
            "title": "Informações",
            "field": [
                "professor",
                "acumulavel",
                "ativo",
                "designa_exercicio",
                "chefia",
                "substituivel",
            ],
        },
    ]
)
class RHCargo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        lotacao_responsavel = AutoCompleteField(
            model=Lotacao,
            controller=RHLotacao,
            label="Lotação responsável",
            required=False,
        )
        unidade_administrativa = AutoCompleteField(
            model=UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Órgão",
            required=True,
        )
        carreira = AutoCompleteField(
            model=Carreira, controller=RHCarreira, label="Carreira", required=False
        )
        cbo = AutoCompleteField(model=Cbo, controller=RHCbo, label="CBO")

        class Meta:
            model = Cargo
            exclude = ["numero_designacao", "data_alteracao", "cargo_arquimedes"]

    titles = {
        "PANEL": "Cargo",
        "LIST": "Gerenciador de Cargo",
        "NEW": "Novo(a) Cargo",
        "EDIT": "Editando um(a) Cargo",
        "DELETE": "Removendo um(a) Cargo",
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
                "width": 350,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 200,
            },
            {
                "header": "Código",
                "sortable": True,
                "dataIndex": "codigo",
                "key": "codigo",
                "width": 100,
            },
            {
                "header": "Carreira",
                "sortable": True,
                "dataIndex": "carreira",
                "key": "carreira",
                "width": 240,
            },
            {
                "header": "CBO",
                "sortable": True,
                "dataIndex": "cbo",
                "key": "cbo",
                "width": 240,
            },
            {
                "header": "Entrância",
                "sortable": True,
                "dataIndex": "entrancia",
                "key": "entrancia",
                "width": 240,
            },
            {
                "header": "Instância",
                "sortable": True,
                "dataIndex": "instancia",
                "key": "instancia",
                "width": 240,
            },
            {
                "header": "Acumulável",
                "sortable": True,
                "dataIndex": "acumulavel",
                "key": "acumulavel",
                "width": 90,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "key": "ativo",
                "width": 70,
            },
            {
                "header": "Designa Exercício",
                "sortable": True,
                "dataIndex": "designa_exercicio",
                "key": "designa_exercicio",
                "width": 120,
            },
            {
                "header": "Professor",
                "sortable": True,
                "dataIndex": "professor",
                "key": "professor",
                "width": 70,
            },
            {
                "header": "Tipo Lei Cargo",
                "sortable": True,
                "dataIndex": "tipo_lei_cargo",
                "key": "tipo_lei_cargo",
                "width": 100,
            },
            {
                "header": "Poder",
                "sortable": True,
                "dataIndex": "poder",
                "key": "poder",
                "width": 100,
            },
            {
                "header": "Unidade Administrativa",
                "sortable": True,
                "dataIndex": "unidade_administrativa",
                "key": "unidade_administrativa",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHPublicacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        arquivo = FileUploadField(label="Arquivo", required=False)
        observacao = forms.CharField(
            label="Assunto(site)",
            max_length=2000,
            required=False,
            widget=forms.Textarea,
        )
        origem = AutoCompleteField(
            model=OrgaoGeral, controller=RHOrgaoGeral, label="Origem", required=False
        )

        class Meta:
            model = Publicacao
            exclude = [
                "ano",
                "cache_unicode",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "publication_state",
                "indirect",
                "document",
                "document_read_only",
                "sent_to_publication_by",
                "sent_to_publication_at",
                "confirm_publication_by",
                "confirm_publication_at",
                "vehicle_page",
            ]

    titles = {
        "PANEL": "Publicação",
        "LIST": "Gerenciador de Publicações",
        "NEW": "Novo(a) Publicação",
        "EDIT": "Editando um(a) Publicação",
        "DELETE": "Removendo um(a) Publicação",
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
                "header": "Cache",
                "sortable": True,
                "dataIndex": "cache_unicode",
                "key": "cache_unicode",
                "width": 350,
            },
            {
                "header": "Tipo de Publicação",
                "hidden": True,
                "sortable": True,
                "dataIndex": "tipo",
                "key": "tipo",
                "width": 130,
            },
            {
                "header": "Interessado",
                "sortable": True,
                "dataIndex": "interessado_nome",
                "key": "interessado_nome",
                "width": 130,
            },
            {
                "header": "Número",
                "hidden": True,
                "sortable": True,
                "dataIndex": "numero",
                "key": "numero",
                "width": 80,
            },
            {
                "header": "Ano",
                "hidden": True,
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Expedição",
                "sortable": True,
                "dataIndex": "data_expedicao",
                "key": "data_expedicao",
                "width": 80,
            },
            {
                "header": "Vigência",
                "sortable": True,
                "dataIndex": "data_vigencia",
                "key": "data_vigencia",
                "width": 80,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "data_publicacao",
                "key": "data_publicacao",
                "width": 80,
            },
            {
                "header": "Lei Autorizativa",
                "sortable": True,
                "dataIndex": "lei_autorizativa",
                "key": "lei_autorizativa",
                "width": 100,
            },
            {
                "header": "Veículo Publicação",
                "hidden": True,
                "sortable": True,
                "dataIndex": "veiculo_publicacao",
                "key": "veiculo_publicacao",
                "width": 240,
            },
            {
                "header": "Número Publicação",
                "hidden": True,
                "sortable": True,
                "dataIndex": "numero_publicacao",
                "key": "numero_publicacao",
                "width": 130,
            },
            {
                "header": "Interno",
                "sortable": True,
                "dataIndex": "interno",
                "key": "interno",
                "width": 50,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def list_pub_portal(self, args=[]):
        obj, tipo_documento, num_doc = {"result": []}, "Ato", 1

        if args:
            if args[0] == "portarias":
                tipo_documento = "Portaria"
                num_doc = 3
            elif args[0] == "despachos":
                tipo_documento = "Despachos"
                num_doc = 5

            list = Publicacao.objects.filter(
                Q(interno=True) & Q(arquivo__isnull=False) & Q(tipo=num_doc)
            ).order_by("-ano", "numero")
            if args[1] is not None:
                list = list.filter(Q(ano=args[1]))

            for row in list:
                obj["result"].append(
                    {
                        "numero": row.numero,
                        "ano": row.ano,
                        "observacao": row.observacao,
                        "arquivo": row.arquivo.permalink(),
                    }
                )
                obj["tipo"] = tipo_documento

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": ["servidor", "resumo", "tipo_documento", "publicacao", "texto"],
        }
    ]
)
class RHAnotacaoGeral(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor", required=True
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoGeral
            exclude = [
                "numero_processo",
                "data_documento",
                "anotacaogeral_ptr",
                "numero_documento",
                "indireto",
                "data_portaria_inicio",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Geral",
        "LIST": "Gerenciador de Anotação Geral",
        "NEW": "Novo(a) Anotação Geral",
        "EDIT": "Editando um(a) Anotação Geral",
        "DELETE": "Removendo um(a) Anotação Geral",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 120,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 350,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 180,
            },
            {
                "header": "Data do Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 140,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 320,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def get_query(self):
        return AnotacaoGeral.objects.filter(
            anotacaoausencia=None,
            anotacaocomunicacao=None,
            anotacaoelogio=None,
            anotacaoenquadramento=None,
            anotacaoevento=None,
            anotacaofalta=None,
            anotacaoferias=None,
            anotacaogratificacao=None,
            anotacaohorarioespecial=None,
            anotacaolicenca=None,
            anotacaopenadisciplinar=None,
            anotacaorecesso=None,
            anotacaofolgacompensacao=None,
            anotacaofolgaeleitoral=None,
            anotacaofolgaaniversario=None,
            anotacaoplantao=None,
            anotacaoremocao=None,
            anotacaotempodobro=None,
            anotacaotemposervico=None,
            anotacaotransposicao=None,
            anotacaocarreira=None,
            anotacaoafastamento=None,
            anotacaoviagem=None,
        )


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "publicacao",
                "tipo_comunicacao",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoComunicacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoComunicacao
            exclude = [
                "numero_processo",
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Comunicação",
        "LIST": "Gerenciador de Anotação Comunicação",
        "NEW": "Novo(a) Anotação Comunicação",
        "EDIT": "Editando um(a) Anotação Comunicação",
        "DELETE": "Removendo um(a) Anotação Comunicação",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Tipo Comunicação",
                "sortable": True,
                "dataIndex": "tipo_comunicacao",
                "key": "tipo_comunicacao",
                "width": 130,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "responsavel",
                "data_inicio",
                "data_fim",
                "publicacao",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoElogio(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        responsavel = AutoCompleteField(
            model=PessoaFisica, controller=RHPessoaFisica, label="Responsável"
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoElogio
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Elogio",
        "LIST": "Gerenciador de Anotação Elogio",
        "NEW": "Novo(a) Anotação Elogio",
        "EDIT": "Editando um(a) Anotação Elogio",
        "DELETE": "Removendo um(a) Anotação Elogio",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Responsável",
                "sortable": True,
                "dataIndex": "responsavel",
                "key": "responsavel",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "publicacao",
                "quadro",
                "complemento_cargo",
                "lei",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoEnquadramento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        quadro = AutoCompleteField(model=Quadro, controller="RHQuadro", label="Cargo")
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoEnquadramento
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Enquadramento",
        "LIST": "Gerenciador de Anotação Enquadramento",
        "NEW": "Novo(a) Anotação Enquadramento",
        "EDIT": "Editando um(a) Anotação Enquadramento",
        "DELETE": "Removendo um(a) Anotação Enquadramento",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 240,
            },
            {
                "header": "Complemento Cargo",
                "sortable": True,
                "dataIndex": "complemento_cargo",
                "key": "complemento_cargo",
                "width": 140,
            },
            {
                "header": "Lei",
                "sortable": True,
                "dataIndex": "lei",
                "key": "lei",
                "width": 120,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "tipo_evento",
                "nome_evento",
                "instituicao",
                "carga_horaria",
                "patrocinador",
                "tipo_participacao",
                "resumo",
            ],
        },
    ]
)
class RHAnotacaoEvento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        patrocinador = AutoCompleteField(
            model=Patrocinador,
            controller=RHPatrocinador,
            label="Patrocinador",
            required=False,
        )
        certificado = FileUploadField(label="Certificado", required=False)
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoEvento
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Evento",
        "LIST": "Gerenciador de Anotação Evento",
        "NEW": "Novo(a) Anotação Evento",
        "EDIT": "Editando um(a) Anotação Evento",
        "DELETE": "Removendo um(a) Anotação Evento",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Carga Horária",
                "sortable": True,
                "dataIndex": "carga_horaria",
                "key": "carga_horaria",
                "width": 140,
            },
            {
                "header": "Efeito Progressão",
                "sortable": True,
                "dataIndex": "efeito_progressao",
                "key": "efeito_progressao",
                "width": 140,
            },
            {
                "header": "Instituição",
                "sortable": True,
                "dataIndex": "instituicao",
                "key": "instituicao",
                "width": 120,
            },
            {
                "header": "Patrocinador",
                "sortable": True,
                "dataIndex": "patrocinador",
                "key": "patrocinador",
                "width": 240,
            },
            {
                "header": "Tipo Evento",
                "sortable": True,
                "dataIndex": "tipo_evento",
                "key": "tipo_evento",
                "width": 240,
            },
            {
                "header": "Nome Evento",
                "sortable": True,
                "dataIndex": "nome_evento",
                "key": "nome_evento",
                "width": 240,
            },
            {
                "header": "Tipo Participação",
                "sortable": True,
                "dataIndex": "tipo_participacao",
                "key": "tipo_participacao",
                "width": 140,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "abonada",
                "dias",
                "publicacao",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoFalta(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoFalta
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Falta",
        "LIST": "Gerenciador de Anotação Falta",
        "NEW": "Novo(a) Anotação Falta",
        "EDIT": "Editando um(a) Anotação Falta",
        "DELETE": "Removendo um(a) Anotação Falta",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Abonada",
                "sortable": True,
                "dataIndex": "abonada",
                "key": "abonada",
                "width": 90,
            },
            {
                "header": "Dias",
                "sortable": True,
                "dataIndex": "dias",
                "key": "dias",
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "publicacao", "resumo", "texto"]},
        {"title": "Informações", "field": ["periodo"]},
    ]
)
class RHAnotacaoFerias(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoFerias
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "numero_processo",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Férias",
        "LIST": "Gerenciador de Anotação Férias",
        "NEW": "Novo(a) Anotação Férias",
        "EDIT": "Editando um(a) Anotação Férias",
        "DELETE": "Removendo um(a) Anotação Férias",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Periodo",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 90,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            # {'header': 'Número Processo', 'sortable': True, 'dataIndex': 'numero_processo', 'key': 'numero_processo', 'width': 130},
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            # {'header': 'Ativa', 'sortable': True, 'dataIndex': 'ativa', 'key': 'ativa', 'width': 70},
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "publicacao",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoGratificacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoGratificacao
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "numero_processo",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Gratificação",
        "LIST": "Gerenciador de Anotação Gratificação",
        "NEW": "Novo(a) Anotação Gratificação",
        "EDIT": "Editando um(a) Anotação Gratificação",
        "DELETE": "Removendo um(a) Anotação Gratificação",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": ["servidor", "dados_horario", "publicacao", "resumo", "texto"],
        }
    ]
)
class RHAnotacaoHorarioEspecial(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoHorarioEspecial
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "numero_processo",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Horário Especial",
        "LIST": "Gerenciador de Anotação Horário Especial",
        "NEW": "Novo(a) Anotação Horário Especial",
        "EDIT": "Editando um(a) Anotação Horário Especial",
        "DELETE": "Removendo um(a) Anotação Horário Especial",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 320,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHAnotHorEspDados(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = AnotHorEspDados
            exclude = ["created_by", "modified_by", "created_at", "modified_at"]

    titles = {
        "PANEL": "Dados do Horário Especial",
        "LIST": "Gerenciador de Dados do Horário Especial",
        "NEW": "Novo(a) Dado do Horário Especial",
        "EDIT": "Editando um(a) Dado do Horário Especial",
        "DELETE": "Removendo um(a) Dado do Horário Especial",
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
                "header": "Dia da Semana",
                "sortable": True,
                "dataIndex": "dia_semana",
                "key": "dia_semana",
                "width": 120,
            },
            {
                "header": "Turno",
                "sortable": True,
                "dataIndex": "turno",
                "key": "turno",
                "width": 120,
            },
            {
                "header": "Entrada/Saída",
                "sortable": True,
                "dataIndex": "ent_saida",
                "key": "ent_saida",
                "width": 120,
            },
            {
                "header": "Horário",
                "sortable": True,
                "dataIndex": "horario",
                "key": "horario",
                "width": 120,
            },
        ]
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "remunerada",
                "quinquenio",
                "publicacao",
                "prazo_dias",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoLicenca(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoLicenca
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "numero_processo",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Licença",
        "LIST": "Gerenciador de Anotação Licença",
        "NEW": "Novo(a) Anotação Licença",
        "EDIT": "Editando um(a) Anotação Licença",
        "DELETE": "Removendo um(a) Anotação Licença",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Prazo Dias",
                "sortable": True,
                "dataIndex": "prazo_dias",
                "key": "prazo_dias",
                "width": 120,
            },
            {
                "header": "Quinquênio",
                "sortable": True,
                "dataIndex": "quinquenio",
                "key": "quinquenio",
                "width": 120,
            },
            {
                "header": "Remunerada",
                "sortable": True,
                "dataIndex": "remunerada",
                "key": "remunerada",
                "width": 120,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "penalidade",
                "responsavel",
                "resumo",
                "texto",
            ],
        },
        {
            "title": "Informações",
            "field": ["data_inicio", "data_fim", "numero_processo"],
        },
        {"title": "Decisão", "field": ["data_decisao", "texto_decisao"]},
    ]
)
class RHAnotacaoPenaDisciplinar(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        penalidade = AutoCompleteField(
            model=Penalidade, controller=RHPenalidade, label="Penalidade"
        )
        responsavel = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Responsável"
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoPenaDisciplinar
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Pena Disciplinar",
        "LIST": "Gerenciador de Anotação Pena Disciplinar",
        "NEW": "Novo(a) Anotação Pena Disciplinar",
        "EDIT": "Editando um(a) Anotação Pena Disciplinar",
        "DELETE": "Removendo um(a) Anotação Pena Disciplinar",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Data Decisão",
                "sortable": True,
                "dataIndex": "data_decisao",
                "key": "data_decisao",
                "width": 100,
            },
            {
                "header": "Texto Decisão",
                "sortable": True,
                "dataIndex": "texto_decisao",
                "key": "texto_decisao",
                "width": 240,
            },
            {
                "header": "Penalidade",
                "sortable": True,
                "dataIndex": "penalidade",
                "key": "penalidade",
                "width": 120,
            },
            {
                "header": "Responsável",
                "sortable": True,
                "dataIndex": "responsavel",
                "key": "responsavel",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "situacao",
                "periodo",
                "resumo",
                "texto",
            ],
        },
        {
            "title": "Informações",
            "field": ["ano", "data_inicio", "data_fim", "data_reassuncao"],
        },
    ]
)
class RHAnotacaoRecesso(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoRecesso
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Recesso",
        "LIST": "Gerenciador de Anotação Recesso",
        "NEW": "Novo(a) Anotação Recesso",
        "EDIT": "Editando um(a) Anotação Recesso",
        "DELETE": "Removendo um(a) Anotação Recesso",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "data_inicio",
                "data_fim",
                "resumo",
                "texto",
            ],
        },
    ]
)
class RHAnotacaoFolgaCompensacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoFolgaCompensacao
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Folga Compensação",
        "LIST": "Gerenciador de Anotação Folga Compensação",
        "NEW": "Novo(a) Anotação Folga Compensação",
        "EDIT": "Editando um(a) Anotação Folga Compensação",
        "DELETE": "Removendo um(a) Anotação Folga Compensação",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "data_inicio",
                "data_fim",
                "resumo",
                "texto",
            ],
        },
    ]
)
class RHAnotacaoFolgaEleitoral(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoFolgaEleitoral
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Folga Eleitoral",
        "LIST": "Gerenciador de Anotação Folga Eleitoral",
        "NEW": "Novo(a) Anotação Folga Eleitoral",
        "EDIT": "Editando um(a) Anotação Folga Eleitoral",
        "DELETE": "Removendo um(a) Anotação Folga Eleitoral",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "data_inicio",
                "data_fim",
                "resumo",
                "texto",
            ],
        },
    ]
)
class RHAnotacaoFolgaAniversario(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoFolgaAniversario
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Folga Aniversário",
        "LIST": "Gerenciador de Anotação Folga Aniversário",
        "NEW": "Novo(a) Anotação Folga Aniversário",
        "EDIT": "Editando um(a) Anotação Folga Aniversário",
        "DELETE": "Removendo um(a) Anotação Folga Aniversário",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "ano",
                "data_inicio",
                "data_fim",
                "data_reassuncao",
                "publicacao",
                "situacao",
                "periodo",
                "resumo",
                "texto",
            ],
        },
    ]
)
class RHAnotacaoPlantao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoPlantao
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Plantão",
        "LIST": "Gerenciador de Anotação Plantão",
        "NEW": "Novo(a) Anotação Plantão",
        "EDIT": "Editando um(a) Anotação Plantão",
        "DELETE": "Removendo um(a) Anotação Plantão",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "data_inicio",
                "data_fim",
                "resumo",
                "texto",
            ],
        },
    ]
)
class RHAnotacaoViagem(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoViagem
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Viagem",
        "LIST": "Gerenciador de Anotação Viagem",
        "NEW": "Novo(a) Anotação Viagem",
        "EDIT": "Editando um(a) Anotação Viagem",
        "DELETE": "Removendo um(a) Anotação Viagem",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano",
                "sortable": True,
                "dataIndex": "ano",
                "key": "ano",
                "width": 70,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 100,
            },
            {
                "header": "Data Reassunção",
                "sortable": True,
                "dataIndex": "data_reassuncao",
                "key": "data_reassuncao",
                "width": 120,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "key": "situacao",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "publicacao", "resumo", "texto"]},
    ]
)
class RHAnotacaoRemocao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoRemocao
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Remoção",
        "LIST": "Gerenciador de Anotação Remoção",
        "NEW": "Novo(a) Anotação Remoção",
        "EDIT": "Editando um(a) Anotação Remoção",
        "DELETE": "Removendo um(a) Anotação Remoção",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 240,
            },
            {
                "header": "Classe",
                "sortable": True,
                "dataIndex": "classe",
                "key": "classe",
                "width": 120,
            },
            {
                "header": "Local",
                "sortable": True,
                "dataIndex": "local",
                "key": "local",
                "width": 120,
            },
            {
                "header": "Órgão",
                "sortable": True,
                "dataIndex": "unidade_administrativa",
                "key": "unidade_administrativa",
                "width": 240,
            },
            {
                "header": "Parecer",
                "sortable": True,
                "dataIndex": "parecer",
                "key": "parecer",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao",
                "unidade_administrativa",
                "pessoa_juridica",
                "resumo",
                "texto",
            ],
        },
        {
            "title": "Tempo de Serviço",
            "field": [
                "data_inicio",
                "data_fim",
                "tempo_servico_finalidade",
                "tempo_liquido",
                "responsavel",
                "parecer",
                "anos",
                "meses",
                "dias",
            ],
        },
    ]
)
class RHAnotacaoTempoServico(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        tempo_servico_finalidade = AutoCompleteField(
            model=TempoServicoFinalidade,
            controller=RHTempoServicoFinalidade,
            label="Finalidade de Tempo de Serviço",
        )
        pessoa_juridica = AutoCompleteField(
            model=PessoaJuridica,
            label="Pessoa Jurídica",
            controller=RHPessoaJuridica,
            required=False,
        )
        unidade_administrativa = AutoCompleteField(
            model=UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Unidade Administrativa",
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoTempoServico
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Tempo Serviço/Contribuição",
        "LIST": "Gerenciador de Anotação Tempo Serviço/Contribuição",
        "NEW": "Novo(a) Anotação Tempo Serviço/Contribuição",
        "EDIT": "Editando um(a) Anotação Tempo Serviço/Contribuição",
        "DELETE": "Removendo um(a) Anotação Tempo Serviço/Contribuição",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Anos",
                "sortable": True,
                "dataIndex": "anos",
                "key": "anos",
                "width": 90,
            },
            {
                "header": "Meses",
                "sortable": True,
                "dataIndex": "meses",
                "key": "meses",
                "width": 90,
            },
            {
                "header": "Dias",
                "sortable": True,
                "dataIndex": "dias",
                "key": "dias",
                "width": 90,
            },
            {
                "header": "Órgão Geral",
                "sortable": True,
                "dataIndex": "orgao_geral",
                "key": "orgao_geral",
                "width": 240,
            },
            {
                "header": "Parecer",
                "sortable": True,
                "dataIndex": "parecer",
                "key": "parecer",
                "width": 120,
            },
            {
                "header": "Pessoa Jurídica",
                "sortable": True,
                "dataIndex": "pessoa_juridica",
                "key": "pessoa_juridica",
                "width": 240,
            },
            {
                "header": "Responsável",
                "sortable": True,
                "dataIndex": "responsavel",
                "key": "responsavel",
                "width": 240,
            },
            {
                "header": "Tempo Líquido",
                "sortable": True,
                "dataIndex": "tempo_liquido",
                "key": "tempo_liquido",
                "width": 140,
            },
            {
                "header": "Tempo Serviço Finalidade",
                "sortable": True,
                "dataIndex": "tempo_servico_finalidade",
                "key": "tempo_servico_finalidade",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "ano_ferias",
                "total_dias",
                "periodo",
                "publicacao",
                "resumo",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoTempoDobro(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoTempoDobro
            exclude = [
                "anotacaogeral_ptr",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "ativa",
                "numero_processo",
                "data_documento",
                "data_portaria_inicio",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Tempo Dobro",
        "LIST": "Gerenciador de Anotação Tempo Dobro",
        "NEW": "Novo(a) Anotação Tempo Dobro",
        "EDIT": "Editando um(a) Anotação Tempo Dobro",
        "DELETE": "Removendo um(a) Anotação Tempo Dobro",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Ano Férias",
                "sortable": True,
                "dataIndex": "ano_ferias",
                "key": "ano_ferias",
                "width": 90,
            },
            {
                "header": "Total Dias",
                "sortable": True,
                "dataIndex": "total_dias",
                "key": "total_dias",
                "width": 90,
            },
            {
                "header": "Período",
                "sortable": True,
                "dataIndex": "periodo",
                "key": "periodo",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": ["servidor", "data_opcao", "publicacao", "resumo", "texto"],
        }
    ]
)
class RHAnotacaoTransposicao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoTransposicao
            exclude = [
                "anotacaogeral_ptr",
                "data_documento",
                "data_portaria_inicio",
                "tipo_documento",
                "numero_documento",
                "indireto",
                "numero_processo",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Transposição",
        "LIST": "Gerenciador de Anotação Transposição",
        "NEW": "Novo(a) Anotação Transposição",
        "EDIT": "Editando um(a) Anotação Transposição",
        "DELETE": "Removendo um(a) Anotação Transposição",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 120,
            },
            {
                "header": "Data Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 120,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 90,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
            {
                "header": "Número Processo",
                "sortable": True,
                "dataIndex": "numero_processo",
                "key": "numero_processo",
                "width": 130,
            },
            {
                "header": "Data Opção",
                "sortable": True,
                "dataIndex": "data_opcao",
                "key": "data_opcao",
                "width": 120,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "resumo",
                "tipo_documento",
                "publicacao",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoAfastamento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoAfastamento
            exclude = [
                "numero_processo",
                "data_documento",
                "anotacaogeral_ptr",
                "numero_documento",
                "indireto",
                "data_portaria_inicio",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Afastamento",
        "LIST": "Gerenciador de Anotação Afastamento",
        "NEW": "Novo(a) Anotação Afastamento",
        "EDIT": "Editando um(a) Anotação Afastamento",
        "DELETE": "Removendo um(a) Anotação Afastamento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 280,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "toSearch": True,
                "width": 250,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "toSearch": False,
                "width": 120,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "toSearch": True,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_fim",
                "resumo",
                "tipo_documento",
                "publicacao",
                "texto",
            ],
        }
    ]
)
class RHAnotacaoAusencia(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoAusencia
            exclude = [
                "numero_processo",
                "data_documento",
                "anotacaogeral_ptr",
                "numero_documento",
                "indireto",
                "data_portaria_inicio",
                "ativa",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação Ausência",
        "LIST": "Gerenciador de Anotação Ausência",
        "NEW": "Novo(a) Anotação Ausência",
        "EDIT": "Editando um(a) Anotação Ausência",
        "DELETE": "Removendo um(a) Anotação Ausência",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHQuadro(extjs.ExtCrud):
    class Form(forms.ModelForm):
        cargo = AutoCompleteField(model=Cargo, controller=RHCargo, label="Cargo")
        especialidade = AutoCompleteField(
            model=Especialidade,
            controller=RHEspecialidade,
            required=False,
            label="Especialidade",
        )

        class Meta:
            model = Quadro
            exclude = ["created_by", "modified_by", "created_at", "modified_at"]

    titles = {
        "PANEL": "Quadro",
        "LIST": "Gerenciador de Quadros",
        "NEW": "Novo(a) Quadro",
        "EDIT": "Editando um(a) Quadro",
        "DELETE": "Removendo um(a) Quadro",
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
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "cargo",
                "key": "cargo",
                "width": 350,
            },
            {
                "header": "Especialidade",
                "sortable": True,
                "dataIndex": "especialidade",
                "key": "especialidade",
                "width": 350,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHCargoQuadro(extjs.ExtCrud):
    class Form(forms.ModelForm):
        cargo = AutoCompleteField(model=Cargo, controller=RHCargo, label="Cargo")
        publicacao_criacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação de Criação"
        )
        publicacao_extincao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação de Extinção",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação de Alteração",
            required=False,
        )
        especialidade = AutoCompleteField(
            model=Especialidade,
            controller=RHEspecialidade,
            required=False,
            label="Especialidade",
        )

        class Meta:
            model = CargoQuadro
            exclude = ["created_by", "modified_by", "created_at", "modified_at"]

    titles = {
        "PANEL": "Quadro",
        "LIST": "Gerenciador Cargos de Quadros",
        "NEW": "Novo(a) Cargos de Quadro",
        "EDIT": "Editando um(a) Cargo de Quadro",
        "DELETE": "Removendo um(a) Cargo de Quadro",
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
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "cargo",
                "key": "cargo",
                "width": 350,
            },
            {
                "header": "Código",
                "sortable": True,
                "dataIndex": "cargo",
                "key": "cargo",
                "width": 70,
            },
            {
                "header": "Especialidade",
                "sortable": True,
                "dataIndex": "especialidade",
                "key": "especialidade",
                "width": 250,
            },
            {
                "header": "Qtd. Vagas",
                "sortable": True,
                "dataIndex": "quantidade_vagas",
                "key": "quantidade_vagas",
                "width": 75,
            },
            {
                "header": "C. Horária",
                "sortable": True,
                "dataIndex": "carga_horaria",
                "key": "carga_horaria",
                "width": 70,
            },
            {
                "header": "Nível Escolaridade",
                "sortable": True,
                "dataIndex": "nivel_escolaridade",
                "key": "nivel_escolaridade",
                "width": 140,
            },
            {
                "header": "Publicação Criação",
                "sortable": True,
                "dataIndex": "publicacao_criacao",
                "key": "publicacao_criacao",
                "width": 120,
            },
            {
                "header": "Publicação Extinção",
                "sortable": True,
                "dataIndex": "publicacao_extinsao",
                "key": "publicacao_extinsao",
                "width": 120,
            },
            {
                "header": "Remuneração Inicial",
                "sortable": True,
                "dataIndex": "remuneracao_inicial",
                "key": "remuneracao_inicial",
                "width": 120,
            },
            {
                "header": "Remuneração Final",
                "sortable": True,
                "dataIndex": "remuneracao_final",
                "key": "remuneracao_final",
                "width": 120,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class RHMovimentacaoPessoal(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor,
            father=b"RHMovimentacaoPessoal",
            controller=RHServidor,
            label="Servidor",
        )

        class Meta:
            model = MovimentacaoPessoal
            exclude = [
                "data_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Movimentação Pessoal",
        "LIST": "Gerenciador de Movimentações Pessoais",
        "NEW": "Novo(a) Movimentação Pessoal",
        "EDIT": "Editando um(a) Movimentação Pessoal",
        "DELETE": "Removendo um(a) Movimentação Pessoal",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Anotação Geral",
                "sortable": True,
                "dataIndex": "anotacao_geral",
                "key": "anotacao_geral",
                "width": 350,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 320,
            },
        ]
        self.response.write(json.encode(obj))


class RHPublicConcurrence(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = PublicConcurrence
            exclude = ["created_by", "modified_by", "created_at", "modified_at"]

    titles = {
        "PANEL": "Concurso Público",
        "LIST": "Gerenciador de Concurso Público",
        "NEW": "Novo(a) Concurso Público",
        "EDIT": "Editando um(a) Concurso Público",
        "DELETE": "Removendo um(a) Concurso Público",
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
                "dataIndex": "name",
                "key": "name",
                "width": 140,
            },
            {
                "header": "Número MPE",
                "sortable": True,
                "dataIndex": "number_mpe",
                "key": "number_mpe",
                "width": 140,
            },
            {
                "header": "Ano MPE",
                "sortable": True,
                "dataIndex": "year_mpe",
                "key": "year_mpe",
                "width": 140,
            },
            {
                "header": "TCE",
                "sortable": True,
                "dataIndex": "number_tce",
                "key": "number_tce",
                "width": 140,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "resume",
                "key": "resume",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Posse",
            "field": [
                "servidor",
                "quadro",
                "data_posse",
                "data_exercicio",
                "publicacao_movimentacao",
                "bond",
                "public_concurrence",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoPosse(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        quadro = AutoCompleteField(model=Quadro, controller=RHQuadro, label="Cargo")
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação Nomeação"
        )
        public_concurrence = AutoCompleteField(
            model=PublicConcurrence,
            controller=RHPublicConcurrence,
            label="Concurso",
            required=False,
        )

        class Meta:
            model = MovimentacaoPosse
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "anotacao_geral_nomeacao",
                "data_desligamento",
                "anotacao_geral_exercicio",
                "ativo",
                "data_alteracao",
                "publicacao_alteracao",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Nomeação - Posse - Exercício",
        "LIST": "Gerenciador de Nomeação - Posse - Exercício",
        "NEW": "Novo(a) Nomeação - Posse - Exercício",
        "EDIT": "Editando um(a)  Nomeação - Posse - Exercício",
        "DELETE": "Removendo um(a)  Nomeação - Posse - Exercício",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        buf = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Quadro",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 300,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "key": "ativo",
                "width": 70,
            },
            {
                "header": "Data Exercício",
                "sortable": True,
                "dataIndex": "data_exercicio",
                "key": "data_exercicio",
                "width": 100,
            },
            {
                "header": "Data Posse",
                "sortable": True,
                "dataIndex": "data_posse",
                "key": "data_posse",
                "width": 90,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 180,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
        ]
        buf = self._apply_to_search_for_columns_grid(buf)
        self.response.write(json.encode(buf))


@tab(
    [
        {
            "title": "Desligamento",
            "field": [
                "movimentacao_posse",
                "tipo_desligamento",
                "data_desligamento",
                "publicacao_movimentacao",
                "opcao",
                "vacancia",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoDesligamento(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        movimentacao_posse = AutoCompleteField(
            model=MovimentacaoPosse, father=b"RHMovimentacaoDesligamento", label="Posse"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )

        class Meta:
            model = MovimentacaoDesligamento
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "publicacao_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Desligamento",
        "LIST": "Gerenciador de Desligamentos",
        "NEW": "Novo(a) Desligamento",
        "EDIT": "Editando um(a)  Desligamento",
        "DELETE": "Removendo um(a)  Desligamento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        buf = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Desligamento",
                "sortable": True,
                "dataIndex": "data_desligamento",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Tipo de Desligamento",
                "sortable": True,
                "dataIndex": "tipo_desligamento",
                "key": "tipo_desligamento",
                "width": 150,
            },
            {
                "header": "Movimentação Posse",
                "sortable": True,
                "dataIndex": "movimentacao_posse",
                "key": "movimentacao_posse",
                "width": 240,
            },
            {
                "header": "Opção",
                "sortable": True,
                "dataIndex": "opcao",
                "key": "opcao",
                "width": 70,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
        ]
        buf = self._apply_to_search_for_columns_grid(buf)
        self.response.write(json.encode(buf))

    def get_query(self):
        return MovimentacaoDesligamento.objects.filter(movimentacaoaposentadoria=None)


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "orgao_origem",
                "posse_origem",
                "publicacao_movimentacao",
                "onus",
                "data_inicio",
                "data_fim",
                "texto",
            ],
        },
        {"title": "Períodos", "field": ["periodo", "anota"]},
    ]
)
class RHMovimentacaoRequisicao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        orgao_origem = AutoCompleteField(
            model=UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Órgão Origem",
            required=False,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação da requisição"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )
        posse_origem = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse Origem",
            required=False,
        )

        class Meta:
            model = MovimentacaoRequisicao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "ativo",
                "servidor",
                "data_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 50,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Onus",
                "sortable": True,
                "dataIndex": "onus",
                "toSearch": True,
                "width": 100,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "toSearch": True,
                "width": 50,
            },
            {
                "header": "Órgão origem",
                "sortable": True,
                "dataIndex": "orgao_origem",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Posse Origem",
                "sortable": True,
                "dataIndex": "posse_origem",
                "toSearch": True,
                "width": 300,
            },
            {
                "header": "Primeira publicação",
                "sortable": True,
                "dataIndex": "posse",
                "toSearch": True,
                "width": 300,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Requisição",
        "LIST": "Gerenciador de Requisições",
        "NEW": "Novo(a) Requisição",
        "EDIT": "Editando um(a)  Requisição",
        "DELETE": "Removendo um(a)  Requisição",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "publicacao_movimentacao",
            ],
        },
    ]
)
class RHMovimentacaoAproveitamento(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse anterior",
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoAproveitamento
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Aproveitamento",
        "LIST": "Gerenciador de Aproveitamentos",
        "NEW": "Novo(a) Aproveitamento",
        "EDIT": "Editando um(a) Aproveitamento",
        "DELETE": "Removendo um(a) Aproveitamento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "publicacao_movimentacao",
            ],
        },
    ]
)
class RHMovimentacaoReadaptacao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse anterior",
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoReadaptacao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Readaptação",
        "LIST": "Gerenciador de Readaptação",
        "NEW": "Novo(a) Readaptação",
        "EDIT": "Editando um(a) Readaptação",
        "DELETE": "Removendo um(a) Readaptação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "data_exercicio",
                "publicacao_movimentacao",
                "publicacao_alteracao",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoReconducao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse anterior",
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoReconducao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "quadro",
                "data_posse",
                "data_desligamento",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Recondução",
        "LIST": "Gerenciador de Reconduções",
        "NEW": "Novo(a) Recondução",
        "EDIT": "Editando um(a) Recondução",
        "DELETE": "Removendo um(a) Recondução",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "publicacao_movimentacao",
            ],
        },
    ]
)
class RHMovimentacaoReintegracao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse anterior",
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoReintegracao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Reintegração",
        "LIST": "Gerenciador de Reintegrações",
        "NEW": "Novo(a) Reintegração",
        "EDIT": "Editando um(a)  Reintegração",
        "DELETE": "Removendo um(a)  Reintegração",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "publicacao_movimentacao",
            ],
        },
    ]
)
class RHMovimentacaoReversao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse anterior",
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoReversao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Reversão",
        "LIST": "Gerenciador de Reversões",
        "NEW": "Novo(a) Reversão",
        "EDIT": "Editando um(a)  Reversão",
        "DELETE": "Removendo um(a)  Reversão",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Desligamento",
            "field": [
                "movimentacao_posse",
                "tipo_aposentadoria",
                "data_desligamento",
                "opcao",
                "publicacao_movimentacao",
            ],
        },
    ]
)
class RHMovimentacaoAposentadoria(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        data_desligamento = forms.DateField(label="Data")
        movimentacao_posse = AutoCompleteField(
            model=MovimentacaoPosse, father="RHMovimentacaoDesligamento", label="Posse"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoAposentadoria
            exclude = [
                "movimentacaopessoal_ptr",
                "movimentacaodesligamento_ptr",
                "servidor",
                "anotacao_geral",
                "data_alteracao",
                "tipo_desligamento",
                "reversao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Tipo Aposentadoria",
                "sortable": True,
                "dataIndex": "tipo_aposentadoria",
                "key": "tipo_aposentadoria",
                "width": 200,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 280,
            },
            {
                "header": "Reversão",
                "sortable": True,
                "dataIndex": "reversao",
                "key": "reversao",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Aposentadoria",
        "LIST": "Gerenciador de Aposentadorias",
        "NEW": "Novo(a) Aposentadoria",
        "EDIT": "Editando um(a)  Aposentadoria",
        "DELETE": "Removendo um(a)  Aposentadoria",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHSituacaoFuncional(CustomAutocomplete, extjs.ExtViewOnlyCrud):

    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )

        class Meta:
            model = SituacaoFuncional
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Situação Funcional",
        "LIST": "Gerenciador de Situações Funcionais",
        "VIEW": "Visualizar",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 50,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": False,
                "width": 250,
            },
            {
                "header": "Alteração",
                "sortable": True,
                "dataIndex": "data_alteracao",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Situação",
                "sortable": True,
                "dataIndex": "situacao",
                "toSearch": False,
                "width": 250,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def query(self, args=[]):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        from django.db.models import Model

        result = {
            "result": [],
            "totalRows": self.get_total_rows(),
        }

        query = self.get_query_filtred()

        for row in query:
            info = {}

            info["__description__"] = row
            try:
                for field in list(self.get_fields().keys()):
                    if field != "id" and field[len(field) - 3 :] == "_id":
                        field = field[0 : len(field) - 3]

                    funcname = "get_{0}_display".format(field)
                    func = getattr(row, funcname, None)
                    value = getattr(row, field)

                    if func is not None:
                        info[field] = func()
                    elif isinstance(value, datetime):
                        info[field] = DateUtils.datetime_to_str(value)
                    elif isinstance(value, date):
                        info[field] = DateUtils.date_to_str(value)
                    elif isinstance(value, bool):
                        info[field] = value and "Sim" or "Não"
                    elif value is None:
                        info[field] = ""
                    elif isinstance(value, Model):
                        info[field] = value
                        info["%s__pk" % field] = value.pk
                    else:
                        info[field] = value

                info["pk"] = row.pk
                info["description"] = row
                info["controller"] = self.get_instance_controller(row)

                result["result"].append(info)
            except Exception as e:
                self.log.exception(e)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(result))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "afastamento",
                "servidor",
                "posse",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "data_fim",
            ],
        },
    ]
)
class RHMovimentacaoSubstituicao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        afastamento = AutoCompleteField(
            model=afastamento_models.BaseLicencaAfastamento,
            father="RHMovimentacaoSubstituicao",
            label="Afastamento",
        )
        posse = AutoCompleteField(
            model=MovimentacaoPosse,
            father="RHMovimentacaoSubstituicaoMembro",
            label="Posse substituído",
            required=False,
        )
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Substituto"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Documento", required=False
        )
        publicacao_fim = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Documento fim",
            required=False,
        )
        designation_substitute = AutoCompleteField(
            model=ServidorLotacao,
            controller="RHServidorLotacao",
            label="Designação Substituto",
        )

        designation_substituted = AutoCompleteField(
            model=ServidorLotacao,
            controller="RHServidorLotacao",
            label="Designação Substituição",
        )
        place = AutoCompleteField(
            model=Lotacao,
            controller=RHLotacao,
            label="Lotação",
        )

        class Meta:
            model = MovimentacaoSubstituicao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "servidor_substituido",
                "designation_substitute",
                "data_alteracao",
                "publicacao_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Substituição",
        "LIST": "Gerenciador de Substituições",
        "NEW": "Novo(a) Substituição",
        "EDIT": "Editando um(a)  Substituição",
        "DELETE": "Removendo um(a)  Substituição",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_query(self, args=[]):
        """ """
        return MovimentacaoSubstituicao.objects.filter().exclude(
            ~Q(movimentacaosubstituicaomembro=None)
        )

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "posse",
                "key": "posse",
                "width": 340,
            },
            {
                "header": "Substituto",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 250,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def retorno_list(self, query):
        result = []
        for substituicao in query:
            try:
                status = "ATIVO"
                try:
                    if datetime.now().date() < substituicao.data_inicio:
                        status = "AGENDADO"
                    elif datetime.now().date() > substituicao.data_fim:
                        status = "ENCERRADO"
                except Exception:
                    pass
                cargo = (
                    substituicao.posse
                    if substituicao.posse
                    else substituicao.servidor_substituido
                )
                tipo = "servidor"
                if hasattr(substituicao, "movimentacaosubstituicaomembro"):
                    tipo = "membro"
                item = {
                    "pk": substituicao.pk,
                    "data_inicio": (
                        DateUtils.date_to_str(substituicao.data_inicio)
                        if substituicao.data_inicio
                        else ""
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(substituicao.data_fim)
                        if substituicao.data_fim
                        else ""
                    ),
                    "data_prevista": (
                        DateUtils.date_to_str(substituicao.data_prevista)
                        if substituicao.data_prevista
                        else ""
                    ),
                    "cargo": cargo,
                    "substituto": substituicao.servidor,
                    "situacao": status,
                    "tipo": tipo,
                }
            except Exception as e:
                log.exception(e)
            else:
                result.append(item)
        return result

    def apply_filter(self, query):
        qs = []
        if "keyword" in self.request.POST:
            qs.append(
                Q(
                    servidor_substituido__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    servidor_substituido__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(servidor__pessoa_fisica__nome__icontains=self.request.POST["keyword"])
            )
            qs.append(Q(servidor__matricula__icontains=self.request.POST["keyword"]))
        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)
        query = query.filter(q) if q else query
        return query

    @login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST.get("sort", "data_fim")
        direction = self.request.POST.get("dir", "DESC")

        order_by = "%s%s" % ("" if direction == "ASC" else "-", sort)

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 50))
        end = start + limit

        query = MovimentacaoSubstituicao.objects.filter().order_by(order_by)
        if self.request.POST.get("servidor", False) and self.request.POST.get(
            "afastamento", False
        ):
            query = query.filter(
                servidor_substituido__matricula=self.request.POST.get("servidor"),
                afastamento__pk=self.request.POST.get("afastamento"),
            ).order_by(order_by)

        query = self.apply_filter(query)
        obj.update(totalRows=query.count())

        query = query[start:end]
        result = self.retorno_list(query)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def list_substitute(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST.get("sort", "data_fim")
        direction = self.request.POST.get("dir", "DESC")

        order_by = "%s%s" % ("" if direction == "ASC" else "-", sort)

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 50))
        end = start + limit

        query = MovimentacaoSubstituicao.objects.filter().order_by(order_by)
        qs = []
        if "keyword" in self.request.POST:
            qs.append(
                Q(servidor__pessoa_fisica__nome__icontains=self.request.POST["keyword"])
            )
            qs.append(Q(servidor__matricula__icontains=self.request.POST["keyword"]))
        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)
        query = query.filter(q) if q else query

        obj.update(totalRows=query.count())
        query = query[start:end]
        result = self.retorno_list(query)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "afastamento",
                "servidor",
                "designacao_substituido",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "data_fim",
            ],
        },
    ]
)
class RHMovimentacaoSubstituicaoMembro(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        afastamento = AutoCompleteField(
            model=afastamento_models.BaseLicencaAfastamento,
            father="RHMovimentacaoSubstituicaoMembro",
            label="Afastamento",
            required=False,
        )
        servidor = AutoCompleteField(
            model=Servidor,
            controller=RHServidor,
            queryAction="query_membro",
            label="Substituto",
        )
        designacao_substituido = AutoCompleteField(
            model=ServidorLotacao,
            controller="RHServidorLotacao",
            label="Órgão de Execução",
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Documento", required=False
        )
        publicacao_fim = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Documento fim",
            required=False,
        )

        class Meta:
            model = MovimentacaoSubstituicaoMembro
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "servidor_substituido",
                "data_alteracao",
                "publicacao_alteracao",
                "movimentacaosubstituicao_ptr",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "designacao",
            ]

    titles = {
        "PANEL": "Substituição de Membro",
        "LIST": "Gerenciador de Substituições de Membro",
        "NEW": "Novo(a) Substituição de Membro",
        "EDIT": "Editando um(a)  Substituição de Membro",
        "DELETE": "Removendo um(a)  Substituição de Membro",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor_substituido",
                "key": "servidor_substituido",
                "width": 300,
            },
            {
                "header": "Designação",
                "sortable": True,
                "dataIndex": "designacao_substituido",
                "key": "designacao_substituido",
                "width": 280,
            },
            {
                "header": "Substituto",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 250,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 90,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 90,
            },
            {
                "header": "Retorno",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    def get_data(self, args=[]):
        obj = {
            "afastamento": None,
            "cargo_arquimedes": None,
            "designacao_substituido": None,
            "substituto": None,
            "substituido_matricula": None,
            "publicacao_movimentacao": None,
            "publicacao_fim": None,
            "publicacao_alteracao": None,
            "data_inicio": None,
            "data_fim": None,
            "data_prevista": None,
            "motivo": None,
            "anota": None,
            "texto": None,
            "posse": None,
        }
        try:
            substituicao = MovimentacaoSubstituicaoMembro.objects.get(
                pk=int(self.request.POST.get("substituicao"))
            )
            obj.update({"afastamento": substituicao.afastamento.pk})
            obj.update({"cargo_arquimedes": substituicao.cargo_arquimedes})
            obj.update(
                {
                    "designacao_substituido": (
                        substituicao.designacao_substituido.pk
                        if substituicao.designacao_substituido
                        else ""
                    )
                }
            )
            obj.update({"substituto": substituicao.servidor.pk})
            obj.update(
                {"substituido_matricula": substituicao.servidor_substituido.matricula}
            )
            obj.update(
                {
                    "publicacao_movimentacao": (
                        substituicao.publicacao_movimentacao.pk
                        if substituicao.publicacao_movimentacao
                        else ""
                    )
                }
            )
            obj.update(
                {
                    "publicacao_fim": (
                        substituicao.publicacao_fim.pk
                        if substituicao.publicacao_fim
                        else None
                    )
                }
            )
            obj.update(
                {
                    "publicacao_alteracao": (
                        substituicao.publicacao_alteracao.pk
                        if substituicao.publicacao_alteracao
                        else None
                    )
                }
            )
            obj.update({"data_inicio": DateUtils.date_to_str(substituicao.data_inicio)})
            obj.update(
                {
                    "data_fim": (
                        DateUtils.date_to_str(substituicao.data_fim)
                        if substituicao.data_fim
                        else None
                    )
                }
            )
            obj.update(
                {
                    "data_prevista": (
                        DateUtils.date_to_str(substituicao.data_prevista)
                        if substituicao.data_prevista
                        else None
                    )
                }
            )
            obj.update({"motivo": substituicao.afastamento.motivo})
            obj.update({"anota": substituicao.anota})
            obj.update({"texto": substituicao.texto})
            obj.update({"posse": substituicao.posse.pk if substituicao.posse else None})
        except Exception as e:
            self.log.exception(e)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def retorno_list(self, query):
        result = []
        for substituicao in query:
            try:
                status = "ATIVO"
                try:
                    if datetime.now().date() < substituicao.data_inicio:
                        status = "AGENDADO"
                    elif datetime.now().date() > substituicao.data_fim:
                        status = "ENCERRADO"
                except Exception:
                    pass
                cargo = substituicao.posse if substituicao.posse else ""
                tipo = "servidor"
                if hasattr(substituicao, "movimentacaosubstituicaomembro"):
                    tipo = "membro"
                afastamento_conflito = afastamento_models.BaseLicencaAfastamento.verifica_interseccao_periodo(
                    substituicao.servidor,
                    substituicao.data_inicio,
                    substituicao.data_fim,
                )
                afastamento_conflito = (
                    afastamento_conflito[0] if len(afastamento_conflito) > 0 else None
                )
                item = {
                    "pendencia": {
                        "conflito": not (afastamento_conflito is None),
                        "title": (
                            "Substituição conflitando com %s à %s - %s"
                            % (
                                DateUtils.date_to_str(afastamento_conflito.data_inicio),
                                (
                                    DateUtils.date_to_str(afastamento_conflito.data_fim)
                                    if afastamento_conflito.data_fim
                                    else "----"
                                ),
                                afastamento_conflito,
                            )
                            if afastamento_conflito is not None
                            else ""
                        ),
                    },
                    "pk": substituicao.pk,
                    "data_inicio": (
                        DateUtils.date_to_str(substituicao.data_inicio)
                        if substituicao.data_inicio
                        else ""
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(substituicao.data_fim)
                        if substituicao.data_fim
                        else ""
                    ),
                    "data_prevista": (
                        DateUtils.date_to_str(substituicao.data_prevista)
                        if substituicao.data_prevista
                        else ""
                    ),
                    "cargo": cargo,
                    "substituto": substituicao.servidor,
                    "substituido": substituicao.servidor_substituido,
                    "situacao": status,
                    "tipo": tipo,
                }
            except Exception as err:
                log.exception(err)
            else:
                result.append(item)
        return result

    @login_required(type="JSON")
    def list_agendada(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST.get("sort", "data_fim")
        direction = self.request.POST.get("dir", "DESC")

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 50))
        end = start + limit

        query = MovimentacaoSubstituicao.objects.filter(
            servidor__matricula=self.request.POST.get("servidor")
        ).order_by("%s%s" % ("" if direction == "ASC" else "-", sort))
        query = self.apply_filter(query)

        obj.update(totalRows=query.count())

        query = query[start:end]

        result = []
        item = {}
        for substituicao in query:
            try:
                status = "Ativo"
                try:
                    if datetime.now().date() < substituicao.data_inicio:
                        status = "Agendado"
                    elif datetime.now().date() > substituicao.data_fim:
                        status = "Encerrado"
                except Exception:
                    pass
                cargo = substituicao.posse.quadro
                tipo = "servidor"
                if hasattr(substituicao, "movimentacaosubstituicaomembro"):
                    tipo = "membro"
                item = {
                    "pk": substituicao.pk,
                    "data_inicio": (
                        DateUtils.date_to_str(substituicao.data_inicio)
                        if substituicao.data_inicio
                        else ""
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(substituicao.data_fim)
                        if substituicao.data_fim
                        else ""
                    ),
                    "data_prevista": (
                        DateUtils.date_to_str(substituicao.data_prevista)
                        if substituicao.data_prevista
                        else ""
                    ),
                    "cargo": cargo,
                    "substituto": substituicao.servidor,
                    "substituido": substituicao.servidor_substituido,
                    "situacao": status,
                    "tipo": tipo,
                }
            except Exception as err:
                log.exception(err)
            else:
                result.append(item)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def delete(self, args=[]):
        obj = {"success": True, "msg": ""}
        try:
            MovimentacaoSubstituicaoMembro.objects.filter(
                pk=self.request.POST.get("result")
            ).delete()
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def apply_filter(self, query):
        qs = []
        if "keyword" in self.request.POST:
            qs.append(
                Q(
                    servidor_substituido__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    servidor_substituido__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)
        query = query.filter(q) if q else query
        return query

    @login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST.get("sort", "data_inicio")
        direction = self.request.POST.get("dir", "DESC")

        order_by = "%s%s" % ("" if direction == "ASC" else "-", sort)

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 50))
        end = start + limit

        query = MovimentacaoSubstituicaoMembro.objects.filter().order_by(order_by)
        if self.request.POST.get("servidor", False) and self.request.POST.get(
            "afastamento", False
        ):
            query = query.filter(
                servidor_substituido__matricula=self.request.POST.get("servidor"),
                afastamento__pk=self.request.POST.get("afastamento"),
            ).order_by(order_by)

        query = self.apply_filter(query)
        obj.update(totalRows=query.count())

        query = query[start:end]
        result = self.retorno_list(query)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "afastamento",
                "publicacao_inativacao",
                "data_inicio",
                "publicacao_ativacao",
                "data_prevista",
                "publicacao_alteracao",
                "data_fim",
            ],
        },
    ]
)
class RHInativacaoCargoMembro(extjs.ExtCrud):
    class Form(forms.ModelForm):
        afastamento = AutoCompleteField(
            model=afastamento_models.BaseLicencaAfastamento,
            controller="AFAAfastamento",
            label="Afastamento",
        )
        posse = AutoCompleteField(
            model=MovimentacaoPosse,
            controller=RHMovimentacaoPosse,
            label="Posse",
            required=True,
        )
        publicacao_inativacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Documento Inativação",
            required=False,
        )
        publicacao_ativacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Documento Ativação",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = InativacaoCargoMembro
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def __init__(self, request, response, response_format=False):
        super(RHInativacaoCargoMembro, self).__init__(
            request, response, response_format
        )

        self.titles = {
            "PANEL": "%s" % self.Form.Meta.model._meta.verbose_name,
            "LIST": "Gerenciador de %s" % self.Form.Meta.model._meta.verbose_name,
            "NEW": "Novo(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "EDIT": "Editando um(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "DELETE": "Removendo um(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "FILTER": "NOT_DEFINED_IN_CONTROLLER",
        }

    def get_data(self, args=[]):
        obj = {
            "posse": None,
            "publicacao_inativacao": None,
            "publicacao_ativacao": None,
            "data_inicio": None,
            "data_fim": None,
            "data_prevista": None,
        }
        try:
            inativacao = InativacaoCargoMembro.objects.get(
                pk=int(self.request.POST.get("inativacao"))
            )
            obj.update({"posse": inativacao.posse})
            obj.update(
                {
                    "publicacao_inativacao": (
                        inativacao.publicacao_inativacao.pk
                        if inativacao.publicacao_inativacao
                        else None
                    )
                }
            )
            obj.update(
                {
                    "publicacao_ativacao": (
                        inativacao.publicacao_ativacao.pk
                        if inativacao.publicacao_ativacao
                        else None
                    )
                }
            )
            obj.update(
                {
                    "publicacao_alteracao": (
                        inativacao.publicacao_alteracao.pk
                        if inativacao.publicacao_alteracao
                        else None
                    )
                }
            )
            obj.update(
                {
                    "data_inicio": (
                        DateUtils.date_to_str(inativacao.data_inicio)
                        if inativacao.data_inicio
                        else None
                    )
                }
            )
            obj.update(
                {
                    "data_fim": (
                        DateUtils.date_to_str(inativacao.data_fim)
                        if inativacao.data_fim
                        else None
                    )
                }
            )
            obj.update(
                {
                    "data_prevista": (
                        DateUtils.date_to_str(inativacao.data_prevista)
                        if inativacao.data_prevista
                        else None
                    )
                }
            )
        except Exception as e:
            self.log.exception(e)
        self.response.write(json.encode(obj))

    def apply_filter(self, query):
        qs = []
        if "keyword" in self.request.POST:
            qs.append(
                Q(
                    afastamento__servidor__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    afastamento__servidor__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)
        query = query.filter(q) if q else query
        return query

    @login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}

        sort = self.request.POST.get("sort", "publicacao_inativacao__data_vigencia")
        direction = self.request.POST.get("dir", "DESC")

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 50))
        end = start + limit

        q = []

        if not self.request.POST.get("servidor", None) is None:
            q.append(
                Q(afastamento__servidor__matricula=self.request.POST.get("servidor"))
            )
        if not self.request.POST.get("afastamento", None) is None:
            q.append(Q(afastamento__pk=self.request.POST.get("afastamento")))

        qry = None
        for qn in q:
            qry = qn if qry is None else Q(qry & qn)

        query = (
            InativacaoCargoMembro.objects.filter(qry).order_by(
                "%s%s" % ("" if direction == "ASC" else "-", sort)
            )
            if qry is not None
            else InativacaoCargoMembro.objects.filter().order_by(
                "%s%s" % ("" if direction == "ASC" else "-", sort)
            )
        )
        query = self.apply_filter(query)
        obj.update(totalRows=query.count())

        query = query[start:end]

        result = []
        item = {}
        for inativacao in query:
            try:
                status = "Ativo"
                try:
                    if datetime.now().date() < inativacao.data_inicio:
                        status = "Agendado"
                    elif datetime.now().date() > inativacao.data_fim:
                        status = "Encerrado"
                except Exception:
                    pass
                item = {
                    "pk": inativacao.pk,
                    "data_inicio": (
                        DateUtils.date_to_str(inativacao.data_inicio)
                        if inativacao.data_inicio
                        else ""
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(inativacao.data_fim)
                        if inativacao.data_fim
                        else ""
                    ),
                    "data_prevista": (
                        DateUtils.date_to_str(inativacao.data_prevista)
                        if inativacao.data_prevista
                        else ""
                    ),
                    "posse": inativacao.posse,
                    "situacao": status,
                }
            except Exception as e:
                log.exception(e)
            else:
                result.append(item)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def delete(self, args=[]):
        obj = {"success": True, "msg": ""}
        try:
            InativacaoCargoMembro.objects.filter(
                pk=self.request.POST.get("result")
            ).delete()
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "criterio",
                "publicacao_movimentacao",
                "publicacao_alteracao",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoTitularizacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse, controller=RHMovimentacaoPosse, label="Posse atual"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoTitularizacao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "movimentacaopromocao_ptr",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "bond",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 300,
            },
            {
                "header": "Critério",
                "sortable": True,
                "dataIndex": "criterio",
                "key": "criterio",
                "width": 80,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 280,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 200,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Titularização",
        "LIST": "Gerenciador de Titularizações",
        "NEW": "Novo(a) Titularização",
        "EDIT": "Editando um(a)  Titularização",
        "DELETE": "Removendo um(a)  Titularização",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Concessão",
            "field": ["servidor", "publicacao_movimentacao", "texto"],
        },
    ]
)
class RHMovimentacaoConcessao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoConcessao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "data_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "toSearch": True,
                "width": 300,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Concessão",
        "LIST": "Gerenciador de Concessão",
        "NEW": "Novo(a) Concessão",
        "EDIT": "Editando um(a) Concessão",
        "DELETE": "Removendo um(a) Concessão",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Remoção",
            "field": [
                "servidor",
                "remocao",
                "publicacao_movimentacao",
                "servidor_permuta",
                "lotacao_destino",
                "data_vigencia",
                "texto",
            ],
        }
    ]
)
class RHMovimentacaoRemocao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        lotacao_destino = AutoCompleteField(
            model=Lotacao, controller=RHLotacao, label="Nova lotação", required=False
        )
        servidor_permuta = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Permutado", required=False
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoRemocao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "permuta",
                "data_alteracao",
                "movimento_origem",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Remoção",
                "sortable": True,
                "dataIndex": "remocao",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "toSearch": True,
                "width": 300,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Remoção",
        "LIST": "Gerenciador de Remoção",
        "NEW": "Novo(a) Remoção",
        "EDIT": "Editando um(a) Remoção",
        "DELETE": "Removendo um(a) Remoção",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Redistribuição",
            "field": [
                "movimentacao_posse",
                "quadro",
                "orgao_destino",
                "redistribuicao",
                "publicacao_movimentacao",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoRedistribuicao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        movimentacao_posse = AutoCompleteField(
            model=MovimentacaoPosse,
            father="RHMovimentacaoRedistribuicao",
            label="Posse",
        )
        orgao_destino = AutoCompleteField(
            model=UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Órgão destino",
        )
        quadro = AutoCompleteField(model=Quadro, controller=RHQuadro, label="Cargo")
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoRedistribuicao
            exclude = [
                "movimentacaopessoal_ptr",
                "servidor",
                "anotacao_geral",
                "data_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 160,
            },
            {
                "header": "Posse",
                "sortable": True,
                "dataIndex": "movimentacao_posse",
                "toSearch": True,
                "width": 100,
            },
            {
                "header": "Destino",
                "sortable": True,
                "dataIndex": "orgao_destino",
                "toSearch": True,
                "width": 100,
            },
            {
                "header": "Quadro",
                "sortable": True,
                "dataIndex": "quadro",
                "toSearch": True,
                "width": 100,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "toSearch": True,
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Redistribuição",
        "LIST": "Gerenciador de Redistribuição",
        "NEW": "Novo(a) Redistribuição",
        "EDIT": "Editando um(a) Redistribuição",
        "DELETE": "Removendo um(a) Redistribuição",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Descontos Legais",
            "field": [
                "servidor",
                "desconto",
                "parcela",
                "valor",
                "publicacao_movimentacao",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoDescontoLegal(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = MovimentacaoDescontoLegal
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral",
                "data_alteracao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
            },
            {
                "header": "Desconto",
                "sortable": True,
                "dataIndex": "desconto",
                "toSearch": False,
            },
            {
                "header": "Parcela",
                "sortable": True,
                "dataIndex": "parcela",
                "toSearch": False,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "quad_ano",
                "toSearch": False,
            },
            {
                "header": "Valor",
                "sortable": True,
                "dataIndex": "valor",
                "toSearch": False,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Descontos Legais",
        "LIST": "Gerenciador de Descontos Legais",
        "NEW": "Novo(a) Descontos Legais",
        "EDIT": "Editando um(a) Descontos Legais",
        "DELETE": "Removendo um(a) Descontos Legais",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHServidorLocalizacao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        localizacao = AutoCompleteField(
            model=Lotacao, controller=RHLotacao, label="Localização"
        )

        class Meta:
            model = ServidorLocalizacao
            exclude = [
                "data_cadastro",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Localização do Servidor",
        "LIST": "Gerenciador de Localização do Servidor",
        "NEW": "Novo(a) Localização do Servidor",
        "EDIT": "Editando um(a) Localização do Servidor",
        "DELETE": "Removendo um(a) Localização do Servidor",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def store(self, args=[]):
        obj = []
        try:
            if args:
                query = Lotacao.objects.filter(organograma=True, pai=args[0])
            else:
                query = Lotacao.objects.filter(organograma=True, pai=None)
            for lotacao in query:
                obj.append(
                    [
                        lotacao.pk,
                        lotacao,
                        Lotacao.objects.filter(
                            organograma=True, pai=lotacao.pk
                        ).count(),
                    ]
                )
        except Exception as e:
            self.log.exception(e)
            obj.append(["", ""])
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHServidorLotacao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor", required=True
        )
        movimentacao_posse = AutoCompleteField(
            model=MovimentacaoPosse,
            father="RHMovimentacaoDesligamento",
            label="Posse",
            required=True,
        )
        lotacao = AutoCompleteField(
            model=Lotacao,
            controller=RHLotacao,
            label="Lotação/Designação",
            required=True,
        )
        publicacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )

        class Meta:
            model = ServidorLotacao
            exclude = [
                "anotacao_geral_lotacao",
                "data_cadastro",
                "data_alteracao",
                "data_vigencia",
                "ativo",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
                "responsible",
                "from_substitution",
                "situation",
            ]

    titles = {
        "PANEL": "Lotação/Designação do Servidor",
        "LIST": "Gerenciador de Lotações dos Servidores",
        "NEW": "Novo(a) Lotação/Designação do Servidor",
        "EDIT": "Editando um(a)  Lotação/Designação do Servidor",
        "DELETE": "Removendo um(a)  Lotação/Designação do Servidor",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 240,
            },
            {
                "header": "Posse",
                "sortable": True,
                "dataIndex": "movimentacao_posse",
                "key": "movimentacao_posse",
                "width": 120,
            },
            {
                "header": "Lotação",
                "sortable": True,
                "dataIndex": "lotacao",
                "key": "lotacao",
                "width": 260,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 240,
            },
            {
                "header": "Designação",
                "sortable": True,
                "dataIndex": "designacao",
                "key": "designacao",
                "width": 70,
            },
            {
                "header": "Provisório",
                "sortable": True,
                "dataIndex": "provisorio",
                "key": "provisorio",
                "width": 70,
            },
            {
                "header": "Pleno",
                "sortable": True,
                "dataIndex": "responsible",
                "key": "responsible",
                "width": 70,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_vigencia_inicio",
                "key": "data_vigencia_inicio",
                "width": 100,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_vigencia_fim",
                "key": "data_vigencia_fim",
                "width": 100,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "key": "ativo",
                "width": 90,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_query(self):
        return super(RHServidorLotacao, self).get_query()

    def get_store(self, args=[]):
        obj = ["", ""]
        try:
            query = []
            if self.request.POST.get("pk", False):
                query = self.Form.Meta.model.objects.filter(
                    pk=self.request.POST.get("pk")
                )
            elif self.request.POST.get("matricula", False):
                query = self.Form.Meta.model.objects.filter(
                    matricula=self.request.POST.get("matricula")
                )
            obj = []
            for row in query:
                obj.append([row.id, row])
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Lotação do Servidor",
            "field": [
                "servidor",
                "movimentacao_posse",
                "lotacao",
                "publicacao",
                "data_vigencia_inicio",
                "data_vigencia_fim",
                "designacao",
                "provisorio",
                "responsible",
            ],
        },
    ]
)
class RHServidorLotacaoExpediente(RHServidorLotacao):
    class Form(RHServidorLotacao.Form):
        class Meta:
            model = ServidorLotacao
            exclude = [
                "anotacao_geral_lotacao",
                "data_cadastro",
                "data_alteracao",
                "data_vigencia",
                "ativo",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
                "from_substitution",
                "situation",
            ]

    def get_query_filtred(self, paginator=True):
        query = super(RHServidorLotacaoExpediente, self).get_query_filtred(
            paginator=paginator
        )
        return query.filter(servidor__tipo="M")


class BuildFile(threading.Thread):

    def __init__(self, user, method):
        threading.Thread.__init__(self)
        try:
            self.user = user
            self.method = method
        except Exception as e:
            print(e)

    def run(self):
        try:
            if self.method == "lotacaodistribuicao":
                file = self.gera_lotacao_distribuicao()
                subject = "Arquivo de Lotação e Distribuição"
            elif self.method == "servidorposse":
                file = self.gera_servidor_posse()
                subject = "Arquivo de Servidor(es) com Posse(s)"
            elif self.method == "servidorsemposse":
                file = self.gera_servidor_sem_posse()
                subject = "Arquivo de Servidor(es) sem Posse(s)"
        except Exception as e:
            print(e)
        self.envia_mail(file, subject)
        os.unlink(file)

    def gera_lotacao_distribuicao(self):
        try:
            lotacao_distribuicao = "%s/ld_%s.csv" % (CACHE_PATH, str(datetime.now()))
            file_lotacao_distribuicao = open(lotacao_distribuicao, "w")
            file_lotacao_distribuicao.write(self.get_lotacao_distribuicao())
            file_lotacao_distribuicao.close()
        except Exception as e:
            print(e)
        return lotacao_distribuicao

    def gera_servidor_posse(self):
        try:
            servidor_posse = "%s/sp_%s.csv" % (CACHE_PATH, str(datetime.now()))
            file_servidor_posse = open(servidor_posse, "w")
            file_servidor_posse.write(self.get_servidor_posse())
            file_servidor_posse.close()
        except Exception as e:
            print(e)
        return servidor_posse

    def gera_servidor_sem_posse(self):
        try:
            servidor_sem_posse = "%s/ssp_%s.csv" % (CACHE_PATH, str(datetime.now()))
            file_servidor_sem_posse = open(servidor_sem_posse, "w")
            file_servidor_sem_posse.write(self.get_servidor_sem_posse())
            file_servidor_sem_posse.close()
        except Exception as e:
            print(e)
        return servidor_sem_posse

    def envia_mail(self, file_name, subject):
        try:
            servidor = Servidor.objects.get(user=self.user)
        except Exception:
            pass
        email = "drtinfo@mp.to.gov.br"
        mensagem = """    Prezado(a) {nome_responsavel},

        Segue em anexo arquivo solicitado.

        Atenciosamente,
        DTI do MPE-TO

        Mensagem enviada {data_hora}
        Mensagem automática, favor não responda."""
        try:
            message = mensagem.format(
                nome_responsavel=servidor.pessoa_fisica.nome,
                data_hora=datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
            )
            from_email = email
            recipient_list = [
                self.user.email,
            ]
            email = EmailMessage(subject, message, from_email, recipient_list)
            file = open(file_name, "r")
            email.attach("%s.csv" % self.method, file.read(), "multipart/mixed")
            email.send()
        except Exception as e:
            print(e)

    def get_cargo(self, mov):
        from rh.gfp.models import MovimentacaoProgressao

        if not mov:
            return ""

        mov = MovimentacaoPosse.objects.get(pk=mov)
        try:
            mProg = MovimentacaoProgressao.objects.filter(
                movimentacao_posse=mov
            ).order_by("pk")[0]
        except MovimentacaoProgressao.DoesNotExist:
            mProg = None

        if mov.quadro.cargo.tipo_lei_cargo == "EF":
            if mov.quadro.especialidade is not None:
                cargo = "%s-%s - %s" % (
                    mov.quadro.cargo.nome,
                    mov.quadro.especialidade.sigla,
                    (mProg.salario if mProg else ""),
                )
            else:
                cargo = "%s - %s" % (
                    mov.quadro.cargo.nome,
                    (mProg.salario if mProg else ""),
                )
        else:
            cargo = "%s - %s" % (
                mov.quadro.cargo.nome,
                (mProg.salario if mProg else ""),
            )
        return cargo

    def get_classe(self, mov):
        from rh.gfp.models import MovimentacaoProgressao

        try:
            mProg = MovimentacaoProgressao.objects.filter(
                movimentacao_posse=mov
            ).order_by("pk")[0]
        except MovimentacaoProgressao.DoesNotExist:
            mProg = None

        if mProg:
            if mProg.salario:
                return mProg.salario.get_nivel_display()
        return ""

    def get_padrao(self, mov):
        from rh.gfp.models import MovimentacaoProgressao

        try:
            mProg = MovimentacaoProgressao.objects.filter(
                movimentacao_posse=mov
            ).order_by("pk")[0]
        except MovimentacaoProgressao.DoesNotExist:
            mProg = None

        if mProg:
            if mProg.salario:
                return mProg.salario.padrao
        return ""

    def get_tipo_lei_cargo(self, mov):
        return mov.quadro.cargo.tipo_lei_cargo

    def get_lotacao_distribuicao(self):
        texto_lotacao_distribuicao = (
            "Matricula|CPF|Nome|Cargo|Lotacao|Designacao|Cidade de lotacao|Situacao\n"
        )
        servidores = Servidor.objects.all().order_by("pessoa_fisica__nome")
        for s in servidores:
            situacao = "ATIVO" if s.ativo else "INATIVO"
            try:
                matricula = s.matricula if s.matricula is not None else ""
            except Exception as e:
                print(e)

            try:
                cpf = s.pessoa_fisica.cpf if s.pessoa_fisica.cpf is not None else ""
            except Exception as e:
                print(e)

            try:
                nome = s.pessoa_fisica.nome if s.pessoa_fisica.nome is not None else ""
            except Exception as e:
                print(e)

            cargo = ""
            try:
                m = MovimentacaoPosse.objects.filter(Q(servidor=s)).order_by(
                    "data_posse"
                )
                if len(m):
                    cargo = self.get_cargo(m[0])
            except Exception as e:
                print(e)

            sl = None
            try:
                sl = s.work_assignment.order_by("data_cadastro")
                if len(sl) > 0:
                    sl = sl[0]
                    if sl.lotacao is not None:
                        lotacao = (
                            "{0}".format(sl.lotacao.nome) if not sl.designacao else ""
                        )
                        designacao = (
                            "{0}".format(sl.lotacao.nome) if sl.designacao else ""
                        )
                        cidade_lotacao = "{0}/{1}".format(
                            sl.lotacao.localidade.nome,
                            sl.lotacao.localidade.estado.sigla,
                        )
            except Exception as e:
                print(e)
            try:
                texto = """{matricula}|{cpf}|{nome}|{cargo}|{lotacao}|{designacao}|{cidade_lotacao}|{situacao}\n""".format(
                    matricula=matricula,
                    cpf=cpf,
                    nome=nome.encode("utf-8"),
                    cargo=cargo.encode("utf-8"),
                    lotacao=lotacao.encode("utf-8"),
                    designacao=designacao.encode("utf-8"),
                    cidade_lotacao=cidade_lotacao.encode("utf-8"),
                    situacao=situacao.encode("utf-8"),
                )
                texto_lotacao_distribuicao = texto_lotacao_distribuicao + texto
            except Exception as e:
                texto_lotacao_distribuicao += "texto err"
                print(e)
        return texto_lotacao_distribuicao

    def get_servidor_posse(self):
        texto_info = (
            "Matricula|CPF|Nome|Ativo|Tipo|Situacao|Cargo|Tipo Lei Cargo|Classe|"
            "Padrao|Data Posse|Data Exercicio|Posse Ativa|Tipo Ato Movimentacao|"
            "Numero Ano|Data Expedicao|Lei Autorizativa|Veiculo Publicacao|Numero Publicacao|Data Publicacao|Data Vigencia\n"
        )
        for mov in MovimentacaoPosse.objects.all().order_by(
            "servidor__pessoa_fisica__nome"
        ):
            matricula = mov.servidor.matricula if mov.servidor.matricula else ""
            try:
                cpf = (
                    mov.servidor.pessoa_fisica.cpf
                    if mov.servidor.pessoa_fisica.cpf is not None
                    else ""
                )
            except Exception as e:
                print(e)

            nome = (
                mov.servidor.pessoa_fisica.nome
                if mov.servidor.pessoa_fisica.nome
                else ""
            )
            ativo = "Sim" if mov.servidor.ativo else "Não"
            tipo = mov.servidor.get_tipo_display() if mov.servidor.tipo else ""
            try:
                cargo = self.get_cargo(mov)
                classe = self.get_classe(mov)
                padrao = self.get_padrao(mov)
                tipo_lei_cargo = self.get_tipo_lei_cargo(mov)
            except Exception:
                cargo = ""
                classe = ""
                padrao = ""
                padrao = ""
            data_posse = DateUtils.date_to_str(mov.data_posse) if mov.data_posse else ""
            data_exercicio = (
                DateUtils.date_to_str(mov.data_exercicio) if mov.data_exercicio else ""
            )
            posse_ativa = "Sim" if mov.ativo else "Não"
            try:
                cls = RHServidoresToCSV()
                tipo_ato_movimentacao = TIPO_ATO_SICAP.get(
                    cls.get_tipo_ato(m.publicacao_movimentacao.tipo)
                )
            except Exception as e:
                self.log.exception(e)
                tipo_ato_movimentacao = ""
            #            tipo_ato_movimentacao = mov.publicacao_movimentacao.get_tipo_display() if mov.publicacao_movimentacao else ''
            numero_ano = (
                "%s%s"
                % (mov.publicacao_movimentacao.numero, mov.publicacao_movimentacao.ano)
                if mov.publicacao_movimentacao.numero
                and mov.publicacao_movimentacao.ano
                else ""
            )
            data_expedicao = (
                DateUtils.date_to_str(mov.publicacao_movimentacao.data_expedicao)
                if mov.publicacao_movimentacao.data_expedicao
                else ""
            )
            lei_autorizativa = (
                "Sim" if mov.publicacao_movimentacao.lei_autorizativa else "Não"
            )
            veiculo_publicacao = (
                mov.publicacao_movimentacao.get_veiculo_publicacao_display()
                if mov.publicacao_movimentacao.veiculo_publicacao
                else ""
            )
            numero_publicacao = (
                mov.publicacao_movimentacao.numero_publicacao
                if mov.publicacao_movimentacao.numero_publicacao
                else ""
            )
            data_publicacao = (
                DateUtils.date_to_str(mov.publicacao_movimentacao.data_publicacao)
                if mov.publicacao_movimentacao.data_publicacao
                else ""
            )
            data_vigencia = (
                DateUtils.date_to_str(mov.publicacao_movimentacao.data_vigencia)
                if mov.publicacao_movimentacao.data_vigencia
                else ""
            )
            situacao = format_situacao_funcional(mov.servidor.situacao_funcional_cache)
            try:
                texto = """{matricula}|{cpf}|{nome}|{ativo}|{tipo}|{situacao}|{cargo}|{tipo_lei_cargo}|{classe}|{padrao}|{data_posse}|{data_exercicio}|{posse_ativa}|{tipo_ato_movimentacao}|{numero_ano}|{data_expedicao}|{lei_autorizativa}|{veiculo_publicacao}|{numero_publicacao}|{data_publicacao}|{data_vigencia}\n""".format(
                    matricula=matricula,
                    cpf=cpf,
                    nome=nome.encode("utf-8"),
                    ativo=ativo.encode("utf-8"),
                    tipo=tipo.encode("utf-8"),
                    situacao=situacao.encode("utf-8"),
                    cargo=cargo.encode("utf-8"),
                    tipo_lei_cargo=tipo_lei_cargo,
                    classe=classe.encode("utf-8"),
                    padrao=padrao,
                    data_posse=data_posse,
                    data_exercicio=data_exercicio,
                    posse_ativa=posse_ativa.encode("utf-8"),
                    tipo_ato_movimentacao=tipo_ato_movimentacao.encode("utf-8"),
                    numero_ano=numero_ano,
                    data_expedicao=data_expedicao,
                    lei_autorizativa=lei_autorizativa.encode("utf-8"),
                    veiculo_publicacao=veiculo_publicacao.encode("utf-8"),
                    numero_publicacao=numero_publicacao,
                    data_publicacao=data_publicacao,
                    data_vigencia=data_vigencia,
                )
                texto_info = texto_info + texto
            except Exception as e:
                texto_info += "texto err"
                print(e)
        return texto_info

    def get_servidor_sem_posse(self):
        texto_info = """Matricula|CPF|Nome|Ativo|Tipo\n"""
        for s in Servidor.objects.all().exclude(
            pk__in=MovimentacaoPosse.objects.all().values("servidor__pk")
        ):
            matricula = s.matricula if s.matricula else ""
            try:
                cpf = s.pessoa_fisica.cpf if s.pessoa_fisica.cpf is not None else ""
            except Exception as e:
                print(e)

            nome = s.pessoa_fisica.nome if s.pessoa_fisica.nome else ""
            ativo = "Sim" if s.ativo else "Não"
            tipo = s.get_tipo_display() if s.tipo else ""
            try:
                texto = """{matricula}|{cpf}|{nome}|{ativo}|{tipo}\n""".format(
                    matricula=matricula,
                    cpf=cpf,
                    nome=nome.encode("utf-8"),
                    ativo=ativo.encode("utf-8"),
                    tipo=tipo.encode("utf-8"),
                )
                texto_info = texto_info + texto
            except Exception as e:
                texto_info += "texto err"
                print(e)
        return texto_info


class RHBuilderFile(extjs.ExtWidget):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.servidor.BuilderFile()")

    def gerar(self, args=[]):
        obj = {"success": True}
        try:
            thread = BuildFile(**{"user": self.request.user, "method": args[0]})
            thread.start()
        except Exception as err:
            log.exception(err)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHDeclaracaoAtividade(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        quadro = AutoCompleteField(model=Quadro, controller=RHQuadro, label="Cargo")
        lotacao = AutoCompleteField(
            model=Lotacao, controller=RHLotacao, label="Lotação estagiário"
        )

        class Meta:
            model = DeclaracaoAtividade
            exclude = [
                "texto",
                "anotacao_geral",
                "publicacao_movimentacao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
            ]

    titles = {
        "PANEL": "Declaração de Atividade",
        "LIST": "Gerenciador de Declaração de Atividade",
        "NEW": "Novo(a) Declaração de Atividade",
        "EDIT": "Editando um(a) Declaração de Atividade",
        "DELETE": "Removendo um(a) Declaração de Atividade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 250,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Exercício",
                "sortable": True,
                "dataIndex": "data_exercicio",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Turno",
                "sortable": True,
                "dataIndex": "turno",
                "toSearch": False,
                "width": 70,
            },
            {
                "header": "Encerramento",
                "sortable": True,
                "dataIndex": "data_encerramento",
                "toSearch": False,
                "width": 90,
            },
            {
                "header": "Lotação",
                "sortable": True,
                "dataIndex": "lotacao",
                "toSearch": False,
                "width": 350,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def csv(self, args=[]):
        query = self.get_query_filtred()
        texto = ""
        for q in query:
            texton = """{nome}|{cargo}|{exercicio}|{lotacao}\n""".format(
                nome=q.servidor,
                cargo=q.quadro,
                exercicio=DateUtils.date_to_str(q.data_exercicio),
                lotacao=q.lotacao,
            )
            texto += texton
        self.response["content-type"] = "text/javascript"
        self.response.write(texto)


class RHMolestia(extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = Molestia
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Moléstia",
        "LIST": "Gerenciador de Moléstia",
        "NEW": "Novo(a) Moléstia",
        "EDIT": "Editando um(a) Moléstia",
        "DELETE": "Removendo um(a) Moléstia",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHPeriodoRequisicao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = PeriodoRequisicao
            exclude = [
                "anotacao_geral",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Período de Requisição",
        "LIST": "Gerenciador de Período de Requisição",
        "NEW": "Novo(a) Período de Requisição",
        "EDIT": "Editando um(a) Período de Requisição",
        "DELETE": "Removendo um(a) Período de Requisição",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHDocumentoDigital(extjs.ExtCrud):
    class Form(forms.ModelForm):
        arquivo = FileUploadField(label="Arquivo", required=False)

        class Meta:
            model = DocumentoDigital
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Documento Digital",
        "LIST": "Gerenciador de Documento Digital",
        "NEW": "Novo(a) Documento Digital",
        "EDIT": "Editando um(a) Documento Digital",
        "DELETE": "Removendo um(a) Documento Digital",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": ["servidor", "resumo", "tipo_documento", "publicacao", "texto"],
        }
    ]
)
class RHAnotacaoCarreira(extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor", required=True
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        texto = forms.CharField(label="Texto", required=False, widget=forms.Textarea)

        class Meta:
            model = AnotacaoCarreira
            exclude = [
                "numero_processo",
                "data_documento",
                "anotacaogeral_ptr",
                "numero_documento",
                "indireto",
                "data_portaria_inicio",
                "ativa",
                "movimento_origem",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anotação de Carreira",
        "LIST": "Gerenciador de Anotação de Carreira",
        "NEW": "Novo(a) Anotação de Carreira",
        "EDIT": "Editando um(a) Anotação de Carreira",
        "DELETE": "Removendo um(a) Anotação de Carreira",
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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Resumo",
                "sortable": True,
                "dataIndex": "resumo",
                "key": "resumo",
                "width": 120,
            },
            {
                "header": "Texto",
                "sortable": True,
                "dataIndex": "texto",
                "key": "texto",
                "width": 350,
            },
            {
                "header": "Tipo Documento",
                "sortable": True,
                "dataIndex": "tipo_documento",
                "key": "tipo_documento",
                "width": 180,
            },
            {
                "header": "Data do Documento",
                "sortable": True,
                "dataIndex": "data_documento",
                "key": "data_documento",
                "width": 140,
            },
            {
                "header": "Número Documento",
                "sortable": True,
                "dataIndex": "numero_documento",
                "key": "numero_documento",
                "width": 140,
            },
            {
                "header": "Data Portaria Início",
                "sortable": True,
                "dataIndex": "data_portaria_inicio",
                "key": "data_portaria_inicio",
                "width": 140,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 320,
            },
            {
                "header": "Ativa",
                "sortable": True,
                "dataIndex": "ativa",
                "key": "ativa",
                "width": 70,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "criterio",
                "publicacao_movimentacao",
                "publicacao_alteracao",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoPromocao(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse, controller=RHMovimentacaoPosse, label="Posse atual"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        class Meta:
            model = MovimentacaoPromocao
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "data_desligamento",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Critério",
                "sortable": True,
                "dataIndex": "criterio",
                "key": "criterio",
                "width": 120,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Promoção",
        "LIST": "Gerenciador de Promoções",
        "NEW": "Novo(a) Promoção",
        "EDIT": "Editando um(a) Promoção",
        "DELETE": "Removendo um(a) Promoção",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse_anterior",
                "quadro",
                "data_posse",
                "data_exercicio",
                "criterio",
                "servidor_permuta",
                "lotacao_destino",
                "publicacao_movimentacao",
                "publicacao_alteracao",
                "anota",
                "texto",
            ],
        },
    ]
)
class RHMovimentacaoRemocaoMembro(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_movimentacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )
        quadro = AutoCompleteField(
            model=Quadro, controller=RHQuadro, label="Novo Cargo"
        )
        posse_anterior = AutoCompleteField(
            model=MovimentacaoPosse, controller=RHMovimentacaoPosse, label="Posse atual"
        )
        publicacao_alteracao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação revogação",
            required=False,
        )

        lotacao_destino = AutoCompleteField(
            model=Lotacao, controller=RHLotacao, label="Nova lotação", required=False
        )
        servidor_permuta = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Permutado", required=False
        )

        class Meta:
            model = MovimentacaoRemocaoMembro
            exclude = [
                "movimentacaopessoal_ptr",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "anotacao_geral",
                "servidor",
                "data_alteracao",
                "movimentacaoposse_ptr",
                "ativo",
                "tipo_movcarreira",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "data_desligamento",
                "bond",
                "public_concurrence",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Cargo",
                "sortable": True,
                "dataIndex": "quadro",
                "key": "quadro",
                "width": 180,
            },
            {
                "header": "Critério",
                "sortable": True,
                "dataIndex": "criterio",
                "key": "criterio",
                "width": 120,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Remoção de Membro",
        "LIST": "Gerenciador de Remoções de Membros",
        "NEW": "Novo(a) Remoção de Membro",
        "EDIT": "Editando um(a) Remoção de Membro",
        "DELETE": "Removendo um(a) Remoção de Membro",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class RHProrrogacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = Prorrogacao
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Prorrogação",
        "LIST": "Gerenciador de Prorrogação",
        "NEW": "Novo(a) Prorrogação",
        "EDIT": "Editando um(a) Prorrogação",
        "DELETE": "Removendo um(a) Prorrogação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {"title": "Dados", "field": ["conselho_regional", "pessoa_fisica"]},
    ]
)
class RHProfissionalSaude(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        profissional_saude = AutoCompleteField(
            model=ProfissionalSaude,
            controller=RHPessoaFisicaSimplificadoSemDocumento,
            label="Profissional de Saúde",
            required=False,
        )

        class Meta:
            model = ProfissionalSaude
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Profissional de Saúde",
        "LIST": "Gerenciador de Profissional de Saúde",
        "NEW": "Novo(a) Profissional de Saúde",
        "EDIT": "Editando um(a) Profissional de Saúde",
        "DELETE": "Removendo um(a) Profissional de Saúde",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "tipo",
                "quantidade",
                "data_inicio",
                "data_fim",
                "publicacao",
                "texto",
            ],
        },
    ]
)
class RHCargaHoraria(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        servidor = AutoCompleteField(model=Servidor, controller=RHServidor)
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = CargaHoraria
            exclude = [
                "anotacao_geral",
                "anota",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Tipo",
                "sortable": True,
                "dataIndex": "tipo",
                "key": "tipo",
                "width": 80,
            },
            {
                "header": "Quantidade",
                "sortable": True,
                "dataIndex": "quantidade",
                "key": "quantidade",
                "width": 80,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Publicação Movimentação",
                "sortable": True,
                "dataIndex": "publicacao_movimentacao",
                "key": "publicacao_movimentacao",
                "width": 240,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Carga Horária",
        "LIST": "Gerenciador de Carga Horária",
        "NEW": "Novo(a) Carga Horária",
        "EDIT": "Editando um(a) Carga Horária",
        "DELETE": "Removendo um(a) Carga Horária",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }
