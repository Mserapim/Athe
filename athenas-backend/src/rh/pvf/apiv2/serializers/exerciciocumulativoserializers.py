from contrib.middleware import get_current_user
from rh.models import ConfigPeriodoCumulativoSubstituicao, MovimentacaoSubstituicao
from rh.pvf.const import REQUEST_ACT_ANNOTATION, STS_REJECTED
from rh.pvf.models import PVFExercicioCumulativo, PortalRequestHistory
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.db import transaction
from contrib.utils import getLogger
from datetime import datetime
import json

log = getLogger(__name__)


class PVFExercicioCumulativoSerializers(ModelSerializer):

    class Meta:
        model = PVFExercicioCumulativo
        fields = []

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            params.update(
                {
                    "substituicoes_ids": json.dumps(data.get("substituicoes_ids")),
                    "observacao": data.get("observation"),
                }
            )
            instance = self.Meta.model.create(params)
            instance.send()
            rst.update(
                {
                    "success": True,
                    "message": "Registro criado com sucesso",
                    "data": {
                        "pk": instance.pk,
                        "type_of_request": instance.type_of_request,
                        "date": instance.date,
                        "employee_name": instance.employee_name,
                        "approver": instance.set_custom_approver,
                        "status_name": instance.status_name,
                    },
                }
            )

        except Exception as err:
            log.error(str(err))
            rst.update({"message": str(err)})

        return rst

    def send(self, data, pk):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            instance = PVFExercicioCumulativo.objects.get(pk=pk)
            instance.send(observation=data.get("observation"))
            rst = {"success": True, "message": "Envio realizado como sucesso."}
        except Exception as err:
            log.error(err)
            rst.update({"message": str(err)})

        return rst


class PVFSubstituicaoConfigPeridoVendaSerializers(ModelSerializer):

    class Meta:
        model = ConfigPeriodoCumulativoSubstituicao
        fields = [
            "data_inicio_periodo",
            "data_fim_periodo",
            "data_inicio_abrangencia",
            "data_fim_abrangencia",
        ]


class PVFIndefirExercicioCumulativoeSerializer(ModelSerializer):
    class Meta:
        model = MovimentacaoSubstituicao
        fields = []

    def indeferir(self, data, pk):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            observacao = data.get("observation", None)
            with transaction.atomic():
                MovimentacaoSubstituicao.objects.filter(pk=pk).update(indeferido=True)
                solicitacao = PVFExercicioCumulativo.objects.filter(
                    substituicoes__pk=pk
                ).first()
                if not solicitacao.substituicoes.filter(indeferido=False).exists():
                    solicitacao.status = STS_REJECTED
                    solicitacao.save()
                PortalRequestHistory.create_history(
                    observation=observacao,
                    action=REQUEST_ACT_ANNOTATION,
                    request=solicitacao,
                    date=datetime.now(),
                    group=None,
                    user=get_current_user(),
                )
            rst.update(success=True, message="Procedimento realizado com sucesso.")

        except Exception as err:
            log.error(err)
            rst.update({"message": str(err)})

        return rst


class PVFDiasConsolidadosSerializer(serializers.Serializer):
    """
    Serializers dos dias consolidados
    """

    dias_consolidados = serializers.IntegerField()
