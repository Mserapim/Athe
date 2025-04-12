from django.urls import path

from rh.mov_carreira.apiv2.views import (
    MembroProbatorioAfastamentosView,
    MembrosEstagioProbatorioView,
)

urlpatterns = [
    path(
        "membros-estagio-probatorio/",
        MembrosEstagioProbatorioView.as_view(),
        name="lista_membros_estagio_probatorio",
    ),
    path(
        "membros-estagio-probatorio/afastamentos/",
        MembroProbatorioAfastamentosView.as_view(),
        name="lista_afastamentos_membros_estagio_probatorio",
    ),
]
