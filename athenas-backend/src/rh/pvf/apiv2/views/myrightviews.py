from apiv2.utils import response_api_view
from rh.pvf.apiv2.serializers.myrightserializers import *
from rh.models import Servidor
from rh.pvf.const import *
from rh.pvf.apiv2.filters import PVFMyRightsAqPeriodFilter, PVFMyRightsUsufructFilter
from contrib.middleware import set_current_user
from rh.dayoff.models import (
    AcquisitionPeriod,
    AcquisitionPeriodAttachment,
    Configuration,
    GroupPeriod,
    Usufruct,
)
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rest_framework.decorators import action
from rest_framework.response import Response


class PVFMyRightsViewSet(BaseRequestViewSet):
    """
    View dos tipos de direitos da tela meus direitos
    """

    queryset = Configuration.objects.all()
    serializer_class = PVFMyRightsSerializer

    def get_queryset(self):
        set_current_user(self.request.user)
        employee = Servidor.objects.get(user=self.request.user)
        ap = AcquisitionPeriod.objects.filter(employee=employee).values("group_period")
        queryset = self.queryset.filter(
            pk__in=GroupPeriod.objects.filter(pk__in=ap).values("configuration")
        )
        return self.filter_queryset(queryset)


class PVFMyRightsAqPeriodViewSet(BaseRequestViewSet):
    """
    View dos períodos aquisitivo da tela meus direitos
    """

    queryset = AcquisitionPeriod.objects.all()
    serializer_class = PVFMyRightsAqPeriodSerializer
    filterset_class = PVFMyRightsAqPeriodFilter

    def get_queryset(self):
        set_current_user(self.request.user)
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee).order_by(
            "-start_date_acquisition"
        )
        return self.filter_queryset(queryset)

    def get(self, request, *args, **kwargs):
        """Retorna as solicitações"""
        return self.list(request, *args, **kwargs)


class PVFMyRightsUsufructViewSet(BaseRequestViewSet):
    """
    View dos usufrutos da tela meus direitos
    """

    queryset = Usufruct.objects.all()
    serializer_class = PVFMyRightsUsufructSerializer
    filterset_class = PVFMyRightsUsufructFilter

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(activity__acquisition_period__employee=employee)
        return self.filter_queryset(queryset)

    @action(detail=True, methods=["GET"])
    def usufructs(self, request, pk=None):
        queryset = self.queryset.filter(activity__acquisition_period__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFAttachmentAqPeriodViewSet(BaseRequestViewSet):
    """
    View dos anexos do período aquisitivo
    """

    queryset = AcquisitionPeriodAttachment.objects.all()
    serializer_class = PVFAttachmentAqPeriodSerializer

    @action(detail=True, methods=["GET"])
    def attachments(self, request, pk=None):
        queryset = self.queryset.filter(acquisition_period__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)
