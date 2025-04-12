from django.urls import path
from painel_controle.configuracoes.apiv2.views import (
    ConfiguracaoDePontoCoreView,
    ConfiguracaoDePontoView,
    ConfiguracaoDePontoDetailView,
)

urlpatterns = [
    path(
        "configuracoes-de-ponto/",
        ConfiguracaoDePontoView.as_view(),
        name="configuracoes-de-ponto",
    ),
    path(
        "configuracao-de-ponto/",
        ConfiguracaoDePontoDetailView.as_view(),
        name="configuracoes-de-ponto-detail",
    ),
    path(
        "configuracao-de-ponto/criar/",
        ConfiguracaoDePontoCoreView.as_view(),
        name="configuracao-de-ponto-criar",
    ),
    path(
        "configuracao-de-ponto/editar/",
        ConfiguracaoDePontoCoreView.as_view(),
        name="configuracao-de-ponto-editar",
    ),
    path(
        "configuracao-de-ponto/apagar/",
        ConfiguracaoDePontoCoreView.as_view(),
        name="configuracao-de-ponto-apagar",
    ),
]
