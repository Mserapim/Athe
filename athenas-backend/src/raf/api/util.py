# -*- coding: utf-8 -*-


def request_params(me):
    params = {}

    for key in list(me.request.POST.keys()):
        value = me.request.POST.getlist(key)
        if len(value) > 1:
            params.update({key: value})
        else:
            params.update({key: value[0]})

    return params
