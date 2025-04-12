from contrib.utils import getLogger
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rh.models import MetaTeletrabalho, MovimentacaoTeletrabalho, NewDateRange
from ged.models import Arquivo
from rh.pvf.const import MSG_SUCCESS_METHOD
from rh.pvf.models import (
    MarkTelework,
    PVFSolicitacaoDesbloqueioTeletrabalho,
    RelatorioSemestralTeletrabalho,
    SendingTelework,
)
from rh.pvf.apiv2.utils.telework import (
    get_envios,
    get_request_progress_telework,
    solicitacao_cancelamento_andamento,
)
from rest_framework import status
from rh.teletrabalho.utils import datas_recesso_por_ano
from standard.models import Choice
from rh.afastamento.models import BaseLicencaAfastamento
import json
import calendar

log = getLogger(__name__)


class MarkPlanSerializer(serializers.ModelSerializer):
    periodicity_label = serializers.SerializerMethodField()

    class Meta:
        model = MetaTeletrabalho
        fields = [
            "data_inicio",
            "data_fim",
            "descricao",
            "meta",
            "periodicity",
            "periodicity_label",
            "active",
        ]

    def get_periodicity_label(self, obj):
        periodicity = obj.periodicity
        choice = Choice.objects.filter(
            value=periodicity, name="TELE_WORK_META_PERIODICITY", app_label="rh"
        ).first()
        if choice:
            return choice.label
        return None


