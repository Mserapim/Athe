from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
from esocial.models import ItemTable
from standard.models import Choice

from contrib.utils import getLogger

log = getLogger(__name__)


class OpcoesSerializer(serializers.ModelSerializer):

    titulo = serializers.CharField(source="label")
    valor = serializers.CharField(source="value")

    class Meta:
        model = Choice
        fields = ["id", "titulo", "valor"]


class ItemTabelaSerializer(BaseSerializer):
    """
    classe serializer View dos itens de tabelas do esocial
    """

    ORDER_BY_MAP = {
        "titulo": "title",
        "codigo": "code",
        "tabela_esocial": "esocial_table",
        "inicio_vigencia": "start_validity",
        "fim_vigencia": "end_validity",
    }

    titulo = serializers.CharField(source="title")
    codigo = serializers.CharField(source="code")
    descricao = serializers.CharField(
        source="description", required=False, allow_blank=True
    )
    tabela_esocial = serializers.CharField(source="esocial_table")
    inicio_vigencia = serializers.DateField(
        source="start_validity", required=False, allow_null=True
    )
    fim_vigencia = serializers.DateField(
        source="end_validity", required=False, allow_null=True
    )
    criado_em = serializers.DateTimeField(source="created_at", required=False)
    modificado_em = serializers.DateTimeField(source="modified_at", required=False)
    criado_por = serializers.SerializerMethodField(required=False)
    modificado_por = serializers.SerializerMethodField(required=False)
    choice_filtro = serializers.SerializerMethodField(required=False)
    opcoes = serializers.PrimaryKeyRelatedField(
        source="choice", queryset=Choice.objects.all(), many=True, write_only=True
    )
    opcoes_detalhes = OpcoesSerializer(
        source="choice", many=True, required=False, read_only=True
    )

    class Meta:
        model = ItemTable
        fields = [
            "id",
            "titulo",
            "codigo",
            "info",
            "descricao",
            "tabela_esocial",
            "inicio_vigencia",
            "fim_vigencia",
            "criado_em",
            "modificado_em",
            "criado_por",
            "modificado_por",
            "choice_filtro",
            "opcoes",
            "opcoes_detalhes",
        ]

    def get_criado_por(self, obj):
        return obj.created_by.username

    def get_modificado_por(self, obj):
        return obj.modified_by.username

    def get_choice_filtro(self, obj):
        choice_filtro = Choice.get_dict_choices_for("esocial", "CHOICE_ITEM_MAP").get(
            int(obj.esocial_table), ""
        )
        return choice_filtro
