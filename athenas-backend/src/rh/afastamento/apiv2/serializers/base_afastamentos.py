import random
from contrib.crypt import Cipher
from Crypto.Cipher import AES
from django.conf import settings

from rest_framework import serializers
from rh.afastamento.models import BaseLicencaAfastamento


class BasicAbsenceSerializer(serializers.ModelSerializer):
    """
    Serializer do Afastamentos - (Modelo de Teste)
    """

    employee_matricula = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    absence_type = serializers.SerializerMethodField()
    absence_start_date = serializers.SerializerMethodField()
    absence_end_date = serializers.SerializerMethodField()

    class Meta:
        model = BaseLicencaAfastamento
        fields = [
            "employee_matricula",
            "employee_name",
            "absence_type",
            "absence_start_date",
            "absence_end_date",
        ]

    def __init__(self, *args, **kwargs) -> None:
        self.cipher = Cipher(
            algorithm=AES, mode=AES.MODE_ECB, secret=settings.SECRET_KEY[:16]
        )
        super().__init__(*args, **kwargs)

    def get_employee_matricula(self, obj):
        return self.cipher.b64_encrypt(str(obj.servidor.matricula))

    def get_employee_name(self, obj):
        return f"FICTITIOUS NAME {random.randint(0, 999999)}"

    def get_absence_type(self, obj):
        return obj.situation_unicode

    def get_absence_start_date(self, obj):
        return obj.data_inicio

    def get_absence_end_date(self, obj):
        return obj.data_fim

    def decrypt_employee_matricula(self, matricula):
        return int(self.cipher.b64_decrypt(matricula))
