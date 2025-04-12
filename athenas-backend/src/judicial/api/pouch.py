# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from judicial.models import Pouch, OutCourtLawsuit
from contrib.utils import getLogger, DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_datetime
from django.db import transaction


log = getLogger(__name__)


class EJudPouch(Restful):

    _model = Pouch

    force_upper = False

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.pouch.Manage")')

    def sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        try:
            obj = self.Model.objects.get(pk=args[0])
            with transaction.atomic():
                obj.sign()

            rst.update(success=True, message="itens adicionado com sucesso.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def add_items(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        try:
            obj = self.Model.objects.get(pk=args[0])
            with transaction.atomic():
                obj.add_items(
                    OutCourtLawsuit.objects.filter(
                        pk__in=self.request.POST.getlist("items")
                    )
                )

            rst.update(success=True, message="itens adicionado com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def remove_items(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        try:
            obj = self.Model.objects.get(pk=args[0])
            with transaction.atomic():
                self._read_special_verb()
                obj.remove_items(
                    OutCourtLawsuit.objects.filter(
                        pk__in=self.get_params().get("items")
                    )
                )

            rst.update(success=True, message="itens removidos com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("to_location", "from_location"):
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
            to_location=nil_pk(instance.to_location, None),
            to_location_unicode=nil_unicode(instance.to_location, None),
            signed_at=nil_datetime(instance.signed_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            from_location=nil_pk(instance.from_location, None),
            from_location_unicode=nil_unicode(instance.from_location, None),
            created_at=nil_datetime(instance.created_at, None),
            pouch_number=instance.pouch_number,
            pouch_year=instance.pouch_year,
            cache_number=instance.cache_number,
            content=instance.content,
            items_done=instance.items.exclude(movement_part=None).count(),
            items_count=instance.items.count(),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
