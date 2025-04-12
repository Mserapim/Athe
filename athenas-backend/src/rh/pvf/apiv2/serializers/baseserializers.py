import json
from contrib.middleware import set_current_user
from ged.models import Arquivo
from rest_framework.serializers import ModelSerializer
from rh.apiv2.serializers.servidor import ServidorListagemSerializer
from rh.pvf.apiv2.utils.base import formart_date_str, get_lista_params
from rh.pvf.apiv2.utils.telework import (
    get_request_progress_telework,
    solicitacao_cancelamento_andamento,
)
from rh.pvf.apiv2.utils.timesheet import get_request_progress_timesheet
from rh.pvf.const import (
    CHAVE_TIPOS_SOLICITACOES,
    MSG_SUCCESS_METHOD,
    REQUEST_TYPE_TELEWORK,
)
from rh.pvf.models import PortalRequest, PortalRequestHistory, PortalRequestSubstitute
from standard.models import Choice
from contrib.utils import getLogger
from rh.models import (
    Lotacao,
    MovesSubstitutionsConsolidated,
    Servidor,
    ServidorLotacao,
    PessoaFisica,
    MovimentacaoSubstituicao,
)
from rest_framework import serializers
from rest_framework import status
from datetime import datetime


log = getLogger(__name__)


class PVFRequestSerializer(ModelSerializer):
    """
    classe serializer das solicitações VDF
    """

    parcel_number = serializers.IntegerField(source="get_parcel_number")
    reference = serializers.CharField(source="get_sending_reference")
    start_work_plan = serializers.CharField(source="get_current_work_plan_start_date")
    end_work_plan = serializers.CharField(source="get_current_work_plan_end_date")
    plan_work_id = serializers.IntegerField(source="get_plan_work_id")
    lotacao_teletrabalho = serializers.CharField(source="get_lotacao_teletrabalho")
    anexo_id = serializers.SerializerMethodField()
    anexo_name = serializers.SerializerMethodField()
    termo_aceite = serializers.SerializerMethodField()
    classe_atual = serializers.SerializerMethodField()
    classe_progredir = serializers.SerializerMethodField()
    metas_saldo_devedor = serializers.SerializerMethodField()

    titulo_campo = {
        "pk": "Código",
        "date": "Data da solicitação",
        "type_of_request": "Tipo da solicitação",
        "employee_name": "Solicitante",
        "approver_name": "Aprovador",
        "status_name": "Situação",
        "days_awaiting_approval": "Dias aguardando aprovação",
    }

    class Meta:
        model = PortalRequest
        fields = [
            "pk",
            "portal_request_type",
            "type_of_request",
            "date",
            "employee",
            "employee_name",
            "status",
            "status_name",
            "step_current",
            "step_current_name",
            "approver",
            "approver_name",
            "parcel_number",
            "acquisitive_period",
            "days_awaiting_approval",
            "reference",
            "start_work_plan",
            "end_work_plan",
            "plan_work_id",
            "lotacao_teletrabalho",
            "anexo_id",
            "anexo_name",
            "termo_aceite",
            "classe_atual",
            "classe_progredir",
            "metas_saldo_devedor",
        ]

    def get_anexo_id(self, obj):
        if obj.request_type == REQUEST_TYPE_TELEWORK:
            return obj.sendingtelework.anexo.pk if obj.sendingtelework.anexo else None
        return None

    def get_anexo_name(self, obj):
        if obj.request_type == REQUEST_TYPE_TELEWORK:
            return (
                obj.sendingtelework.anexo.filename
                if obj.sendingtelework.anexo
                else None
            )
        return None

    def get_termo_aceite(self, obj):
        if hasattr(obj, "portalrequestprogressionh"):
            return obj.portalrequestprogressionh.termo_aceite
        return None

    def get_classe_atual(self, obj):
        if hasattr(obj, "portalrequestprogressionh"):
            return (
                obj.portalrequestprogressionh.progression.referencia_nivel2d.sigla_cache
            )
        return None

    def get_classe_progredir(self, obj):
        if hasattr(obj, "portalrequestprogressionh"):
            return obj.portalrequestprogressionh.config.name
        return None

    def get_metas_saldo_devedor(self, obj):
        if hasattr(obj, "sendingtelework"):
            return obj.sendingtelework.metas_saldo_devedor
        return None


class PVFServidorSerializer(ServidorListagemSerializer):

    class Meta:
        model = Servidor
        fields = ServidorListagemSerializer.Meta.fields

    def get_unicode(self, obj):
        return f"{obj.matricula}: {self.get_nome(obj)}"


class PVFConfigTypeSerializer(ModelSerializer):
    """
    classe serializer das configuração dos tipos de solicitação VDF
    """

    class Meta:
        model = Choice
        fields = ["label", "value"]


