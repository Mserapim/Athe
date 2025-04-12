from contrib.utils import getLogger
from rest_framework import serializers

log = getLogger(__name__)


class LotacionogramSerializer(serializers.Serializer):
    """
    Serializer do lotacionograma
    """

    localidade = serializers.CharField()
    localidade_id = serializers.IntegerField()
    comarca = serializers.CharField()
    comarca_id = serializers.IntegerField()
    nucleo = serializers.CharField()
    nucleo_id = serializers.IntegerField()
    endereco = serializers.CharField()
    phones = serializers.ListField()
    lotacao = serializers.CharField()
    responsavel = serializers.CharField()
    dados = serializers.ListField()
