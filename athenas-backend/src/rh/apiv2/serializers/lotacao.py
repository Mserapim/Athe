from contrib.utils import getLogger
from rest_framework import serializers
from rh.models import Comarca, Lotacao, ServidorLotacao
from rest_framework.serializers import ModelSerializer
from rh.models import Lotacao
from rest_framework import serializers

log = getLogger(__name__)


class ComarcaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Comarca
    """

    lotacao = serializers.SerializerMethodField()

    class Meta:
        model = Comarca
        fields = ["id", "nome", "lotacao"]

    def get_lotacao(self, obj):
        return [LotacaoSerializer(lotacao).data for lotacao in obj.lotacao_set.all()]


class LotacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Lotaçâo
    """

    class Meta:
        model = Lotacao
        fields = ["id", "nome"]


class WorkplaceSerializer(ModelSerializer):
    """
    Serializer do model Lotação
    """

    name = serializers.CharField(source="nome")
    responsible = serializers.CharField(source="responsible_name")

    class Meta:
        model = Lotacao
        fields = ["pk", "name", "responsible"]


class ServidorLotacaoZonaEleitoralSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de Lotaçâo
    """

    lotacao = serializers.SerializerMethodField()
    data_inicio = serializers.DateField(source="data_vigencia_inicio")
    data_fim = serializers.DateField(source="data_vigencia_fim")

    class Meta:
        model = ServidorLotacao
        fields = ["lotacao", "data_inicio", "data_fim"]

    def get_lotacao(self, instance):
        if instance.lotacao:
            return instance.lotacao.nome
        return None
