# -*- coding: utf-8 -*-
from contrib.utils import DateUtils


def nil_unicode(x, v):
    return str(x) if x is not None else v


def nil_new_unicode(x, v):
    return "%s" % x if x is not None else v


def nil_str(x, v):
    return str(x) if x is not None else v


def nil_pk(x, v):
    return x.pk if x is not None else v


def nil_datetime(x, v):
    return DateUtils.datetime_to_str(x) if x is not None else v


def nil_date(x, v):
    return DateUtils.date_to_str(x) if x is not None else v


def nil_person_user(user, value=None):
    if user and user.servidor:
        return user.servidor.pessoa_fisica.nome
    else:
        return value


def nil_display(inst, field, value):
    def foo():
        return value

    return getattr(inst, "get_{0}_display".format(field), foo)()


def nil_new_display(inst, field, value):
    def foo():
        return value

    return "%s" % getattr(inst, "get_{0}_display".format(field), foo)()
