from contrib.utils import getLogger
from rest_framework import serializers
from apiv2.baseserializers import BaseSerializer
from rh.antiguidades.models import ListaAntiguidadeMembros

log = getLogger(__name__)


class AntiguidadesSerializer(BaseSerializer):
    """
    Serializer para o modelo de ListaAntiguidadesMembros
    """

    class Meta:
        model = ListaAntiguidadeMembros
        fields = [
            "pk",
            "matricula",
            "servidor",
            "nome",
            "nome_social",
            "cpf",
            "ordem_antiguidade",
            "data_inicio_instancia",
            "data_inicio_carreira",
            "tempo_afastamento_formatado",
            "total_instancia_formatado",
            "efetivo_exercicio_formatado",
            "total_carreira_formatado",
            "get_origem_display",
            "get_tipo_cargo_display",
            "posicao_concurso",
            "modified_at",
        ]

    ORDER_BY_MAP = {
        "matricula": "servidor__matricula",
        "cpf": "servidor__pessoa_fisia__cpf",
        "social_name": "servidor__pessoa_fisia__social_name",
        "nome": "servidor__pessoa_fisia__nome",
        "posicao_concurso": "servidor__posicao_concurso",
        "tempo_afastamento_formatado": "tempo_afastamento",
        "total_instancia_formatado": "data_inicio_instancia",
        "efetivo_exercicio_formatado": "data_inicio_carreira",
        "total_carreira_formatado": "data_inicio_carreira",
        "get_tipo_cargo_display": "tipo_cargo",
    }
