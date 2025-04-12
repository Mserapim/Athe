from contrib.utils import getLogger
from rest_framework import serializers
from common.usefulday.models import NonWorkingDay
from apiv2.baseserializers import BaseSerializer

log = getLogger(__name__)


class NonWorkingDaySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de NonWorkingDay
    """

    class Meta:
        model = NonWorkingDay
        fields = [
            "description",
            "is_partial",
            "start_date",
            "end_date",
            "abrangency",
            "kind",
            "places",
        ]


class DiasUteisSerializer(BaseSerializer):
    """
    Serializer para o modelo de NonWorkingDay
    """

    class Meta:
        model = NonWorkingDay
        fields = "__all__"
