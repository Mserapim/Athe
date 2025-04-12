# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger, person_from_user
from judicial.models import PartLawsuitAccess
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudPartLawsuitAccess(Restful):

    _model = PartLawsuitAccess

    force_upper = False

    def sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            self.get_query().get(pk=args[0]).sign()
            rst.update(success=True, message="tudo ok!")
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado.")

        self.renderer(rst)

    def suspend(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            self.get_query().get(pk=args[0]).suspend()
            rst.update(success=True, message="tudo ok!")
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for related in ("part", "lawsuit"):
            if related in params:
                if params.get(related) != "":
                    field = getattr(self.Model, related)

                    # mater compatibilidade com django-1.4.x
                    get_queryset = field.get_queryset
                    query = get_queryset()

                    try:
                        params.update({related: query.get(pk=params.get(related))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({related: None})

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            unicode=instance.title,
            motivation=instance.motivation,
            motivation_display=nil_display(instance, "motivation", None),
            part=nil_pk(instance.part, None),
            part_unicode=nil_unicode(instance.part, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            modified_by_person=str(person_from_user(instance.modified_by)),
            justification=instance.justification,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            created_by_person=str(person_from_user(instance.created_by, False)),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            signed_by_person=str(person_from_user(instance.signed_by, False)),
            suspended_by=nil_pk(instance.suspended_by, None),
            suspended_by_unicode=nil_unicode(instance.suspended_by, None),
            suspended_by_person=str(person_from_user(instance.suspended_by, False)),
        )

        return rst
