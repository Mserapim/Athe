# -*- coding: utf-8 -*-
from django import template
import datetime

register = template.Library()


@register.filter(name="get_value")
def get_value(dictionary, key):
    if isinstance(dictionary.get(key), datetime.date):
        return dictionary.get(key).strftime("%d/%m/%Y")
    if dictionary.get(key) is None:
        return ""
    return dictionary.get(key)


@register.filter(name="get_week")
def get_week(value):
    DAYS_WEEK = ("DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB")
    return DAYS_WEEK[int(value) - 1]
