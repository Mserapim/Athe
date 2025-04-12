# -*- coding: utf-8 -*-

import codecs
import os
import shutil
import threading
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.db.models import Max, Q
from django.http import QueryDict
from django.template.defaultfilters import slugify

from contrib.decorator import deprecated, login_required
from contrib.helpers import clear_to_ascii
from contrib.extjs import ExtFileBuild, ExtReportBuild, ExtWidget
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import get_json_engine, getLogger, make_zipfile
from engine.models import TaskSession
from engine.mq.models import Task
from ged.models import Arquivo as FileGED
from rh.gfp import models as gfp_models
from rh.gfp.dirf.models import Declaracao, Dialect
from rh.gfp.planoconta.models import Plano
from rh.gfp.previdencia.sefip import File as SEFIPFile
from rh.gfp.previdencia.task.igeprev import sisprev_web
from rh.gfp.rais import File as RAISFile
from rh.gfp.tasks import process_credit_file, gerar_cnab_consignados_task
from rh.gfp.views import CustomAutocomplete
from rh.gfp.models import ContraCheque, Evento
from rh.models import (
    Cargo,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    PessoaFisica,
    Servidor,
    UnidadeAdministrativa,
    SocialSecurityEmployee,
)
from rh.pensao.models import PensaoMorte
from standard.models import Configuration
from standard.views import AutoCompleteField
from contrib.utils import DateUtils
from standard.models import Choice

json = get_json_engine()

log = getLogger(__name__)


class GFPPrecisaValidar(ExtReportBuild):

    report_src = "/to/mpe/gfp/chancela/main"

    titles = {"TITLE": "Para Validação", "SUB_TITLE": "Necessita de validação"}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/chancela/"},
    ]

    class Form(forms.Form):
        folha = forms.ModelChoiceField(
            queryset=gfp_models.Folha.objects.filter(fechado=False, ci=False),
            label="Folha",
        )
        level = forms.ChoiceField(
            choices=((1, "FOLHA DE PAGAMENTO"), (2, "CONTROLE INTERNO")), label="Nível"
        )


