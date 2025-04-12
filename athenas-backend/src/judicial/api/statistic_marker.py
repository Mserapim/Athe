# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from judicial.models import StatisticMarker


log = getLogger(__name__)


class EJudStatisticMarker(RestfulDRY):

    _model = StatisticMarker

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("judicial.statisticMarker.Manage")')

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(count=instance.lawsuits.count())

        return rst