class PVFMarkTeleworkSerializer(serializers.ModelSerializer):
    mark_plan = MarkPlanSerializer()
    mark_situation_label = serializers.SerializerMethodField()
    saldo_devedor = serializers.IntegerField(source="saldo_devedor_anterior")
    qtde_dias_mes = serializers.SerializerMethodField()
    qtde_dias_mes_proporcional = serializers.SerializerMethodField()

    class Meta:
        model = MarkTelework
        fields = [
            "id",
            "mark_plan",
            "total_completed",
            "mark_situation",
            "mark_situation_label",
            "observation",
            "request",
            "meta_mes",
            "saldo_devedor",
            "qtde_dias_afastamento_mes",
            "qtde_dias_mes",
            "qtde_dias_mes_proporcional",
        ]

    def get_mark_situation_label(self, obj):
        mark_situation = obj.mark_situation
        choice = Choice.objects.filter(
            value=mark_situation, name="MARK_SITUATION", app_label="pvf"
        ).first()
        if choice:
            return choice.label
        return None

    def get_qtde_dias_mes_proporcional(self, obj):
        ano = obj.request.reference_year
        mes = obj.request.reference_month
        dias_mes = obj.mark_plan.meta_dias_mes(ano, mes)
        if mes == 1 or mes == 12:
            dt_inicio_recesso, dt_fim_recesso = datas_recesso_por_ano(ano, mes)
            if obj.mark_plan.data_fim >= dt_inicio_recesso:
                if obj.mark_plan.data_fim < dt_fim_recesso:
                    dias_recesso = NewDateRange(
                        dt_inicio_recesso, obj.mark_plan.data_fim
                    ).days
                else:
                    dias_recesso = NewDateRange(dt_inicio_recesso, dt_fim_recesso).days

                dias_mes = abs(dias_mes - dias_recesso)
        return dias_mes

    def get_qtde_dias_mes(self, obj):
        ano = obj.request.reference_year
        mes = obj.request.reference_month
        dias_mes = calendar.monthrange(ano, mes)[1]
        return dias_mes

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_400_BAD_REQUEST,
        }
        try:
            self.is_valid(raise_exception=True)
            instance.total_completed = self.validated_data.get(
                "total_completed", instance.total_completed
            )
            instance.mark_situation = self.validated_data.get(
                "mark_situation", instance.mark_situation
            )
            instance.observation = self.validated_data.get(
                "observation", instance.observation
            )
            instance.request = self.validated_data.get("request", instance.request)
            instance.mark_plan.data_inicio = self.validated_data["mark_plan"].get(
                "data_inicio", instance.mark_plan.data_inicio
            )
            instance.mark_plan.data_fim = self.validated_data["mark_plan"].get(
                "data_fim", instance.mark_plan.data_fim
            )
            instance.mark_plan.descricao = self.validated_data["mark_plan"].get(
                "descricao", instance.mark_plan.descricao
            )
            instance.mark_plan.meta = self.validated_data["mark_plan"].get(
                "meta", instance.mark_plan.meta
            )
            instance.mark_plan.periodicity = self.validated_data["mark_plan"].get(
                "periodicity", instance.mark_plan.periodicity
            )
            instance.mark_plan.active = self.validated_data["mark_plan"].get(
                "active", instance.mark_plan.active
            )
            instance.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "code": status.HTTP_201_CREATED,
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class PVFSendTeleworkSerializer(serializers.ModelSerializer):
    """
    classe serializer da solicitação de teletrablaho
    """

    referencia = serializers.CharField(source="get_sending_reference")
    inicio_plano = serializers.CharField(source="get_current_work_plan_start_date")
    fim_plano = serializers.CharField(source="get_current_work_plan_end_date")
    status = serializers.CharField(source="status_name")
    tipo_solicitacao = serializers.CharField(source="type_of_request")

    class Meta:
        model = SendingTelework
        fields = [
            "id",
            "status",
            "referencia",
            "tipo_solicitacao",
            "inicio_plano",
            "fim_plano",
            "date",
        ]

    def create(self):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            if (
                not get_request_progress_telework()
                and not solicitacao_cancelamento_andamento()
            ):
                instance = SendingTelework.create()
                rst.update(
                    success=True,
                    message="Registro criado com sucesso.",
                    data={
                        "pk": instance.pk,
                        "reference": f"{instance.reference_month}/{instance.reference_year}",
                        "work_plan_start_date": instance.work_plan.data_inicio.strftime(
                            "%Y-%m-%d"
                        ),
                        "work_plan_end_date": (
                            instance.work_plan.data_fim.strftime("%Y-%m-%d")
                            if instance.work_plan.data_fim
                            else "-"
                        ),
                    },
                )
            else:
                rst.update(
                    message="Já existe uma solicitação teletrabalho/cancelamento em andamento."
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst

    def send(self, data, pk):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            targets = json.loads(json.dumps(data.get("targets", "[]")))
            for target in targets:
                mark = MarkTelework.objects.get(pk=target.get("id"))
                total_completed = target.get("total_completed")
                balance = (
                    0
                    if total_completed >= mark.meta_mes
                    else (mark.meta_mes - target.get("total_completed"))
                )
                MarkTelework.objects.filter(pk=target.get("id")).update(
                    total_completed=target.get("total_completed"),
                    mark_situation=target.get("mark_situation"),
                    observation=target.get("observation"),
                    saldo_devedor=balance,
                )
            anexo = (
                Arquivo.objects.get(pk=data.get("anexo_id"))
                if data.get("anexo_id")
                else None
            )
            instance = SendingTelework.objects.get(pk=pk)
            instance.send(observation=data.get("observation"), anexo=anexo)
            rst = {"success": True, "message": "Envio realizado como sucesso."}
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFConfigTeleworkEmployeeSerializer(serializers.Serializer):
    """
    classe serializer da config de teletrabalho
    """

    active_workplan = serializers.BooleanField()
    telework_pending = serializers.BooleanField()
    telework_id = serializers.IntegerField()
    send_workplan_reference = serializers.IntegerField()


class PVFListaRelatorioSemestralTeletrabalhoSerializer(serializers.Serializer):
    """
    Serializer das informações de teletrabalho por aprovador
    """

    tipo_ato = serializers.CharField()
    matricula = serializers.CharField(source="servidor.matricula")
    nome = serializers.CharField(source="servidor.pessoa_fisica.social_name")

    class Meta:
        model = MovimentacaoTeletrabalho
        fields = ["tipo_ato", "matricula", "nome"]

    def get_detalhes_teletrabalho(self, obj):
        return {
            "gedoc": obj.gedoc,
            "data_inicio": obj.data_inicio,
            "data_fim": obj.data_fim,
            "envios": get_envios(obj),
        }


class PVFRelatorioSemestralTeletrabalhoSerializer(serializers.ModelSerializer):
    """
    classe serializer da solicitação semestral de teletrablaho
    """

    plano_servidores = serializers.SerializerMethodField()

    class Meta:
        model = RelatorioSemestralTeletrabalho
        fields = [
            "dificuldades_servidores",
            "medidas_dirimir_dificuldades_servidores",
            "dificuldades_facilidades_gestor",
            "medidas_dirimir_dificuldades_gestor",
            "resultados_alcancados",
            "sugestoes_melhorias",
            "plano_servidores",
        ]

    def get_plano_servidores(self, obj):
        grupo_registros = {}
        for plano in obj.espelho_mov_teletrabalhos.all():
            matricula = plano.servidor.matricula
            if matricula not in grupo_registros:
                grupo_registros[matricula] = {
                    "matricula": matricula,
                    "nome": plano.servidor.pessoa_fisica.social_name,
                    "registros": [],
                }
            grupo_registros[matricula]["registros"].append(
                {
                    "gedoc": plano.gedoc,
                    "data_inicio": plano.data_inicio,
                    "ato": plano.get_tipo_ato_display(),
                    "data_fim": plano.data_fim,
                    "envios": get_envios(plano),
                }
            )
        return list(grupo_registros.values())

    def create(self, dados):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:

            params = {
                "dificuldades_servidores": dados.get("dificuldades_servidores"),
                "medidas_dirimir_dificuldades_servidores": dados.get(
                    "medidas_dirimir_dificuldades_servidores"
                ),
                "dificuldades_facilidades_gestor": dados.get(
                    "dificuldades_facilidades_gestor"
                ),
                "medidas_dirimir_dificuldades_gestor": dados.get(
                    "medidas_dirimir_dificuldades_gestor"
                ),
                "resultados_alcancados": dados.get("resultados_alcancados"),
                "sugestoes_melhorias": dados.get("sugestoes_melhorias"),
            }
            instance = RelatorioSemestralTeletrabalho.create(params)
            rst.update(
                success=True,
                message="Registro criado com sucesso.",
                data={
                    "pk": instance.pk,
                    "dificuldades_servidores": instance.dificuldades_servidores,
                    "resultados_alcancados": instance.resultados_alcancados,
                },
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFSolicitacaoTeletrabalhoAfastamentosSerializer(ModelSerializer):
    """
    classe serializer das solicitações de afastamentos abertos que não foram efetivadas
    """

    tipo = serializers.SerializerMethodField()

    class Meta:
        model = BaseLicencaAfastamento
        fields = "__all__"

    def get_tipo(self, instance):
        return instance.situation_unicode


class PVFDesbloqueioTeletrabalhoSerializer(serializers.ModelSerializer):
    """
    classe serializer da solicitação desbloqueio do teletrabalho
    """

    class Meta:
        model = PVFSolicitacaoDesbloqueioTeletrabalho
        fields = []

    def criar(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            instance = PVFSolicitacaoDesbloqueioTeletrabalho.criar(data)
            rst.update(
                success=True,
                message="Registro criado com sucesso.",
                data={"pk": instance.pk},
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst
