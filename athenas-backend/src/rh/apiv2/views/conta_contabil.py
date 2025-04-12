from rh.apiv2.serializers.conta_contabil import (
    ContaContabilSerializer,
    PagamentoSerializer,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import CustomTokenJWTAuthentication
from rest_framework.generics import ListAPIView
from apiv2.pagination import CustomPagination
from rest_framework.response import Response
from apiv2.baseviews import ListBaseView
from django.shortcuts import get_object_or_404

from standard.models import Choice
from rh.gfp.models import ContraCheque, FolhaEvento

from rest_framework import status
from rest_framework.response import Response


from contrib.utils import getLogger

log = getLogger(__name__)


class ContaContabilView(ListBaseView):
    queryset = Choice.objects.filter(name="CONTA_CONTABIL")
    # queryset = Choice.objects.filter(label='1.02.05.001')
    # queryset = Choice.objects.filter(label='1.01.01.001')
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = ContaContabilSerializer

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada.
        """
        if not request.query_params.get("ano", None) or not request.query_params.get(
            "mes", None
        ):
            return Response(
                {"erro": "A requisição deve enviar os paramentros ano/mes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(self.get_queryset().filter().distinct())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContaContabilPagamentosView(ListBaseView):
    queryset = FolhaEvento.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = PagamentoSerializer

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada.
        """
        conta = request.query_params.get("conta_contabil", None)

        mes = request.query_params.get("mes", None)
        ano = request.query_params.get("ano", None)
        per_page = request.query_params.get("per_page", None)

        if conta is None or mes is None or ano is None or per_page is None:
            return Response(
                {
                    "erro": "A requisição deve enviar os paramentros ano/mes/conta_contabil/per_page"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        conta_value = Choice.objects.filter(label=conta).first().value

        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(
                evento__conta_contabil=conta_value,
                folha__dt_pagamento__month=mes,
                folha__dt_pagamento__year=ano,
            )
            .distinct()
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
