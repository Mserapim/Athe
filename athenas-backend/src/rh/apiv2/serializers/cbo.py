from contrib.utils import getLogger
from rest_framework.serializers import SerializerMethodField
from rh.models import Cbo
from apiv2.baseserializers import BaseSerializer

log = getLogger(__name__)


class CboSerializer(BaseSerializer):
    """
    Serializer para o modelo de Cbo
    """

    unicode = SerializerMethodField()

    class Meta:
        model = Cbo
        fields = "__all__"

    def get_unicode(self, obj):
        return obj.__str__()
