# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from judicial.models import (
    OutCourtLawsuit,
    RemittanceInternal,
    SpecialRemittanceInternal,
)
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime

from rh.models import Lotacao
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudRemittanceInternal(BasePartLawsuit, Restful):

    _model = RemittanceInternal

    def get_params(self, *args, **kargs):
        params = super(EJudRemittanceInternal, self).get_params(*args, **kargs)

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

        if "conflict" in params:
            params.update(conflict=params.get("conflict").lower() == "on")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudRemittanceInternal, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                conflict=instance.conflict,
                text=instance.text,
                department=nil_pk(instance.department, None),
                department_unicode=nil_unicode(instance.department, None),
            )

        return rst

    def remittance_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                department = Lotacao.objects.get(
                    pk=self.request.POST.get("department", None)
                )
                location = Lotacao.objects.get(
                    pk=self.request.POST.get("location", None)
                )

                for lw in lawsuits:
                    obj = RemittanceInternal()
                    obj.department = department
                    obj.lawsuit = lw
                    obj.location = location

                    obj.save()
                    obj.sign_part()
                    obj.create_cache_document()

        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(
                success=True, message="Procedimentos finalizados com sucesso."
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))


class EJudSpecialRemittanceInternal(BasePartLawsuit, Restful):

    _model = SpecialRemittanceInternal

    def get_params(self, *args, **kargs):
        params = super(EJudSpecialRemittanceInternal, self).get_params(*args, **kargs)

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

        if "conflict" in params:
            params.update(conflict=params.get("conflict").lower() == "on")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudSpecialRemittanceInternal, self).complement_model_to_dict(
            instance
        )

        if instance.can_read:
            rst.update(
                conflict=instance.conflict,
                text=instance.text,
                department=nil_pk(instance.department, None),
                department_unicode=nil_unicode(instance.department, None),
            )

        return rst
