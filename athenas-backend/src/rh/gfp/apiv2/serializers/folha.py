from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import SerializerMethodField
from rh.gfp.models import Folha


class FolhaSerializer(BaseSerializer):
    """
    Serializer para o modelo de Folha
    """

    periodo_display = SerializerMethodField()
    tipo_folha_display = SerializerMethodField()
    folha_anterior_display = SerializerMethodField()
    fechado_por_display = SerializerMethodField()
    processado_por_display = SerializerMethodField()
    ci_por_display = SerializerMethodField()

    class Meta:
        model = Folha
        fields = [
            "id",
            "periodo",
            "periodo_display",
            "tipo_folha",
            "tipo_folha_display",
            "folha_anterior",
            "folha_anterior_display",
            "fechado",
            "processado",
            "ci",
            "fechado_por",
            "fechado_por_display",
            "processado_por",
            "processado_por_display",
            "ci_por",
            "ci_por_display",
            "dt_fechamento",
            "dt_processado",
            "dt_ci",
            "dt_pagamento",
            "dt_corte",
            "status",
            "dt_criacao",
            "unicode_cache",
            "complemento",
            "bloqueia_contra_cheque",
            "aplica_modelos",
            "disponivel_vdf",
            "created_at",
            "modified_at",
        ]

        extra_kwargs = {
            "id": {"source": "pk"},
            "complemento": {"source": "complement"},
            "bloqueia_contra_cheque": {"source": "paycheck_locked"},
            "aplica_modelos": {"source": "apply_models"},
            "disponivel_vdf": {"source": "available_pvf"},
        }


    def get_periodo_display(self, obj):
        if obj.periodo:
            return obj.periodo.__str__()
        return ""
    
    def get_tipo_folha_display(self, obj):
        if obj.tipo_folha:
            return obj.tipo_folha.__str__()
        return ""

    def get_folha_anterior_display(self, obj):
        if obj.folha_anterior:
            return obj.folha_anterior.__str__()
        return ""
    
    def get_fechado_por_display(self, obj):
        if obj.fechado_por:
            return obj.fechado_por.__str__()
        return ""

    def get_processado_por_display(self, obj):
        if obj.processado_por:
            return obj.processado_por.__str__()
        return ""
    
    def get_ci_por_display(self, obj):
        if obj.ci_por:
            return obj.ci_por.__str__()
        return ""