# -*- coding: utf-8 -*-
# from django.db.models import Q
from contrib.newrest import RestfulDRY

# from contrib.middleware import get_current_user
from contrib.utils import getLogger  # , employee_from_user

from .models import Channel


log = getLogger(__name__)


class ProtocolChannelsRestful(RestfulDRY):

    _model = Channel
    force_orm_single = True
    force_upper = False
    full_text_index = ("name__icontains",)

    # force_persist_boolean_fields = ['']

    # def get_query(self):
    #     pass

    # def model_to_dict(self, instance):
    #     m2d = RestfulDRY.model_to_dict(self, instance)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.protocolo.channels.ChannelsManage")')
