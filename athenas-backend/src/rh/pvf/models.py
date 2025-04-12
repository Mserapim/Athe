# -*- coding: utf-8 -*-
# import oracledb
import calendar

from calendar import monthrange
from collections import Counter
from functools import reduce
from operator import or_

from auditlog.registry import auditlog
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import connections, transaction, models
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
import time

from rh.dayoff.const import (
    ACT_BOOK_SELL,
    ACT_INTERRUPT,
    ACT_RECTIFY,
    USU_CANCELED,
    USU_CHANGED,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_NEW,
    USU_NOT_AUTHORIZED,
    USU_SOLD,
    USU_SUBSTITUTE,
    USU_SUSPENDED,
    USU_INTERRUPTED,
    ACT_BOOK,
    ACT_CHANGE,
    ACT_ST_HOMOLOGATED,
    ACT_ST_SOLD,
    ACQP_PROGRESS,
    ACQP_FINISHED,
    ACQP_INDEMNIFIED,
    ACT_SUSPEND,
)
from rh.const import (
    CANCELADO,
    STATUS_TELETRABALHO_BLOQUEADO,
    STATUS_TELETRABALHO_DESBLOQUEADO,
    STATUS_TELETRABALHO_PENDENTE,
    STATUS_TELETRABALHO_REGULAR,
    TIPO_DEPENDENTE_IR,
    TIPO_DEPENDENTE_AUX_CRECHE,
    TYPE_HEALTH_FAMILY_DESEASE,
    TYPE_MATERNITY_LICENSE,
    TYPE_ABSENCE_BIRTH,
)
from rh.gratifications_manager.cumulative_exercices_utils import (
    validar_periodo_vigente_exerc_cumul_subs,
)
from rh.pvf.apiv2.utils.approval import group_list
from rh.pvf.const import *
from rh.pvf.utils.folha_ponto import (
    data_inicio_fim_referencia,
    get_ultimo_dia_referencia,
    proxima_referencia,
    referencia_anterior,
)
from rh.pvf.utils.justificativas_portal_request import cancelar_justificativas_request
from rh.pvf.utils.teletrabalho import get_teletrabalhos_semestrais
from rh.pvf.utils.emails import notifica_cadastro_plantao
from rh.pvf.utils.utils import (
    ajustar_venda_plantoes,
    e_plantao_compensatoria,
    get_period_aquisitivos_ordernados,
)
from rh.pvf.utils.validacoes import validar_substituto_afastamento
from rh.registerpoint.const import (
    ORIGEM_JUSTIFICATIVA_FOLHA_PONTO,
    ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO,
)
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
from standard.models import (
    Choice,
    Item,
    JustificationItem,
    AuditTimestampModel,
    EmailTemplate,
)

from contrib.utils import employee_from_user, getLogger
from contrib.middleware import get_current_user
from rh.dayoff.models import (
    Activity,
    ConfiguracaoPlantaoEleitoral,
    Usufruct,
    AcquisitionPeriod,
    Configuration,
    ActivityBookSell,
    ActivityCancel,
    ActivityRetify,
    AcquisitionPeriodAttachment,
    GroupPeriod,
)
from rh.models import (
    PessoaFisica,
    Servidor,
    CargaHoraria,
    MovimentacaoPosse,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
)
from rh.afastamento.models import CID, BaseLicencaAfastamento
from datetime import date, datetime, timedelta
from contrib.daterange import NewDateRange
from common.usefulday.models import NonWorkingDay
from common.util.send_email import EmailNotification
from rh.models import (
    ServidorLotacao,
    Publicacao,
    Dependente,
    Dependencia,
    MetaTeletrabalho,
    MovimentacaoTeletrabalho,
)
from contrib.decorator import to_search
from rh.pvf.approvalflow import (
    BloodDonationApprovalFlow,
    CancelamentoTeletrabalhoApprovalFlow,
    ExercicioCumulativoApprovalFlow,
    MemberApprovalFlow,
    RelatorioSemestralTeletrabalhoApprovalFlow,
    ServerApprovalFlow,
    ManagerApprovalFlow,
    InternApprovalFlow,
    PointSheetApprovalFlow,
    SolicitacaoCreditoFolgaApprovalFlow,
    SolicitacaoVendaPlantaoFlow,
    TeleWorkApprovalFlow,
    DutyApprovalFlow,
    ProgressionApprovalFlow,
    ProgressionHApprovalFlow,
    SolicitacaoAuxCrecheDepenIRApprovalFlow,
    DesbloqueioTeletrabalhoApprovalFlow,
    CreditoDispensaEleitoralApprovalFlow,
)
from ged.models import Arquivo as File
from rh.gfp.models import (
    ProgressionDocument,
    MovimentacaoProgressao,
    HorizontalProgressionConfig,
    EstruturaTabelaSalarial,
)
from engine.models import GroupPermission
from rh.pvf.utils.point_sheet_data import create_data_point_sheet
from engine.mq.models import Task
from collections import defaultdict
from rh.gratifications_manager.tasks_cumulative_exercises import (
    consolidate_able_to_pay_employee_task,
    desconsolidate_item_task,
    calculate_consolidated_task,
    defer_consolidated_task,
    efetivar_exercicio_cumulativo_task,
)


log = getLogger(__name__)


TIPOS_FLUXO_APROVACAO_NAO_USUFRUTOS_AFASTAMENTOS = {
    REQUEST_TYPE_POINT_SHEET: PointSheetApprovalFlow,
    REQUEST_TYPE_TELEWORK: TeleWorkApprovalFlow,
    REQUEST_TYPE_SERVER_DUTY: DutyApprovalFlow,
    REQUEST_TYPE_PROGRESSION_V: ProgressionApprovalFlow,
    REQUEST_TYPE_PROGRESSION_H: ProgressionHApprovalFlow,
    REQUEST_TYPE_CUMULATIVE_EXERCISE: ExercicioCumulativoApprovalFlow,
    REQUEST_TYPE_CANCELAMENTO_TELETRABALHO: CancelamentoTeletrabalhoApprovalFlow,
    REQUEST_TYPE_RELATORIO_TELE_SEMESTRAL: RelatorioSemestralTeletrabalhoApprovalFlow,
    REQUEST_TYPE_SOLICITACAO_CREDITO_FOLGA: SolicitacaoCreditoFolgaApprovalFlow,
    REQUEST_TYPE_SOLICITACAO_AUX_CRECHE_DEPEN_IR: SolicitacaoAuxCrecheDepenIRApprovalFlow,
    REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO: DesbloqueioTeletrabalhoApprovalFlow,
    REQUEST_TYPE_CREDITO_DISPENSA_ELEITORAL: CreditoDispensaEleitoralApprovalFlow,
}


