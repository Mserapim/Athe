from django.urls import path, include
from rest_framework import routers

from rh.apiv2.views.comarca import ComarcaView
from rh.apiv2.views.gratificacoesmembros import GratificacaoMembrosView
from rh.apiv2.views.lotacao import (
    ComarcaLotacaoView,
    ServidorLotacaoZonaEleitoralView,
    WorkplaceViewSet,
    LotacaoListView,
)
from rh.apiv2.views.conta_contabil import ContaContabilView, ContaContabilPagamentosView
from rh.apiv2.views.employeecurrent import EmployeeCurrentView
from rh.apiv2.views.localidade import (
    LotacionogramLocationView,
    LocationsView,
    StateView,
    PaisView,
)
from rh.apiv2.views.locationagram import LotacionogramView
from rh.apiv2.views.servidor import (
    SMCMembrosview,
    AtualizaEmailPessoalViewSet,
    UsufrutoFeriasServidoresView,
    ValidaEmailPessoalViewSet,
    ServidorListagemView,
    TipoPosseView,
    ServidorDetailView,
)
from rh.apiv2.views.telecommuting import TelecommutingView
from rh.apiv2.views.cargo import (
    AreaTrabalhoCargoView,
    CargoCoreView,
    CargoDetailView,
    CargoView,
    IndicativoCargoView,
    JobPositionViewSet,
    TipoLeiCargoView,
    TipoNivelEscolaridadeView,
)
from rh.apiv2.views.configparam import (
    ConfigTypeDepedentView,
    ConfigDegreekinshiptView,
    ConfigSexualOrientationView,
    ConfigImigrantResidenceTimeView,
    ConfigImigranteEntryConditionView,
)
from rh.apiv2.views.employeeconcept import BaseEmployeeViewSet, AidsEmployeeViewSet
from rh.apiv2.views.configparam import ConfigTypeDepedentView, ConfigDegreekinshiptView
from rh.apiv2.views.censoprevidenciario import CensoprevidenciarioView

from rh.apiv2.views.membros_trabalho_remoto import (
    MembrosTrabalhoRemotoListView,
    MembrosTrabalhoRemotoCoreView,
    MembrosTrabalhoRemotoDetailView,
)

from rh.apiv2.views.publicacao import (
    PublicacaoListView,
    PublicacaoCoreView,
    VeiculoPublicacaoListView,
    PublicationViewSet,
    PublicacaoDetailView,
)
from rh.apiv2.views.orgao_geral import OrgaoGeralListView, UnidadeAdmnistrativaListView

from rh.apiv2.views.cbo import CboListView, CboApiCore, CboDetailView
from rh.apiv2.views.teletrabalho import MovimentacaoTeletrabalhoDetailView
from rh.apiv2.views.telefone import (
    TelefoneApiCore,
    TelefoneDetailView,
    TelefoneListView,
)
from rh.apiv2.views.endereco import (
    EnderecoApiCore,
    EnderecoDetailView,
    EnderecoListView,
)
from rh.apiv2.views.gestao_pvf import *

router = routers.DefaultRouter()
router.register("workplaces", WorkplaceViewSet, basename="workplaces")
router.register("jobpositions", JobPositionViewSet, basename="jobpositions")
router.register(
    "employees/job-aids", AidsEmployeeViewSet, basename="employees_job-aids"
)
router.register("publications", PublicationViewSet, basename="publications")
# router.register('servidores', ServidorListagemView)

# Validação do e-mail pessoal
router.register(
    "current-user/atualiza-email-pessoal",
    AtualizaEmailPessoalViewSet,
    basename="current-user_atualiza-email-pessoal",
)
router.register(
    "current-user/valida-email-pessoal",
    ValidaEmailPessoalViewSet,
    basename="current-user_valida-email-pessoal",
)

