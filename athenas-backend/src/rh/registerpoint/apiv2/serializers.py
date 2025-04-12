from apiv2.baseserializers import BaseSerializer
from rest_framework.serializers import ModelSerializer
from rh.models import Lotacao, Servidor
from rh.pvf.models import PointJustification
from rh.registerpoint.const import ANEXO_OBRIGATORIO
from rh.registerpoint.models import MarkPoint
from contrib.utils import getLogger, get_json_engine
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
from datetime import datetime, timedelta
from rest_framework import serializers
from rh.registerpoint.utils.markpoint import get_ipaddress, validate_ip_address
import pytz

from standard.models import Choice, JustificationItem

log = getLogger(__name__)
json = get_json_engine()


class PVFLastRegistereSerializer(ModelSerializer):
    """
    Classe serializer da última batida de ponto
    """

    name = serializers.CharField(source="get_name")
    date = serializers.DateField(source="day")
    hour = serializers.TimeField(source="mark")

    class Meta:
        model = MarkPoint
        fields = ["pk", "hour", "date", "name"]


class PVFRegisterPointSerializer(ModelSerializer):
    """
    Classe serializer para registro de ponto
    """

    class Meta:
        model = MarkPoint
        fields = []

    def register_point(self, request):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            employee = employee_from_user(get_current_user())
            if employee is None:
                return {
                    "success": False,
                    "message": "Usuário inativo para registro de ponto. Procure o DGP para regularizar o cadastro.",
                }

            timezone_cuiaba = pytz.timezone("America/Cuiaba")
            hoje = datetime.now(timezone_cuiaba)

            ultima_batida = (
                MarkPoint.objects.filter(employee=employee)
                .order_by("-day", "-mark")
                .first()
            )
            if ultima_batida and ultima_batida.marcacao:
                ultima_batida_marcacao = timezone_cuiaba.localize(
                    ultima_batida.marcacao
                )
                if hoje - ultima_batida_marcacao < timedelta(minutes=3):
                    return {
                        "success": False,
                        "message": "Identificamos um ponto registrado em menos de 3 minutos. Aguarde para registrar um novo ponto.",
                    }
            marks = MarkPoint.objects.filter(
                day=datetime.today().date(), employee=employee
            ).count()
            ip = get_ipaddress(request)
            validate_ip_address(ip)
            if marks < 4:
                instance = MarkPoint(
                    employee=employee,
                    mark=hoje.time(),
                    day=hoje.date(),
                    marcacao=datetime(
                        hoje.year,
                        hoje.month,
                        hoje.day,
                        hoje.hour,
                        hoje.minute,
                        hoje.second,
                    ),
                    ip=ip,
                )
                instance.save()
                obj.update(
                    success=True,
                    message="Ponto registrado com sucesso.",
                )
            else:
                obj.update(
                    success=False,
                    message="Já foram registradas 4 batidas no dia.",
                )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        return obj


class FolhaPontoServidorSerializer(serializers.ModelSerializer):
    servidor = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ["id", "servidor", "ativo"]

    def get_servidor(self, instance):
        return instance.__str__()


class FolhaPontoParamentroSerializer(serializers.ModelSerializer):

    descricao = serializers.CharField(source="label")
    cod = serializers.IntegerField(source="value")

    class Meta:
        model = Choice
        fields = ["cod", "descricao"]


class FolhaPontoJustificativasSerializer(BaseSerializer):
    tipo_justificativa = serializers.IntegerField(source="reason_type")
    tipo_justificativa_display = serializers.SerializerMethodField(required=False)
    horas = serializers.CharField(source="number_hours")
    data_inicio = serializers.DateField(source="start_date")
    data_fim = serializers.DateField(source="end_date")
    observacao = serializers.CharField(
        source="observation", required=False, allow_null=True
    )
    anexo_id = serializers.IntegerField(
        source="attachment_id", required=False, allow_null=True
    )
    origem_display = serializers.SerializerMethodField(required=False)
    servidor_id = serializers.IntegerField(source="employee_id")

    class Meta:
        model = PointJustification
        fields = [
            "id",
            "tipo_justificativa",
            "tipo_justificativa_display",
            "horas",
            "data_inicio",
            "data_fim",
            "observacao",
            "anexo_id",
            "cancelado",
            "origem",
            "origem_display",
            "servidor_id",
        ]

    def get_tipo_justificativa_display(self, instance):
        return instance.get_motivo_nome

    def get_origem_display(self, instance):
        if instance.origem:
            return instance.get_origem_display()
        return None


class FolhaPontoTipoJustificativaSerializer(serializers.ModelSerializer):

    justificativa_display = serializers.CharField(source="name")
    anexo_obrigatorio = serializers.SerializerMethodField()

    class Meta:
        model = JustificationItem
        fields = ["id", "justificativa_display", "anexo_obrigatorio", "value"]

    def get_anexo_obrigatorio(self, instance):
        if (
            instance.mandatory_document
            and instance.mandatory_document == ANEXO_OBRIGATORIO
        ):
            return True
        return False


class FolhaPontoLotacaoSerializer(serializers.ModelSerializer):

    lotacao_display = serializers.CharField(source="nome")

    class Meta:
        model = Lotacao
        fields = ["id", "lotacao_display"]
