from django.urls import path, include
from common.usefulday.apiv2.views.nonworkingday import (
    NonWorkingDayView,
    DiasUteisView,
    DiasUteisApicoreView,
    LocalidadeSelecionadaDiaUtilAPIList,
    DiasUteisFiltroAnosACopiarView,
    DiasUteisFiltroTiposACopiarView,
    DiasUteisDetailView,
)
from rest_framework import routers

urlpatterns = [
    # usefulday
    path("usefulday/", NonWorkingDayView.as_view(), name="usefulday"),
    path("dias-uteis/", DiasUteisView.as_view(), name="dias_uteis"),
    path("dia-util/", DiasUteisDetailView.as_view(), name="detalhes_dia_util"),
    path("dia-util/criar/", DiasUteisApicoreView.as_view(), name="criar_dia_util"),
    path("dia-util/editar/", DiasUteisApicoreView.as_view(), name="editar_dia_util"),
    path("dia-util/apagar/", DiasUteisApicoreView.as_view(), name="apagar_dia_util"),
    path("dia-util/copiar/", DiasUteisApicoreView.as_view(), name="copiar_dia_util"),
    path(
        "dia-util/localidades/selecionadas/",
        LocalidadeSelecionadaDiaUtilAPIList.as_view(),
        name="localidades_selecionadas",
    ),
    path(
        "dia-util/filtro-anos-copiar/",
        DiasUteisFiltroAnosACopiarView.as_view(),
        name="filtro_anos_copiar",
    ),
    path(
        "dia-util/filtro-tipos-copiar/",
        DiasUteisFiltroTiposACopiarView.as_view(),
        name="filtro_tipos_copiar",
    ),
]
