from contrib.middleware import set_current_user
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema
from apiv2.pagination import CustomPagination

from rh.pvf.models import PVFSolicitacaoCreditoDispensaEleitoral
from rh.pvf.apiv2.serializers.solicitacaodispensaeleitoralserializers import (
    PVFSolicitacaoDispensaEleitoralSerializer,
)

from contrib.utils import getLogger


log = getLogger(__name__)


class PVFSolicitacaoDispensaEleitoral(CreateAPIView, UpdateAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = PVFSolicitacaoDispensaEleitoralSerializer
    http_method_names = ["post"]
    model = PVFSolicitacaoCreditoDispensaEleitoral

    # Mapeamento de caminho para função
    path_function_map = {"criar": "create", "editar": "update", "apagar": "destroy"}

    def post(self, request, *args, **kwargs):
        """
        Descrição da operação POST
        """

        path = request.path

        for keyword, func_name in self.path_function_map.items():
            if keyword in path:
                if func_name == "update":
                    kwargs["partial"] = True
                func = getattr(self, func_name)
                return func(request, *args, **kwargs)

        return Response(
            {"message": "Método não suportado"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self):
        """
        Mudando a função get_object para pegar o pk pelo data
        """
        pk = self.request.data.get("id", None)

        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            if pk is not None:
                raise Http404("O objeto não existe para o pk fornecido")
            raise Http404("O parametro pk não foi fornecido")

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        serializer = self.get_serializer(data=request.data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def get_serializer(self, *args, **kwargs):
        from datetime import datetime

        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class PVFDetalhesSolicitacaoDispensaEleitoral(RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = PVFSolicitacaoDispensaEleitoralSerializer
    http_method_names = ["get"]
    model = PVFSolicitacaoCreditoDispensaEleitoral

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id", description="Chave primario(Primary Key)", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Descrição da operação GET ->
        Detalhes da solicitação de crédito de dispensa eleitoral
        """

        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self):
        """
        Mudando a função get_object para pegar o pk pelo data
        """
        pk = self.request.data.get("pk", None)

        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:

            if pk is not None:
                raise Http404("O objeto não existe para o pk fornecido")
            raise Http404("O parametro pk não foi fornecido")

    def retrieve(self, request, *args, **kwargs):
        pk = request.query_params.get("id", None)
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)
