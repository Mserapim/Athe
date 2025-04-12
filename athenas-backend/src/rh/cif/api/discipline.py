# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk, nil_new_unicode
from contrib.utils import getLogger
from rh.cif.models import Discipline

log = getLogger(__name__)


class CifDiscipline(Restful):

    _model = Discipline

    full_text_index = ("name__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.discipline.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_at=nil_datetime(instance.modified_at, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            name=nil_new_unicode(instance.name, ""),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
