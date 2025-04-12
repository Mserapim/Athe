from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from drf_spectacular.utils import extend_schema
from rh.models import Servidor
from contrib.middleware import set_current_user
from rest_framework import status
from rest_framework.response import Response
from rh.pvf.models import PortalRetificationSchedule
from rh.dayoff.models import Usufruct
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.apiv2.serializers.retificationserializers import (
    PVFRetificationScheduleSerializers,
)
from rh.pvf.apiv2.serializers.cancelserializers import PVFCancelUsufructSerializer
from rh.dayoff.const import USU_HOMOLOGATED, USU_SOLD, USU_ENJOYING, USU_ENJOYED
from rh.dayoff.models import AcquisitionPeriod
from django.db.models.query_utils import Q
from dateutil.relativedelta import relativedelta
from rh.pvf.apiv2.utils.retification import (
    get_list_of_non_retifications_usufructs,
    totally_paid_periods,
    get_sold_usufructs_date,
)
from rh.dayoff.const import *
from standard.models import Choice
from datetime import datetime


class PVFRetificationScheduleViewSet(GenericViewSet):
    """
    View da solicitação de retificação da programação
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRetificationSchedule.objects.filter()
    serializer_class = PVFRetificationScheduleSerializers

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee)
        return queryset

    def post(self, request, *args, **kwargs):
        """ Cria uma nova solicitação de retificação de programação """
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "usufructs_in": {
                        "type": "[{start_date:date,end_date:date:0,days:0,sale_usufruct:0}]"
                    },
                    "observation": {"type": "string"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "usufructs_ids": {"type": "[]"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFRetificationUsufructViewSet(BaseRequestViewSet):
    """
    View que retorna os usufrutos que podem ser retificados
    """

    queryset = Usufruct.objects.filter()
    serializer_class = PVFCancelUsufructSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        qtd_days = 0

        if employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            amount_past_days = Choice.objects.filter(
                name="PVF_AMOUNT_PAST_DAYS_FOR_RETIFICATION_MEMBER"
            ).first()
            if amount_past_days:
                qtd_days = amount_past_days.value
            acquisition_period = AcquisitionPeriod.objects.filter(
                Q(employee=employee),
                Q(activities__usufructs__end_date__lte=datetime.now())
                & ~Q(
                    activities__usufructs__status__in=[
                        USU_SUSPENDED,
                        USU_CANCELED,
                        USU_CHANGED,
                    ]
                )
                | Q(activities__usufructs__status=USU_CHANGING),
            ).values_list("pk")

            queryset = (
                self.queryset.filter(
                    Q(activity__acquisition_period__employee=employee),
                    Q(
                        status__in=[
                            USU_HOMOLOGATED,
                            USU_ENJOYING,
                            USU_ENJOYED,
                            USU_CHANGING,
                        ]
                    ),
                    Q(start_date__gte=datetime.now() - relativedelta(days=qtd_days)),
                    ~Q(
                        activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=get_list_of_non_retifications_usufructs()
                    ),
                )
                .exclude(pk__in=get_sold_usufructs_date(acquisition_period))
                .exclude(
                    activity__acquisition_period__pk__in=totally_paid_periods(employee)
                )
            )
        else:
            amount_past_days = Choice.objects.filter(
                name="PVF_AMOUNT_PAST_DAYS_FOR_RETIFICATION"
            ).first()
            if amount_past_days:
                qtd_days = amount_past_days.value
            queryset = self.queryset.filter(
                Q(activity__acquisition_period__employee=employee),
                Q(status__in=[USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED]),
                Q(start_date__gte=datetime.now() - relativedelta(days=qtd_days)),
                ~Q(
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=get_list_of_non_retifications_usufructs()
                ),
                ~Q(activity__type_of_activity=ACT_CHANGE),
            )
        return self.filter_queryset(queryset)
