from rh.pvf.models import PortalRequestHistory
from rest_framework.serializers import ModelSerializer


class PVFObservationRetificationSerializer(ModelSerializer):
    """
    classe serializer para editar o campo 'observation' no histórico
    """

    class Meta:
        model = PortalRequestHistory
        fields = ["observation"]

    def update(self, instance, validated_data):
        instance.observation = validated_data.get("observation", instance.observation)
        instance.save()
        return instance
