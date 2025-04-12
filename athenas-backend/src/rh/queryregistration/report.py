# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from ged.models import Arquivo
from contrib.utils import getLogger
from default.websocket import RemoteEmmiter
from django.db import connection
from rh.queryregistration.const import STYLE_HEAD_ROW, STYLE_DATA_ROW
from rh.queryregistration.ged_file import GedFile
from datetime import datetime, date
import base64
from standard.models import Choice
from rh.queryregistration.models import Consultation, TagField
from rh.models import Cargo, Servidor
from rh.gfp.models import Folha, Evento, FolhaEvento
from rh.cadastralquality.models import RegistrationQuery
import xlwt


log = getLogger(__name__)


def get_data_report(sql, params, pk, title, save_log):
    """realiza a extração dos dados da consulta sql"""
    change_data_value(params)
    value = dictfetchall(
        sql.replace("UPDATE", "").replace("DELETE", "").replace("DROP", ""),
        params,
        pk,
        save_log,
    )
    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    values = {
        "title": title,
        "data": value,
        "keys": list(value[0].keys()) if value else "",
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values


def get_data_report_xls(sql, params, pk, title, save_log):
    """realiza a extração dos dados da consulta sql para relatório xls"""
    value = dictfetchall(
        sql.replace("UPDATE", "").replace("DELETE", "").replace("DROP", ""),
        params,
        pk,
        save_log,
    )
    values = {
        "title": title,
        "data": value,
        "keys": list(value[0].keys()) if value else "",
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
    }
    return values


def get_data_report_xls_full(queries, params, save_log):
    """realiza a extração dos dados da consulta sql para relatório xls"""
    data = None
    for query in queries:
        sql = query["sql"]
        pk = query["pk"]
        if not data:
            data = dictfetchall(
                sql.replace("UPDATE", "").replace("DELETE", "").replace("DROP", ""),
                params,
                pk,
                save_log,
            )
        else:
            data = data + dictfetchall(
                sql.replace("UPDATE", "").replace("DELETE", "").replace("DROP", ""),
                params,
                pk,
                save_log,
            )

    values = {
        "title": "Qualidade Cadastral",
        "data": data,
        "keys": list(data[0].keys()) if data else "",
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
    }
    return values


def get_filename(filename, identifier):
    file = False
    try:
        file = Arquivo.objects.get(filename=filename, user=get_current_user())
        file = GedFile(file.file, identifier)
    except:
        log.info("Arquivo não encontrado!")
    return file


def create_gedfile(filename, buffer, mimetype, identifier):
    ged = None
    signature = Arquivo.hash_buffer(buffer)
    gedfile = GedFile(signature, identifier)
    ged = Arquivo(
        file=signature,
        filename=filename,
        mimetype=mimetype,
        user=get_current_user(),
        acesso=3,
    )
    gedfile.save_file(gedfile, signature, buffer)
    ged.save(ignore_cache=True)
    return gedfile


def remote_emmiter(download, task, name_observer=None):
    if download and task.state != "failed":
        RemoteEmmiter.emmit_for_user(
            task.owner,
            name_observer if name_observer else "query-report",
            path=f"/athenas/QueryReport/download_file/?uuid={task.uuid}",
            filename="",
            status="success",
        )
    else:
        RemoteEmmiter.emmit_for_user(
            task.owner,
            name_observer if name_observer else "query-report",
            path=f"/athenas/QueryReport/download_file/?uuid={task.uuid}",
            filename="",
            status="failed",
        )


def create_file_xls(values_data, filepath):
    work_book = xlwt.Workbook(encoding="utf-8")
    work_book.owner = get_current_user().username
    key_sheet = 1
    for values in values_data:
        work_sheet = work_book.add_sheet("planilha" + str(key_sheet))
        style_head_row = xlwt.easyxf(STYLE_HEAD_ROW)
        style_data_row = xlwt.easyxf(STYLE_DATA_ROW)
        style_date_row = xlwt.easyxf(STYLE_DATA_ROW)
        style_date_row.num_format_str = "dd/mm/yyyy"
        # style_green = xlwt.easyxf("pattern: fore-colour 0x11, pattern solid;")
        # style_red = xlwt.easyxf(" pattern: fore-colour 0x0A, pattern solid;")
        keys = values.get("keys")
        for i in range(len(keys)):
            work_sheet.write(0, i, str(keys[i]).upper(), style_head_row)

        row = 1
        for value in values.get("data"):
            column = 0
            for item in value:
                data = value[item]
                colwidth = (
                    256 * len(str(data)) if 256 * len(str(data)) < 65536 else 65535
                )
                if colwidth > work_sheet.col(column).width:
                    work_sheet.col(column).width = colwidth
                if isinstance(data, date):
                    work_sheet.write(row, column, data, style_date_row)
                else:
                    work_sheet.write(row, column, data, style_data_row)
                column = column + 1
            row = row + 1
        key_sheet = key_sheet + 1

    if not filepath:
        return work_book.get_biff_data()

    return work_book.save(filepath)


def dictfetchall(sql, params, pk, save_log):
    "Este metódo realiza a consulta sql e retorna um dicionário de dados"
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params))
            if save_log:
                Consultation.save_log_sql(pk, cursor.cursor.query)
            columns = [col[0] for col in cursor.description]
            dict_value = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return dict_value

    except Exception as err:
        if save_log:
            Consultation.save_log_sql(pk, cursor.cursor.query)
        log.exception(err)
        raise err


def change_data_value(params):
    """Este metódo faz o tratamento de valores booleanos para a consulta sql"""
    for param in params:
        if isinstance(params[param], list):
            params[param] = tuple(params[param])
        elif params[param] == "yes":
            params[param] = True
        elif params[param] == "no":
            params[param] = False


def set_params_sql(params, tags, sql):
    for tag in tags:
        key_tag = tag.split(":")[0].replace("?", "").replace(" ", "_")
        result = TagField.objects.get(key_tag=key_tag)
        if result and result.many:
            if result.type_tag == "checkboxchoicefield":
                name = result.choice_id.split(".")[1]
                if params.get(tags[tag]):
                    params[tags[tag]] = list(
                        Choice.objects.filter(
                            name=name, value__in=params[tags[tag]]
                        ).values_list(result.value, flat=True)
                    )
                else:
                    params[tags[tag]] = list(
                        Choice.objects.filter(name=name).values_list(
                            result.value, flat=True
                        )
                    )

            elif result.type_tag == "multiselectfield":
                if params.get(tags[tag]):
                    if isinstance(params[tags[tag]], str):
                        params[tags[tag]] = params[tags[tag]].split(" ")
                    params[tags[tag]] = list(
                        eval(result.model)
                        .objects.filter(pk__in=params[tags[tag]])
                        .values_list(result.value, flat=True)
                    )
                else:
                    params[tags[tag]] = list(
                        eval(result.model)
                        .objects.filter()
                        .values_list(result.value, flat=True)
                    )
        elif result.sql_in and result.type_tag == "choicefield":
            if params[tags[tag]] == "9999":
                name = result.choice_id.split(".")[1]
                app = result.choice_id.split(".")[0]
                params[tags[tag]] = list(
                    Choice.objects.filter(
                        name=name, app_label=app, active=True
                    ).values_list(result.value, flat=True)
                )
            else:
                value = [params[tags[tag]]]
                params[tags[tag]] = tuple(value)

        sql = sql.replace("$" + tag + "$", "%(" + tags[tag] + ")s")
    return [params, sql]
