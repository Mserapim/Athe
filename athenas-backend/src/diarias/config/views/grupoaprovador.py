from contrib.utils import getLogger
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from diarias.config.serializers.grupoaprovador import (
    GrupoAprovadorSerializer,
    UsuarioDiariasSerializer,
    PerfilAprovadorDiariasSerializer,
)
from diarias.models import GrupoAprovador
from rh.models import Servidor


log = getLogger()


class GrupoAprovadorView(ListBaseView):
    """
    View da lista de Grupo Aprovador
    """

    permission_classes = [IsAuthenticated]
    queryset = GrupoAprovador.objects.filter().order_by("nome")
    serializer_class = GrupoAprovadorSerializer
    full_text_index = ("nome__unaccent__icontains",)


class GrupoAprovadorApicoreView(ApiCore):
    """
    View da Criar, editar e apagar de Grupo Aprovador
    """

    model = GrupoAprovador
    serializer_class = GrupoAprovadorSerializer


class GrupoAprovadorDetailView(ApiDetailView):
    """
    View de detalhes de Grupo Aprovador
    """

    model = GrupoAprovador
    serializer_class = GrupoAprovadorSerializer


class UsuarioGrupoAprovadorAPIList(ListBaseView):
    """
    View para listar os usuarios de um UsuarioGrupo
    """

    model = Servidor
    serializer_class = UsuarioDiariasSerializer
    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "pessoa_fisica__social_name__unaccent__icontains",
        "matricula__icontains",
        "user__username__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="grupo_id", description="ID do Grupo Aprovador", type=int
            ),
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
        ]
    )
    def get_queryset(self):
        grupo_id = self.request.GET.get("grupo_id")

        try:
            usuarios_grupo_aprovador = GrupoAprovador.objects.get(pk=grupo_id)
            return usuarios_grupo_aprovador.servidores.all()
        except:
            return []


class UsuariosAPIList(ListBaseView):
    """
    View para listar os usuarios
    """

    model = Servidor
    serializer_class = UsuarioDiariasSerializer
    queryset = Servidor.objects.all()
    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "pessoa_fisica__social_name__unaccent__icontains",
        "matricula__icontains",
        "user__username__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="situacao", description="Situação", type=str),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        situacao = self.request.GET.get("situacao")

        if situacao is not None and situacao != "Todos":
            if situacao == "Ativo":
                queryset = queryset.filter(ativo=True)
            else:
                queryset = queryset.filter(ativo=False)

        return queryset


class PerfilAprovadorDetailView(ApiDetailView):
    """
    View de detalhes de Perfil Aprovador
    """

    model = Servidor
    serializer_class = PerfilAprovadorDiariasSerializer
