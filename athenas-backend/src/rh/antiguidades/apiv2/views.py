from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import MultiAuthentication
from rest_framework.generics import ListAPIView
from apiv2.pagination import CustomPagination
from rest_framework.response import Response
from apiv2.baseviews import ListBaseView

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from contrib.middleware import set_current_user

from rh.antiguidades.lista_antiguidades_membros_utils import ListaAntiguidades as LAM


from rh.antiguidades.apiv2.serializers import AntiguidadesSerializer
from rh.antiguidades.models import ListaAntiguidadeMembros

from contrib.utils import getLogger

log = getLogger(__name__)


class AntiguidadesView(ListBaseView):
    """
    View de Antiguidades

    Esta classe é responsável por fornecer uma lista paginada de Comarcas.

    :queryset: conjunto de objetos do modelo Lista de Antiguidades
    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :authentication_classes: lista de classes de autenticação requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = ListaAntiguidadeMembros.objects.filter(servidor__ativo=True).order_by(
        "tipo_cargo", "ordem_antiguidade"
    )
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiAuthentication]
    pagination_class = CustomPagination
    serializer_class = AntiguidadesSerializer
    full_text_index = (
        "servidor__pessoa_fisica__nome__unaccent__icontains",
        "servidor__pessoa_fisica__social_name__unaccent__icontains",
        "servidor__matricula__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="tipo_membro", description="Tipo de Membro", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        tipo_membro = self.request.GET.get("tipo_membro")

        if tipo_membro is not None and tipo_membro != 0 and tipo_membro != "0":
            queryset = queryset.filter(tipo_cargo=tipo_membro)

        return queryset


class AtualizarAntiguidadesView(APIView):
    """
    View para chamar a função do job que atualiza a lista de Atinguidades
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {"type": "object", "properties": {}},
        },
        responses={
            "application/json": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {
            "success": False,
            "message": "Nada foi feito ainda!",
        }

        try:
            lam = LAM()
            lam.atualizar_lista_antiguidades_membros("Manual")

            obj.update(
                success=True,
                message="Lista de Antiguidades de Membros Atualizada",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)
