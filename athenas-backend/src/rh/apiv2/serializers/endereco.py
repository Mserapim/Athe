from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import SerializerMethodField
from rh.models import Endereco


class EnderecoSerializer(BaseSerializer):
    """
    Serializer para o modelo de Endereco
    """

    municipio_display = SerializerMethodField()
    pais_display = SerializerMethodField()
    orgao_display = SerializerMethodField()
    modified_by_display = SerializerMethodField()
    created_by_display = SerializerMethodField()

    class Meta:
        model = Endereco
        fields = [
            "id",
            "tipo_endereco",
            "tipo_endereco_display",
            "tipo_logradouro",
            "tipo_logradouro_display",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cep",
            "municipio",
            "municipio_display",
            "data_alteracao",
            "pessoa",
            "orgao",
            "orgao_display",
            "pais",
            "pais_display",
            "exterior",
            "cidade_exterior",
            "unicode",
            "modified_at",
            "modified_by",
            "modified_by_display",
            "created_at",
            "created_by",
            "created_by_display",
        ]

        extra_kwargs = {
            "id": {"source": "pk"},
            "exterior": {"source": "outsider"},
            "tipo_endereco_display": {"source": "get_tipo_endereco_display"},
            "tipo_logradouro_display": {"source": "get_tipo_logradouro_display"},
            "pessoa": {"source": "person"},
            "orgao": {"source": "general_organ"},
            "pais": {"source": "country"},
            "cidade_exterior": {"source": "outsider_citty"},
        }

    def get_municipio_display(self, obj):
        return obj.municipio.nome

    def get_pais_display(self, obj):
        if obj.country:
            return obj.country.nome
        return ""
    
    def get_orgao_display(self, obj):
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