urlpatterns = [
    # RH models
    path("", include(router.urls)),
    path("servidores", ServidorListagemView.as_view(), name="servidores"),
    path("servidor/", ServidorDetailView.as_view(), name="servidor"),
    path("tipo-posses/", TipoPosseView.as_view(), name="tipo_posses"),
    path("comarcas/", ComarcaView.as_view(), name="comarcas"),
    path("lotacao/", ComarcaLotacaoView.as_view(), name="lotacao"),
    path("conta-contabil/", ContaContabilView.as_view(), name="conta-contabil"),
    path(
        "conta-contabil/pagamentos/",
        ContaContabilPagamentosView.as_view(),
        name="conta-contabil-pagamentos",
    ),
    path(
        "localidades/",
        LotacionogramLocationView.as_view(),
        name="lotacionograma-localidades",
    ),
    path("locations/", LocationsView.as_view(), name="localidades"),
    path("states/", StateView.as_view(), name="states"),
    path("paises/", PaisView.as_view(), name="states"),
    path("employees/", BaseEmployeeViewSet.as_view({"get": "list"}), name="servidores"),
    path("lotacionagram/", LotacionogramView.as_view(), name="lotacionograma"),
    path("telecommuting/", TelecommutingView.as_view(), name="telecommuting"),
    path("smc-membros/", SMCMembrosview.as_view(), name="smc_membros"),
    path(
        "censo-previdenciario/",
        CensoprevidenciarioView.as_view(),
        name="CensoprevidenciarioView",
    ),
    # Afastamento
    path("absence/", include("rh.afastamento.urls")),
    # Dados Bancarios
    path("dados-bancarios/", include("rh.dados_bancarios.urls")),
    # VDF
    path("pvf/", include("rh.pvf.urls")),
    path("pvf/clocking/", include("rh.registerpoint.urls")),
    # GFP
    path("gfp/", include("rh.gfp.urls")),
    # Antiguidades
    path("antiguidades/", include("rh.antiguidades.urls")),
    # Defin
    path("defin/", include("rh.defin.urls")),
    # RH CONFIGS
    path(
        "config/params/type-dependents/",
        ConfigTypeDepedentView.as_view(),
        name="type_dependents",
    ),
    path(
        "config/params/degree-kinshipt/",
        ConfigDegreekinshiptView.as_view(),
        name="degree_kinshipt",
    ),
    path(
        "config/params/sexual-orientations/",
        ConfigSexualOrientationView.as_view(),
        name="sexual_orientations",
    ),
    path(
        "config/params/imigrant-residences/",
        ConfigImigrantResidenceTimeView.as_view(),
        name="imigrant_residences",
    ),
    path(
        "config/params/imigrant-conditions/",
        ConfigImigranteEntryConditionView.as_view(),
        name="imigrant_conditions",
    ),
    # Membros Trabalho Remoto
    path(
        "membros-trabalho-remotos/",
        MembrosTrabalhoRemotoListView.as_view(),
        name="membros_trabalho_remto_lista",
    ),
    path(
        "membros-trabalho-remoto/",
        MembrosTrabalhoRemotoDetailView.as_view(),
        name="membros_trabalho_remto",
    ),
    path(
        "membros-trabalho-remoto/criar",
        MembrosTrabalhoRemotoCoreView.as_view(),
        name="criar_membros_trabalho_remto",
    ),
    path(
        "membros-trabalho-remoto/editar",
        MembrosTrabalhoRemotoCoreView.as_view(),
        name="editar_membros_trabalho_remto",
    ),
    path(
        "membros-trabalho-remoto/apagar",
        MembrosTrabalhoRemotoCoreView.as_view(),
        name="apagar_membros_trabalho_remto",
    ),
    # Publicações
    path("publicacoes/", PublicacaoListView.as_view(), name="publicacao_lista"),
    path("publicacao/", PublicacaoDetailView.as_view(), name="publicacao"),
    path("publicacao/criar", PublicacaoCoreView.as_view(), name="criar_publicacao"),
    path("publicacao/editar", PublicacaoCoreView.as_view(), name="editar_publicacao"),
    path("publicacao/apagar", PublicacaoCoreView.as_view(), name="apagar_publicacao"),
    path(
        "veiculo-publicacao/",
        VeiculoPublicacaoListView.as_view(),
        name="veiculo_publicacao",
    ),
    path("orgao-geral/", OrgaoGeralListView.as_view(), name="orgao_geral"),
    path(
        "unidades-admisitrativas/",
        UnidadeAdmnistrativaListView.as_view(),
        name="uniadade_administativa",
    ),
    # Cbo
    path("cbos/", CboListView.as_view(), name="cbos"),
    path("cbo/", CboDetailView.as_view(), name="cbo"),
    path("cbo/criar", CboApiCore.as_view(), name="cbo-criar"),
    path("cbo/editar", CboApiCore.as_view(), name="cbo-editar"),
    path("cbo/apagar", CboApiCore.as_view(), name="cbo-apagar"),
    # Gratificação de membros
    path(
        "gratificacao-membros/",
        GratificacaoMembrosView.as_view(),
        name="gratificacao_membros",
    ),
    # Usufrutos férias de Servidores/membros
    path(
        "usufrutos-ferias/",
        UsufrutoFeriasServidoresView.as_view(),
        name="usufrutos_ferias",
    ),
    # Lotações eleitorais do servidor
    path(
        "servidor-lotacoes-eleitorais/",
        ServidorLotacaoZonaEleitoralView.as_view(),
        name="servidor_lotacoes_eleitorais",
    ),
    # Movimentação teletrabalho
    path(
        "movimentacao-teletrabalho/",
        MovimentacaoTeletrabalhoDetailView.as_view(),
        name="movimentacao-teletrabalho",
    ),
    # Gestao
    path("gestao/vdf/", GestaoPVFView.as_view(), name="gestao-vdf"),
    # Movimentaçào carreira
    path("mov-carreira/", include("rh.mov_carreira.urls")),
    # Telefone
    path("telefones/", TelefoneListView.as_view()),
    path("telefone/", TelefoneDetailView.as_view()),
    path("telefone/criar/", TelefoneApiCore.as_view()),
    path("telefone/editar/", TelefoneApiCore.as_view()),
    path("telefone/apagar/", TelefoneApiCore.as_view()),
    # Endereço
    path("enderecos/", EnderecoListView.as_view()),
    path("endereco/", EnderecoDetailView.as_view()),
    path("endereco/criar/", EnderecoApiCore.as_view()),
    path("endereco/editar/", EnderecoApiCore.as_view()),
    path("endereco/apagar/", EnderecoApiCore.as_view()),
    # Lotações
    path("lotacoes/", LotacaoListView.as_view()),
    # Cargos
    path("cargos/", CargoView.as_view(), name="cargos"),
    path("cargo/", CargoDetailView.as_view(), name="cargos-detalhes"),
    path("cargo/criar/", CargoCoreView.as_view(), name="criar-cargos"),
    path("cargo/editar/", CargoCoreView.as_view(), name="editar-cargos"),
    path("cargo/apagar/", CargoCoreView.as_view(), name="apagar-cargos"),
    path(
        "area-trabalho-cargos",
        AreaTrabalhoCargoView.as_view(),
        name="area-trabalho-cargos",
    ),
    path("tipo-lei-cargos/", TipoLeiCargoView.as_view(), name="tipo-lei-cargos"),
    path("indicativo-cargos/", IndicativoCargoView.as_view(), name="indicativo-cargos"),
    # Nível escolaridade
    path(
        "nivel-escolaridade/",
        TipoNivelEscolaridadeView.as_view(),
        name="nivel-escolaridade",
    ),
]
