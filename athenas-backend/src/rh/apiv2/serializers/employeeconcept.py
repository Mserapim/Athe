import random

from contrib.crypt import Cipher
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework import serializers

from rh.gfp.models import Evento, Folha
from rh.gfp.paycheckdifference_utils import calc_from_period
from rh.models import Servidor


class BasicEmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer do Servidor para o teste de conceito
    """

    employee_matricula = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_type_by_possession = serializers.SerializerMethodField()
    employee_job_position = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = [
            "employee_matricula",
            "employee_name",
            "employee_type_by_possession",
            "employee_job_position",
        ]

    def __init__(self, *args, **kwargs) -> None:
        self.cipher = Cipher(
            algorithm=AES, mode=AES.MODE_ECB, secret=settings.SECRET_KEY[:16]
        )
        super().__init__(*args, **kwargs)

    def get_employee_matricula(self, obj):
        return self.cipher.b64_encrypt(str(obj.matricula))

    def get_employee_type_by_possession(self, obj):
        return obj.get_type_by_possession_display()

    def get_employee_job_position(self, obj):
        possessions = obj.get_posses_ativas()
        job_position = None
        if possessions.exists():
            possession = possessions.latest("data_exercicio")
            job_position = (
                possession.quadro if possession and possession.quadro else None
            )
            if not possession.quadro or not job_position:
                return ""
            return str(job_position.cargo)
        return ""

    def get_employee_name(self, obj):
        return f"FICTITIOUS NAME {random.randint(0, 999999)}"


class AidsEmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer de Auxílios do Servidor para o teste de conceito
    """

    employee_matricula = serializers.SerializerMethodField()
    aid_transportation = serializers.SerializerMethodField()
    aid_food = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ["employee_matricula", "aid_transportation", "aid_food"]

    def __init__(self, *args, **kwargs) -> None:
        self.cipher = Cipher(
            algorithm=AES, mode=AES.MODE_ECB, secret=settings.SECRET_KEY[:16]
        )
        self.folha = (
            Folha.objects.filter(tipo_folha__titulo="NORMAL")
            .order_by("-periodo__ano", "-periodo__mes")
            .first()
        )
        self.aid_transportation_event = Evento.objects.get(numero="07600")
        self.aid_food_event = Evento.objects.get(numero="06700")
        super().__init__(*args, **kwargs)

    def get_employee_matricula(self, obj):
        return self.cipher.b64_encrypt(str(obj.matricula))

    def get_aid_transportation(self, obj):
        servidor = Servidor.objects.get(id=obj.id)
        return (
            "SIM"
            if calc_from_period(
                servidor, self.folha, self.aid_transportation_event
            ).get("qnt", 0)
            else "NÃO"
        )

    def get_aid_food(self, obj):
        servidor = Servidor.objects.get(id=obj.id)
        return (
            "SIM"
            if calc_from_period(servidor, self.folha, self.aid_food_event).get("qnt", 0)
            else "NÃO"
        )

    def decrypt_employee_matricula(self, matricula):
        return int(self.cipher.b64_decrypt(matricula))
