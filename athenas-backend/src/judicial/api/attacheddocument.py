# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import AttachedDocument
from contrib.nil import nil_display, nil_pk
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EJudAttachedDocument(BasePartLawsuit, Restful):

    _model = AttachedDocument

    def complement_model_to_dict(self, instance):
        rst = super(EJudAttachedDocument, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                attached_type=instance.attached_type,
                attached_type_display=nil_display(instance, "attached_type", None),
                type_part=instance.type_part,
                resume=instance.resume,
                attached_title=instance.attached_title,
                diligence=nil_pk(instance.diligence, None),
            )

        return rst

    def get_params(self, *args, **kargs):
        params = super(EJudAttachedDocument, self).get_params(*args, **kargs)

        for attr in ("diligence",):
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
