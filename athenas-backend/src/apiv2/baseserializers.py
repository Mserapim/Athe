from rest_framework import status
from rest_framework import serializers
from apiv2.const import MSG_SUCCESS_METHOD

from contrib.utils import getLogger


log = getLogger(__name__)


class BaseSerializer(serializers.ModelSerializer):

    def get_nome_display(self, valor, campo_display):
        return getattr(valor, campo_display, None)

    def serialize_campos_relacionados(self, instance, response):
        """Substitui campos de relacionamento (ForeignKey e ManyToManyField) pelo formato desejado."""
        campos_relacionados = getattr(self.Meta, "campos_relacionados", {})

        for nome_campo, config in campos_relacionados.items():
            campo = self.fields[nome_campo]

            nome_campo_fonte = campo.source or nome_campo

            campo_id = config.get("campo_id", "id")
            campo_display = config.get("campo_display", "display")

            values = getattr(instance, nome_campo_fonte, None)

            if hasattr(values, "all"):
                response[nome_campo] = [
                    {"id": v[0], "display": v[1]}
                    for v in values.values_list(campo_id, campo_display)
                ]
            else:
                if values:
                    response[nome_campo] = {
                        "id": getattr(values, campo_id, None),
                        "display": self.get_nome_display(values, campo_display),
                    }

    def serialize_campos_choice(self, instance, response):
        """Substitui campos de escolha (ChoiceField) pelo formato desejado."""
        campos_choices = getattr(self.Meta, "campos_choices", [])

        for nome_campo in campos_choices:
            campo_choice = self.fields[nome_campo]

            nome_campo_fonte = campo_choice.source or nome_campo

            value = getattr(instance, nome_campo_fonte, None)

            if value is not None:
                response[nome_campo] = {
                    "valor": value,
                    "display": getattr(instance, f"get_{nome_campo_fonte}_display")(),
                }

    def to_representation(self, instance):
        """Gera a saída final e substitui os campos de relacionamento e choices pelos valores formatados."""
        response = super().to_representation(
            instance
        )  # Serializa todos os campos normais

        # Substitui os valores nos campos de relacionamento e choices
        self.serialize_campos_relacionados(instance, response)
        self.serialize_campos_choice(instance, response)

        return response

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_200_OK,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


def get_serializer_dinamico(serializer_class, campos):
    class SerializerDinamico(serializer_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            campos_permitido = set(campos)
            campos_existente = set(self.fields.keys())
            for campo in campos_existente - campos_permitido:
                self.fields.pop(campo)

    return SerializerDinamico
