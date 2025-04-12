# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.socialsecurity.models import EmploymentBond

log = getLogger(__name__)


class SSEmploymentBond(RestfulDRY):

    _model = EmploymentBond

    full_text_index = ("employer__icontains",)

    force_upper = True

    force_persist_boolean_fields = ["contribution_double", "public_employee"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.socialsecurity.EmploymentBondManage")')

    def model_to_dict(self, instance):
        _dict_ = super(SSEmploymentBond, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": instance.get_icons,
                "liquid_days": instance.liquid_days,
                "possession_unicode": (
                    "%s" % instance.possession.quadro
                    if instance.possession and instance.possession.quadro
                    else ""
                ),
                "deduction": instance.deduction,
            }
        )

        return _dict_
