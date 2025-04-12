# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter(name="creditor_format")
def creditor_format(value):
    if len(str(value)) == 10:
        return "{}{}{}{}.{}{}{}{}{}-{}".format(*str(value))

    return value