class GFPCriticas(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/gfp/critica/main"

    titles = {
        "TITLE": "Critias da Folha de Pagamento",
        "SUB_TITLE": "Impressão do Criticas da Folha de Pagamento",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/criticas/"}
    ]

    class Form(forms.Form):
        folha = AutoCompleteField(
            label="Folha de Pagamento",
            model=gfp_models.Folha,
            father="GFPCriticas",
            display_field="description",
            value_field="id",
        )


class GFPChancela(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/gfp/chancela/main"

    titles = {
        "TITLE": "Chancelas que deve ser validadas",
        "SUB_TITLE": "Lista de contracheques com pendencias de chancela",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/chancela/"}
    ]

    class Form(forms.Form):
        folha_tipo = forms.ModelChoiceField(
            label="Tipo da Folha", queryset=gfp_models.FolhaTipo.objects.all()
        )
        periodo = forms.ModelChoiceField(
            label="Período", queryset=gfp_models.Periodo.objects.all()
        )
        tipo = forms.ChoiceField(
            label="Nível",
            choices=(("1", "RECURSOS HUMANOS"), ("2", "CONTROLE INTERNO")),
            required=True,
        )

    def get_generated_filename(self):
        return "pendencias-da-folha-de-pagamento.pdf"


class GFPCarreiraSalario(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/gfp/carreira/main"

    titles = {"TITLE": "Carreira", "SUB_TITLE": "Informações de carreira de Efetivos"}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/carreira/"}
    ]

    filename = "tabela_progressao_salarial.pdf"

    class Form(forms.Form):
        cargo = AutoCompleteField(label="Cargo", model=Cargo, father="GFPCriticas")


class GFPReportUsuario(ExtWidget):
    @login_required("JSON")
    def json(self, args=None):
        args = args or []
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.employee.Manager")')

    @login_required("JSON")
    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "folhatipo":
            obj = self.store_folhatipo(args)
        elif args[0] == "periodo":
            obj = self.store_periodo(args)
        elif args[0] == "ano":
            obj = self.store_ano(args)
        elif args[0] == "complemento":
            obj = self.store_complemento(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def paycheck_by_period_and_type(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            servidor = Servidor.objects.get(pk=self.request.POST["servidor"])
            periodo = gfp_models.Periodo.objects.get(pk=self.request.POST["periodo"])
            period_christmas = None
            if periodo.mes == 12:
                period_christmas = gfp_models.Periodo.objects.filter(
                    mes=13, ano=periodo.ano
                ).first()

            folhatipo = self.request.POST["folhatipo"]
            folhatipo = (
                gfp_models.FolhaTipo.objects.get(pk=folhatipo)
                if folhatipo and folhatipo.isnumeric()
                else folhatipo
            )

            complemento = self.request.POST["complemento"]
            complemento = (
                Choice.objects.get(pk=complemento)
                if complemento and complemento.isnumeric()
                else complemento
            )
            if isinstance(folhatipo, gfp_models.FolhaTipo) and isinstance(
                complemento, Choice
            ):
                paycheckid = gfp_models.ContraCheque.objects.filter(
                    servidor__pessoa_fisica=servidor.pessoa_fisica,
                    folha__periodo=periodo,
                    folha__tipo_folha=folhatipo,
                    folha__complement=complemento.value,
                )
            elif isinstance(folhatipo, gfp_models.FolhaTipo) and complemento == "N":
                paycheckid = gfp_models.ContraCheque.objects.filter(
                    servidor=servidor,
                    folha__periodo=periodo,
                    folha__tipo_folha=folhatipo,
                    folha__complement=0,
                )
            elif isinstance(folhatipo, gfp_models.FolhaTipo) and (
                not complemento or complemento == "T"
            ):
                paycheckid = gfp_models.ContraCheque.objects.filter(
                    servidor__pessoa_fisica=servidor.pessoa_fisica,
                    folha__periodo=periodo,
                    folha__tipo_folha=folhatipo,
                )
            else:
                paycheckid = gfp_models.ContraCheque.objects.filter(
                    servidor__pessoa_fisica=servidor.pessoa_fisica,
                    folha__periodo__in=[periodo, period_christmas],
                )
            if self.request.POST.get("pvf_restrict", None):
                paycheckid = paycheckid.filter(folha__available_pvf=True)
            if paycheckid:
                list_paycheck = ", ".join([str(cc.pk) for cc in paycheckid])
                obj.update(pk=list_paycheck)
            else:
                raise Exception(
                    "Não foi localizada folha disponível para o período informado."
                )
        except Exception as e:
            self.log.exception(e)
            obj["message"] = str(e)
            obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def store_folhatipo(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            folhatipo = gfp_models.FolhaTipo.objects.all()
            if "servidor" in self.request.POST:
                servidor = Servidor.objects.get(pk=self.request.POST["servidor"])
                _period = gfp_models.Periodo.objects.get(
                    pk=self.request.POST["periodo"]
                )
                folhatipo = folhatipo.filter(
                    folhas__lancamentos__servidor__pessoa_fisica=servidor.pessoa_fisica,
                    folhas__periodo=_period,
                ).distinct()
            if self.request.POST.get("pvf_restrict", None):
                folhatipo = folhatipo.filter(folhas__available_pvf=True).distinct()
            obj["totalRows"] = folhatipo.count()
            obj["result"].append({"codigo": "T", "descricao": str("TODOS")})
            for ft in folhatipo:
                obj["result"].append({"codigo": ft.pk, "descricao": str(ft.titulo)})
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(
                {"codigo": "", "descricao": "Erro realizando consulta."}
            )
        return obj

    @login_required("JSON")
    def store_complemento(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            if (
                "servidor" in self.request.POST
                and "folhatipo" in self.request.POST
                and self.request.POST["folhatipo"] != "T"
            ):
                servidor = Servidor.objects.get(pk=self.request.POST["servidor"])
                _period = gfp_models.Periodo.objects.get(
                    pk=self.request.POST["periodo"]
                )
                folhatipo = gfp_models.FolhaTipo.objects.get(
                    pk=self.request.POST["folhatipo"]
                )
                folhas = gfp_models.Folha.objects.filter(
                    lancamentos__servidor__pessoa_fisica=servidor.pessoa_fisica,
                    periodo=_period,
                    tipo_folha=folhatipo,
                ).distinct()

                if self.request.POST.get("pvf_restrict", None):
                    folhas = folhas.filter(available_pvf=True).distinct()
                complement_pks = [f.complement for f in folhas]
                choices = Choice.objects.filter(
                    name="COMPLEMENT_PAYROLL", app_label="gfp"
                ).filter(value__in=complement_pks)
                obj["totalRows"] = choices.count()
                obj["result"].append({"codigo": "T", "descricao": str("TODOS")})
                obj["result"].append(
                    {"codigo": "N", "descricao": str(folhatipo.titulo)}
                )
                for ch in choices:
                    obj["result"].append({"codigo": ch.pk, "descricao": str(ch.label)})
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(
                {"codigo": "", "descricao": "Erro realizando consulta."}
            )
        return obj

    @login_required("JSON")
    def store_periodo(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            if "servidor" in self.request.POST:
                servidor = Servidor.objects.get(pk=self.request.POST["servidor"])
                periodo = (
                    gfp_models.Periodo.objects.filter(
                        folhas__status__in=[1, 2, 3, 4],
                        folhas__lancamentos__servidor__pessoa_fisica=servidor.pessoa_fisica,
                    )
                    .distinct()
                    .order_by("-ano", "-mes")
                )
                if self.request.POST.get("pvf_restrict", None):
                    periodo = (
                        periodo.filter(folhas__available_pvf=True)
                        .distinct()
                        .order_by("-ano", "-mes")
                    )
                obj["totalRows"] = periodo.count()
                for pe in periodo:
                    obj["result"].append({"codigo": pe.pk, "descricao": str(pe)})
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(
                {"codigo": "", "descricao": "Erro realizando consulta."}
            )
        return obj

    @login_required("JSON")
    def store_ano(self, args=[]):
        try:
            choices = [
                {"codigo": ano, "descricao": str(ano)}
                for ano in range(1997, (datetime.now().year + 1))
            ]
            obj = {"totalRows": len(choices), "result": choices}
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(
                {"codigo": "", "descricao": "Erro realizando consulta."}
            )
        return obj

    @login_required("JSON")
    def employee(self, args=None):
        args = args or []

        result = {"message": "Nothing done yet", "success": False}

        try:
            result.update(
                {
                    "employee": {
                        "name": self.request.user.servidor.pessoa_fisica.nome,
                        "id": self.request.user.servidor.pk,
                        "type": self.request.user.servidor.tipo,
                        "naturalPersonId": self.request.user.servidor.pessoa_fisica.pk,
                        "storageDir": settings.EXTERNAL_UPLOAD_STORE_DIR,
                    },
                }
            )
        except Exception as e:
            log.exception(e)
            result.update({"message": str(e)})
        else:
            result.update(
                {"message": "Operação realizada com sucesso", "success": True}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))


@deprecated
class GFPAlistamentoEleitoral(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/alistamento_eleitoral"

    titles = {"TITLE": "Alistamento Eleitoral", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "alistamento_eleitoral_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPAlistamentoEleitoral",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPAuxilioNatalidade(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/auxilio_natalidade"

    titles = {"TITLE": "Auxilio Natalidade", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "auxilio_natalidade_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPAuxilioNatalidade",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPCasamento(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/casamento"

    titles = {"TITLE": "Casamento", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "casamento_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPCasamento",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPConcessaoNascimentoFilho(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/concessao_nascimento_filho"

    titles = {"TITLE": "Concessão Nascimento Filho", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "concessao_nascimento_filho_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPConcessaoNascimentoFilho",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPConclusaoTcc(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/conclusao_tcc"

    titles = {"TITLE": "Conclusão TCC", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "conclusao_tcc_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPConclusaoTcc",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPDoacaoSangue(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/doacao_sangue"

    titles = {"TITLE": "Doação Sangue", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "doacao_sangue_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPDoacaoSangue",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPFalecimentoFamilia(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/falecimento_familia"

    titles = {"TITLE": "Falecimento Família", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "falecimento_familia_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPFalecimentoFamilia",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPFerias(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/ferias"

    titles = {"TITLE": "Férias", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "ferias_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor", model=Servidor, father="GFPFerias"
        )


@deprecated
class GFPFeriasMembro(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/ferias_membro"

    titles = {"TITLE": "Férias Membro", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "ferias_membro_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPFeriasMembro",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPInclusaoDependentes(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/inclusao_dependentes"

    titles = {"TITLE": "Inclusão Dependentes", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "inclusao_dependentes_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPInclusaoDependentes",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPLicencaEleitoral(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/licenca_eleitoral"

    titles = {"TITLE": "Licença Eleitoral", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "licenca_eleitoral_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPLicencaEleitoral",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPLicencaJuntaMedica(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/licenca_junta_medica"

    titles = {"TITLE": "Licença Junta Médica", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "licenca_junta_medica_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPLicencaJuntaMedica",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPLicencaTratamentoSaude(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/licenca_tratamento_saude"

    titles = {"TITLE": "Licença Tratamento Saúde", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "licenca_tratamento_saude_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPLicencaTratamentoSaude",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoProcurador(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_procurador"

    titles = {"TITLE": "Requerimento Procurador", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_procurador_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoProcurador",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoCracha(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/confeccaocracha"

    titles = {"TITLE": "Requerimento Crachá", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_cracha_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoCracha",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoPromotorProcurador(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_promotor_procurador"

    titles = {"TITLE": "Requerimento Promotor Procurador", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_promotor_procurador_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoPromotorProcurador",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoRessarcimentoDespesa(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_ressarcimento_despesa"

    titles = {"TITLE": "Requerimento Ressarcimento Despesa", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_ressarcimento_despesa_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoRessarcimentoDespesa",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoIndenizacaoOficialDiligencia(CustomAutocomplete, ExtReportBuild):

    report_src = (
        "/to/mpe/portalservidor/requerimento_indenizacao_transporte_oficial_diligencias"
    )

    titles = {
        "TITLE": "Requerimento Indenização Oficial de Diligências",
        "SUB_TITLE": "",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_indenizacao_transporte_oficial_diligencias_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoIndenizacaoOficialDiligencia",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoSalarioFamilia(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_salario_familia"

    titles = {"TITLE": "Requerimento Salário Família", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_salario_familia_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoSalarioFamilia",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoServidorAdministrativo(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_servidor_administrativo"

    titles = {"TITLE": "Requerimento Servidor Administrativo", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_servidor_administrativo_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoServidorAdministrativo",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPRequerimentoValeTransporte(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/requerimento_vale_transporte"

    titles = {"TITLE": "Requerimento Vale Transporte", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "requerimento_vale_transporte_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoValeTransporte",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPSolicitacaoDiarias(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/solicitacao_diarias_servidor"

    titles = {"TITLE": "Solicitação Diarias", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        try:
            s = Servidor.objects.get(pk=int(self.request.GET.get("servidor")))
        except:
            name = "solicitacao-diaria"
        else:
            name = "solicitacao-diaria-%s" % s.matricula

        return "%s.pdf" % slugify(name)

    def run_report(self, args=[]):
        try:
            s = Servidor.objects.get(pk=int(self.request.POST.get("servidor")))
            self.report_src = (
                "/to/mpe/portalservidor/solicitacao_diarias_membros"
                if s.tipo == "M"
                else "/to/mpe/portalservidor/solicitacao_diarias_servidor"
            )
        except:
            pass

        return ExtReportBuild.run_report(self, args)

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPSolicitacaoDiarias",
            display_field="description",
            value_field="id",
        )


class GFPComprovanteRendimentosServidor(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/gfp/comprovanterendimentos/comprovante"

    titles = {
        "TITLE": "Comprovante de Redimentos",
        "SUB_TITLE": "Comprovante de Rendimentos",
    }

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/gfp/comprovanterendimentos/",
        }
    ]

    def get_generated_filename(self):
        cpf = ""
        if "servidor" in self.request.GET:
            cpf = Servidor.objects.get(
                pk=self.request.GET.get("servidor")
            ).pessoa_fisica.cpf
        else:
            cpf = PessoaFisica.objects.get(
                pk=int(self.request.GET["pessoa_fisica"])
            ).cpf

        return "comprovante-rendimentos-%s.pdf" % cpf

    class Form(forms.Form):
        pessoa_fisica = AutoCompleteField(
            model=PessoaFisica,
            father="GFPComprovanteRendimentosServidor",
            required=True,
            display_field="description",
            value_field="id",
            label="Pessoa Física",
        )
        declaracao = AutoCompleteField(
            model=Declaracao,
            required=True,
            label="Declaração",
        )

    def autocomplete(self, args=[]):
        query = PessoaFisica.objects.exclude(dirfs_pessoa_fisica=None).filter(
            nome__icontains=self.request.POST.get("query")
        )

        obj = {"result": [{"id": row.pk, "description": str(row)} for row in query]}
        self.response.write(json.encode(obj))

    def run_report(self, args=[]):
        if "servidor" in self.request.POST:
            _dict_ = {}
            for key in self.request.POST:
                if len(self.request.POST.getlist(key)) > 1:
                    _dict_.update({key: self.request.POST.getlist(key)})
                else:
                    _dict_.update({key: self.request.POST.get(key)})
            if isinstance(_dict_.get("servidor"), str):
                _dict_.update(
                    pessoa_fisica=PessoaFisica.objects.get(
                        servidor=_dict_.get("servidor")
                    ).pk
                )
            elif isinstance(_dict_.get("servidor"), (list, tuple, set)):
                _dict_.update(
                    pessoa_fisica=[
                        PessoaFisica.objects.get(servidor=servidor_id).pk
                        for servidor_id in _dict_.get("servidor", [])
                    ]
                )
            self.request.POST = QueryDict("", True)
            self.request.POST.update(_dict_)

        return ExtReportBuild.run_report(self, args)

    @login_required("JSON")
    def get_store(self, args=[]):
        from rh.gfp.dirf.models import Declaracao

        obj = {"totalRows": 0, "result": []}
        try:
            servidor = Servidor.objects.get(pk=int(self.request.POST.get("servidor")))
        except Exception as e:
            obj.update(
                result=[{"codigo": "", "descricao": "Erro realizando consulta."}]
            )
            self.log.exception(e)
        else:
            obj.update(
                result=[
                    {"pk": dec.pk, "nome": "%s.%s" % (dec.ano_base, dec.mv)}
                    for dec in Declaracao.objects.filter(
                        published=True,
                        demonstrativos__pessoa_fisica=servidor.pessoa_fisica,
                    )
                    .annotate(mv=Max("demonstrativos__version"))
                    .order_by("-ano_base", "-retificadora")
                    .distinct()
                ]
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPResumoGeralEventos(ExtReportBuild):

    report_src = "/to/mpe/gfp/geraleventos/geraleventosmain"

    titles = {
        "TITLE": "Resumo Geral de Eventos",
        "SUB_TITLE": "Resumo geral de Eventos por Folha de Pagamento",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/geraleventos/"}
    ]

    class Form(forms.Form):
        ano = forms.ChoiceField(
            label="Ano",
            choices=[
                (p.get("ano"), p.get("ano"))
                for p in gfp_models.Periodo.objects.order_by("-ano")
                .values("ano")
                .distinct()
            ],
        )
        mes = forms.ChoiceField(
            label="Mês",
            choices=(
                (1, "JANEIRO"),
                (2, "FEVEREIRO"),
                (3, "MARÇO"),
                (4, "ABRIL"),
                (5, "MAIO"),
                (6, "JUNHO"),
                (7, "JULHO"),
                (8, "AGOSTO"),
                (9, "SETEMBRO"),
                (10, "OUTUBRO"),
                (11, "NOVEMBRO"),
                (12, "DEZEMBRO"),
                (13, "13° TERCEIRO"),
            ),
            required=True,
        )
        folha_tipo = forms.ModelChoiceField(
            label="Tipo da Folha", queryset=gfp_models.FolhaTipo.objects.all()
        )
        evento = AutoCompleteField(
            model=gfp_models.Evento,
            father="GFPPrintContracheque",
            label="Evento",
            required=True,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        try:
            e = gfp_models.Evento.objects.get(pk=int(self.request.GET.get("evento")))
        except:
            name = "resumo-geral-evento"
        else:
            name = "resumo-geral-evento-evento-%(evento_numero)s" % {
                "evento_numero": str(e.numero)
            }

        return "%s.pdf" % slugify(name)

    def run_report(self, args=[]):
        try:
            self.log.debug(self.request.POST)
            if "folha" in self.request.POST and self.request.POST.get("folha"):
                f = gfp_models.Folha.objects.get(pk=self.request.POST.get("folha"))
                self.log.debug(self.params)
                self.params.append(
                    {"nome": "ano", "valor": f.periodo.ano, "tipo": "string"}
                )
                self.params.append(
                    {"nome": "mes", "valor": f.periodo.mes, "tipo": "string"}
                )
                self.params.append(
                    {"nome": "folha_tipo", "valor": f.tipo_folha.pk, "tipo": "string"}
                )
                self.log.debug(self.params)
        except Exception as e:
            self.log.exception(e)

        return ExtReportBuild.run_report(self, args)


class GFPResumoGeralEventosConsignatario(ExtReportBuild):

    report_src = "/to/mpe/gfp/consignatarioeventos/geralconsignatarioeventosmain"

    titles = {
        "TITLE": "Resumo Geral de Eventos",
        "SUB_TITLE": "Resumo geral de Eventos por Folha de Pagamento",
    }

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/gfp/consignatarioeventos/",
        }
    ]

    class Form(forms.Form):
        ano = forms.ChoiceField(
            label="Ano",
            choices=[
                (p.get("ano"), p.get("ano"))
                for p in gfp_models.Periodo.objects.order_by("-ano")
                .values("ano")
                .distinct()
            ],
        )
        mes = forms.ChoiceField(
            label="Mês",
            choices=(
                (1, "JANEIRO"),
                (2, "FEVEREIRO"),
                (3, "MARÇO"),
                (4, "ABRIL"),
                (5, "MAIO"),
                (6, "JUNHO"),
                (7, "JULHO"),
                (8, "AGOSTO"),
                (9, "SETEMBRO"),
                (10, "OUTUBRO"),
                (11, "NOVEMBRO"),
                (12, "DEZEMBRO"),
                (13, "13° TERCEIRO"),
            ),
            required=True,
        )
        folha_tipo = forms.ModelChoiceField(
            label="Tipo da Folha", queryset=gfp_models.FolhaTipo.objects.all()
        )
        plano = AutoCompleteField(
            model=Plano,
            father="PCPlano",
            label="Consignatário",
            required=True,
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        name = "resumo-geral-evento-por-consignatario"

        return "%s.pdf" % slugify(name)

    def run_report(self, args=[]):
        try:
            if "folha" in self.request.POST and self.request.POST.get("folha"):
                f = gfp_models.Folha.objects.get(pk=self.request.POST.get("folha"))
                self.params.append(
                    {"nome": "ano", "valor": f.periodo.ano, "tipo": "string"}
                )
                self.params.append(
                    {"nome": "mes", "valor": f.periodo.mes, "tipo": "string"}
                )
                self.params.append(
                    {"nome": "folha_tipo", "valor": f.tipo_folha.pk, "tipo": "string"}
                )
                self.params.append(
                    {
                        "nome": "plano",
                        "valor": self.request.POST.get("plano"),
                        "tipo": "string",
                    }
                )

        except Exception as e:
            self.log.exception(e)

        return ExtReportBuild.run_report(self, args)


@deprecated
class GFPFormularioAuxilioCreche(ExtReportBuild):

    report_src = "/to/mpe/portalservidor/auxilio_creche"

    titles = {"TITLE": "Auxilio Creche", "SUB_TITLE": "Formulário de Auxílio Creche"}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPFichaFinanceira",
            display_field="description",
            value_field="id",
        )

    def get_generated_filename(self):
        try:
            p = Servidor.objects.get(pk=int(self.request.GET.get("servidor")))
        except:
            name = "requerimento-auxilio-creche"
        else:
            name = "requerimento-auxilio-creche-%(servidor)s" % {"servidor": str(p)}

        return "%s.pdf" % slugify(name)


@deprecated
class GFPSolicitaDiariaAcrecimo80(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/solicitacao_diarias_servidor_acrescimo80"

    titles = {
        "TITLE": "Requerimento Acréscimo",
        "SUB_TITLE": "SERVIDORES - REQUERIMENTO DE DIÁRIA COM ACRÉSCIMO DE 80%",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "solicitacao-acrescimo80pct-diaria-%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPRequerimentoCracha",
            display_field="description",
            value_field="id",
        )


class GFPPrintContrachequePensionista(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/gfp/contracheque/contracheque_pensionista"

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/contracheque/"}
    ]

    titles = {
        "TITLE": "Contra Cheque",
        "SUB_TITLE": "Impressão do Contra Cheque para Pensionista",
    }

    def autocomplete(self, args=[]):
        if len(args) > 0:
            model = args[0]

            if model == "PessoaFisica":
                query = PensaoMorte.objects.filter(
                    Q(servidor__matricula__icontains=self.request.POST.get("query"))
                    | Q(
                        servidor__pessoa_fisica__nome__icontains=self.request.POST.get(
                            "query"
                        )
                    )
                    | Q(
                        servidor__pessoa_fisica__cpf__icontains=self.request.POST.get(
                            "query"
                        )
                    )
                    | Q(pensionista__nome__icontains=self.request.POST.get("query"))
                    | Q(pensionista__cpf__icontains=self.request.POST.get("query"))
                )

                obj = {
                    "result": [
                        {"id": row.pensionista.pk, "description": str(row)}
                        for row in query
                    ]
                }
                self.response.write(json.encode(obj))
            else:
                log.info("not found")
                CustomAutocomplete.autocomplete(self, args)
        else:
            pass

    class Form(forms.Form):
        pensionista = AutoCompleteField(
            model=PessoaFisica,
            father="GFPPrintContrachequePensionista",
            label="Pensionista",
            required=True,
            display_field="description",
            value_field="id",
        )
        folhatipo = forms.ModelChoiceField(
            label="Tipo da Folha", queryset=gfp_models.FolhaTipo.objects.all()
        )
        periodo = forms.ModelChoiceField(
            label="Período", queryset=gfp_models.Periodo.objects.all()
        )


class GFPReportMargem(ExtReportBuild):

    report_src = "/to/mpe/gfp/margemconsignada/margemconsignadalivre"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/gfp/margemconsignada/",
        }
    ]

    class Form(forms.Form):
        folha = AutoCompleteField(
            label="Folha de Pagamento",
            model=gfp_models.Folha,
            father="GFPReportMargem",
            display_field="description",
            value_field="id",
        )


@deprecated
class GFPAPD(CustomAutocomplete, ExtReportBuild):

    report_src = "/to/mpe/portalservidor/relatorio_apd"

    titles = {"TITLE": "APD", "SUB_TITLE": ""}

    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/portalservidor/"}
    ]

    def get_generated_filename(self):
        return (
            "apd_%s.pdf"
            % Servidor.objects.get(pk=int(self.request.GET["servidor"])).matricula
        )

    class Form(forms.Form):
        servidor = AutoCompleteField(
            label="Servidor",
            model=Servidor,
            father="GFPAPD",
            display_field="description",
            value_field="id",
        )


class GFPConfigDirf(CustomAutocomplete, ExtReportBuild):

    class Form(forms.Form):
        dialect = AutoCompleteField(
            label="Ano Calendário",
            model=Dialect,
            # controller="DIRFDialect",
            # display_field='description',
            # value_field='id'
            required=True,
        )

    report_src = "/to/mpe/gfp/dirf/dirfmain"

    titles = {"TITLE": "Configuração DIRF", "SUB_TITLE": ""}

    params = [{"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/gfp/dirf/"}]

    def get_generated_filename(self):
        return "dirf_configuracao_%s.pdf" % slugify(
            Dialect.objects.get(pk=int(self.request.GET["dialect"])).nome
        )


class GFPDependenteAuxilioCreche(ExtReportBuild):

    report_src = "/to/mpe/gfp/dependentes/servidor_dependentes"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/gfp/dependentes/servidor_dependentes/",
        }
    ]


class GFPReturnFile(ExtFileBuild):
    """docstring for GFPReturnFile"""

    _generated_filename = "retorno_mpto.txt"

    encoding_out = "utf-8"

    NL_END_OF_FILE = False

    def __init__(self, *args, **kargs):
        log.debug("INIT GFPReturnFile")
        super(GFPReturnFile, self).__init__(*args, **kargs)
        self.uuid = uuid.uuid1().hex
        if "period" in self.request.POST:
            self.period = gfp_models.Periodo.objects.get(
                id=self.request.POST.get("period")
            )
        if "payroll" in self.request.POST:
            self.payroll = gfp_models.Folha.objects.get(
                id=self.request.POST.get("payroll")
            )

    @property
    def tmp_dir(self):
        return os.path.join(settings.UPLOAD_STORE_DIR, "gfp", self.uuid)

    @property
    def generated_filename(self):
        return self._generated_filename

    def get_generate_filename(self):
        return self._generated_filename

    def create_file(self, file_path, objs=[], xml=False):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        if xml:
            objs.write(file_path, encoding=self.encoding_out, xml_declaration=True)
        else:
            with codecs.open(file_path, "w", self.encoding_out) as fd:
                fd.writelines(objs)
                if self.NL_END_OF_FILE:
                    fd.write("\n")

        return file_path

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def clear_tmpdir(self):
        shutil.rmtree(self.tmp_dir)


class GFPReturnViabillize2(GFPReturnFile):
    """docstring for GFPReturnViabillize"""

    _generated_filename = "viabillize_mpto.zip"

    def __init__(self, *args, **kargs):
        log.debug("INIT GFPReturnViabillize")
        super(GFPReturnViabillize2, self).__init__(*args, **kargs)
        self.query_entries = gfp_models.FolhaEvento.objects.filter(
            evento__carater__in=[6, 7],
            contracheque__folha__periodo=self.period,
            contracheque__folha__tipo_folha__margem__gt=0,
            contracheque__folha__status__in=[4, 3],
            contracheque__pensioner=None,
        ).order_by("contracheque__servidor", "contracheque__folha")

    def get_generate_filename(self):
        return "viabillize_mpto_%02d%04d.zip" % (self.period.mes, self.period.ano)

    def registration_events(self):
        # ANEXO I - CADASTRO DE EVENTOS
        lines = []
        log.debug("REGISTRATION EVENTS")
        for e in gfp_models.Evento.objects.filter(
            Q(carater__in=[6, 7]) & Q(active=True)
        ):
            lines.append(
                "%s|%s|%s|%s|%s|%s|%s\r\n"
                % (
                    e.numero,
                    "",
                    e.titulo,
                    ("True" if e.porcentagem else "False"),
                    (e.get_base_de_calculo_display() if e.porcentagem else ""),
                    (("%s%%" % e.porcentagem) if e.porcentagem else ""),
                    ("True" if e.carater == 6 else "False"),
                )
            )
        # print 'OK',
        # print 'CRIANDO ARQUIVO [CADASTRO DE EVENTOS]... ',
        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_eventos.txt")

        return self.create_file(file_path, lines)
        # print 'OK'

    def functional_register(self):
        # ANEXO II - CADASTRO FUNCIONAL
        lines = []
        resgistrations = []

        # print 'COLETANDO INFORMAÇÔES...',
        log.debug("FUNCTIONAL REGISTER")
        # for fe in self.query_entries:
        #     cc = fe.contracheque
        for cc in gfp_models.ContraCheque.objects.filter(
            folha__periodo=self.period, folha__tipo_folha__margem__gt=0, pensioner=None
        ).order_by("servidor"):
            payroll = cc.folha
            _id = "%s%s" % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura)
            if _id not in resgistrations:
                resgistrations.append(_id)
                # if 0 < payroll.tipo_folha.margem <= 100:
                # for cc in payroll.paychecks.all().order_by('servidor'):
                try:
                    endereco = (
                        cc.servidor.pessoa_fisica.address.all()[0]
                        if cc.servidor.pessoa_fisica.address.exists()
                        else None
                    )
                    desligamento = {"data": "", "motivo": ""}
                    if payroll.tipo_folha.margem < 100:
                        # Folhas que podem ser totalmente consignadas, normalmente
                        if not cc.servidor.get_posses_ativas(cc.folha.date_range.last):
                            mov_desligamento = cc.servidor.posses.latest(
                                "data_desligamento"
                            ).desligamento
                            desligamento["data"] = mov_desligamento.data_desligamento
                            desligamento["motivo"] = (
                                mov_desligamento.get_opcao_display()
                            )
                    elif payroll.tipo_folha.margem == 100:
                        data_limite = date.today()
                        for fe1 in cc.lancamentos.filter(evento__tipo="P", prazo__gt=0):
                            dt = date(
                                fe1.contracheque.folha.periodo.ano,
                                fe1.contracheque.folha.periodo.mes,
                                5,
                            ) + relativedelta(months=int(fe1.prazo - fe1.qnt))
                            if dt > data_limite:
                                data_limite = dt
                        desligamento["data"] = data_limite
                        desligamento["motivo"] = "FIM DO BENEFÍCIO"

                    if cc.servidor.is_acordo_cooperacao:
                        type_employee = "EFETIVO/REQUISITADO"
                    elif cc.servidor.is_efetivo:
                        type_employee = "EFETIVO"
                    else:
                        type_employee = "COMISSIONADO"

                    lines.append(
                        "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\r\n"
                        % (
                            cc.servidor.pessoa_fisica,
                            _id,
                            cc.servidor.data_exercicio,
                            cc.servidor.pessoa_fisica.cpf,
                            cc.servidor.pessoa_fisica.rg,
                            cc.servidor.pessoa_fisica.rg_orgao,
                            cc.servidor.pessoa_fisica.rg_uf,
                            cc.servidor.pessoa_fisica.rg_data_expedicao,
                            (
                                cc.servidor.pessoa_fisica.phone.all()[0]
                                if cc.servidor.pessoa_fisica.phone.all()
                                else "(63) 3216-7600"
                            ),
                            endereco.logradouro if endereco else "",
                            endereco.numero if endereco else "",
                            endereco.bairro if endereco else "",
                            (
                                endereco.municipio.nome
                                if endereco and endereco.municipio
                                else ""
                            ),
                            endereco.cep if endereco else "",
                            (
                                endereco.municipio.estado.sigla
                                if endereco
                                and endereco.municipio
                                and endereco.municipio.estado
                                else ""
                            ),
                            cc.folha.tipo_folha,
                            type_employee,
                            cc.cargo_eletivo
                            or cc.cargo_comissao
                            or cc.cargo_efetivo
                            or "",
                            cc.lotacao or "",
                            cc.situacao_previdenciaria or "",
                            desligamento["data"],
                            desligamento["motivo"],
                            cc.margem_consignada_total,
                            "%02d%04d" % (cc.folha.periodo.mes, cc.folha.periodo.ano),
                        )
                    )
                except (
                    MovimentacaoPosse.DoesNotExist,
                    MovimentacaoDesligamento.DoesNotExist,
                ) as e:
                    # print 'ERRO: %s' % cc
                    log.exception(e)
                except Exception as e:
                    log.exception(e)
                    raise e
        # print 'OK',
        # print 'CRIANDO ARQUIVO [CADASTRO FUNCIONAL - %s]... ' % folha.tipo_folha.abreviatura,
        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_funcional.txt")

        return self.create_file(file_path, lines)
        # print 'OK'

    def bases_events(self):
        # ANEXO IV - CADASTRO DE BASES
        lines = []
        matriculas = {}
        log.debug("BASES EVENTS")
        # print 'COLETANDO INFORMAÇÔES...',
        # for cc in payroll.paychecks.order_by('servidor'):
        for fe in self.query_entries.filter(
            Q(evento__carater__in=[6]) & Q(evento__porcentagem__gt=0)
        ):
            if fe.contracheque.servidor.matricula not in matriculas:
                matriculas[fe.contracheque.servidor.matricula] = []
            if (
                fe.evento.base_de_calculo
                not in matriculas[fe.contracheque.servidor.matricula]
            ):
                matriculas[fe.contracheque.servidor.matricula].append(
                    fe.evento.base_de_calculo
                )
                try:
                    lines.append(
                        "%s|%s|%s|%s\r\n"
                        % (
                            "%02d%04d"
                            % (
                                fe.contracheque.folha.periodo.mes,
                                fe.contracheque.folha.periodo.ano,
                            ),
                            "%s%s"
                            % (
                                fe.contracheque.servidor.matricula,
                                fe.contracheque.folha.tipo_folha.abreviatura,
                            ),
                            fe.evento.get_base_de_calculo_display(),
                            fe.valor_base,
                        )
                    )
                except Exception as e:
                    raise e

        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_bases.txt")
        # file_path = os.path.join(self.tmp_dir, dir_path, 'cadastro_bases_%s.txt' % payroll.tipo_folha)

        return self.create_file(file_path, lines)

    def returned_events(self, query_entries=[]):
        # ANEXO III - ARQUIVO RETORNO
        lines = []
        # print 'COLETANDO INFORMAÇÔES...',
        # for cc in payroll.paychecks.all().order_by('servidor'):
        for fe in self.query_entries:
            try:
                lines.append(
                    "%s|%s|%s|%s|%s|%s\r\n"
                    % (
                        "%02d%04d"
                        % (
                            fe.contracheque.folha.periodo.mes,
                            fe.contracheque.folha.periodo.ano,
                        ),
                        fe.evento.numero,
                        "%s%s"
                        % (
                            fe.servidor.matricula,
                            fe.contracheque.folha.tipo_folha.abreviatura,
                        ),
                        int(fe.parcela) if fe.evento.carater == 7 else 1,
                        int(fe.prazo),
                        fe.valor,
                    )
                )
            except Exception as e:
                raise e

        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        # file_path = os.path.join(self.tmp_dir, dir_path, 'arquivo_retorno_%s.txt' % payroll.tipo_folha)
        file_path = os.path.join(self.tmp_dir, "arquivo_retorno.txt")

        return self.create_file(file_path, lines)

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s" % (user, self.period, self.tmp_dir)
            )
            log.debug("PERIOD: %s" % self.period)
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivos Viabillize - %02d/%04d"
                % (self.period.mes, self.period.ano)
            )
            # for payroll in gfp_models.Folha.objects.filter(
            #   periodo=self.period, tipo_folha__margem__gt=0, status__in=[4, 3]):
            #     log.debug('>>>>>>>>>>>> %s ' % payroll)
            #     if not os.path.exists(self.tmp_dir):
            #         os.makedirs(self.tmp_dir)
            self.registration_events()
            self.functional_register()
            self.bases_events()
            self.returned_events()
            # else:
            #     log.debug('<<<<<<<<< NENHUMA FOLHA PROCESSADA PARA ENVIAR...')

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)

            zipfile = make_zipfile(
                os.path.join(self.tmp_dir, "..", self.get_generate_filename()),
                self.tmp_dir,
                False,
            )
            log.debug(">>>>>>>>>>>> ZIP GERADO: %s" % zipfile)
            gedfile = FileGED.from_filepath(zipfile, user, "application/zip", 1)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPReturnViabillize3(GFPReturnFile):
    """docstring for GFPReturnViabillize"""

    _generated_filename = "viabillize_mpto.zip"

    def __init__(self, *args, **kargs):
        log.debug("INIT GFPReturnViabillize")
        super(GFPReturnViabillize3, self).__init__(*args, **kargs)
        self.query_entries = gfp_models.FolhaEvento.objects.filter(
            evento__carater__in=[6, 7],
            contracheque__folha__periodo=self.period,
            contracheque__folha__tipo_folha__margem__gt=0,
            contracheque__folha__status__in=[4, 3],
            contracheque__pensioner=None,
        ).order_by("contracheque__servidor", "contracheque__folha")

        self.query_events = gfp_models.Evento.objects.filter(
            carater__in=[6, 7], active=True
        ).order_by("numero")

        self.cfg = Configuration.get_or_create("gfp")
        self.uadm = UnidadeAdministrativa.objects.get(pk=int(self.cfg.get("orgao")))
        self.responsavel_gfp = Servidor.objects.get(
            pk=int(self.cfg.get("responsavel_gfp"))
        )
        self.email_gfp = self.cfg.get("email_gfp", "")
        self.fone_gfp = self.cfg.get("telefone_responsavel_gfp", "")

    def get_generate_filename(self):
        return "viabillize_mpto_%02d%04d.zip" % (self.period.mes, self.period.ano)

    def generate_viabillizexml_file(self):
        path = settings.BASE_DIR
        model_file = ET.parse("%s/rh/gfp/loaders/Viabillize.xml" % path)
        root = model_file.getroot()
        cnpj = (
            self.uadm.pessoa_juridica.cnpj
            if self.uadm and self.uadm.pessoa_juridica
            else "00000000000000"
        )
        period = self.period if self.period else self.payroll.periodo

        root.find("Consignante").text = str(self.uadm)
        root.find("Cnpj").text = "%s.%s.%s/%s-%s" % (
            cnpj[0:2],
            cnpj[2:5],
            cnpj[5:8],
            cnpj[8:12],
            cnpj[12:14],
        )
        root.find("Folha_Descricao").text = (
            str(self.payroll) if hasattr(self, "payroll") else "NORMAL"
        )
        root.find("Folha_Referencia").text = "%02d%04d" % (period.mes, period.ano)
        root.find("Responsavel").find("Nome").text = str(
            self.responsavel_gfp.pessoa_fisica
        )
        root.find("Responsavel").find("Fone").text = self.fone_gfp
        root.find("Responsavel").find("Email").text = self.email_gfp

        el_margins = root.find("TiposDeMargens")
        cut_date = date(period.ano, period.mes, 1) + relativedelta(months=1, days=-1)
        for mc in gfp_models.MarginConsignable.objects.exclude(
            start_validity__gt=cut_date
        ):
            mc_el = ET.SubElement(el_margins, "TipoMargem")
            ET.SubElement(mc_el, "Codigo").text = "%s" % mc.pk
            ET.SubElement(mc_el, "Descricao").text = str(mc.title)
            ET.SubElement(mc_el, "PrazoMaximo").text = "%s" % mc.maximum_installment
            ET.SubElement(mc_el, "CetMaximo").text = "%s" % mc.maximum_cet
            ET.SubElement(mc_el, "ServicoUnico").text = "false"
            events_mc_el = ET.SubElement(mc_el, "Rubricas")
            consigned_ids = [ev.pk for ev in mc.consigneds.all()]
            for ev in self.query_events.all():
                ev_el = ET.SubElement(events_mc_el, "Rubrica")
                ET.SubElement(ev_el, "Codigo").text = (
                    ("%s%s" % (ev.numero, mc.type_of_payroll.abreviatura))
                    if not mc.type_of_payroll.principal
                    else ev.numero
                )
                ET.SubElement(ev_el, "Descricao").text = str(ev.titulo)
                ET.SubElement(ev_el, "TipoDePrazo").text = (
                    "FIXO" if ev.carater == 7 else "MENSALIDADE"
                )
                ET.SubElement(ev_el, "Aliquota").text = (
                    "%s" % ev.porcentagem
                    if ev.carater == 6 and ev.tipo_calculo in [1, 5]
                    else "0"
                )
                ET.SubElement(ev_el, "BaseAliquota").text = (
                    "%s" % ev.get_base_de_calculo_display()
                )
                ET.SubElement(ev_el, "IncideNaMargem").text = (
                    "true" if ev.pk in consigned_ids else "false"
                )

        viabillize_file = ET.ElementTree(root)
        # viabillize_file.write("Viabillize_teste.xml")

        # dom = parseString(root)
        # dom = parseString(xml)
        # print 'CRIANDO ARQUIVO [CADASTRO DE EVENTOS]... ',
        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "viabillize.xml")

        return self.create_file(file_path, viabillize_file, xml=True)

    def margins_to_elements(self):
        pass

    def registration_events(self):
        # ANEXO I - CADASTRO DE EVENTOS
        lines = []
        log.debug("REGISTRATION EVENTS")
        for e in gfp_models.Evento.objects.filter(
            Q(carater__in=[6, 7]) & Q(active=True)
        ):
            lines.append(
                "%s|%s|%s|%s|%s|%s|%s\r\n"
                % (
                    e.numero,
                    "",
                    e.titulo,
                    ("True" if e.porcentagem else "False"),
                    (e.get_base_de_calculo_display() if e.porcentagem else ""),
                    (("%s%%" % e.porcentagem) if e.porcentagem else ""),
                    ("True" if e.carater == 6 else "False"),
                )
            )
        # print 'OK',
        # print 'CRIANDO ARQUIVO [CADASTRO DE EVENTOS]... ',
        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_eventos.txt")

        return self.create_file(file_path, lines)
        # print 'OK'

    def functional_register(self):
        # ANEXO II - CADASTRO FUNCIONAL
        lines = []
        resgistrations = []

        # print 'COLETANDO INFORMAÇÔES...',
        log.debug("FUNCTIONAL REGISTER")
        # for fe in self.query_entries:
        #     cc = fe.contracheque
        for cc in gfp_models.ContraCheque.objects.filter(
            folha__periodo=self.period, folha__tipo_folha__margem__gt=0, pensioner=None
        ).order_by("servidor"):
            payroll = cc.folha
            _id = "%s%s" % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura)
            if _id not in resgistrations:
                resgistrations.append(_id)
                # if 0 < payroll.tipo_folha.margem <= 100:
                # for cc in payroll.paychecks.all().order_by('servidor'):
                try:
                    endereco = (
                        cc.servidor.pessoa_fisica.address.all()[0]
                        if cc.servidor.pessoa_fisica.address.exists()
                        else None
                    )
                    desligamento = {"data": "", "motivo": ""}
                    if payroll.tipo_folha.margem < 100:
                        # Folhas que podem ser totalmente consignadas, normalmente
                        if not cc.servidor.get_posses_ativas(cc.folha.date_range.last):
                            mov_desligamento = cc.servidor.posses.latest(
                                "data_desligamento"
                            ).desligamento
                            desligamento["data"] = mov_desligamento.data_desligamento
                            desligamento["motivo"] = (
                                mov_desligamento.get_opcao_display()
                            )
                    elif payroll.tipo_folha.margem == 100:
                        data_limite = date.today()
                        for fe1 in cc.lancamentos.filter(evento__tipo="P", prazo__gt=0):
                            dt = date(
                                fe1.contracheque.folha.periodo.ano,
                                fe1.contracheque.folha.periodo.mes,
                                5,
                            ) + relativedelta(months=int(fe1.prazo - fe1.qnt))
                            if dt > data_limite:
                                data_limite = dt
                        desligamento["data"] = data_limite
                        desligamento["motivo"] = "FIM DO BENEFÍCIO"

                    if cc.servidor.is_acordo_cooperacao:
                        type_employee = "EFETIVO/REQUISITADO"
                    elif cc.servidor.is_efetivo:
                        type_employee = "EFETIVO"
                    else:
                        type_employee = "COMISSIONADO"

                    lines.append(
                        "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\r\n"
                        % (
                            cc.servidor.pessoa_fisica,
                            _id,
                            cc.servidor.data_exercicio,
                            cc.servidor.pessoa_fisica.cpf,
                            cc.servidor.pessoa_fisica.rg,
                            cc.servidor.pessoa_fisica.rg_orgao,
                            cc.servidor.pessoa_fisica.rg_uf,
                            cc.servidor.pessoa_fisica.rg_data_expedicao,
                            (
                                cc.servidor.pessoa_fisica.phone.all()[0]
                                if cc.servidor.pessoa_fisica.phone.all()
                                else "(63) 3216-7600"
                            ),
                            endereco.logradouro if endereco else "",
                            endereco.numero if endereco else "",
                            endereco.bairro if endereco else "",
                            (
                                endereco.municipio.nome
                                if endereco and endereco.municipio
                                else ""
                            ),
                            endereco.cep if endereco else "",
                            (
                                endereco.municipio.estado.sigla
                                if endereco
                                and endereco.municipio
                                and endereco.municipio.estado
                                else ""
                            ),
                            cc.folha.tipo_folha,
                            type_employee,
                            cc.cargo_eletivo
                            or cc.cargo_comissao
                            or cc.cargo_efetivo
                            or "",
                            cc.lotacao or "",
                            cc.situacao_previdenciaria or "",
                            desligamento["data"],
                            desligamento["motivo"],
                            cc.margem_consignada_total,
                            "%02d%04d" % (cc.folha.periodo.mes, cc.folha.periodo.ano),
                        )
                    )
                except (
                    MovimentacaoPosse.DoesNotExist,
                    MovimentacaoDesligamento.DoesNotExist,
                ) as e:
                    # print 'ERRO: %s' % cc
                    log.exception(e)
                except Exception as e:
                    log.exception(e)
                    raise e
        # print 'OK',
        # print 'CRIANDO ARQUIVO [CADASTRO FUNCIONAL - %s]... ' % folha.tipo_folha.abreviatura,
        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_funcional.txt")

        return self.create_file(file_path, lines)
        # print 'OK'

    def bases_events(self):
        # ANEXO IV - CADASTRO DE BASES
        lines = []
        matriculas = {}
        log.debug("BASES EVENTS")
        # print 'COLETANDO INFORMAÇÔES...',
        # for cc in payroll.paychecks.order_by('servidor'):
        for fe in self.query_entries.filter(
            Q(evento__carater__in=[6]) & Q(evento__porcentagem__gt=0)
        ):
            if fe.contracheque.servidor.matricula not in matriculas:
                matriculas[fe.contracheque.servidor.matricula] = []
            if (
                fe.evento.base_de_calculo
                not in matriculas[fe.contracheque.servidor.matricula]
            ):
                matriculas[fe.contracheque.servidor.matricula].append(
                    fe.evento.base_de_calculo
                )
                try:
                    lines.append(
                        "%s|%s|%s|%s\r\n"
                        % (
                            "%02d%04d"
                            % (
                                fe.contracheque.folha.periodo.mes,
                                fe.contracheque.folha.periodo.ano,
                            ),
                            "%s%s"
                            % (
                                fe.contracheque.servidor.matricula,
                                fe.contracheque.folha.tipo_folha.abreviatura,
                            ),
                            fe.evento.get_base_de_calculo_display(),
                            fe.valor_base,
                        )
                    )
                except Exception as e:
                    raise e

        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        file_path = os.path.join(self.tmp_dir, "cadastro_bases.txt")
        # file_path = os.path.join(self.tmp_dir, dir_path, 'cadastro_bases_%s.txt' % payroll.tipo_folha)

        return self.create_file(file_path, lines)

    def returned_events(self, query_entries=[]):
        # ANEXO III - ARQUIVO RETORNO
        lines = []
        # print 'COLETANDO INFORMAÇÔES...',
        # for cc in payroll.paychecks.all().order_by('servidor'):
        for fe in self.query_entries:
            try:
                lines.append(
                    "%s|%s|%s|%s|%s|%s\r\n"
                    % (
                        "%02d%04d"
                        % (
                            fe.contracheque.folha.periodo.mes,
                            fe.contracheque.folha.periodo.ano,
                        ),
                        fe.evento.numero,
                        "%s%s"
                        % (
                            fe.servidor.matricula,
                            fe.contracheque.folha.tipo_folha.abreviatura,
                        ),
                        int(fe.parcela) if fe.evento.carater == 7 else 1,
                        int(fe.prazo),
                        fe.valor,
                    )
                )
            except Exception as e:
                raise e

        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.period.mes, self.period.ano)
        # file_path = os.path.join(self.tmp_dir, dir_path, 'arquivo_retorno_%s.txt' % payroll.tipo_folha)
        file_path = os.path.join(self.tmp_dir, "arquivo_retorno.txt")

        return self.create_file(file_path, lines)

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s" % (user, self.period, self.tmp_dir)
            )
            log.debug("PERIOD: %s" % self.period)
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivos Viabillize - %02d/%04d"
                % (self.period.mes, self.period.ano)
            )
            # for payroll in gfp_models.Folha.objects.filter(periodo=self.period,
            #       tipo_folha__margem__gt=0, status__in=[4, 3]):
            #     log.debug('>>>>>>>>>>>> %s ' % payroll)
            #     if not os.path.exists(self.tmp_dir):
            #         os.makedirs(self.tmp_dir)
            # self.registration_events()
            # self.functional_register()
            # self.bases_events()
            # self.returned_events()
            self.generate_viabillizexml_file()
            # else:
            #     log.debug('<<<<<<<<< NENHUMA FOLHA PROCESSADA PARA ENVIAR...')

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)

            zipfile = make_zipfile(
                os.path.join(self.tmp_dir, "..", self.get_generate_filename()),
                self.tmp_dir,
                False,
            )
            log.debug(">>>>>>>>>>>> ZIP GERADO: %s" % zipfile)
            gedfile = FileGED.from_filepath(zipfile, user, "application/zip", 1)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPGenerateCreditFile(GFPReturnFile):
    """docstring for"""

    _generated_filename = "fpsf900.txt"

    def __init__(self, *args, **kargs):
        super(GFPGenerateCreditFile, self).__init__(*args, **kargs)
        self.somente_pensionistas = (
            True if self.request.POST.get("somente_pensionistas") == "on" else False
        )
        self.convenant = None
        if self.request.POST.get("convenant"):
            self.convenant = gfp_models.BankingConvenant.objects.get(
                id=self.request.POST.get("convenant")
            )
        if "dt_pg" in self.request.POST:
            self.dt_pg = DateUtils.str_to_date(self.request.POST.get("dt_pg"), None)
            if self.payroll.status is not 3:
                self.payroll.dt_pagamento = self.dt_pg
                self.payroll.save()
        self.employees = []
        if "employees" in self.request.POST:
            list_employees = self.request.POST.getlist("employees")
            if len(list_employees) == 1 and "" in list_employees:
                pass
            else:
                self.employees = [int(id) for id in list_employees]

    def get_generate_filename(self):
        if self.convenant:
            file_name = "%s-%02d-%04d-%s.txt" % (
                self.convenant.bank.nome,
                self.payroll.periodo.mes,
                self.payroll.periodo.ano,
                self.convenant.convenant,
            )
            return clear_to_ascii(file_name)
        return ""

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}
        convenant_id = None
        if self.convenant:
            convenant_id = self.convenant.id

        Task.start(
            process_credit_file,
            convenant=convenant_id,
            payroll=self.payroll.id,
            employees=self.employees,
            filename=self.get_generate_filename(),
            # self.tmp_dir(),
            user=self.request.user.id,
            somente_pensionistas=self.somente_pensionistas,
        )

        # t = threading.Thread(target=process, args=(self.request.user, log))
        # t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPGerarArquivoConsignado(GFPReturnFile):

    @login_required("JSON")
    def gerar_arquivo_bancario_consignado(self, args=[]):
        obj = {"success": True}

        # remover os logs abaixo
        log.info(">>> self.request.POST")
        log.info(self.request.POST)

        Task.start(
            gerar_cnab_consignados_task,
            user=self.request.user.id,
            periodo=self.request.POST.get("periodo"),
            data_pgto=self.request.POST.get("dt_pg"),
        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPRAISFile(GFPReturnFile):
    """docstring for"""

    _generated_filename = "rais.txt"

    def __init__(self, *args, **kargs):
        super(GFPRAISFile, self).__init__(*args, **kargs)
        self.base_year = (
            int(self.request.POST.get("ano_base"))
            if "ano_base" in self.request.POST
            else (datetime.now().year - 1)
        )
        self.rectifier = (
            self.request.POST.get("retificadora")
            if "retificadora" in self.request.POST
            else False
        )

    def get_generate_filename(self):
        return "rais%s.txt" % self.base_year

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s"
                % (user, self.base_year, self.tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution("Arquivo da RAIS %s" % self.base_year)

            # file_buffer = bb.File(self.payroll, self.bank, task, log)
            file_buffer = RAISFile(self.base_year, self.rectifier, task, log)

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)
            file_path = os.path.join(self.tmp_dir, self.get_generate_filename())

            if not os.path.exists(self.tmp_dir):
                os.makedirs(self.tmp_dir)
            log.debug(">>>>>>>>>>>> ARQUIVO: %s" % file_path)

            try:
                log.debug("OPEN FILE TO WRITE")
                with codecs.open(file_path, "w", "utf-8") as fd:
                    log.debug("WRITE CONTENT FILE")
                    fd.write(str(file_buffer))
                log.debug(">>>>>>>>>>>> BUFFER: %s" % file_path)
            except Exception as e:
                log.debug("ERRO AO GERAR ARQUIVO")
                log.debug(str(e))
            else:
                gedfile = FileGED.from_filepath(file_path, user, "application/txt", 1)
                # zipfile = make_zipfile(os.path.join(self.tmp_dir, '..', self.get_generate_filename()),
                #                        self.tmp_dir, False)
                # log.debug('>>>>>>>>>>>> ZIP GERADO: %s' % zipfile)
                log.debug("GEDFILE CRIADO...")
                task.add_file(gedfile)

                task.finish_execution()
                log.debug("TASK FINALIZADA...")

                self.clear_tmpdir()
                log.debug("TMP DIR CLEAR...")

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPSEFIPFile(GFPReturnFile):
    """docstring for"""

    _generated_filename = "sefip.re"

    def __init__(self, *args, **kargs):
        super(GFPSEFIPFile, self).__init__(*args, **kargs)

    # def get_generate_filename(self):
    #     return 'sefip%s.re' % self.base_year

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        log.debug(">>>>>>>>>>>>>> SEFIPFile <<<<<<<<<<<<<<")

        def process(code, user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s" % (user, self.payroll, self.tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution("Arquivo SEFIP %s" % self.payroll)

            # file_buffer = bb.File(self.payroll, self.bank, task, log)
            file_buffer = SEFIPFile(self.payroll, task, log, code=code)

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)
            file_path = os.path.join(self.tmp_dir, self.get_generate_filename())

            if not os.path.exists(self.tmp_dir):
                log.debug(">>>>>>>>>>>> CREATE DIR: %s" % self.tmp_dir)
                os.makedirs(self.tmp_dir)
            log.debug(">>>>>>>>>>>> ARQUIVO: %s" % file_path)

            try:
                log.debug("OPEN FILE TO WRITE")
                with codecs.open(file_path, "w", "utf-8") as fd:
                    log.debug("WRITE CONTENT FILE")
                    fd.write(str(file_buffer))
                log.debug(">>>>>>>>>>>> BUFFER: %s" % file_path)
            except Exception as e:
                log.debug("ERRO AO GERAR ARQUIVO")
                log.debug(str(e))
            else:
                gedfile = FileGED.from_filepath(file_path, user, "application/txt", 1)
                # zipfile = make_zipfile(os.path.join(self.tmp_dir, '..', self.get_generate_filename()),
                #                        self.tmp_dir, False)
                # log.debug('>>>>>>>>>>>> ZIP GERADO: %s' % zipfile)
                log.debug("GEDFILE CRIADO...")
                task.add_file(gedfile)

                task.finish_execution()
                log.debug("TASK FINALIZADA...")

                # self.clear_tmpdir()
                log.debug("TMP DIR CLEAR...")

        code = self.request.POST.get("code", 115)
        t = threading.Thread(target=process, args=(code, self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPSisprevGenerator(GFPReturnFile):

    _generated_filename = "sisprev_mpto.zip"

    def renderer(self, data):
        import json

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    @login_required(type="JSON")
    def generate_file(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        try:
            Task.start(
                sisprev_web,
                period=self.period.pk,
                user=get_current_user().pk,
                success="""<p>
                    Arquivo
                    <span style="font-weight:bold">IGEPREV %(igeprev)s</span>
                    foi gerado com sucesso. Para fazer o download clique no
                    <a href="/athenas/GFPSocialSecurityWindowFileGenerator/file/?uuid=%(uuid)s">link</a>.
                    </p>
                    <p>
                    Este arquivo está disponível para download até dia
                    <span style="font-weight:bold">%(deadline)s</span>
                    </p>""",
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            periodo = gfp_models.Periodo.objects.get(pk=self.request.POST.get("period"))
            rst.update(
                success=True,
                message="Arquivo do IGEPREV %s-%s requisitado com sucesso, \
                        você será avisado quando o mesmo for concluído."
                % (periodo.mes, periodo.ano),
            )
        self.renderer(rst)


class GFPSPPrevcom(GFPReturnFile):
    """docstring for GFPSPPrevcom"""

    _generated_filename = "spprevicom.txt"

    def __init__(self, *args, **kargs):
        super(GFPSPPrevcom, self).__init__(*args, **kargs)

    def get_generate_filename(self):
        return "spprevicom.txt"

    def gera_arq_spprevcom(self):
        """
        Este método gera o arquivo do relatório SP Previcom utilizando o padrão informado.
        ---------------------------------
        Padrão por ContraCheque: 00000000001219810020160378743104202312202312000001REMUNERACAO                                  00000000357104600000V
        ---------------------------------
        # Estrutura caso o campo participante_migrado esteja Desabilitado
        # Verbas SPPREVCOM  Verbas Athenas                      Nome da Verba no Relatório
        # 1                 00100                               REMUNERAÇÃO
        # 070150            91200 -  Cont.PREV.COMPLEMENTAR     CONTRIBUIÇÃO PARTICIPANTE
        # 077059            91200 - (Exportar o patronal)       CONTRIBUIÇÃO PATROCINADOR
        # 070169            92200                               CONTRIBUIÇÃO PARTICIPANTE-ATIVO ANTERIOR
        # 070159            91300 -  Cont.PREV.COMPLEMENTAR     CONTRIBUIÇÃO PARTICIPANTE - 13º SALÁRIO
        # 077159            91300 - (Exportar o patronal)       CONTRIBUIÇÃO PATROCINADOR - 13º SALÁRIO
        # 070154            92220 - SP PREVCOM - I              CONTRIBUIÇÃO BENEFÍCIO DE RISCO - INVALIDEZ
        # 070155            92221- SP PREVCOM - II              CONTRIBUIÇÃO BENEFÍCIO DE RISCO - MORTE

        # Estrutura caso o campo participante_migrado esteja Habilitado
        # Verbas SPPREVCOM  Verbas Athenas                      Nome da Verba no Relatório
        # 1                 00100                               REMUNERAÇÃO
        # 071151            91200 -  Cont.PREV.COMPLEMENTAR     CONTRIBUIÇÃO DE PARTICIPANTE MIGRADO
        # 077151            91200 - (Exportar o patronal)       CONTRIBUIÇÃO PATRONAL DO MIGRADO
        # 070169            92200                               CONTRIBUIÇÃO PARTICIPANTE-ATIVO ANTERIOR
        # 071160            91300 -  Cont.PREV.COMPLEMENTAR     CONTRIBUIÇÃO DE PARTICIPANTE MIGRADO - 13º SALÁRIO
        # 077160            91300 - (Exportar o patronal)       CONTRIBUIÇÃO PATRONAL DO MIGRADO - 13º SALÁRIO
        # 070154            92220 - SP PREVCOM - I              CONTRIBUIÇÃO BENEFÍCIO DE RISCO - INVALIDEZ
        # 070155            92221- SP PREVCOM - II              CONTRIBUIÇÃO BENEFÍCIO DE RISCO - MORTE
        """

        log.debug("CONTEÚDO PREVCOM")
        linhas = []
        verbas_patronal = ["91200", "91300"]
        de_para_nao_migrado = {
            "00100": {"1": "REMUNERAÇÃO"},
            "91200": [
                {"70150": "CONTRIBUIÇÃO PARTICIPANTE"},
                {"77059": "CONTRIBUIÇÃO PATROCINADOR"},
            ],
            "92200": {"070169": "CONTRIBUIÇÃO PARTICIPANTE-ATIVO ANTERIOR"},
            "91300": [
                {"70159": "CONTRIBUIÇÃO PARTICIPANTE - 13º SALÁRIO"},
                {"77159": "CONTRIBUIÇÃO PATROCINADOR - 13º SALÁRIO"},
            ],
            "92220": {"70154": "CONTRIBUIÇÃO BENEFÍCIO DE RISCO - INVALIDEZ"},
            "92221": {"70155": "CONTRIBUIÇÃO BENEFÍCIO DE RISCO - MORTE"},
        }
        de_para_migrado = {
            "00100": {"1": "REMUNERAÇÃO"},
            "91200": [
                {"71151": "CONTRIBUIÇÃO DE PARTICIPANTE MIGRADO"},
                {"77151": "CONTRIBUIÇÃO PATROCINADOR DO MIGRADO"},
            ],
            "92200": {"070169": "CONTRIBUIÇÃO PARTICIPANTE-ATIVO ANTERIOR"},
            "91300": [
                {"71160": "CONTRIBUIÇÃO DE PARTICIPANTE MIGRADO - 13º SALÁRIO"},
                {"77160": "CONTRIBUIÇÃO PATRONAL DO MIGRADO - 13º SALÁRIO"},
            ],
            "92220": {"70154": "CONTRIBUIÇÃO BENEFÍCIO DE RISCO - INVALIDEZ"},
            "92221": {"70155": "CONTRIBUIÇÃO BENEFÍCIO DE RISCO - MORTE"},
        }

        contra_cheques = ContraCheque.objects.filter(
            lancamentos__evento__numero=verbas_patronal[0], folha=self.payroll
        )
        if contra_cheques.count() > 0:
            for cc in contra_cheques:
                servidor = cc.servidor
                previdencia = SocialSecurityEmployee.objects.filter(
                    employee=servidor, social_security_config__pk=7
                )
                if previdencia.exists() and previdencia.first().participante_migrado:
                    for chave, valor in de_para_migrado.items():
                        q_evento = Evento.objects.filter(numero=chave)
                        if q_evento.exists():
                            evento = q_evento.first()
                            query = cc.lancamentos.filter(evento=evento)
                            if query.exists():
                                folha_evento = query.first()
                                linhas.append(
                                    self.gera_linha_valor(
                                        servidor,
                                        cc,
                                        valor,
                                        folha_evento,
                                        evento,
                                        chave,
                                        verbas_patronal,
                                    )
                                )
                                if (
                                    evento.numero == verbas_patronal[0]
                                    or evento.numero == verbas_patronal[1]
                                ):
                                    linhas.append(
                                        self.gera_linha_patronal(
                                            servidor, cc, valor, folha_evento, evento
                                        )
                                    )
                elif previdencia.exists():
                    for chave, valor in de_para_nao_migrado.items():

                        q_evento = Evento.objects.filter(numero=chave)
                        if q_evento.exists():
                            evento = q_evento.first()
                            query = cc.lancamentos.filter(evento=evento)
                            if query.exists():
                                folha_evento = query.first()
                                linhas.append(
                                    self.gera_linha_valor(
                                        servidor,
                                        cc,
                                        valor,
                                        folha_evento,
                                        evento,
                                        chave,
                                        verbas_patronal,
                                    )
                                )
                                if (
                                    evento.numero == verbas_patronal[0]
                                    or evento.numero == verbas_patronal[1]
                                ):
                                    linhas.append(
                                        self.gera_linha_patronal(
                                            servidor, cc, valor, folha_evento, evento
                                        )
                                    )
        else:
            linhas.append(
                f"NÃO FOI ENCONTRADO CONTRACHEQUE COM A VERBA: {verbas_patronal[0]} NA FOLHA {self.payroll}"
            )
        file_path = os.path.join(self.tmp_dir, "spprevicom.txt")
        return self.create_file(file_path, linhas)

    def gera_linha_valor(
        self, servidor, cc, valor, folha_evento, evento, chave, verbas_patronal
    ):
        """
        Esse método gera as linhas utilizando o campo valor do folha_evento
        """
        return "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\r\n" % (
            "00",  # Espaços - 00 (2)
            "000",  # Código do Cliente - 000 (3)
            "0",  # População - 0 (1)
            f"{servidor.matricula}".zfill(
                8
            ),  # Matrícula do Servidor - 0000 + Matricula (8),
            "81",  # Órgão - 81 (2) Enviar o código 81 por padrão;
            "002",  # U.O - 002 (3) Por padrão enviar o código 2
            "01",  # P.V - 00 (2) Por padrão enviar 01 (Alterado em ATS-5188)
            f"{servidor.pessoa_fisica.cpf}",  # CPF - Exportar CPF dos servidores sem pontuação (11)
            f"{cc.folha.periodo.ano}{cc.folha.periodo.mes:02}",  # ANO/MÊS - (6) dígitos, Ano e mês da competência selecionada 202401
            f"{cc.lancamentos.first().reference_year}{cc.lancamentos.first().reference_month:02}",  # ANO/MÊS - (6) dígitos, Ano e mês do holerite 202401
            f"{list(valor[0].keys())[0] if chave in verbas_patronal else list(valor.keys())[0]}".zfill(
                6
            ),  # Código da Rubrica - 6 dígitos, preencher com 0 a esquerda
            f"{list(valor[0].values())[0] if chave in verbas_patronal else list(valor.values())[0]}".ljust(
                45
            ),  # Nome da Rubrica - 45 dígitos, preencher com espaços a direita
            f"{folha_evento.valor}".replace(".", "").zfill(
                15
            ),  # Valor - 15 digitos, sem pontuação adicionando 0 a esquerda
            f"{folha_evento.pct:.2f}".replace(".", "").zfill(
                5
            ),  # Percentual - 5 dígitos, adicionando 0 a esquerda
            (
                "V" if evento.tipo == "P" else evento.tipo
            ),  # Natureza - 1 dígito, Sendo V para vencimento e D para desconto:
        )

    def gera_linha_patronal(self, servidor, cc, valor, folha_evento, evento):
        """
        Esse método gera as linhas utilizando o campo patronal do folha_evento para os eventos da variável verbas_patronal
        """
        return "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\r\n" % (
            "00",  # Espaços - 00 (2)
            "000",  # Código do Cliente - 000 (3)
            "0",  # População - 0 (1)
            f"{servidor.matricula}".zfill(
                8
            ),  # Matrícula do Servidor - 0000 + Matricula (8),
            "81",  # Órgão - 81 (2) Enviar o código 81 por padrão;
            "002",  # U.O - 002 (3) Por padrão enviar o código 2
            "01",  # P.V - 00 (2) Por padrão enviar 01 (Alterado em ATS-5188)
            f"{servidor.pessoa_fisica.cpf}",  # CPF - Exportar CPF dos servidores sem pontuação (11)
            f"{cc.folha.periodo.ano}{cc.folha.periodo.mes:02}",  # ANO/MÊS - (6) dígitos, Ano e mês da competência selecionada 202401
            f"{cc.lancamentos.first().reference_year}{cc.lancamentos.first().reference_month:02}",  # ANO/MÊS - (6) dígitos, Ano e mês do holerite 202401
            f"{list(valor[1].keys())[0]}".zfill(
                6
            ),  # Código da Rubrica - 6 dígitos, preencher com 0 a esquerda
            f"{list(valor[1].values())[0]}".ljust(
                45
            ),  # Nome da Rubrica - 45 dígitos, preencher com espaços a direita
            f"{folha_evento.patronal}".replace(".", "").zfill(
                15
            ),  # Valor - 15 digitos, sem pontuação adicionando 0 a esquerda
            f"{folha_evento.pct:.2f}".replace(".", "").zfill(
                5
            ),  # Percentual - 5 dígitos, adicionando 0 a esquerda
            (
                "V" if evento.tipo == "P" else evento.tipo
            ),  # Natureza - 1 dígito, Sendo V para vencimento e D para desconto:
        )

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            log.debug("GENERATE FILE PROCESS: %s: %s" % (user, self.tmp_dir))
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivo SP Prevcom - %s" % self.payroll
            )

            self.gera_arq_spprevcom()

            log.debug(">>>>>>>>>>>> ARQUIVO GERADO EM %s" % self.tmp_dir)
            file_path = os.path.join(self.tmp_dir, self.get_generate_filename())
            gedfile = FileGED.from_filepath(file_path, user, "application/txt", 1)

            log.debug(f"gedfile: {gedfile}")

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
