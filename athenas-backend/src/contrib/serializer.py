# -*- coding:utf-8 -*-
from django.core.serializers.json import Serializer as JsonSerializer
from django.core import serializers
from contrib.utils import getLogger

log = getLogger(__name__)


class Serializer(JsonSerializer):

    def get_dump_object(self, obj):
        data = super(Serializer, self).get_dump_object(obj)
        log.debug(
            "SERIALISER END_OBJ: %s >> %s | %s"
            % (hasattr(obj, "natural_key"), obj, data)
        )
        if hasattr(obj, "natural_key"):
            data["pk"] = obj.natural_key()
        return data


serializers.register_serializer("json_nk", "contrib.serializer")
