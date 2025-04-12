from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field, OpenApiTypes


class AuditoriaLogSerializer(BaseSerializer):

    usuario = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    alteracoes = serializers.SerializerMethodField()
    modelo = serializers.CharField(source="content_type")

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "objeto_id",
            "data",
            "usuario",
            "endereco_ip",
            "modelo",
            "acao",
            "alteracoes",
        ]
        extra_kwargs = {
            "acao": {"source": "action"},
            "objeto_id": {"source": "object_id"},
            "endereco_ip": {"source": "remote_addr"},
        }
        campos_choices = ["acao"]
        campos_relacionados = {"modelo": {"campo_id": "id", "campo_display": "model"}}

    @extend_schema_field({"type": "array", "items": {"type": "object"}})
    def get_alteracoes(self, obj):
        resultado = [
            {campo: {"anterior": valores[0], "novo": valores[1]}}
            for campo, valores in obj.changes_dict.items()
        ]
        return resultado

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_data(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @extend_schema_field(OpenApiTypes.STR)
    def get_usuario(self, obj):
        return obj.actor.username if obj.actor else None


class ModeloLogSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="model")
    value = serializers.IntegerField(source="id")

    class Meta:
        model = ContentType
        fields = ["label", "value"]
