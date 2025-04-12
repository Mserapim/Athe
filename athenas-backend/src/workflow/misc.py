# -*- coding:utf-8 -*-
from importlib import import_module


def extract_params(request):
    params = dict(request.REQUEST).copy()
    exclude = ["start", "end", "limit", "_dc"]
    for key in exclude:
        if key in params:
            del params[key]
    return params


def get_slice(request):
    start = int(request.REQUEST.get("start", 0))
    end = int(request.REQUEST.get("limit", 50)) + start
    return start, end


def vars(obj):
    return dict([[k, v] for k, v in obj.__dict__.items() if not k.startswith("_")])


def evaluate(canonical_name):
    module_path = ".".join(canonical_name.split(".")[:-1])
    model_name = canonical_name.split(".")[-1]
    _module = import_module(module_path)

    return getattr(_module, model_name)
