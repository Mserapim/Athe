# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import slugify

from contrib import extjs
from contrib.decorator import deprecated
from contrib.utils import get_json_engine, getLogger
from rh.const import INDICATIVO, MESES, QUADRIMESTRE_CHOICES, SIM_NAO, TIPO_LEI_CARGO
from rh.constants_functional_situations import SITUACAO_FUNCIONAL
from rh.models import Cargo, Lotacao, Servidor, Especialidade
from rh.views import CustomAutocomplete, RHServidor
from standard.models import Choice
from standard.views import AutoCompleteField

log = getLogger(__name__)
json = get_json_engine()


class RHRelatorioServidor(extjs.ExtReportBuild):

    report_src = "/pgjadmin/reports/rh/servidores"

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatórios"}

    class Form(forms.Form):
        relatorio = forms.ChoiceField(
            label="Servidores", choices=((1, "Servidores por Nome"),)
        )


class RHPrintFichaFuncional(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/servidor/ficha_funcional/ficha_funcional"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/ficha_funcional/",
        },
        {
            "nome": "upload_dir",
            "tipo": "String",
            "valor": settings.EXTERNAL_UPLOAD_STORE_DIR,
        },
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Ficha Funcional"}

    def get_generated_filename(self):
        return (
            "ficha_funcional_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            controller="RHServidor",
            required=False,
            display_field="description",
            value_field="id",
        )
        todas_anot = forms.ChoiceField(
            label="Sim para todas opções abaixo", choices=SIM_NAO, required=False
        )
        endereco = forms.ChoiceField(label="Endereço", choices=SIM_NAO, required=False)
        dependente = forms.ChoiceField(
            label="Dependente", choices=SIM_NAO, required=False
        )
        anot_geral = forms.ChoiceField(
            label="Anotação Geral", choices=SIM_NAO, required=False
        )
        anot_afastamento = forms.ChoiceField(
            label="Anotação Afastamento", choices=SIM_NAO, required=False
        )
        anot_ausencia = forms.ChoiceField(
            label="Anotação Ausência", choices=SIM_NAO, required=False
        )
        anot_carreira = forms.ChoiceField(
            label="Anotação Carreira", choices=SIM_NAO, required=False
        )
        anot_elogio = forms.ChoiceField(
            label="Anotação Elogio", choices=SIM_NAO, required=False
        )
        anot_enquadramento = forms.ChoiceField(
            label="Anotação Enquadramento", choices=SIM_NAO, required=False
        )
        anot_evento = forms.ChoiceField(
            label="Anotação Evento", choices=SIM_NAO, required=False
        )
        anot_falta = forms.ChoiceField(
            label="Anotação Falta", choices=SIM_NAO, required=False
        )
        anot_ferias = forms.ChoiceField(
            label="Anotação Férias", choices=SIM_NAO, required=False
        )
        anot_folga_eleitoral = forms.ChoiceField(
            label="Anotação Folga Eleitoral", choices=SIM_NAO, required=False
        )
        anot_gratificacao = forms.ChoiceField(
            label="Anotação Gratificação", choices=SIM_NAO, required=False
        )
        anot_licenca = forms.ChoiceField(
            label="Anotação Licença", choices=SIM_NAO, required=False
        )
        anot_pena_disciplinar = forms.ChoiceField(
            label="Anotação Pena Disciplinar", choices=SIM_NAO, required=False
        )
        anot_plantao = forms.ChoiceField(
            label="Anotação Plantão", choices=SIM_NAO, required=False
        )
        anot_recesso = forms.ChoiceField(
            label="Anotação Recesso", choices=SIM_NAO, required=False
        )
        anot_remocao = forms.ChoiceField(
            label="Anotação Remoção", choices=SIM_NAO, required=False
        )
        anot_tempo_dobro = forms.ChoiceField(
            label="Anotação Tempo Dobro", choices=SIM_NAO, required=False
        )
        anot_tempo_servico = forms.ChoiceField(
            label="Anotação Tempo Serviço/Contribuição", choices=SIM_NAO, required=False
        )
        anot_transposicao = forms.ChoiceField(
            label="Anotação Transposição", choices=SIM_NAO, required=False
        )
        anot_viagem = forms.ChoiceField(
            label="Anotação Viagem", choices=SIM_NAO, required=False
        )

    def autocomplete(self, args=[]):

        # TODO: Realizar tarefa relatada no ticket #184

        obj = {"result": []}
        if len(args) > 0 and args[0] in ("Servidor"):
            if args[0] == "Servidor":
                for row in Servidor.objects.filter(
                    Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                    | Q(matricula__icontains=self.request.POST["query"])
                ):
                    obj["result"].append({"id": row.pk, "description": str(row)})
            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(RHPrintFichaFuncional, self).autocomplete(args)


