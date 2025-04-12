from django.db import connections

# import oracledb
import calendar
import base64
import datetime
from contrib.utils import getLogger

log = getLogger(__name__)


def dictfetchall_resume(employee, month, year):
    "Este metódo faz a chamada da proc do banco folha ponto e retorna um dicionário de dados"
    try:
        pass
        # with connections["mdc4web"].cursor() as cursor:
        #     cpf = employee.pessoa_fisica.cpf
        #     dt_init = datetime.date(year, month, 1)
        #     dt_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
        #     VRETORNORESUME = cursor.var(oracledb.CURSOR).var
        #     cursor.callproc(
        #         "resumo_folhaponto",
        #         (
        #             cpf,
        #             dt_init.strftime("%d/%m/%Y"),
        #             dt_end.strftime("%d/%m/%Y"),
        #             VRETORNORESUME,
        #         ),
        #     )
        #     cursor_data_resume = VRETORNORESUME.getvalue()

        #     columns_resume = [col[0] for col in cursor_data_resume.description]

        #     dict_value_resume = [
        #         dict(zip(columns_resume, row)) for row in cursor_data_resume.fetchall()
        #     ]

        # return dict_value_resume[0]

    except Exception as err:
        log.exception(err)
        raise err


def range_dictfetchall_resume(employee, start_competence, end_competence):
    "Este metódo faz a chamada da proc do banco folha ponto e retorna um dicionário de dados"
    try:
        pass
        # with connections["mdc4web"].cursor() as cursor:
        #     month_start, year_start = start_competence.split("/")
        #     month_end, year_end = end_competence.split("/")
        #     cpf = employee.pessoa_fisica.cpf
        #     dt_init = datetime.date(int(year_start), int(month_start), 1)
        #     dt_end = datetime.date(
        #         int(year_end),
        #         int(month_end),
        #         calendar.monthrange(int(year_end), int(month_end))[1],
        #     )
        #     VRETORNORESUME = cursor.var(oracledb.CURSOR).var
        #     cursor.callproc(
        #         "resumo_folhaponto",
        #         (
        #             cpf,
        #             dt_init.strftime("%d/%m/%Y"),
        #             dt_end.strftime("%d/%m/%Y"),
        #             VRETORNORESUME,
        #         ),
        #     )
        #     cursor_data_resume = VRETORNORESUME.getvalue()

        #     columns_resume = [col[0] for col in cursor_data_resume.description]

        #     dict_value_resume = [
        #         dict(zip(columns_resume, row)) for row in cursor_data_resume.fetchall()
        #     ]

        # return dict_value_resume[0]

    except Exception as err:
        log.exception(err)
        raise err
