from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import Dependent, DependentInclusion

log = getLogger(__name__)


class RequestFormDependentInclusion(EDOCManage):

    _model = DependentInclusion

    def model_to_dict(self, instance):
        data = super(RequestFormDependentInclusion, self).model_to_dict(instance)

        form = instance.protocolo.dependentinclusion

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                )
            }
        )

        return data


class RequestFormDependent(RestfulDRY):

    _model = Dependent

    full_text_index = ("name__icontains", "cpf__icontains")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.protocolo.requestform.dependent.Manage")'
        )
