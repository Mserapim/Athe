from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer

from standard.models import Choice


class ChoicesFormularioSerializer(BaseSerializer):
    """ 
        Serializer do model Choices
    """

    class Meta:
        model = Choice
        fields = ['valor', 'display']

        extra_kwargs = {
            "valor": {"source": "value"},
            "display": {"source": "label"},
        }