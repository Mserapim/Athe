# -.- coding: utf-8 -.-
from contrib.daterange import NewDateRange
from esocial.const import DIFF_VALIDITY, DIFF_VALIDITY_END, EQUAL_VALIDITY


def limits_from_date(date):
    """Este método retorna os limites de um NewDateRange(first, last).

    Returns:
        dr.first (date):
        dr.last (date):
    """
    dr = NewDateRange.from_month(date.year, date.month)
    return dr.first, dr.last


def validity_between_events(dr_event, dr_other):
    """Este método avalia a validade entre dois NewDateRange de acordo com as necessidades da análise de dr_eventos e
    dr_eventos extraídos.

    Params:
        dr_event(NewDateRange):
        dr_other(NewDateRange):
    """
    rs = EQUAL_VALIDITY
    if dr_event != dr_other:
        rs = DIFF_VALIDITY
        if dr_event.first == dr_other.first:
            rs = DIFF_VALIDITY_END
    return rs


def format_reference(dt):
    return dt.strftime("%Y-%m") if dt else None


def all_fields_many_to_many_rel(instance):
    for field in instance._meta.get_fields():
        if field.many_to_many and hasattr(field, "related_name") and field.related_name:
            yield field


def extract_dates(dates):
    """Este método extrai as datas de um objeto(dates). Caso se enviado lista, extrai as datas de cada item.
    Caso não seja lista, dates será considerado como uma data.

    Params:
        start_date(date):
        financial_effect_date(date):
    """
    start_date = None
    financial_effect_date = None
    if type(dates) is list:
        if len(dates) > 0:
            financial_effect_date = dates[1] if len(dates) > 1 else dates[0]
            start_date = dates[0]
    else:
        start_date = dates
    return start_date, financial_effect_date
