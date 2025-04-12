from apiv2.baseserializers import BaseSerializer
from diarias.models import Pagamento
from rest_framework import serializers


class PagamentoSerializer(BaseSerializer):
    """
    Serializer do model Pagamento
    """

    data_inicio_viagem = serializers.SerializerMethodField()
    data_pgto = serializers.SerializerMethodField()
    servidor = serializers.SerializerMethodField()
    servidor_id = serializers.SerializerMethodField()
    valor_liquido_viagem = serializers.SerializerMethodField()
    valor_liquido_deferido_viagem = serializers.SerializerMethodField()
    info_conta_bancaria = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    criado_por = serializers.SerializerMethodField()
    modificado_por = serializers.SerializerMethodField()

    class Meta:
        model = Pagamento
        fields = "__all__"

    def get_data_inicio_viagem(self, obj):
        return obj.beneficiario.viagem.data_inicio_viagem.strftime("%d/%m/%Y")

    def get_data_pgto(self, obj):
        return obj.data_pgto.strftime("%d/%m/%Y") if obj.data_pgto else ""

    def get_servidor(self, obj):
        return obj.servidor

    def get_servidor_id(self, obj):
        return obj.beneficiario.servidor.id

    def get_valor_liquido_viagem(self, obj):
        return obj.valor_liquido_viagem

    def get_valor_liquido_deferido_viagem(self, obj):
        return obj.valor_liquido_deferido_viagem

    def get_info_conta_bancaria(self, obj):
        return obj.info_conta_bancaria

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_criado_por(self, obj):
        return obj.criado_por

    def get_modificado_por(self, obj):
        return obj.modificado_por
