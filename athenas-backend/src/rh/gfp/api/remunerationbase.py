# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.models import RemunerationBase, RemunerationPeriod


log = getLogger(__name__)


class GFPRemunerationBase(RestfulDRY):

    _model = RemunerationBase

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.remunerationbase.RemunerationBaseManage")'
        )


class GFPRemunerationPeriod(RestfulDRY):

    _model = RemunerationPeriod

    full_text_index = (
        "remuneration__employee__pessoa_fisica__nome__icontains",
        "remuneration__employee__matricula__iexact",
        "remuneration__identifier__icontains",
    )

    def model_to_dict(self, instance):
        """DOCSTRING."""
        _dict = super(GFPRemunerationPeriod, self).model_to_dict(instance)
        _dict.update(
            employee_unicode=str(instance.remuneration.employee),
            identifier=str(instance.remuneration.identifier),
            link=str(instance.remuneration.link),
            salary=instance.remuneration.salary,
            pct_gratification=(
                float(instance.remuneration.base_gratification)
                if instance.remuneration.percentage
                else ""
            ),
            pct_value=(
                float(instance.remuneration.base_value)
                if instance.remuneration.percentage
                else ""
            ),
            percentage=instance.remuneration.percentage,
            onus=instance.remuneration.onus,
        )

        return _dict

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.remunerationbase.RemunerationPeriodManage")'
        )
