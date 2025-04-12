from django.urls import path

from diarias.config.apiv2.views import (
    CargoDiariasDetailView,
    CargoDiariasApicoreView,
    CargoDiariasView,
    LimiteDiariasApicoreView,
    LimiteDiariasDetailView,
    LimiteDiariasView,
    MotoristasDiariasAPIList,
    ValorDiariasView,
    ValorDiariasDetailView,
    ValorDiariasApicoreView,
)
from diarias.config.views.fluxo import (
    CondicionaisDiariasView,
    EtapasDiariasView,
    FluxoViagemApicoreView,
    FluxoViagemAtualizarOrdemView,
    FluxoViagemDetailView,
    FluxoViagemView,
    SituacoesDiariasView,
)
from diarias.config.views.grupoaprovador import (
    GrupoAprovadorApicoreView,
    GrupoAprovadorDetailView,
    GrupoAprovadorView,
    UsuarioGrupoAprovadorAPIList,
    UsuariosAPIList,
    PerfilAprovadorDetailView,
)

urlpatterns = [
    path("cargos/", CargoDiariasView.as_view(), name="lista_cargos"),
    path("cargo/", CargoDiariasDetailView.as_view(), name="detalhes_cargo"),
    path("cargo/criar/", CargoDiariasApicoreView.as_view(), name="criar_cargo"),
    path("cargo/editar/", CargoDiariasApicoreView.as_view(), name="editar_cargo"),
    path("cargo/apagar/", CargoDiariasApicoreView.as_view(), name="apagar_cargo"),
    path("valores/", ValorDiariasView.as_view(), name="lista_valores"),
    path("valor/", ValorDiariasDetailView.as_view(), name="detalhes_valor"),
    path("valor/criar/", ValorDiariasApicoreView.as_view(), name="criar_valor"),
    path("valor/editar/", ValorDiariasApicoreView.as_view(), name="editar_valor"),
    path("valor/apagar/", ValorDiariasApicoreView.as_view(), name="apagar_valor"),
    path("fluxos/", FluxoViagemView.as_view(), name="lista_fluxos"),
    path(
        "fluxos/atualizar-ordem",
        FluxoViagemAtualizarOrdemView.as_view(),
        name="atualizar-ordem-fluxos",
    ),
    path("fluxo/", FluxoViagemDetailView.as_view(), name="fluxo"),
    path("fluxo/criar/", FluxoViagemApicoreView.as_view(), name="criar_fluxo_viagem"),
    path("fluxo/editar/", FluxoViagemApicoreView.as_view(), name="editar_fluxo_viagem"),
    path("fluxo/apagar/", FluxoViagemApicoreView.as_view(), name="apagar_fluxo_viagem"),
    path("etapas/", EtapasDiariasView.as_view(), name="lista_etapas"),
    path("situacoes/", SituacoesDiariasView.as_view(), name="lista_situacoes"),
    path("condicionais/", CondicionaisDiariasView.as_view(), name="lista_condicionais"),
    path(
        "grupos-aprovadores/",
        GrupoAprovadorView.as_view(),
        name="lista_grupos_aprovadores",
    ),
    path(
        "grupo-aprovador/", GrupoAprovadorDetailView.as_view(), name="grupo_aprovador"
    ),
    path(
        "grupo-aprovador/criar/",
        GrupoAprovadorApicoreView.as_view(),
        name="criar_grupo_aprovador",
    ),
    path(
        "grupo-aprovador/editar/",
        GrupoAprovadorApicoreView.as_view(),
        name="editar_grupo_aprovador",
    ),
    path(
        "grupo-aprovador/apagar/",
        GrupoAprovadorApicoreView.as_view(),
        name="apagar_grupo_aprovador",
    ),
    path(
        "grupo-aprovador/usuarios/",
        UsuarioGrupoAprovadorAPIList.as_view(),
        name="usuarios_grupo_aprovador",
    ),
    path("usuarios/", UsuariosAPIList.as_view(), name="lista_usuarios"),
    path(
        "perfil-aprovador/",
        PerfilAprovadorDetailView.as_view(),
        name="perfil_aprovador",
    ),
    path("limites-diarias/", LimiteDiariasView.as_view(), name="limites_diarias"),
    path("limite-diarias/", LimiteDiariasDetailView.as_view(), name="limite-diarias"),
    path(
        "limite-diarias/criar/",
        LimiteDiariasApicoreView.as_view(),
        name="criar_limite_diarias",
    ),
    path(
        "limite-diarias/editar/",
        LimiteDiariasApicoreView.as_view(),
        name="editar_limite_diarias",
    ),
    path(
        "limite-diarias/apagar/",
        LimiteDiariasApicoreView.as_view(),
        name="apagar_limite_diarias",
    ),
    path(
        "motoristas-diarias/",
        MotoristasDiariasAPIList.as_view(),
        name="lista_motoristas_diarias",
    ),
]
