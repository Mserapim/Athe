# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk, nil_new_unicode
from contrib.utils import getLogger
from rh.cif.models import CodeProperty

log = getLogger(__name__)


class CifCodeProperty(Restful):

    _model = CodeProperty

    full_text_index = (
        "code__icontains",
        "title__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.codeproperty.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            code=int(instance.code or 0),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            title=nil_new_unicode(instance.title, ""),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
