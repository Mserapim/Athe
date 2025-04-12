from datetime import datetime

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from django.db.models import Q
from rh.pvf.const import REGULAR_VACATIONS, PREMIUM_LICENSE, INDIVIDUAL_VACATION
from rh.dayoff.models import AcquisitionPeriod, Configuration, GroupPeriod, Usufruct


log = getLogger(__name__)


class PVFRightType(RestfulDRY):
    _model = Configuration

    full_text_index = ("title__icontains",)

    def get_remainig_by_employee_total(self, instance):
        employee = employee_from_user(get_current_user())
        days_remaining = 0
        query = AcquisitionPeriod.objects.filter(
            group_period__configuration=instance.pk, employee=employee
        )
        filter_by_sub_type = query.filter(
            Q(group_period__configuration__sub_type_of_usufruct=REGULAR_VACATIONS)
            | Q(group_period__configuration__sub_type_of_usufruct=PREMIUM_LICENSE)
            | Q(group_period__configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION)
        )
        filter_by_date = query.filter(end_date_acquisition__lt=datetime.today().date())

        for acquisition_period in query:
            if acquisition_period not in filter_by_sub_type:
                days_remaining += acquisition_period.days_not_booked_cache

            elif acquisition_period in filter_by_date:
                real_days = acquisition_period.real_days
                booked_days = acquisition_period.booked_days
                days_remaining += real_days - booked_days

        return days_remaining

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)
        _dict_.update(
            {
                "days_balance": self.get_remainig_by_employee_total(instance),
            }
        )
        return _dict_

    def get_query(self, *args, **kwargs):
        query = super().get_query()

        employee = employee_from_user(get_current_user())
        ap = AcquisitionPeriod.objects.filter(employee=employee).values("group_period")

        query = self._model.objects.filter(
            pk__in=GroupPeriod.objects.filter(pk__in=ap).values("configuration")
        )

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.myrights.Manage")')


class PVFAcquisitionPeriod(RestfulDRY):
    _model = AcquisitionPeriod

    full_text_index = ("employee__pessoa_fisica__nome__icontains",)

    def get_query(self, *args, **kwargs):
        query = super().get_query()
        employee = employee_from_user(get_current_user())
        query = self._model.objects.filter(employee=employee).order_by(
            "-start_date_acquisition"
        )

        return query.order_by("group_period__year_reference").reverse()


class PVFUsufruct(RestfulDRY):
    _model = Usufruct

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)
        _dict_.update({"icons": instance.icons})
        return _dict_
