# -*- coding: utf-8 -*-
import json

from contrib.newrest import Restful
from contrib.utils import getLogger
from contrib.nil import nil_pk, nil_unicode, nil_datetime, nil_display

from judicial.models import Recomendation
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudRecomendation(BasePartLawsuit, Restful):

    _model = Recomendation

    def complement_model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        if instance.can_read:
            rst.update(
                content=instance.content,
                deadline_type=instance.deadline_type,
                deadline_type_display=nil_display(instance, "deadline_type", None),
                deadline=instance.deadline,
                deadline_display="{} {}".format(
                    instance.deadline, nil_display(instance, "deadline_type", None)
                ),
                finished_by=nil_pk(instance.finished_by, None),
                finished_by_unicode=nil_unicode(instance.finished_by, None),
                finished_at=nil_datetime(instance.finished_at, None),
                remaining_days=(
                    instance.remaining_days if instance.remaining_days else "--"
                ),
                lawsuit_number=instance.lawsuit.cache_number,
                out_court_lawsuit_pk=instance.lawsuit.pk,
                dispatch_title=instance.dispatch_title,
            )

        return rst

    def fulfilled(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            pk = args[0] if args else 0
            obj = self.Model.objects.get(pk=pk)
            obj.fulfilled()
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Finalização realizada com sucesso.")

        self.renderer(rst)

    def render(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        oid = args[0] if args else 0

        try:
            recomendation = self.Model.objects.get(pk=oid)
            rst.update(
                success=True,
                message="Dados processados com sucesso",
                rendered=recomendation.rendered,
                extra_pages=recomendation.extra_pages,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
