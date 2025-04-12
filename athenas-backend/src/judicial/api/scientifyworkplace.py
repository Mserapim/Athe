# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import ScientifyWorkplace, PartLawsuit
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_datetime
from django.db import transaction

from rh.models import Lotacao


log = getLogger(__name__)


class EJudScientifyWorkplace(Restful):

    _model = ScientifyWorkplace

    force_orm_single = True

    force_upper = False

    def dispatch(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                for science in self.Model.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    science.dispatch()
                rst.update(success=True, message="Comunicações enviadas com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("part", "location"):
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

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            content=instance.content,
            part=nil_pk(instance.part, None),
            part_unicode=nil_unicode(instance.part, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            received_by=nil_pk(instance.received_by, None),
            received_by_unicode=nil_unicode(instance.received_by, None),
            received_at=nil_datetime(instance.received_at, None),
            location=nil_pk(instance.location, None),
            location_unicode=nil_unicode(instance.location, None),
            protocol=nil_pk(instance.protocol, None),
            protocol_unicode=nil_unicode(instance.protocol, None),
            protocol_code=None if not instance.protocol else instance.protocol.codigo,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            movement=nil_pk(instance.movement, None),
            movement_unicode=nil_unicode(instance.movement, None),
        )

        return rst

    def save_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                location = Lotacao.objects.get(
                    pk=self.request.POST.get("location", None)
                )
                content = self.request.POST.get("content", None)
                parts = PartLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("parts")
                )

                for part in parts:
                    obj = ScientifyWorkplace()
                    obj.part = part
                    obj.location = location
                    obj.content = content

                    obj.save()

        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(
                success=True, message="Comunicações salvas nos procedimentos."
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))
