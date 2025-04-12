from rest_framework import serializers
from standard.models import ConfigPoint
from apiv2.baseserializers import BaseSerializer


class ConfiguracaoDePontoSerializer(BaseSerializer):
    class Meta:
        model = ConfigPoint
        fields = "__all__"
