from django.urls import path, include
from diarias.apiv2.views.analise import (
    AnaliseCeafApiCore,
    AnaliseEmpenhoDeplanApiView,
    AnaliseNotaLiquidacaoDefinApiView,
    AnaliseOrdemBancariaDefinApiView,
    ReceberBeneficiariosApiView,
)
from diarias.apiv2.views.aprovacoes import (
    AnaliseDaaPassagemAereaApiView,
    AnaliseExcedenteDefin,
    AnaliseQuantidadeDiariasApiView,
    AnaliseValorDeferidoBeneficiario,
    CienciaChefeImediatoApiView,
    InformacaoAprovacaoApiView,
    MoverBeneficiariosDiariasApiView,
    SalvarVeiculosPassageirosApiView,
)
from diarias.apiv2.views.aprovacoes import (
    AnaliseDaaPassagemAereaApiView,
    AnaliseExcedenteDefin,
    AnaliseQuantidadeDiariasApiView,
    CienciaCancelamentoDiaria,
    CienciaChefeImediatoApiView,
    InformacaoAprovacaoApiView,
)
from diarias.apiv2.views.limite_diarias import LimiteUsoDiariasView
from diarias.apiv2.views.pagamentos import GerarCnabView, PagamentoView
from diarias.apiv2.views.viagem import (
    HistoricoFluxoViagemBeneficiarioView,
    MinhasViagensApiList,
    ObservacaoHistoricoFluxoBeneficiario,
    PassagemAereaViagemView,
    ViagemApiCore,
    ViagemApiDetail,
    ViagemPermissaoView,
    ViagensApiList,
    ViagemHistoricoView,
    ViagemBeneficiarioHistoricoView,
    DestinosDetalhadoView,
    VeiculoPassageiroViagemView,
)
from diarias.apiv2.views.choices import (
    AcompAutoridadeDiariasApiList,
    EtapasDiariasApiList,
    FinalidadesDiariasApiList,
    MotivosViagemDiariasApiList,
    SituacoesDiariasApiList,
    TipoSolicitanteDiariasApiList,
)
from diarias.apiv2.views.beneficiarios import (
    BeneficiariosApiCore,
    BeneficiariosApiList,
    BeneficiariosDetailView,
    BeneficiariosFluxoHistoricoApiList,
    ColaboradorventualApiCreate,
)
from diarias.apiv2.views.destino import (
    DestinoCloneLoteView,
    DestinoDetailView,
    DestinosApiCore,
    DestinosApiList,
)
from diarias.apiv2.views.prestacao_contas import (
    PrestacaoContasApiCore,
    PrestacaoContasApiDetailView,
    PrestacaoContasApiList,
    PrestacaoContasExternaView,
    ContaMpmtDevolucaoDetailView,
)
from diarias.apiv2.views.evento import (
    EventoApiCore,
    EventoDetailView,
    EventosApiList,
    EventoCloneLoteView,
)
from diarias.apiv2.views.importacao import ImportarDiariasView
from diarias.apiv2.views.portal_transparencia import BeneficiariosTransparenciaView