def get_choice_standard(ch):
    choice = list(ch)
    choice.insert(0, ("t", "TODOS"))
    return choice


def get_choice_models(md):
    choice = []
    choice.insert(0, ("t", "TODOS"))
    for row in md:
        choice.append([row.pk, str(row)])
    return choice


class RHPrintListagemServidores(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/servidor/lista_servidor/servidor"
    filename = "listagem_servidores.pdf"

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Listagem dos Servidores"}

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/lista_servidor/",
        }
    ]

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintListagemServidores",
            label="Servidor",
            controller=RHServidor,
            required=True,
            display_field="description",
            value_field="id",
        )
        cargo = forms.ChoiceField(
            label="Cargo",
            choices=get_choice_models(Cargo.objects.all().order_by("nome")),
        )
        especialidade = forms.ChoiceField(
            label="Especialidade",
            choices=get_choice_models(Especialidade.objects.all().order_by("nome")),
        )
        lotacao = forms.ChoiceField(
            label="Lotação/Designação",
            choices=get_choice_models(Lotacao.objects.all().order_by("nome")),
        )
        ativo = forms.ChoiceField(
            label="Ativo", choices=(("t", "TODOS"), ("s", "SIM"), ("n", "NÃO"))
        )
        situacao = forms.ChoiceField(
            label="Situação", choices=get_choice_standard(SITUACAO_FUNCIONAL)
        )
        tipo = forms.ChoiceField(
            label="Tipo", choices=get_choice_standard(TIPO_LEI_CARGO)
        )
        tipo_servidor = forms.ChoiceField(
            label="Tipo do Servidor", choices=get_choice_standard(INDICATIVO)
        )
        data_exercicio_inicio = forms.DateField(label="Data Exercício Início")
        data_exercicio_final = forms.DateField(label="Data Exercício Final")

    def autocomplete(self, args=[]):

        # TODO: Realizar tarefa relatada no ticket #184

        obj = {"result": []}
        if len(args) > 0 and args[0] in ("Servidor"):
            if args[0] == "Servidor":
                obj["result"].insert(0, ({"id": "t", "description": "TODOS"}))
                for row in Servidor.objects.filter(
                    Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                    | Q(matricula__icontains=self.request.POST["query"])
                ):
                    obj["result"].append({"id": row.pk, "description": str(row)})
            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(RHPrintListagemServidores, self).autocomplete(args)


class RHPrintCargosEmComissao(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/servidor/cargos_em_comissao/cargos_em_comissao"
    filename = "cargos_em_comissao.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/cargos_em_comissao/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Cargos em Comissão"}

    class Form(forms.Form):
        pass


class RHPrintDataNascimento(extjs.ExtReportBuild):

    report_src = (
        "/to/mpe/rh/servidor/lista_servidor/data_nascimento/servidor_data_nascimento"
    )
    filename = "servidor_data_nascimento.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/lista_servidor/data_nascimento/",
        }
    ]

    titles = {
        "TITLE": "Relatórios",
        "SUB_TITLE": "Data de Nascimento dos Servidores - Gerado em Ordem Alfabética",
    }

    class Form(forms.Form):
        mes = forms.ChoiceField(label="Mês", choices=get_choice_standard(MESES))


