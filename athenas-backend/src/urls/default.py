import os

try:
    from django.urls import re_path, include
except ImportError:
    from django.conf.urls import url as re_path, include

from django.conf import settings
from contrib import router

from auth.sso.views import login_callback, login_redirect

from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from anotacao_pessoal.urls import (
    urlpatterns_anotacao_pessoal,
    urlpatterns_anotacoes_pessoais,
)
from rh.pvf.urls import urlpatternsvdf
from rh.registerpoint.urls import urlpatterns_folha_ponto


STATIC_PATH = os.path.sep.join([getattr(settings, "BASE_DIR"), "static"])
STATIC_FILE_INDEX = True

urlpatterns = [
    re_path(
        "oauth/login/callback/", login_callback, name="oauth2_client_login_callback"
    ),
    re_path("accounts/login/", login_redirect, name="oauth2_client_login_redirect"),
    re_path(settings.CONTEXT + "/api/v2/rh/", include("rh.urls")),
    re_path(settings.CONTEXT + "/api/v2/vdf/", include(urlpatternsvdf)),
    re_path(settings.CONTEXT + "/api/v2/report/", include("reports.urls")),
    re_path(settings.CONTEXT + "/api/v2/usefulday/", include("common.urls")),
    re_path(settings.CONTEXT + "/api/v2/ged/", include("ged.urls")),
    re_path(
        settings.CONTEXT + "/api/v2/anotacao-pessoal/",
        include(urlpatterns_anotacao_pessoal),
    ),  # urls do vdf
    re_path(
        settings.CONTEXT + "/api/v2/anotacoes-pessoais/",
        include(urlpatterns_anotacoes_pessoais),
    ),
    re_path(settings.CONTEXT + "/api/v2/ceaf/", include("ceaf.urls")),
    re_path(settings.CONTEXT + "/api/v2/auth/", include("auth.urls")),
    re_path(
        settings.CONTEXT + "/api/v2/painel-controle/controle-acesso/",
        include("painel_controle.controle_acesso.urls"),
    ),
    re_path(
        settings.CONTEXT + "/api/v2/painel-controle/configuracoes/",
        include("painel_controle.configuracoes.urls"),
    ),
    re_path(settings.CONTEXT + "/api/v2/diarias/", include("diarias.urls")),
    re_path(settings.CONTEXT + "/api/v2/adm/", include("adm.urls")),
    re_path(settings.CONTEXT + "/api/v2/esocial/", include("esocial.urls")),
    re_path(
        settings.CONTEXT + "/api/v2/folha-ponto/", include(urlpatterns_folha_ponto)
    ),
    re_path(settings.CONTEXT + "/api/v2/auditoria/", include("auditoria.urls")),
    re_path(settings.CONTEXT + "/api/v2/standard/", include("standard.urls")),
    # DOC API
    re_path(
        settings.CONTEXT + "/api/v2/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    re_path(
        settings.CONTEXT + "/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(
        settings.CONTEXT + "/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    re_path("/healthcheck/", include("health_check.urls")),
    re_path(r"^" + settings.CONTEXT + "/$", router.router_function),
    re_path(r"^" + settings.CONTEXT + "/(.*)/$", router.router_function),
]
