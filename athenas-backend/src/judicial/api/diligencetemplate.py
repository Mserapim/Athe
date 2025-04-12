# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DiligenceTemplate
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from engine.notification.models import Message


log = getLogger(__name__)


class EJudDiligenceTemplate(Restful):

    _model = DiligenceTemplate

    force_upper = False

    def json(self, args=[]):
        self.response.write('Ext._create("judicial.diligencetemplate.Manage")')

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            default_params=instance.default_params,
            header=instance.header,
            message=instance.message,
            mid=instance.mid,
        )

        return rst
