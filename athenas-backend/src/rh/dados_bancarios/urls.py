from django.urls import path

from rh.dados_bancarios.apiv2.views import (
    DadoBancarioPessoaApiList,
    DadoBancarioPessoaApiCore,
    BancosApiList,
    TipoContaApiList,
)


urlpatterns = [
    path("bancos/", BancosApiList.as_view()),
    path("tipos-conta/", TipoContaApiList.as_view()),
    path("servidor/contas/", DadoBancarioPessoaApiList.as_view()),
    path("servidor/conta/criar/", DadoBancarioPessoaApiCore.as_view()),
]
