from django.urls import path

from adm.apiv2.views import NotificacaoHermesView, UsuarioApiAdmView, AssinadorAthenas
from common.services.apiv2.views.servicos import (
    ServicosView,
    ServicosDetailView,
    ServicosApicoreView,
    MensagensServicoView,
)
from common.services.apiv2.views.historico_servicos import (
    HistoricoServicosView,
    HistoricoServicoDetailView,
)

from standard.apiv2.views.classcodes import (
    ClasscodesView,
    ClasscodesDetailView,
    ClasscodesApicoreView,
    TiposClasscodesView,
)

urlpatterns = [
    path("usuario/", UsuarioApiAdmView.as_view(), name="adm_detalhes_usuario"),
    path("assinador/", AssinadorAthenas.as_view(), name="adm_assinador_athenas"),
    path(
        "notificacoes-hermes/",
        NotificacaoHermesView.as_view(),
        name="notificacoes_hermes",
    ),
    path("servicos/", ServicosView.as_view(), name="lista_servicos"),
    path("servico/", ServicosDetailView.as_view(), name="detalhes_servico"),
    path("servico/criar/", ServicosApicoreView.as_view(), name="criar_servico"),
    path("servico/editar/", ServicosApicoreView.as_view(), name="editar_servico"),
    path("servico/apagar/", ServicosApicoreView.as_view(), name="apagar_servico"),
    path(
        "servico/executar-servico/",
        ServicosApicoreView.as_view(),
        name="executar_servico",
    ),
    path("classcodes/", ClasscodesView.as_view(), name="lista_classcodes"),
    path("classcode/", ClasscodesDetailView.as_view(), name="detalhes_classcode"),
    path("classcode/criar/", ClasscodesApicoreView.as_view(), name="criar_classcode"),
    path("classcode/editar/", ClasscodesApicoreView.as_view(), name="editar_classcode"),
    path("classcode/apagar/", ClasscodesApicoreView.as_view(), name="apagar_classcode"),
    path("classcode/tipos/", TiposClasscodesView.as_view(), name="tipos_classcodes"),
    path(
        "historico-servicos/",
        HistoricoServicosView.as_view(),
        name="lista_historico_servicos",
    ),
    path(
        "historico-servico/",
        HistoricoServicoDetailView.as_view(),
        name="detalhe_historico_servico",
    ),
    path(
        "historico-servico/<int:pk>/mensagens/",
        MensagensServicoView.as_view({"get": "mensagens"}),
        name="mensagens_servico",
    ),
]
