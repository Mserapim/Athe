# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import IdBadge
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormIdBadge(EDOCManage):

    _model = IdBadge

    def prepare_params(self, querydict):
        params = super(RequestFormIdBadge, self).prepare_params(querydict)

        is_reissue = params.get("is_reissue", "off") == "on"
        params.update(is_reissue=is_reissue)

        if is_reissue:
            try:
                params.update(reissue_reason=int(params.get("reissue_reason", "")))
            except ValueError:
                raise Exception(
                    "Por favor, preencha corretamente o campo Motivo da 2ª via."
                )
        else:
            params.update(reissue_reason=None)

        if not params.get("display_name", ""):
            raise Exception("Por favor, preencha corretamente o campo Nome no crachá.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormIdBadge, self).model_to_dict(instance)

        form = instance.protocolo.idbadge

        data.update(
            {
                "is_reissue": form.is_reissue,
                "reissue_reason": (
                    form.reissue_reason if form.reissue_reason is not None else ""
                ),
                "display_name": form.display_name or "",
            }
        )

        return data
