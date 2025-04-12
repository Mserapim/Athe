from apiv2.baseserializers import BaseSerializer
from rest_framework import serializers
import rest_framework.serializers
from ged.models import Arquivo


from contrib.utils import getLogger

log = getLogger(__name__)


class ArquivoSerializer(BaseSerializer):
    class Meta:
        model = Arquivo
        fields = "__all__"
