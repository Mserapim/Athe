# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from edocs.protocolo.models import GroupGeneralOrgan
from contrib.middleware import get_current_user
from django.db.models import Q

log = getLogger(__name__)


class EDOCGroupGeneralOrgan(RestfulDRY):

    _model = GroupGeneralOrgan

    full_text_index = ("title__icontains",)

    force_orm_single = True

    force_upper = True
    force_persist_boolean_fields = ["all_work_location"]

    def get_query(self):
        query = super(EDOCGroupGeneralOrgan, self).get_query()
        user = get_current_user()

        query = query.filter(
            Q(
                Q(level_access=1)
                | Q(
                    department__in=employee_from_user(
                        user
                    ).work_locations_effective_exercise.values("pk")
                )
            )
        )

        return query

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(total_destinations=instance.destinations.count())

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.protocolo.GroupGeneralOrganManage")')
