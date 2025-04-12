from rh.afastamento.models import CID
from rh.gfp.models import FolhaTipo
from standard.models import Choice
from contrib.utils import getLogger
from rest_framework import serializers
from rest_framework import status


class PVFListMonthYearSerializer(serializers.Serializer):
    """
    classe serializer da lista de anos folha ponto
    """

    value = serializers.IntegerField()
    label = serializers.CharField()


class PVFConfigValueSerializer(serializers.Serializer):
    """
    classe serializer da lista de anos folha ponto
    """

    id = serializers.IntegerField()
    description = serializers.CharField()


class PVFListaAnoFichaFinaceiraSerializador(serializers.Serializer):
    """
    classe serializer da lista de anos da ficha financeira
    """

    id = serializers.IntegerField()
    description = serializers.CharField()


class PVFTypesPayrollSerializer(serializers.ModelSerializer):
    """
    classe serializer do tipo de folha
    """

    title = serializers.CharField(source="titulo")

    class Meta:
        model = FolhaTipo
        fields = ["pk", "title"]


class PVFListCIDSerializer(serializers.ModelSerializer):
    """
    classe serializer do modelo CID
    """

    code = serializers.CharField(source="codigos_cid")

    class Meta:
        model = CID
        fields = ["pk", "chapter", "code", "description"]