class PVFConfigStepSerializer(ModelSerializer):
    """
    classe serializer das configuração das etapas/aprovador VDF
    """

    label = serializers.CharField(source="description")

    class Meta:
        model = Choice
        fields = ["label", "value"]


class PVFConfigTypeEmployeeSerializer(serializers.Serializer):
    """
    classe serializer das configuração das Tipo Servidor VDF
    """

    value = serializers.CharField(source="cvalue")

    label = serializers.CharField()
    value = serializers.CharField()


class PVFSubstituteCandidateSerializer(ModelSerializer):
    """
    classe serializer dos candidatos à subsititutos das solicitações VDF
    """

    class Meta:
        model = Servidor
        fields = ["pk", "matricula", "name", "office"]


class PVFEmployeeSerializer(ModelSerializer):
    """
    classe serializer do servidores ativos
    """

    class Meta:
        model = Servidor
        fields = ["pk", "name", "matricula"]


class PVFWorkplaceDutySerializer(ModelSerializer):
    """
    Serializer do model Lotação
    """

    name = serializers.CharField(source="nome")
    responsible = serializers.CharField(source="responsible_name")

    class Meta:
        model = Lotacao
        fields = ["pk", "name", "responsible"]


class HistoricoArquivoSerializer(serializers.ModelSerializer):
    nome_arquivo = serializers.CharField(source="filename")

    class Meta:
        model = Arquivo
        fields = ["id", "nome_arquivo"]


class PVFHistorySerializer(ModelSerializer):
    """
    classe serializer histórico da solicitações do vida funcional
    """

    group = serializers.CharField(source="get_group_name")
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    anexos = serializers.SerializerMethodField()

    class Meta:
        model = PortalRequestHistory
        fields = [
            "pk",
            "date",
            "group",
            "employee",
            "action_label",
            "observation",
            "anexos",
        ]

    def get_anexos(self, obj):
        anexos = obj.anexos.all()
        serializer = HistoricoArquivoSerializer(anexos, many=True)

        anexos_data = serializer.data
        for anexo_data in anexos_data:
            anexo_data["origem"] = obj.get_origem
        return anexos_data


class PVFSubstituteSerializer(ModelSerializer):
    """
    classe serializer do substitutos da solicitações do vida funcional
    """

    class Meta:
        model = PortalRequestSubstitute
        fields = ["pk", "substitute_name", "designation", "start_date", "end_date"]


class PVFDesignationSerializer(ModelSerializer):
    """
    classe serializer da Designação/Exercicio da tela de substitutos
    """

    employee = serializers.CharField(source="employee_name")
    exercise = serializers.CharField(source="exercise_name")
    range_dates = serializers.SerializerMethodField()

    class Meta:
        model = ServidorLotacao
        fields = ["pk", "employee", "exercise", "range_dates"]

    def get_range_dates(self, obj):
        params = self.context["request"].query_params.items()
        datas = get_lista_params(params)
        intervalo_data = []
        if datas:
            for data in datas:
                data_inicio = datetime.strptime(
                    formart_date_str(data["start_date"]), "%d/%m/%Y"
                ).date()
                data_fim = datetime.strptime(
                    formart_date_str(data["end_date"]), "%d/%m/%Y"
                ).date()
                if not obj.data_vigencia_fim:
                    if (
                        data_inicio < obj.data_vigencia_inicio
                        and data_fim >= obj.data_vigencia_inicio
                    ):
                        intervalo_data.append([obj.data_vigencia_inicio, data_fim])
                    elif data_inicio >= obj.data_vigencia_inicio:
                        intervalo_data.append([data_inicio, data_fim])
                else:
                    if (
                        data_inicio >= obj.data_vigencia_inicio
                        and data_fim <= obj.data_vigencia_fim
                    ):
                        intervalo_data.append([data_inicio, data_fim])
                    elif (
                        data_inicio >= obj.data_vigencia_inicio
                        and data_fim > obj.data_vigencia_fim
                    ):
                        if data_inicio <= obj.data_vigencia_fim:
                            intervalo_data.append([data_inicio, obj.data_vigencia_fim])
                    elif (
                        data_inicio < obj.data_vigencia_inicio
                        and data_fim <= obj.data_vigencia_fim
                    ):
                        if obj.data_vigencia_inicio <= data_fim:
                            intervalo_data.append([obj.data_vigencia_inicio, data_fim])
                    elif (
                        data_inicio < obj.data_vigencia_inicio
                        and data_fim > obj.data_vigencia_fim
                    ):
                        intervalo_data.append(
                            [obj.data_vigencia_inicio, obj.data_vigencia_fim]
                        )
        else:
            data_futura = datetime.strptime("01/01/9999", "%d/%m/%Y").date()
            data_fim = obj.data_vigencia_fim if obj.data_vigencia_fim else data_futura
            intervalo_data.append([obj.data_vigencia_inicio, data_fim])
        return intervalo_data


