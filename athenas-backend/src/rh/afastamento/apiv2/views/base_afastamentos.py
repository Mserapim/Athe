from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apiv2.baseviews import BaseViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from auth.backend import ExternalJWTAuthentication
from rh.afastamento.apiv2.serializers.base_afastamentos import BasicAbsenceSerializer
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import Servidor

from contrib.utils import getLogger

log = getLogger(__name__)


class BaseAbsenceViewSet(BaseViewSet, ListModelMixin, RetrieveModelMixin):
    """
    View para os Afastamentos
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExternalJWTAuthentication]
    queryset = BaseLicencaAfastamento.objects.all()
    serializer_class = BasicAbsenceSerializer

    def get_queryset(self):
        return (
            self.queryset.filter(servidor__ativo=True)
            .exclude(
                servidor__type_by_possession__in=[
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
                queryset = self.queryset.filter(servidor__matricula=matricula)
            except Servidor.DoesNotExist as error:
                log.error(error)
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
