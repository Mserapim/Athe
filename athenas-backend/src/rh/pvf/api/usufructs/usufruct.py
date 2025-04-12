from dateutil.relativedelta import relativedelta
from datetime import datetime
from rh.dayoff.models import Activity, Usufruct, Choice
from contrib.newrest import RestfulDRY
from django.db.models import Q
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger
from rh.dayoff.api.usufruct import DAYOFFUsufruct
from rh.dayoff.models import AcquisitionPeriod
from rh.dayoff.const import (
    CONF_VACATION,
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_CHANGED,
    USU_CHANGING,
    USU_HOMOLOGATED,
    USU_NOT_AUTHORIZED,
    USU_SOLD,
    USU_SUSPENDED,
    USU_INTERRUPTED,
    USU_SUBSTITUTE,
    ACT_BOOK,
    ACT_CHANGE,
    ACT_SUSPEND,
    ACT_INTERRUPT,
    ACT_INDEMNIFY,
    ACT_SELL,
    USU_NEW,
    USU_ENJOYED,
    USU_ENJOYING,
    CONF_BIRTHDAY_BREAK,
    CONF_RECESS,
    CONF_ELECTORAL_SLACK,
    CONF_DUTTY,
    CONF_COMPENSATION,
)
from rh.pvf.const import (
    COMP_VACATION_MEMBERS,
    INDIVIDUAL_VACATION,
    PREMIUM_LICENSE,
    REGULAR_VACATIONS,
    REQUEST_TYPE_RETIFICATION,
    USUFRUCT_STATUS,
    REQUEST_TYPE_SCHEDULE,
)

log = getLogger(__name__)


class PVFUsufruct(DAYOFFUsufruct):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalusufruct.Manage")')

    def get_type_activity(self, instance):
        if not instance.start_date:
            return "Venda"
        else:
            return "Usufruto"
        # if instance.activity.type_of_activity == ACT_BOOK:
        #     return "Usufruto"
        # elif instance.activity.type_of_activity == ACT_SELL:
        #     return "Venda"
        # elif instance.activity.type_of_activity == ACT_CHANGE:
        #     return "Alteração"

    def get_status_type(self, instance):
        for usu in USUFRUCT_STATUS:
            if instance.status == usu:
                return USUFRUCT_STATUS.get(usu)

    def get_sale_usufruct(self, instance):
        if instance.activity.configuration.max_days_sale:
            if instance.activity.configuration.max_days_sale > 0:
                return True
        else:
            return False

    def get_acquisition_period(self, instance):
        return instance.activity.acquisition_period.pk

    def model_to_dict(self, instance):
        _dict_ = super(PVFUsufruct, self).model_to_dict(instance)

        _dict_.update(
            subtype_usufruct=instance.activity.configuration.get_sub_type_of_usufruct_display(),
            subtype_id=instance.activity.configuration.sub_type_of_usufruct,
            type_activity=self.get_type_activity(instance),
            start_date_acquisition=instance.activity.acquisition_period.start_date_acquisition.strftime(
                "%d/%m/%Y"
            ),
            status_type=self.get_status_type(instance),
            sale_usufruct=self.get_sale_usufruct(instance),
            acquisition_period=self.get_acquisition_period(instance),
            prev_competence_paid=instance.prev_competence_paid,
        )
        return _dict_


class PVFUsufructRetification(PVFUsufruct):

    def get_query(self):
        query = super(PVFUsufructRetification, self).get_query()
        employee = employee_from_user(get_current_user())
        amount_past_days = 0
        try:
            amount_past_days = Choice.objects.get(
                name="VDF_AMOUNT_PAST_DAYS_FOR_CANCEL_AND_RETIFICATION", active=True
            ).value
        except Exception as err:
            log.error(err)

        if employee.tipo == "M":
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
            ids_acq_period = [x[0] for x in acquisition_period]

            usufructs = (
                Usufruct.objects.filter(
                    activity__acquisition_period__pk__in=ids_acq_period
                )
                .exclude(
                    Q(
                        end_date__gte=datetime.now()
                        - relativedelta(days=amount_past_days)
                    )
                    & ~Q(
                        activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                            REGULAR_VACATIONS,
                            INDIVIDUAL_VACATION,
                            PREMIUM_LICENSE,
                        ]
                    )
                )
                .exclude(~Q(end_date__lt=datetime.now()))
                .values_list("pk")
            )
            usufruct_ids = [x[0] for x in usufructs]

            return (
                query.filter(
                    Q(activity__acquisition_period__employee=employee),
                    Q(
                        status__in=[
                            USU_HOMOLOGATED,
                            USU_SOLD,
                            USU_ENJOYING,
                            USU_ENJOYED,
                        ]
                    ),
                    ~Q(
                        activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=self._get_list_of_non_retifications_usufructs()
                    ),
                )
                .exclude(
                    pk__in=usufruct_ids
                    + self._get_sold_usufructs_date(acquisition_period)
                )
                .exclude(
                    activity__acquisition_period__pk__in=self.totally_paid_periods(
                        employee
                    )
                )
            )

        else:
            return query.filter(
                Q(activity__acquisition_period__employee=employee),
                Q(status__in=[USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED]),
                Q(end_date__gte=datetime.now() - relativedelta(days=amount_past_days))
                & ~Q(
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                        REGULAR_VACATIONS,
                        INDIVIDUAL_VACATION,
                        PREMIUM_LICENSE,
                    ]
                )
                | Q(end_date__gte=datetime.now()),
                ~Q(
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=self._get_list_of_non_retifications_usufructs()
                ),
                ~Q(activity__type_of_activity=ACT_CHANGE),
            )

    def _get_list_of_non_retifications_usufructs(self):
        """
        Função que consulta Parâmetro do Sistema que verifica quais itens não serão passíveis de retificação e retorna em uma lista.
        :returns: (list)
        """
        try:
            list_exclude_usufruct = Choice.objects.filter(
                name="PVF_SUB_CONFIGURATION_EXCLUDE_USUFRUCT", active=True
            ).values_list("value")
            ids_exclude_usufruct = [x[0] for x in list_exclude_usufruct]
            return ids_exclude_usufruct
        except Exception as e:
            log.error(e)

    def _get_sold_usufructs_date(self, acq_period):
        """
        Função que verifica se já houve o gozo da primeira parcela dento do período aquisitivo e retorna lista com as 'pk' dos usufrutos vendidos e recebidos
        :returns: (list)
        """
        try:
            list_of_started_acq_per = [x[0] for x in acq_period]
            sold_usufruted = Usufruct.objects.filter(
                activity__acquisition_period__id__in=list_of_started_acq_per,
                status=USU_SOLD,
            ).values_list("pk")
            return [x[0] for x in sold_usufruted]
        except Exception as e:
            log.error(e)

    def totally_paid_periods(self, employee):
        """
        Retorna uma lista de pk's dos períodos aquisitivos que tiveram todos os dias vendidos, filtrados pelo servidor
        :returns:
            list_of_totally_paid_periods (list)
        """
        list_of_totally_paid_periods = []
        acq_periods = AcquisitionPeriod.objects.filter(employee=employee)
        for acq in acq_periods:
            if acq.days == acq.paid_days:
                list_of_totally_paid_periods.append(acq.pk)
        return list_of_totally_paid_periods

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalusufructretification.Manage")')
