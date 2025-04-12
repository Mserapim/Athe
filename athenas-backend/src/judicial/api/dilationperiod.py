# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from judicial.models import DilationPeriod, OutCourtLawsuit
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit

from rh.models import Lotacao

log = getLogger(__name__)


class EJudDilationPeriod(BasePartLawsuit, Restful):

    _model = DilationPeriod

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            signed_at=nil_datetime(instance.signed_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            type_part=instance.type_part,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            justification=instance.justification,
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            cache_rendered=instance.cache_rendered,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
        )

        return rst

    def dilation_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                location = Lotacao.objects.get(
                    pk=self.request.POST.get("location", None)
                )

                for lw in lawsuits:
                    obj = DilationPeriod()
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
                success=True, message="Prazos de procedimentos atualizados com sucesso."
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))
