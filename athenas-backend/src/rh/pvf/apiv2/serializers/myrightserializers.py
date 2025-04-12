from rest_framework.serializers import ModelSerializer
from rh.dayoff.models import (
    AcquisitionPeriod,
    AcquisitionPeriodAttachment,
    Configuration,
    Usufruct,
)
from contrib.utils import getLogger
from rest_framework import serializers


log = getLogger(__name__)


class PVFMyRightsSerializer(ModelSerializer):
    """
    classe serializer dos tipos de direitos
    """

    class Meta:
        model = Configuration
        fields = ["pk", "title", "balance_days"]


class PVFMyRightsAqPeriodSerializer(ModelSerializer):
    """
    classe serializer dos períodos aquisitivos da tela meus direitos
    """

    class Meta:
        model = AcquisitionPeriod
        fields = [
            "pk",
            "group_period_name",
            "start_date_fruition",
            "start_date_acquisition",
            "end_date_acquisition",
            "days",
            "booked_days",
            "balance_available",
        ]


class PVFMyRightsUsufructSerializer(ModelSerializer):
    """
    classe serializer dos usufrutos da tela meus direitos
    """

    class Meta:
        model = Usufruct
        fields = ["pk", "status_name", "start_date", "end_date", "days"]


class PVFAttachmentAqPeriodSerializer(ModelSerializer):
    """
    classe serializer dos anexos do período aquisitivo
    """

    start_date = serializers.DateField(source="date_start")
    end_date = serializers.DateField(source="date_end")
    days = serializers.IntegerField(source="days_law")
    acquisition_period_name = serializers.CharField(source="acquisition_period_str")

    class Meta:
        model = AcquisitionPeriodAttachment
        fields = [
            "pk",
            "acquisition_period_name",
            "description",
            "information",
            "start_date",
            "end_date",
            "days",
        ]
