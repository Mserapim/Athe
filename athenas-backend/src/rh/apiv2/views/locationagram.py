from rh.apiv2.serializers.lotacionogram import LotacionogramSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import CustomTokenJWTAuthentication
from rh.lotacionogram import get_data, filter_data, get_data_resume
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from apiv2.pagination import CustomPagination


class LotacionogramView(ListAPIView):
    """
    View do lotacionograma
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="page", description="Página", type=int),
            OpenApiParameter(name="municipio", description="Municipio", type=int),
            OpenApiParameter(name="cargo", description="Cargo", type=int),
            OpenApiParameter(name="lotacao", description="Lotação", type=int),
            OpenApiParameter(
                name="types_by_possession", description="Tipo posse", type=str
            ),
            OpenApiParameter(name="servidor", description="Servidor", type=int),
            OpenApiParameter(name="competencia", description="Competencia", type=str),
            OpenApiParameter(name="comarca", description="Comarca", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        params = self.request.query_params
        data = get_data_resume(params)
        paginated_data = self.paginate_queryset(data)
        if paginated_data:
            data_serializer = LotacionogramSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        return Response([])
