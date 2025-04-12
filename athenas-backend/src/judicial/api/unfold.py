# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Unfold
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_unicode

log = getLogger(__name__)


class EJudUnfold(BasePartLawsuit, Restful):

    _model = Unfold

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("unfold_document", "lawsuit"):
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
        rst = super(EJudUnfold, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                unfold_document=instance.unfold_document.pk,
                unfold_document_unicode=nil_unicode(instance.unfold_document, None),
            )

        return rst
