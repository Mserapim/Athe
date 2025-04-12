# -*- coding: utf-8 -*-
import time
from datetime import datetime

from adm.sispat.fields import MSSQLAutocompleteField
from contrib.extjs import ExtReportBuild
from django import forms
from django.forms.fields import CharField, ChoiceField, DateField

JASPER_DATASOURCE = "sispat-srvwin"

TIPO_BEM_CHOICES = (
    #    ("", u"TODOS"),
    ("p", "PRÓPRIOS"),
    ("t", "TERCEIROS"),
)

TIPO_BAIXA_CHOICES = (
    ("", "TODOS"),
    ("Venda".encode("ascii", "xmlcharrefreplace"), "VENDA"),
    ("Sinistro".encode("ascii", "xmlcharrefreplace"), "SINISTRO"),
    ("Outros".encode("ascii", "xmlcharrefreplace"), "OUTROS"),
    ("Doação".encode("ascii", "xmlcharrefreplace"), "DOAÇÃO"),
)

MSSQLAutocompleteField.register(
    "grupo",
    """
SELECT
    0 as contador,
    'TODOS' as descricao
UNION ALL
SELECT DISTINCT
    EG.contador,
    EG.descricao
FROM
    especgrupo  EG
    JOIN especie E ON EG.contador = E.grupo
WHERE
    LOWER(EG.descricao) LIKE LOWER('%%%(query)s%%') OR
    LOWER(E.descricao) LIKE LOWER('%%%(query)s%%')
ORDER BY
    EG.descricao
    """,
    "sispat",
)

MSSQLAutocompleteField.register(
    "departamento",
    """
SELECT
    0 as contador,
    'TODOS' as descricao
UNION ALL
SELECT DISTINCT
    D.contador,
    D.descricao
FROM
    dbo.departamento D
WHERE
    LOWER(D.sigla) LIKE  LOWER('%%%(query)s%%') OR
    LOWER(D.descricao) LIKE  LOWER('%%%(query)s%%')
ORDER BY
    D.descricao
    """,
    "sispat",
)


class PTMRelatorioRelacionadoLocalizacao(ExtReportBuild):

    report_src = (
        "/to/mpe/patrimonio/bens_relacionados/por_localizacao/br_por_localizacao"
    )

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_relacionados/por_localizacao/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Bens Relacionados",
        "SUB_TITLE": "Bens Relacionados organizados por localização",
    }

    class Form(forms.Form):
        tipo = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        setor = MSSQLAutocompleteField(
            label="Departamento", required=True, slug="departamento"
        )
        bem_descricao = CharField(label="Descrição", required=False)
        dt_inicio = DateField(label="Inicio do periodo")
        dt_fim = DateField(label="Final do periodo")


class PTMRelatorioControladoLocalizacao(ExtReportBuild):

    report_src = (
        "/to/mpe/patrimonio/bens_controlados/por_localizacao/bc_por_localizacao"
    )

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_controlados/por_localizacao/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Bens Controlados",
        "SUB_TITLE": "Bens Controlados organizados por localização",
    }

    class Form(forms.Form):
        tipo = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        setor = MSSQLAutocompleteField(
            label="Departamento", required=True, slug="departamento"
        )
        bem_descricao = CharField(label="Descrição", required=False)
        dt_inicio = DateField(label="Inicio do periodo")
        dt_fim = DateField(label="Final do periodo")


class PTMRelatorioRelacionadoGrupoEspecie(ExtReportBuild):

    report_src = (
        "/to/mpe/patrimonio/bens_relacionados/por_grupo_especie/br_por_grupo_especie"
    )

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_relacionados/por_grupo_especie/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Bens relacionados",
        "SUB_TITLE": "Bens Relacionados organizados por Grupo/Especie",
    }

    class Form(forms.Form):
        tipo = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        grupo = MSSQLAutocompleteField(label="Grupo", required=True, slug="grupo")
        especie = CharField(label="Especie", required=False)
        dt_inicio = DateField(label="Inicio do periodo")
        dt_fim = DateField(label="Final do periodo")


class PTMSinteticoAdquirido(ExtReportBuild):

    report_src = "/to/mpe/patrimonio/sefaz/bens_adquiridos_por_grupo_especie"

    datasource = JASPER_DATASOURCE

    params = [
        {"nome": "SUBREPORT_DIR", "valor": "to/mpe/patrimonio/sefaz/", "tipo": "String"}
    ]

    titles = {"TITLE": "Sintetico por Grupo", "SUB_TITLE": "Bens por Grupo/Especie"}

    class Form(forms.Form):
        dt_i = DateField(label="Inicio do periodo")
        dt_e = DateField(label="Final do periodo")

    def str_to_time(self, dt):
        return time.strptime(dt, "%Y-%m-%d")

    def get_generated_filename(self):
        return "SINTETICO_POR_GRUPO_ESPECIE_DE_{0}_ATE_{1}.pdf".format(
            time.strftime("%d-%m-%Y", self.str_to_time(self.request.GET["dt_i"])),
            time.strftime("%d-%m-%Y", self.str_to_time(self.request.GET["dt_e"])),
        )


