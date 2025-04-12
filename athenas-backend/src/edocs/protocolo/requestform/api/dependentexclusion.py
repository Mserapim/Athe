from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import (
    DependentExclusion,
    DependentExclusionItem,
)
from judicial.api.mixins import (
    FilterEvalValueMixin,
)  # TODO: tornar o mixin segmentável e parte do core
from rh.api.dependente import RHDependenteRestful

log = getLogger(__name__)


class RequestFormDependentExclusion(EDOCManage):

    _model = DependentExclusion

    def model_to_dict(self, instance):
        data = super(RequestFormDependentExclusion, self).model_to_dict(instance)

        form = instance.protocolo.dependentexclusion

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                )
            }
        )

        return data


class RequestFormDependentExclusionItem(RestfulDRY):

    _model = DependentExclusionItem

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.protocolo.requestform.dependentexclusionitem.Manage")'
        )
