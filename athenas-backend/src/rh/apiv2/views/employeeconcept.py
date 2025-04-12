from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apiv2.baseviews import BaseViewSet
from auth.backend import ExternalJWTAuthentication
from rh.models import Servidor
from rh.apiv2.serializers.employeeconcept import (
    AidsEmployeeSerializer,
    BasicEmployeeSerializer,
)


class BaseEmployeeViewSet(BaseViewSet):
    """
    View das Servidores para teste de conceito
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExternalJWTAuthentication]
    queryset = Servidor.objects.all()
    serializer_class = BasicEmployeeSerializer

    def get_queryset(self):
        return (
            self.queryset.filter(ativo=True)
            .exclude(
                type_by_possession__in=[
                    "BFP",
                    "MAP",
                    "MAP2",
                    "SAP",
                    "APO",
                    "VOL",
                    "TCR",
                    "JCA",
                    "EXT",
                ]
            )
            .order_by("?")[:40]
        )

    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AidsEmployeeViewSet(BaseViewSet, ListModelMixin, RetrieveModelMixin):
    """
    View dos Auxílios de Servidores para o teste de conceito
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExternalJWTAuthentication]
    queryset = Servidor.objects.all()
    serializer_class = AidsEmployeeSerializer

    def get_queryset(self):
        return (
            self.queryset.filter(ativo=True)
            .exclude(
                type_by_possession__in=[
                    "BFP",
                    "MAP",
                    "MAP2",
                    "SAP",
                    "APO",
                    "VOL",
                    "TCR",
                    "JCA",
                    "EXT",
                ]
            )
            .order_by("-id")[:40]
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Método retrieve de afastamento
        """
        matricula_encrypted = kwargs.get("pk", None)
        if matricula_encrypted:
            try:
                matricula = self.serializer_class().decrypt_employee_matricula(
                    matricula_encrypted
                )
                queryset = self.queryset.filter(matricula=matricula)
            except Servidor.DoesNotExist as error:
                raise Http404 from error

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return self._list(request)

    def list(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self._list(request)

    def _list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
