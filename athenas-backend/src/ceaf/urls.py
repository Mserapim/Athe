from django.urls import path

from ceaf.apiv2.views import (
    CapacitacaoListView,
    CapacitacaoApiCore,
    CapacitacaoDetailView,
    ParticipanteListView,
    ParticipanteApiCore,
    ParticipanteDetailView,
)

urlpatterns = [
    path("capacitacoes/", CapacitacaoListView.as_view(), name="capacitacoes"),
    path("capacitacao/", CapacitacaoDetailView.as_view(), name="capacitacao"),
    path("capacitacao/criar", CapacitacaoApiCore.as_view(), name="criar-capacitacao"),
    path("capacitacao/editar", CapacitacaoApiCore.as_view(), name="editar-capacitacao"),
    path("capacitacao/apagar", CapacitacaoApiCore.as_view(), name="apagar-capacitacao"),
    path("participantes/", ParticipanteListView.as_view(), name="participantes"),
    path("participante/", ParticipanteDetailView.as_view(), name="participante"),
    path(
        "participante/criar", ParticipanteApiCore.as_view(), name="criar-participante"
    ),
    path(
        "participante/editar", ParticipanteApiCore.as_view(), name="editar-participante"
    ),
    path(
        "participante/apagar", ParticipanteApiCore.as_view(), name="apagar-participante"
    ),
]
