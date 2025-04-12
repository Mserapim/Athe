from apiv2.baseserializers import BaseSerializer
from diarias.models import EventoBeneficiario, Destino


from rest_framework import serializers

from contrib.utils import getLogger


log = getLogger(__name__)


class EventoSerializer(BaseSerializer):

    destinos = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.all(), many=True, required=False, allow_empty=True
    )
    unicode = serializers.SerializerMethodField()

    class Meta:
        model = EventoBeneficiario
        fields = "__all__"
        extra_kwargs = {"destinos": {"required": False}}

    def get_unicode(self, obj):
        dt_inicio = obj.data_inicio.strftime("%d/%m/%Y")
        dt_fim = f" até {obj.data_fim.strftime('%d/%m/%Y')}" if obj.data_fim else ""
        txt_data = f"de {dt_inicio}{dt_fim}" if dt_fim else f"data: {dt_inicio}"

        return f"{obj.titulo} - {txt_data}"