class PortalRequest(models.Model):
    request_type = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "REQUEST_TYPE"),
        verbose_name="Tipo agrupado de solicitação",
    )  # Tipos genéricos das solicitações do VDF
    date = models.DateField(verbose_name="Data da Solicitação")
    request = models.ForeignKey(
        User,
        verbose_name="Solicitante",
        related_name="portal_request_user",
        on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="portal_request_employee",
        on_delete=models.CASCADE,
    )
    status = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "REQUEST_STATUS"),
        verbose_name="Status",
    )
    step_current = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "REQUEST_STEP"),
        verbose_name="Etapa Atual",
    )
    approver = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Aprovador Atual",
        related_name="portal_request_approver_current",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    portal_request_type = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "REQUEST_TYPE_VDF"),
        verbose_name="Tipos de Solicitações VDF",
        blank=True,
        null=True,
    )  # Tipos específicos das solicitações do VDF

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "{}-{}".format(
            self.get_request_type_display(),
            self.employee if hasattr(self, "employee") else "",
        )

    def __init__(self, *args, **kwargs):
        self.book_usufructs = []
        self.sale_usufructs = None
        self.sub_type_usufruct_id = None
        super().__init__(*args, **kwargs)

    @property
    def employee_name(self):
        """property que retorna o nome do solicitante
        :returns: str
        """
        return f"{self.employee.matricula}:{self.employee.pessoa_fisica.nome}"

    @property
    def approver_name(self):
        """property que retorna o nome do aprovador
        :returns: str
        """
        return self.set_custom_approver

    @property
    def status_name(self):
        """property que retorna o status da solicitação
        :returns: str
        """
        return self.get_status_display()

    @property
    def step_current_name(self):
        """property que retorna o etapa atual da solicitação
        :returns: str
        """
        return self.get_step_current_display()

    @property
    def get_sending_reference(self):
        """property que retorna a referência do teletrablho ou folha ponto
        :returns: str
        """
        if hasattr(self, "sendingtimesheet"):
            return f"{self.sendingtimesheet.reference_month}/{self.sendingtimesheet.reference_year}"
        elif hasattr(self, "sendingtelework"):
            return f"{self.sendingtelework.reference_month}/{self.sendingtelework.reference_year}"
        elif hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho"):
            solicitacao_desbloqueio = self.pvfsolicitacaodesbloqueioteletrabalho
            return f"{solicitacao_desbloqueio.referencia_mes}/{solicitacao_desbloqueio.referencia_ano}"

    @property
    def days_awaiting_approval(self):
        """
        Dias Aguardando Aprovação
        """
        if self.status in [
            STS_EFFECTIVE,
            STS_REJECTED,
            STS_CANCELED_DGP,
            STS_CANCELED_APPLICANT,
        ]:
            return 0
        historys = self.portalrequesthistory_set.all()
        history = historys.order_by("-date").first()
        return abs((history.date.date() - datetime.today().date()).days)

    @property
    def type_of_request(self):
        """Retorna o tipo da solicitação"""
        if self.request_type == REQUEST_TYPE_SCHEDULE:
            if self.portalrequestusufruct.activity.filter():
                return (
                    self.portalrequestusufruct.activity.first().configuration.get_sub_type_of_usufruct_display()
                )
        else:
            if self.request_type == REQUEST_TYPE_RETIFICATION:
                if self.portalrequestusufruct.activity.filter():
                    return f"""{self.get_request_type_display()} de
                    {self.portalrequestusufruct.activity.first().configuration.get_sub_type_of_usufruct_display()}"""
            elif self.request_type == REQUEST_TYPE_CANCELLATION:
                return f"""{self.get_request_type_display()} de
                {self.portalcancelschedule.usufruct.activity.configuration.get_sub_type_of_usufruct_display()}"""
            elif self.request_type == REQUEST_TYPE_ABSENCE:
                return TYPE_OF_LICENSE.get(self.tipo_label_afastamento())
            elif self.request_type == REQUEST_TYPE_SOLICITACAO_CREDITO_FOLGA:
                return self.get_tipo_folga
            else:
                return self.get_request_type_display()

    @property
    def get_tipo_folga(self):
        return f"Solicitação de Folga {self.pvfsolicitacaocreditofolga.get_tipo_folga_display()}"

    @property
    def type_of_usufruct_id(self):
        """Retorna o id do subtipo do usufruto"""
        if self.request_type == REQUEST_TYPE_SCHEDULE:
            if self.portalrequestusufruct.activity.filter():
                return str(
                    self.portalrequestusufruct.activity.first().configuration.sub_type_of_usufruct
                )

    @property
    def get_parcel_number(self):
        """Retorna quantas parcelas da venda da solicitação caso tenha"""
        if self.request_type in [REQUEST_TYPE_SCHEDULE, REQUEST_TYPE_RETIFICATION]:
            return self.portalrequestusufruct.parcel_number

    @property
    def acquisitive_period(self):
        """Retorna o grupo do período aquisitivo"""
        if self.request_type in [REQUEST_TYPE_SCHEDULE, REQUEST_TYPE_RETIFICATION]:
            if self.portalrequestusufruct.activity.filter():
                return str(
                    self.portalrequestusufruct.activity.first().acquisition_period.group_period
                )

    @property
    def set_custom_approver(self):
        """Retorna o aprovador da solicitação"""
        if not self.approver and self.step_current == REQUEST_STEP_APPROVER:
            return ""
        else:
            if self.approver != None:
                return self.approver.pessoa_fisica.nome
            else:
                if self.status == STS_EFFECTIVE:
                    return ""
                else:
                    return self.get_step_current_display()

    @property
    def have_substitute(self):
        """Retorna se a solicitação tem substituto"""
        return self.portal_request_substitute.exists()

    @property
    def request_effective_or_canceled(self):
        """Retorna se a solicitação é cancelavel pelo requisitante"""
        if self.employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
            if self.portal_request_type == PORTAL_CUMULATIVE_EXERCISE_TYPE:
                if self.step_current not in [
                    REQUEST_STEP_DGP,
                    REQUEST_STEP_STAND,
                ] or self.status in [
                    STS_EFFECTIVE,
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]:
                    return False
                else:
                    return True

            if self.belongs_superior_administration():
                if self.step_current not in [
                    REQUEST_STEP_APPROVER,
                    REQUEST_STEP_PGJ,
                    REQUEST_STEP_CORREGEDORIES_ADVISORY,
                    REQUEST_STEP_EFETIVACAO_AUTOMATICA,
                ] or self.status in [
                    STS_EFFECTIVE,
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]:
                    return False
                else:
                    return True
            else:
                if self.step_current not in [
                    REQUEST_STEP_CORREGEDORIES_ADVISORY,
                    REQUEST_STEP_APPROVER,
                    REQUEST_STEP_EFETIVACAO_AUTOMATICA,
                ] or self.status in [
                    STS_EFFECTIVE,
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]:
                    return False
                else:
                    return True
        else:
            if self.status in [
                STS_EFFECTIVE,
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]:
                return False
            else:
                return True

    @property
    def start_date_absence(self):
        """Retorna a data início do afastamento/licença"""
        if self.request_type == REQUEST_TYPE_ABSENCE:
            return self.portalrequestabsence.start_date.strftime("%d/%m/%Y")

    @property
    def end_date_absence(self):
        """Retorna a data fim do afastamento/licença"""
        if self.request_type == REQUEST_TYPE_ABSENCE:
            return self.portalrequestabsence.end_date.strftime("%d/%m/%Y")

    @property
    def get_degree_kinship(self):
        """Retorna o grau de parentesco familiar em tratamento saúde em pessoa da família"""
        if self.request_type == REQUEST_TYPE_ABSENCE:
            if self.portalrequestabsence.type == TYPE_HEALTH_FAMILY_DESEASE:
                return (
                    self.portalrequestabsence.familyhealthtreatmentabsence.degree_kinship
                )

    @property
    def get_dependent(self):
        if self.request_type == REQUEST_TYPE_ABSENCE:
            if hasattr(self.portalrequestabsence, "maternityabsence") or hasattr(
                self.portalrequestabsence, "paternityabsence"
            ):
                return eval(
                    "self.portalrequestabsence"
                    + CLASS_ABSENCE[self.portalrequestabsence.type]
                    + ".dependent.id"
                )

    @property
    def get_dependent_type(self):
        if self.request_type == REQUEST_TYPE_ABSENCE:
            if hasattr(self.portalrequestabsence, "maternityabsence") or hasattr(
                self.portalrequestabsence, "paternityabsence"
            ):
                return eval(
                    "self.portalrequestabsence"
                    + CLASS_ABSENCE[self.portalrequestabsence.type]
                    + ".dependent_type"
                )

    @property
    def get_family_bond(self):
        if self.request_type == REQUEST_TYPE_ABSENCE:
            if hasattr(self.portalrequestabsence, "mourningabsence"):
                return self.portalrequestabsence.mourningabsence.family_bond

    @property
    def get_person(self):
        if self.request_type == REQUEST_TYPE_ABSENCE:
            if hasattr(self.portalrequestabsence, "mourningabsence"):
                return self.portalrequestabsence.mourningabsence.person.id

    @property
    def get_reference_month(self):
        if hasattr(self, "sendingtimesheet"):
            return self.sendingtimesheet.reference_month
        elif hasattr(self, "sendingtelework"):
            return self.sendingtelework.reference_month

    @property
    def get_reference_year(self):
        if hasattr(self, "sendingtimesheet"):
            return self.sendingtimesheet.reference_year
        elif hasattr(self, "sendingtelework"):
            return self.sendingtelework.reference_year

    @property
    def get_current_work_plan_start_date(self):
        if hasattr(self, "sendingtelework"):
            return self.sendingtelework.work_plan.data_inicio.strftime("%d/%m/%Y")
        if hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho"):
            return self.pvfsolicitacaodesbloqueioteletrabalho.plano_teletrabalho.data_inicio.strftime(
                "%d/%m/%Y"
            )
        return None

    @property
    def get_current_work_plan_end_date(self):
        if hasattr(self, "sendingtelework"):
            if self.sendingtelework.work_plan.data_fim:
                return self.sendingtelework.work_plan.data_fim.strftime("%d/%m/%Y")
        if hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho"):
            if self.pvfsolicitacaodesbloqueioteletrabalho.plano_teletrabalho.data_fim:
                return self.pvfsolicitacaodesbloqueioteletrabalho.plano_teletrabalho.data_fim.strftime(
                    "%d/%m/%Y"
                )
        return None

    @property
    def get_lotacao_teletrabalho(self):
        if hasattr(self, "sendingtelework"):
            if self.sendingtelework.work_plan.lotacao:
                return self.sendingtelework.work_plan.lotacao.lotacao.nome
        elif hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho"):
            if self.pvfsolicitacaodesbloqueioteletrabalho.plano_teletrabalho.lotacao:
                return (
                    self.pvfsolicitacaodesbloqueioteletrabalho.plano_teletrabalho.lotacao.lotacao.nome
                )
        return None

    @property
    def get_plan_work_id(self):
        if hasattr(self, "sendingtelework"):
            return self.sendingtelework.work_plan.pk
        return None

    @property
    def daily_workload(self):
        job_position = self.get_config_job_position()
        if job_position:
            if job_position.workload == 25:
                return 5
        return 6

    @property
    def get_last_working_day_month(self):
        if hasattr(self, "sendingtimesheet") and self.status == STS_STAND_BY:
            data_current = date.today()
            last_month_date = self.last_working_day_month()
            if data_current >= last_month_date:
                return True
        return False

    @property
    def get_approver_vdf_str(self):
        try:
            return self.get_immediate_boss(self.employee).pessoa_fisica.nome
        except:
            log.error("Aprovador não encontrado.")

    def get_config_job_position(self):
        job_position = self.employee.job_position()
        if job_position:
            return job_position.cargo.configs.last()

    def tipo_label_afastamento(self):
        if self.portalrequestabsence.type == TYPE_HEALTH_FAMILY_DESEASE:
            return (
                self.portalrequestabsence.familyhealthtreatmentabsence.tipo_label_lincenca
            )
        return self.portalrequestabsence.type

    @classmethod
    def is_workplan(cls):
        """
        Função que verifica se o servidor tem plano de trabalho ativo
        """
        date_current = datetime.today().date()
        work_plan = MovimentacaoTeletrabalho.objects.filter(
            Q(servidor=employee_from_user(get_current_user())),
            Q(data_fim__isnull=True)
            | Q(data_fim__isnull=False) & Q(data_fim__gte=date_current),
        )

        if work_plan:
            return True
        return False

    def get_return_approver(self):
        if hasattr(self, "approveserverduty"):
            return self.approveserverduty.duty.owner

    def has_substitute(self, substitutes):
        """Verifica se a solicitação tem substituto.
        Parameters:
            substitutes: substitutos.

        Returns:
            True ou False.
        """
        if substitutes:
            if substitutes["substitutes"]:
                return True
            else:
                return False
        return False

    def all_indemnified(self, activitys):
        """Verifica se a solicitação é totalmente indenizada.
        Parameters:
            activitys: atividades.

        Returns:
            True ou False.
        """
        if activitys:
            for activity in activitys:
                if activity.usufructs.filter(start_date__isnull=False):
                    return False
            return True

        return False

    def part_indemnified(self, activitys):
        """Verifica se a solicitação tem alguma venda.
        Parameters:
            activitys: atividades.

        Returns:
            True ou False.
        """
        if activitys:
            for activity in activitys:
                if activity.usufructs.filter(start_date__isnull=True):
                    return True
            return False

        return False

    def get_activitys(self):
        """retorna as atividades da solicitação caso tenha"""
        if self.request_type in [REQUEST_TYPE_SCHEDULE, REQUEST_TYPE_RETIFICATION]:
            return self.portalrequestusufruct.activity.all()
        else:
            return None

    def belongs_superior_administration(self):
        """retorna se o servidor é do grupo da administração superior"""
        for group in self.employee.user.groups.all():
            if group.name == GROUPS_PVF["AS"]:
                return True
        return False

    def solicitacao_venda_plantao(self):
        return (
            not self.book_usufructs
            and self.sale_usufructs
            and e_plantao_compensatoria(self.sub_type_usufruct_id)
        )

    def efetivacao_venda_plantao(self):
        return (
            self.status == STS_EFETIVACAO_AUTOMATICA
            and self.portal_request_type
            in [
                PORTAL_FORENSIC_RECESS_TYPE,
                PORTAL_SERVER_SHIFT_TYPE,
                PORTAL_COMP_CLEARANCE_MEMBERS_TYPE,
                PORTAL_COMP_VACATION_MEMBERS_TYPE,
            ]
        )

    def set_group_history(self):
        """retorna o grupo conforme o step da solicitação"""
        if self.step_current == REQUEST_STEP_DG:
            return GROUP_DG
        elif self.step_current == REQUEST_STEP_DGP:
            if self.employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
                return GROUP_MEMBER
            else:
                return GROUP_SERVER
        elif self.step_current == REQUEST_STEP_CORREGEDORIES_ADVISORY:
            return GROUP_ASS_COGER
        elif self.step_current == REQUEST_STEP_CORREGEDORATION:
            return GROUP_COGER
        elif self.step_current == REQUEST_STEP_PGJ:
            return GROUP_PGJ
        elif self.step_current == REQUEST_STEP_JURIDICAL_ADVISORY_1:
            return GROUP_ASS_JUR_1
        elif self.step_current == REQUEST_STEP_PROG_DG:
            return GROUP_PROG_DG
        elif self.step_current == REQUEST_STEP_JURIDICAL_ADVISORY_2:
            return GROUP_ASS_JUR_2
        elif self.step_current == REQUEST_STEP_GER_DEV:
            return GROUP_GER_DEV
        elif self.step_current == REQUEST_STEP_SUB_ADM:
            return GROUP_SUB_ADM
        else:
            return None

    def get_substitute_approver(self, substitutes):
        """retorna o aprovador 'substituto'"""
        if not self.step_current:
            return Servidor.objects.get(pk=substitutes["substitutes"][0]["substitute"])
        science_ids = self.portalrequesthistory_set.filter(
            action=REQUEST_ACT_SCIENCE
        ).values_list("user__servidor__pk", flat=True)
        science_ids = list(science_ids)
        science_ids.append(get_current_user().servidor.pk)

        substitute = self.portal_request_substitute.exclude(
            substitute__pk__in=set(science_ids)
        )
        if substitute:
            return substitute.first().substitute
        else:
            return None

    def upper_capacity(self, employee):
        """
        Busca a lotação atual do servidor ou lotação superior se for responsável pela lotação atual
        """
        employee_capacity = ServidorLotacao.objects.filter(
            servidor__matricula=employee.matricula, designacao=False, ativo=True
        )
        if employee_capacity:
            upper_capacity = employee_capacity.first().lotacao
            if upper_capacity.responsavel == employee:
                return upper_capacity.pai
            return upper_capacity
        else:
            raise Exception("Não foi possível encontrar a lotação do servidor.")

    def validate_cancel_absence(self):
        """
        Retorna True se o afastamento relacionado à requisição PortalRequestAbsence estiver cancelado
        ou retorna False se não for o caso
        """
        if hasattr(self, "portalrequestabsence"):
            if self.portalrequestabsence.absence:
                return (
                    True
                    if self.portalrequestabsence.absence.estado == CANCELADO
                    else False
                )
        return False

    def get_current_capacity(self, employee):
        """Retorna a lotação do atual servidor"""
        employee_capacity = ServidorLotacao.objects.filter(
            servidor__matricula=employee.matricula, designacao=False, ativo=True
        )
        if employee_capacity:
            capacity = employee_capacity.first().lotacao
            return capacity
        else:
            raise Exception("Não foi possível encontrar a lotação do servidor.")

    def get_portal_approver(self, employee):
        """checa se o servidor é responsável pela lotação e se possui aprovador portal"""
        capacity = self.get_current_capacity(employee)
        if capacity.portal_approver and capacity.responsavel == employee:
            return True
        else:
            return False

    def get_portal_approver_capacity(self, employee):
        """Retorna True se encontrar uma lotação superior com aprovador portal"""
        portal_approver = False
        if self.get_portal_approver(employee):
            capacity = self.get_current_capacity(employee).pai
            while not portal_approver:
                if capacity:
                    if capacity.portal_approver:
                        portal_approver = True
                    else:
                        if capacity.pai:
                            stocking_dad = capacity.pai
                            capacity = stocking_dad
                        else:
                            break
                else:
                    break

        return portal_approver

    def get_aprovador_teletrabalho(self, servidor):
        """
        Método que retorna o aprovador da solicitação de teletrabalho.
        Args:
        - servidor
        Returns:
            Aprovador(Servidor).
        """
        mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            servidor=servidor, ativo=True
        ).last()
        if mov_teletrabalho and mov_teletrabalho.aprovador:
            return mov_teletrabalho.aprovador
        else:
            return servidor.chefe_imediato

    def get_aprovador_plantao(self):
        """
        Método que retorna o aprovador da solicitação de plantão.

        Returns:
            Aprovador(Servidor).
        """
        if hasattr(self, "approveserverduty"):
            return self.approveserverduty.duty.owner
        return self.duty.owner

    def get_aprovador(self, servidor, lotacao_atual, lotacao_superior):
        """
        Método que retorna o aprovador da solicitação.
        Args:
        - servidor
        - lotacao_atual (Lotacao do servidor)
        - lotacao_superior (Lotacao superior da lotação atual)
        Returns:
            Aprovador(Servidor).
        """
        if (
            servidor.chefe_imediato
            and lotacao_atual.responsavel != servidor.chefe_imediato
        ):
            if servidor.chefe_imediato.afastamento_ativo():
                if servidor.chefe_imediato.substitutions():
                    return servidor.chefe_imediato.substitutions().first().servidor
                else:
                    return servidor.chefe_imediato
            else:
                return servidor.chefe_imediato
        else:
            resposavel_lotacao = None
            while not resposavel_lotacao:
                if (
                    lotacao_superior.responsavel
                    and lotacao_superior.portal_approver
                    and lotacao_superior.responsavel != servidor
                ):
                    resposavel_lotacao = lotacao_superior.responsavel
                else:
                    if lotacao_superior.pai:
                        lotacao_pai = lotacao_superior.pai
                        lotacao_superior = lotacao_pai
                    else:
                        break

            if not resposavel_lotacao:
                raise Exception(
                    "Não foi possível encontrar um aprovador. Entre em contato com o DGP."
                )

            if resposavel_lotacao.afastamento_ativo():
                if resposavel_lotacao.substitutions():
                    return resposavel_lotacao.substitutions().first().servidor
                else:
                    return resposavel_lotacao
            else:
                return resposavel_lotacao

    def get_immediate_boss(self, employee):
        """
        Método que retorna o aprovador da solicitação ( busca recursivamente pela
          lotação servidor).
        Args:
        - employee
        Returns:
            Aprovador(Servidor).
        """
        upper_capacity = self.upper_capacity(employee)
        current_capacity = self.get_current_capacity(employee)

        if self.request_type in [
            REQUEST_TYPE_TELEWORK,
            REQUEST_TYPE_CANCELAMENTO_TELETRABALHO,
        ]:
            return self.get_aprovador_teletrabalho(employee)
        elif self.request_type in [REQUEST_TYPE_SERVER_DUTY]:
            return self.get_aprovador_plantao()
        else:
            return self.get_aprovador(employee, current_capacity, upper_capacity)

    def return_action_pending(self):
        from rh.registerpoint.utils.ponto import total_faltas_e_saldo_periodo

        employee = Servidor.objects.get(pk=self.employee.id)
        month = self.sendingtimesheet.reference_month
        year = self.sendingtimesheet.reference_year
        lack, balance = total_faltas_e_saldo_periodo(month, year, employee)
        justifications = self.sendingtimesheet.pvf_request_justification.filter(
            reason_type__in=Choice.objects.filter(
                name="TYPE_OF_REASON_PENDING"
            ).values_list("value", flat=True)
        )
        if self.status == STS_WAI_EFFECTIVENESS:
            return REQUEST_ACT_EFFECTIVENESS
        elif lack > 0 or balance < timedelta(0) or len(justifications) > 0:
            return REQUEST_ACT_DEFER

        return REQUEST_ACT_AUTOMATIC_APPROVER

    def get_action_type(self):
        if hasattr(self, "sendingtimesheet"):
            return self.return_action_pending()
        if hasattr(self, "sendingtelework"):
            return REQUEST_ACT_APPROVER
        return REQUEST_ACT_DEFER

    def _pop_before_save(self, **kwargs):
        dict_keys = kwargs.copy()
        for key in dict_keys:
            kwargs.pop(key)
        return kwargs

    def validar_status(self):
        if self.status in [
            STS_CANCELED_APPLICANT,
            STS_REJECTED,
            STS_CANCELED_DGP,
            STS_EFFECTIVE,
        ]:
            raise Exception(
                f"Ação inválida! Solicitação nº {self.pk} foi efetivada/cancelada."
            )

        return True

    def validar_permissao(self):
        employee = employee_from_user(get_current_user())
        if (
            not self.step_current in group_list(employee)
            and self.approver != employee
            and self.status != STS_EFETIVACAO_AUTOMATICA
        ):
            raise Exception(
                f"""Ação inválida! Não tem a permissão para deferir solicitação
                com a situação {self.get_status_display()}."""
            )
        return True

    def criar_progressao(self, publicacao):
        if hasattr(self, "portalrequestprogressionh"):
            prph = PortalRequestProgressionH.objects.get(pk=self.pk)
            prph.progression.forward_h(publicacao, prph)

    def efetivar_deferir(self, tipo_acao, publicacao, observation=None):
        if self.status == STS_EFFECTIVE:
            if tipo_acao not in [
                REQUEST_ACT_AUTOMATIC_APPROVER,
                REQUEST_ACT_APPROVER,
                REQUEST_ACT_EFETIVACAO_AUTOMATICO,
            ]:
                tipo_acao = REQUEST_ACT_EFFECTIVENESS
                self.effectived(publicacao, observation=observation)
            elif tipo_acao == REQUEST_ACT_APPROVER and hasattr(self, "sendingtelework"):
                self.sendingtelework.efetivar_teletrabalho()
            elif tipo_acao == REQUEST_ACT_EFETIVACAO_AUTOMATICO:
                self.effectived(publicacao, observation=observation)

        return tipo_acao

    def effectived(self, publication, observation=None):
        """
        Rotina que efetiva uma solicitação
        """
        if hasattr(self, "portalrequestusufruct"):
            if hasattr(self.portalrequestusufruct, "portalretificationschedule"):
                self.portalrequestusufruct.portalretificationschedule.effectived_retification()
            else:
                self.portalrequestusufruct.effectived_usufruct()
        elif hasattr(self, "portalrequestworkload"):
            self.portalrequestworkload.effectived_workload()
        elif hasattr(self, "portalcancelschedule"):
            self.portalcancelschedule.effectived_cancel()
        elif hasattr(self, "portalrequestabsence"):
            self.portalrequestabsence.effectived_absence(publication)
        elif hasattr(self, "approveserverduty"):
            self.approveserverduty.effectived_duty()
        elif hasattr(self, "pvfcancelamentoteletrabalho"):
            self.pvfcancelamentoteletrabalho.efetivar_cancelamento()
        elif hasattr(self, "pvfsolicitacaocreditofolga"):
            self.pvfsolicitacaocreditofolga.efetivar()
        elif hasattr(self, "pvfsolicitacaocreditodispensaeleitoral"):
            self.pvfsolicitacaocreditodispensaeleitoral.efetivar()
        elif hasattr(self, "pvfsolicitacaoauxiliocrechedepenir"):
            self.pvfsolicitacaoauxiliocrechedepenir.efetivar()
        elif hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho"):
            self.pvfsolicitacaodesbloqueioteletrabalho.efetivar(observation)

    def rejected(self, data={}, observation=None):
        """
        Rotina que indefere uma solicitação
        """
        if hasattr(self, "portalrequestusufruct"):
            if hasattr(self.portalrequestusufruct, "portalretificationschedule"):
                self.portalrequestusufruct.portalretificationschedule.rejected_retification()
            else:
                self.portalrequestusufruct.rejected_usufruct()
        elif hasattr(self, "pvfexerciciocumulativo"):
            self.pvfexerciciocumulativo.cancelar()
        elif hasattr(self, "pvfsolicitacaodesbloqueioteletrabalho") and data:
            self.pvfsolicitacaodesbloqueioteletrabalho.indeferir(data, observation)

    def get_classe(self):
        if hasattr(self, "pvfexerciciocumulativo"):
            return PVFExercicioCumulativo
        return PortalRequest

    @classmethod
    def homologar_indeferir(cls, request, data):
        """
        Função que realiza as operações do fluxo de aprovação
        (deferir, indeferir, efetivar, cancelar, ciência e anotar)
        """
        observation = data.get("observation", None)
        action = data.get("action")

        if action == "defer":
            request.defered(data)
        elif action == "deny":
            request.denyed(data)
        elif action == "science":
            request.science(observation, user=get_current_user())
        elif action == "annotation":
            request.annoted(data)
        elif action == "dgp_observation":
            request.dgp_annoted_observation(observation)
        elif action == "return_applicant":
            request.return_applicant(observation)
        elif action == "return_approver":
            request.return_approver(observation)
        elif action == "cancel":
            request.cancel(
                observation=observation, status=STS_CANCELED_DGP, validate=False
            )
        elif action == "send_sub":
            request.enviar_sub(data)

    def defered(self, data):
        observation = data.get("observation", None)
        publication = data.get("publication", None)
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                user = data.get("usuario_job", get_current_user())
                action_type = data.get("acao_efetivar", self.get_action_type())
                self.criar_progressao(publication)
                group = self.set_group_history()
                self.approval_flow(activitys=self.get_activitys(), action=action_type)
                self.save()
                action_type = self.efetivar_deferir(
                    action_type, publication, observation=observation
                )
                anexos = [
                    File.objects.get(pk=anexo_id) for anexo_id in data.get("anexos", [])
                ]
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=user,
                    anexos=anexos,
                )
                if (
                    self.request_type == REQUEST_TYPE_POINT_SHEET
                    and self.status == STS_EFFECTIVE
                ):
                    # CRIA PENDÊNCIAS DO FOLHA PONTO
                    create_data_point_sheet(self)

        except Exception as e:
            log.error(e)
            raise Exception(e)

    def denyed(self, data):
        observation = data.get("observation", None)
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                action_type = data.get("acao_indeferir", REQUEST_ACT_INDEFER)
                group = self.set_group_history()
                self.status = STS_REJECTED
                self.save()
                self.rejected(data=data, observation=observation)
                anexos = [
                    File.objects.get(pk=anexo_id) for anexo_id in data.get("anexos", [])
                ]
                if data.get("teletrabalho_desbloqueio_anexo_id"):
                    anexos.append(
                        File.objects.get(
                            pk=data.get("teletrabalho_desbloqueio_anexo_id")
                        )
                    )
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=data.get("usuario_job", get_current_user()),
                    anexos=anexos,
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def science(self, observation, user=get_current_user()):
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                action_type = REQUEST_ACT_SCIENCE
                group = self.set_group_history()
                self.approval_flow(activitys=self.get_activitys())
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=user,
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def annoted(self, data):
        observation = data.get("observation", None)
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                action_type = REQUEST_ACT_ANNOTATION
                group = self.set_group_history()
                self.approval_flow(activitys=self.get_activitys())
                self.save()
                anexos = [
                    File.objects.get(pk=anexo_id) for anexo_id in data.get("anexos", [])
                ]
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                    anexos=anexos,
                )
        except Exception as e:
            raise Exception(e)

    def dgp_annoted_observation(self, observation):
        try:
            with transaction.atomic():
                action_type = REQUEST_ACT_ANNOTATION
                group = self.set_group_history()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def return_applicant(self, observation):
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                action_type = REQUEST_ACT_RETURN_APPLICANT
                group = self.set_group_history()
                self.approval_flow(action=action_type)
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def return_approver(self, observation):
        try:
            with transaction.atomic():
                self.validar_status()
                self.validar_permissao()
                action_type = REQUEST_ACT_RETURN_APPROVER
                group = self.set_group_history()
                self.approval_flow(action=action_type)
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def cancel(self, observation=None, status=None, validate=True):
        try:
            if validate:
                self.validate_cancel_requisition()
            with transaction.atomic():
                action_type = REQUEST_ACT_CANCEL
                group = self.set_group_history()
                self.status = status
                self.save()
                self.rejected()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
                cancelar_justificativas_request(self)
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def send(self, observation=None):
        try:
            with transaction.atomic():
                self.validade_last_working_day_month()
                action_type = REQUEST_ACT_SOLICITATION
                group = self.set_group_history()
                self.approval_flow()
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def enviar_sub(self, data):
        observation = data.get("observation", None)
        try:
            with transaction.atomic():
                action_type = REQUEST_ACT_SEND_SUB
                group = self.set_group_history()
                self.approval_flow(action=action_type)
                self.save()
                anexos = [
                    File.objects.get(pk=anexo_id) for anexo_id in data.get("anexos", [])
                ]
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                    anexos=anexos,
                )
        except Exception as e:
            log.error(e)
            raise Exception(e)

    def fluxo_aprovacao_usufrutos_afastamentos(self, substitutos, atividades):
        """
        Função que realiza as ações do fluxo da solicitações de usufrutos e afastamentos
        Args:
        - substitutos (list)
        - atividades (list)
        """
        if self.solicitacao_venda_plantao() or self.efetivacao_venda_plantao():
            SolicitacaoVendaPlantaoFlow.approval_flow(self)
        elif self.belongs_superior_administration():
            ManagerApprovalFlow.approval_flow(self, substitutos)
        elif self.employee.type_by_possession in ["MBR", "MEC", "MEL", "MCM"]:
            total_venda = self.all_indemnified(atividades)
            parcial_venda = self.part_indemnified(atividades)
            MemberApprovalFlow.approval_flow(
                self, substitutos, total_venda, parcial_venda
            )
        elif self.employee.type_by_possession in ["EST", "RES"]:
            InternApprovalFlow.approval_flow(self)
        else:
            ServerApprovalFlow.approval_flow(self)

    def fluxo_aprovacao_solicitacoes(self, acao):
        """
        Função que realiza as ações do fluxo conforme com o tipo de solicitação
        Args:
        - acao (str)
        """
        approval_class = TIPOS_FLUXO_APROVACAO_NAO_USUFRUTOS_AFASTAMENTOS.get(
            self.request_type
        )
        if approval_class:
            if self.request_type in TIPO_SOLICITACAO_APROVACAO_SEM_ACAO:
                approval_class.approval_flow(self)
            else:
                approval_class.approval_flow(self, acao)

    def approval_flow(self, substitutes=None, activitys=None, action=None):
        if self.request_type in TIPOS_SOLICITACOES_USUFRUTOS_AFASTAMENTO:
            self.fluxo_aprovacao_usufrutos_afastamentos(substitutes, activitys)
        else:
            self.fluxo_aprovacao_solicitacoes(action)

    def validate_cancel_requisition(self):
        if not self.request_effective_or_canceled:
            raise Exception(
                "Somente solicitações Em Andamento podem ser canceladas pelo solicitante."
            )

    def validate_start_date_greater_end_date(self, start_date, end_date):
        """Valida se data início é menor ou igual a data fim"""
        if start_date > end_date:
            raise Exception("Data Início deve ser menor ou igual a Data Fim.")
        return True

    def validate_usufruct_conflict(self, start_date, end_date, employee, modifieds=[]):
        """Valida se existe um usufruto marcado para a mesma data"""
        usufructs = (
            Usufruct.objects.filter(
                Q(activity__acquisition_period__employee=employee),
                Q(start_date__range=[start_date, end_date])
                | Q(end_date__range=[start_date, end_date])
                | Q(start_date__lte=start_date) & Q(end_date__gte=end_date),
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                ]
            )
            .exclude(pk__in=modifieds)
        )
        if usufructs:
            raise Exception(
                f""" O periodo informado conflita com os dias de usufrutos programados/solicitados abaixo:\n
              {usufructs.first().activity.configuration.get_sub_type_of_usufruct_display()}
              {usufructs.first().start_date.strftime("%d/%m/%Y")} - {usufructs.first().end_date.strftime("%d/%m/%Y")}. """
            )
        else:
            return True

    def validate_absence_conflict(self, start_date, end_date, employee, modifieds=[]):
        absence = (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor=employee),
                Q(data_inicio__range=[start_date, end_date])
                | Q(data_fim__range=[start_date, end_date])
                | Q(data_inicio__lte=start_date) & Q(data_fim__gte=end_date),
            )
            .exclude(estado__in=[CANCELADO])
            .exclude(dayoff_usufructs__pk__in=modifieds)
            .exclude(~Q(afastamento__afastamentoestudar=None))
            .exclude(
                dayoff_usufructs__status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                ]
            )
        )
        request_absence = (
            PortalRequestAbsence.objects.filter(
                Q(employee=employee),
                Q(start_date__range=[start_date, end_date])
                | Q(end_date__range=[start_date, end_date])
                | Q(start_date__lte=start_date) & Q(end_date__gte=end_date),
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            .exclude(absence__isnull=False)
        )
        if absence or request_absence:
            start_date = (
                absence.first().data_inicio
                if absence
                else request_absence.first().start_date
            )
            end_date = (
                absence.first().data_fim
                if absence
                else request_absence.first().end_date
            )
            title_absence = (
                TYPE_OF_LICENSE.get(absence.first().tipo)
                if absence
                else TYPE_OF_LICENSE.get(request_absence.first().type)
            )
            raise Exception(
                f""" O periodo informado conflita com os dias de afastamento agendados/solicitados abaixo:
              {title_absence} {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}. """
            )
        return True

    def validate_substitute_conflict_period(self, start_date, end_date, employee):
        mov_substitutes = MovimentacaoSubstituicao.objects.filter(
            Q(servidor=employee),
            Q(data_inicio__range=[start_date, end_date])
            | Q(data_fim__range=[start_date, end_date])
            | Q(data_inicio__lte=start_date) & Q(data_fim__gte=end_date),
        )

        request_substitutes = PortalRequestSubstitute.objects.filter(
            Q(substitute=employee),
            Q(start_date__range=[start_date, end_date])
            | Q(end_date__range=[start_date, end_date])
            | Q(start_date__lte=start_date) & Q(end_date__gte=end_date),
        ).exclude(
            portal_request__status__in=[
                STS_REJECTED,
                STS_CANCELED_APPLICANT,
                STS_CANCELED_DGP,
                STS_EFFECTIVE,
            ]
        )

        if mov_substitutes or request_substitutes:
            substitute = self.get_substituto_solicitacao(
                mov_substitutes, request_substitutes
            )
            substituted = self.get_substituido_solicitacao(
                mov_substitutes, request_substitutes
            )
            raise Exception(
                f"""Não é possível efetuar a solicitação pois conflita com uma substituição:\n
            Substituto: {substitute}
            \n Substituído: {substituted}
            """
            )
        return True

    def validate_conflict_dependent_ir_childcare(self, dependent):
        dependent_child = Dependente.objects.filter(
            pessoa_fisica__pk=dependent.pk,
            dependencias__tipo__in=[TIPO_DEPENDENTE_IR, TIPO_DEPENDENTE_AUX_CRECHE],
        )

        if dependent_child:
            raise Exception(
                """Pessoa informada já é dependente no sistema,
                por isso não permite a seleção das opções auxílio creche e IR."""
            )

    def get_substituto_solicitacao(self, mov_substituicoes, sol_substitutos):
        if mov_substituicoes:
            return mov_substituicoes.first().servidor.pessoa_fisica
        else:
            return sol_substitutos.first().substitute.pessoa_fisica

    def get_substituido_solicitacao(self, mov_substituicoes, sol_substitutos):
        if mov_substituicoes:
            return f"""{mov_substituicoes.first().servidor_substituido.pessoa_fisica} -
              {mov_substituicoes.first().afastamento.__str_restful__()}"""
        else:
            return f"""{sol_substitutos.first().portal_request.employee.pessoa_fisica} -
                  {sol_substitutos.first().portal_request.type_of_request}"""

    def validate_duty_conflict(self, start_date, end_date, employee):
        duties = ShiftManager.objects.filter(
            Q(employee=employee),
            Q(start_date__range=[start_date, end_date])
            | Q(end_date__range=[start_date, end_date])
            | Q(start_date__lte=start_date) & Q(end_date__gte=end_date),
        ).exclude(
            server_duty__status__in=[
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )
        if duties:
            start_date = duties.first().start_date
            end_date = duties.first().end_date
            owner = duties.first().owner
            raise Exception(
                f"""Usufruto conflita com o plantão agendado para ({start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}).\n
             Caso deseje cancelar o plantão, entre em contato com {owner.pessoa_fisica.nome}.\n
             Mais dúvidas, entre em contato com o Departamento de Gestão de Pessoas. """
            )
        return True

    def validade_last_working_day_month(self):
        if hasattr(self, "sendingtimesheet"):
            if not self.get_last_working_day_month:
                raise Exception(
                    """O envio da folha ponto pode ser realizado somente após o último dia útil do mês.<br>
                    Para calculo do último dia útil, o sistema considera os fériados, finais de semana,
                    afastamentos e usufrutos como férias. """
                )
        return True

    def last_working_day_month(self):
        data_reference = datetime.strptime(
            f"{str(self.sendingtimesheet.reference_year)}-{str(self.sendingtimesheet.reference_month)}-01",
            "%Y-%m-%d",
        ).date()
        last_month_date = data_reference.replace(
            day=monthrange(data_reference.year, data_reference.month)[1]
        )
        for i in range(30):
            out_days = NonWorkingDay.objects.filter(
                start_date__lte=last_month_date, end_date__gte=last_month_date
            )
            absence_days = BaseLicencaAfastamento.objects.filter(
                servidor=self.employee,
                data_inicio__lte=last_month_date,
                data_fim__gte=last_month_date,
            ).exclude(estado__in=[CANCELADO])
            if (
                not out_days
                and not absence_days
                and last_month_date.weekday() not in (5, 6)
            ):
                break
            else:
                last_month_date = last_month_date - relativedelta(days=1)

        return last_month_date

    def interval_dates(self, start_date, end_date):
        import datetime

        date_generated = [
            start_date + datetime.timedelta(days=x)
            for x in range(0, (end_date - start_date).days + 1)
        ]
        return date_generated

    @classmethod
    def telework_pending(cls):
        employee = employee_from_user(get_current_user())
        mov_telework = MovimentacaoTeletrabalho.objects.filter(servidor=employee).last()
        if mov_telework:
            if mov_telework.data_fim:
                if (
                    SendingTelework.objects.filter(
                        employee=employee,
                        reference_year=mov_telework.data_fim.year,
                        reference_month=mov_telework.data_fim.month,
                    )
                    .exclude(
                        status__in=[
                            STS_REJECTED,
                            STS_CANCELED_DGP,
                            STS_CANCELED_APPLICANT,
                            STS_STAND_BY,
                        ]
                    )
                    .exclude(cancelado_solicitacao=True)
                    .count()
                    > 0
                ):
                    return False
                else:
                    return True
            else:
                return True

        return False


class PortalRequestUsufruct(PortalRequest):
    activity = models.ManyToManyField(
        "dayoff.Activity", related_name="activity_requests", verbose_name="Atividade"
    )
    parcel_number = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "PARCEL_NUMBER"),
        verbose_name="Número de Parcelas",
        blank=True,
        null=True,
    )

    def effectived_usufruct(self):
        activitys = self.portalrequestusufruct.activity.all()
        for activity in activitys:
            self.deferer_retroactive_usufructs(activity)
            activity.my_origin.authorize_and_homologate(authorize=True, note=True)
        PortalRequestSubstitute.effectived_substitute(self)

    def rejected_usufruct(self):
        activitys = self.portalrequestusufruct.activity.all().order_by("-id")
        for activity in activitys:
            self.validate_cancel_usufruct(activity)
            activity.my_origin.cancel()

    @classmethod
    def configuration_group(cls):
        """retorna as configurações dos usufrutos"""
        configurations = Configuration.objects.all()
        config = {}

        for configuration in configurations:
            if not config.get(str(configuration.sub_type_of_usufruct)):
                obj = {"sale": configuration.max_days_sale or 0}
                config[str(configuration.sub_type_of_usufruct)] = obj

        return config

    def deferer_retroactive_usufructs(self, activity):
        for usufruct in activity.usufructs.all():
            if usufruct.status in [USU_ENJOYED, USU_ENJOYING, USU_HOMOLOGATED]:
                usufruct.status = USU_NEW
                usufruct.save()

        if activity.acquisition_period.status == ACQP_FINISHED:
            try:
                AcquisitionPeriod.objects.filter(
                    pk=activity.acquisition_period.pk
                ).update(status=ACQP_PROGRESS)

            except:
                raise Exception(
                    "Não foi possível alterar o status do período aquisitivo."
                )

    @classmethod
    def set_total_days(cls, usufructs_in):
        total = 0
        for usufruct in usufructs_in["usufructs_in"]:
            total = total + usufruct["days"]
        return total

    def period_acquisition_usufruct(self, employee, type_usufruct):
        """retorna o período aquisitivo mais antigo disponível"""
        period_acquisitions = AcquisitionPeriod.objects.filter(
            Q(employee=employee),
            Q(group_period__configuration__sub_type_of_usufruct=type_usufruct),
            Q(status__in=(ACQP_PROGRESS, ACQP_INDEMNIFIED)),
            Q(end_date_fruition__gte=datetime.today().date())
            | Q(end_date_fruition=None),
            Q(days_not_booked_cache__gt=0),
        )

        if period_acquisitions:
            sorted_period_acquisition = get_period_aquisitivos_ordernados(
                period_acquisitions
            )
            return sorted_period_acquisition[-1]
        else:
            return None

    def validate_cancel_usufruct(self, activity):
        if (
            activity.status in [ACT_ST_HOMOLOGATED, ACT_ST_SOLD]
            and self.step_current != REQUEST_STEP_DGP
        ):
            raise Exception("Verifique com o DGP a situação da solicitação.")

    def validate_date(
        self,
        usufructs,
        date_request,
        type_usufruct,
        employee,
        period_acquisition,
        modifieds=[],
        validate_max_days=True,
    ):
        """
        Valida os campos de data, dias e conflitos entre os períodos marcados
        """
        if usufructs.get("usufructs_in"):
            usufructs_in = usufructs["usufructs_in"]
            for usufruct in usufructs_in:
                if usufruct["sale_usufruct"]:
                    if not usufruct["days"]:
                        raise Exception("Informe‌ ‌a ‌quantidade‌ ‌de‌ ‌dias.")
                else:
                    if not usufruct["start_date"] or not usufruct["end_date"]:
                        raise Exception(
                            "Em‌ ‌uma‌ ‌das‌ ‌programações‌ ‌informadas,‌ ‌não‌ ‌foi‌‌ informado‌ ‌início‌ ‌e/ou‌ ‌quantidade‌ ‌de‌ ‌dias."
                        )
                    else:
                        start_date = datetime.strptime(
                            usufruct["start_date"], "%d/%m/%Y"
                        ).date()
                        end_date = datetime.strptime(
                            usufruct["end_date"], "%d/%m/%Y"
                        ).date()
                        self.validate_usufruct_conflict(
                            start_date, end_date, employee, modifieds
                        )
                        self.validate_absence_conflict(
                            start_date, end_date, employee, modifieds
                        )
                        self.validate_substitute_conflict_period(
                            start_date, end_date, employee
                        )
                        self.validate_duty_conflict(start_date, end_date, employee)
                        if (
                            int(type_usufruct) == INDIVIDUAL_VACATION
                            and validate_max_days
                        ):
                            self.validate_max_enjoyment_day(
                                start_date,
                                end_date,
                                employee,
                                usufructs,
                                modifieds,
                                usufructs_in,
                            )
                        if int(type_usufruct) in [
                            INDIVIDUAL_VACATION,
                            REGULAR_VACATIONS,
                            COMP_VACATION_MEMBERS,
                            PREMIUM_LICENSE,
                        ]:
                            self.validate_close_date_period(
                                start_date, period_acquisition
                            )
                        self.validate_minimum_advance_days(
                            date_request, start_date, period_acquisition
                        )
                        self.validate_qtd_minimum_days(
                            start_date, end_date, period_acquisition
                        )
                        if int(type_usufruct) not in [
                            COMP_CLEARANCE_MEMBERS,
                        ]:
                            self.validate_previous_schedule(
                                employee,
                                type_usufruct,
                                start_date,
                                end_date,
                                period_acquisition,
                            )
                        if int(type_usufruct) in [
                            ELECTORAL_SLACK,
                            INTERNSHIP_COMPETITION,
                            COMP_CLERARANCE_SERVERS,
                            FORENSIC_RECESS,
                            COMP_CLEARANCE_MEMBERS,
                            COMP_VACATION_MEMBERS,
                            SUBSTITUTE_PROMOTER_CONTEST,
                        ]:
                            self.validate_schedule_on_weekends_and_holidays(
                                start_date, end_date, type_usufruct
                            )
        else:
            raise Exception("Adicione uma programação.")

        return True

    def config_holiday(self, usufructs, employee, modifieds):
        """Combinações permitidas a serem realizada nas férias"""

        usufruct_modified = Usufruct.objects.filter(pk__in=modifieds).values_list(
            "days"
        )
        total_days = sum([sum(x) for x in list(usufruct_modified)])
        indemnity = []
        enjoyment = []

        for usufruct in usufructs["usufructs_in"]:
            if usufruct["sale_usufruct"]:
                indemnity.append(usufruct["days"])
            else:
                enjoyment.append(usufruct["days"])

        if employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            if self.request_type is REQUEST_TYPE_RETIFICATION and not indemnity:
                total_days = sum(enjoyment)
                if total_days == 30:
                    config_holiday = CONFIG_HOLIDAY
                elif total_days == 20:
                    config_holiday = CONFIG_HOLIDAY_TWENTY
                elif total_days == 15:
                    config_holiday = CONFIG_HOLIDAY_FIFTEEN
                elif total_days == 10:
                    config_holiday = CONFIG_HOLIDAY_TEN
                else:
                    return False
            else:
                if total_days < 10 and not indemnity:
                    return True
                else:
                    config_holiday = CONFIG_HOLIDAY_MEMBER
        elif employee.type_by_possession in ["EST", "RES"]:
            dt_cut = datetime.strptime(INTERNS_CUT_DATE, "%d/%m/%Y").date()
            if employee.exercise_date < dt_cut:
                config_holiday = CONFIG_INTERNS_RECESS_BEFORE
            else:
                config_holiday = CONFIG_INTERNS_RECESS_AFTER
        else:
            if not modifieds:
                config_holiday = CONFIG_HOLIDAY
            else:
                if total_days == 30:
                    config_holiday = CONFIG_HOLIDAY
                elif total_days == 20:
                    config_holiday = CONFIG_HOLIDAY_TWENTY
                elif total_days == 15:
                    config_holiday = CONFIG_HOLIDAY_FIFTEEN
                elif total_days == 10:
                    config_holiday = CONFIG_HOLIDAY_TEN
                elif total_days < 10 and not indemnity:
                    return True
                else:
                    return False

        enjoyment.sort()
        indemnity.sort()
        for config in config_holiday:
            enjoy = config["enjoyment"]
            indem = config["indemnity"]
            enjoy.sort()
            indem.sort()
            if enjoy == enjoyment and indem == indemnity:
                return True
        return False

    def count_total_days(self, modifieds):
        usufruct_modified = Usufruct.objects.filter(pk__in=modifieds).values_list(
            "days"
        )
        total_days = sum([sum(x) for x in list(usufruct_modified)])
        return total_days

    def set_message_holiday(self, employee, modifieds, usufructs):
        if employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            return """
                Combinação de parcela(s) inválida(s).<br><br>
                Combinações válidas:<br>
                30 gozo<br>
                15 gozo + 15 gozo<br>
                20 gozo + 10 gozo<br>
                10 gozo + 10 gozo + 10 gozo<br>
                15 gozo + 15 indenizado<br>
                20 gozo + 10 indenizado<br>
                10 gozo + 10 gozo + 10 indenizado<br>
                10 gozo + 20 indenizado
            """
        elif employee.type_by_possession in ["EST", "RES"]:
            dt_cut = datetime.strptime(INTERNS_CUT_DATE, "%d/%m/%Y").date()
            if employee.exercise_date < dt_cut:
                return """
                    Combinação de parcela(s) inválida(s).<br><br>
                    Combinações válidas:<br>
                    30 gozo<br>
                    15 gozo + 15 gozo<br>
                    20 gozo + 10 gozo<br>
                    10 gozo + 10 gozo + 10 gozo<br>
                """
            else:
                return """
                    Combinação de parcela(s) inválida(s).<br><br>
                    Combinações válidas:<br>
                    12 gozo<br>
                """

        else:
            if not modifieds:
                return """
                    Combinação de parcela(s) inválida(s).<br><br>
                    Combinações válidas:<br>
                    30 gozo<br>
                    15 gozo + 15 gozo<br>
                    20 gozo + 10 gozo<br>
                    10 gozo + 10 gozo + 10 gozo<br>
                    15 gozo + 15 indenizado<br>
                    20 gozo + 10 indenizado<br>
                    10 gozo + 10 gozo + 10 indenizado
                """
            else:
                total_days = self.count_total_days(modifieds)
                if total_days == 30:
                    return """
                        Combinação de parcela(s) inválida(s).<br><br>
                        Combinações válidas:<br>
                        30 gozo<br>
                        15 gozo + 15 gozo<br>
                        20 gozo + 10 gozo<br>
                        10 gozo + 10 gozo + 10 gozo<br>
                    """
                if total_days == 20:
                    return """
                        Combinação de parcela(s) inválida(s).<br><br>
                        Combinações válidas:<br>
                        10 gozo + 10 gozo<br>
                        20 gozo<br>
                    """
                elif total_days == 15:
                    return """
                        Combinação de parcela(s) inválida(s).<br><br>
                        Combinações válidas:<br>
                        15 gozo.<br>

                    """
                elif total_days == 10:
                    return """
                        Combinação de parcela(s) inválida(s).<br><br>
                        Combinações válidas:<br>
                        10 gozo.<br>

                    """
                else:
                    return f"Quantidade de dias ({total_days}) selecionados inválido para retificação."

    def validate_qtd_days(self, period_acquisition):
        if period_acquisition and period_acquisition.days_not_booked_cache not in [30]:
            raise Exception(
                "Saldo de Férias Remanescente deverá ser solicitado via GEDOC."
            )

    def validate_config_holiday(self, usufructs, employee, modifieds=[]):
        """Valida se as combinações passadas pelo usuário são válidas"""

        config = self.config_holiday(usufructs, employee, modifieds)
        if not config:
            raise Exception(self.set_message_holiday(employee, modifieds, usufructs))
        return True

    def validate_balance_days(self, total_days, period_acquisition):
        """Valida se existe saldo para realiazar a solitação"""
        if period_acquisition:
            if int(total_days) > period_acquisition.days_not_booked_cache:
                raise Exception(
                    f"""
                    O total de programações da solicitação é superior ao total disponível no periodo aquistivo mais antigo.\n\
                    Deve-se marcar todos os dias do período aquisitivo mais antigo,\
                    para que se marque/venda dias de períodos aquisitivos mais recentes.
                    Procure o DGP para maiores informações.
                """
                )
        return True

    def validate_balance_usufruct(self, period_acquisition):
        """Valida se existe saldo para realiazar a solitação"""
        if not period_acquisition:
            raise Exception(
                "O total de programações da solicitação é superior ao total disponível no periodo aquistivo mais antigo."
            )
        return True

    def validate_close_date_period(self, start_date, period_acquisition):
        """Valida se a data do usufruto é superior a data de fechamento do periodo aquisitivo"""
        if period_acquisition:
            if period_acquisition.end_date_acquisition:
                if start_date <= period_acquisition.end_date_acquisition:
                    raise Exception(
                        "A data da programação tem que ser superior a data fim da aquisição do direito."
                    )

        return True

    def validate_previous_schedule(
        self, employee, type_usufruct, start_date, end_date, period_acquisition
    ):
        """Valida se a data da programação é superior a data última programação do último período aquisitivo
        e inferior a data da programação do período superior
        """
        days_usufruct = NewDateRange(start_date, end_date).days
        if (
            type_usufruct in [REGULAR_VACATIONS, INDIVIDUAL_VACATION]
            and days_usufruct not in COMBINACACAO_DIAS_FERIAS
        ):
            return True
        if period_acquisition and period_acquisition.group_period.year_reference:
            previous_year = period_acquisition.group_period.year_reference - 1
            senior_year = period_acquisition.group_period.year_reference + 1
            previous_usufruct = (
                Usufruct.objects.filter(
                    activity__type_of_activity__in=[ACT_BOOK, ACT_BOOK_SELL],
                    activity__acquisition_period__employee=employee,
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct=type_usufruct,
                    activity__acquisition_period__group_period__year_reference=previous_year,
                )
                .exclude(
                    status__in=[
                        USU_CANCELED,
                        USU_NOT_AUTHORIZED,
                        USU_SOLD,
                        USU_SUSPENDED,
                        USU_INTERRUPTED,
                        USU_CHANGED,
                        USU_SUBSTITUTE,
                    ]
                )
                .exclude(start_date__isnull=True)
                .order_by("-end_date")
                .first()
            )
            senior_usufruct = (
                Usufruct.objects.filter(
                    activity__type_of_activity__in=[ACT_BOOK, ACT_BOOK_SELL],
                    activity__acquisition_period__employee=employee,
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct=type_usufruct,
                    activity__acquisition_period__group_period__year_reference=senior_year,
                )
                .exclude(
                    status__in=[
                        USU_CANCELED,
                        USU_NOT_AUTHORIZED,
                        USU_SOLD,
                        USU_SUSPENDED,
                        USU_INTERRUPTED,
                        USU_CHANGED,
                        USU_SUBSTITUTE,
                    ]
                )
                .exclude(start_date__isnull=True)
                .order_by("end_date")
                .first()
            )

            if previous_usufruct:
                if self.employee.type_by_possession in ["EST", "RES"]:
                    return True
                if start_date <= previous_usufruct.end_date:
                    raise Exception(
                        "A data programação deve ser superior a data programação do período anterior."
                    )
            if senior_usufruct:
                if self.employee.type_by_possession in ["EST", "RES"]:
                    return True
                if end_date >= senior_usufruct.start_date:
                    raise Exception(
                        "A data programação deve ser inferior a data programação do período superior."
                    )
        return True

    def validate_maximum_rectification(self, employee, type_usufruct):
        """Valida do máximo de retificação com base na configuração"""
        pass

    def validate_minimum_advance_days(
        self, date_request, start_date, period_acquisition
    ):
        """Antecedencia Mínima - em dias"""
        if period_acquisition:
            configuration = period_acquisition.group_period.configuration
            days = self.diff_days(start_date, date_request)
            if configuration.days_precede_fruition:
                if (
                    configuration.days_precede_fruition < 0
                    and start_date < date_request
                ):
                    if days > abs(configuration.days_precede_fruition):
                        raise Exception(
                            f"""O máximo de dias retroativos para fruição desse usufruto é
                            {abs(configuration.days_precede_fruition)} Dia(s)"""
                        )
                else:
                    if (
                        days < configuration.days_precede_fruition
                        or start_date < date_request
                    ):
                        raise Exception(
                            f"""Antecedência mínima de dias para fruição desse usufruto é
                            {configuration.days_precede_fruition} Dia(s)"""
                        )

        return True

    def validate_qtd_minimum_days(self, start_date, end_date, period_acquisition):
        """Quantidade Minima por divisão"""
        if period_acquisition:
            configuration = period_acquisition.group_period.configuration
            days = NewDateRange(start_date, end_date).days
            if configuration.min_days_division:
                if days < configuration.min_days_division:
                    raise Exception(
                        f"""A quantidade mínima de dias que pode ser dividido o período de usufruto é de
                        {configuration.min_days_division} Dia(s)"""
                    )

        return True

    def year_indemnified(self, usufruct):
        acquisition_period = AcquisitionPeriod.objects.get(
            activities__usufructs__pk=usufruct.pk
        )
        usufructs_year = (
            Usufruct.objects.filter(
                activity__acquisition_period__pk=acquisition_period.pk
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                    USU_CHANGED,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_SUBSTITUTE,
                    USU_SOLD,
                ]
            )
            .values_list("start_date__year")
        )

        year = None
        for usu_year in usufructs_year:
            if usu_year[0]:
                if not year:
                    year = usu_year[0]
                else:
                    if year > usu_year[0]:
                        year = usu_year[0]

        return year

    def max_days_indemnified(self, employee, start_year, end_year, modifieds):
        """Retorna a quantidade de dias de venda de usufruos de férias individuais."""
        acquisition_period = AcquisitionPeriod.objects.filter(
            Q(activities__usufructs__start_date__year=start_year)
            | Q(activities__usufructs__end_date__year=end_year),
            Q(employee=employee),
            Q(group_period__configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION),
            ~Q(
                activities__usufructs__status__in=[
                    USU_CANCELED,
                    USU_CHANGED,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_SUBSTITUTE,
                ]
            ),
        ).distinct()

        usufructs = (
            Usufruct.objects.filter(
                start_date__isnull=True,
                activity__acquisition_period__pk__in=[
                    acq.pk for acq in acquisition_period
                ],
                payment_year__gte=start_year,
                payment_year__lte=end_year,
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                ]
            )
            .exclude(pk__in=modifieds)
            .distinct("pk")
        )
        year_days = {}
        for usufruct in usufructs:
            year = self.year_indemnified(usufruct)
            if year:
                if not year_days.get(year):
                    year_days[year] = usufruct.days
                else:
                    year_days[year] = year_days[year] + usufruct.days
        return year_days

    def validate_max_enjoyment_day(
        self, starte_date, end_date, employee, usufruct_days, modifieds, usufructs_in
    ):
        """Valida a quantidade máxima de dias que pode ser usufruido por ano 'Férias Individuais''"""
        year_starte_date = starte_date.year
        year_end_date = end_date.year
        usufructs = (
            Usufruct.objects.filter(
                Q(
                    activity__type_of_activity__in=[
                        ACT_BOOK_SELL,
                        ACT_RECTIFY,
                        ACT_BOOK,
                        ACT_CHANGE,
                        ACT_INTERRUPT,
                        ACT_SUSPEND,
                    ]
                ),
                Q(start_date__year=year_starte_date) | Q(end_date__year=year_end_date),
                Q(activity__acquisition_period__employee=employee),
                Q(
                    activity__acquisition_period__group_period__configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION
                ),
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_CHANGED,
                    USU_SUBSTITUTE,
                ]
            )
            .exclude(pk__in=modifieds)
        )
        usufructs_int = usufructs.filter(status__in=[USU_INTERRUPTED])
        usufructs = usufructs.exclude(status__in=[USU_INTERRUPTED])
        max_enjoy_days_year = Choice.objects.get(
            name="MAX_ENJOY_DAYS_YEAR", app_label="pvf"
        )
        qtd_days_year = self.sum_days_year(usufructs)
        qtd_days_int = self.sum_days_year(usufructs_int)
        max_days_indemnified = self.max_days_indemnified(
            employee, year_starte_date, year_end_date, modifieds
        )
        request_days = self.max_usufruct_days(usufruct_days, employee, modifieds)
        qtd_days = dict(
            Counter(qtd_days_year)
            + Counter(request_days)
            + Counter(max_days_indemnified)
            - Counter(qtd_days_int)
        )

        ano_solicitacao = ""
        for usufruct in usufructs_in:
            if usufruct["sale_usufruct"] == 0:
                ano_solicitacao = datetime.strptime(
                    usufruct["start_date"], "%d/%m/%Y"
                ).year
        for usufruct in usufructs_in:
            dias_vendidos = (
                max_days_indemnified.get(ano_solicitacao)
                if max_days_indemnified.get(ano_solicitacao)
                else 0
            )
            if usufruct["sale_usufruct"] and ((dias_vendidos + usufruct["days"]) > 40):
                raise Exception("Não é permitido vender mais de 40 dias por ano")

    def set_sale_year(self, start_date, sale_year):
        if not sale_year:
            return start_date.year
        else:
            if start_date.year < sale_year:
                return start_date.year

        return sale_year

    def max_usufruct_days(self, usufructs, employee, modifieds):
        """retorna uma a quantidade de dias da solicitação"""
        request_days = {}
        days_sale = 0
        sale_year = 0
        for usufruct in usufructs["usufructs_in"]:
            if not usufruct["sale_usufruct"]:
                start_date = datetime.strptime(
                    usufruct["start_date"], "%d/%m/%Y"
                ).date()
                end_date = datetime.strptime(usufruct["end_date"], "%d/%m/%Y").date()
                sale_year = self.set_sale_year(start_date, sale_year)
                days = self.interval_dates(start_date, end_date)
                year_days = self.count_date(days)
                request_days = dict(Counter(request_days) + Counter(year_days))
            else:
                days_sale = usufruct["days"]

        request_days[sale_year] = request_days[sale_year] + days_sale
        return request_days

    def sum_days_year(self, usufructs):
        count_days = {}
        for usufruct in usufructs:
            count = [
                x.year
                for x in self.interval_dates(usufruct.start_date, usufruct.end_date)
            ]
            count_days = dict(Counter(count) + Counter(count_days))

        return count_days

    def count_date(self, value):
        count_days = [x.year for x in value]
        return dict(Counter(count_days))

    def employee_place(self, employee):
        employee_place = ServidorLotacao.objects.filter(
            servidor__matricula=employee.matricula, designacao=False, ativo=True
        )
        if employee_place:
            return employee_place.first().lotacao.localidade_id

    def set_weekdays(self, value):
        return value.weekday()

    def validate_schedule_on_weekends_and_holidays(
        self, start_date, end_date, type_usufruct
    ):
        """Não permitir programar em finais de semana e fériados"""
        usufruct_name = Choice.objects.get(
            name="SUB_CONFIGURATION_CHOICE", app_label="dayoff", value=type_usufruct
        )
        dates = self.interval_dates(start_date, end_date)
        local_id = self.employee_place(get_current_user().servidor)
        for date in dates:
            nondays = (
                NonWorkingDay.objects.filter(
                    Q(end_date__isnull=False, start_date__lte=date, end_date__gte=date)
                    | Q(end_date__isnull=True, start_date=date)
                )
                .exclude(is_partial=True)
                .exclude(kind__in=[3, 4])  # 3=Suspensão, 4=Recesso
            )
            for nonday in nondays:
                if nonday.abrangency == ABRANGENCY_CITY:
                    if nonday.places.filter(pk=local_id).exists():
                        raise Exception(
                            f"{usufruct_name.label} não pode ser programado(a) em finais de semana e feriados."
                        )
                else:
                    raise Exception(
                        f"{usufruct_name.label} não pode ser programado(a) em finais de semana e feriados."
                    )

        list_weekdays = list(map(self.set_weekdays, dates))
        if 5 in list_weekdays or 6 in list_weekdays:
            raise Exception(
                f"{usufruct_name.label} não pode ser programado(a) em finais de semana e feriados."
            )

        return True

    def diff_days(self, start_date, end_date):
        return abs((start_date - end_date).days)

    def set_usufructs_in(self, usufructs):
        for usufructs in usufructs["usufructs_in"]:
            if not usufructs["sale_usufruct"]:
                self.book_usufructs.append(usufructs)
            else:
                self.sale_usufructs = usufructs

    def set_type_usufruct(self, type_usufruct):
        if type_usufruct:
            self.sub_type_usufruct_id = int(type_usufruct)

    def save_usufruct_sell(self, acquisition_period, modifieds):
        return ActivityBookSell.do(
            days=self.sale_usufructs["days"] if self.sale_usufructs else 0,
            acquisition_period=acquisition_period,
            usufructs_in=self.book_usufructs,
            modifieds=modifieds,
            authorize=None,
            attachment=None,
            justification=None,
            note=True,
            context=None,
        )

    def save_activitys(self, acquisition_period, modifieds=[]):
        self.validate_same_usufructs_in()
        return self.save_usufruct_sell(acquisition_period, modifieds)

    def validate_same_usufructs_in(self):
        """
        Valida se os usufrutos solicitados são iguais.
        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usufruct in self.book_usufructs:
            if self.book_usufructs.count(usufruct) > 1:
                raise Exception(
                    "Foram incluídas programações com datas coincidentes, confirme as datas das programações."
                )

        return True

    def validate_prescription(self, acquisition_period, usufructs_in, total_days):
        configurations = Configuration.objects.filter(prescription_days__gt=0)
        configurations_not_prescriptable = Configuration.objects.filter(
            prescription_days=0
        )
        msg_exception = """Não é possível solicitar a programação, pois o usufruto é posterior a prescrição
                            de parte ou todo do período aquisitivo, mais informações consulte o DGP."""
        # Verifica se tem 'Configuração de Prescrição', se há 'Anexos ativos' e 'Dias não agendados' para o  Período Aquisitivo
        if (
            acquisition_period
            and acquisition_period.group_period.configuration in configurations
            and acquisition_period.exist_active_attachment()
            and acquisition_period.days_not_booked_cache > 0
        ):

            prescription_days = (
                acquisition_period.group_period.configuration.prescription_days
            )
            usufructs = usufructs_in["usufructs_in"]
            usufructs_verified = []

            if usufructs:
                prescribed = False
                available_attachment = True
                # Para cada anexo ativo do 'Período Aquisitivo'
                active_attachment = (
                    acquisition_period.attachment_acquisitionperiod.filter(status=1)
                )

                days_for_sale = 0
                for usufruct in usufructs:
                    if usufruct["sale_usufruct"] == 1:
                        days_for_sale += usufruct["days"]
                    else:
                        # Tenta encontrar um anexo com a mesma quantidade de dias desse 'Período solicitado'
                        active_attachment_filtered = active_attachment.filter(
                            days_law=int(usufruct["days"])
                        )
                        if active_attachment_filtered:
                            if active_attachment_filtered.count() == 1:
                                attachment = active_attachment_filtered.get(
                                    days_law=int(usufruct["days"])
                                )
                            else:
                                attachment = active_attachment_filtered.first()
                            date_with_prescription = attachment.date_start + timedelta(
                                days=prescription_days
                            )

                            # Se a 'Data início' desse 'Período solicitado' é menor que a 'Data início' desse anexo
                            usufruct_start_date = datetime.strptime(
                                usufruct["start_date"], "%d/%m/%Y"
                            ).date()
                            self.validate_usufruct_start_date(
                                usufruct_start_date, attachment, prescribed
                            )
                            # Se a 'Data fim' desse 'Período solicitado' é maior que a 'Data de prescrição' desse anexo
                            usufruct_end_date = datetime.strptime(
                                usufruct["end_date"], "%d/%m/%Y"
                            ).date()
                            self.validate_usufruct_end_date(
                                usufruct_end_date, date_with_prescription, msg_exception
                            )

                            if prescribed == False:
                                active_attachment = active_attachment.exclude(
                                    pk=attachment.pk
                                )
                                usufructs_verified.append(usufruct)
                                if not usufructs:
                                    return True
                                continue
                            else:
                                raise Exception(
                                    "Não foi encontrado anexo Ativo com dias suficientes para o(s) período(s) solicitado(s)."
                                )

                total_days_enjoy = int(total_days) - days_for_sale
                # Se o total de 'Dias solicitados' é maior que 'Cache de dias não agendados'
                if total_days_enjoy > acquisition_period.days_not_booked_cache:
                    raise Exception(
                        "A quantidade de dias solicitados é maior que o saldo disponível."
                    )

                # Para cada 'Período solicitado'
                for usufruct in usufructs:
                    # Valida apenas para dias que não serão vendidos
                    if (
                        usufruct["sale_usufruct"] != 1
                        and usufruct not in usufructs_verified
                    ):
                        for attachment in active_attachment:
                            date_with_prescription = attachment.date_start + timedelta(
                                days=prescription_days
                            )
                            # Se a 'Quantidade de dias' desse 'Período solicitado' é maior que os 'Dias de direito' desse anexo
                            if int(usufruct["days"]) > attachment.days_law:
                                prescribed = True
                                available_attachment = False
                            else:
                                attachment.days_law -= int(usufruct["days"])
                                if attachment.days_law >= 0:
                                    active_attachment = active_attachment.exclude(
                                        pk=attachment.pk
                                    )
                                    continue
                                else:
                                    prescribed = True
                            # Se a 'Data início' desse 'Período solicitado' é menor que a 'Data início' desse anexo
                            usufruct_start_date = datetime.strptime(
                                usufruct["start_date"], "%d/%m/%Y"
                            ).date()
                            self.validate_usufruct_start_date(
                                usufruct_start_date, attachment, prescribed
                            )
                            # Se a 'Data fim' desse 'Período solicitado' é maior que a 'Data de prescrição' desse anexo
                            usufruct_end_date = datetime.strptime(
                                usufruct["end_date"], "%d/%m/%Y"
                            ).date()
                            self.validate_usufruct_end_date(
                                usufruct_end_date, date_with_prescription, msg_exception
                            )
                            # Remove o anexo da lista se conseguiu agendar dias nele e a quantidade de dias for maior/igual a zero (0)
                            if prescribed == False:
                                attachment.days_law -= int(usufruct["days"])
                                if attachment.days_law >= 0:
                                    active_attachment = active_attachment.exclude(
                                        pk=attachment.pk
                                    )
                                    continue
                                else:
                                    prescribed = True
                            # Valida o saldo disponível no anexo
                            self.validate_balance_attachment(
                                attachment, active_attachment, available_attachment
                            )
                            # Se chegou no último anexo e teve prescrição
                            if (
                                attachment == active_attachment.last()
                                and prescribed == True
                            ):
                                raise Exception(
                                    "Não foi encontrado anexo Ativo com dias suficientes para o(s) período(s) solicitado(s)."
                                )
        elif (
            acquisition_period
            and acquisition_period.group_period.configuration
            in configurations_not_prescriptable
        ):
            """
            Quanto o prazo para prescrição configurado for 0, considere que não vai prescrever.
            """
            pass
        else:
            raise Exception(
                "Favor verificar se há Saldo disponível, se há Anexos ativos no Período Aquisitivo e se há configuração de Prescrição."
            )

    def validate_usufruct_start_date(self, usufruct_start_date, attachment, prescribed):
        if usufruct_start_date < attachment.date_start:
            prescribed = True
        return prescribed

    def validate_usufruct_end_date(
        self, usufruct_end_date, date_with_prescription, msg_exception
    ):
        if usufruct_end_date > date_with_prescription:
            raise Exception(msg_exception)

    def validate_balance_attachment(
        self, attachment, active_attachment, available_attachment
    ):
        if attachment == active_attachment.last() and available_attachment == False:
            raise Exception(
                f"Permitido informar somente o saldo disponível no anexo. <br>Saldo do anexo: {attachment.days_law} dia(s)"
            )
        return True

    def exist_config_sale(self, configs_sale):
        if not configs_sale:
            raise Exception(
                f"Não existe Configuração de Venda disponível para a data atual. Procure o DGP para maiores informações."
            )

    def validate_cutoff_date(self, acquisition_period, config_sale):
        if acquisition_period.get_saldo_venda <= 0:
            raise Exception(
                f"""A data de término de uma ou mais folgas compensatórias do período aquisitivo {acquisition_period.group_period} ultrapassa
                  a data de corte definida na configuração de venda, que é { config_sale.cutoff_date }."""
            )

    def validate_configuration_sale(self, acquisition_period, date_request):
        configs_sale = (
            acquisition_period.group_period.configuration.configuration_sale.filter(
                Q(start_date_sale__lte=date_request, end_date_sale__isnull=True)
                | Q(start_date_sale__lte=date_request, end_date_sale__gte=date_request)
            )
        )

        self.exist_config_sale(configs_sale)
        config_sale = configs_sale.first()
        self.validate_cutoff_date(acquisition_period, config_sale)

    def validar_data_recesso_florence(self, usufrutos):

        if usufrutos:
            for usufruto in usufrutos:
                if usufruto.get("start_date"):
                    start_date = usufruto.get("start_date")
                    data_inicio = datetime.strptime(start_date, "%d/%m/%Y").date()

                    if (data_inicio.month == 12 and data_inicio.day >= 20) or (
                        data_inicio.month == 1 and data_inicio.day <= 6
                    ):
                        raise Exception(
                            "Não é permitido solicitar férias dentro do periodo de recesso de Forense."
                        )

                if usufruto.get("end_date"):
                    end_date = usufruto.get("end_date")
                    if end_date:
                        data_fim = datetime.strptime(end_date, "%d/%m/%Y").date()
                        if (data_fim.month == 12 and data_fim.day >= 20) or (
                            data_fim.month == 1 and data_fim.day <= 6
                        ):
                            raise Exception(
                                "Não é permitido solicitar férias dentro do periodo de recesso de Forense."
                            )

    def validar_data_fim_provimento_est_res(self, usufrutos):
        servidor = self.employee

        if servidor.type_by_possession in ["EST", "RES"]:

            posses = MovimentacaoPosse.objects.filter(
                servidor__matricula__exact=servidor.matricula, ativo=True
            )

            if usufrutos:
                for usufruto in usufrutos:
                    if usufruto.get("start_date"):
                        data_inicio = datetime.strptime(
                            usufruto.get("start_date"), "%d/%m/%Y"
                        ).date()

                        for posse in posses:
                            if (
                                posse.data_desligamento
                                and data_inicio > posse.data_desligamento
                            ):
                                raise Exception(
                                    "Não é permitido solicitar férias após a data de término de provimento."
                                )

                    if usufruto.get("end_date"):
                        end_date = usufruto.get("end_date")

                        if end_date:
                            data_fim = datetime.strptime(end_date, "%d/%m/%Y").date()

                            for posse in posses:
                                if (
                                    posse.data_desligamento
                                    and data_fim > posse.data_desligamento
                                ):
                                    raise Exception(
                                        "Não é permitido solicitar férias após a data de término de provimento."
                                    )

    def pre_validacao(self, params):
        """
        Método que realiza a pré validação da criação da solicitação de usufrutos
        """
        servidor = get_current_user().servidor
        data_inicio = datetime.strptime(params["data_inicio"], "%d/%m/%Y").date()
        data_fim = datetime.strptime(params["data_fim"], "%d/%m/%Y").date()
        tipo_usufruto = int(params["tipo_usufruto"])
        data_solicitacao = datetime.today().date()
        periodo_aquisitivo = self.period_acquisition_usufruct(servidor, tipo_usufruto)
        modificados = []

        self.validate_usufruct_conflict(data_inicio, data_fim, servidor, modificados)
        self.validate_absence_conflict(data_inicio, data_fim, servidor, modificados)
        self.validate_substitute_conflict_period(data_inicio, data_fim, servidor)
        self.validate_duty_conflict(data_inicio, data_fim, servidor)
        if tipo_usufruto in [
            INDIVIDUAL_VACATION,
            REGULAR_VACATIONS,
            COMP_VACATION_MEMBERS,
            PREMIUM_LICENSE,
        ]:
            self.validate_close_date_period(data_inicio, periodo_aquisitivo)
        self.validate_minimum_advance_days(
            data_solicitacao, data_inicio, periodo_aquisitivo
        )
        self.validate_qtd_minimum_days(data_inicio, data_fim, periodo_aquisitivo)
        if tipo_usufruto in [
            ELECTORAL_SLACK,
            INTERNSHIP_COMPETITION,
            COMP_CLERARANCE_SERVERS,
            FORENSIC_RECESS,
            COMP_CLEARANCE_MEMBERS,
            COMP_VACATION_MEMBERS,
            SUBSTITUTE_PROMOTER_CONTEST,
        ]:
            self.validate_schedule_on_weekends_and_holidays(
                data_inicio, data_fim, tipo_usufruto
            )
        if tipo_usufruto not in [COMP_CLEARANCE_MEMBERS]:
            self.validate_previous_schedule(
                servidor, tipo_usufruto, data_inicio, data_fim, periodo_aquisitivo
            )
        self.validate_balance_usufruct(periodo_aquisitivo)

    # TODO Alterar após implantação do novo front
    def validate(
        self,
        employee,
        type_usufruct,
        usufructs_in,
        total_days,
        date_request,
        acquisition_period,
    ):
        usufructs = usufructs_in["usufructs_in"]
        type_usufruct = int(type_usufruct)
        has_sale = False
        if usufructs:
            for usufruct in usufructs:
                if usufruct["sale_usufruct"] == 1:
                    has_sale = True
        if has_sale:
            self.validate_configuration_sale(acquisition_period, date_request)

        if type_usufruct in [
            REGULAR_VACATIONS,
            INDIVIDUAL_VACATION,
            FORENSIC_RECESS,
            ELECTORAL_SLACK,
        ]:
            self.validate_prescription(acquisition_period, usufructs_in, total_days)
        if type_usufruct in [REGULAR_VACATIONS, INDIVIDUAL_VACATION, INTERNS_RECESS]:
            if employee.type_by_possession in [
                "EFE",
                "ECM",
                "EFC",
                "CMS",
                "RCM",
                "REQ",
                "RFC",
                "REX",
            ]:
                self.validate_qtd_days(acquisition_period)
            if employee.type_by_possession in ["RES", "EST"]:
                dt_cut = datetime.strptime(INTERNS_CUT_DATE, "%d/%m/%Y").date()
                if employee.exercise_date < dt_cut:
                    self.validate_qtd_days(acquisition_period)

            self.validate_config_holiday(usufructs_in, employee)
        self.validate_date(
            usufructs_in, date_request, type_usufruct, employee, acquisition_period
        )
        self.validate_balance_usufruct(acquisition_period)
        self.validate_balance_days(total_days, acquisition_period)

        if type_usufruct in [
            RESIDENTS_RECESS,
            INTERNS_RECESS,
        ]:
            self.validar_data_recesso_florence(usufructs)
        self.validar_data_fim_provimento_est_res(usufructs)

    def save(self, *args, **kwargs):
        params = kwargs.get("params")
        # TODO Alterar após implantação do novo front
        self.validate(
            self.employee,
            params["type_usufruct"],
            params["usufructs_in"],
            params["total_days"],
            self.date,
            kwargs.get("acquisition_period"),
        )
        kwargs = self._pop_before_save()
        super(PortalRequestUsufruct, self).save(**kwargs)

    @classmethod
    def enviar_notificacao_email(self, params, usufruct_in, servidor):
        obj = {
            "success": True,
            "message": "Nada Feito",
        }

        try:
            usufruto = PortalRequestUsufruct.objects.filter(employee=servidor).first()
            data_inicio = params["usufructs_in"]["usufructs_in"][0]["start_date"]
            data_fim = params["usufructs_in"]["usufructs_in"][0]["end_date"]
            data_inicio_formatada = data_inicio.strftime("%d/%m/%Y")
            data_fim_formatada = data_fim.strftime("%d/%m/%Y")

            codigo_email = "NOTIFICACAO_SEM_SUSBTITUTO"
            email_template = EmailTemplate.objects.get(code=codigo_email)

            conteudo = (
                email_template.contents.replace(
                    "@nome@", servidor.pessoa_fisica.social_name
                )
                .replace("@cod_vdf@", str(usufruto.pk))
                .replace(
                    "@periodo_afastamento@",
                    f"{data_inicio_formatada} a {data_fim_formatada}",
                )
                .replace("@tipo@", usufruto.type_of_request)
                .replace("@periodo_aquisitivo@", usufruto.acquisitive_period)
                .replace("@data_solicitacao@", usufruto.date.strftime("%d/%m/%Y"))
            )

            lista_destinatarios = []

            config_email_item = Item.objects.get(
                key="notificacao_usufruto_sem_substituto"
            )

            lista_email = config_email_item.value.split(",")

            for email in lista_email:
                lista_destinatarios.append(
                    {
                        "email": email,
                        "nome": email.upper(),
                    }
                )

            html_content = render_to_string(
                "util/template_email.html", {"message": conteudo}
            )
            EmailNotification().send_email_default(
                lista_destinatarios, email_template.subject, html_content
            )

        except Exception as error:
            log.error(error)
            obj["success"] = False
            obj["message"] = "Erro ao tentar Enviar a Notificação por Email."

    @classmethod
    def _create_multiple_sell_request_usufruct(
        cls,
        employee,
        date_request,
        user,
        params,
        portal_request_type,
        usufructs_in,
        usufruct,
    ):
        """
        Função responsável por criar requisição de venda, em casos de soliticações de vendas múltiplas
        """
        params.update(
            {
                "usufructs_in": {
                    "usufructs_in": (usufruct,),
                },
                "total_days": usufruct.get("days"),
            }
        )
        obj = cls(
            employee=employee,
            request_type=REQUEST_TYPE_SCHEDULE,
            date=date_request,
            request=user,
            parcel_number=params["parcel_number"] if params["parcel_number"] else None,
            portal_request_type=portal_request_type,
        )
        acquisition_period = obj.period_acquisition_usufruct(
            employee, params["type_usufruct"]
        )
        obj.set_usufructs_in({"usufructs_in": (usufruct,)})
        obj.set_type_usufruct(params["type_usufruct"])
        obj.approval_flow(params["substitutes"])

        obj.save(params=params, acquisition_period=acquisition_period)

        activity = obj.save_activitys(acquisition_period)
        obj.activity.add(activity)

        PortalRequestSubstitute.create_substitute(
            substitutes=params["substitutes"],
            request=obj,
            interval_dates=usufructs_in,
            total_days=params["total_days"],
        )
        PortalRequestHistory.create_history(
            observation=params["observation"],
            action=REQUEST_ACT_SOLICITATION,
            request=obj,
            date=datetime.now(),
            group=None,
            user=user,
        )
        return obj

    @classmethod
    def _create_usufruct(
        cls, employee, date_request, user, params, portal_request_type, usufructs_in
    ):
        """
        Função responsável por criar as soliticações VDF
        """
        obj = cls(
            employee=employee,
            request_type=REQUEST_TYPE_SCHEDULE,
            date=date_request,
            request=user,
            parcel_number=params["parcel_number"] if params["parcel_number"] else None,
            portal_request_type=portal_request_type,
        )
        acquisition_period = obj.period_acquisition_usufruct(
            employee, params["type_usufruct"]
        )
        obj.set_usufructs_in(usufructs_in)
        obj.set_type_usufruct(params["type_usufruct"])
        obj.approval_flow(params["substitutes"])
        obj.save(params=params, acquisition_period=acquisition_period)

        activity = obj.save_activitys(acquisition_period)
        obj.activity.add(activity)

        PortalRequestSubstitute.create_substitute(
            substitutes=params["substitutes"],
            request=obj,
            interval_dates=usufructs_in,
            total_days=params["total_days"],
        )
        PortalRequestHistory.create_history(
            observation=params["observation"],
            action=REQUEST_ACT_SOLICITATION,
            request=obj,
            date=datetime.now(),
            group=None,
            user=user,
        )

        tipos_membro = ["MBR", "MEL", "MCM", "MEC", "MBR2", "MEL2", "MCM2", "MEC2"]
        if employee.type_by_possession in tipos_membro:
            if (
                "substitutes" in params
                and params["substitutes"].get("substitutes") == []
            ):
                obj.enviar_notificacao_email(params, usufructs_in, employee)

        return obj

    @classmethod
    def create_request_usufruct(cls, params, portal_request_type=None):
        """
        Rotina que criar as solicitações de usufrutos
        """
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        usufructs_in = params["usufructs_in"]
        if e_plantao_compensatoria(params["type_usufruct"]):
            usufructs_in = ajustar_venda_plantoes(usufructs_in, employee)
        params.update({"total_days": cls.set_total_days(usufructs_in)})
        sale_usufructs = 0
        for usufruct in usufructs_in["usufructs_in"]:
            if usufruct["sale_usufruct"]:
                sale_usufructs += 1
        try:
            with transaction.atomic():
                list_usufructs = [
                    COMP_CLEARANCE_MEMBERS,
                    COMP_VACATION_MEMBERS,
                    ONCALL_BONUS_SERVERS,
                    ELECTORAL_SLACK,
                    FORENSIC_RECESS,
                ]
                if (
                    int(params["type_usufruct"]) in list_usufructs
                    and sale_usufructs > 1
                ):
                    for usufruct in usufructs_in["usufructs_in"]:
                        obj = cls._create_multiple_sell_request_usufruct(
                            employee,
                            date_request,
                            user,
                            params,
                            portal_request_type,
                            usufructs_in,
                            usufruct,
                        )
                else:
                    obj = cls._create_usufruct(
                        employee,
                        date_request,
                        user,
                        params,
                        portal_request_type,
                        usufructs_in,
                    )
                return obj

        except Exception as ex:
            raise Exception(ex)


class PVFRegularVacation(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFIndividualVacation(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFElectoralSlack(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFForensicRecess(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFServerShift(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFIntershipCompetition(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFCompClearanceMembers(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFCompVactionMembers(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFSubstitutePromoterContest(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFBloodDonation(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFSolicitacaoEstagiario(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PVFSolicitacaoResidente(PortalRequestUsufruct):

    class Meta:
        proxy = True


class PortalRequestAbsence(PortalRequest):
    absence = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="portal_request_absence",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    start_date = models.DateField(verbose_name="Data Início", db_index=True)
    end_date = models.DateField(verbose_name="Data Fim", db_index=True)
    days = models.IntegerField("Quantidade de dias")
    type = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "TIPO_BASE_LICENCA_AFASTAMENTO"),
        blank=True,
        db_index=True,
    )

    deadline = {"days": 0}

    def pre_validacao(self, params):
        """
        Método que realiza a pré validação da criação da solicitação de afastamentos
        """
        servidor = get_current_user().servidor

        data_inicio = datetime.strptime(params["data_inicio"], "%d/%m/%Y").date()
        data_fim = datetime.strptime(params["data_fim"], "%d/%m/%Y").date()
        self.validate_substitute_conflict_period(data_inicio, data_fim, servidor)
        self.validate_usufruct_conflict(data_inicio, data_fim, servidor)
        self.validate_absence_conflict(data_inicio, data_fim, servidor)

    def validate_start_date(self, start_date):
        if not start_date:
            raise Exception("Infome a data início.")
        return True

    def validate_end_date(self, end_date):
        if not end_date:
            raise Exception("Infome a data fim.")
        return True

    def validate_days(self, days):
        if not days:
            raise Exception("Informe a quantidade de dias.")
        return True

    def validate_date_of_birth(self):
        if self.dependent and not self.dependent.data_nascimento:
            raise Exception("Dependente sem data de nascimento cadastrada.")
        return True

    def validate_conflict_dependent(self, dependent):
        if dependent:
            dependent_child = Dependente.objects.filter(
                pessoa_fisica__pk=dependent.pk, servidor=self.employee
            )
            if dependent_child:
                raise Exception(f"{dependent_child.first()} Já consta como dependente.")
        return True

    def validate_conflict_employee_dependent(self, dependent):
        if dependent and dependent.pk == self.employee.pessoa_fisica.pk:
            raise Exception(
                "Não é possível informar como dependente o mesmo usuário solicitante."
            )

    def validate_max_days(self):
        days = NewDateRange(self.start_date, self.end_date).days
        if days > self.deadline["days"]:
            raise Exception(
                f"O prazo máximo permitido é de {self.deadline['days']} dia(s)."
            )
        return True

    def set_days(self):
        days = NewDateRange(self.start_date, self.end_date).days
        if hasattr(self, "hours"):
            days = 0 if self.hours else days
        self.days = days

    def published(self, publication):
        if publication:
            return Publicacao.objects.get(pk=publication)
        else:
            return None

    def create_dependency(self, dependent):
        if self.dependent == self.employee.pessoa_fisica:
            raise Exception(
                "Não é possível informar como dependente o mesmo usuário solicitante."
            )

        if self.is_childcare_assistence:
            dependency = Dependencia(
                dependente=dependent,
                tipo=TYPE_CHILDCARE_ASSISTENCE,
                data_inicio=self.start_date,
                idade_limite=CHILD_AGE_LIMIT,
            )
            dependency.save()
        if self.is_incoming_tax:
            dependency = Dependencia(
                dependente=dependent,
                tipo=TYPE_INCOMING_TAX,
                data_inicio=self.start_date,
            )
            dependency.save()

    def create_dependent(self):
        dependente = Dependente.objects.filter(
            servidor=self.employee, pessoa_fisica=self.dependent
        ).first()
        if not dependente:
            dependente = Dependente(
                pessoa_fisica=self.dependent,
                responsavel=self.employee.pessoa_fisica,
                servidor=self.employee,
                grau_parentesco=DEPENDENT_CHILD,
                capacidade=self.capacity,
                incapacity=self.incapacity,
                dep_ir=self.is_incoming_tax,
                tipo=self.dependent_type,
                auxilio_creche=self.is_childcare_assistence,
            )
            dependente.save()
        return dependente

    def effectived_absence(self, publication):
        request = self.portalrequestabsence
        class_instance = CLASS_ABSENCE[request.type]
        obj = eval("request" + class_instance)
        obj.effectived(publication)

    def effectived_substitute(self):
        substitutes = self.portal_request_substitute.all()
        if substitutes:
            for substitute in substitutes:
                instance = (
                    "MovimentacaoSubstituicaoMembro"
                    if self.employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]
                    else "MovimentacaoSubstituicao"
                )
                instance = eval(instance)(
                    afastamento=self.absence,
                    servidor_substituido=substitute.portal_request.employee,
                    posse=substitute.provision,
                    data_inicio=substitute.start_date,
                    data_fim=substitute.end_date,
                    servidor=substitute.substitute,
                    designation_substituted=substitute.exercise,
                    place=substitute.local,
                    origin_register=1,  # Origem = VDF
                )
                instance.save()

    @classmethod
    def set_cid(cls, cid_id):
        if cid_id:
            return CID.objects.get(pk=int(cid_id))
        return None


class PortalRequestDoc(PortalRequest):
    document_type = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "TYPE_DOC"), verbose_name="Documento"
    )


class PortalRequestWorkload(PortalRequest):
    date_start = models.DateField(verbose_name="Data início")
    from_workload = models.IntegerField(verbose_name="da carga de horária")
    to_workload = models.IntegerField(verbose_name="para carga de horária")

    def diff_month(self, dt_start, dt_end):
        return (dt_start.year - dt_end.year) * 12 + dt_start.month - dt_end.month

    def validate_deadline(self, date, employee):
        """valida o prazo mínimo para troca de jornada"""
        workloads = CargaHoraria.objects.filter(servidor=employee).order_by(
            "-data_inicio"
        )
        workload = workloads.first()

        if workloads.count() > 1:
            if workload:
                months = self.diff_month(date, workload.data_inicio)
                date_workload = workload.data_inicio.strftime("%d/%m/%Y")
                if months < 6:
                    raise Exception(
                        f""" Não‌ ‌é‌ ‌permitido‌ ‌alterar‌ ‌jornada‌ ‌em‌ ‌um‌ ‌intervalo‌ ‌inferior‌ ‌a‌ ‌6‌‌ meses.‌
                        ‌Última‌ ‌troca‌ ‌de‌ ‌jornada‌  {date_workload}."""
                    )
                return True
            else:
                raise Exception("Servidor sem carga horária cadastrada")

    def validate_equals(self, to_workload, employee):
        """Valida se a nova jornada é igual a atual"""
        if self.get_current_workload(employee) == to_workload:
            raise Exception("A nova jornada deve ser diferente da jornada atual.")
        return True

    def validate_payment_cutoff_date(self, date_start):
        """valida a data de início com a data de corte da folha de pagamento"""
        date_current = datetime.today().date()
        payment_cutoff = Choice.objects.get(
            name="PAYMENT_CUTOFF_DATE", app_label="pvf", value=1
        )
        if (
            date_start.day >= int(payment_cutoff.label)
            and date_current.month == date_start.month
            and date_current.year == date_start.year
        ):
            raise Exception(
                f"""Não‌ ‌é‌ ‌possível‌ ‌alterar‌ ‌jornada‌ ‌com‌ ‌início‌ ‌no‌ ‌mesmo‌‌ mês‌ ‌após‌ ‌data‌ ‌de‌ ‌corte‌ ‌da‌ ‌folha(Dia‌
                ‌{payment_cutoff.label}).‌ ‌Altere‌ ‌o‌ ‌início‌ ‌para‌ ‌o‌ ‌próximo‌ ‌mês."""
            )
        return True

    def validate_conflict_schedule(self, employee):
        """valida se existe uma solicitação de alteração de jornada"""
        request = PortalRequest.objects.filter(
            employee=employee,
            request_type=REQUEST_TYPE_CHANGE_JOURNEY,
            status__in=[STS_WAI_APPROVER, STS_WAI_EFFECTIVENESS],
        )
        if request:
            raise Exception(
                "Já‌ ‌existe‌ ‌uma‌‌ solicitação‌ ‌pendente‌ ‌para‌ ‌alteração‌ ‌de‌ ‌jornada‌ ‌de‌ ‌trabalho."
            )
        return True

    def validate_fields(self, params):
        if not params["to_workload"]:
            raise Exception("Selecione uma jornada.")
        elif not params["start_date"]:
            raise Exception("Preencha o campo data início.")
        return True

    def effectived_workload(self):
        """Efetiva uma solicitação de alteração de jornada"""
        workload = CargaHoraria()
        workload.quantidade = self.portalrequestworkload.to_workload
        workload.data_inicio = self.portalrequestworkload.date_start
        workload.servidor = self.portalrequestworkload.employee
        workload.save()
        workload.anotacao()

    def get_current_workload(self, employee):
        """Busca a jornada de trabalho atual"""
        workload = (
            CargaHoraria.objects.filter(servidor=employee)
            .order_by("-data_inicio")
            .first()
        )
        if workload:
            return workload.quantidade
        else:
            raise Exception("Servidor sem carga horária cadastrada")

    def validate(self, params):
        self.validate_fields(params)
        date = datetime.strptime(params["start_date"], "%d/%m/%Y").date()
        choice_workload = Choice.objects.get(
            name="WORKLOAD", app_label="pvf", value=params["to_workload"]
        )
        to_workload = int(choice_workload.label)
        self.validate_payment_cutoff_date(date)
        self.validate_equals(to_workload, self.employee)
        self.validate_deadline(date, self.employee)
        self.validate_conflict_schedule(self.employee)

    def save(self, *args, **kwargs):
        params = kwargs.get("params")
        self.validate(params)
        choice_workload = Choice.objects.get(
            name="WORKLOAD", app_label="pvf", value=params["to_workload"]
        )
        self.date_start = datetime.strptime(params["start_date"], "%d/%m/%Y").date()
        self.to_workload = int(choice_workload.label)
        self.from_workload = self.get_current_workload(self.employee)
        kwargs = self._pop_before_save()
        super(PortalRequestWorkload, self).save(**kwargs)

    @classmethod
    def create_change_workload(cls, params):
        employee = get_current_user().servidor
        date = datetime.today().date()
        user = get_current_user()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_CHANGE_JOURNEY,
                    date=date,
                    request=user,
                )
                obj.approval_flow()
                obj.save(params=params)

                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )

        except Exception as ex:
            raise Exception(ex)


@to_search(
    [
        {"name": "observation", "type": "text"},
    ]
)
class PortalRequestHistory(models.Model):
    date = models.DateTimeField(verbose_name="Data da ação")
    portal_request = models.ForeignKey(
        "pvf.PortalRequest",
        verbose_name="Solicitação",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Usuário",
        related_name="portal_request_history",
        on_delete=models.CASCADE,
    )
    group = models.CharField(
        blank=True, null=True, verbose_name="Grupo", max_length=255
    )
    action = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "ACTION_TAKEN"),
        verbose_name="Ação Realizada",
    )
    observation = models.TextField(verbose_name="Observação", blank=True, null=True)
    anexos = models.ManyToManyField(
        File, related_name="portalrequesthistory", verbose_name="Anexos"
    )

    class Meta:
        ordering = ["id"]

    @property
    def get_group_name(self):
        if self.group:
            if self.group in [GROUPS_PVF["GS"], GROUPS_PVF["GM"]]:
                return "DGP"
            elif self.group in [GROUPS_PVF["ASS_JUR_1"]]:
                return "ASSJUR1"
            elif self.group in [GROUPS_PVF["PROG_DG"]]:
                return "PROG_DG"
            elif self.group in [GROUPS_PVF["ASS_JUR_2"]]:
                return "ASSJUR2"
            elif self.group == GROUP_SUB_ADM:
                return "SUB ADMINISTRATIVA"
            else:
                group_name = self.group.split("-").pop().upper()
                return group_name
        return ""

    @property
    def action_label(self):
        if self.action:
            return self.get_action_display()
        return None

    @property
    def employee(self):
        if self.user:
            if hasattr(self.user, "servidor"):
                return self.user.servidor.pessoa_fisica.nome
            else:
                return NOME_JOB_SERVICO.get(self.user.username, None)
        return None

    @property
    def get_origem(self):
        if self.group:
            return self.get_group_name
        elif self.user != self.portal_request.request:
            return "Aprovador"

        return "Solicitante"

    @classmethod
    def create_history(cls, **kwargs):
        """Rotina que cria um histórico da solicitação"""

        observation = kwargs.get("observation")
        action = kwargs.get("action")
        request = kwargs.get("request")
        date = kwargs.get("date")
        group = kwargs.get("group")
        user = kwargs.get("user")
        anexos = kwargs.get("anexos", [])

        if action == REQUEST_ACT_AUTOMATIC_APPROVER:
            history_approver = cls(
                date=date,
                portal_request=request,
                user=user,
                group=group,
                action=REQUEST_ACT_DEFER,
                observation=observation,
            )
            history_dgp = cls(
                date=date,
                portal_request=request,
                user=User.objects.get(pk=1),
                group=GROUP_SERVER,
                action=action,
                observation=observation,
            )
            PortalRequestHistory.objects.bulk_create([history_approver, history_dgp])
        else:
            history = cls(
                date=date,
                portal_request=request,
                user=user,
                group=group,
                action=action,
                observation=observation,
            )
            history.save()
            history.anexos.add(*anexos)


class PortalRequestSubstitute(models.Model):
    portal_request = models.ForeignKey(
        "pvf.PortalRequest",
        verbose_name="Solicitação",
        related_name="portal_request_substitute",
        on_delete=models.CASCADE,
    )
    exercise = models.ForeignKey(
        "rh.ServidorLotacao",
        related_name="request_exercise",
        on_delete=models.PROTECT,
    )
    provision = models.ForeignKey(
        "rh.MovimentacaoPosse",
        related_name="request_provision",
        on_delete=models.PROTECT,
    )
    local = models.ForeignKey(
        "rh.Lotacao",
        related_name="request_local",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    start_date = models.DateField(verbose_name="Data início")
    end_date = models.DateField(verbose_name="Data Fim")
    substitute = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Substituto",
        related_name="request_substitute",
        on_delete=models.PROTECT,
    )

    @property
    def substitute_name(self):
        """property que retorna o nome do substituto
        :returns: str
        """
        return self.substitute.pessoa_fisica.nome

    @property
    def designation(self):
        """property que retorna a desingação da substituição
        :returns: str
        """
        if self.exercise.lotacao:
            return self.exercise.lotacao.nome
        return None

    @classmethod
    def return_absence(cls, request):
        activity_book = None
        if request.request_type == REQUEST_TYPE_SCHEDULE:
            activity_book = request.portalrequestusufruct.activity.filter(
                type_of_activity__in=[ACT_BOOK_SELL, ACT_BOOK]
            ).first()
        else:
            activity_book = request.portalrequestusufruct.activity.filter(
                type_of_activity__in=[ACT_RECTIFY, ACT_CHANGE]
            ).first()

        list_id = list(activity_book.usufructs.values_list("pk", flat=True))
        return BaseLicencaAfastamento.objects.filter(dayoff_usufructs__in=list_id)

    @classmethod
    def instance_model(cls, employee):
        instance = MovimentacaoSubstituicao()
        if employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
            instance = MovimentacaoSubstituicaoMembro()
        return instance

    @classmethod
    def delete_substitute_conflict(cls, request, absence):
        if request.request_type == REQUEST_TYPE_RETIFICATION:
            if absence.substituicao.exists():
                usufructs = Usufruct.objects.filter(
                    activity__activity_requests=request
                ).exclude(status=USU_SOLD)
                for usu in usufructs:
                    if (
                        usu.start_date == absence.data_inicio
                        and usu.end_date == absence.data_fim
                    ):
                        absence.substituicao.all().delete()

    @classmethod
    def effectived_substitute(cls, request):
        substitutes = request.portal_request_substitute.all()
        if substitutes:
            for absence in cls.return_absence(request):
                cls.delete_substitute_conflict(request, absence)
                for substitute in substitutes:
                    if (
                        substitute.start_date >= absence.data_inicio
                        and substitute.end_date <= absence.data_fim
                    ):
                        mov_substitute = cls.instance_model(request.employee)
                        mov_substitute.afastamento = absence
                        mov_substitute.servidor_substituido = (
                            substitute.portal_request.employee
                        )
                        mov_substitute.posse = substitute.provision
                        mov_substitute.data_inicio = substitute.start_date
                        mov_substitute.data_fim = substitute.end_date
                        mov_substitute.servidor = substitute.substitute
                        mov_substitute.designation_substituted = substitute.exercise
                        mov_substitute.place = substitute.local
                        mov_substitute.origin_register = 1  # Vida Funcional
                        mov_substitute.save()

    def get_provision_substitute(self, employee):
        provision = MovimentacaoPosse.objects.filter(
            ativo=True, servidor=employee, quadro__cargo__substituivel=True
        )

        return provision

    def check_optional_substitute(self, employee, first_start_date):
        checked = False
        for group in employee.user.groups.all():
            if group.name == GROUPS_PVF["AS"]:
                checked = True

        try:
            lotacoes_exclude_names = ServidorLotacao.objects.filter(
                Q(
                    servidor=employee,
                    ativo=True,
                    designacao=True,
                    responsible=True,
                    owner=True,
                ),
                Q(
                    Q(data_vigencia_fim__gt=first_start_date)
                    | Q(data_vigencia_fim__isnull=True)
                ),
            ).values_list("lotacao__pk")

            labels_lotacoes = [x[0] for x in lotacoes_exclude_names]
            q_object = reduce(or_, (Q(label=int(x)) for x in labels_lotacoes))
            optional_locals = Choice.objects.filter(
                q_object, name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
            )
            if optional_locals:
                if optional_locals.count() == len(labels_lotacoes):
                    checked = True

        except Exception as e:
            log.error(e)

        if employee.type_by_possession in [
            "EFE",
            "ECM",
            "EFC",
            "CMS",
            "RCM",
            "REQ",
            "RFC",
            "REX",
            "EST",
            "RES",
            "VOL",
        ]:
            checked = True

        if employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
            if not employee.posses_ativas.filter(
                quadro__cargo__configs__replaceable=True,
                quadro__cargo__configs__active=True,
            ):
                checked = True

            query = ServidorLotacao.objects.filter(
                ativo=True, designacao=True, servidor=employee, responsible=True
            )

            if first_start_date:
                query = query.filter(
                    Q(
                        Q(data_vigencia_fim__gt=first_start_date)
                        | Q(data_vigencia_fim__isnull=True)
                    )
                )

            if not query:
                checked = True

        return checked

    def get_date_recess(self, start):
        date_cut_recess = datetime.strptime(f"06/01/{start.year}", "%d/%m/%Y").date()
        start_year_recess = None
        end_year_recess = None
        if start > date_cut_recess:
            start_year_recess = start.year
            end_year_recess = start.year + 1
        else:
            start_year_recess = start.year - 1
            end_year_recess = start.year

        return [
            datetime.strptime(f"20/12/{start_year_recess}", "%d/%m/%Y").date(),
            datetime.strptime(f"06/01/{end_year_recess}", "%d/%m/%Y").date(),
        ]

    def period_recess(self, interval_dates):
        dates = interval_dates.get("usufructs_in", False) or interval_dates.get(
            "date_absence", False
        )
        for date in dates:
            if not date.get("sale_usufruct", False):
                start_recess, end_recess = self.get_date_recess(date["start_date"])
                if (
                    date["start_date"] >= start_recess
                    and date["end_date"] <= end_recess
                ):
                    return True
        return False

    def validate_mandatory_substitute(
        self, employee, substitutes, request, interval_dates
    ):
        """Valida se é obrigatório informa substituto"""
        if request.request_type == REQUEST_TYPE_ABSENCE:
            absences_in = substitutes.get("substitutes", [])
            start_dates = [
                datetime.strptime(absence.get("start_date"), "%d/%m/%Y")
                for absence in absences_in
                if "start_date" in absence
            ]
        else:
            usufructs_in = interval_dates.get("usufructs_in", [])
            start_dates = [
                usufruct.get("start_date")
                for usufruct in usufructs_in
                if "start_date" in usufruct
            ]
        first_start_date = min(start_dates) if start_dates else None
        if not substitutes["substitutes"] and not self.check_optional_substitute(
            employee, first_start_date
        ):
            if not self.period_recess(interval_dates):
                if request.request_type in [
                    REQUEST_TYPE_SCHEDULE,
                    REQUEST_TYPE_RETIFICATION,
                ]:
                    if request.book_usufructs:
                        raise Exception("Obrigatório informar substituto.")
                else:
                    raise Exception("Obrigatório informar substituto.")
        if (
            not substitutes["substitutes"]
            and first_start_date
            and validar_substituto_afastamento(employee)
        ):
            raise Exception("Obrigatório informar substituto.")
        return True

    def intersect_recess(self, start_date, end_date):
        start_recess, end_recess = self.get_date_recess(start_date)
        range_recess = NewDateRange(start_recess, end_recess)
        range_date = NewDateRange(start_date, end_date)
        result = NewDateRange.intersect(range_recess, range_date)
        return [result, range_date]

    def set_total_days_usufruct(self, interval_dates, total_days):
        intersect_recess = NewDateRange()
        range_date = NewDateRange()
        dates = interval_dates.get("usufructs_in", False) or interval_dates.get(
            "date_absence", False
        )
        for date in dates:
            if date.get("sale_usufruct", False):
                total_days = int(total_days) - int(date["days"])
            else:
                intersect_recess, range_date = self.intersect_recess(
                    date["start_date"], date["end_date"]
                )

        return [total_days, intersect_recess, range_date]

    def validate_substitute_date(self, interval_dates, substitutes, total_days):
        """Valida se data da substituição está no mesmo intervalo de data do afastamento"""
        days_designation = {}
        range_days_substituition = NewDateRange()
        exercise = None
        list_date_ranges = []
        for substitute in substitutes["substitutes"]:
            checked = False
            exercise = ServidorLotacao.objects.filter(
                pk=substitute.get("exercise", None)
            ).first()
            start_date = datetime.strptime(substitute["start_date"], "%d/%m/%Y").date()
            end_date = datetime.strptime(substitute["end_date"], "%d/%m/%Y").date()
            range_days_substituition = NewDateRange.union(
                range_days_substituition, NewDateRange(start_date, end_date)
            )
            if not days_designation.get(substitute["exercise"]):
                days_designation[substitute["exercise"]] = NewDateRange(
                    start_date, end_date
                ).days
            else:
                days_designation[substitute["exercise"]] = (
                    days_designation[substitute["exercise"]]
                    + NewDateRange(start_date, end_date).days
                )

            dates = interval_dates.get("usufructs_in", False) or interval_dates.get(
                "date_absence", False
            )
            for date in dates:
                if not date.get("sale_usufruct", False):
                    objeto = {
                        "exercise": substitute["exercise"],
                        "start_date": date["start_date"],
                        "end_date": date["end_date"],
                    }

                    if not objeto in list_date_ranges:
                        list_date_ranges.append(objeto)

                    if (
                        start_date >= date["start_date"]
                        and end_date <= date["end_date"]
                    ):
                        checked = True
            if not checked:
                raise Exception(
                    "A substituição informada deve estar no intervalo de início e fim na programação."
                )

        if substitutes["substitutes"]:
            total_days, intersect_recess, range_date = self.set_total_days_usufruct(
                interval_dates, total_days
            )
            self.validate_leave_period(
                days_designation=days_designation,
                total_days=total_days,
                intersect_recess=intersect_recess,
                range_date=range_date,
                range_days_substituition=range_days_substituition,
                list_date_ranges=list_date_ranges,
            )
        return True

    def set_total_dia_exercicio(self, lista_intervalo_datas, exercicio):
        """Função que alterar o total dias quando a data fim do exercicio for
          menor que o periodo programado.
        args:
            - intervalo_lista:(list)
            - exercicio:(object)
        returns:
            - total de dias:(int)
        """

        total_dias = 0

        for intervalo_data in lista_intervalo_datas:
            if intervalo_data["exercise"] == exercicio.pk:

                if not exercicio.data_vigencia_fim:
                    if intervalo_data["start_date"] < exercicio.data_vigencia_inicio:
                        if exercicio.data_vigencia_inicio <= intervalo_data["end_date"]:
                            total_dias = (
                                total_dias
                                + NewDateRange(
                                    exercicio.data_vigencia_inicio,
                                    intervalo_data["end_date"],
                                ).days
                            )
                    else:
                        total_dias = (
                            total_dias
                            + NewDateRange(
                                intervalo_data["start_date"], intervalo_data["end_date"]
                            ).days
                        )
                else:
                    if (
                        intervalo_data["start_date"] >= exercicio.data_vigencia_inicio
                        and intervalo_data["end_date"] > exercicio.data_vigencia_fim
                    ):
                        if intervalo_data["start_date"] <= exercicio.data_vigencia_fim:
                            total_dias = (
                                total_dias
                                + NewDateRange(
                                    intervalo_data["start_date"],
                                    exercicio.data_vigencia_fim,
                                ).days
                            )

                    elif (
                        intervalo_data["start_date"] < exercicio.data_vigencia_inicio
                        and intervalo_data["end_date"] <= exercicio.data_vigencia_fim
                    ):
                        if exercicio.data_vigencia_inicio <= intervalo_data["end_date"]:
                            total_dias = (
                                total_dias
                                + NewDateRange(
                                    exercicio.data_vigencia_inicio,
                                    intervalo_data["end_date"],
                                ).days
                            )

                    elif (
                        intervalo_data["start_date"] < exercicio.data_vigencia_inicio
                        and intervalo_data["end_date"] > exercicio.data_vigencia_fim
                    ):
                        total_dias = (
                            total_dias
                            + NewDateRange(
                                exercicio.data_vigencia_inicio,
                                exercicio.data_vigencia_fim,
                            ).days
                        )
                    else:
                        total_dias = (
                            total_dias
                            + NewDateRange(
                                intervalo_data["start_date"], intervalo_data["end_date"]
                            ).days
                        )

        return total_dias

    def validate_leave_period(self, **kargs):
        """Valida se o período informado compreende todo o período do afastamento"""

        days_designation = kargs["days_designation"]
        total_days = kargs["total_days"]
        intersect_recess = kargs["intersect_recess"]
        range_date = kargs["range_date"]
        range_days_substituition = kargs["range_days_substituition"]
        list_date_ranges = kargs["list_date_ranges"]

        if not intersect_recess.days > 0:
            for id in days_designation:
                _total_days = int(total_days)
                exercise = ServidorLotacao.objects.get(pk=id)
                range_days = self.set_total_dia_exercicio(list_date_ranges, exercise)
                if range_days < total_days:
                    _total_days = range_days
                if int(days_designation[id]) != _total_days:
                    raise Exception(
                        "O período da substituição deverá ser igual ao período da programação."
                    )
        else:
            range_validation = NewDateRange.subtraction(range_date, intersect_recess)
            if not range_days_substituition.contains(range_validation):
                raise Exception(
                    "Deverá informar substituto para todos os dias da programação com exceção dos dias de recesso forense."
                )

    def get_data_inicio_fim_afastamento(self, afastamentos):
        datas_inicio = []
        datas_fim = []
        for afastamento in afastamentos:
            if "start_date" in afastamento:
                datas_inicio.append(
                    datetime.strptime(afastamento.get("start_date"), "%d/%m/%Y")
                )
            if "end_date" in afastamento:
                datas_fim.append(
                    datetime.strptime(afastamento.get("end_date"), "%d/%m/%Y")
                )
        return datas_inicio, datas_fim

    def get_data_inicio_fim_usufrutos(self, usufrutos):
        datas_inicio = []
        datas_fim = []
        for usufruto in usufrutos:
            if "start_date" in usufruto:
                datas_inicio.append(usufruto.get("start_date"))
            if "end_date" in usufruto:
                datas_fim.append(usufruto.get("end_date"))
        return datas_inicio, datas_fim

    def validate_designation(self, employee, substitutes, interval_dates, request):
        """Valida se foi informado o substituto para cada Exercício"""
        if substitutes["substitutes"]:
            designation_id = []
            for designation in substitutes["substitutes"]:
                designation_id.append(designation["exercise"])

            if request.request_type == REQUEST_TYPE_ABSENCE:
                absences_in = substitutes.get("substitutes", [])
                start_dates, end_dates = self.get_data_inicio_fim_afastamento(
                    absences_in
                )
                menor_start_date = min(start_dates) if start_dates else None
                max_end_date = max(end_dates) if end_dates else None
            else:
                usufructs_in = interval_dates.get("usufructs_in", [])
                start_dates, end_dates = self.get_data_inicio_fim_usufrutos(
                    usufructs_in
                )
                menor_start_date = min(start_dates) if start_dates else None
                max_end_date = max(end_dates) if end_dates else None

            if employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
                choices = Choice.objects.filter(
                    name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
                ).values_list("label")
                designation_substitutes = ServidorLotacao.objects.filter(
                    pk__in=designation_id,
                    designacao=True,
                    ativo=True,
                    responsible=True,
                    owner=True,
                ).count()
                designations = (
                    ServidorLotacao.objects.filter(
                        Q(
                            Q(data_vigencia_fim__gt=menor_start_date)
                            | Q(
                                Q(data_vigencia_fim__isnull=True),
                                Q(data_vigencia_inicio__lte=max_end_date),
                            )
                        ),
                        servidor=employee,
                        ativo=True,
                        designacao=True,
                        responsible=True,
                        owner=True,
                        lotacao__electoral_zone=False,
                        movimentacao_posse__quadro__cargo__configs__replaceable=True,
                    )
                    .exclude(lotacao__pk__in=[int(x[0]) for x in choices])
                    .count()
                )
            else:
                designation_substitutes = ServidorLotacao.objects.filter(
                    pk__in=designation_id,
                    designacao=True,
                    ativo=True,
                    movimentacao_posse__quadro__cargo__chefia=True,
                ).count()
                designations = ServidorLotacao.objects.filter(
                    Q(
                        Q(data_vigencia_fim__gt=menor_start_date)
                        | Q(data_vigencia_fim__isnull=True)
                    ),
                    servidor=employee,
                    ativo=True,
                    designacao=True,
                    movimentacao_posse__quadro__cargo__chefia=True,
                ).count()
            if designation_substitutes < designations:
                raise Exception("Deverá informar um substituto para cada exercício.")

        return True

    def validate_absence_schedule(self, substitute):
        """Valida se o susbstituto já tem um afastamento programado ou usufruto programado"""
        if substitute:
            start_date = datetime.strptime(substitute["start_date"], "%d/%m/%Y").date()
            end_date = datetime.strptime(substitute["end_date"], "%d/%m/%Y").date()
            employee = Servidor.objects.get(pk=substitute["substitute"])
            try:
                request = PortalRequest()
                request.validate_absence_conflict(start_date, end_date, employee)
                request.validate_usufruct_conflict(start_date, end_date, employee)
            except:
                raise Exception(
                    f"""O(A) substituto(a) {employee.pessoa_fisica.nome}
                    já tem um usufruto/afastamento programado para o período informado."""
                )
        return True

    def validate_start_date_greater_end_date(self, substitutes):
        """Valida se data início é menor ou igual a data fim"""
        for substitute in substitutes["substitutes"]:
            start_date = datetime.strptime(substitute["start_date"], "%d/%m/%Y").date()
            end_date = datetime.strptime(substitute["end_date"], "%d/%m/%Y").date()
            if start_date > end_date:
                raise Exception("Data Início deve ser menor ou igual a Data Fim.")
        return True

    def get_designation_electoral(self, employee):
        designations_electoral = ServidorLotacao.objects.filter(
            servidor=employee,
            ativo=True,
            designacao=True,
            responsible=True,
            owner=True,
            lotacao__electoral_zone=True,
        )
        return designations_electoral

    def validate_substitute_field(self, substitute):
        """Valida se o campo substituto foi preeenchido"""
        if not substitute:
            raise Exception("Prencha o campo substituto.")
        return True

    def validate_substitute_exercise_field(self, exercise):
        """Valida se o campo exercício foi preeenchido"""
        if not exercise:
            raise Exception("Prencha o campo Exercício.")
        return True

    def validate_substitute_start_date_field(self, start_date):
        """Valida se o campo data início foi preeenchido"""
        if not start_date:
            raise Exception("Prencha o campo data início.")
        return True

    def validate_substitute_end_date_field(self, end_date):
        """Valida se o campo data fim foi preeenchido"""
        if not end_date:
            raise Exception("Prencha o campo data fim.")
        return True

    def validate_fields(self, substitutes):
        for substitute in substitutes["substitutes"]:
            self.validate_substitute_field(substitute["substitute"])
            self.validate_substitute_exercise_field(substitute["exercise"])
            self.validate_substitute_end_date_field(substitute["end_date"])
            self.validate_substitute_start_date_field(substitute["start_date"])

    def validate(self, employee, substitutes, interval_dates, total_days, request):
        self.validate_mandatory_substitute(
            employee, substitutes, request, interval_dates
        )
        self.validate_designation(employee, substitutes, interval_dates, request)
        self.validate_start_date_greater_end_date(substitutes)
        self.validate_substitute_date(interval_dates, substitutes, total_days)
        for substitute in substitutes["substitutes"]:
            self.validate_absence_schedule(substitute)

    @classmethod
    def get_lotacao(cls, employee):
        employee_capacity = ServidorLotacao.objects.filter(
            servidor__matricula=employee.matricula, designacao=False, ativo=True
        )
        if employee_capacity:
            capacity = employee_capacity.first().lotacao
        else:
            capacity = None
        return capacity

    def create_substitute_electoral(self, designation_electoral):
        for designation in designation_electoral:
            instance = PortalRequestSubstitute(
                portal_request=self.portal_request,
                local=self.local,
                provision=self.provision,
                start_date=self.start_date,
                end_date=self.end_date,
                exercise=designation,
                substitute=self.substitute,
            )
            instance.save()

    @classmethod
    def create_substitute(cls, substitutes, request, interval_dates, total_days):
        employee = get_current_user().servidor
        obj = cls()
        if obj.get_provision_substitute(employee):
            obj.validate_fields(substitutes)
            obj.validate(employee, substitutes, interval_dates, total_days, request)
            for substitute in substitutes["substitutes"]:
                start_date = datetime.strptime(
                    substitute["start_date"], "%d/%m/%Y"
                ).date()
                end_date = datetime.strptime(substitute["end_date"], "%d/%m/%Y").date()
                exercise = ServidorLotacao.objects.get(pk=substitute["exercise"])
                employee_substitute = Servidor.objects.get(pk=substitute["substitute"])
                provision = MovimentacaoPosse.objects.get(
                    pk=exercise.movimentacao_posse.pk
                )
                instance = cls(
                    portal_request=request,
                    local=cls.get_lotacao(employee),
                    provision=provision,
                    start_date=start_date,
                    end_date=end_date,
                    exercise=exercise,
                    substitute=employee_substitute,
                )
                instance.save()
                designation_electoral = instance.get_designation_electoral(employee)
                if exercise.main and designation_electoral:
                    instance.create_substitute_electoral(designation_electoral)


class PortalCancelSchedule(PortalRequest):
    usufruct = models.ForeignKey(
        "dayoff.Usufruct",
        verbose_name="Usufruto",
        related_name="cancel_usufruct",
        on_delete=models.PROTECT,
    )

    def effectived_cancel(self):
        # cancel_schedule = cls.objects.get(portalrequest_ptr_id=request.pk)
        usufruct = Usufruct.objects.get(pk=self.usufruct.pk)
        acquisition_period = AcquisitionPeriod.objects.get(
            pk=usufruct.acquisition_period.pk
        )
        ActivityCancel.do(
            acquisition_period=acquisition_period,
            modified=usufruct.pk,
            authorize=True,
            attachment=None,
            justification=None,
            note=True,
            immediate_authorization=None,
            mediate_authorization=None,
        )

    def save(self, *args, **kwargs):
        self.validate(kwargs.get("usufruct"))
        kwargs = self._pop_before_save()
        super(PortalCancelSchedule, self).save(**kwargs)

    def validate(self, usufruct):
        # self.validate_selected_usufruct(usufruct)
        self.validate_conflict_cancel(usufruct)

    def validate_selected_usufruct(self, usufruct_id):
        if not usufruct_id:
            raise Exception("Informe o usufruto que deseja solicitar o cancelamento.")
        return True

    def validate_conflict_cancel(self, usufruct_id):
        usufruct = PortalCancelSchedule.objects.filter(
            usufruct__pk=usufruct_id,
        ).exclude(
            status__in=[
                STS_EFFECTIVE,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
                STS_REJECTED,
            ]
        )
        if usufruct:
            raise Exception(
                "Já existe uma solicitação de cancelamento para esse usufruto."
            )
        return True

    @classmethod
    def create_cancel_schedule(cls, params):
        employee = get_current_user().servidor
        date = datetime.today().date()
        user = get_current_user()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_CANCELLATION,
                    request=user,
                    date=date,
                    portal_request_type=PORTAL_CANCELAMENTO_TYPE,
                )
                obj.validate_selected_usufruct(params["usufruct_id"])
                obj.usufruct = Usufruct.objects.get(pk=params["usufruct_id"])
                obj.approval_flow()
                obj.save(usufruct=params["usufruct_id"])

                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            raise Exception(ex)


class PortalRetificationSchedule(PortalRequestUsufruct):

    def effectived_retification(self):
        activitys = self.portalrequestusufruct.activity.all()
        for activity in activitys:
            self.deferer_retroactive_usufructs(activity)
            if activity.status != ACT_ST_HOMOLOGATED:
                activity.my_origin.authorize_and_homologate(
                    authorize=True, note=True, validate_prevent_usufruct=True
                )
        PortalRequestSubstitute.effectived_substitute(self)

    def rejected_retification(self):
        activitys = self.portalrequestusufruct.activity.all().order_by("-id")
        for activity in activitys:
            if activity.status not in [ACT_ST_HOMOLOGATED, ACT_ST_SOLD]:
                self.validate_cancel_usufruct(activity)
                activity.my_origin.cancel()

    def save_change_usufruct(self, acquisition_period, modifieds):
        return ActivityRetify.do(
            acquisition_period=acquisition_period,
            usufructs_in=self.book_usufructs,
            modifieds=modifieds,
            authorize=None,
            note=False,
            immediate_authorization=None,
            mediate_authorization=None,
            context=None,
        )

    @classmethod
    def change_retroactive_usufructs_status(self, acquisition_period, modifieds=None):
        """
        Nas solicitações de retificação retroativo e retornar o usufurto no status homologado e o período aquisitico no status "em andamento",
        possibilita-se assim salvar requisições retroativas
        """
        if modifieds:
            modifieds = Usufruct.objects.filter(pk__in=modifieds)

            for usufruct in modifieds:
                if usufruct.status in [USU_ENJOYED, USU_ENJOYING, USU_HOMOLOGATED]:
                    usufruct.status = USU_HOMOLOGATED
                    usufruct.save()
                    AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
                        status=ACQP_PROGRESS
                    )

    def check_parcel_combination(self, acquisition_period):
        """Checa se vai passar pela validação de combinação de férias"""
        for usufruct in acquisition_period.usufructs:
            if usufruct.status == USU_ENJOYED:
                return False
        return True

    def check_rectification_validation(self, acquisition_period, usufructs_in):
        """
        Checa se é necessário realizar a validação de limite anual de férias
        individuais.
        """
        usufructs = acquisition_period.usufructs.filter(status=USU_HOMOLOGATED)
        sum_days_year = self.sum_days_year(usufructs)

        request_days = {}
        for usu in usufructs_in["usufructs_in"]:
            if not usu["sale_usufruct"]:
                start_date = datetime.strptime(usu["start_date"], "%d/%m/%Y").date()
                end_date = datetime.strptime(usu["end_date"], "%d/%m/%Y").date()
                dates = self.interval_dates(start_date, end_date)
                count = [x.year for x in dates]
                request_days = dict(Counter(count) + Counter(request_days))

        keys = list(sum_days_year.keys())
        for k in keys:
            if request_days.get(k):
                if request_days.get(k) != sum_days_year.get(k):
                    return True
            else:
                return True

        return False

    def validade_max_rectify_usufructs(self, modifieds):
        MAX_RETIFICATION = 2
        for usufruct in modifieds:
            usu = Usufruct.objects.get(pk=usufruct)
            if not (MAX_RETIFICATION > usu.retification_usufruct_sum):
                raise Exception(
                    f"""Não é possível retificar pois um ou mais usufrutos selecionados
                    já foram retificados {MAX_RETIFICATION} vezes."""
                )
        return True

    def validate_rectify_only_once(self, acquisition_period, type_usufruct):
        """Valida se tem mais de uma retificação por período aquisitivo em férias regulamentares"""
        if type_usufruct == REGULAR_VACATIONS:
            if acquisition_period.usufructs.filter(status=USU_CHANGED):
                raise Exception(
                    "Só é permitido uma retificação por período aquisitivo."
                )
        return True

    def validate_selected_usufruct(self, modifieds):
        """Valida se foi informado o usufruto a ser retificado"""
        if not modifieds:
            raise Exception("Informe o usufruto que deseja retificar.")
        return True

    def validate_checked_days_usufructs(self, usufructs, days_usufructs):
        days = 0
        for usufructs in usufructs["usufructs_in"]:
            if not usufructs["sale_usufruct"]:
                days = days + usufructs["days"]

        if days != int(days_usufructs):
            raise Exception(
                f"A quantidade de dias ({days}) de usufruto deve ser igual a da solicitação a ser retificada ({days_usufructs})."
            )

    def get_type_usufruct(self, usufruct_id):
        """busca o subtipo de usufruto da retificação"""
        usufruct = Usufruct.objects.get(pk=usufruct_id)
        return usufruct.activity.configuration.sub_type_of_usufruct

    def get_acquisition_period(self, modifieds):
        """busca o período aqusisitivo de usufruto da retificação"""
        if modifieds:
            return AcquisitionPeriod.objects.filter(
                activities__usufructs=modifieds[0]
            ).first()

    def validate_usufructs_in(self, usufructs_in):
        """
        Valida se foi informado usufruto para agendamento"
        """
        usufructs = []
        for usufruct in usufructs_in["usufructs_in"]:
            if not usufruct["sale_usufruct"]:
                usufructs.append(usufruct)
        if not usufructs:
            raise Exception("Não é possível realizar retificação de venda.")
        return True

    def set_activity_sell(self, params):
        activity_sell = list(set(params["all_modifieds"]) - set(params["modifieds"]))
        if activity_sell:
            usufruct = Usufruct.objects.get(pk=activity_sell[0])
            return usufruct.activity

    def save_activitys(self, acquisition_period, modifieds=[]):
        return self.save_change_usufruct(acquisition_period, modifieds)

    def validate_same_period(self, usufructs_in, modifieds):
        qtd_modifieds = len(modifieds)
        qtd_remove = 0
        usufructs = list(usufructs_in["usufructs_in"])
        for usufruct_pk in modifieds:
            usu = Usufruct.objects.get(pk=usufruct_pk)
            count = 0
            remove = False
            sale_usu = True if not usu.start_date else False
            for usu_in in usufructs:
                start_date = (
                    datetime.strptime(usu_in["start_date"], "%d/%m/%Y").date()
                    if "start_date" in usu_in
                    else None
                )
                end_date = (
                    datetime.strptime(usu_in["end_date"], "%d/%m/%Y").date()
                    if "end_date" in usu_in
                    else None
                )
                days = usu_in["days"]
                sale_usufruct = True if usu_in["sale_usufruct"] == 1 else False

                if (
                    usu.start_date == start_date
                    and usu.end_date == end_date
                    and usu.days == days
                    and sale_usu == sale_usufruct
                ):
                    remove = True
                    break
                count += 1

            if remove:
                qtd_remove += 1
                del usufructs[count]
            if qtd_remove == qtd_modifieds:
                raise Exception(
                    "Não é possível retificar a programação para os mesmos dias da original."
                )

    def validate(
        self,
        employee,
        type_usufruct,
        usufructs_in,
        date_request,
        acquisition_period,
        modifieds,
        days_usufructs,
    ):
        if int(type_usufruct) in [
            REGULAR_VACATIONS,
            INDIVIDUAL_VACATION,
            INTERNS_RECESS,
        ]:
            if employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
                if self.check_parcel_combination(acquisition_period):
                    self.validate_config_holiday(usufructs_in, employee)
                self.validate_checked_days_usufructs(usufructs_in, days_usufructs)
            else:
                self.validate_config_holiday(usufructs_in, employee, modifieds)
        self.validade_max_rectify_usufructs(modifieds)
        validate_max_days = self.check_rectification_validation(
            acquisition_period, usufructs_in
        )
        self.validate_usufructs_in(usufructs_in)
        self.validate_date(
            usufructs_in,
            date_request,
            type_usufruct,
            employee,
            acquisition_period,
            modifieds,
            validate_max_days,
        )
        self.validate_same_period(usufructs_in, modifieds)

    def save(self, *args, **kwargs):
        type_usufruct = kwargs.get("type_usufruct")
        params = kwargs.get("params")
        self.validate(
            self.employee,
            type_usufruct,
            params["usufructs_in"],
            self.date,
            kwargs.get("acquisition_period"),
            params["all_modifieds"],
            params["days_usufructs"],
        ),
        kwargs = self._pop_before_save()
        super(PortalRequestUsufruct, self).save(**kwargs)

    @classmethod
    def create_request_retification(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        usufructs_in = params["usufructs_in"]
        try:
            cls.change_retroactive_usufructs_status(
                cls().get_acquisition_period(params["modifieds"]), params["modifieds"]
            )
            with transaction.atomic():
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_RETIFICATION,
                    request=user,
                    date=date_request,
                    parcel_number=(
                        params["parcel_number"] if params["parcel_number"] else None
                    ),
                    portal_request_type=PORTAL_RETIFICACAO_USUFRUTO_TYPE,
                )
                obj.validate_selected_usufruct(params["modifieds"])
                acquisition_period = obj.get_acquisition_period(params["modifieds"])
                type_usufruct = obj.get_type_usufruct(params["modifieds"][0])
                obj.set_usufructs_in(usufructs_in)
                obj.approval_flow(params["substitutes"])
                obj.save(
                    type_usufruct=type_usufruct,
                    params=params,
                    acquisition_period=acquisition_period,
                )
                activity = obj.save_activitys(acquisition_period, params["modifieds"])
                obj.activity.add(activity)

                activity_sell = obj.set_activity_sell(params)
                if activity_sell:
                    obj.activity.add(activity_sell)

                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=obj,
                    interval_dates=usufructs_in,
                    total_days=params["total_days"],
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                if acquisition_period.status == ACQP_FINISHED:
                    acquisition_period.status = ACQP_PROGRESS
                    acquisition_period.save()

                return obj

        except Exception as ex:
            raise Exception(ex)


class SendingTimeSheet(PortalRequest):
    reference_month = models.IntegerField(verbose_name="Referência Mês")
    reference_year = models.IntegerField(verbose_name="Referência Ano")

    class Meta:
        ordering = ["id"]

    @classmethod
    def get_reference(cls, reference):
        if reference:
            month, year = reference.split("/")
            return [int(month), int(year)]
        return cls.get_reference_year_month()

    def validate_conflict_reference(self):
        if not self.pk:
            if SendingTimeSheet.objects.filter(
                employee=employee_from_user(get_current_user()),
                reference_month=self.reference_month,
                reference_year=self.reference_year,
            ).exclude(
                status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
            ):
                raise Exception("Já existe uma folha ponto para essa referência.")
        return True

    def validate(self):
        self.validate_conflict_reference()

    def save(self, *args, **kwargs):
        self.validate()
        super(SendingTimeSheet, self).save(**kwargs)

    @classmethod
    def ref_mes_teletrabalho(cls, servidor):
        """
        Função que retorna a próxima refrencia a ser enviada para os casos de teletrabalho
        Args:
            servidor: (object)
        Returns:
            referencia: date
        """
        ref_mes = None
        ref_folha = None
        movs_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            servidor=servidor
        ).order_by("data_inicio")
        for mov in movs_teletrabalho:
            if ref_mes:
                dias = NewDateRange(ref_mes, mov.data_inicio).days - 1
                cp_ref_folha = ref_mes + timedelta(days=1)
                query = SendingTimeSheet.objects.filter(
                    employee=servidor,
                    reference_month=cp_ref_folha.month,
                    reference_year=cp_ref_folha.year,
                    status=STS_EFFECTIVE,
                )
                if dias > 1 and not query.exists():
                    ref_folha = cp_ref_folha
                    break
                else:
                    ref_mes = mov.data_fim
                    ref_folha = mov.data_fim + timedelta(days=1)
            else:
                ref_mes = mov.data_fim
                ref_folha = mov.data_fim + timedelta(days=1)
        return ref_folha

    @classmethod
    def referencia_mes_afastamento(cls, mes, ano, servidor, ref_tele=None):
        """
        Função que retorna a próxima referencia a ser enviada para os casos de afastamentos
        Args:
            mes: int
            ano: int
            servidor: (object)
        Returns:
            tupla:(mes, ano)
        """
        ref_mes = mes
        ref_ano = ano
        dt_inicio_ref, dt_fim_ref = data_inicio_fim_referencia(mes, ano)
        if ref_tele:
            dt_inicio_ref = ref_tele
        afastamentos = BaseLicencaAfastamento.objects.afastamento_referencia(
            servidor, dt_inicio_ref, dt_fim_ref
        )
        total_dias = 0
        total_dias_mes = NewDateRange(dt_inicio_ref, dt_fim_ref).days
        for afastamento in afastamentos:
            dt_inicio = afastamento.data_inicio
            dt_fim = afastamento.data_fim
            if afastamento.data_inicio < dt_inicio_ref:
                dt_inicio = dt_inicio_ref
            if afastamento.data_fim > dt_fim_ref:
                dt_fim = dt_fim_ref
            dias = NewDateRange(dt_inicio, dt_fim).days
            total_dias = total_dias + dias

        if total_dias == total_dias_mes:
            if afastamentos.count() > 1:
                ref_mes, ref_ano = proxima_referencia(ref_mes, ref_ano)
            else:
                ref_mes = (afastamentos.first().data_fim + timedelta(days=1)).month
                ref_ano = (afastamentos.first().data_fim + timedelta(days=1)).year
            return cls.referencia_mes_afastamento(ref_mes, ref_ano, servidor)

        return ref_mes, ref_ano

    @classmethod
    def referencia_foha_ponto_sequenciada(
        cls, solicitacao, mes_referencia, ano_referencia
    ):
        """
        Função que retorna a próxima referencia a ser enviada para os casos que já
        foi enviada uma folha ponto
        Args:
            solicitacao:(object)
            mes_referencia: int
            ano_referencia: int
        Returns:
            tupla:(mes, ano)
        """
        servidor = employee_from_user(get_current_user())
        mes, ano = proxima_referencia(
            solicitacao.reference_month, solicitacao.reference_year
        )
        if ano < ano_referencia:
            mes = mes_referencia
            ano = ano_referencia

        ref_teletrabalho = cls.ref_mes_teletrabalho(servidor)
        if ref_teletrabalho:
            query_folha_ponto = SendingTimeSheet.objects.filter(
                employee=servidor,
                reference_month=ref_teletrabalho.month,
                reference_year=ref_teletrabalho.year,
                status=STS_EFFECTIVE,
            )
            dt_inicio_ref, dt_fim_ref = data_inicio_fim_referencia(mes, ano)
            mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                servidor=servidor,
                data_inicio__lte=dt_inicio_ref,
                data_fim__gte=dt_fim_ref,
            )

            if not query_folha_ponto.exists() and mov_teletrabalho.exists():
                mes = ref_teletrabalho.month
                ano = ref_teletrabalho.year

                afatamento_referencia_tele = (
                    BaseLicencaAfastamento.objects.afastamento_referencia(
                        servidor,
                        ref_teletrabalho,
                        get_ultimo_dia_referencia(
                            ref_teletrabalho.year, ref_teletrabalho.month
                        ),
                    ).exists()
                )

                if afatamento_referencia_tele:
                    mes, ano = cls.referencia_mes_afastamento(
                        mes, ano, servidor, ref_tele=ref_teletrabalho
                    )
            else:
                mes, ano = cls.referencia_mes_afastamento(mes, ano, servidor)
        else:
            mes, ano = cls.referencia_mes_afastamento(mes, ano, servidor)

        return mes, ano

    @classmethod
    def referencia_folha_ponto_inicial(cls, mes_referencia, ano_referencia):
        """
        Função que retorna a referencia a ser enviada  no primeiro envio
        Args:
            mes_referencia: int
            ano_referencia: int
        Returns:
            tupla:(mes, ano)
        """
        servidor = employee_from_user(get_current_user())
        ano = None
        mes = None
        if (
            servidor.exercise_date.month > mes_referencia
            and servidor.exercise_date.year == ano_referencia
            or servidor.exercise_date.year > ano_referencia
        ):
            mes = servidor.exercise_date.month
            ano = servidor.exercise_date.year
        else:
            mes = mes_referencia
            ano = ano_referencia
        ref_teletrabalho = cls.ref_mes_teletrabalho(servidor)
        if ref_teletrabalho:
            ano = ref_teletrabalho.year
            mes = ref_teletrabalho.month
        else:
            mes, ano = cls.referencia_mes_afastamento(mes, ano, servidor)

        return mes, ano

    @classmethod
    def get_reference_year_month(cls):
        """
        Retorna a referência (mês/ano) da folha ponto
        """
        employee = employee_from_user(get_current_user())
        request = SendingTimeSheet.objects.filter(
            employee=employee, status=STS_EFFECTIVE
        ).last()
        month = None
        year = None
        month_default = Choice.objects.get(
            app_label="pvf", name="REFERENCE_MONTH_POINT_SHEET"
        ).value
        month_default_ext = Choice.objects.get(
            app_label="pvf", name="REFERENCE_MONTH_SHEET_EXT"
        ).value
        year_default = Choice.objects.get(
            app_label="pvf", name="REFERENCE_YEAR_POINT_SHEET"
        ).value
        if request:
            month, year = cls.referencia_foha_ponto_sequenciada(
                request, month_default, year_default
            )

        elif employee.type_by_possession in ["EXT", "REQ"]:
            month, year = cls.referencia_folha_ponto_inicial(
                month_default_ext, year_default
            )
        else:
            month, year = cls.referencia_folha_ponto_inicial(
                month_default, year_default
            )

        return month, year

    @classmethod
    def create(cls, reference):
        employee = get_current_user().servidor
        date = datetime.today().date()
        user = get_current_user()
        try:
            with transaction.atomic():
                reference_year_month = cls.get_reference(reference)
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_POINT_SHEET,
                    date=date,
                    request=user,
                    reference_month=int(reference_year_month[0]),
                    reference_year=int(reference_year_month[1]),
                    portal_request_type=PORTAL_FOLHA_PONTO_TYPE,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_OPEN_SOLICITANTION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                cls.justificar_feriado_municipal(reference_year_month, employee, obj)
                return obj

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def justificar_feriado_municipal(cls, reference_year_month, employee, obj):
        """
        Método responsável por criar justificativa para feriado municipal referente
        a competência da folha ponto e da titularidade do solicitante
        """
        dt_incio_ref = date(reference_year_month[1], reference_year_month[0], 1)
        dt_fim_ref = dt_incio_ref + relativedelta(day=31)

        titularidades = ServidorLotacao.objects.filter(
            Q(servidor=employee)
            & Q(designacao=False)
            & Q(
                Q(
                    data_vigencia_inicio__lte=dt_fim_ref,
                    data_vigencia_fim__gte=dt_incio_ref,
                )
                | Q(
                    data_vigencia_inicio__lte=dt_fim_ref, data_vigencia_fim__isnull=True
                )
            )
        )

        for titularidade in titularidades:
            dt_ini_ref_vigencia = dt_incio_ref
            dt_fim_ref_vigencia = dt_fim_ref
            if titularidade.data_vigencia_inicio > dt_incio_ref:
                dt_ini_ref_vigencia = titularidade.data_vigencia_inicio
            if (
                titularidade.data_vigencia_fim
                and titularidade.data_vigencia_fim < dt_fim_ref
            ):
                dt_fim_ref_vigencia = titularidade.data_vigencia_fim

            feriados = NonWorkingDay.objects.filter(
                Q(abrangency=3)
                & Q(places=titularidade.lotacao.localidade)  # Municipal
                & Q(
                    Q(start_date__range=(dt_ini_ref_vigencia, dt_fim_ref_vigencia))
                    | Q(end_date__range=(dt_ini_ref_vigencia, dt_fim_ref_vigencia))
                )
            )

            if feriados.exists():
                for feriado in feriados:
                    justificativa = PointJustification(
                        reason_type=24,  # Feriado Municipal
                        start_date=feriado.start_date,
                        end_date=(
                            feriado.end_date if feriado.end_date else feriado.start_date
                        ),
                        observation=feriado.description,
                        request=obj,
                        employee=employee,
                        origem=3,  # Feriado Municipal
                        number_hours="00:00",
                    )
                    justificativa.save()


class PortalRequestProgression(PortalRequest):
    progression = models.ForeignKey(
        MovimentacaoProgressao,
        related_name="portal_request_progression",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        super(PortalRequestProgression, self).save(**kwargs)

    @classmethod
    def create(cls, progression):
        date = datetime.today().date()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=progression.servidor,
                    request_type=REQUEST_TYPE_PROGRESSION_V,
                    date=date,
                    request=progression.servidor.user,
                    progression=progression,
                    portal_request_type=PORTAL_REQUEST_TYPE_PROGRESSION_V,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=progression.servidor.user,
                )
                return obj

        except Exception as ex:
            raise Exception(ex)

    def resend_request(self, progression):
        try:
            with transaction.atomic():
                self.progression = progression
                self.approval_flow()
                self.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_SOLICITATION,
                    request=self,
                    date=datetime.now(),
                    group=None,
                    user=progression.servidor.user,
                )
                return self

        except Exception as ex:
            raise Exception(ex)


class PortalRequestProgressionH(PortalRequest):
    """
    Descrição do campo termo_aceite: “Requerimento fundamentado nos artigos 35 e 36, ambos da Lei nº. 9.782/2012,
    em razão de preencher os requisitos exigidos pelos dispositivos supramencionados, conforme
    comprova-se pelo documento em anexo”
    """

    progression = models.ForeignKey(
        MovimentacaoProgressao,
        related_name="portal_request_progression_h",
        on_delete=models.PROTECT,
        verbose_name="Movimentação Progressão",
    )
    config = models.ForeignKey(
        HorizontalProgressionConfig,
        related_name="portal_request_progression_h",
        on_delete=models.PROTECT,
        verbose_name="Configuração de Progressão Horizontal",
    )
    publication = models.ForeignKey(
        Publicacao,
        related_name="portal_request_progression_h",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Publicação Movimentação",
    )
    termo_aceite = models.BooleanField(verbose_name="Termo de aceite", default=False)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.validar()
        super(PortalRequestProgressionH, self).save(**kwargs)

    def validar(self):
        self.validar_termo_aceite()

    def validar_termo_aceite(self):
        if self.termo_aceite == False:
            raise Exception("É necessário preencher o Termo de aceite!")

    @classmethod
    def create(cls, progression, config, termo_aceite):
        date = datetime.today().date()
        employee = get_current_user().servidor
        user = get_current_user()
        provimento = MovimentacaoPosse.objects.get(
            servidor=employee, quadro__cargo__tipo_lei_cargo="EF", ativo=True
        )
        if config.schooling:
            cls.validate_schooling_on_create(provimento, config)
        if config.contribution_time:
            cls.validate_contribution_time_on_create(provimento, config)
        try:
            with transaction.atomic():
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_PROGRESSION_H,
                    date=date,
                    request=user,
                    progression=progression,
                    config=config,
                    portal_request_type=PORTAL_REQUEST_TYPE_PROGRESSION_H,
                    termo_aceite=termo_aceite,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_OPEN_SOLICITANTION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            raise Exception(ex)

    def validate_schooling_on_create(provimento, config):
        cargo = provimento.quadro.cargo
        estrutura_salarial = EstruturaTabelaSalarial.objects.get(pk=config.schooling.pk)
        cargo_ok = False
        for config_cargo in estrutura_salarial.cargos_estrutura.all():
            if cargo == config_cargo.cargo:
                cargo_ok = True
        if not cargo_ok:
            raise Exception(
                "Seu Cargo não foi encontrado nos Cargos da Classe a Progredir!"
            )

    def validate_contribution_time_on_create(provimento, config):
        now = datetime.today().date()
        dif = now - provimento.data_exercicio
        if config.contribution_time > int(dif.days / 365):
            raise Exception(
                "O tempo de contribuição do provimento atual é menor que o solicitado na Classe a Progredir!"
            )

    def register_publication(self, publication):
        try:
            with transaction.atomic():
                self.publication = publication
                self.save()
                return self

        except Exception as ex:
            raise Exception(ex)

    def resend_request(self):
        try:
            with transaction.atomic():
                self.validate()
                if self.config.qtd_documents:
                    self.validate_qtd_documents()
                self.approval_flow()
                self.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_SOLICITATION,
                    request=self,
                    date=datetime.now(),
                    group=None,
                    user=get_current_user(),
                )
                return self

        except Exception as ex:
            raise Exception(ex)

    def validate(self):
        servidor = get_current_user().servidor
        provimento = MovimentacaoPosse.objects.get(
            servidor=servidor, quadro__cargo__tipo_lei_cargo="EF", ativo=True
        )
        if self.config.schooling:
            self.validate_schooling(provimento)
        if self.config.contribution_time:
            self.validate_contribution_time(provimento)

    def validate_schooling(self, provimento):
        cargo = provimento.quadro.cargo
        estrutura_salarial = EstruturaTabelaSalarial.objects.get(
            pk=self.config.schooling.pk
        )
        cargo_ok = False
        for config_cargo in estrutura_salarial.cargos_estrutura.all():
            if cargo == config_cargo.cargo:
                cargo_ok = True
        if not cargo_ok:
            raise Exception(
                "Seu Cargo não foi encontrado nos Cargos da Classe a Progredir!"
            )

    def validate_contribution_time(self, provimento):
        now = datetime.today().date()
        dif = now - provimento.data_exercicio
        if self.config.contribution_time > int(dif.days / 365):
            raise Exception(
                "O tempo de contribuição do provimento atual é menor que o solicitado na Classe a Progredir!"
            )

    def validate_qtd_documents(self):
        if self.document.count() < self.config.qtd_documents:
            raise Exception(
                "A quantidade de documentos enviados é menor do que o solicitado na Classe a Progredir!"
            )


class PRProgressionHDocument(AuditTimestampModel):
    class Meta:
        verbose_name = "PVF - Documentos de Progressão Horizontal"

    pr_progression_h = models.ForeignKey(
        PortalRequestProgressionH,
        related_name="document",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    description = models.CharField(
        verbose_name="Descrição", max_length=250, null=True, blank=True
    )
    attachment = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attachment_progression_h_doc",
    )
    doc_origin = models.SmallIntegerField(
        verbose_name="Origem do Documento", null=True, blank=True
    )

    def __str__(self):
        return "%s" % self.description

    @property
    def pr_progression_h_str(self):
        return self.pr_progression_h.__str__

    def get_doc_origin_display(self, value):
        if value:
            return Choice.objects.get(
                app_label="pvf",
                name="REQUEST_STEP",
                value=value,
            ).label
        else:
            return ""

    def validate_attachment(self):
        if not self.attachment:
            raise Exception("Favor selecionar um documento!")

    def add_step_ger_dev(self):
        if self.pr_progression_h.step_current in [REQUEST_STEP_GER_DEV]:
            self.doc_origin = self.pr_progression_h.step_current
        else:
            raise Exception(
                "Você não tem permissão para adicionar documento nessa etapa!"
            )

    def validate_step_ger_dev(self):
        if (
            self.pr_progression_h.step_current == self.doc_origin
            and self.pr_progression_h.step_current in [REQUEST_STEP_GER_DEV]
        ):
            self.doc_origin = self.pr_progression_h.step_current
        else:
            raise Exception(
                "Você não tem permissão para alterar o documento dessa etapa!"
            )

    def validate(self):
        self.validate_attachment()

        employee = employee_from_user(get_current_user())
        if employee.user.groups.filter(name__in=[GROUP_GER_DEV]):
            if self.pk:
                # Editar
                self.validate_step_ger_dev()
            else:
                # Criar
                self.add_step_ger_dev()

    def save(self, *args, **kwargs):
        self.validate()
        super(PRProgressionHDocument, self).save(*args, **kwargs)


class SendingTelework(PortalRequest):
    reference_month = models.IntegerField(verbose_name="Referência Mês")
    reference_year = models.IntegerField(verbose_name="Referência Ano")
    work_plan = models.ForeignKey(
        MovimentacaoTeletrabalho,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="pvf_work_plan",
        verbose_name="Plano de Trabalho",
    )
    cancelado_solicitacao = models.BooleanField(default=False)
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="anexo_sending_telework",
    )

    class Meta:
        ordering = ["id"]

    QTD_WORK_PLAN = 1

    @property
    def get_count_workplan(self):
        month, year = SendingTelework.get_reference_year_month()
        return SendingTelework.count_work_plan(month, year)

    @property
    def metas_saldo_devedor(self):
        metas_saldo_devedor = []
        metas_devedoras = MarkTelework.objects.filter(
            request=self, saldo_devedor_anterior__gt=0
        )
        for meta in metas_devedoras:
            metas_saldo_devedor.append(
                {
                    "saldo_devedor": meta.saldo_devedor_anterior,
                    "descricacao": meta.mark_plan.descricao,
                }
            )
        return metas_saldo_devedor

    @property
    def get_count_send(self):
        return (
            SendingTelework.objects.filter(
                employee=employee_from_user(get_current_user()),
                reference_month=self.reference_month,
                reference_year=self.reference_year,
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
            )
            .exclude(cancelado_solicitacao=True)
            .count()
        )

    def save(self, *args, **kwargs):
        self.validate()
        if self.status != STS_STAND_BY:
            self.validate_mark_situation()
        if not self.work_plan:
            self.work_plan = self.get_work_plan()
        super(SendingTelework, self).save(**kwargs)

    def validate_mark_situation(self):
        for mark_plan in self.pvf_request_telework.filter():
            if (
                not mark_plan.total_completed and mark_plan.total_completed != 0
            ) or not mark_plan.mark_situation:
                raise Exception("Preencha o total mensal e a situação da meta.")
        return True

    def validate(self):
        self.validate_work_plan()
        # self.valdidate_date_work_plan()

    def validate_work_plan(self):
        work_plan = self.get_work_plan()
        if not work_plan:
            raise Exception("Servidor sem plano de trabalho.")
        return True

    def valdidate_date_work_plan(self):
        work_plan = self.get_work_plan()
        today = datetime.today().date()
        if work_plan:
            if work_plan.data_fim and not work_plan.data_fim >= today:
                raise Exception(
                    "Não há plano de trabalho para o servidor na data atual."
                )
            elif not today >= work_plan.data_inicio:
                raise Exception(
                    "Não há plano de trabalho para o servidor na data atual."
                )
        return True

    def return_number_to_str(self, number):
        if number <= 9:
            return f"0{number}"
        return str(number)

    @classmethod
    def get_mov_teletrabalho(self, servidor, solicitacao):
        """
        Retorna o plano atual vigente para solicitação.
        Args:
        - servidor
        - solicitacao
        Returns:
            plano atual vigente para a solicitação no servidor especificado.
        """
        ultimo_mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            situacao__in=[
                STATUS_TELETRABALHO_REGULAR,
                STATUS_TELETRABALHO_DESBLOQUEADO,
                STATUS_TELETRABALHO_PENDENTE,
            ],
            servidor=servidor,
        ).last()
        mov_teletrabalho = None
        if solicitacao:
            mov_teletrabalho = (
                MovimentacaoTeletrabalho.objects.filter(ativo=True, servidor=servidor)
                .exclude(pk=solicitacao.work_plan.pk)
                .first()
            )
        if not mov_teletrabalho:
            mov_teletrabalho = ultimo_mov_teletrabalho
        return mov_teletrabalho

    def get_work_plan(self):
        servidor = employee_from_user(get_current_user())
        if self.get_count_workplan > self.QTD_WORK_PLAN:
            request = (
                SendingTelework.objects.filter(employee=servidor)
                .exclude(
                    status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
                )
                .exclude(cancelado_solicitacao=True)
                .last()
            )
        else:
            request = (
                SendingTelework.objects.filter(employee=servidor, status=STS_EFFECTIVE)
                .exclude(cancelado_solicitacao=True)
                .last()
            )
        if request:
            if request.work_plan.data_fim:
                month_workplan = self.return_number_to_str(
                    request.work_plan.data_fim.month
                )
                month_reference = self.return_number_to_str(self.reference_month)
                month_year_reference = int((f"{self.reference_year}{month_reference}"))
                month_year_workplan = int(
                    (f"{request.work_plan.data_fim.year}{month_workplan}")
                )
                old_request_referene = int(
                    (
                        f"{request.reference_year}{self.return_number_to_str(request.reference_month)}"
                    )
                )
                if (
                    month_year_reference <= month_year_workplan
                    and old_request_referene < month_year_workplan
                ):
                    return request.work_plan
        return SendingTelework.get_mov_teletrabalho(servidor, request)

    @classmethod
    def count_work_plan(cls, month, year):
        servidor = employee_from_user(get_current_user())
        return (
            MovimentacaoTeletrabalho.objects.filter(
                Q(data_fim__isnull=False)
                & Q(data_fim__month=month)
                & Q(data_fim__year=year)
                & Q(ativo=True)
                & Q(servidor=servidor)
                | Q(data_inicio__month=month)
                & Q(data_inicio__year=year)
                & Q(ativo=True)
                & Q(servidor=servidor)
            )
            .distinct()
            .count()
        )

    @classmethod
    def get_reference_year_month(cls, employee=None):
        """
        Retorna a referência (mês/ano) do relatório de teletrabalho
        """
        if not employee:
            employee = employee_from_user(get_current_user())
        request = (
            SendingTelework.objects.filter(employee=employee, status=STS_EFFECTIVE)
            .exclude(cancelado_solicitacao=True)
            .last()
        )
        month = None
        year = None
        work_plan = cls.get_mov_teletrabalho(employee, request)

        if request:
            if request.work_plan.data_fim:
                if (
                    work_plan
                    and request.reference_month == request.work_plan.data_fim.month
                    and request.reference_year == request.work_plan.data_fim.year
                    and request.work_plan != work_plan
                ):
                    month = work_plan.data_inicio.month
                    year = work_plan.data_inicio.year
                else:
                    month = (
                        1
                        if request.reference_month == 12
                        else request.reference_month + 1
                    )
                    year = (
                        request.reference_year + 1
                        if request.reference_month == 12
                        else request.reference_year
                    )
            else:
                month = (
                    1 if request.reference_month == 12 else request.reference_month + 1
                )
                year = (
                    request.reference_year + 1
                    if request.reference_month == 12
                    else request.reference_year
                )
        else:
            month_default = Choice.objects.get(
                app_label="pvf", name="REFERENCE_MONTH_TELE_WORK"
            ).value
            year_default = Choice.objects.get(
                app_label="pvf", name="REFERENCE_YEAR_TELE_WORK"
            ).value

            if not work_plan:
                month = month_default
                year = year_default

            elif (
                work_plan
                and work_plan.data_inicio.month > month_default
                and work_plan.data_inicio.year == year_default
                or work_plan.data_inicio.year > year_default
            ):
                month = work_plan.data_inicio.month
                year = work_plan.data_inicio.year
            else:
                month = month_default
                year = year_default

        return month, year

    def efetivar_teletrabalho(self):
        from rh.teletrabalho.utils import (
            concluir_mov_teletrabalho,
            verificar_plano_pendente,
            atualizar_possui_saldo_devedor,
        )

        mov_teletrabalho = self.work_plan
        if not verificar_plano_pendente(mov_teletrabalho, self):
            concluir_mov_teletrabalho(mov_teletrabalho)
        atualizar_possui_saldo_devedor(mov_teletrabalho)

    @classmethod
    def create(cls):
        from rh.teletrabalho.utils import calculo_meta_mensal, get_saldo_devedor

        employee = get_current_user().servidor
        date = datetime.today().date()
        user = get_current_user()
        try:
            with transaction.atomic():
                reference_year_month = cls.get_reference_year_month()
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_TELEWORK,
                    date=date,
                    request=user,
                    reference_month=reference_year_month[0],
                    reference_year=reference_year_month[1],
                    portal_request_type=PORTAL_TELEWORK_TYPE,
                )
                obj.approval_flow()
                obj.save()

                for mark in obj.work_plan.mov_teletrabalho.filter():
                    mes_anterior, ano_anterior = referencia_anterior(
                        obj.reference_month, obj.reference_year
                    )
                    saldo_devedor = get_saldo_devedor(mark, mes_anterior, ano_anterior)
                    meta_mensal = calculo_meta_mensal(
                        mark, obj.reference_month, obj.reference_year, saldo_devedor
                    )
                    instance = MarkTelework(
                        mark_plan=mark,
                        request=obj,
                        meta_mes=meta_mensal,
                        saldo_devedor_anterior=saldo_devedor,
                    )
                    instance.save(validate_prevent=False)
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_OPEN_SOLICITANTION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            raise Exception(ex)

    def send(self, observation=None, anexo=None):
        from rh.teletrabalho.utils import (
            regularizar_mov_teletrabalho,
            notificar_metas_com_saldo_devedor,
        )

        try:
            with transaction.atomic():
                self.validade_last_working_day_month()
                action_type = REQUEST_ACT_SOLICITATION
                group = self.set_group_history()
                self.anexo = anexo
                self.approval_flow()
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
                regularizar_mov_teletrabalho(self)
                notificar_metas_com_saldo_devedor(self)
        except Exception as e:
            log.error(e)
            raise Exception(e)

    @classmethod
    def update_approver_from_existing_telework_report(cls, teleworks, new_approver):
        cls.objects.filter(
            work_plan__in=teleworks,
            status=STS_WAI_APPROVER,
            step_current=REQUEST_STEP_APPROVER,
        ).update(approver=new_approver)


class PointJustification(models.Model):
    reason_type = models.IntegerField(
        choices=JustificationItem.get_config_for("folha_ponto_justificativas"),
        verbose_name="Motivo",
    )
    number_hours = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(verbose_name="Início")
    end_date = models.DateField(verbose_name="Fim")
    observation = models.TextField(verbose_name="Observação", blank=True, null=True)
    attachment = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_attachment_justification",
    )
    request = models.ForeignKey(
        SendingTimeSheet,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="pvf_request_justification",
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="point_justification",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    fault = models.ForeignKey(
        "ponto.Falta",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="point_justification",
    )
    origem = models.SmallIntegerField(
        choices=Choice.get_choices_for("ponto", "ORIGEM_JUSTIFICATIVA"),
        blank=True,
        null=True,
    )
    cancelado = models.BooleanField(
        verbose_name="Cancelado", default=False, blank=True, null=True
    )
    tipo_justificativa_origem = models.CharField(
        choices=Choice.get_choices_for(
            "registerpoint", "FOLHA_PONTO_TIPO_JUSTIFICATIVA", char_field=True
        ),
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        motivo = ""
        try:
            motivo = (
                JustificationItem.objects.get(value=self.reason_type).name
                if self.reason_type
                else ""
            )
        except Exception as e:
            log.error(e)
        return f'{self.start_date if self.start_date else ""} - {motivo}'

    @property
    def get_motivo_nome(self):
        motivo = JustificationItem.objects.filter(value=self.reason_type).first()
        if motivo:
            return motivo.name
        return None

    @property
    def get_dias(self):
        if self.number_hours == "00:00":
            return NewDateRange(self.start_date, self.end_date).days
        return None

    def save(self, *args, **kwargs):
        self.validar_cancelado()
        modulo = 0
        if any("modulo" in sub for sub in args):
            modulo = args[0]["modulo"]
        self.employee = self.request.employee if self.request else self.employee
        if self.origem != ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO:
            self.validate(modulo)

        super(PointJustification, self).save(**kwargs)

    def delete(self, *args, **kargs):
        modulo = 0
        if not args:
            modulo = 1
        elif any("modulo" in sub for sub in args):
            modulo = args[0]["modulo"]

        # 1 - Vida Funcional, 3 - Feriado Municipal
        if self.origem == 1 and modulo != 1:
            raise Exception(
                "Não é permitido cancelar uma Justificativa com origem Vida Funcional"
            )
        elif self.origem == 3 and modulo != 1:
            raise Exception(
                "Não é permitido cancelar uma Justificativa com origem Feriado Municipal"
            )

        self.cancelado = True
        self.save_base()
        # super(PointJustification, self).delete(*args, **kargs)

    def validar_cancelado(self):
        if self.pk and self.cancelado == True:
            justificativa = PointJustification.objects.get(pk=self.pk)
            if justificativa.cancelado == True:
                raise Exception("Não é permitido alterar Justificativa cancelada!")

    def validate(self, modulo):
        self.validar_modulo_alteracao(modulo)
        if not self.fault and self.request:
            self.validate_start_date()
        elif self.fault:
            self.validar_justificativa_gestor_faltas()
        elif self.origem == ORIGEM_JUSTIFICATIVA_FOLHA_PONTO:
            self.validar_solicitacao_folha_ponto()

        self.validate_format_hours()
        self.validate_limit_hours()
        self.validate_attachment()
        self.validar_justificativa_unica_ativa()

    def validar_justificativa_gestor_faltas(self):
        query = self.fault.point_justification.filter(
            start_date__gte=self.start_date, end_date__lte=self.end_date
        )
        if not self.pk and query:
            ativa = False
            for just in query:
                if just.cancelado == False:
                    ativa = True
            if ativa == True:
                raise Exception(
                    "Já existe Justificativa cadastrada para a Falta selecionada!"
                )

    def validar_modulo_alteracao(self, modulo):
        # Quano módulo = 2 (Vida Funcional) e self.origem = 2 (Vida Funcional), pode alterar.
        if self.origem == 3 and self.pk:
            raise Exception(
                "Não é permitido alterar Justificativa com origem Feriado Municipal!"
            )
        elif modulo == 1 and self.origem != 1 and self.pk:
            raise Exception(
                "Só é permitido alterar esta Justificativa pela tela Minhas Solicitações do Vida Funcional!"
            )

    def validate_start_date(self):
        month = self.request.reference_month
        year = self.request.reference_year
        if (
            self.start_date.month != month
            or self.end_date.month != month
            or self.start_date.year != year
            or self.end_date.year != year
        ):
            raise Exception(
                "Data início e fim da justificativa devem estar dentro do mês correspondente."
            )
        return True

    def validate_limit_hours(self):
        item = JustificationItem.objects.filter(
            configuration__application="folha_ponto_justificativas",
            value=self.reason_type,
        ).first()
        if item and item.max_value:
            number_hours = float(self.number_hours.replace(":", "."))
            if self.number_hours == "00:00":
                days = NewDateRange(self.start_date, self.end_date).days
                number_hours = self.get_workload() * days
            if not number_hours <= item.max_value:
                raise Exception(
                    f"A quantidade máxima de horas para o tipo de justificativa selecionada é: {item.max_value}horas(s)"
                )
        return True

    def validate_format_hours(self):
        try:
            datetime.strptime(self.number_hours, "%H:%M")
        except:
            raise Exception("Formato de hora inválido. formato válido: 00:00")
        return True

    def validate_attachment(self):
        justif_item = JustificationItem.objects.get(value=self.reason_type)
        if justif_item.mandatory_document == 1 and not self.attachment:
            raise Exception(
                f"É obrigatória a seleção do Anexo para o Motivo: {justif_item.name}"
            )

    def validar_solicitacao_folha_ponto(self):
        solicitacao_folha_ponto = (
            SendingTimeSheet.objects.filter(
                Q(employee=self.employee),
                Q(
                    Q(reference_year__lt=self.end_date.year)
                    | Q(
                        reference_year=self.end_date.year,
                        reference_month__lte=self.end_date.month,
                    )
                )
                & Q(
                    Q(reference_year__gt=self.start_date.year)
                    | Q(
                        reference_year=self.start_date.year,
                        reference_month__gte=self.start_date.month,
                    )
                ),
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
            )
            .exists()
        )

        if solicitacao_folha_ponto:
            raise Exception(
                "Não é possível criar a justificativa porque já existe um envio de folha de ponto para a competência."
            )
        return True

    @property
    def is_update(self):
        if self.request and self.request.status != STS_STAND_BY:
            return False
        return True

    @property
    def get_days(self):
        return NewDateRange(self.start_date, self.end_date).days

    @property
    def get_reason_type_str(self):
        reason_type = JustificationItem.objects.filter(value=self.reason_type).first()
        if reason_type:
            return reason_type.name
        return ""

    def get_workload(self):
        jornada_trabalho = (
            CargaHoraria.objects.filter(
                servidor=self.employee, jornada_trabalho__isnull=False
            )
            .order_by("-data_inicio", "-pk")
            .first()
        )

        return jornada_trabalho.duration_hour if jornada_trabalho else 6

    def validar_justificativa_unica_ativa(self):
        q_justificativa = (
            PointJustification.objects.filter(
                Q(employee__pk=self.employee.pk),
                Q(
                    Q(start_date__lte=self.start_date, end_date__gte=self.start_date)
                    | Q(start_date__gte=self.start_date, start_date__lte=self.end_date)
                ),
            )
            .exclude(
                request__status__in=[
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )
            .exclude(cancelado=True)
            .exclude(fault__situacao=3)
        )

        if not self.pk and q_justificativa.exists():
            raise Exception("Não é possivel criar duas Justificativas no mesmo dia.")


class MarkTelework(models.Model):
    mark_plan = models.ForeignKey(
        MetaTeletrabalho,
        on_delete=models.PROTECT,
        related_name="mark_plan_work",
        verbose_name="Meta do Plano",
    )
    total_completed = models.IntegerField(
        verbose_name="Total Realizado", blank=True, null=True
    )
    mark_situation = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "MARK_SITUATION"),
        verbose_name="Situação da Meta",
        blank=True,
        null=True,
    )
    observation = models.TextField(verbose_name="Observação", blank=True, null=True)
    request = models.ForeignKey(
        SendingTelework,
        on_delete=models.CASCADE,
        related_name="pvf_request_telework",
        verbose_name="Solicitação",
    )
    meta_mes = models.IntegerField(blank=True, null=True)
    saldo_devedor_anterior = models.IntegerField(default=0)
    saldo_devedor = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.validate(kwargs.get("validate_prevent", True))
        if "validate_prevent" in kwargs:
            kwargs.pop("validate_prevent")
        super(MarkTelework, self).save(**kwargs)

    def validate(self, validate_prevent):
        if validate_prevent:
            self.validate_mark_situation()

    def validate_mark_situation(self):
        if (
            not self.total_completed and self.total_completed != 0
        ) or not self.mark_situation:
            raise Exception("Preencha o total realizado e a situação da meta.")
        return True

    @property
    def description_mark(self):
        return self.mark_plan.descricao

    @property
    def mark(self):
        return self.mark_plan.meta

    @property
    def qtde_dias_afastamento_mes(self):
        from rh.afastamento.afastamento_utils import dias_afastamento_mes

        indice = 0
        mes = self.request.reference_month
        ano = self.request.reference_year
        servidor = self.request.employee
        meta = self.mark_plan
        if mes == 1 or mes == 12:
            indice = 1
        qtde_dias = dias_afastamento_mes(servidor, mes, ano, meta)[indice]
        return qtde_dias

    @property
    def is_update(self):
        if self.request.status != STS_STAND_BY:
            return False
        return True


class ShiftManager(models.Model):
    """
    Classe reponsável pelo controle de plantões de servidores
    """

    owner = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Responsável",
        related_name="shift_owner",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    workplace = models.ForeignKey(
        "rh.Lotacao",
        verbose_name="Lotação",
        related_name="shift_workplace",
        on_delete=models.PROTECT,
    )
    type_shift = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "TYPE_SHIFT"), verbose_name="Tipo"
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Plantonista",
        related_name="shift_employee",
        on_delete=models.PROTECT,
    )
    days = models.PositiveIntegerField(verbose_name="Quantidade de dias")
    start_date = models.DateField(verbose_name="Data Início")
    end_date = models.DateField(verbose_name="Data Fim")
    observacao = models.TextField(verbose_name="Observação", blank=True, null=True)
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="shiftmanger",
    )

    class Meta:
        ordering = ["-id"]

    def get_request(self):
        if self.server_duty.exists():
            solicitacao = self.server_duty.filter().first()
            return solicitacao
        return None

    @property
    def icons(self):
        icons = []

        if self.server_duty.exists():

            if self.get_request().status in [STS_WAI_APPROVER, STS_WAI_EFFECTIVENESS]:
                icons.append(
                    {
                        "icon": PVF_ICONS_THEME["waiting"],
                        "title": "Existe uma solicitação pendente de aprovação, consulte a tela Aguardando Aprovação/Ciência",
                        "alt": "Em andamento",
                    }
                )

            if self.get_request().status == STS_EFFECTIVE:
                icons.append(
                    {
                        "icon": PVF_ICONS_THEME["approver"],
                        "title": "Solicitação Aprovada",
                        "alt": "Aprovada",
                    }
                )

            if self.get_request().status in [
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]:
                icons.append(
                    {
                        "icon": PVF_ICONS_THEME["rejected"],
                        "title": "Solicitação Cancelada",
                        "alt": "Cancelado",
                    }
                )
        else:
            icons.append({"icon": PVF_ICONS_THEME["blank"], "title": "", "alt": "--"})

        return icons

    @property
    def get_status(self):
        solicitacao = self.get_request()
        if solicitacao:
            return solicitacao.status
        return STS_ESCALA_ENVIADA

    @property
    def get_status_nome(self):
        solicitacao = self.get_request()
        if solicitacao:
            return solicitacao.get_status_display()
        return (
            Choice.objects.filter(name="REQUEST_STATUS", value=STS_ESCALA_ENVIADA)
            .first()
            .label
        )

    @property
    def workplace_name(self):
        return self.workplace.nome

    @property
    def employee_name(self):
        return f"{self.employee.matricula}:{self.employee.pessoa_fisica.nome}"

    @property
    def type_shift_label(self):
        return self.get_type_shift_display()

    def set_weekdays(self, value):
        return value.weekday()

    def interval_dates(self, start_date, end_date):
        import datetime

        date_generated = [
            start_date + datetime.timedelta(days=x)
            for x in range(0, (end_date - start_date).days + 1)
        ]
        return date_generated

    def set_dates_recess(self):
        if self.start_date.month != 1:
            year = str(self.start_date.year)
            next_year = str(self.start_date.year + 1)
            start_date = datetime.strptime("20/12/" + year, "%d/%m/%Y").date()
            end_date = datetime.strptime("06/01/" + next_year, "%d/%m/%Y").date()
            return start_date, end_date
        else:
            if self.start_date.day <= 6:
                year = str(self.start_date.year - 1)
                next_year = str(self.start_date.year)
                start_date = datetime.strptime("20/12/" + year, "%d/%m/%Y").date()
                end_date = datetime.strptime("06/01/" + next_year, "%d/%m/%Y").date()
                return start_date, end_date
            else:
                year = str(self.start_date.year)
                next_year = str(self.start_date.year + 1)
                start_date = datetime.strptime("20/12/" + year, "%d/%m/%Y").date()
                end_date = datetime.strptime("06/01/" + next_year, "%d/%m/%Y").date()
                return start_date, end_date

    def check_abrangency_city(self, nondays):
        for nonday in nondays:
            if nonday.abrangency == ABRANGENCY_CITY:
                return nonday.places.filter(pk=self.workplace.localidade_id).exists()
        return True

    def checked_weekend_nonday(self):
        dates = self.interval_dates(self.start_date, self.end_date)
        is_weekend_nonday = False
        log.info(f"dates: {dates}")
        for date in dates:
            is_weekday = False
            nondays = (
                NonWorkingDay.objects.filter(
                    Q(end_date__isnull=False, start_date__lte=date, end_date__gte=date)
                    | Q(end_date__isnull=True, start_date=date)
                )
                .exclude(is_partial=True)
                .exclude(kind__in=[3, 4])  # 3=Suspensão, 4=Recesso
            )
            is_nonday = self.check_abrangency_city(nondays) if nondays else False

            if date.weekday() == 5 or date.weekday() == 6:
                is_weekday = True

            if is_nonday or is_weekday:
                is_weekend_nonday = True

        return is_weekend_nonday

    def only_weekend_nonday(self):
        dates = self.interval_dates(self.start_date, self.end_date)

        for date in dates:
            is_weekend_nonday = False
            is_weekday = False
            nondays = (
                NonWorkingDay.objects.filter(
                    Q(end_date__isnull=False, start_date__lte=date, end_date__gte=date)
                    | Q(end_date__isnull=True, start_date=date)
                )
                .exclude(is_partial=True)
                .exclude(kind__in=[3, 4])  # 3=Suspensão, 4=Recesso
            )
            is_nonday = self.check_abrangency_city(nondays) if nondays else False

            if date.weekday() == 5 or date.weekday() == 6:
                is_weekday = True

            if is_nonday or is_weekday:
                is_weekend_nonday = True

            if is_weekend_nonday == False:
                return is_weekend_nonday

        return is_weekend_nonday

    def validate_type_dti(self):
        if self.type_shift == TYPE_SHIFT_DTI:
            if (
                ShiftManager.objects.filter(
                    Q(type_shift=TYPE_SHIFT_DTI),
                    Q(workplace=self.workplace),
                    Q(start_date__range=[self.start_date, self.end_date])
                    | Q(end_date__range=[self.start_date, self.end_date])
                    | Q(start_date__lte=self.start_date)
                    & Q(end_date__gte=self.end_date),
                )
                .exclude(pk=self.pk)
                .exclude(
                    server_duty__isnull=False,
                    server_duty__status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                    ],
                )
                .exists()
            ):
                raise Exception(
                    "Não é permitido escalar mais de um servidor para o mesmo dia."
                )
        return True

    def validate_type_weekend(self):
        if self.type_shift == TYPE_SHIFT_WEEKEND:
            if (
                ShiftManager.objects.filter(
                    Q(type_shift=TYPE_SHIFT_WEEKEND),
                    Q(workplace=self.workplace),
                    Q(start_date__range=[self.start_date, self.end_date])
                    | Q(end_date__range=[self.start_date, self.end_date])
                    | Q(start_date__lte=self.start_date)
                    & Q(end_date__gte=self.end_date),
                )
                .exclude(pk=self.pk)
                .exclude(
                    server_duty__isnull=False,
                    server_duty__status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                    ],
                )
                .exists()
            ):
                raise Exception(
                    "Não é permitido escalar mais de um servidor para o mesmo dia."
                )
        return True

    def validate_type_weekend_days(self):
        if self.type_shift == TYPE_SHIFT_WEEKEND:
            if not self.only_weekend_nonday():
                raise Exception(
                    "Só é permitido escalar em finais de semana e feriados."
                )
        return True

    def validate_type_recess_days(self):
        if self.type_shift == TYPE_SHIFT_RECESS:
            if self.checked_weekend_nonday():
                raise Exception(
                    "Não é permitido escalar plantão de recesso em finais de semana e feriados."
                )
        return True

    def validate_type_recess(self):
        if self.type_shift == TYPE_SHIFT_RECESS:
            date_recess = self.set_dates_recess()
            dates = self.interval_dates(date_recess[0], date_recess[1])
            if not self.start_date in dates or not self.end_date in dates:
                raise Exception(
                    "Data início e fim deve está no intervalo de 20/12 a 06/01."
                )
        return True

    def validate_type_electoral(self):
        if self.type_shift == TYPE_SHIFT_ELECTORAL:
            if (
                ShiftManager.objects.filter(
                    Q(type_shift=TYPE_SHIFT_ELECTORAL),
                    Q(workplace=self.workplace),
                    Q(start_date__range=[self.start_date, self.end_date])
                    | Q(end_date__range=[self.start_date, self.end_date])
                    | Q(start_date__lte=self.start_date)
                    & Q(end_date__gte=self.end_date),
                )
                .exclude(pk=self.pk)
                .exclude(
                    server_duty__isnull=False,
                    server_duty__status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                    ],
                )
                .exists()
            ):
                raise Exception(
                    "Não é permitido escalar mais de um servidor para o mesmo dia."
                )
        return True

    def validate_shift_usufruct_conflict(self):
        """Valida se existe um usufruto marcado para a data indicada no plantão"""
        usufructs = (
            Usufruct.objects.filter(
                Q(activity__acquisition_period__employee=self.employee),
                Q(start_date__range=[self.start_date, self.end_date])
                | Q(end_date__range=[self.start_date, self.end_date])
                | Q(start_date__lte=self.start_date) & Q(end_date__gte=self.end_date),
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                ]
            )
            .exclude()
        )
        if usufructs:
            raise Exception(
                f""" O periodo informado conflita com os dias de usufrutos programados/solicitados abaixo:\n
              {usufructs.first().activity.configuration.get_sub_type_of_usufruct_display()}
              {usufructs.first().start_date.strftime("%d/%m/%Y")} - {usufructs.first().end_date.strftime("%d/%m/%Y")}. """
            )
        else:
            return True

    def validate_shift_absence_conflict(self):
        absence = (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor=self.employee),
                Q(data_inicio__range=[self.start_date, self.end_date])
                | Q(data_fim__range=[self.start_date, self.end_date])
                | Q(data_inicio__lte=self.start_date) & Q(data_fim__gte=self.end_date),
            )
            .exclude(estado__in=[CANCELADO])
            .exclude(~Q(afastamento__afastamentoestudar=None))
            .exclude(
                dayoff_usufructs__status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                ]
            )
        )
        request_absence = (
            PortalRequestAbsence.objects.filter(
                Q(employee=self.employee),
                Q(start_date__range=[self.start_date, self.end_date])
                | Q(end_date__range=[self.start_date, self.end_date])
                | Q(start_date__lte=self.start_date) & Q(end_date__gte=self.end_date),
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            .exclude(absence__isnull=False)
        )
        if absence or request_absence:
            start_date = (
                absence.first().data_inicio
                if absence
                else request_absence.first().start_date
            )
            end_date = (
                absence.first().data_fim
                if absence
                else request_absence.first().end_date
            )
            title_absence = (
                TYPE_OF_LICENSE.get(absence.first().tipo)
                if absence
                else TYPE_OF_LICENSE.get(request_absence.first().type)
            )
            raise Exception(
                f""" O periodo informado conflita com os dias de afastamento agendados/solicitados abaixo:
              {title_absence} {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}. """
            )
        return True

    def validate_shift_manager_conflict(self):
        if (
            ShiftManager.objects.filter(
                Q(employee=self.employee),
                Q(start_date__range=[self.start_date, self.end_date])
                | Q(end_date__range=[self.start_date, self.end_date]),
            )
            .exclude(pk=self.pk)
            .exclude(
                server_duty__isnull=False,
                server_duty__status__in=[
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ],
            )
            .exists()
        ):
            raise Exception(
                "O plantonista já foi escalado em outro plantão no período informado."
            )
        return True

    def validar_tipo_posse(self):
        if self.employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            raise Exception("Não permitido escalar plantão de servidores para Membro.")
        return True

    def validar_lotacao(self):
        if not self.workplace or self.workplace.ativo == False:
            raise Exception(
                "Não é permitido escalar plantão, pois a lotação não foi selecionada ou está inativa!"
            )

    def validar_lotacao_serv(self):
        query = self.employee.lotacoes.filter(designacao=False)
        if not query.exists() or not query.filter(ativo=True).exists():
            raise Exception(
                "Não é permitido escalar plantão, pois o plantonista não possui lotação ou a lotação está inativa!"
            )

    def validar_anexo(self):
        if self.type_shift == TYPE_SHIFT_ELECTORAL and not self.anexo:
            raise Exception("Obrigatório informar anexo para plantão eleitoral.")
        return True

    def validar_periodo_eleitoral(self):
        config_periodo = ConfiguracaoPlantaoEleitoral.objects.filter(
            data=self.start_date, ativo=True
        ).exists()
        if self.type_shift == TYPE_SHIFT_ELECTORAL and not config_periodo:
            raise Exception(
                "Data do plantão fora do(s) dia(s) permitidos para cadastro."
            )
        return True

    def validate(self):
        log.info(f"self.type_shift: {self.type_shift}")
        self.validate_type_dti()
        self.validate_type_weekend()
        self.validate_type_weekend_days()
        self.validate_type_recess()
        self.validate_type_recess_days()
        # self.validate_type_electoral()
        self.validate_shift_usufruct_conflict()
        self.validate_shift_absence_conflict()
        self.validate_shift_manager_conflict()
        self.validar_tipo_posse()
        self.validar_lotacao()
        self.validar_anexo()
        self.validar_periodo_eleitoral()
        # self.validar_lotacao_serv()

    def save(self, *args, **kwargs):
        self.validate()
        if not self.owner:
            self.owner = employee_from_user(get_current_user())

        notifica_cadastro_plantao("CADASTRO_PLANTAO", self)
        super(ShiftManager, self).save(**kwargs)


class ApproveServerDuty(PortalRequest):
    """
    Classe reponsável pela criação das solicitações de plantões servidores
    """

    duty = models.ForeignKey(
        ShiftManager,
        related_name="server_duty",
        on_delete=models.PROTECT,
        verbose_name="Plantão",
    )

    def get_return_approver(self):
        return self.duty.owner

    def effectived_duty(self):
        factor = 2 if self.duty.type_shift == TYPE_SHIFT_ELECTORAL else 1

        date_range = NewDateRange.separar_datas_ano_distintos(
            self.duty.start_date, self.duty.end_date
        )
        with transaction.atomic():
            for obj_date in date_range:
                year_reference = obj_date["dt_inicio"].year
                last_acquisition_period = AcquisitionPeriod.objects.filter(
                    group_period__configuration__sub_type_of_usufruct=ONCALL_BONUS_SERVERS,
                    group_period__year_reference=year_reference,
                    employee=self.duty.employee,
                    group_period__configuration__type_of_duty=self.duty.type_shift,
                ).first()
                if last_acquisition_period:
                    attachment = AcquisitionPeriodAttachment(
                        acquisition_period=last_acquisition_period,
                        date_start=obj_date["dt_inicio"],
                        date_end=obj_date["dt_fim"],
                        days_law=obj_date["dias"] * factor,
                        information=f"Solicitação nº{self.pk}",
                        description=f"Plantão - {self.duty.get_type_shift_display()}",
                    )
                    attachment.save()
                else:
                    group_period = GroupPeriod.objects.filter(
                        configuration__sub_type_of_usufruct=ONCALL_BONUS_SERVERS,
                        configuration__type_of_duty=self.duty.type_shift,
                        year_reference=year_reference,
                    ).first()
                    if group_period:
                        acquisition_period = AcquisitionPeriod(
                            status=2,
                            start_date_acquisition=datetime.strptime(
                                f"{str(year_reference)}-01-01", "%Y-%m-%d"
                            ).date(),
                            start_date_fruition=datetime.strptime(
                                f"{str(year_reference)}-01-01", "%Y-%m-%d"
                            ).date(),
                            end_date_acquisition=datetime.strptime(
                                f"{str(year_reference)}-12-31", "%Y-%m-%d"
                            ).date(),
                            group_period=group_period,
                            employee=self.duty.employee,
                            paid_without_payroll=False,
                            indemnified=False,
                            note=False,
                            pendency=False,
                            continuous_period=False,
                            blocked=False,
                            automatic_created=False,
                        )
                        acquisition_period.save()
                        attachment = AcquisitionPeriodAttachment(
                            acquisition_period=acquisition_period,
                            date_start=obj_date["dt_inicio"],
                            date_end=obj_date["dt_fim"],
                            days_law=obj_date["dias"] * factor,
                            information=f"Solicitação nº{self.pk}",
                            description=f"Plantão - {self.duty.get_type_shift_display()}",
                        )
                        attachment.save()

                    else:
                        raise Exception(
                            f"Não foi encontrado grupo de plantão ({self.duty.get_type_shift_display()}) para referência {year_reference}."
                        )

    @classmethod
    def create(cls, duty, user):
        date = datetime.today().date()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=duty.employee,
                    request_type=REQUEST_TYPE_SERVER_DUTY,
                    date=date,
                    request=user,
                    duty=duty,
                    portal_request_type=PORTAL_SOLICITACAO_PLANTAO_TYPE,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            raise Exception(ex)


class PVFExercicioCumulativo(PortalRequest):
    substituicoes = models.ManyToManyField(
        "rh.MovimentacaoSubstituicao",
        verbose_name="Substituições",
        related_name="pvf_exercicio_cumulativos",
    )

    class Meta:
        db_table = "pvf_exerciciocumulativo"

    def cancelar(self):
        mov_substituicoes = self.substituicoes.all()
        mov_substituicoes.update(able_to_pay=False)
        for mov_substituicao in mov_substituicoes:
            self.substituicoes.remove(mov_substituicao)

    @classmethod
    def homologar_indeferir(cls, request, data):
        observation = data.get("observation", None)
        action = data.get("action")

        with transaction.atomic():
            if action == "defer":
                request.defered(data)
                if request.status == STS_EFFECTIVE:
                    user = get_current_user()
                    mov_substituicao = (
                        request.pvfexerciciocumulativo.substituicoes.filter(
                            indeferido=False
                        ).first()
                    )
                    Task.start(
                        efetivar_exercicio_cumulativo_task,
                        user=user.pk,
                        mov_substituicao=mov_substituicao.pk,
                    )
            elif action == "consolidated":
                cls.consolidar_exercicio_cumulativo(request.pvfexerciciocumulativo)
            elif action == "annotation":
                request.annoted(data)
            elif action == "dgp_observation":
                request.dgp_annoted_observation(observation)
            elif action == "return_applicant":
                request.return_applicant(observation)
            elif action == "return_approver":
                request.return_approver(observation)
                cls.desconsolidar_exercicio_cumulativo(request.pvfexerciciocumulativo)

    @classmethod
    def consolidar_exercicio_cumulativo(cls, solicitacao):
        user = get_current_user()
        mov_substituicoes_ids = solicitacao.substituicoes.filter(
            able_to_pay=True, consolidated=False, defer=False, indeferido=False
        ).values_list("pk", flat=True)

        if mov_substituicoes_ids.count() == 0:
            raise Exception("Não há exercícios cumulativos aptos para pagamentos")

        validacao_periodo = validar_periodo_vigente_exerc_cumul_subs()
        Task.start(
            consolidate_able_to_pay_employee_task,
            description=f"Consolidando cumulativos do servidor {solicitacao.employee}",
            user=user.id,
            employee_id=solicitacao.employee.pk,
            employee_movs_ids=list(mov_substituicoes_ids),
            periodo_cumul_subs_id=validacao_periodo["periodo"].pk,
        )

    @classmethod
    def efetivar_exercicio_cumulativo(cls, task=None, mov_substituicao=None):
        user = get_current_user()
        mov_sub = MovimentacaoSubstituicao.objects.get(pk=mov_substituicao)
        mov_sub_cons = mov_sub.substitutions_consolidated.first()

        task_calc = calculate_consolidated_task.apply_async(
            kwargs={
                "task": task.uuid,
                "hook": None,
                "user": user.pk,
                "mov_sub_consolidated_id": mov_sub_cons.pk,
            }
        )

        while not task_calc.ready():
            time.sleep(0.5)

        defer_consolidated_task.apply_async(
            kwargs={
                "task": task.uuid,
                "hook": None,
                "user": user.pk,
                "mov_sub_id": mov_sub_cons.pk,
            }
        )

    @classmethod
    def desconsolidar_exercicio_cumulativo(cls, solicitacao):
        user = get_current_user()
        mov_substituicao = solicitacao.substituicoes.filter(indeferido=False).first()
        mov_sub_cons = mov_substituicao.substitutions_consolidated.first()
        if mov_sub_cons:
            Task.start(
                desconsolidate_item_task,
                description=f"Desconsolidando exercícios cumulativos: {mov_sub_cons}",
                user=user.id,
                mov_sub_consolidated_id=mov_sub_cons.pk,
            )

    def send(self, observation=None):
        try:
            with transaction.atomic():
                action_type = REQUEST_ACT_SOLICITATION
                group = self.set_group_history()
                self.approval_flow()
                self.save()
                PortalRequestHistory.create_history(
                    observation=observation,
                    action=action_type,
                    request=self,
                    date=datetime.now(),
                    group=group,
                    user=get_current_user(),
                )
        except Exception as e:
            raise Exception(e)

    @classmethod
    def create(cls, params):
        """
        Função responsável por criar as soliticações de venda de exercicio cumulativo
        """
        user = get_current_user()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=user.servidor,
                    request_type=REQUEST_TYPE_CUMULATIVE_EXERCISE,
                    date=datetime.now().date(),
                    request=user,
                    portal_request_type=PORTAL_CUMULATIVE_EXERCISE_TYPE,
                )
                obj.approval_flow()
                obj.save()
                mov_substituicoes = MovimentacaoSubstituicao.objects.filter(
                    pk__in=eval(params.get("substituicoes_ids"))
                )
                for mov_substituicao in mov_substituicoes:
                    obj.substituicoes.add(mov_substituicao)
                    mov_substituicao.able_to_pay = True
                    mov_substituicao.save()

                PortalRequestHistory.create_history(
                    observation=params.get("observacao"),
                    action=REQUEST_ACT_OPEN_SOLICITANTION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)


class PVFCancelamentoTeletrabalho(PortalRequest):
    envios_teletrabalho = models.ManyToManyField(
        SendingTelework,
        related_name="pvf_envios_teletrabalho",
    )

    class Meta:
        db_table = "pvf_cancelamentoteletrabalho"

    def validar_solicitacao_desbloqueio(self):
        if PVFSolicitacaoDesbloqueioTeletrabalho.objects.filter(
            employee=self.employee, status__in=[STS_WAI_APPROVER, STS_WAI_EFFECTIVENESS]
        ).exists():
            raise Exception(
                "Solicitação não autorizada.Existe uma solicitação de desbloqueio em andamento."
            )
        return True

    def validate(self):
        self.validar_solicitacao_desbloqueio()

    def save(self, *args, **kwargs):
        self.validate()
        super(PVFCancelamentoTeletrabalho, self).save(**kwargs)

    def efetivar_cancelamento(self):
        from rh.teletrabalho.utils import (
            mov_status_teletrabalho_pendente,
            atualizar_possui_saldo_devedor,
        )

        self.envios_teletrabalho.update(cancelado_solicitacao=True)
        valores_dict = defaultdict(list)
        envios_valores = self.envios_teletrabalho.values(
            "pk", "work_plan", "reference_year", "reference_month"
        )
        [
            valores_dict[valor["work_plan"]].append(
                f"Solicitação {valor['pk']} ({valor['reference_month']}/{valor['reference_year']})"
            )
            for valor in envios_valores
        ]

        for valor in valores_dict:
            observacao = ", ".join(valores_dict[valor])
            mov_teletrabalho = MovimentacaoTeletrabalho.objects.get(pk=valor)
            mov_status_teletrabalho_pendente(mov_teletrabalho, observacao)

        atualizar_possui_saldo_devedor(mov_teletrabalho)

    @classmethod
    def create(cls, params):
        employee = get_current_user().servidor
        date = datetime.today().date()
        user = get_current_user()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_CANCELAMENTO_TELETRABALHO,
                    request=user,
                    date=date,
                    portal_request_type=PORTAL_CANCELAMENTO_TELETRABALHO_TYPE,
                )
                obj.approval_flow()
                obj.save()

                envios_teletrabalho = SendingTelework.objects.filter(
                    pk__in=eval(params.get("request_ids"))
                )
                for teletrabalho in envios_teletrabalho:
                    obj.envios_teletrabalho.add(teletrabalho)
                    teletrabalho.save()

                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            log.error(ex)
            raise Exception(ex)


class PSPendencies(models.Model):
    type_report = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "TYPE_REPORT"),
        verbose_name="Tipo relatório",
    )
    reference = models.CharField(max_length=7, verbose_name="Referência")
    enrollment = models.CharField(max_length=20, verbose_name="Matricula")
    name = models.CharField(max_length=250, verbose_name="Nome")
    balance_negative = models.CharField(
        max_length=12, verbose_name="Total Negativo Mês", blank=True, null=True
    )
    date = models.DateField(verbose_name="Data", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.reference}"


class EspelhoPlanoTeletrabalhoSemestral(models.Model):
    servidor = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="plano_teletrabalho_semestral",
        on_delete=models.PROTECT,
    )
    tipo_ato = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_ACT"), verbose_name="Tipo Ato"
    )
    ato = models.ForeignKey(
        "rh.Publicacao", null=True, blank=True, on_delete=models.PROTECT
    )
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim", blank=True, null=True)
    gedoc = models.TextField(verbose_name="GEDOC", blank=True, null=True)


class RelatorioSemestralTeletrabalho(PortalRequest):
    periodo_envio = models.ForeignKey(
        ConfigPeriodoEnvioRelatoriosSemestrais,
        on_delete=models.PROTECT,
        verbose_name="Período de Envio",
        related_name="relatorio_semestral_teletrabalho",
    )
    espelho_mov_teletrabalhos = models.ManyToManyField(
        EspelhoPlanoTeletrabalhoSemestral,
        related_name="relatorios_semestrais_teletrabalho",
    )
    dificuldades_servidores = models.TextField(
        "Dificuldades Observadas em Relação aos Servidores"
    )
    medidas_dirimir_dificuldades_servidores = models.TextField(
        "Medidas para Dirimir Dificuldades dos Servidores"
    )
    dificuldades_facilidades_gestor = models.TextField(
        "Dificuldades e Facilidades na Gestão do Teletrabalho"
    )
    medidas_dirimir_dificuldades_gestor = models.TextField(
        "Medidas para Dirimir Dificuldades do Gestor"
    )
    resultados_alcancados = models.TextField("Resultados Alcançados")
    sugestoes_melhorias = models.TextField("Sugestões de Melhorias")

    class Meta:
        verbose_name = "Relatório Semestral de Teletrabalho"

    def validar_perido_servidor(self):
        if RelatorioSemestralTeletrabalho.objects.filter(
            periodo_envio=self.periodo_envio, employee=self.employee
        ).exists():
            msg = "Já existe um relatório enviado nesse período."
            raise Exception(msg)
        return True

    def validate(self):
        self.validar_perido_servidor()

    def save(self, *args, **kwargs):
        self.validate()
        super(RelatorioSemestralTeletrabalho, self).save(**kwargs)

    @classmethod
    def criar_objeto_espelho_mov_teletrabalho(cls, mov_teletrabalhos):
        objetos = []
        for teletrabalho in mov_teletrabalhos:
            objetos.append(
                EspelhoPlanoTeletrabalhoSemestral(
                    servidor=teletrabalho.servidor,
                    tipo_ato=teletrabalho.tipo_ato,
                    ato=teletrabalho.publicacao_movimentacao,
                    data_inicio=teletrabalho.data_inicio,
                    data_fim=teletrabalho.data_fim,
                    gedoc=teletrabalho.gedoc,
                )
            )
        objetos_criados = EspelhoPlanoTeletrabalhoSemestral.objects.bulk_create(objetos)
        return objetos_criados

    @classmethod
    def create(cls, params):
        servidor = get_current_user().servidor
        data = datetime.today().date()
        usuario = get_current_user()
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
        try:
            with transaction.atomic():
                obj = cls(
                    employee=servidor,
                    request_type=REQUEST_TYPE_RELATORIO_TELE_SEMESTRAL,
                    request=usuario,
                    date=data,
                    portal_request_type=PORTAL_RELATORIO_TELETRABALHO_SEMESTRAL_TYPE,
                    dificuldades_servidores=params["dificuldades_servidores"],
                    medidas_dirimir_dificuldades_servidores=params[
                        "medidas_dirimir_dificuldades_servidores"
                    ],
                    dificuldades_facilidades_gestor=params[
                        "dificuldades_facilidades_gestor"
                    ],
                    medidas_dirimir_dificuldades_gestor=params[
                        "medidas_dirimir_dificuldades_gestor"
                    ],
                    resultados_alcancados=params["resultados_alcancados"],
                    sugestoes_melhorias=params["sugestoes_melhorias"],
                    periodo_envio=periodo,
                )
                obj.approval_flow()
                obj.save()

                mov_teletrabalhos = get_teletrabalhos_semestrais(servidor)
                espelho_mov_teletrabalhos = cls.criar_objeto_espelho_mov_teletrabalho(
                    mov_teletrabalhos
                )
                for teletrabalho in espelho_mov_teletrabalhos:
                    obj.espelho_mov_teletrabalhos.add(teletrabalho)

                PortalRequestHistory.create_history(
                    observation="",
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=usuario,
                )
                return obj

        except Exception as ex:
            log.error(ex)
            raise Exception(ex)


class PVFSolicitacaoCreditoFolga(PortalRequest):
    data_inicio = models.DateField(verbose_name="Data Início", db_index=True)
    data_fim = models.DateField(verbose_name="Data Fim", db_index=True)
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_solicitacao_folga",
    )
    tipo_folga = models.IntegerField(
        choices=Choice.get_choices_for("pvf", "TIPO_FOLGA"), verbose_name="Tipos Folgas"
    )

    class Meta:
        db_table = "pvf_solicitacaofolga"

    def get_dias_saldo_anexo(self, total_perido):
        """
        Função que retorna o total de dias que será adicionado ao anexo
        Args:
            total_perido:int
        Returns:
           total_perido:int
        """
        dias_saldo = NewDateRange(self.data_inicio, self.data_fim).days
        if self.tipo_folga == TIPO_FOLGA_JUIZADO_TORCEDOR:
            total_perido = self.get_total_folga_compensatoria() + total_perido
            if total_perido >= MAX_SALDO_FOLGA_PLANTAO:
                return 0
            elif (total_perido + dias_saldo) > MAX_SALDO_FOLGA_PLANTAO:
                return MAX_SALDO_FOLGA_PLANTAO - total_perido
            else:
                return dias_saldo
        return dias_saldo

    def get_total_folga_compensatoria(self):
        """
        Função que retorna o total de dias do perído acquisitivo de folga compensatória
        Returns:
           total_perido:int
        """
        ano_referencia = self.data_inicio.year
        config = Configuration.objects.filter(
            sub_type_of_usufruct=COMP_CLEARANCE_MEMBERS
        ).first()
        perido_acquisitivo = AcquisitionPeriod.objects.filter(
            group_period__configuration=config,
            employee=self.employee,
            group_period__year_reference=ano_referencia,
        ).first()
        if perido_acquisitivo:
            return perido_acquisitivo.days
        return 0

    def validar_periodo_conflitado(self):
        """
        Função que valida se há conflito com outra solicitação de folga
        """
        solicitacoes = (
            PVFSolicitacaoCreditoFolga.objects.filter(
                Q(employee=self.employee),
                Q(data_inicio__range=[self.data_inicio, self.data_fim])
                | Q(data_fim__range=[self.data_inicio, self.data_fim])
                | Q(data_inicio__lte=self.data_inicio) & Q(data_fim__gte=self.data_fim),
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            .exclude(pk=self.pk)
        )
        if solicitacoes.exists():
            solicitacao = solicitacoes.first()
            raise Exception(
                f""" O periodo informado conflita com os dia(s) solicitados abaixo:
              {solicitacao.get_tipo_folga} {solicitacao.data_inicio.strftime("%d/%m/%Y")} - {solicitacao.data_fim.strftime("%d/%m/%Y")}. """
            )
        return True

    def validate(self):
        self.validar_periodo_conflitado()

    def save(self, *args, **kwargs):
        self.validate()
        super(PVFSolicitacaoCreditoFolga, self).save(**kwargs)

    def efetivar(self):
        ano_referencia = self.data_inicio.year
        tipo_folga_plantao = CONFIG_SOLICITACAO_FOLGA_PLANTAO.get(self.tipo_folga, None)
        fator = 2 if self.tipo_folga == TIPO_FOLGA_AUXILIO_ELEITORAL else 1
        with transaction.atomic():
            ultimo_peridodo_acquisitivo = AcquisitionPeriod.objects.filter(
                group_period__configuration__sub_type_of_usufruct=COMP_CLEARANCE_MEMBERS,
                group_period__year_reference=ano_referencia,
                employee=self.employee,
                group_period__configuration__type_of_duty=tipo_folga_plantao,
            ).first()
            if ultimo_peridodo_acquisitivo:
                anexo = AcquisitionPeriodAttachment(
                    acquisition_period=ultimo_peridodo_acquisitivo,
                    date_start=self.data_inicio,
                    date_end=self.data_fim,
                    days_law=self.get_dias_saldo_anexo(ultimo_peridodo_acquisitivo.days)
                    * fator,
                    description=f"Plantão - {self.get_tipo_folga_display()}",
                )
                anexo.save()
            else:
                grupo_periodo = GroupPeriod.objects.filter(
                    configuration__sub_type_of_usufruct=COMP_CLEARANCE_MEMBERS,
                    configuration__type_of_duty=tipo_folga_plantao,
                    year_reference=ano_referencia,
                ).first()
                if grupo_periodo:
                    peridodo_acquisitivo = AcquisitionPeriod(
                        status=2,
                        start_date_acquisition=datetime.strptime(
                            f"{str(ano_referencia)}-01-01", "%Y-%m-%d"
                        ).date(),
                        start_date_fruition=datetime.strptime(
                            f"{str(ano_referencia)}-01-01", "%Y-%m-%d"
                        ).date(),
                        end_date_acquisition=datetime.strptime(
                            f"{str(ano_referencia)}-12-31", "%Y-%m-%d"
                        ).date(),
                        group_period=grupo_periodo,
                        employee=self.employee,
                        paid_without_payroll=False,
                        indemnified=False,
                        note=False,
                        pendency=False,
                        continuous_period=False,
                        blocked=False,
                        automatic_created=False,
                    )
                    peridodo_acquisitivo.save()
                    anexo = AcquisitionPeriodAttachment(
                        acquisition_period=peridodo_acquisitivo,
                        date_start=self.data_inicio,
                        date_end=self.data_fim,
                        days_law=self.get_dias_saldo_anexo(peridodo_acquisitivo.days)
                        * fator,
                        description=f"Plantão - {self.get_tipo_folga_display()}",
                    )
                    anexo.save()

                else:
                    raise Exception(
                        f"Não foi encontrado grupo de plantão ({self.get_tipo_folga_display()}) para referência {ano_referencia}."
                    )

    @classmethod
    def create(cls, dados):
        user = get_current_user()
        servidor = get_current_user().servidor
        try:
            with transaction.atomic():
                obj = cls(
                    employee=servidor,
                    request_type=REQUEST_TYPE_SOLICITACAO_CREDITO_FOLGA,
                    date=datetime.today().date(),
                    data_inicio=dados.get("data_inicio"),
                    data_fim=dados.get("data_fim"),
                    anexo=(
                        File.objects.get(pk=dados.get("anexo"))
                        if dados.get("anexo")
                        else None
                    ),
                    tipo_folga=dados.get("tipo_folga"),
                    request=user,
                    portal_request_type=PORTAL_SOLICITCAO_CREDITO_SALDO_TYPE,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @classmethod
    def update(cls, dados, instance):
        user = get_current_user()
        try:
            with transaction.atomic():
                instance.data_inicio = dados.get("data_inicio")
                instance.data_fim = dados.get("data_fim")
                instance.save()

                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_EDITAR,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)


class PVFSolicitacaoCreditoDispensaEleitoral(PortalRequest):
    data_inicio = models.DateField(verbose_name="Data Início", db_index=True)
    data_fim = models.DateField(verbose_name="Data Fim", db_index=True)
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_solicitacao_dispensa_eleitoral",
    )
    observacao = models.TextField(verbose_name="Observação", blank=True, null=True)

    class Meta:
        db_table = "pvf_solicitacaodispensaeleitoral"

    def validar_datas(self):
        if not self.data_inicio or not self.data_fim:
            raise Exception(f"É necessário informar data início e fim!")

    def validar_inicio_fim(self):
        if self.data_fim and self.data_inicio > self.data_fim:
            raise Exception(f"Data início deve ser menor que data fim!")

    def validar_data_posse(self):
        if self.data_inicio < self.employee.data_exercicio:
            raise Exception(
                f"Data início/fim não pode ser menor que a data de posse: {self.employee.data_exercicio.strftime('%d/%m/%Y')}!"
            )

    def validar_periodo_conflitado(self):
        """
        Função que valida se há conflito com outra solicitação de crédito de dispensa eleitoral
        """
        solicitacoes = (
            PVFSolicitacaoCreditoDispensaEleitoral.objects.filter(
                Q(employee=self.employee),
                Q(data_inicio__range=[self.data_inicio, self.data_fim])
                | Q(data_fim__range=[self.data_inicio, self.data_fim])
                | Q(data_inicio__lte=self.data_inicio) & Q(data_fim__gte=self.data_fim),
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            .exclude(pk=self.pk)
        )
        if solicitacoes.exists():
            solicitacao = solicitacoes.first()
            raise Exception(
                f""" O periodo informado conflita com os dia(s) solicitados abaixo:
              {solicitacao.data_inicio.strftime("%d/%m/%Y")} - {solicitacao.data_fim.strftime("%d/%m/%Y")}. """
            )
        return True

    def validar_conflito_anexos(self):
        """
        Função que valida se há conflito com outro anexo do período aquisitivo
        """
        query = AcquisitionPeriodAttachment.objects.filter(
            Q(acquisition_period__employee=self.employee),
            Q(
                acquisition_period__group_period__configuration__type_of_usufruct=4
            ),  # Folga Eleitoral
            Q(date_start__range=[self.data_inicio, self.data_fim])
            | Q(date_end__range=[self.data_inicio, self.data_fim])
            | Q(date_start__lte=self.data_inicio) & Q(date_end__gte=self.data_fim),
        )
        if query.exists():
            raise Exception("Já existe anexo cadastrado para o período informado!")

    def validar(self):
        self.validar_datas()
        self.validar_inicio_fim()
        self.validar_data_posse()
        self.validar_periodo_conflitado()
        self.validar_conflito_anexos()

    def save(self, *args, **kwargs):
        self.validar()
        super(PVFSolicitacaoCreditoDispensaEleitoral, self).save(**kwargs)

    def get_qnt_dias(self):
        if self.data_inicio and self.data_fim:
            return NewDateRange(self.data_inicio, self.data_fim).days
        return 0

    @classmethod
    def criar(cls, dados):
        user = get_current_user()
        servidor = get_current_user().servidor
        try:
            with transaction.atomic():
                obj = cls(
                    employee=servidor,
                    request_type=REQUEST_TYPE_CREDITO_DISPENSA_ELEITORAL,
                    date=datetime.today().date(),
                    data_inicio=datetime.strptime(
                        dados.get("data_inicio"), "%Y-%m-%d"
                    ).date(),
                    data_fim=datetime.strptime(
                        dados.get("data_fim"), "%Y-%m-%d"
                    ).date(),
                    anexo=(
                        File.objects.get(pk=dados.get("anexo"))
                        if dados.get("anexo")
                        else None
                    ),
                    observacao=(
                        dados.get("observacao") if dados.get("observacao") else None
                    ),
                    request=user,
                    portal_request_type=PORTAL_SOLICITCAO_CREDITO_DISPENSA_ELEITORAL,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return obj

        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @classmethod
    def reenviar(cls, dados, instance):
        user = get_current_user()
        try:
            with transaction.atomic():
                instance.data_inicio = datetime.strptime(
                    dados.get("data_inicio"), "%Y-%m-%d"
                ).date()
                instance.data_fim = datetime.strptime(
                    dados.get("data_fim"), "%Y-%m-%d"
                ).date()
                instance.observacao = (
                    dados.get("observacao") if dados.get("observacao") else None,
                )
                instance.anexo = (
                    File.objects.get(pk=dados.get("anexo"))
                    if dados.get("anexo")
                    else None
                )
                instance.approval_flow()
                instance.save()

                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    def efetivar(self):
        self.validar_conflito_anexos()
        ano_referencia = self.data_inicio.year
        log.info(f"ano_referencia: {ano_referencia}")
        # tipo_folga_plantao = CONFIG_SOLICITACAO_FOLGA_PLANTAO.get(self.tipo_folga, None)
        with transaction.atomic():
            ultimo_peridodo_aquisitivo = AcquisitionPeriod.objects.filter(
                group_period__configuration__sub_type_of_usufruct=ELECTORAL_SLACK,
                group_period__year_reference=ano_referencia,
                employee=self.employee,
                group_period__configuration__type_of_usufruct=4,  # Folga Eleitoral
            ).first()
            if ultimo_peridodo_aquisitivo:
                log.info(f"ultimo_peridodo_aquisitivo: {ultimo_peridodo_aquisitivo}")
                anexo = AcquisitionPeriodAttachment(
                    acquisition_period=ultimo_peridodo_aquisitivo,
                    date_start=self.data_inicio,
                    date_end=self.data_fim,
                    days_law=self.get_qnt_dias() * 2,
                    description=f"Solicitação Nº {self.pk}",
                )
                anexo.save()
                log.info(f"anexo: {anexo}")
            else:
                grupo_periodo = GroupPeriod.objects.filter(
                    configuration__sub_type_of_usufruct=ELECTORAL_SLACK,
                    configuration__type_of_usufruct=4,  # Folga Eleitoral
                    year_reference=ano_referencia,
                ).first()
                if grupo_periodo:
                    peridodo_aquisitivo = AcquisitionPeriod(
                        status=2,
                        start_date_acquisition=datetime.strptime(
                            f"{str(ano_referencia)}-01-01", "%Y-%m-%d"
                        ).date(),
                        start_date_fruition=datetime.strptime(
                            f"{str(ano_referencia)}-01-01", "%Y-%m-%d"
                        ).date(),
                        end_date_acquisition=datetime.strptime(
                            f"{str(ano_referencia)}-12-31", "%Y-%m-%d"
                        ).date(),
                        group_period=grupo_periodo,
                        employee=self.employee,
                        paid_without_payroll=False,
                        indemnified=False,
                        note=False,
                        pendency=False,
                        continuous_period=False,
                        blocked=False,
                        automatic_created=False,
                    )
                    peridodo_aquisitivo.save()
                    anexo = AcquisitionPeriodAttachment(
                        acquisition_period=peridodo_aquisitivo,
                        date_start=self.data_inicio,
                        date_end=self.data_fim,
                        days_law=self.get_qnt_dias() * 2,
                        description=f"Solicitação Nº {self.pk}",
                    )
                    anexo.save()

                else:
                    raise Exception(
                        f"Não foi encontrado grupo de plantão ({self.get_tipo_folga_display()}) para referência {ano_referencia}."
                    )


class PVFSolicitacaoAuxilioCrecheDepenIR(PortalRequest):
    pessoa_familia = models.ForeignKey(
        PessoaFisica, related_name="pvf_auxiliocrechedepenir", on_delete=models.PROTECT
    )
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_auxiliocrechedepenir",
    )
    dependente_aux_creche = models.BooleanField(
        "Dependente do Auxílio Creche", default=False
    )
    dependente_ir = models.BooleanField("Dependente do IR", default=False)
    capacidade = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CAPACITY"), null=True, default=1
    )
    tipo_parentesco = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Dependente Tipo IRRF",
        null=True,
        blank=True,
    )
    dependente_tipo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        verbose_name="Dependente Tipo",
        null=True,
        blank=True,
    )
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "pvf_solicitacaoauxiliocrechedepenir"

    def save(self, *args, **kwargs):
        self.validate_conflict_dependent_ir_childcare(self.pessoa_familia)
        self.validar_conflito_solicitacao_creche_ir()
        super(PVFSolicitacaoAuxilioCrecheDepenIR, self).save(**kwargs)

    def validar_conflito_solicitacao_creche_ir(self):
        query = PVFSolicitacaoAuxilioCrecheDepenIR.objects.filter(
            pessoa_familia=self.pessoa_familia
        ).exclude(status__in=[STS_CANCELED_DGP, STS_CANCELED_APPLICANT, STS_REJECTED])
        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise Exception(
                "Já existe uma solicitação de auxílio creche ou IR para esse dependente."
            )
        return True

    def efetivar(self):
        try:
            with transaction.atomic():
                dependente = Dependente.objects.filter(
                    pessoa_fisica=self.pessoa_familia
                ).first()
                if not dependente:
                    dependente = Dependente(
                        pessoa_fisica=self.pessoa_familia,
                        responsavel=self.employee.pessoa_fisica,
                        servidor=self.employee,
                        grau_parentesco=self.tipo_parentesco,
                        capacidade=self.capacidade,
                        dep_ir=self.dependente_ir,
                        tipo=self.dependente_tipo,
                        auxilio_creche=self.dependente_aux_creche,
                    )
                    dependente.save()
                else:
                    dependente.grau_parentesco = self.tipo_parentesco
                    dependente.capacidade = self.capacidade
                    dependente.dep_ir = self.dependente_ir
                    dependente.tipo = self.dependente_tipo
                    dependente.auxilio_creche = self.dependente_aux_creche
                    dependente.save()
                self.cria_dependencia(dependente)
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @classmethod
    def create(cls, dados):
        usuario = get_current_user()
        servidor = get_current_user().servidor
        try:
            with transaction.atomic():
                obj = cls(
                    employee=servidor,
                    date=datetime.today().date(),
                    request_type=REQUEST_TYPE_SOLICITACAO_AUX_CRECHE_DEPEN_IR,
                    pessoa_familia=PessoaFisica.objects.get(
                        pk=dados.get("pessoa_familia_id")
                    ),
                    anexo=(
                        File.objects.get(pk=dados.get("anexo_id"))
                        if dados.get("anexo_id")
                        else None
                    ),
                    dependente_aux_creche=dados.get("dependente_aux_creche", False),
                    dependente_ir=dados.get("dependente_ir", False),
                    capacidade=dados.get("capacidade", None),
                    tipo_parentesco=dados.get("tipo_parentesco", None),
                    dependente_tipo=dados.get("dependente_tipo", None),
                    observacao=dados.get("observacao", None),
                    request=usuario,
                    portal_request_type=PORTAL_SOLICITACAO_AUX_CRECHE_DEPEN_IR,
                )
                obj.approval_flow()
                obj.save()
                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=usuario,
                )
                return obj
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @classmethod
    def reenviar(cls, dados):
        user = get_current_user()
        try:
            with transaction.atomic():
                instancia = PVFSolicitacaoAuxilioCrecheDepenIR.objects.get(
                    pk=dados.get("id")
                )
                instancia.pessoa_familia = PessoaFisica.objects.get(
                    pk=dados.get("pessoa_familia_id")
                )
                instancia.anexo = (
                    File.objects.get(pk=dados.get("anexo_id"))
                    if dados.get("anexo_id")
                    else None
                )
                instancia.dependente_aux_creche = dados.get(
                    "dependente_aux_creche", False
                )
                instancia.dependente_ir = dados.get("dependente_ir", False)
                instancia.capacidade = dados.get("capacidade", None)
                instancia.tipo_parentesco = dados.get("tipo_parentesco", None)
                instancia.dependente_tipo = dados.get("dependente_tipo", None)
                instancia.observacao = dados.get("observacao", None)
                instancia.approval_flow()
                instancia.save()
                PortalRequestHistory.create_history(
                    observation=dados.get("observation"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=instancia,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    def buscar_data_inicio_ir(self):
        """função que busca a data inicio de dependencia de IR
        Returns:
            date
        """
        data_atual = datetime.now()
        dia_corte = Item.objects.get(key="data_corte_aux_creche_ir").value
        # Verificar o dia do mês
        if data_atual.day <= int(dia_corte):
            dia_do_mes = 1
            mes = data_atual.month
            ano = data_atual.year
        else:
            mes_subsequente = data_atual.replace(day=28) + timedelta(days=4)
            dia_do_mes = 1
            mes = mes_subsequente.month
            ano = mes_subsequente.year
        # Criar uma nova data com o dia 1 do mês calculado
        data_inicio = datetime(year=ano, month=mes, day=dia_do_mes).date()
        return data_inicio

    def cria_dependencia(self, depedente):
        """função que a dependencia vinculando ao dependente
        Args:
            dependente
        Returns:
        """
        if self.pessoa_familia == self.employee.pessoa_fisica:
            raise Exception(
                "Não é possível informar como dependente o mesmo usuário solicitante."
            )

        if self.dependente_aux_creche:
            dependencia = Dependencia(
                dependente=depedente,
                tipo=TYPE_CHILDCARE_ASSISTENCE,
                data_inicio=self.date,
                idade_limite=CHILD_AGE_LIMIT,
                origem="vdf",
            )
            dependencia.save()
        if self.dependente_ir:
            dependencia = Dependencia(
                dependente=depedente,
                tipo=TYPE_INCOMING_TAX,
                data_inicio=self.buscar_data_inicio_ir(),
                origem="vdf",
            )
            dependencia.save()


class PVFSolicitacaoDesbloqueioTeletrabalho(PortalRequest):
    plano_teletrabalho = models.ForeignKey(
        MovimentacaoTeletrabalho,
        on_delete=models.PROTECT,
        related_name="solicitacao_desbloqueio_tele",
        verbose_name="Plano de Trabalho",
    )
    referencia_mes = models.IntegerField(verbose_name="Referência mês")
    referencia_ano = models.IntegerField(verbose_name="Referência ano")

    class Meta:
        db_table = "pvf_solicitacaodesbloqueioteletrabalho"

    def efetivar(self, observation):
        from rh.teletrabalho.utils import desbloquear_mov_teletrabalho

        try:
            observacao = f"Solicitação nº {self.pk} - {observation}"
            desbloquear_mov_teletrabalho(self.plano_teletrabalho, observacao=observacao)
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    def indeferir(self, data, observation):
        from rh.teletrabalho.utils import revogar_mov_teletrabalho

        try:
            data_fim = data.get("teletrabalho_desbloqueio_data_encerramento")
            qtd_prazo_impedimento = data.get(
                "teletrabalho_desbloqueio_prazo_impedimento"
            )
            observacao = f"Solicitação nº {self.pk} - {observation}"
            revogar_mov_teletrabalho(
                self.plano_teletrabalho,
                qtd_prazo_impedimento,
                data_fim,
                observacao=observacao,
            )
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @property
    def solicitacao_andamento(self):
        return PortalRequest.objects.filter(
            employee=self.employee,
            request_type=REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
            status__in=[STS_WAI_APPROVER, STS_WAI_EFFECTIVENESS],
        ).exists()

    def save(self, *args, **kwargs):
        self.validar_solicitacao_andamento()
        super(PVFSolicitacaoDesbloqueioTeletrabalho, self).save(**kwargs)

    def validar_solicitacao_andamento(self):
        if self.solicitacao_andamento:
            raise Exception("Já existe uma solicitação de desbloqueio em andamento.")
        return True

    @classmethod
    def criar(cls, dados):
        usuario = get_current_user()
        servidor = get_current_user().servidor
        try:
            with transaction.atomic():
                anexo_ids = dados.get(
                    "anexos", [dados.get("anexo_id")] if dados.get("anexo_id") else []
                )
                anexos = [File.objects.get(pk=anexo_id) for anexo_id in anexo_ids]
                mov_tele = MovimentacaoTeletrabalho.objects.filter(
                    servidor=servidor, situacao=STATUS_TELETRABALHO_BLOQUEADO
                ).first()
                ref_mes, ref_ano = SendingTelework.get_reference_year_month(
                    employee=servidor
                )
                obj = cls(
                    employee=servidor,
                    date=datetime.today().date(),
                    request_type=REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
                    request=usuario,
                    portal_request_type=PORTAL_SOLICITACAO_DESBLOQUEIO_TELETRABALHO,
                    plano_teletrabalho=mov_tele,
                    referencia_mes=ref_mes,
                    referencia_ano=ref_ano,
                )
                obj.approval_flow(action=REQUEST_ACT_SOLICITATION)
                obj.save()
                PortalRequestHistory.create_history(
                    observation=dados.get("observacao"),
                    action=REQUEST_ACT_SOLICITATION,
                    request=obj,
                    date=datetime.now(),
                    group=None,
                    user=usuario,
                    anexos=anexos,
                )
                return obj
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)

    @classmethod
    def criar_solicitacao_sub(cls, mov_tele, observacao, anexo_id):
        usuario = get_current_user()
        try:
            with transaction.atomic():
                anexos = [File.objects.get(pk=anexo_id)] if anexo_id else []
                ref_mes, ref_ano = SendingTelework.get_reference_year_month(
                    employee=mov_tele.servidor
                )
                obj = cls(
                    employee=mov_tele.servidor,
                    date=datetime.today().date(),
                    request_type=REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
                    request=usuario,
                    portal_request_type=PORTAL_SOLICITACAO_DESBLOQUEIO_TELETRABALHO,
                    step_current=REQUEST_STEP_GER_DEV,
                    plano_teletrabalho=mov_tele,
                    referencia_mes=ref_mes,
                    referencia_ano=ref_ano,
                )
                obj.approval_flow(action=REQUEST_ACT_SEND_SUB)
                obj.save()
                PortalRequestHistory.create_history(
                    observation=observacao,
                    action=REQUEST_ACT_SEND_SUB,
                    request=obj,
                    date=datetime.now(),
                    group=GROUP_GER_DEV,
                    user=usuario,
                    anexos=anexos,
                )
                return obj
        except Exception as ex:
            log.error(ex)
            raise Exception(ex)


auditlog.register(PortalRequest)
auditlog.register(PortalRequestUsufruct)
auditlog.register(PortalRequestAbsence)
auditlog.register(PortalRequestWorkload)
auditlog.register(PortalRequestHistory)
auditlog.register(PortalCancelSchedule)
auditlog.register(PortalRetificationSchedule)
auditlog.register(PortalRequestSubstitute)
auditlog.register(PortalRequestProgression)
auditlog.register(PortalRequestProgressionH)
auditlog.register(SendingTimeSheet)
auditlog.register(SendingTelework)
auditlog.register(PVFExercicioCumulativo)
auditlog.register(PVFCancelamentoTeletrabalho)
auditlog.register(PVFSolicitacaoCreditoFolga)
auditlog.register(PVFSolicitacaoAuxilioCrecheDepenIR)
auditlog.register(PVFSolicitacaoDesbloqueioTeletrabalho)
auditlog.register(PVFSolicitacaoCreditoDispensaEleitoral)
auditlog.register(RelatorioSemestralTeletrabalho)
auditlog.register(ApproveServerDuty)
auditlog.register(PointJustification)
auditlog.register(MarkTelework)
auditlog.register(ShiftManager)