@deprecated
class RHCarteiraFuncional(extjs.ExtWidget):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.relatorio.CarteiraFuncional()")


class RHPrintCarteiraFuncional(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/carteira_funcional/carteira_4_1"
    filename = "CarteiraFuncional.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/carteira_funcional/",
        },
        {
            "nome": "storagedir",
            "tipo": "String",
            "valor": settings.EXTERNAL_UPLOAD_STORE_DIR,
        },
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Geração de Carteira Funcional"}

    class Form(forms.Form):
        servidores = forms.ModelMultipleChoiceField(
            queryset=Servidor.objects.all(), label="Servidores"
        )


class RHPrintParticipacaoClimaOrganizacional(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/pesquisa_organizacional/pequisa_organizacional_membros"
    filename = "ParticipacaoPesquisaClimaOrganizacional.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/pesquisa_organizacional/",
        }
    ]

    titles = {
        "TITLE": "Relatórios",
        "SUB_TITLE": "Participação na Pesquisa sobre o Clima Organizacional",
    }

    class Form(forms.Form):
        pass


class RHPrintPublicacao(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/publicacao/publicacao"
    filename = "Publicacao.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/publicacao/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatório de Publicações"}

    class Form(forms.Form):
        tipo_publicacao = forms.ChoiceField(
            label="Tipo",
            choices=get_choice_standard(
                Choice.get_choices_for(
                    "rh",
                    "TIPO_DOCUMENTO",
                    query_dict={
                        "value__in": [
                            1,
                            2,
                            3,
                            4,
                            5,
                            6,
                            7,
                            8,
                            9,
                            10,
                            11,
                            12,
                            13,
                            14,
                            96,
                            97,
                            98,
                            99,
                        ]
                    },
                )
            ),
            required=False,
        )
        numero = forms.CharField(label="Número", max_length=200, required=False)
        ano = forms.CharField(label="Ano", max_length=200, required=False)
        veiculo_publicacao = forms.ChoiceField(
            label="Veículo / Publicação",
            choices=get_choice_standard(
                Choice.get_choices_for("rh", "VEICULO_PUBLICACAO")
            ),
            required=False,
        )
        numero_publicacao = forms.CharField(
            label="Número / Publicação", max_length=200, required=False
        )
        interno = forms.ChoiceField(
            label="Interno", choices=get_choice_standard(SIM_NAO), required=False
        )
        lei_autorizativa = forms.ChoiceField(
            label="Lei autorizativa",
            choices=get_choice_standard(SIM_NAO),
            required=False,
        )
        interessado = forms.CharField(
            label="Interessado", max_length=200, required=False
        )
        observacao = forms.CharField(
            label="Assunto / Observação", max_length=200, required=False
        )
        expedicao_inicio = forms.DateField(
            label="Data de Expedição - Início", required=False
        )
        expedicao_final = forms.DateField(
            label="Data de Expedição - Final", required=False
        )
        vigencia_inicio = forms.DateField(
            label="Data de Vigência - Início", required=False
        )
        vigencia_final = forms.DateField(
            label="Data de Vigência - FInal", required=False
        )
        publicacao_inicio = forms.DateField(
            label="Data de Publicação - Início", required=False
        )
        publicacao_final = forms.DateField(
            label="Data de Publicação - Final", required=False
        )


class RHPrintMovimentacaoSicap(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/mov_sicap/movimentacoes"
    filename = "MovimentacaoSicap.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/mov_sicap/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Movimentações do SICAP AP"}

    class Form(forms.Form):
        quadrimestre = forms.ChoiceField(
            label="Quadrimestre", choices=QUADRIMESTRE_CHOICES, required=False
        )
        ano = forms.CharField(label="Ano", max_length=4, required=True)


