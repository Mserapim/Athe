# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import AdjustmentLawsuit
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_pk, nil_unicode

log = getLogger(__name__)


class EJudAdjustmentLawsuit(BasePartLawsuit, Restful):

    _model = AdjustmentLawsuit

    def get_params(self, *args, **kargs):
        params = super(EJudAdjustmentLawsuit, self).get_params(*args, **kargs)

        if "new_acting_zone" in params:
            if params.get("new_acting_zone") != "":
                field = getattr(self.Model, "new_acting_zone")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        new_acting_zone=query.get(pk=params.get("new_acting_zone"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(new_acting_zone=None)

        if "new_main_matter" in params:
            if params.get("new_main_matter") != "":
                field = getattr(self.Model, "new_main_matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        new_main_matter=query.get(pk=params.get("new_main_matter"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(new_main_matter=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudAdjustmentLawsuit, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                last_title=instance.last_title,
                new_title=instance.new_title,
                last_acting_zone=nil_pk(instance.last_acting_zone, None),
                last_acting_zone_unicode=nil_unicode(instance.last_acting_zone, None),
                new_acting_zone=nil_pk(instance.new_acting_zone, None),
                new_acting_zone_unicode=nil_unicode(instance.new_acting_zone, None),
                new_main_matter=nil_pk(instance.new_main_matter, None),
                new_main_matter_unicode=nil_unicode(instance.new_acting_zone, None),
            )

        return rst
