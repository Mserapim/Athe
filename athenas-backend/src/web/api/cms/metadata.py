# -*- coding: utf-8 -*-

# from django.db import transaction
from contrib.newrest import RestfulDRY
from web.models import MetaKey, MetaValue
from contrib.utils import getLogger

log = getLogger()


class MetaKeyRestful(RestfulDRY):
    _model = MetaKey
    force_upper = False
    force_orm_single = True
    full_text_index = ["name__icontains", "key__icontains"]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(MetaKeyRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.metadata.MetaKeyManager")')


class MetaValueRestful(RestfulDRY):
    _model = MetaValue
    force_upper = False
    force_orm_single = True
    full_text_index = [
        "value__icontains",
        "key__title__icontains",
        "key__name__icontains",
    ]
    # exclude_fields = ['created_by', 'modified_by', 'modified_at']

    def __init__(self, *args, **kwargs):
        super(MetaValueRestful, self).__init__(*args, **kwargs)
        self.set_restful("json")

    # def model_to_dict(self, instance):
    #     m2d = super(MetaValueRestful, self).model_to_dict(instance)
    #     if instance.ged:
    #         m2d['ged_uri'] = instance.ged.permalink()
    #     return m2d

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.cms.metadata.MetaValueManager")')