class PVFPersonSerializer(ModelSerializer):
    """
    classe serializer de pesssoa física VDF
    """

    name = serializers.CharField(source="nome")

    class Meta:
        model = PessoaFisica
        fields = [
            "pk",
            "name",
            "social_name",
            "email_pessoal",
            "cpf",
            "rg",
            "rg_orgao",
            "rg_uf",
            "rg_data_expedicao",
            "data_nascimento",
            "municipio_naturalidade",
            "sexo",
            "sexual_orientation",
            "immigrant_residence_time",
            "immigrant_entry_condition",
        ]

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class PVFTypeAbsenceSerializer(ModelSerializer):
    """
    classe serializer das configuração dos tipos de afastamentos VDF
    """

    class Meta:
        model = Choice
        fields = ["label", "value"]


class PVFTipoSolicitacaoSerializer(ModelSerializer):
    """
    classe serializer das configuração dos tipos de solicitações VDF
    """

    value = serializers.SerializerMethodField()
    habilitado = serializers.SerializerMethodField()
    mensagem = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["label", "value", "habilitado", "mensagem"]

    def get_value(self, obj):
        return CHAVE_TIPOS_SOLICITACOES.get(obj.value, None)

    def get_habilitado(self, obj):
        set_current_user(self.context["request"].user)
        if CHAVE_TIPOS_SOLICITACOES.get(obj.value) == "FOLHA_PONTO":
            return not get_request_progress_timesheet()
        elif CHAVE_TIPOS_SOLICITACOES.get(obj.value) in [
            "TELETRABALHO",
            "CANCELAMENTO_TELETRABALHO",
        ]:
            return not (
                get_request_progress_telework() or solicitacao_cancelamento_andamento()
            )
        else:
            return True

    def get_mensagem(self, obj):
        if not self.get_habilitado(obj):
            if CHAVE_TIPOS_SOLICITACOES.get(obj.value) == "FOLHA_PONTO":
                return "Já existe uma solicitação de folha ponto em andamento."
            elif CHAVE_TIPOS_SOLICITACOES.get(obj.value) in [
                "TELETRABALHO",
                "CANCELAMENTO_TELETRABALHO",
            ]:
                return "Já existe uma solicitação de Teletrabalho/Cancelamento aguardando aprovação no momento.'"
        return None


class NumberOrStringField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if data is None or isinstance(data, (int, float, str)):
            return data
        raise serializers.ValidationError(
            "Este campo deve ser um número, texto ou None."
        )


class PVFTMyPendeciesSerializer(serializers.Serializer):

    title = serializers.CharField()
    type = serializers.CharField()
    message = serializers.CharField()
    value = NumberOrStringField()


class PVFMinhasSubstituicoesSerializer(ModelSerializer):
    """
    classe serializer das Minhas Substituicoes
    """

    serv_substituto = serializers.CharField(source="get_texto_servidor")
    serv_substituido = serializers.CharField(source="get_texto_servidor_substituido")
    cumulativa = serializers.CharField(source="get_cumulativa")
    lotacao = serializers.CharField(source="get_lotacao")

    class Meta:
        model = MovimentacaoSubstituicao
        fields = [
            "id",
            "lotacao",
            "serv_substituto",
            "serv_substituido",
            "data_inicio",
            "data_fim",
            "cumulativa",
            "pay_month",
            "pay_year",
            "paid_out",
            "able_to_pay",
        ]


class PVFVendaSubstituicoesSerializer(ModelSerializer):
    """
    classe serializer da Venda de Cumulativo de Substituições
    """

    serv_substituto = serializers.CharField(source="get_texto_servidor")
    serv_substituido = serializers.CharField(source="get_texto_servidor_substituido")
    cumulativa = serializers.CharField(source="get_cumulativa")
    lotacao = serializers.CharField(source="get_lotacao")
    dias_consolidados = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = MovimentacaoSubstituicao
        fields = [
            "id",
            "lotacao",
            "serv_substituto",
            "serv_substituido",
            "data_inicio",
            "data_fim",
            "cumulativa",
            "able_to_pay",
            "pay_month",
            "pay_year",
            "paid_out",
            "indeferido",
            "dias_consolidados",
            "status_label",
        ]

    def get_dias_consolidados(self, obj):
        mov_consolidado = MovesSubstitutionsConsolidated.objects.filter(
            substitutions__pk=obj.pk
        ).first()
        if mov_consolidado:
            return mov_consolidado.days_consolidated
        return None

    def get_status_label(self, obj):
        if obj.indeferido:
            return "Indeferido"
        elif obj.paid_out:
            return "Pago"
        elif obj.consolidated:
            return "Consolidado"
        elif obj.able_to_pay:
            return "Apto Pagamento"
        else:
            return "Inapto Pagamento"
