# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import ChildbirthAllowance
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormChildbirthAllowance(EDOCManage):

    _model = ChildbirthAllowance

    def prepare_params(self, querydict):
        params = super(RequestFormChildbirthAllowance, self).prepare_params(querydict)

        if not params.get("child_name", ""):
            raise Exception("Por favor, preencha corretamente o campo Nome da criança.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormChildbirthAllowance, self).model_to_dict(instance)

        form = instance.protocolo.childbirthallowance

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                ),
                "child_name": form.child_name if form.child_name is not None else "",
            }
        )

        return data
