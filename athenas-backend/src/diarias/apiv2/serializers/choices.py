from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
from standard.models import Choice

from contrib.utils import getLogger

log = getLogger(__name__)


class ChoicesDiariasSerializer(BaseSerializer):

    id = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "descricao"]

    def get_id(self, obj):
        return obj.value

    def get_descricao(self, obj):
        return obj.label