class RHPrintOnlyMovimentacaoSicap(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/sicap/moviementacoes/sicap_movimentacoes"
    filename = "movimentacao-sicapap.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/sicap/moviementacoes/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Movimentações do SICAP AP"}

    class Form(forms.Form):
        quadrimestre = forms.ChoiceField(
            label="Quadrimestre", choices=QUADRIMESTRE_CHOICES, required=False
        )
        ano = forms.CharField(label="Ano", max_length=4, required=True)

    def get_generated_filename(self):
        return "movimentacao-sicapap-%s%s.pdf" % (
            self.request.GET["quadrimestre"],
            self.request.GET["ano"],
        )


class RHPrintServidoresSicap(extjs.ExtReportBuild):

    # - tipo_cargo = ['CM', 'EF']

    report_src = "/to/mpe/rh/sicap/servidores/servidor"
    filename = "movimentacao-sicapap.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/sicap/servidores/",
        }
    ]

    titles = {
        "TITLE": "Relatórios",
        "SUB_TITLE": "Relação atual de servidores do SICAP AP",
    }

    class Form(forms.Form):
        tipo_cargo = forms.ChoiceField(
            label="Tipo do Cargo", choices=("CM", "EF"), required=False
        )
        quadrimestre = forms.ChoiceField(
            label="Quadrimestre", choices=QUADRIMESTRE_CHOICES, required=False
        )
        ano = forms.CharField(label="Ano", max_length=4, required=True)

    def get_generated_filename(self):
        return "movimentacao-sicapap-%s%s.pdf" % (
            self.request.GET["quadrimestre"],
            self.request.GET["ano"],
        )


@deprecated
class RHRelatorioViagem(CustomAutocomplete, extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/relatorio_viagem_servidor"

    titles = {"TITLE": "Relatório de Viagem", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        try:
            s = Servidor.objects.get(pk=int(self.request.GET.get("servidor")))
        except Servidor.DoesNotExist:
            name = "relatorio-viagem"
        else:
            name = "relatorio-viagem-%s" % s.matricula
        return "%s.pdf" % slugify(name)

    def run_report(self, args=[]):
        try:
            s = Servidor.objects.get(pk=int(self.request.POST.get("servidor")))
            self.report_src = (
                "/to/mpe/portalservidor/relatorio_viagem_membro"
                if s.tipo == "M"
                else "/to/mpe/portalservidor/relatorio_viagem_servidor"
            )
        except Servidor.DoesNotExist:
            pass

        return extjs.ExtReportBuild.run_report(self, args)

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="RHRelatorioViagem",
            display_field="description",
            value_field="id",
        )


class RHLotacaoHierarquia(CustomAutocomplete, extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/lotacao/lotacao"
    filename = "lotacao-hierarquia.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/lotacao/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Hierarquia de Lotações"}

    class Form(forms.Form):
        lotacao = forms.ModelChoiceField(
            label="Lotação", queryset=Lotacao.objects.all(), required=False
        )


@deprecated
class RHRequerimentoExoneracao(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/exoneracao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {
        "TITLE": "Requisição de Exoneração",
        "SUB_TITLE": "Requisição de Exoneração",
    }

    def get_generated_filename(self):
        return (
            "requisicao-exoneracao-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


@deprecated
class RHRequerimentoVacancia(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/vacancia"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {"TITLE": "Requisição de Vacância", "SUB_TITLE": "Requisição de Vacância"}

    def get_generated_filename(self):
        return (
            "requisicao-vacancia-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


class RHServidorPorLotacao(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/lotacao/servidor_por_lotacao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/lotacao/",
        }
    ]

    titles = {
        "TITLE": "Servidor por Lotação",
        "SUB_TITLE": "Lista de Servidores por Lotação",
    }

    def get_generated_filename(self):
        return "servidores-por-lotacao.pdf"

    class Form(forms.Form):
        pass


@deprecated
class RHSolicitacaoCarteiraFuncional(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/solicitacao_identidade_funcional"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {
        "TITLE": "Servidor por Lotação",
        "SUB_TITLE": "Lista de Servidores por Lotação",
    }

    def get_generated_filename(self):
        return "solicitacao-identidade-funcional.pdf"

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


class RHPrintServidorCargo(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/servidor/lista_servidor/servidor_cargo"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/lista_servidor/",
        }
    ]

    titles = {
        "TITLE": "Servidor por Cargo",
        "SUB_TITLE": "Lista de Servidores por Cargo",
    }

    def get_generated_filename(self):
        return "servidor-cargo.pdf"

    class Form(forms.Form):
        cargo = forms.ChoiceField(
            label="Cargo",
            choices=get_choice_models(Cargo.objects.all().order_by("nome")),
        )
        ativo = forms.ChoiceField(
            label="Ativo", choices=(("t", "TODOS"), ("s", "SIM"), ("n", "NÃO"))
        )
        tipo = forms.ChoiceField(
            label="Tipo do Servidor", choices=get_choice_standard(INDICATIVO)
        )


class RHPrintMovimentacaoSicapAp(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/mov_sicap_geral/movimentacoes"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/mov_sicap_geral/",
        }
    ]

    titles = {
        "TITLE": "Movimentações do Sicap AP",
        "SUB_TITLE": "Lista de Movimentações do Sicap AP",
    }

    def get_generated_filename(self):
        return "movimentacoes-sicapap.pdf"

    class Form(forms.Form):
        data_vigencia = forms.DateField(label="Data final de vigência")


class RHPrintTransparenciaFolhaServidores(extjs.ExtReportBuild):

    report_src = "/to/mpe/portaltransparencia/rh/extrato_folha_servidores"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portaltransparencia/rh/",
        }
    ]

    titles = {
        "TITLE": "Extrato da Folha de Servidores",
        "SUB_TITLE": "Folha de Servidores",
    }

    def get_generated_filename(self):
        return "rh_transparencia_folha_servidores.pdf"

    class Form(forms.Form):
        mes = forms.ChoiceField(label="Mês", choices=get_choice_standard(MESES))
        ano = forms.CharField(label="Ano", max_length=4, required=True)


