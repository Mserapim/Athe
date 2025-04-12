# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import FuneralAllowance
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormFuneralAllowance(EDOCManage):

    _model = FuneralAllowance

    def prepare_params(self, querydict):
        params = super(RequestFormFuneralAllowance, self).prepare_params(querydict)

        if not params.get("degree_of_kinship", ""):
            raise Exception(
                "Por favor, preencha corretamente o campo Grau de parentesco."
            )

        if not params.get("deceased_name", ""):
            raise Exception(
                "Por favor, preencha corretamente o campo Nome do(a) falecido(a)."
            )

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormFuneralAllowance, self).model_to_dict(instance)

        form = instance.protocolo.funeralallowance

        data.update(
            {
                "contact_number": form.contact_number or "",
                "degree_of_kinship": form.degree_of_kinship or "",
                "deceased_name": form.deceased_name or "",
            }
        )

        return data
