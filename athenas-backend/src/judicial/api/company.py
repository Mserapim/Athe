# -*- coding: utf-8 -*-
from judicial.api.bloke import EJudBloke
from contrib.utils import getLogger
from judicial.models import Company
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudCompany(EJudBloke):

    _model = Company

    def get_params(self, *args, **kargs):
        params = EJudBloke.get_params(self, *args, **kargs)

        if "bloke" in params:
            if params.get("bloke") != "":
                field = getattr(self.Model, "bloke")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(bloke=query.get(pk=params.get("bloke")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(bloke=None)

        return params
