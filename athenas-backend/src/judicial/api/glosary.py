# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Glosary
from django.contrib.contenttypes.models import ContentType
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.middleware import get_current_user


log = getLogger(__name__)


class EJudGlosary(Restful):

    _model = Glosary

    full_text_index = ("title__icontains",)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.params.GlosaryManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "active" in params:
            params.update(active=params.get("active").lower() == "on")

        if "classification_type" in params and params.get("classification_type") == "":
            params.update(classification_type=None)

        if "legal_classification" in params:
            if params.get("legal_classification") != "":
                field = getattr(self.Model, "legal_classification")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        legal_classification=query.get(
                            pk=params.get("legal_classification")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(legal_classification=None)

        return params

    def get_query(self):
        query = super(EJudGlosary, self).get_query()

        user = get_current_user()
        if not user.has_perm("judicial.can_admin_glosary"):
            query = query.filter(allowed_for__users=user)

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            classification_type=instance.classification_type,
            classification_type_display=nil_display(
                instance, "classification_type", None
            ),
            legal_classification=nil_pk(instance.legal_classification, None),
            legal_classification_unicode=nil_unicode(
                instance.legal_classification, None
            ),
            icon_class=instance.icon_class,
            model_name=instance.model_name,
            app_label=instance.app_label,
            meaning_type=instance.meaning_type,
            meaning_type_display=nil_display(instance, "meaning_type", None),
            title=instance.title,
            active=instance.active,
        )

        return rst


class EJudGlosaryFilter(EJudGlosary):

    def get_query(self):
        return self.Model.objects.filter(templates__active=True)