urlpatterns = [
    path("config/", include("diarias.config.urls")),
    path("minhas-diarias/", MinhasViagensApiList.as_view(), name="minhas_diarias"),
    path(
        "minhas-diarias/viagem/criar/",
        ViagemApiCore.as_view(),
        name="minhas_diarias_viagem_criar",
    ),
    path("minhas-diarias/viagem/editar/", ViagemApiCore.as_view()),
    path("minhas-diarias/viagem/cancelar/", ViagemApiCore.as_view()),
    path("minhas-diarias/viagem/finalizar/", ViagemApiCore.as_view()),
    path("viagem/", ViagemApiDetail.as_view()),
    path("viagens/", ViagensApiList.as_view()),
    path("viagem/destinos/", DestinosApiList.as_view()),
    path("viagem/destino/criar/", DestinosApiCore.as_view()),
    path("viagem/destino/", DestinoDetailView.as_view()),
    path("viagem/destino/editar/", DestinosApiCore.as_view()),
    path("viagem/destino/apagar/", DestinosApiCore.as_view()),
    path("viagem/destino/clonar/", DestinosApiCore.as_view()),
    path("viagem/destino/clonar/lote/", DestinoCloneLoteView.as_view()),
    path("viagem/eventos/", EventosApiList.as_view()),
    path("viagem/evento/", EventoDetailView.as_view()),
    path("viagem/evento/criar/", EventoApiCore.as_view()),
    path("viagem/evento/editar/", EventoApiCore.as_view()),
    path("viagem/evento/apagar/", EventoApiCore.as_view()),
    path("viagem/evento/clonar/", EventoApiCore.as_view()),
    path("viagem/evento/clonar/lote/", EventoCloneLoteView.as_view()),
    path("viagem/detalhe/historico", ViagemHistoricoView.as_view()),
    path(
        "viagem/detalhe/historico/anexos-informacoes/",
        HistoricoFluxoViagemBeneficiarioView.as_view(),
    ),
    path(
        "viagem/detalhe/historico/observacao/",
        ObservacaoHistoricoFluxoBeneficiario.as_view(),
    ),
    path(
        "viagem/detalhe/beneficiario/historico",
        ViagemBeneficiarioHistoricoView.as_view(),
    ),
    path(
        "viagem/detalhe/beneficiario/destinos-detalhado",
        DestinosDetalhadoView.as_view(),
    ),
    path(
        "viagem/receber-beneficiarios/",
        ReceberBeneficiariosApiView.as_view(),
        name="viagem-receber-beneficiarios",
    ),
    path(
        "minhas-diarias/beneficiarios/",
        BeneficiariosApiList.as_view(),
        name="minhas_diarias_beneficiarios",
    ),
    path("minhas-diarias/beneficiario/criar/", BeneficiariosApiCore.as_view()),
    path("minhas-diarias/beneficiario/editar/", BeneficiariosApiCore.as_view()),
    path("minhas-diarias/beneficiario/apagar/", BeneficiariosApiCore.as_view()),
    path("minhas-diarias/beneficiario/", BeneficiariosDetailView.as_view()),
    path(
        "minhas-diarias/beneficiarios-fluxo-historico/",
        BeneficiariosFluxoHistoricoApiList.as_view(),
    ),
    path("minhas-diarias/permissao/", ViagemPermissaoView.as_view()),
    path("colaborador-eventual/criar/", ColaboradorventualApiCreate.as_view()),
    path("beneficiario/limite-uso-diarias/", LimiteUsoDiariasView.as_view()),
    path("beneficiario/recalcular/", BeneficiariosApiCore.as_view()),
    path(
        "beneficiario/analise-ceaf/criar/",
        AnaliseCeafApiCore.as_view(),
        name="analise-ceaf-beneficiario-criar",
    ),
    path(
        "beneficiario/analise-deplan/criar/",
        AnaliseEmpenhoDeplanApiView.as_view(),
        name="analise-deplan-beneficiario-criar",
    ),
    path(
        "beneficiario/analise-defin/criar/",
        AnaliseNotaLiquidacaoDefinApiView.as_view(),
        name="analise-defin-beneficiario-criar",
    ),
    path(
        "beneficiario/analise-ordem-bancaria-defin/criar/",
        AnaliseOrdemBancariaDefinApiView.as_view(),
        name="analise-ordem-bancaria-defin-beneficiario-criar",
    ),
    path(
        "beneficiario/ciencia-chefe-imediato/",
        CienciaChefeImediatoApiView.as_view(),
        name="ciencia-chefe-imediato-beneficiario",
    ),
    path(
        "beneficiario/informacao-e-aprovacao/",
        InformacaoAprovacaoApiView.as_view(),
        name="informacao-e-aprovacao-beneficiario",
    ),
    path(
        "beneficiario/analise-quantidade-diarias/",
        AnaliseQuantidadeDiariasApiView.as_view(),
        name="analise-quantidade-diarias",
    ),
    path(
        "beneficiario/analise-daa-passagem/criar/",
        AnaliseDaaPassagemAereaApiView.as_view(),
        name="analise-daa-passagem-diarias",
    ),
    path(
        "beneficiario/analise-defin-excedente/",
        AnaliseExcedenteDefin.as_view(),
        name="analise-defin-excedente-diarias",
    ),
    path(
        "beneficiario/passagem-aerea/",
        PassagemAereaViagemView.as_view(),
        name="passagem-aerea-diarias",
    ),
    path(
        "beneficiario/analise-valor-deferido/",
        AnaliseValorDeferidoBeneficiario.as_view(),
        name="analise-valor-deferido-beneficiario",
    ),
    path(
        "beneficiarios/ciencia-cancelamento/",
        CienciaCancelamentoDiaria.as_view(),
        name="ciencia-cancelamento-diarias",
    ),
    path(
        "beneficiario/analise-daa-veiculo-passageiros/criar/",
        SalvarVeiculosPassageirosApiView.as_view(),
        name="veiculo-motorista-diarias",
    ),
    path(
        "beneficiario/destino/veiculo-motorista/",
        VeiculoPassageiroViagemView.as_view(),
        name="veiculo-motorista-destino",
    ),
    path(
        "beneficiarios/mover-fluxo/",
        MoverBeneficiariosDiariasApiView.as_view(),
        name="mover-fluxo-beneficarios",
    ),
    path("prestacoes-contas/", PrestacaoContasApiList.as_view()),
    path("prestacao-contas/", PrestacaoContasApiDetailView.as_view()),
    path("prestacao-contas/editar/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/assinar/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/aprovar/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/indeferir/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/cancelar/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/notificar/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/receber/", PrestacaoContasApiCore.as_view()),
    path("prestacao-contas/conta-devolucao/", ContaMpmtDevolucaoDetailView.as_view()),
    path("prestacao-contas-externa/autenticar/", PrestacaoContasExternaView.as_view()),
    path("prestacao-contas-externa/cadastrar/", PrestacaoContasExternaView.as_view()),
    # choices
    path("situacoes/", SituacoesDiariasApiList.as_view(), name="situacoes_diarias"),
    path(
        "motivos-viagem/",
        MotivosViagemDiariasApiList.as_view(),
        name="motivos_viagem_diarias",
    ),
    path(
        "finalidades/", FinalidadesDiariasApiList.as_view(), name="finalidades_diarias"
    ),
    path(
        "acompamento-autoridade/",
        AcompAutoridadeDiariasApiList.as_view(),
        name="acompamento_autoridade_diarias",
    ),
    path("etapa-viagem/", EtapasDiariasApiList.as_view(), name="etapa_viagem_diarias"),
    path(
        "tipo-solicitante/",
        TipoSolicitanteDiariasApiList.as_view(),
        name="tipo_solicitante_diarias",
    ),
    path("pagamentos/", PagamentoView.as_view(), name="lista_pagamentos"),
    path("gerar-cnab/", GerarCnabView.as_view(), name="gerar-cnab"),
    # importacao
    path("importar/", ImportarDiariasView.as_view()),
    # portal transparencia
    path("portal-transparencia/", BeneficiariosTransparenciaView.as_view()),
]