@deprecated
class RHPrintBolsaEstudo(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/solicitacao_bolsa_estudo"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {"TITLE": "Requerimento Bolsa de Estudo", "SUB_TITLE": "Bolsa de Estudo"}

    def get_generated_filename(self):
        return "requerimento-bolsa-estudo.pdf"

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


@deprecated
class RHPrintDependenteExclusao(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/exclusao_dependentes"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {
        "TITLE": "Requerimento para Exclusão de Dependente",
        "SUB_TITLE": "Exclusão de Dependente",
    }

    def get_generated_filename(self):
        return "requerimento-dependente-exclusao.pdf"

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


@deprecated
class RHPrintAntecipacao13Salario(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_adiantamento13salario"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/portalservidor/",
        }
    ]

    titles = {
        "TITLE": "Antecipação de 13º Salário",
        "SUB_TITLE": "Antecipação de 13º Salário",
    }

    def get_generated_filename(self):
        return (
            "requerimento-antecipacao-13salario-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )


@deprecated
class RHRequerimentoAuxilioEspecial(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/auxilio_especial"
    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    titles = {
        "TITLE": "Requisição de Auxílio Especial",
        "SUB_TITLE": "Requisição de Auxílio Especial",
    }

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        return (
            "requisicao-auxilio-especial-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )


@deprecated
class RHDeclaracaoParentesco(extjs.ExtReportBuild):

    report_src = "/to/mpe/portalservidor/declaracao_ato105_2014"
    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    titles = {
        "TITLE": "Declaração Relação de Parentesco",
        "SUB_TITLE": "Declaração Relação de Parentesco",
    }

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            father="RHPrintFichaFuncional",
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        return (
            "declaracao_parentesco-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )
