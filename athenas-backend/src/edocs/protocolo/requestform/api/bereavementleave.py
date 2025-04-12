# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import BereavementLeave
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormBereavementLeave(EDOCManage):

    _model = BereavementLeave

    def prepare_params(self, querydict):
        params = super(RequestFormBereavementLeave, self).prepare_params(querydict)

        if not params.get("degree_of_kinship", ""):
            raise Exception(
                "Por favor, preencha corretamente o campo Grau de parentesco."
            )

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormBereavementLeave, self).model_to_dict(instance)

        form = instance.protocolo.bereavementleave

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                ),
                "degree_of_kinship": (
                    form.degree_of_kinship if form.degree_of_kinship is not None else ""
                ),
            }
        )

        return data
