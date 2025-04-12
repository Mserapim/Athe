# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import FunctionalIdentity
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormFunctionalIdentity(EDOCManage):

    _model = FunctionalIdentity

    def prepare_params(self, querydict):
        params = super(RequestFormFunctionalIdentity, self).prepare_params(querydict)

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

        if len(params.get("original_employment_date", "")) > 0:
            try:
                params.update(
                    original_employment_date=DateUtils.str_to_date(
                        params.get("original_employment_date")
                    )
                )
            except Exception:
                raise Exception(
                    "Por favor, preencha corretamente o campo Data admissão origem."
                )

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormFunctionalIdentity, self).model_to_dict(instance)

        form = instance.protocolo.functionalidentity

        original_employment_date = ""
        if form.original_employment_date is not None:
            original_employment_date = DateUtils.date_to_str(
                form.original_employment_date
            )

        data.update(
            {
                "is_reissue": form.is_reissue,
                "reissue_reason": (
                    form.reissue_reason if form.reissue_reason is not None else ""
                ),
                "original_public_institution": form.original_public_institution or "",
                "original_employment_date": original_employment_date,
                "original_job_position": form.original_job_position or "",
            }
        )

        return data
