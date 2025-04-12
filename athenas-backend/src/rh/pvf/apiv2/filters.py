from contrib.base_converter import str_to_bool
from django_filters import rest_framework as filters
from rh.dayoff.const import INTERNS_RECESS
from rh.dayoff.models import AcquisitionPeriod, Usufruct
from rh.pvf.apiv2.utils.approval import (
    filtro_tipo_servidor,
    get_employee_approver,
    group_list,
)
from rh.pvf.const import (
    DATA_CONFIG_VACATION,
    GROUPS_PVF,
    QTD_DAYS_RECESS,
    QTD_DAYS_RECESS_PARCIAL,
    REQUEST_STATUS_GROUP,
    RESIDENTS_RECESS,
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_EFFECTIVE,
    STS_REJECTED,
    STS_WAI_APPROVER,
)
from rest_framework.filters import BaseFilterBackend
from django.db.models import Q
from rh.pvf.models import PointJustification, PortalRequestUsufruct
from rh.models import Servidor
from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class PVFRequestListFilterBackend(BaseFilterBackend):
    """
    Classe responsável por realizar os filtros do PortalRequest da tela minhas solicitações.
    """

    def filter_queryset(self, request, queryset, view):
        status_list = request.query_params.getlist("status[]")
        request_type_list = request.query_params.getlist("request_type[]")
        if status_list:
            queryset = queryset.filter(Q(status__in=status_list))
        if request_type_list:
            queryset = queryset.filter(Q(portal_request_type__in=request_type_list))

        return queryset


