from rh.registerpoint.apiv2.views import (
    FolhaPontoCoreView,
    FolhaPontoJustificativaCoreView,
    FolhaPontoJustificativasView,
    FolhaPontoLotacaoView,
    FolhaPontoMarcacoesView,
    FolhaPontoServidoresView,
    FolhaPontoTipoJustificativaView,
    PVFRegisterPointViewSet,
    PVFLastRegisterView,
    FolhaPontoTipoDiaView,
    PermissaoAdicionarJustificativaView,
)
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()

router.register("registers", PVFRegisterPointViewSet, basename="registers")

urlpatterns = [
    path("", include(router.urls)),
    path("last-beats/", PVFLastRegisterView.as_view(), name="last_registers"),
]

urlpatterns_folha_ponto = [
    path(
        "servidores/", FolhaPontoServidoresView.as_view(), name="folha-ponto-servidores"
    ),
    path("tipos-dias/", FolhaPontoTipoDiaView.as_view(), name="folha-ponto-tipos-dias"),
    path(
        "marcacoes/", FolhaPontoMarcacoesView.as_view(), name="folha-ponto-marcacaoes"
    ),
    path(
        "ignorar-batida/",
        FolhaPontoCoreView.as_view(),
        name="folha-ponto-ignorar-batida",
    ),
    path(
        "justificativas/",
        FolhaPontoJustificativasView.as_view(),
        name="folha-ponto-justificativas",
    ),
    path(
        "justificativas/permissao/",
        PermissaoAdicionarJustificativaView.as_view(),
        name="permissao-justificativa",
    ),
    path(
        "justificativa/criar/",
        FolhaPontoJustificativaCoreView.as_view(),
        name="folha-ponto-justificativa-criar",
    ),
    path(
        "justificativa/cancelar/",
        FolhaPontoJustificativaCoreView.as_view(),
        name="folha-ponto-justificativa-cancelar",
    ),
    path(
        "tipos-justificativas/",
        FolhaPontoTipoJustificativaView.as_view(),
        name="folha-ponto-tipos-justificativas",
    ),
    path("lotacoes/", FolhaPontoLotacaoView.as_view(), name="folha-ponto-lotacoes"),
]
