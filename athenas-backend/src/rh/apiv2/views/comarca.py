from rh.apiv2.serializers.comarca import ComarcaSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import CustomTokenJWTAuthentication
from rest_framework.generics import ListAPIView
from apiv2.pagination import CustomPagination
from rh.models import Comarca
from rest_framework.response import Response
from apiv2.baseviews import ListBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class ComarcaView(ListBaseView):
    """
    View de Comarcas

    Esta classe é responsável por fornecer uma lista paginada de Comarcas.

    :queryset: conjunto de objetos do modelo Comarca
    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :authentication_classes: lista de classes de autenticação requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Comarca.objects.all().order_by("nome")
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = ComarcaSerializer
    full_text_index = ("nome__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada de Comarcas.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
