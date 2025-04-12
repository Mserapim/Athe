# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import AuthorizationExternalAccess
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_pk, nil_unicode

log = getLogger(__name__)


class EJudAuthorizationExternalAccess(BasePartLawsuit, Restful):

    _model = AuthorizationExternalAccess

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("request_external_access", "lawsuit"):
            if attr in params:
                if params.get(attr) != "":
                    field = getattr(self.Model, attr)
                    query = field.get_queryset()
                    try:
                        params.update({attr: query.get(pk=params.get(attr))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({attr: None})

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudAuthorizationExternalAccess, self).complement_model_to_dict(
            instance
        )

        if instance.can_read:
            rst.update(
                justification=instance.justification,
                request_external_access=nil_pk(instance.request_external_access, None),
                request_external_access_unicode=nil_unicode(
                    instance.request_external_access, None
                ),
                state=instance.state,
            )

        return rst