class PTMSinteticoAtivo(ExtReportBuild):

    report_src = "/to/mpe/patrimonio/sefaz/bens_ativos_por_grupo_especie"

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/sefaz/",
            "tipo": "String",
        },
        {"nome": "dt_i", "valor": "1989-01-01", "tipo": "String"},
    ]

    titles = {"TITLE": "Sintetico por Grupo", "SUB_TITLE": "Bens por Grupo/Especie"}

    class Form(forms.Form):
        # dt_i = DateField(label = u"Inicio do periodo")
        dt_e = DateField(label="Final do periodo")

    def str_to_time(self, dt):
        return time.strptime(dt, "%Y-%m-%d")

    def get_generated_filename(self):
        return "SINTETICO_POR_GRUPO_ESPECIE_ATE_{0}.pdf".format(
            time.strftime("%d-%m-%Y", self.str_to_time(self.request.GET["dt_e"]))
        )


class PTMSinteticoBaixa(ExtReportBuild):

    report_src = "/to/mpe/patrimonio/sefaz/baixa_sintetico"

    datasource = JASPER_DATASOURCE

    params = [
        {"nome": "SUBREPORT_DIR", "valor": "to/mpe/patrimonio/sefaz/", "tipo": "String"}
    ]

    titles = {
        "TITLE": "Sintetico por Grupo",
        "SUB_TITLE": "Bens Baixados por Grupo/Especie",
    }

    class Form(forms.Form):
        dt_i = DateField(label="Inicio do periodo")
        dt_e = DateField(label="Final do periodo")

    def str_to_time(self, dt):
        return time.strptime(dt, "%Y-%m-%d")

    def get_generated_filename(self):
        return "SINTETICO_BAIXADO_POR_GRUPO_ESPECIE_DE_{0}_ATE_{1}.pdf".format(
            time.strftime("%d-%m-%Y", self.str_to_time(self.request.GET["dt_i"])),
            time.strftime("%d-%m-%Y", self.str_to_time(self.request.GET["dt_e"])),
        )


class PTMRelatorioControladoGrupoEspecie(ExtReportBuild):

    report_src = (
        "/to/mpe/patrimonio/bens_controlados/por_grupo_especie/bc_por_grupo_especie"
    )

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_controlados/por_grupo_especie/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Bens Controlados",
        "SUB_TITLE": "Bens Controlados organizados por Grupo/Especie",
    }

    class Form(forms.Form):
        tipo = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        grupo = MSSQLAutocompleteField(label="Grupo", required=True, slug="grupo")
        especie = CharField(label="Especie", required=False)
        dt_inicio = DateField(label="Inicio do periodo")
        dt_fim = DateField(label="Final do periodo")


class PTMSinteticoControladoBaixa(ExtReportBuild):

    report_src = "/to/mpe/patrimonio/bens_controlados/baixa_analitico/baixa_analitico"

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_controlados/baixa_analitico/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Sintético de Baixa",
        "SUB_TITLE": "Relatório de Bens Controlados Baixados por Data",
    }

    def get_generated_filename(self):
        return "sispat-baixa-controlado-%s.pdf" % datetime.now().strftime("%Y%m%d")

    class Form(forms.Form):
        tipobem = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        tipobaixa = ChoiceField(label="Tipo de baixa", choices=TIPO_BAIXA_CHOICES)
        dt_i = DateField(label="Inicio do periodo")
        dt_e = DateField(label="Final do periodo")


class PTMSinteticoRelacionadoBaixa(ExtReportBuild):

    report_src = "/to/mpe/patrimonio/bens_relacionados/baixa_analitico/baixa_analitico"

    datasource = JASPER_DATASOURCE

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "valor": "to/mpe/patrimonio/bens_relacionados/baixa_analitico/",
            "tipo": "String",
        }
    ]

    titles = {
        "TITLE": "Sintético de Baixa",
        "SUB_TITLE": "Relatório de Bens Relacionado Baixados por Data",
    }

    def get_generated_filename(self):
        return "sispat-baixa-relacionado-%s.pdf" % datetime.now().strftime("%Y%m%d")

    class Form(forms.Form):
        tipobem = ChoiceField(label="Tipo", choices=TIPO_BEM_CHOICES)
        tipobaixa = ChoiceField(label="Tipo de baixa", choices=TIPO_BAIXA_CHOICES)
        dt_i = DateField(label="Inicio do periodo")
        dt_e = DateField(label="Final do periodo")
