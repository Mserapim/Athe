# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from judicial.models import ArchivementNoticeOffice, OutCourtLawsuit
from judicial.api.partlawsuit import BasePartLawsuit
from rh.models import Lotacao
from contrib.nil import nil_display

log = getLogger(__name__)


class EJudArchivementNoticeOffice(BasePartLawsuit, Restful):

    _model = ArchivementNoticeOffice

    def get_params(self, *args, **kargs):
        params = super(EJudArchivementNoticeOffice, self).get_params(*args, **kargs)

        if "cause" in params:
            if params.get("cause") == "":
                params.pop("cause")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudArchivementNoticeOffice, self).complement_model_to_dict(
            instance
        )

        if instance.can_read:
            rst.update(
                cause=instance.cause,
                cause_display=nil_display(instance, "cause", None),
                content=instance.content,
            )

        return rst

    def finalize_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                cause = self.request.POST.get("cause", 0)
                location = Lotacao.objects.get(
                    pk=self.request.POST.get("location", None)
                )

                for lw in lawsuits:
                    obj = ArchivementNoticeOffice()
                    obj.cause = cause
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
