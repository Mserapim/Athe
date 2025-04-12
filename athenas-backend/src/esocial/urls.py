from django.urls import path
from esocial.apiv2.views.configuracao import (
    CertificadoEsocialView,
    ConfiguracaoCoreView,
    ConfiguracaoView,
    EventosChoiceView,
    AtualizarCertificadoCoreView,
)
from esocial.apiv2.views.itemtabela import (
    ItemTabelaCoreView,
    ItemTabelaDetailView,
    ItemTabelaView,
    OpcaoTableChoiceView,
    TabelaEsocialView,
)
from esocial.apiv2.views.qualificacaocadastral import (
    FiltroCategoriaTipoPessoaView,
    FiltroOrientacaoCPFView,
    FiltroOrientacaoNISPISPASEPView,
    FiltroStatusQualificacaoView,
    QualificacaoCadastralView,
    QualificacaoCadastralCoreView,
)


urlpatterns = [
    path("itens-tabela/", ItemTabelaView.as_view(), name="itens-tabela"),
    path("item-tabela/", ItemTabelaDetailView.as_view(), name="itens-tabela-detalhes"),
    path("item-tabela/criar/", ItemTabelaCoreView.as_view(), name="itens-tabela-criar"),
    path(
        "item-tabela/editar/", ItemTabelaCoreView.as_view(), name="itens-tabela-criar"
    ),
    path(
        "item-tabela/apagar/", ItemTabelaCoreView.as_view(), name="itens-tabela-criar"
    ),
    path("tabelas/", TabelaEsocialView.as_view(), name="lista-tabelas"),
    path("opcoes-tabela/", OpcaoTableChoiceView.as_view(), name="opcoes-tabelas"),
    path(
        "qualificacoes-cadastrais/",
        QualificacaoCadastralView.as_view(),
        name="qualificacoes-cadastrais",
    ),
    path(
        "qualificacao-cadastral/atualizar-lista/",
        QualificacaoCadastralCoreView.as_view(),
        name="atualizar-lista",
    ),
    path(
        "qualificacao-cadastral/confirmar-qualificacao/",
        QualificacaoCadastralCoreView.as_view(),
        name="confirmar-qualificacao",
    ),
    path(
        "qualificacao-cadastral/gerar-arquivo/",
        QualificacaoCadastralCoreView.as_view(),
        name="gerar-arquivo",
    ),
    path(
        "config/categorias-tipos-pessoas/",
        FiltroCategoriaTipoPessoaView.as_view(),
        name="categorias-tipos-pessoas",
    ),
    path(
        "config/orientacoes-cpf/",
        FiltroOrientacaoCPFView.as_view(),
        name="orientacoes-cpf",
    ),
    path(
        "config/orientacoes-nis/",
        FiltroOrientacaoNISPISPASEPView.as_view(),
        name="orientacoes-nis",
    ),
    path("config/status/", FiltroStatusQualificacaoView.as_view(), name="status"),
    path("configuracoes/", ConfiguracaoView.as_view(), name="configuracoes"),
    path(
        "configuracao/criar/", ConfiguracaoCoreView.as_view(), name="configuracao-criar"
    ),
    path(
        "configuracao/editar/",
        ConfiguracaoCoreView.as_view(),
        name="configuracao-editar",
    ),
    path(
        "configuracao/apagar/",
        ConfiguracaoCoreView.as_view(),
        name="configuracao-apagar",
    ),
    path(
        "configuracao/atualizar-certificado/",
        AtualizarCertificadoCoreView.as_view(),
        name="atualizar-certificado",
    ),
    path(
        "configuracao/certificado-digital/",
        CertificadoEsocialView.as_view(),
        name="certificado-digital",
    ),
    path("eventos/", EventosChoiceView.as_view(), name="eventos"),
]
