from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers

from diarias.models import CargoDiarias, LimiteDiarias, ValorDiarias
from standard.models import Choice


class CargoDiariasSerializer(BaseSerializer):
    """
    Serializer do model CargoDiarias
    """

    class Meta:
        model = CargoDiarias
        fields = "__all__"


class ValorDiariasSerializer(BaseSerializer):
    """
    Serializer do model ValorDiarias
    """

    class Meta:
        model = ValorDiarias
        fields = "__all__"


class LimiteDiariasSerializer(BaseSerializer):
    """
    Serializer do model LimiteDiarias
    """

    tipo_display = serializers.SerializerMethodField()
    referencia_display = serializers.SerializerMethodField()
    motivos_viagem_display = serializers.SerializerMethodField()
    criado_por_username = serializers.SerializerMethodField()
    modificado_por_username = serializers.SerializerMethodField()

    class Meta:
        model = LimiteDiarias
        fields = "__all__"

    def get_tipo_display(self, obj):
        return obj.get_tipo_display() or ""

    def get_referencia_display(self, obj):
        return obj.get_referencia_display() or ""

    def get_motivos_viagem_display(self, obj):
        if not obj.motivos_viagem:
            return ""
        choices = Choice.objects.filter(
            app_label="diarias", name="MOTIVO_VIAGEM", value__in=obj.motivos_viagem
        ).order_by("value")

        labels = [choice.label for choice in choices]
        return ", ".join(labels)

    def get_criado_por_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_modificado_por_username(self, obj):
        return obj.modified_by.username if obj.modified_by else None
