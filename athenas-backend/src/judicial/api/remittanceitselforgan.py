# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import RemittanceItselfOrgan
from contrib.nil import nil_pk, nil_unicode
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudRemittanceItselfOrgan(BasePartLawsuit, Restful):

    _model = RemittanceItselfOrgan

    def get_params(self, *args, **kargs):
        params = super(EJudRemittanceItselfOrgan, self).get_params(*args, **kargs)

        if "department" in params:
            if params.get("department") != "":
                field = getattr(self.Model, "department")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(department=query.get(pk=params.get("department")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(department=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudRemittanceItselfOrgan, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                text=instance.text,
                department=nil_pk(instance.department, None),
                department_unicode=nil_unicode(instance.department, None),
            )

        return rst
