# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import MemberOrgan
import raf.api.util

log = getLogger(__name__)


class INSPECTIONMemberOrgan(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = MemberOrgan

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.memberorgan.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONMemberOrgan, self).model_to_dict(instance)
        _dict_.update(
            {
                # 'icons': instance.icons,
                "member_role_display": instance.get_member_role_display(),
            }
        )
        return _dict_
