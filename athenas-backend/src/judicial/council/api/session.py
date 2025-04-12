# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import Session
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_date


log = getLogger(__name__)


class CouncilSession(Restful):

    _model = Session

    def json(self, args=[]):
        self.response.write('Ext._create("judicial.council.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "expected_date" in params:
            if params.get("expected_date") != "":
                params.update(
                    expected_date=DateUtils.str_to_date(params.get("expected_date"))
                )
            else:
                params.update(expected_date=None)

        if "file_document" in params:
            if params.get("file_document") != "":
                field = getattr(self.Model, "file_document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        file_document=query.get(pk=params.get("file_document"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(file_document=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            expected_date=nil_date(instance.expected_date, None),
            session_type=instance.session_type,
            session_type_display=nil_display(instance, "session_type", None),
            file_document=nil_pk(instance.file_document, None),
            file_document_unicode=nil_unicode(instance.file_document, None),
            cached_number=instance.cached_number,
            year=int(instance.year or 0),
            number=int(instance.number or 0),
            session_status=instance.session_status,
            session_status_display=nil_display(instance, "session_status", None),
        )

        return rst
