from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer

from common.services.models import HistoricoServico

from contrib.utils import getLogger

log = getLogger(__name__)


class HistoricoServicosSerializer(BaseSerializer):
    """
    Serializer do model Historico de Servicos
    """

    nome = serializers.SerializerMethodField()
    comando = serializers.SerializerMethodField()
    classcode_path = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()
    login = serializers.SerializerMethodField()
    created_by_unicode = serializers.SerializerMethodField()
    modified_by_unicode = serializers.SerializerMethodField()
    executado_por_unicode = serializers.SerializerMethodField()
    execucao_unicode = serializers.SerializerMethodField()
    possui_mensagens = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoServico
        fields = "__all__"

    def get_nome(self, obj):
        return obj.servico.name if obj.servico else ""

    def get_comando(self, obj):
        return obj.servico.command if obj.servico else ""

    def get_classcode_path(self, obj):
        return (
            obj.servico.classcode.path if obj.servico and obj.servico.classcode else ""
        )

    def get_descricao(self, obj):
        return obj.servico.description if obj.servico else ""

    def get_login(self, obj):
        return obj.created_by.username

    def get_created_by_unicode(self, obj):
        return obj.created_by.username

    def get_modified_by_unicode(self, obj):
        return obj.modified_by.username

    def get_executado_por_unicode(self, obj):
        return obj.created_by.username

    def get_execucao_unicode(self, obj):
        return obj.get_execucao_display()

    def get_possui_mensagens(self, obj):
        return obj.possui_mensagens
