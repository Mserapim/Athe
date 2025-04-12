# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, get_json_engine, getLogger, DateUtils
from rh.dayoff.models import Usufruct

json = get_json_engine()

log = getLogger(__name__)


class DAYOFFUsufruct(RestfulDRY):

    _model = Usufruct

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.usufruct.Manage")')

    @login_required(type="JSON")
    def get_conflicts(self, args=[]):
        obj = {
            "collection": [],
        }
        conflicts = Usufruct.objects.get(
            pk=self.request.GET.get("usufructPk")
        ).get_conflicts()
        for conflict in conflicts:
            for value in conflicts.get(conflict):
                info = value.get("info")
                label_origin = value.get("label_origin")
                print(f"{label_origin} - {info}")
                obj["collection"].append(value)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFUsufruct, self).model_to_dict(instance)
        authorizers = []
        if instance.activity.immediate_authorization_by:
            authorizers.append(f"{instance.activity.immediate_authorization_by}")
        if instance.activity.immediate_authorization_by:
            authorizers.append(f"{instance.activity.immediate_authorization_by}")
        if instance.activity.mediate_authorization_by:
            authorizers.append(f"{instance.activity.mediate_authorization_by}")
        _dict_.update({"icons": instance.icons})
        _dict_.update({"employee_unicode": f"{instance.employee}"})
        _dict_.update({"authorized_by_unicode": ",".join(authorizers)})
        _dict_.update(
            {
                "authorized_at": (
                    DateUtils.date_to_str(instance.activity.authorized_at)
                    if instance.activity.authorized_at
                    else ""
                )
            }
        )
        return _dict_


class DAYOFFEmployeeUsufruct(DAYOFFUsufruct):

    def get_query(self):
        query = super(DAYOFFEmployeeUsufruct, self).get_query()

        return query.filter(
            activity__acquisition_period__employee=employee_from_user(
                get_current_user()
            ),
            activity__acquisition_period__blocked=False,
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.usufruct.employee.EmployeeManage")')
