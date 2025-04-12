from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers

from contrib.utils import getLogger
from diarias.models import CondicionalFluxoViagem, FluxoViagem
from diarias.utils.utils import buscar_descricao_condicional

log = getLogger()


class CondicionalFluxoViagemSerializer(serializers.ModelSerializer):
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = CondicionalFluxoViagem
        fields = "__all__"

    def get_descricao(self, obj):
        descricao = ""
        if obj.condicionais and obj.condicionais != "":
            if (
                ";" not in obj.condicionais
                and "," not in obj.condicionais
                and not obj.tipo_operador
            ):
                descricao += buscar_descricao_condicional(obj.condicionais)
            else:
                descricao += (
                    "(" if obj.tipo_operador is None else f" {obj.tipo_operador} ("
                )

                if ";" in obj.condicionais:
                    for x, item_cond in enumerate(obj.condicionais.split(";")):
                        if x != 0:
                            descricao += f" E "
                        descricao += buscar_descricao_condicional(item_cond)
                elif "," in obj.condicionais:
                    for x, item_cond in enumerate(obj.condicionais.split(",")):
                        if x != 0:
                            descricao += f" OU "
                        descricao += buscar_descricao_condicional(item_cond)

                else:
                    descricao += buscar_descricao_condicional(obj.condicionais)

                descricao += ")"

        return descricao


class CondicionalFluxoViagemSerializerII(serializers.Serializer):
    tipo_operador = serializers.CharField(required=False, allow_null=True)
    ids_condicionais = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        fields = ["tipo_operador", "ids_condicionais"]


class FluxoViagemLeituraSerializer(BaseSerializer):
    """
    Serializer do model FluxoViagem
    """

    situacao_display = serializers.SerializerMethodField()
    etapa_display = serializers.SerializerMethodField()
    fluxo_display = serializers.SerializerMethodField()
    condicionais = CondicionalFluxoViagemSerializer(many=True)
    condicionais_descricao = serializers.SerializerMethodField()
    criado_por_username = serializers.SerializerMethodField()
    modificado_por_username = serializers.SerializerMethodField()

    class Meta:
        model = FluxoViagem
        fields = "__all__"

    def get_situacao_display(self, obj):
        return obj.get_situacao_display() or ""

    def get_etapa_display(self, obj):
        return obj.get_etapa_display() or ""

    def get_fluxo_display(self, obj):
        return str(obj)

    def get_condicionais(self, obj):
        condicionais = obj.condicionais.all()
        return [
            {"id": condicional.id, "condicionais": condicional.condicionais}
            for condicional in condicionais
        ]

    def get_criado_por_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_modificado_por_username(self, obj):
        return obj.modified_by.username if obj.modified_by else None

    def get_condicionais_descricao(self, obj):
        descricoes = ""
        for condicional in obj.condicionais.all():
            serializer = CondicionalFluxoViagemSerializer(condicional)
            descricoes += serializer.data["descricao"]

        return descricoes


class FluxoViagemSerializer(BaseSerializer):
    """
    Serializer do model FluxoViagem
    """

    condicionais = CondicionalFluxoViagemSerializerII(many=True, required=False)

    class Meta:
        model = FluxoViagem
        fields = "__all__"

    def to_representation(self, instance):
        return FluxoViagemLeituraSerializer(
            instance=instance, context=self.context
        ).data

    def create(self, validated_data):
        condicionais_data = validated_data.pop("condicionais", [])
        fluxo_viagem = FluxoViagem.objects.create(**validated_data)
        if condicionais_data:
            self.criar_condicionais(fluxo_viagem, condicionais_data)
        return fluxo_viagem

    def update(self, instance, validated_data):
        condicionais_data = validated_data.pop("condicionais", [])
        notificar_emails = validated_data.pop("notificar_emails", None)
        if notificar_emails is not None:
            instance.notificar_emails = notificar_emails
            instance.save(update_fields=["notificar_emails"])
        instance = super().update(instance, validated_data)
        instance.condicionais.all().delete()
        if condicionais_data:
            self.criar_condicionais(instance, condicionais_data)
        return instance

    def criar_condicionais(self, fluxo, condicionais_data):
        for condicional in condicionais_data:
            tipo_operador = condicional.get("tipo_operador", None)
            ids_condicionais = condicional.get("ids_condicionais")

            CondicionalFluxoViagem.objects.create(
                fluxo=fluxo, tipo_operador=tipo_operador, condicionais=ids_condicionais
            )
