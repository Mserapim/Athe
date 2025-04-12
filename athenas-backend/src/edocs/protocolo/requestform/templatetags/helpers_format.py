# -*- coding: utf-8 -*-
import locale

from django import template

register = template.Library()


@register.filter(name="currency_format")
def currency_format(value):
    return locale.currency(value, grouping=True)


@register.filter(name="number_format")
def number_format(value):
    return locale.format_string("%0.2f", value, grouping=True)
