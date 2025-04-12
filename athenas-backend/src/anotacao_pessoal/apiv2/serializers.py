from rest_framework.serializers import ModelSerializer
from rest_framework import status, serializers

from anotacao_pessoal.models import AnotacaoPessoal
from standard.models import Choice
from rh.models import Publicacao
from rh.pvf.const import MSG_SUCCESS_METHOD

from contrib.utils import getLogger

from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers


log = getLogger(__name__)


class AnotacaoPessoalSerializer(ModelSerializer):
    """
    Serializer do model AnotacaoPessoal
    """

    class Meta:
        model = AnotacaoPessoal
        fields = [
            "pk",
            "texto",
            "tipo_label",
            "documento_tipo_label",
            "publicacao_label",
            "data_publicacao",
            "documento_numero",
            "documento_ano",
            "documento_data",
            "data_efeito_inicio",
            "data_efeito_fim",
            "gedoc_numero",
        ]
        """
        fields = '__all__'"""


class TiposAnotacaoSerializer(ModelSerializer):
    """
    classe serializer para retornar os tipos de anotação
    """

    class Meta:
        model = Choice
        fields = ["value", "label"]


class TiposDocumentoSerializer(ModelSerializer):
    """
    classe serializer para retornar os tipos de documentos
    """

    class Meta:
        model = Choice
        fields = ["value", "label"]


class AnotacaoPessoalCompletoSerializer(BaseSerializer):
    """
    Serializer do model AnotacaoPessoal
    """

    documento_tipo_display = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    publicacao_display = serializers.SerializerMethodField()
    data_publicacao = serializers.SerializerMethodField()
    data_expedicao_publicacao = serializers.SerializerMethodField()
    servidor_nome = serializers.SerializerMethodField()
    servidor_matricula = serializers.SerializerMethodField()

    class Meta:
        model = AnotacaoPessoal
        fields = "__all__"

    def get_documento_tipo_display(self, obj):
        return obj.documento_tipo_label

    def get_tipo_display(self, obj):
        return obj.tipo_label

    def get_data_publicacao(self, obj):
        return obj.data_publicacao

    def get_data_expedicao_publicacao(self, obj):
        return obj.data_expedicao_publicacao

    def get_servidor_nome(self, obj):
        return obj.servidor.pessoa_fisica.social_name

    def get_servidor_matricula(self, obj):
        return obj.servidor.matricula

    def get_publicacao_display(self, obj):
        return obj.publicacao.__str__() or ""
