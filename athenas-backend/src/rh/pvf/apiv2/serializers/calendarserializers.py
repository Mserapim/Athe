from rest_framework import serializers
from contrib.utils import getLogger
from rest_framework.serializers import ModelSerializer
from rh.models import Servidor
from standard.models import Choice


log = getLogger(__name__)


class PVFCalendarSerializer(serializers.Serializer):
    """
    classe serializer dos eventos(calendário) VDF
    """

    pk = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.DateField()
    end = serializers.DateField()
    event_type = serializers.IntegerField()
    group_id = serializers.IntegerField()
    group_name = serializers.CharField()


class PVFEmployeeTeamSerializer(ModelSerializer):
    """
    classe serializer do time do calendário
    """

    servidor_id = serializers.CharField(source="pk")

    class Meta:
        model = Servidor
        fields = ["servidor_id", "name"]


class PVFEventTypeSerializer(ModelSerializer):
    """
    classe serializer dos tipos de eventos
    """

    class Meta:
        model = Choice
        fields = ["label", "value"]
