# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from judicial.models import RemittanceExternal, OutCourtLawsuit
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit

from rh.models import Lotacao, OrgaoGeral


log = getLogger(__name__)


class EJudRemittanceExternal(BasePartLawsuit, Restful):

    _model = RemittanceExternal

    def get_params(self, *args, **kargs):
        params = super(EJudRemittanceExternal, self).get_params(*args, **kargs)

        if "organ" in params:
            if params.get("organ") != "":
                field = getattr(self.Model, "organ")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(organ=query.get(pk=params.get("organ")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(organ=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudRemittanceExternal, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(text=instance.text)

        return rst

    def remittance_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                log.debug(self.request.POST)
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                location = Lotacao.objects.get(
                    pk=self.request.POST.get("location", None)
                )
                organ = OrgaoGeral.objects.get(pk=self.request.POST.get("organ", None))

                for lw in lawsuits:
                    obj = RemittanceExternal()
                    obj.lawsuit = lw
                    obj.location = location

                    obj.save()

                    obj.organs.add(organ)

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
