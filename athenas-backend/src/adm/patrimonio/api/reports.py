# -*- coding: utf-8 -*-
from adm.patrimonio.models import Conta, NotaEntrada
from contrib.extjs import ExtReportBuild
from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify


class PATReportAnaliticoAtivo(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_ativo_analitico/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_ativo_analitico/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        localizacao = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()


class PATReportAnaliticoAtivoLocalizacao(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/localizacao/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/localizacao/",
        },
        {"nome": "data_inicial", "tipo": "String", "valor": "1989-01-01"},
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        localizacao = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()


class PATReportAnaliticoAtivoSemLocalizacao(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_sem_localizacao/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_sem_localizacao/",
        },
        {"nome": "data_inicial", "tipo": "String", "valor": "1989-01-01"},
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        data_final = forms.CharField()
        conta = forms.CharField()


class PATReportAnaliticoAtivoGrupo(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_analitico_ativo/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_analitico_ativo/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_final = forms.CharField()


class PATReportAnaliticoAdquiridoGrupo(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_analitico_adquirido/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_analitico_adquirido/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_final = forms.CharField()
        data_inicial = forms.CharField()


class PATReportAnaliticoAdquirido(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_adquirido_analitico/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_adquirido_analitico/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        localizacao = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()


class PATReportAnaliticoBaixado(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_baixado_analitico/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_baixado_analitico/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        localizacao = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()


class PATReportSinteticoAdquirido(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_sintetico_adquirido/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_sintetico_adquirido/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        data_inicial = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()
        gerencial = forms.CharField()

    def get_generated_filename(self):
        return "sintetico-de-adquirido-%(conta)s-%(nota)s-ate-%(data)s%(gerencial)s" % {
            "conta": "todas",
            "nota": "todas",
            "data": "",
            "gerencial": "gerencial" if True else "",
        }


class PATReportSinteticoAtivo(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_sintetico_ativo/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_sintetico_ativo/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    def format_geneated_filename(self, **kargs):
        pass

    def get_generated_filename(self):
        conta = None
        nota = None
        data = self.request.GET.get("data_final")
        gerencial = "gerencial" in self.request.GET

        try:
            conta = Conta.objects.get(pk=int(self.request.GET.get("conta", 0) or 0))
        except Conta.DoesNotExist:
            conta = None

        try:
            nota = NotaEntrada.objects.get(pk=int(self.request.GET.get("nota", 0) or 0))
        except NotaEntrada.DoesNotExist:
            nota = None

        return (
            "sintetico-de-ativos-%(conta)s-%(nota)s-ate-%(data)s%(gerencial)s.pdf"
            % {
                "conta": "todas-as-contas" if conta is None else slugify(str(conta)),
                "nota": "todos-tipos-de-notas" if nota is None else nota.cache_type,
                "data": data,
                "gerencial": "-gerencial" if gerencial is True else "",
            }
        )

    class Form(forms.Form):
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()
        gerencial = forms.CharField()


class PATReportSinteticoAtivoLiquido(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_sintetico_ativo_liquido/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_sintetico_ativo_liquido/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_final = forms.CharField()


class PATReportSinteticoBaixado(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_sintetico_baixado/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_sintetico_baixado/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        data_inicial = forms.CharField()
        data_final = forms.CharField()
        conta = forms.CharField()
        tipo_nota = forms.CharField()
        gerencial = forms.CharField()

    def get_generated_filename(self):
        return "sintetico-de-baixas-%(conta)s-%(nota)s-ate-%(data)s%(gerencial)s" % {
            "conta": "todas",
            "nota": "todas",
            "data": "",
            "gerencial": "gerencial" if True else "",
        }


class PATReportSinteticoAvaliado(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/grupo_especie_depreciacao/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/grupo_especie_depreciacao/",
        },
        {"nome": "visao", "tipo": "String", "valor": "grupo"},
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()

    def get_generated_filename(self):
        return "sintetico-de-avaliados-%(conta)s-%(nota)s-ate-%(data)s%(gerencial)s" % {
            "conta": "todas",
            "nota": "todas",
            "data": "",
            "gerencial": "gerencial" if True else "",
        }


class PATReportAnaliticoAvaliado(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/grupo_especie_depreciacao/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/grupo_especie_depreciacao/",
        },
        {"nome": "visao", "tipo": "String", "valor": "item"},
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        grupo = forms.CharField()
        especie = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()


class PATReportTermoMovimento(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/bens_movimento/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/bens_movimento/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        movimento = forms.CharField()


class PATReportResumoSinteticoAtivo(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_sintetico_ativo/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_sintetico_ativo/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_final = forms.CharField()


class PATReportResumoSinteticoAdquirido(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_sintetico_adquirido/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_sintetico_adquirido/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()


class PATReportTermoBaixa(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/termo_baixa_2014/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/termo_baixa_2014/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        baixa = forms.CharField()


class PATReportResumoSinteticoBaixado(ExtReportBuild):

    report_src = "/to/mpe/adm/patrimonio/resumo_sintetico_baixado/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/adm/patrimonio/resumo_sintetico_baixado/",
        },
        {
            "nome": "debug",
            "tipo": "String",
            "valor": "" if getattr(settings, "DEBUG", False) is False else "1",
        },
    ]

    class Form(forms.Form):
        proprio = forms.CharField()
        data_inicial = forms.CharField()
        data_final = forms.CharField()
