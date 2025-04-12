from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer

from standard.models import ClassCode


class ClasscodesSerializer(BaseSerializer):
    """
    Serializer do model ClassCode
    """

    class Meta:
        model = ClassCode
        fields = "__all__"
