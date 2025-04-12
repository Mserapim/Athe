from apiv2.baseserializers import BaseSerializer
from diarias.models import Beneficiario
from rest_framework import serializers


class BeneficiarioTransparenciaSerializer(BaseSerializer):

    nome = serializers.SerializerMethodField()
    cargo = serializers.SerializerMethodField()
    periodo = serializers.SerializerMethodField()
    trecho = serializers.SerializerMethodField()
    transporte = serializers.SerializerMethodField()
    motivo = serializers.SerializerMethodField()
    n_diarias = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiario
        fields = [
            "nome",
            "cargo",
            "periodo",
            "trecho",
            "transporte",
            "motivo",
            "n_diarias",
            "valor_total",
        ]

    def get_nome(self, obj):
        pessoa = obj.servidor.pessoa_fisica
        return pessoa.social_name or pessoa.nome

    def get_cargo(self, obj):
        if obj.cargo:
            return obj.cargo.nome
        servidor = obj.servidor
        return servidor.office or ""

    def get_periodo(self, obj):
        destinos = obj.destinos.all()

        if destinos.count() > 1:
            return f"{destinos.first().data.date()} - {destinos.last().data.date()}"

        return f"{destinos[0].data.date()}"

    def get_trecho(self, obj):
        trechos = ""

        destinos = obj.destinos.all()

        for destino in destinos:
            barra = " | " if trechos != "" else ""
            trechos += f"{barra} {destino.municipio_origem.nome}/{destino.municipio_origem.estado.sigla}  - {destino.municipio_destino.nome}/{destino.municipio_destino.estado.sigla}"

        return trechos

    def get_transporte(self, obj):
        transporte = ""

        destinos = obj.destinos.all()

        for destino in destinos:
            barra = " | " if transporte != "" else ""
            transporte += f"{barra} {destino.get_forma_deslocamento_display()}"

        return transporte

    def get_motivo(self, obj):
        diaria = obj.viagem.get_motivo_viagem_display() or ""
        return diaria

    def get_n_diarias(self, obj):
        calculo = obj.calculos_diarias_consolidados
        return calculo.qtd_total_diarias_deferido

    def get_valor_total(self, obj):
        calculo = obj.calculos_diarias_consolidados
        return calculo.valor_total_liquido_deferido
