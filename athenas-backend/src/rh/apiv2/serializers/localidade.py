from contrib.utils import getLogger
from rest_framework import serializers
from rh.models import Localidade, Estado, Pais

log = getLogger(__name__)


class LotacionogramLocationSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Localidade/Lotacionograma
    """

    comarca = serializers.CharField(source="get_comarca")
    estado_sigla = serializers.CharField(source="get_sigla_estado")

    class Meta:
        model = Localidade
        fields = [
            "id",
            "nome",
            "sigla",
            "comarca",
            "comarca_id",
            "qtd_lotacao",
            "estado_sigla",
        ]


class LocationsSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Localidade
    """

    name = serializers.CharField(source="nome")

    class Meta:
        model = Localidade
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Estado
    """

    name = serializers.CharField(source="nome")

    class Meta:
        model = Estado
        fields = "__all__"


class PaisSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Estado
    """

    class Meta:
        model = Pais
        fields = "__all__"
