# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter(name="format_list_phone_number")
def format_list_phone_number(value):
    if value:
        return "/".join([t.numero for t in value])
    else:
        return "Telefone não definido"
