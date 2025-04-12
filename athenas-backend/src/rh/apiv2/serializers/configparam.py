from rest_framework.serializers import ModelSerializer
from standard.models import Choice


class ConfigParamSerializer(ModelSerializer):
    """
    Serializer da configuração de parâmetros
    """

    class Meta:
        model = Choice
        fields = ["label", "value"]