class PVFApprovalRequestListFilterBackend(BaseFilterBackend):
    """
    Classe responsável por realizar os filtros do PortalRequest da tela de aprovações.
    """

    def get_type_possessions(self, typeslist):
        """
        Recebe uma lista de tipos.
        Args:
            lista_tipos (list): Uma lista de tipos.
        Returns:
            list: Uma nova lista contendo os type_by_possessions dos servidores.
        """
        type_by_possessions = []
        for employee_type in typeslist:
            if employee_type == "SERVIDOR":
                type_by_possessions.extend(
                    ["EFE", "CMS", "ECM", "RCM", "RFC", "EFC", "REQ", "VOL", "EXT"]
                )
            elif employee_type == "MEMBRO":
                type_by_possessions.extend(["MBR", "MEL", "MEC"])
            elif employee_type == "ESTAGIARIO":
                type_by_possessions.extend(["EST"])
            elif employee_type == "RESIDENTE":
                type_by_possessions.extend(["RES"])
        return type_by_possessions

    def filter_queryset(self, request, queryset, view):
        employee = request.user.servidor
        status_list = request.query_params.getlist("status[]")
        request_type_list = request.query_params.getlist("request_type[]")
        approvals_list = request.query_params.getlist("approvals[]")
        employee_types_list = request.query_params.getlist("employe_types[]")
        employee_id = request.query_params.get("employee_id")
        pending_request = request.query_params.get("pending_request")
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")

        if pending_request and pending_request.lower() == "true":
            steps = group_list(employee)
            queryset = queryset.filter(
                Q(approver=employee) | Q(step_current__in=steps)
            ).exclude(
                status__in=[
                    STS_EFFECTIVE,
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )

            filter_employee_types = filtro_tipo_servidor(employee)
            if filter_employee_types:
                queryset = queryset.filter(
                    employee__type_by_possession__in=filter_employee_types
                )

        if status_list:
            queryset = queryset.filter(status__in=status_list)
        if request_type_list:
            queryset = queryset.filter(portal_request_type__in=request_type_list)
        if approvals_list:
            if approvals_list in [1]:
                queryset = queryset.filter(
                    Q(step_current__in=approvals_list) | Q(approver=employee)
                )
            else:
                queryset = queryset.filter(step_current__in=approvals_list)
        if employee_types_list:
            queryset = queryset.filter(
                employee__type_by_possession__in=self.get_type_possessions(
                    employee_types_list
                )
            )
        if employee_id:
            queryset = queryset.filter(employee__id=employee_id)

        if data_inicio and data_fim:
            queryset = queryset.filter(
                date__range=(
                    DateUtils.str_to_date(data_inicio, format="%Y-%m-%d"),
                    DateUtils.str_to_date(data_fim, format="%Y-%m-%d"),
                )
            )

        return queryset


class PVFAcquisitionPeriodFilter(filters.FilterSet):
    """
    classe dos filtros da api PVFAcquisitionPeriodViewSet dos períodos aquisitivos das solicitações VDF
    """

    type_usufruct = filters.Filter(
        field_name="group_period__configuration__sub_type_of_usufruct"
    )

    class Meta:
        model = AcquisitionPeriod
        fields = ["type_usufruct"]


class PVFMyRightsAqPeriodFilter(filters.FilterSet):
    """
    classe dos filtros da api PVFMyRightsAqPeriodViewSet dos períodos aquisitivo da tela meus direitos
    """

    config = filters.Filter(field_name="group_period__configuration__id")

    class Meta:
        model = AcquisitionPeriod
        fields = ["config"]


class PVFMyRightsUsufructFilter(filters.FilterSet):
    """
    classe dos filtros da api PVFMyRightsUsufructViewSet dos usufrutos da tela meus direitos
    """

    aq_period = filters.Filter(field_name="activity__acquisition_period__id")

    class Meta:
        model = Usufruct
        fields = ["aq_period"]


class PVFVactionConfigFilter:
    """
    classe dos filtros da api PVFVactionConfigView das combinações de férias
    """

    @classmethod
    def filter_config_vacation(cls, type_usufruct, total_days, employee):
        """metódo responsável por realizar o filtro da combinações de férias

        Returns:
            dict:
        """
        type_usufruct = int(type_usufruct)
        if not total_days:
            request = PortalRequestUsufruct()
            acq_period = request.period_acquisition_usufruct(employee, type_usufruct)
            if acq_period:
                total_days = acq_period.days_not_booked_cache
            else:
                total_days = 0

        if type_usufruct in [RESIDENTS_RECESS, INTERNS_RECESS]:
            total_days = QTD_DAYS_RECESS_PARCIAL
        else:

            for v in DATA_CONFIG_VACATION:
                if v["type_usufruct"] == type_usufruct and v["total_days"] == int(
                    total_days
                ):
                    return [v]

        return [
            {
                "type_usufruct": type_usufruct,
                "total_days": int(total_days),
                "options": [{"enjoyment": [int(total_days)], "indemnity": []}],
            }
        ]


class PVFMinhasSubstituicoesFilterBackend(BaseFilterBackend):
    """
    Classe responsável por realizar os filtros da tela minhas substituições.
    """

    def filter_queryset(self, request, queryset, view):
        dt_inicio = (
            request.query_params.get("dt_inicio")
            if request.query_params.get("dt_inicio")
            else None
        )
        dt_fim = (
            request.query_params.get("dt_fim")
            if request.query_params.get("dt_fim")
            else None
        )
        tipo_acao = (
            int(request.query_params.get("tipo_acao"))
            if request.query_params.get("tipo_acao")
            else None
        )

        if dt_inicio and dt_fim:
            queryset = queryset.filter(
                Q(data_inicio__gte=dt_inicio) & Q(data_fim__lte=dt_fim)
            )
        elif dt_inicio:
            queryset = queryset.filter(Q(data_inicio__gte=dt_inicio))

        servidor = Servidor.objects.get(user=request.user)
        if tipo_acao == 1:  # Substituto
            queryset = queryset.filter(
                Q(servidor=servidor) & ~Q(servidor_substituido=servidor)
            )
        elif tipo_acao == 2:  # Substituído
            queryset = queryset.filter(
                Q(servidor_substituido=servidor) & ~Q(servidor=servidor)
            )

        return queryset


class PVFVendaSubstituicoesFilterBackend(BaseFilterBackend):
    """
    Classe responsável por realizar os filtros da tela Venda de Cumulativo de Substituições.
    """

    def filter_queryset(self, request, queryset, view):
        dt_inicio = (
            request.query_params.get("dt_inicio")
            if request.query_params.get("dt_inicio")
            else None
        )
        dt_fim = (
            request.query_params.get("dt_fim")
            if request.query_params.get("dt_fim")
            else None
        )
        tipo_acao = (
            int(request.query_params.get("tipo_acao"))
            if request.query_params.get("tipo_acao")
            else None
        )
        dt_ini_periodo = (
            request.query_params.get("dt_ini_periodo")
            if request.query_params.get("dt_ini_periodo")
            else None
        )
        dt_fim_periodo = (
            request.query_params.get("dt_fim_periodo")
            if request.query_params.get("dt_fim_periodo")
            else None
        )
        dt_ini_abrangencia = (
            request.query_params.get("dt_ini_abrangencia")
            if request.query_params.get("dt_ini_abrangencia")
            else None
        )
        dt_fim_abrangencia = (
            request.query_params.get("dt_fim_abrangencia")
            if request.query_params.get("dt_fim_abrangencia")
            else None
        )

        if dt_inicio and dt_fim:
            queryset = queryset.filter(
                Q(data_inicio__gte=dt_inicio) & Q(data_fim__lte=dt_fim)
            )
        elif dt_inicio:
            queryset = queryset.filter(Q(data_inicio__gte=dt_inicio))

        servidor = Servidor.objects.get(user=request.user)
        if tipo_acao == 1:  # Substituto
            queryset = queryset.filter(
                Q(servidor=servidor) & ~Q(servidor_substituido=servidor)
            )
        elif tipo_acao == 2:  # Substituído
            queryset = queryset.filter(
                Q(servidor_substituido=servidor) & ~Q(servidor=servidor)
            )

        if dt_ini_periodo and dt_fim_periodo:
            queryset = queryset.filter(
                Q(data_inicio__gte=dt_ini_periodo) & Q(data_fim__lte=dt_fim_periodo)
            )
        elif dt_ini_periodo:
            queryset = queryset.filter(Q(data_inicio__gte=dt_ini_periodo))

        if dt_ini_abrangencia and dt_fim_abrangencia:
            queryset = queryset.filter(
                Q(data_inicio__gte=dt_ini_abrangencia)
                & Q(data_fim__lte=dt_fim_abrangencia)
            )
        elif dt_ini_abrangencia:
            queryset = queryset.filter(Q(data_inicio__gte=dt_ini_abrangencia))

        return queryset


class PVFListaJustificativasFilter(BaseFilterBackend):
    """
    classe dos filtros da api PVFListPointJustificationView
    """

    def filter_queryset(self, request, queryset, view):
        cancelado = request.query_params.get("cancelado")
        if cancelado:
            queryset = queryset.filter(cancelado=str_to_bool(cancelado))
        return queryset
