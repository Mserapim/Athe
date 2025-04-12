# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


@register.filter(name="cpf")
def cpf_filter(value):

    if not value.isdigit():
        return value

    segments = []
    size = len(value)

    marks = ((0, 3, "."), (3, 6, "."), (6, 9, "-"), (9, 11, None))
    for ps, pe, sep in marks:
        if ps <= size:
            segments.append(value[ps : pe if pe <= size else size])
            if sep and pe < size:
                segments.append(sep)

    return "".join(segments)


@register.filter(name="cnpj")
def cnpj_filter(value):
    segments = []
    size = len(value)

    marks = ((0, 2, "."), (2, 5, "."), (5, 8, "/"), (8, 12, "-"), (12, 14, None))
    for ps, pe, sep in marks:
        if ps <= size:
            segments.append(value[ps : pe if pe <= size else size])
            if sep and pe < size:
                segments.append(sep)

    return "".join(segments)
