from contrib.utils import getLogger
from rest_framework import serializers
from rh.models import Comarca, Localidade

log = getLogger(__name__)


class ComarcaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Comarca
    """

    class Meta:
        model = Comarca
        fields = ["id", "nome"]
