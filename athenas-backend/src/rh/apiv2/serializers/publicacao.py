from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import ModelSerializer
from rh.models import Publicacao
from rest_framework import serializers

from rh.models import Publicacao
from standard.models import Choice


class PublicacaoSerializer(BaseSerializer):
    unicode = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    veiculo_publicacao_display = serializers.SerializerMethodField()

    class Meta:
        model = Publicacao
        fields = "__all__"

    def get_unicode(self, obj):
        return obj.__str__()

    def get_tipo_display(self, obj):
        return obj.get_tipo_display()

    def get_veiculo_publicacao_display(self, obj):
        return obj.get_veiculo_publicacao_display()


class VeiculoPublicacaoSerializer(BaseSerializer):
    class Meta:
        model = Choice
        fields = ["label", "value"]


class PublicationSerializer(ModelSerializer):
    """
    Serializer do model de Publicacao
    """

    description = serializers.CharField(source="cache_unicode")

    class Meta:
        model = Publicacao
        fields = ["pk", "description"]
