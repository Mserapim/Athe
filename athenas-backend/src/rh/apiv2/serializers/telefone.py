from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import SerializerMethodField
from rh.models import Telefone





class TelefoneSerializer(BaseSerializer):
    """
    Serializer para o modelo de Telefone
    """

    orgao_geral_display = SerializerMethodField()
    modified_by_display = SerializerMethodField()
    created_by_display = SerializerMethodField()


    class Meta:
        model = Telefone
        fields = [
            "id",
            "pessoa",
            "tipo_telefone",
            "tipo_telefone_display",
            "numero",
            "publico",
            "principal",
            "orgao_geral",
            "orgao_geral_display",
            "data_alteracao",
            "modified_at",
            "modified_by",
            "modified_by_display",
            "created_at",
            "created_by",
            "created_by_display",
        ]

        extra_kwargs = {
            "id": {"source": "pk"},
            "principal": {"source": "main"},
            "pessoa": {"source": "person"},
            "tipo_telefone_display": {"source": "get_tipo_telefone_display"},
            "pais": {"source": "country"},
            "cidade_exterior": {"source": "outsider_citty"},
            "principal": {"source": "main"},
            "descricao": {"source": "description"},
            "orgao_geral": {"source": "general_organ"},
        }

    
    def get_orgao_geral_display(self, obj):
        if obj.general_organ:
            return obj.general_organ.nome
        return ""

    def get_modified_by_display(self, obj):
        try:
            return obj.modified_by.servidor.pessoa_fisica.social_name
        except:
            return ""
    
    def get_created_by_display(self, obj):
        try:
            return obj.created_by.servidor.pessoa_fisica.social_name
        except:
            return ""