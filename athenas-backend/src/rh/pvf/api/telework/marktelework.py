# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.pvf.models import MarkTelework


log = getLogger(__name__)


class PVFMarkTelework(RestfulDRY):

    _model = MarkTelework

    def model_to_dict(self, instance):
        _dict_ = super(PVFMarkTelework, self).model_to_dict(instance)
        _dict_.update(
            description_mark=instance.description_mark,
            mark=instance.mark,
            is_update=instance.is_update,
            mark_plan_periodicity=instance.mark_plan.periodicity,
            mark_plan_periodicity_display=instance.mark_plan.get_periodicity_display(),
            start_date=instance.mark_plan.data_inicio.strftime("%d/%m/%Y"),
            end_date=(
                instance.mark_plan.data_fim.strftime("%d/%m/%Y")
                if instance.mark_plan.data_fim
                else ""
            ),
        )
        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.sendtelework.MarkTeleworkManage")')
