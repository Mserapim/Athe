# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import ElectoralLicense
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormElectoralLicense(EDOCManage):

    _model = ElectoralLicense

    def prepare_params(self, querydict):
        params = super(RequestFormElectoralLicense, self).prepare_params(querydict)

        if not params.get("description", ""):
            raise Exception("Por favor, preencha corretamente o campo Descrição.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormElectoralLicense, self).model_to_dict(instance)

        form = instance.protocolo.electorallicense

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                ),
                "description": form.description if form.description is not None else "",
            }
        )

        return data
