# -*- coding: utf-8 -*-
"""
Módulo que contém a definição dos métodos:

:Métodos:
   :func:`br_number`,
   :func:`br_money`,
   :func:`br_month`,
   :func:`br_abbreviated_month`,
   :func:`br_weekday`,

"""

from contrib.utils import getLogger

log = getLogger(__name__)


def br_number(value):
    """
    Método para converter números em formato padrão Brasileiro.

    :param value: Valor a ser convertido.
    :type value: Number

    :returns:  String -- String com a representação do número formatado.

    >>> print br_number(123,456.789)
    123.456,789
    """

    before, after = str(value).split("."), 0
    if len(before) > 1:
        after, before = before[1], before[0]

    if isinstance(before, list):
        before = "".join(before)
    before = list(str(before))
    before.reverse()

    slices = []
    for i in range(0, len(before), 3):
        _slice = before[i : i + 3]
        _slice.reverse()
        _slice = "".join(_slice)
        slices.append(_slice)
    slices.reverse()

    if int(after) > 0:
        return "%s,%s" % (".".join(slices), after)
    return ".".join(slices)


def br_money(value):
    """Método para converter números em formato padrão Brasileiro, acrescido do símbolo de moeda.

    :param value: Valor a ser convertido.
    :type value: Number

    :returns:  String -- String com a representação do número formatado.

    >>> print br_money(123,456.789)
    R$ 123.456,789
    """
    return "R$ %s" % br_number(value)


def br_month(month):
    """Método para retornar o nome de um determinado mês por extenso, a partir de seu índice.

    :param month: Índice do mês.
    :type month: Number

    :returns:  String -- Nome do mês por extenso.

    >>> print br_month(10)
    Novembro
    """
    months = dict(
        enumerate(
            [
                "Janeiro",
                "Fevereiro",
                "Março",
                "Abril",
                "Maio",
                "Junho",
                "Julho",
                "Agosto",
                "Setembro",
                "Outubro",
                "Novembro",
                "Dezembro",
            ]
        )
    )
    return months.get(int(month) - 1)


def br_abbreviated_month(month):
    """Método para retornar a abreviatura do nome de um determinado mês, a partir de seu índice.

    :param month: Índice do mês.
    :type month: Number

    :returns:  String -- Abreviatura do nome do mês.

    >>> print br_abbreviated_month(10)
    Nov
    """
    return br_month(month)[:3]


def br_weekday(day):
    """Método para retornar o nome de um determinado dia da semana por extenso, a partir de seu índice.

    :param day: Índice do dia da semana.
    :type day: Number

    :returns:  String -- Nome do dia da semana.

    >>> print br_weekday(0)
    Domingo
    """

    days = dict(
        enumerate(
            [
                "Domingo",
                "Segunda-Feira",
                "Terça-Feira",
                "Quarta-Feira",
                "Quinta-Feira",
                "Sexta-Feira",
                "Sábado",
            ]
        )
    )
    return days.get(day)
