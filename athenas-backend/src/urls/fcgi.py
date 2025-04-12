# -*- coding: utf-8 -*-

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

import static

from contrib import router

STATIC_PATH = static.__path__[0]
STATIC_FILE_INDEX = True

urlpatterns = (
    re_path(
        r"^static/(?P<path>.*)$",
        "django.views.static.serve",
        {"document_root": STATIC_PATH, "show_indexes": STATIC_FILE_INDEX},
    ),
    re_path(r"^$", router.router_function),
    re_path(r"^(.*)/$", router.router_function),
)
