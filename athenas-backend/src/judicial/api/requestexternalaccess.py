# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import RequestExternalAccess
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudRequestExternalAccess(Restful):

    full_text_index = (
        "person__nome__icontains",
        "as_representative_of__nome__icontains",
        "lawsuit__cache_number__icontains",
    )

    _model = RequestExternalAccess

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("as_representative_of", "person", "lawsuit"):
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
            as_representative_of=nil_pk(instance.as_representative_of, None),
            as_representative_of_unicode=nil_unicode(
                instance.as_representative_of, None
            ),
            revoked_at=nil_datetime(instance.revoked_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            revoked_by=nil_pk(instance.revoked_by, None),
            revoked_by_unicode=nil_unicode(instance.revoked_by, None),
            request=instance.request,
            rendered_request=instance.renderer_request,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            authorized_at=nil_datetime(instance.authorized_at, None),
            person=nil_pk(instance.person, None),
            person_unicode=nil_unicode(instance.person, None),
            authorized_by=nil_pk(instance.authorized_by, None),
            authorized_by_unicode=nil_unicode(instance.authorized_by, None),
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            lawsuit_title=instance.lawsuit.title,
            lawsuit_cache_number=instance.lawsuit.cache_number,
            denied_by=nil_pk(instance.denied_by, None),
            denied_by_unicode=nil_unicode(instance.denied_by, None),
            denied_at=nil_datetime(instance.denied_at, None),
            pending=instance.pending,
        )

        return rst

    def authorize(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            request = self.Model.objects.get(pk=self.request.POST.get("pk"))
            request.authorize()

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Realizado com sucesso.")

        self.renderer(rst)

    def deny(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            request = self.Model.objects.get(pk=self.request.POST.get("pk"))
            justification = self.request.POST.get("justification", "")

            if request.authorized_by:
                request.revoke(justification=justification)
            else:
                request.deny(justification=justification)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Realizado com sucesso.")

        self.renderer(rst)
