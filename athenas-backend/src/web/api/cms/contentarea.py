# -*- coding: utf-8 -*-

# from django.db import transaction
from contrib.newrest import RestfulDRY
from web.models import ContentArea
from contrib.utils import getLogger

log = getLogger()


class ContentAreaRestful(RestfulDRY):
    _model = ContentArea
    force_upper = False
    force_orm_single = True
    full_text_index = ["area__fullname__icontains", "content__title__icontains"]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(ContentAreaRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    # def model_to_dict(self, instance):
    #     m2d = super(MetaKeyRestful, self).model_to_dict(instance)
    #     if instance.ged:
    #         m2d['ged_uri'] = instance.ged.permalink()
    #     return m2d

    def get_query(self):
        qs = super(ContentAreaRestful, self).get_query()
        return qs.order_by("area__fullname")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.contentarea.Manager")')
