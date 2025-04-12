from django.urls import path, include
from rest_framework import routers

from anotacao_pessoal.apiv2.views import (
    AnotacaoPessoalView,
    TiposAnotacaoView,
    TiposDocumentosView,
    AnotacaoPessoalViewSet,
    AnotacaoPessoalListView,
    AnotacaoPessoalDetailView,
)

router = routers.DefaultRouter()


urlpatterns_anotacao_pessoal = [
    path("", include(router.urls)),
    path("minhas-anotacoes/", AnotacaoPessoalView.as_view(), name="anotacao_pessoal"),
    path("tipos-anotacao/", TiposAnotacaoView.as_view(), name="tipos_anotacao"),
]
urlpatterns_anotacoes_pessoais = [
    path("", AnotacaoPessoalListView.as_view(), name="lista-anotacao"),
    path("detalhes/", AnotacaoPessoalDetailView.as_view(), name="anotacao"),
    path("criar", AnotacaoPessoalViewSet.as_view(), name="criar-anotacao"),
    path("editar", AnotacaoPessoalViewSet.as_view(), name="editar-anotacao"),
    path("ocultar", AnotacaoPessoalViewSet.as_view(), name="deletar-anotacao"),
    path("tipos-documentos/", TiposDocumentosView.as_view(), name="tipos_documentos"),
]
