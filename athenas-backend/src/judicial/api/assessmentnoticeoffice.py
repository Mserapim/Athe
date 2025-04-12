# -*- coding: utf-8 -*-
import json

from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import AssessmentNoticeOffice
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_datetime, nil_display
from judicial.api.partlawsuit import BasePartLawsuit
from django.db import transaction


log = getLogger(__name__)


class EJudAssessmentNoticeOffice(BasePartLawsuit, Restful):

    _model = AssessmentNoticeOffice

    def destroy_document(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                doc = self.get_query().get(pk=args[0])
                doc.destroy_document()

            rst.update(message="Documento removido com sucesso.", success=True)
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = super(EJudAssessmentNoticeOffice, self).get_params(*args, **kargs)

        if "is_criminal" in params:
            params.update(is_criminal=params.get("is_criminal", "off").lower() == "on")

        if "is_anonymus" in params:
            params.update(is_anonymus=params.get("is_anonymus", "off").lower() == "on")

        if "only_notice" in params:
            params.update(only_notice=params.get("only_notice", "off").lower() == "on")

        if "interested" in params:
            if params.get("interested") != "":
                field = getattr(self.Model, "interested")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(interested=query.get(pk=params.get("interested")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(interested=None)

        if "at_where" in params:
            if params.get("at_where") != "":
                field = getattr(self.Model, "at_where")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(at_where=query.get(pk=params.get("at_where")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(at_where=None)

        if "location" in params:
            if params.get("location") != "":
                field = getattr(self.Model, "location")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(location=query.get(pk=params.get("location")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(location=None)

        if "main_matter" in params:
            if params.get("main_matter") != "":
                field = getattr(self.Model, "main_matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(main_matter=query.get(pk=params.get("main_matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(main_matter=None)

        if "protocol_origin" in params:
            if params.get("protocol_origin") != "":
                field = getattr(self.Model, "protocol_origin")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        protocol_origin=query.get(pk=params.get("protocol_origin"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(protocol_origin=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudAssessmentNoticeOffice, self).complement_model_to_dict(instance)

        if instance.can_read:
            instance = instance.my_origin
            rst.update(
                notice=instance.notice,
                notice_title=instance.notice_title,
                protocol_origin=nil_pk(instance.protocol_origin, None),
                protocol_origin_unicode=nil_unicode(instance.protocol_origin, None),
                at_where=nil_pk(instance.at_where, None),
                at_where_unicode=nil_unicode(instance.at_where, None),
                main_matter=nil_pk(instance.main_matter, None),
                main_matter_unicode=nil_unicode(instance.main_matter, None),
                is_criminal=instance.is_criminal,
                only_notice=instance.only_notice,
                is_anonymus=instance.is_anonymus,
                interested=nil_pk(instance.interested, None),
                interested_unicode=nil_unicode(instance.interested, None),
                notice_office_type=instance.notice_office_type,
                notice_office_type_display=nil_unicode(instance, "notice_office_type"),
            )

        return rst
