# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from raf.models import SubItemCalculate

log = getLogger(__name__)


class RAFSubItemCalculate(RestfulDRY):

    _model = SubItemCalculate

    def model_to_dict(self, instance):
        _dict_ = super(RAFSubItemCalculate, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": instance.icons,
                # 'list_taxonomy': u'', #nil_unicode(instance.list_taxonomy, None),
            }
        )

        return _dict_
