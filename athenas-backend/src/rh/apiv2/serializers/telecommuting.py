from rest_framework import serializers

from rh.models import MembersTelecommuting, Telefone

from contrib.utils import getLogger


log = getLogger(__name__)


class TelecommutingSerializer(serializers.ModelSerializer):
    """
    Serializer de Membros em Trabalho Remoto
    """

    employee_name = serializers.CharField(source="employee.pessoa_fisica.nome")
    institutional_phone = serializers.SerializerMethodField()
    institutional_email = serializers.CharField(
        source="employee.pessoa_fisica.email_institucional"
    )

    class Meta:
        model = MembersTelecommuting
        fields = [
            "employee_name",
            "institutional_phone",
            "institutional_email",
            "data_inicio",
            "data_fim",
        ]

    def get_institutional_phone(self, obj):
        institutional_phone = Telefone.objects.filter(
            person=obj.employee.pessoa_fisica.pk, tipo_telefone=5
        ).last()
        if institutional_phone:
            return institutional_phone.numero
        return None
