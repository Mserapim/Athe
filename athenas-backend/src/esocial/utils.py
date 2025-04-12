# -*- coding: utf-8 -*-
import datetime
import json
import re
from decimal import Decimal

import xmltodict
from django.conf import settings
from lxml import etree

from contrib.utils import DateUtils, getLogger
from standard.models import Configuration
from collections import defaultdict


log = getLogger(__name__)


def validation_xml_schema_show(verbose=False):
    from esocial.models import BatchEvent, Event

    if verbose:
        events = Event.objects.all()  # .not_validated()
        print(
            ">>> validation_xml_schema - para todos eventos (%s) e mostrando erros que ocorreram..."
            % events.count()
        )
        log.debug(
            ">>> validation_xml_schema - para todos eventos (%s) e mostrando erros que ocorreram..."
            % events.count()
        )
        errors = False
        for event in events:
            try:
                event.event.validation_xml_schema(assert_test=True)
            except Exception as err:
                errors = True
                log.exception(err)
        print(
            ">>> validation_xml_schema finalizada %s erros."
            % ("com" if errors else "sem")
        )
        log.debug(
            ">>> validation_xml_schema finalizada %s erros."
            % ("com" if errors else "sem")
        )

        batchevents = BatchEvent.objects.filter()
        print(
            ">>> validation_xml_schema - para todos lotes de eventos (%s) e mostrando erros que ocorreram..."
            % batchevents.count()
        )
        log.debug(
            ">>> validation_xml_schema - para todos lotes de eventos (%s) e mostrando erros que ocorreram..."
            % batchevents.count()
        )
        errors = False
        for batchevent in batchevents:
            try:
                batchevent.validation_xml_schema(assert_test=True)
            except Exception:
                errors = True
        print(
            ">>> validation_xml_schema finalizada %s erros."
            % ("com" if errors else "sem")
        )
        log.debug(
            ">>> validation_xml_schema finalizada %s erros."
            % ("com" if errors else "sem")
        )


def get_acronyms_from_kind(kind=[]):
    """Este método retorna os acrônimos dos eventos de acordo com o kind informado.
        kind possíveis: 'EEMP', 'TI', 'CF', 'FP', 'TOT', 'SST', 'STPC', 'REP', 'FEP', 'EBS'

    Returns:
        events (list):"""
    from esocial.const import EVENT_KIND
    from esocial.models import get_current_config

    config = get_current_config()

    events = []
    for k in kind:
        for event in EVENT_KIND.get(k):
            if config.generate_events.filter(label__iexact=event).exists():
                events.append(event)
    return events


def esocial_environment():
    """Deve ser configurado como 1 no config.json para que funcione em PRODUÇÃO ESOCIAL.
    Assim também será possível escolher PRODUÇÃO RESTRITA nas configurações do Athenas. De outra forma só aceitará PRODUÇÃO RESTRITA.
        Identificação do ambiente:
        1 - Produção;
        2 - Produção restrita.
        Valores Válidos: 1, 2.
    """
    environment = settings.ESOCIAL_ENVIRONMENT

    if environment == 2:
        return environment

    cfg = Configuration.get_or_create("esocial")
    return int(cfg.get("esocial_environment", default="2", type_of=1))


def change_value(value):
    """Este método encontra o valor bruto de value a partir do tipo. Apenas set será modificado para set.
    Os demais terão sua representação em str.

    Args:
        value (_type_): value, default é str()

    Returns:
        _type_: value
    """
    if type(value) is datetime.datetime:
        value = DateUtils.datetime_to_str(value)
    elif type(value) is datetime.date:
        value = DateUtils.date_to_str(value)
    elif type(value) is set:
        value = list(value)
    else:
        value = f"{value}"

    if type(value) is list:
        new_list = []
        for vl in value:
            new_list.append(change_value(vl))
        value = new_list
    return value


def convert_diff_content(diff_content):
    """Este método converte os valores em diff_content para str.

    Args:
        diff_content (dict): diff_content do Event

    Returns:
        dict: diff_content
    """
    for key in diff_content:
        if type(diff_content) is dict:
            value = diff_content.get(key)
        else:
            value = key
        if type(value) is list and len(value) > 1:
            old = change_value(value[0])
            new = change_value(value[1])
            new_list = [old, new]
            if type(key) is str:
                diff_content.update({key: new_list})
            else:
                return new_list
        elif type(value) is list:
            rs = convert_diff_content(value)
            if type(key) is str:
                diff_content.update({key: rs})
            else:
                return rs
        else:
            rs = convert_diff_content(value)
            if type(key) is str:
                diff_content.update({key: rs})
            else:
                return rs
    return diff_content


