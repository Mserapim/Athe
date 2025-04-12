from django.urls import path
from rh.antiguidades.apiv2.views import AntiguidadesView, AtualizarAntiguidadesView


urlpatterns = [
    path("lista/", AntiguidadesView.as_view(), name="antiguidades"),
    path(
        "atualizar_lista/",
        AtualizarAntiguidadesView.as_view(),
        name="atualizar-antiguidades",
    ),
]
