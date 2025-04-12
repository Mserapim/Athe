# -*- coding: utf-8 -*-
from engine.mq.models import Task
from contrib.reports import start_report
from django.conf import settings
from contrib.utils import getLogger
from rh.gfp.models import ContraCheque as Paycheck
from rh.gfp.models import FolhaTipo
from datetime import datetime
from rh.models import Lotacao
from standard.models import Choice


log = getLogger(__name__)

from app import settings


def start_paycheck_reports(params, report, report_name, output=None):
    """
    Função que chama uma task que gera o relatório de contracheque.
    Args:
    params (dict): Um dicionário contendo os parâmetros necessários para gerar o relatório.
    report (Task): path do jasper para gerar o relatório.
    report_name (str): O nome do relatório a ser gerado.
    output (str): formato de saída do relatório.
    Returns:
    dict:
    """

    rst = {"success": False, "message": "Nada feito ainda!"}

    try:
        if not "organ_identifier" in params:
            params["organ_identifier"] = settings.ORGAN_IDENTIFIER

        if getattr(settings, "REPORT_DEFAULT_PATH", None):
            report = "".join(["/", settings.REPORT_DEFAULT_PATH, report])
        t = Task.start(
            start_report,
            report=report,
            report_name=report_name,
            params=params,
            output_format=output,
            success="",
        )
    except Exception as e:
        log.exception(e)
        rst.update(message=str(e))
    else:
        rst.update(
            success=True,
            message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            uuid=t.uuid,
        )
    return rst


def paycheck_list(month, year, type_payroll, employee):
    """
    Função que retorna uma lista (str) de contracheque.
    Args:
    month (int): mês.
    year (int): Ano.
    type_payroll (int): Tipo folha.
    employee (Object): objeto do servidor.
    Returns:
    list (str):
    """

    key_all_kinds = 999999
    key_none_kind = 999998
    try:
        if type == str(key_all_kinds):
            list_month = [month]
            if int(month) == 12:
                list_month.append(13)
            types = FolhaTipo.objects.all()
            list_types = [x.pk for x in types]
            query_cc = Paycheck.objects.filter(
                servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                folha__periodo__mes__in=list_month,
                folha__periodo__ano=year,
                folha__tipo_folha__pk__in=list_types,
            )

        else:
            query_cc = Paycheck.objects.filter(
                servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                folha__periodo__mes=month,
                folha__periodo__ano=year,
                folha__tipo_folha__pk=type_payroll,
            )

        list_paycheck = ",".join(
            [str(cc.pk) for cc in query_cc.filter(folha__available_pvf=True)]
        )

    except Exception as e:
        log.exception(e)

    return list_paycheck


def get_years_point_sheet():
    """
    Retorna uma lista de anos entre o ano a partir de 2010.
    returns:
    list:
    """
    years = []
    current_year = datetime.today().year
    year_corte = 2010
    while current_year >= year_corte:
        years.append(year_corte)
        year_corte = year_corte + 1

    data = [{"value": year, "label": str(year)} for year in years]
    return data


def get_years_paycheck():
    """
    Retorna uma lista de anos entre o ano a partir de HOLERITE_START_YEAR.
    returns:
    list:
    """
    years = []
    start_year = Choice.objects.get(app_label="pvf", name="HOLERITE_START_YEAR").value
    data_year = datetime.today().year
    while data_year >= start_year:
        years.append(data_year)
        data_year = data_year - 1

    data = [{"value": year, "label": str(year)} for year in years]
    return data


def get_months():
    """
    Retorna uma lista de meses do ano.
    returns:
    list:
    """
    return [
        {"value": 1, "label": "JANEIRO"},
        {"value": 2, "label": "FEVEREIRO"},
        {"value": 3, "label": "MARÇO"},
        {"value": 4, "label": "ABRIL"},
        {"value": 5, "label": "MAIO"},
        {"value": 6, "label": "JUNHO"},
        {"value": 7, "label": "JULHO"},
        {"value": 8, "label": "AGOSTO"},
        {"value": 9, "label": "SETEMBRO"},
        {"value": 10, "label": "OUTUBRO"},
        {"value": 11, "label": "NOVEMBRO"},
        {"value": 12, "label": "DEZEMBRO"},
    ]


def get_year_calendar():
    """
    Retorna uma lista anos.
    returns:
    list (dict):
    """
    try:
        years = []
        start_year = datetime.today().year - 1
        data_year = datetime.today().year + 5
        while data_year >= start_year:
            years.append(data_year)
            data_year = data_year - 1

        collection = [{"value": year, "label": str(year)} for year in years]
        return collection
    except Exception as e:
        log.exception(e)


def filter_teams(workplaces):
    """
    Retorna uma lotações do responsável.
    returns:
    list (dict):
    """
    places = []
    for workplace in workplaces:
        workplaces_below = Lotacao.objects.filter(pai=workplace)
        places.append({"id": workplace.pk, "description": str(workplace)})
        for workplace_below in workplaces_below:
            places.append(
                {"id": workplace_below.pk, "description": str(workplace_below)}
            )

        return places


def get_teams(employee):
    """
    Retorna uma lotações do responsável.
    returns:
    list (dict):
    """
    try:
        workplaces = Lotacao.objects.filter(responsavel=employee.id)
        workplace_json = [
            {"id": int(9999), "description": "Todas as equipes"},
            {"id": int(9998), "description": "Nenhuma equipe selecionada"},
        ] + filter_teams(workplaces)

        return workplace_json

    except Exception as e:
        log.error(e)


def lista_ano_ficha_financeira():
    lista = []
    try:
        lista = [
            {"id": ano, "description": str(ano)}
            for ano in range(1997, (datetime.now().year + 1))
        ]
    except Exception as e:
        log.error(e)
    return lista