def format_diff_content(diff):
    """Este método formata o diff convertendo os valores para str.

    Args:
        diff (dict): diff_content

    Returns:
        dict: diff_content
    """
    diff = diff.replace("'", '"')

    """datetime, date"""
    mfound = re.finditer("datetime\.date\(([^)]*)\)", diff)
    for value in mfound:
        value = DateUtils.date_to_str(eval(value.group(0)))
        diff = re.sub(r"datetime\.date\(([^)]*)\)", f'"{value}"', diff, count=1)

    """Decimal"""
    mfound = re.finditer("Decimal\(([^)]*)\)", diff)
    for value in mfound:
        value = f"{eval(value.group(0))}"
        diff = re.sub(r"Decimal\(([^)]*)\)", f'"{value}"', diff, count=1)

    """set, {}"""
    mfound = re.finditer('set\(([^)]*)\)|([\{])("[0-9]+"?,?\s?)+[\}]', diff)
    for value in mfound:
        value = list(eval(value.group(0)))
        diff = re.sub(
            r"set\(([^)]*)\)|([\{])(\"[0-9]+\"?,?\s?)+[\}]", f"{value}", diff, count=1
        )

    find_pipe = diff.find("|")
    diff = diff.replace("} | ", " | ")
    diff = diff.replace(" | NO_RESTRICTION", ', "NO_RESTRICTION": "NO_RESTRICTION"')
    diff = diff.replace(" | SAME_EVENT", ', "SAME_EVENT": "SAME_EVENT"')
    diff = diff.replace(
        " | EQUAL_VALIDITY_DIFF_CONTENT",
        ', "EQUAL_VALIDITY_DIFF_CONTENT": "EQUAL_VALIDITY_DIFF_CONTENT"',
    )
    diff = diff.replace(
        " | DIFF_VALIDITY_DIFF_CONTENT",
        ', "DIFF_VALIDITY_DIFF_CONTENT": "DIFF_VALIDITY_DIFF_CONTENT"',
    )
    diff = diff.replace(
        " | DIFF_VALIDITY_SAME_CONTENT",
        ', "DIFF_VALIDITY_SAME_CONTENT": "DIFF_VALIDITY_SAME_CONTENT"',
    )
    diff = diff.replace(
        " | DIFF_VALIDITY_END_SAME_CONTENT",
        ', "DIFF_VALIDITY_END_SAME_CONTENT": "DIFF_VALIDITY_END_SAME_CONTENT"',
    )
    diff = diff.replace(
        " | DOESNT_EXIST_REFERENCE",
        ', "DOESNT_EXIST_REFERENCE": "DOESNT_EXIST_REFERENCE"',
    )
    diff = diff.replace(" | NOTHING_TODO", ', "NOTHING_TODO": "NOTHING_TODO"')
    diff = diff.replace(" | EXCLUDE_EVENT", ', "EXCLUDE_EVENT": "EXCLUDE_EVENT"')
    diff = diff.replace(" | EQUAL_VALIDITY", ', "EQUAL_VALIDITY": "EQUAL_VALIDITY"')
    diff = diff.replace(
        " | DIFF_VALIDITY_END", ', "DIFF_VALIDITY_END": "DIFF_VALIDITY_END"'
    )
    diff = diff.replace(" | DIFF_VALIDITY", ', "DIFF_VALIDITY": "DIFF_VALIDITY"')
    diff = diff.replace("{, ", "{")
    if diff and find_pipe > -1:
        diff += "}"

    diff = diff.replace("'", '"').replace("None", '"None"')
    diff = diff.replace('""None""', '"None"')
    return diff


def redefine_diff_dict(diff):
    """Este método dedefine o diff substituindo as chaves duplicadas e por "valor_antigo" e "valor_novo".

    Args:
        diff (dict): diff_content

    Returns:
        dict: diff redefinido
    """
    xml_new = {"diff": {}}
    for key in diff:
        value = diff.get(key)
        nm_key = f"{key}".lower()
        if type(value) in (list, tuple):
            old = value[0]
            new = None
            if len(value) > 1:
                new = value[1]
            buff = {nm_key: {"valor_antigo": old}}
            if new:
                buff.get(nm_key).update({"valor_novo": new})
            xml_new.get("diff").update(buff)
        elif type(value) is dict:
            rs = redefine_diff_dict(value)
            diff.update({key: rs})
            return diff
        else:
            buff = {nm_key: value}
            xml_new.get("diff").update(buff)
    return xml_new


def process_xml_diff(xml_diff):
    """Este método processa o xml_diff adicionando um agrupador chamado "diff". Utiliza format_diff_content para traduzir cada valor em str.

    Args:
        xml_diff (dict): xml_diff é o diff_content do Event.

    Returns:
        str: _description_
    """
    xml_diff = format_diff_content(xml_diff)
    if xml_diff:
        xml_diff = {"diff": json.loads(xml_diff)}
        diff = xml_diff.get("diff", {})
        xml_diff = redefine_diff_dict(diff)
        xml_diff = xmltodict.unparse(xml_diff)
        xml_diff = etree.fromstring(
            xml_diff.replace('<?xml version="1.0" encoding="utf-8"?>', "")
        )
        xml_diff = etree.tostring(xml_diff, pretty_print=True, method="xml").decode()
    return xml_diff


def agrupador_lancamentos_pensao(query_dict):
    """Este método agrupa valores por cpf e evento do lançamento de pensão.
    Args:
        query_dict (dict): dicionário de dados do lançamento de pensão
    Returns:
        dict
    """
    agrupador_data = defaultdict(int)
    # Agrupe e some os valores
    for data in query_dict:
        key = (data["cid"], data["evento__tags__label"])
        total_pens = data["correct_valor"]
        agrupador_data[key] += total_pens
    resultado = [
        {"cid": cid, "tag": tag, "total_pens": total_pens}
        for (cid, tag), total_pens in agrupador_data.items()
    ]
    return resultado
