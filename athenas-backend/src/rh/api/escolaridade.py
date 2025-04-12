# -*- coding: utf-8 -*-

from django import forms

from contrib import extjs
from contrib.newrest import Restful, RestfulDRY
from contrib.utils import employee_from_user, get_json_engine, getLogger
from rh.models import (
    CensoEstudo,
    CourseCineBrasil,
    HigherEducationInstitution,
    Localidade,
    MovimentacaoPosse,
)

json = get_json_engine()
log = getLogger(__name__)


ESCOLARIDADE_CHOICES = (
    (1, "MÉDIO"),
    (2, "TÉCNICO"),
    (3, "SUPERIOR"),
    (4, "PÓS-GRADUAÇÃO"),
    (5, "MESTRADO"),
    (6, "DOUTORADO"),
    (7, "PÓS-DOUTORADO"),
)


class RHCensoEstudo(Restful):

    _model = CensoEstudo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.pesquisa.EscolaridadeTabPanel')")

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)
        params.update(
            {
                "servidor_unicode": "%s" % instance.servidor,
                "servidor": instance.servidor_id,
                "cidade_unicode": "%s" % instance.cidade,
                "cidade": instance.cidade_id,
                "nivel_escolaridade_display": instance.get_nivel_escolaridade_display(),
                "nivel_escolaridade": instance.nivel_escolaridade,
                "instituicao": instance.instituicao,
                "curso": instance.curso,
                "ano_conclusao": instance.ano_conclusao,
            }
        )
        return params

    def get_params(self, querydict=None, **kargs):
        params = super(RHCensoEstudo, self).get_params(querydict, **kargs)

        if "cidade" in params:
            params.update(cidade=Localidade.objects.get(pk=params.get("cidade")))

        params.update(servidor=employee_from_user(self.request.user))

        return params

    def get_query(self):
        query = super(RHCensoEstudo, self).get_query()

        if self.request.user.has_perm("escol_admin") is False:
            query = query.filter(servidor=employee_from_user(self.request.user))

        return query

    def has_permission(self, args=[]):
        obj = {
            "result": (
                False
                if MovimentacaoPosse.objects.filter(
                    servidor__matricula=self.request.user.servidor.matricula,
                    quadro__cargo__tipo_lei_cargo="EF",
                    ativo=True,
                    servidor__tipo="S",
                ).count()
                else True
            )
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHRelatorioCensoEstudo(extjs.ExtReportBuild):
    report_src = "/to/mpe/rh/censo_estudo/main"
    params = [
        {"nome": "SUBREPORT_DIR", "tipo": "String", "valor": "to/mpe/rh/censo_estudo/"}
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatório de Censo de Estudo"}

    class Form(forms.Form):
        escolaridade = forms.ChoiceField(
            label="Escolaridade", choices=ESCOLARIDADE_CHOICES, required=False
        )

    def get_generated_filename(self):
        dic = dict(ESCOLARIDADE_CHOICES)
        report = (
            "relatorio-censo-estudo-%s.pdf"
            % dic.get(int(self.request.GET["escolaridade"]))
            if self.request.GET["escolaridade"]
            else "relatorio-censo-estudo-geral.pdf"
        )
        report = report.encode("utf-8")
        return report


class RHHigherEducationInstitution(RestfulDRY):
    _model = HigherEducationInstitution

    full_text_index = (
        "code__icontains",
        "name__icontains",
        "acronym__icontains",
        "municipality__nome__icontains",
        "municipality__sigla__icontains",
    )


class RHCourseCineBrasil(RestfulDRY):
    _model = CourseCineBrasil

    full_text_index = (
        "code__icontains",
        "label__icontains",
    )
