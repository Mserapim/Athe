
# -*- coding:utf-8 -*-

from django.urls import re_path, path, include
from django.conf import settings
from django.views import static  
from contrib import router

STATIC_PATH = static.__path__[0]
STATIC_FILE_INDEX = True

urlpatterns = [
    re_path(
        r"^static/(?P<path>.*)$",
        static.serve,  
        {"document_root": STATIC_PATH, "show_indexes": STATIC_FILE_INDEX},
    ),
    re_path(r"^$", router.router_function),
    re_path(r"^(.*)/$", router.router_function),

    
    path("athenas/api/v2/", include("auth.apiv2.urls")),
]











# -*- coding:utf-8 -*-

# try:
#     from django.urls import re_path
# except ImportError:
#     from django.conf.urls import url as re_path

# from django.conf import settings

# import static

# from contrib import router

# STATIC_PATH = static.__path__[0]
# STATIC_FILE_INDEX = True

# urlpatterns = (
#     re_path(
#         r"^static/(?P<path>.*)$",
#         "django.views.static.serve",
#         {"document_root": STATIC_PATH, "show_indexes": STATIC_FILE_INDEX},
#     ),
#     re_path(r"^$", router.router_function),
#     re_path(r"^(.*)/$", router.router_function),
# )
