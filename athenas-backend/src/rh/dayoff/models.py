# -.- coding: utf-8 -.-
import decimal
import json
import os
import datetime as dt
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields as generic
from django.db import models, transaction
from django.db.models import F, Q, Sum
from django.db.models.query import QuerySet

from contrib.daterange import NewDateRange
from contrib.decorator import deprecated
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger, get_object_or_none
from edocs.protocolo.models import Protocolo as Protocol
from engine.mq.models import Task
from engine.notification.models import Message, Notification
from ged.models import Arquivo as File
from rh.afastamento.models import CANCELED, SCHEDULED, BaseLicencaAfastamento
from rh.dayoff.const import (
    ACQP_CREATION_CREATED,
    ACQP_CREATION_UPDATED,
    ACQP_CREATION_ERROR,
    ACQP_FINISHED,
    ACQP_INDEMNIFIED,
    ACQP_PRESCRIBED,
    ACQP_PROGRESS,
    ACQP_WAIT,
    ACQUISITION_PERIOD_STATUS_CHOICE,
    ACT_BOOK,
    ACT_CHANGE,
    ACT_INDEMNIFY,
    ACT_INTERRUPT,
    ACT_SELL,
    ACT_BOOK_SELL,
    ACT_RECTIFY,
    ACT_REMAINING,
    ACT_CORRECT,
    ACT_ST_AUTHORIZED,
    ACT_ST_AUTHORIZED_M,
    ACT_ST_CANCELED,
    ACT_ST_CREATED,
    ACT_ST_HOMOLOGATED,
    ACT_ST_NOT_AUTHORIZED,
    ACT_ST_SOLD,
    ACT_SUSPEND,
    ACTIVITY_SM,
    ACTIVITY_STATUS_CHOICE,
    ACTIVITY_TYPE_CHOICE,
    AP_SM,
    AUTO_HOMOLOGATION,
    AUTO_HOMOLOGATION_AFTER_SCALE,
    AUTO_HOMOLOGATION_NOT,
    BIRTHDAY_BREAK,
    BLOOD_DONATION_USUFRUCT,
    COMP_CLEARANCE_MEMBERS,
    COMP_CLERARANCE_SERVERS,
    COMP_VACATION_MEMBERS,
    CONF_VACATION,
    CONFIGURATION_TO_ANNOTATION_CLASS,
    CONFIGURATION_TO_DEPARTURE_CLASS,
    DAYOFF_ICONS_THEME,
    ELECTORAL_SLACK,
    FORENSIC_RECESS,
    INDIVIDUAL_VACATION,
    INTERNS_RECESS,
    INTERNSHIP_COMPETITION,
    ONCALL_BONUS_SERVERS,
    PAYMENT_CHECKED,
    PAYMENT_DECLINED,
    PAYMENT_FINALIZED,
    PREMIUM_LICENSE,
    RESIDENT_RECESS,
    SUBSTITUTE_PROMOTER_CONTEST,
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_CHANGED,
    USU_CHANGING,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_NEW,
    USU_NOT_AUTHORIZED,
    USU_SM,
    USU_SOLD,
    USU_SUBSTITUTE,
    USU_SUSPENDED,
    USUFRUCT_STATUS_CHOICE,
    CONFIGURATION_CHOICE,
    CONF_ELECTORAL_SLACK,
    CONF_DUTTY,
    ORIGIN_REQUEST,
    PORTAL,
    MANUAL,
    ACT_CANCEL,
    USUFRUCT_STATUS_MODIFIED,
)
from rh.dayoff.contrib import (
    has_perm_cancel_admin,
    has_perm_homologate,
    has_perm_homologate_admin,
    has_perm_mediate_chief,
    has_perm_super_delete,
    is_current_user_admin,
    is_current_user_system,
    user_has_perm_authorize_admin,
)
from rh.gfp.models import Folha, FolhaEvento, FolhaTipo
from rh.models import (
    AnotacaoFerias,
    AnotacaoFolgaAniversario,
    AnotacaoFolgaCompensacao,
    AnotacaoFolgaEleitoral,
    AnotacaoGeral,
    AnotacaoPlantao,
    AnotacaoRecesso,
)
from rh.models import Publicacao as Publication
from rh.models import Servidor, ServidorLotacao
from rh.gfp.models import Periodo
from rh.pvf.const import REGULAR_VACATIONS
from standard.models import AuditTimestampModel, Choice, ClassCode
from auditlog.registry import auditlog

from .utils import (
    action_check,
    notify,
    working_days,
    competence_paid_unicode,
    get_max_parcel_number,
    reordenar_numero_parcela,
)

from rh.dayoff.model_utils.activity import (
    set_pagamento_usufruto_retificado_suspensao,
    set_pagamento_usufruto_futuro,
    set_pagamento_de_competencia_baseado_em_periodo,
)

log = getLogger(__name__)


class ConfigurationManager(models.Manager):

    def get_by_natural_key(self, title, type_of_usufruct, *args):
        return self.get(title=title, type_of_usufruct=type_of_usufruct)


class Configuration(AuditTimestampModel):
    # GERAL
    title = models.CharField(
        unique=True,
        help_text="Identificação da configuração",
        verbose_name="Identificação",
        max_length=100,
    )
    type_of_usufruct = models.SmallIntegerField(
        default=CONF_VACATION,
        help_text="Tipo",
        verbose_name="Tipo de usufruto",
        choices=Choice.get_choices_for("dayoff", "CONFIGURATION_CHOICE"),
    )
    class_code = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Cálculo",
        related_name="dayoff_configurations",
        on_delete=models.PROTECT,
    )
    authorizer_employee = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        help_text="Chefe que deve entrar como autorizador nas atividades de interrupção, suspensão, indenização, venda.",
        verbose_name="Autorizador para servidores",
        related_name="dayoff_configuration_autorizeremployees",
        blank=True,
        null=True,
    )
    authorizer_member = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        help_text="Chefe que deve entrar como autorizador nas atividades de interrupção, suspensão, indenização, venda.",
        verbose_name="Autorizador para membros",
        related_name="dayoff_configuration_autorizermembers",
        blank=True,
        null=True,
    )
    continuous_period = models.BooleanField(
        default=False,
        help_text="""Modo de avaliação do período aquisitivo. ANUAL: perído por ano.
        CONTINUO: período de acordo com a data de exercício do servidor.""",
        verbose_name="Período contínuo",
        null=True,
    )
    block_on_conflict = models.BooleanField(
        default=False,
        help_text="Se bloquear marcações conflitantes com outros servidores ",
        verbose_name="Bloquer conflitos",
    )
    block_after_pay = models.BooleanField(
        default=False,
        help_text="Se bloqueia alteração depois de pagas",
        verbose_name="Bloquear depois de pago",
    )
    mediate_authorization = models.BooleanField(
        default=False,
        help_text="Se é necessário que a chefia mediata autorize após a chefia imediata",
        verbose_name="Autorizacao chefia mediata",
    )
    auto_authorization = models.SmallIntegerField(
        default=0,
        help_text="Quantidade de dias, posterior à marcação, para que sua autorização seja automática",
        verbose_name="Autorização automática (dias)",
        blank=True,
    )
    run_signal = models.BooleanField(
        default=False,
        help_text="Executa criação/atualização por Provimentos.",
        verbose_name="Executa criação/atualização por Provimentos.",
    )
    """
    auto homologação é o que ocorre no mp hoje, após autorizado do chefe o software envia para homologado
    na escala/marcação inicial é sempre a partir do comando do rh
    """
    auto_homologation = models.SmallIntegerField(
        default=AUTO_HOMOLOGATION,
        help_text="Indicação de auto homologação para que esta ocorra automaticamente",
        verbose_name="Homologação automática",
        choices=Choice.get_choices_for("dayoff", "AUTO_HOMOLOGATION_CHOICE"),
    )
    auto_create_on_scale = models.BooleanField(
        default=False,
        help_text="Cria automaticamente o usufruto para servidores que não marcaram",
        verbose_name="Auto escala (não marcação)",
    )
    # DEPRECATED - UTILIZAR O months_max_usufruct
    months_prescription = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Tempo máximo (em meses) para o gozo dos dias, antes de prescreverem",
        verbose_name="Prescrição (meses)",
    )
    auto_create_prescription = models.BooleanField(
        default=False,
        help_text="Cria automaticamente o usufruto para servidores que possuem parcelas próximas à prescrição",
        verbose_name="Usufruto automático (prescrição)",
    )
    # FRUICAO
    max_division = models.SmallIntegerField(
        default=1,
        blank=True,
        null=True,
        help_text="Quantidade máxima de divisões que um período pode ser usufruído",
        verbose_name="Máximo de divisões",
    )
    min_days_division = models.SmallIntegerField(
        default=1,
        blank=True,
        help_text="Quantidade mínima de dias que pode ser dividida o período de usufruto",
        verbose_name="Quantidade mínimo de dias por divisão",
    )
    chronological_fruition = models.BooleanField(
        default=True,
        help_text="Se o gozo dos dias será realizado de forma cronológica",
        verbose_name="Fruição cronológica",
    )
    months_max_usufruct = models.SmallIntegerField(
        default=12,
        null=True,
        blank=True,
        help_text="Tempo máximo (em meses) para o gozo dos dias. OBS.: XX meses - 1 dia",
        verbose_name="Máximo fruição (meses)",
    )
    max_alteration_usufruct = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Quantidade de vezes que o servidor pode alterar o usufruto",
        verbose_name="Quantidade máxima de alterações",
    )
    # start_fruition_on_year
    start_month_next_period = models.SmallIntegerField(
        help_text="Mês inicial para fruição apartir do segundo período",
        verbose_name="Mês fruição (apartir do 2º período)",
        blank=True,
        null=True,
        choices=Choice.get_choices_for(
            "rh",
            "MONTHS",
            query_dict={"value__in": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
        ),
    )
    days_precede_fruition = models.SmallIntegerField(
        default=15,
        help_text="Dias de antecedência entre a marcação/alteração e a fruição",
        verbose_name="Antecedência fruição (dias)",
        null=True,
        blank=True,
    )
    work_days_precede_fruition = models.BooleanField(
        default=True,
        help_text="Se são contados apenas dias úteis antes do inicio da fruição",
        verbose_name="Dias Úteis",
    )
    # VENDA
    months_exercise_sale = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Quatidade de meses em exercício para poder vender",
        verbose_name="Meses em exercício antes de vender (meses)",
    )
    min_days_sale = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Quantidade mímina de dias que poderão ser vendidos",
        verbose_name="Mínimo de venda (dias)",
    )
    max_days_sale = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Quantidade máxima de dias que poderão ser vendidos",
        verbose_name="Máximo de venda (dias)",
    )
    sell_booked_days = models.BooleanField(
        default=False,
        help_text="Permite vender dias de usufrutos marcados",
        verbose_name="Permite vender marcados?",
    )
    # AQUIÇÃO
    months_exercise_first_acquitition = models.SmallIntegerField(
        default=0,
        blank=True,
        help_text="Tempo de exercício, em meses, para adquirir direito a fruição do primeiro período",
        verbose_name="Tempo de exercício antes de fruir (meses)",
    )
    months_exercise_next_acquitition = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Tempo de exercício, em meses, para adquirir direito a fruição a partir do segundo período",
        verbose_name="Tempo de exercício antes de fruir, próximas parcelas (meses)",
    )
    days_per_period = models.SmallIntegerField(
        default=1,
        null=True,
        blank=True,
        help_text="Quantidade de dias máxima que pode ser usufruído em um período",
        verbose_name="Dias por período",
    )
    periods_per_year = models.SmallIntegerField(
        default=0,
        help_text="Quantidade de períodos em um ano (12 meses).Ex.: Servidor = 1 periodo por ano (12 meses), Membro= 2 períodos por ano",
        verbose_name="Períodos",
        choices=Choice.get_choices_for("dayoff", "PERIODS_YEAR_CHOICE"),
        blank=True,
    )
    # SUSPENSAO
    division_after_suspension = models.SmallIntegerField(
        default=1,
        help_text="Quantidade máxima de divisões após suspensão",
        verbose_name="Máximo de divisões após suspensão (suspenso)",
        blank=True,
    )
    # RELACIONAMENTOS
    """ Choice.get_choices_for('rh', 'CLASSIF_EMPLOYEE_BY_POSSESSION') """
    type_employees = models.ManyToManyField(
        Choice,
        help_text="Para quais tipos de servidor será aplicada essa configuração",
        verbose_name="Tipos de Servidores",
        related_name="dayoff_configuration_typeemployees",
    )
    """ Choice.get_choices_for('rh', 'TIPO_BASE_LICENCA_AFASTAMENTO') """
    suspend_acquisition_departures = models.ManyToManyField(
        Choice,
        help_text="Os afastamentos que suspendem a aquisição dos períodos",
        verbose_name="Afastamentos que suspendem a aquisição dos períodos",
        related_name="dayoff_configuration_suspendacquisitiondepartures",
    )
    """ Choice.get_choices_for('rh', 'TIPO_BASE_LICENCA_AFASTAMENTO') """
    suspend_usufruct_departures = models.ManyToManyField(
        Choice,
        help_text="Os afastamento que suspendem o usufruto",
        verbose_name="Afastamentos que suspendem o usufruto",
        related_name="dayoff_configuration_suspendusufructdepartures",
    )
    """ Choice.get_choices_for('rh', 'TIPO_BASE_LICENCA_AFASTAMENTO') """
    block_usufruct_departures = models.ManyToManyField(
        Choice,
        help_text="Bloqueia criação de usufrutos que conflitam com afastamentos",
        verbose_name="Bloqueia usufrutos que conflitam com afastamentos",
        related_name="dayoff_configuration_blockusufructdepartures",
    )

    excluded_usufructs_amendment = models.ManyToManyField(
        Choice,
        help_text="Tipos de usufrutos que não permitem emenda",
        verbose_name="Usufrutos que não permitem emenda",
        related_name="dayoff_configuration_excludedusufructsamendment",
    )

    # Configurações para Admin
    max_division_admin = models.SmallIntegerField(
        default=1,
        blank=True,
        null=True,
        help_text="Quantidade máxima de divisões que um período pode ser usufruído(Admin)",
        verbose_name="Máximo de divisões(Admin)",
    )
    min_days_division_admin = models.SmallIntegerField(
        default=1,
        blank=True,
        null=True,
        help_text="Quantidade mínima de dias que pode ser dividida o período de usufruto(Admin)",
        verbose_name="Quantidade mínimo de dias por divisão(Admin)",
    )
    sub_type_of_usufruct = models.SmallIntegerField(
        help_text="Tipo",
        verbose_name="Subtipo de usufruto",
        choices=Choice.get_choices_for("dayoff", "SUB_CONFIGURATION_CHOICE"),
        default=0,
    )

    delete_with_zero_days = models.BooleanField(
        default=False,
        help_text="Deleta usufrutos quando o periodo aquisitivo está zerado",
        verbose_name="Deletar usufrutos quando o periodo aquisitivo está zerado?",
    )

    # Prescrição
    prescription_days = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Quantidade em dias para a prescrição",
        verbose_name="Dias para prescrição",
    )
    type_of_duty = models.IntegerField(
        blank=True,
        null=True,
        choices=Choice.get_choices_for("pvf", "TYPE_SHIFT"),
        verbose_name="Tipo Plantão",
    )

    class Meta:
        permissions = (("dayoffadmin", "Pode administrar as Configurações"),)
        ordering = ("title",)

    def __str__(self):
        return "%s - %s" % (
            self.get_type_of_usufruct_display(),
            self.title,
        )

    def natural_key(self):
        return (self.title, self.type_of_usufruct)

    @property
    def type_employees_cache(self):
        if not self._type_employees_cache:
            self._type_employees_cache = [
                t.get("value") for t in self.type_employees.values("value")
            ]
        return self._type_employees_cache

    @property
    def annotation_class(self):
        """Esta propriedade retorna a classe de anotação, como padrão AnotacaoGeral.

        Returns:
            AnotacaoGeral (AnotacaoGeral):
        """
        return CONFIGURATION_TO_ANNOTATION_CLASS.get(
            self.type_of_usufruct, AnotacaoGeral
        )

    @property
    def departure_class(self):
        """Esta propriedade retorna a classe de afastamento.

        Returns:
            departure class (BaseLicencaAfastamento):
        """
        d_class = CONFIGURATION_TO_DEPARTURE_CLASS.get(self.type_of_usufruct, None)
        if not d_class:
            raise Exception(
                f"Não existe classe configurada para {self.type_of_usufruct}. Informe o administrador do sistema!"
            )
        return d_class

    @property
    def balance_days(self):
        """Esta propriedade retorna o saldo total do direito da configuração.

        Returns:
            int:
        """
        return self.get_remainig_by_employee_total()

    def days_remaining_by_employee(self):
        employee = employee_from_user(get_current_user())
        days_remaining = 0
        for acquisition_period in AcquisitionPeriod.objects.filter(
            group_period__configuration=self.pk,
            employee=employee,
            end_date_acquisition__lt=datetime.today().date(),
        ):
            real_days = acquisition_period.real_days
            booked_days = acquisition_period.booked_days
            days_remaining += real_days - booked_days

        return days_remaining

    def get_remainig_by_employee_total(self):
        employee = employee_from_user(get_current_user())
        days_remaining = 0
        query = AcquisitionPeriod.objects.filter(
            group_period__configuration=self.pk, employee=employee
        )
        filter_by_sub_type = query.filter(
            Q(group_period__configuration__sub_type_of_usufruct=REGULAR_VACATIONS)
            | Q(group_period__configuration__sub_type_of_usufruct=PREMIUM_LICENSE)
            | Q(group_period__configuration__sub_type_of_usufruct=INDIVIDUAL_VACATION)
        )
        filter_by_date = query.filter(end_date_acquisition__lt=datetime.today().date())

        for acquisition_period in query:
            if acquisition_period not in filter_by_sub_type:
                days_remaining += acquisition_period.days_not_booked_cache

            elif acquisition_period in filter_by_date:
                real_days = acquisition_period.real_days
                booked_days = acquisition_period.booked_days
                days_remaining += real_days - booked_days

        return days_remaining


class ConfigurationSale(AuditTimestampModel):
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        verbose_name="Configuração",
        related_name="configuration_sale",
    )
    start_date_sale = models.DateField(verbose_name="Data Início da Venda")
    end_date_sale = models.DateField(
        verbose_name="Data Final da Venda", blank=True, null=True
    )
    cutoff_date = models.DateField(verbose_name="Data de Corte", blank=True, null=True)
    attachment = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attachment_config_sale",
    )

    def __str__(self):
        return f"{self.start_date_sale} - {self.end_date_sale }"

    class Meta:
        ordering = ["start_date_sale"]

    def validate_start_date_sale(self):
        if not self.start_date_sale:
            raise Exception("Favor preencher a Data Início da Venda.")

    def validate_cutoff_date(self):
        if not self.cutoff_date:
            raise Exception("Favor preencher a Data de Corte.")

    def validate_date_end_greater_than_date_start(self):
        self.dates_sale()

    def dates_sale(self):
        """A data de fim não pode ser menor que a data de início"""
        if self.end_date_sale and self.end_date_sale < self.start_date_sale:
            raise Exception(
                "A Data Fim de Venda deve ser maior que a Data Início de Venda."
            )

    def validate(self):
        self.validate_start_date_sale()
        self.validate_cutoff_date()
        self.validate_date_end_greater_than_date_start()

    def save(self, *args, **kargs):
        self.validate()
        super().save(*args, **kargs)


class ConfiguracaoPlantaoEleitoral(AuditTimestampModel):

    configuracao = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        verbose_name="Configuração",
        related_name="configuracao_plantao_eleitoral",
    )

    titulo = models.CharField(
        unique=True, help_text="Título", verbose_name="Título", max_length=100
    )

    data = models.DateField(verbose_name="Data", blank=True, null=True)

    turno = models.SmallIntegerField(
        help_text="Turno",
        verbose_name="Turno",
        choices=Choice.get_choices_for("dayoff", "CONFIGURACAO_ELEITORAL_TURNO_CHOICE"),
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Ativo",
        verbose_name="Ativo",
    )

    def validar(self):
        self.validar_data_ativo()

    def validar_data_ativo(self):
        configs = ConfiguracaoPlantaoEleitoral.objects.filter(
            data=self.data, ativo=True
        )
        if self.pk:
            configs = configs.exclude(pk=self.pk)

        if configs.exists():
            raise Exception(
                "Não pode haver mais de uma configuração ativa no mesmo dia"
            )

    def save(self, *args, **kargs):
        self.validar()
        super().save(*args, **kargs)

    def delete(self, *args, **kargs):
        self.ativo = False
        self.save()


class GroupPeriodManager(models.Manager):

    def get_by_natural_key(self, title, configuration, *args):
        return self.get(title=title, configuration=configuration)


class GroupPeriod(AuditTimestampModel):
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.PROTECT,
        verbose_name="Configuração",
        related_name="groupperiods",
    )
    title = models.CharField(
        help_text="Identificação do grupo", verbose_name="Identificação", max_length=100
    )
    period = models.SmallIntegerField(
        default=1,
        help_text="Identificador do Período a que se refere",
        verbose_name="Período",
        blank=True,
    )
    year_collective_fruition = models.SmallIntegerField(
        help_text="Ano para fruição coletiva, caso haja",
        verbose_name="Ano para fruição coletiva",
        null=True,
        blank=True,
    )
    # TODO: remover obrigatoriedade
    start_date_book = models.DateField(
        help_text="Data para início das marcações",
        verbose_name="Início de marcação",
    )
    end_date_book = models.DateField(
        help_text="Data para finalização das marcações",
        verbose_name="Final de marcação",
        blank=True,
        null=True,
    )
    homologation_date = models.DateField(
        help_text="Data prevista para homologação do período aquisitivo",
        verbose_name="Data de Homologação",
        null=True,
        blank=True,
    )
    publication_date = models.DateField(
        help_text="Data prevista para publicação do período aquisitivo",
        verbose_name="Data de Publicação",
        null=True,
        blank=True,
    )
    start_date_fruition = models.DateField(
        help_text="Início da fruição(período para fruição)",
        verbose_name="Início",
    )
    end_date_fruition = models.DateField(
        null=True,
        blank=True,
        help_text="Fim da fruição(período para fruição)",
        verbose_name="Fim",
    )
    start_date_automatic_usufruct = models.DateField(
        null=True,
        blank=True,
        help_text="Início de Usufruto(criar usufrutos automáticos)",
        verbose_name="Início",
    )
    end_date_automatic_usufruct = models.DateField(
        null=True,
        blank=True,
        help_text="Fim de Usufruto(criar usufrutos automáticos)",
        verbose_name="Fim",
    )
    year_reference = models.SmallIntegerField(
        "Ano de Referência", help_text="Ano de referência", blank=True, null=True
    )
    attachment = models.ForeignKey(
        "Attachment",
        on_delete=models.SET_NULL,
        help_text="Referencia do anexo do periodoa aquisitivo",
        verbose_name="Anexo",
        blank=True,
        null=True,
        related_name="dayoff_groupperiods",
    )
    blocked = models.BooleanField(
        default=False,
        help_text="Informa se o Grupo pode ser manipulado por alguém, normalmente é bloqueado quando se cria um período anterior",
        verbose_name="Bloqueado",
    )
    start_date_acquisition = models.DateField(
        verbose_name="Início aquisição(Quando preenchido)", blank=True, null=True
    )
    end_date_acquisition = models.DateField(
        help_text="Fim aquisição(Quando preenchido)",
        verbose_name="Fim aquisição",
        blank=True,
        null=True,
    )
    employee_not_create_usufrutcs = models.ManyToManyField(
        Servidor,
        help_text="Servidores que serão excluídos da geração de Usufrutos",
        verbose_name="Servidores excluídos da geração de usufrutos",
    )
    redo_automatic_book = models.BooleanField(
        default=False, verbose_name="Refazer a marcação automática de usufruto"
    )
    objects = GroupPeriodManager()

    class Meta:
        ordering = ("-year_reference",)
        unique_together = ("title", "period", "year_reference")
        permissions = (("dayoffadmin", "Pode administrar os Grupos"),)
        ordering = ("-year_reference", "-period")

    def __str__(self):
        # return f'{self.title}'
        text = ""
        if self.year_reference:
            text = "%s / " % self.year_reference
        return "%s - %s%s" % (self.title, text, self.period)

    def natural_key(self):
        return (self.title, self.configuration)

    @property
    def icons(self):
        icons = []
        if self.homologation_date:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["homologated"],
                    "title": "Homologado",
                    "alt": "Homologado",
                }
            )
        # else:
        #     icons.append(
        #         {'icon': DAYOFF_ICONS_THEME['blank'], 'title': '', 'alt': '--'})

        if self.blocked:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["blocked"],
                    "title": "Grupo bloqueado",
                    "alt": "Bloqueado",
                }
            )
        # else:
        #     icons.append({'icon': DAYOFF_ICONS_THEME['blank'], 'title': '', 'alt': '--'})
        return icons

    @property
    def classcode(self):
        """Esta propriedade retorna o classcode definido para a configuração.

        Returns:
            ClassCode: ClassCode or None
        """
        class_code = self.configuration.class_code
        # if not class_code:
        #     class_code = ClassCode.objects.get(slug='dayoff-base')
        return class_code

    def classcode_instance(self):
        """Esta propriedade retorna uma instância do classcode definido para o tipo de usufruto ou mostra exceção informando que não possui classcode.

        Returns:
            ClassCode: ClassCode instance

        Raise:
            Exception: raise exception quando não possuir classcode
        """
        if self.classcode and self.classcode.cls:
            return self.classcode.cls(self)
        raise Exception("Class Code not supplied.")

    def _generate_automatic_usufruct(self, acquisition_period):
        if (
            self.start_date_automatic_usufruct
            and self.end_date_automatic_usufruct
            and not acquisition_period.exist_usufruct(
                self.start_date_automatic_usufruct, self.end_date_automatic_usufruct
            )
        ):
            acquisition_period.book(
                usufructs_in=[
                    {
                        "start_date": self.start_date_automatic_usufruct,
                        "end_date": self.end_date_automatic_usufruct,
                    }
                ],
                context="admin",
            )

    def generate_acquisition_periods(self, create_or_update):
        """Este método chama criação de Períodos Aquisitivos.

        Params:
            create_or_update(str): 'create' or 'update'
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        from rh.dayoff.tasks import generate_all_acquisition_periods

        if not self.configuration.class_code:
            raise Exception("Não é possível criar períodos aquisitivos sem ClassCode.")

        # TODO: ADICIONAR VALIDAÇÕES DE HOMOLOGAÇÃO

        task = Task.start(
            generate_all_acquisition_periods,
            group_=self.pk,
            create_or_update=create_or_update,
            user=get_current_user().pk,
            success="""<p>
                Criação de Períodos Aquisitivos de %(type_of_usufruct)s finalizada. Verifique resultado no arquivo
                <a href="/athenas/DAYOFFGroupPeriod/download_file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>
                Este arquivo está disponível para download até dia
                <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
        )
        return task

    @classmethod
    def call_run_generate_periods(self, employee, date_reference):
        """Este método chama criação de Períodos Aquisitivos.

        Params:
            create_or_update(str): 'create' or 'update'
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        from rh.dayoff.tasks import call_run_generate_periods_task

        def unique_task(klass, employee):
            from celery import Celery

            app = Celery("dayoff")
            app.config_from_object(
                os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf")
            )

            active_queues = app.control.inspect().active()
            count = 0
            for queue in active_queues:
                for running_task in active_queues[queue]:
                    if klass == running_task["name"] and employee == running_task[
                        "kwargs"
                    ].get("employee"):
                        log.info(
                            f'\nTask "{call_run_generate_periods_task.__name__}()" cancelled! already running...\n'
                        )
                        count += 1
            return count

        task = None
        if not unique_task("rh.dayoff.tasks.call_run_generate_periods_task", employee):
            task = Task.start(
                call_run_generate_periods_task,
                employee=employee.pk,
                date_reference=DateUtils.date_to_str(date_reference),
                user=(
                    get_current_user().username
                    if is_current_user_admin()
                    else "athenas"
                ),
                success="""<p>Criação/Atualização de Períodos Aquisitivos de %(employee)s finalizada.</p>""",
            )
            return task

    def run_generate_all_acquisition_periods(self, task_uuid, create_or_update):
        task = None
        if task_uuid:
            task = Task.objects.filter(uuid=task_uuid).first()

        # class_code_period = self.configuration.class_code.cls(self)
        class_code_period = self.classcode_instance()

        # periods = self.configuration.class_code.cls(
        #     self,
        # ).generate_all_acquisition_periods()

        def _call_automatic_book(mode, acqp):
            if mode == ACQP_CREATION_CREATED or (
                mode == ACQP_CREATION_UPDATED and acqp.group_period.redo_automatic_book
            ):
                try:
                    if not acqp.group_period.employee_not_create_usufrutcs.filter(
                        pk=acqp.employee.pk
                    ).exists():
                        acqp.group_period._generate_automatic_usufruct(acqp)
                except Exception as err:
                    log.exception(err)
                    if task:
                        task.info(
                            msg=f"Usufruto não criado para {acqp.employee}: {err}",
                            type_of=3,
                        )

        query = class_code_period.get_acquisition_period_query()

        # err_acquisition_period = []
        # err_usufruct = []
        factor = query.count() or 1
        inc_progress = 100.0 / factor
        for acqp, mode, err in class_code_period.generate_all_acquisition_periods(task):
            if err:
                type_error = "atualizar"
                if mode == ACQP_CREATION_ERROR:
                    type_error = "criar"
                if task:
                    task.info(
                        msg=f"Erro ao {type_error} período {acqp}: {err}", type_of=3
                    )
                print(f"Erro ao {type_error} período {acqp}: {err}")
                log.exception(err)
                print(err)
            elif mode == ACQP_CREATION_UPDATED:
                if acqp.diff:
                    if task:
                        task.info(
                            msg=f"Período aquisitivo ({acqp}) atualizado: {acqp.diff}",
                            type_of=2,
                        )
                    print(f"Período aquisitivo ({acqp}) atualizado: {acqp.diff}")
            elif mode == ACQP_CREATION_CREATED:
                if task:
                    task.info(msg=f"Período aquisitivo ({acqp}) criado!", type_of=1)
                print(f"Período aquisitivo ({acqp}) criado!")
            else:
                if task:
                    task.info(msg=f"{mode}: {acqp}", type_of=2)
                print(f"{mode}: {acqp}")

            _call_automatic_book(mode, acqp)

            if task:
                task.increment_progress(inc_progress)

        # task.mark_finished()
        #     try:
        #         if create_or_update == 'create':
        #             acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
        #                 employee=period['employee'],
        #                 group_period=period['group_period'],
        #                 defaults=period,
        #                 automatic_created=True
        #             )

        #         elif create_or_update == 'update':
        #             acquisition_period, created = AcquisitionPeriod.objects.update_or_create(
        #                 employee=period['employee'],
        #                 group_period=period['group_period'],
        #                 defaults=period,
        #                 automatic_created=True
        #             )
        #     except Exception as err:
        #         err_acquisition_period.append('Período aquisitivo de %s não foi criado: %s' % (period['employee'], err))

        #     else:
        #         if created:
        #             try:
        #                 self._generate_automatic_usufruct(acquisition_period)
        #             except Exception as err:
        #                 err_usufruct.append(
        #                     'Usufruto não criado para %s: %s' % (period['employee'], err))
        #                 task.info(
        #                     msg=f"Usufruto não criado para {period['employee']}: {err}", type_of=3)
        #                 log.exception(err)
        #     finally:
        #         if task:
        #             Task.objects.filter(pk=task.pk).update(progress=models.F('progress') + inc_progress)

        # file_result = self._write_result(task, err_acquisition_period, err_usufruct)

        # gedfile = File.from_filepath(file_result, get_current_user(), 'text/plain', 1)

        # task.add_file(gedfile)

    def _write_result(self, task, err_acquisition_period, err_usufruct):
        data = json.loads(task.data)
        filename = data.get("filename")

        cache_path = os.path.join(settings.CACHE_PATH, task.uuid)
        file_path = os.path.join(cache_path, filename)
        if not os.path.exists(cache_path):
            os.makedirs(cache_path, 0o755)
        with open(file_path, "a") as fd:
            fd.write(
                "Períodos Aquisitivos não criados para %d.\n"
                % len(err_acquisition_period)
            )
            for err in err_acquisition_period:
                fd.write(err + "\n")
            fd.write("Usufrutos não criados para %d.\n" % len(err_usufruct))
            for err in err_usufruct:
                fd.write(err + "\n")

        return file_path


class AcquisitionPeriod(AuditTimestampModel):
    group_period = models.ForeignKey(
        GroupPeriod,
        on_delete=models.CASCADE,
        help_text="Agrupador do período aquisitivo",
        verbose_name="Grupo",
        related_name="acquisitionperiods",
    )
    employee = models.ForeignKey(
        Servidor,
        help_text="O servidor que pode marcar para o período aquisitivo solicitado",
        verbose_name="Servidor",
        related_name="dayoff_acquisitionperiods",
        on_delete=models.PROTECT,
    )
    status = models.SmallIntegerField(
        default=ACQP_WAIT,
        help_text="Situação atual desse período aquisitivo",
        verbose_name="Status",
        choices=Choice.get_choices_for("dayoff", "ACQUISITION_PERIOD_STATUS_CHOICE"),
    )
    information = models.CharField(
        max_length=32,
        help_text="Informação do período faz parte da chave",
        verbose_name="Informação",
        blank=True,
        null=True,
    )
    start_date_acquisition = models.DateField(
        verbose_name="Início aquisição", blank=True, null=True
    )
    end_date_acquisition = models.DateField(
        help_text="Data de referência para o cálculo do período aquisitivo",
        verbose_name="Fim aquisição",
        blank=True,
        null=True,
    )
    start_date_fruition = models.DateField(
        help_text="Data mínima para que se possa usufruir esse período",
        verbose_name="Início usufruto",
        blank=True,
    )
    end_date_fruition = models.DateField(
        help_text="Data máxima para que se possa usufruir esse período",
        verbose_name="Fim usufruto",
        blank=True,
        null=True,
    )
    previous_period = models.ForeignKey(
        "AcquisitionPeriod",
        on_delete=models.SET_NULL,
        help_text="Período aquisitivo anterior",
        verbose_name="Período aquisitivo anterior",
        related_name="nextperiods",
        blank=True,
        null=True,
    )
    continuous_period = models.BooleanField(
        default=True,
        help_text="Modo de avaliação do período aquisitivo. ANUAL: perído por ano."
        + "CONTINUO: período de acordo com a data de exercício do servidor.",
        verbose_name="Período contínuo",
    )
    blocked = models.BooleanField(
        default=False,
        help_text="Informa se o PAS pode ser manipulado por alguém, normalmente é bloqueado quando se cria um período anterior",
        verbose_name="Bloqueado",
    )
    automatic_created = models.BooleanField(
        default=False, verbose_name="Criado automaticamente"
    )
    days = models.SmallIntegerField(
        default=1,
        help_text="Quantidade de dias a que o servidor tem direito para o período em questão",
        verbose_name="Quantidade de dias",
    )
    real_days_cache = models.SmallIntegerField(
        default=30,
        help_text="Quantidade de dias reais(desconsiderando pagos e vendidos)",
        verbose_name="Quantidade de dias reais(desconsiderando pagos e vendidos)",
    )
    booked_days_cache = models.SmallIntegerField(
        default=0, verbose_name="Cache de dias agendados"
    )
    days_to_enjoy_cache = models.SmallIntegerField(
        default=0, verbose_name="Cache de dias restantes para fruir"
    )
    paid_days_cache = models.PositiveIntegerField(
        default=0, verbose_name="Cache de dias vendidos"
    )
    days_not_booked_cache = models.PositiveIntegerField(
        default=0, verbose_name="Cache de dias não agendados"
    )
    paid_without_payroll = models.BooleanField(
        default=False,
        help_text="Informa se o PAS foi pago antes da entrada em vigencia do sistema e a folha não pode ser indicada com precisão",
        verbose_name="Pago sem folha",
    )
    indemnified = models.BooleanField(
        default=False,
        help_text="Indenizado nesse período aquisitivo",
        verbose_name="Indenizados",
        blank=True,
    )
    suspended_days = models.PositiveIntegerField(
        default=0,
        help_text="Quantidade de dias que o período está suspenso",
        verbose_name="Dias Suspensos",
        blank=True,
        null=True,
    )
    paycheck_event = models.ForeignKey(
        FolhaEvento,
        on_delete=models.SET_NULL,
        help_text="Referência à folha e evento que gerou o pagamento do terço constitucional para o período aquisitivo",
        verbose_name="Folha Evento",
        blank=True,
        null=True,
        related_name="acquisitionperiods",
    )
    attachment = models.ForeignKey(
        "Attachment",
        on_delete=models.SET_NULL,
        help_text="Referencia do anexo do periodoa aquisitivo",
        verbose_name="Anexo",
        blank=True,
        null=True,
        related_name="dayoff_acquisitionperiods",
    )
    annotation = models.ForeignKey(
        AnotacaoGeral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dayoff_acquisitionperiods",
    )
    note = models.BooleanField(default=True, blank=True, verbose_name="Gerar anotação")
    description = models.TextField(
        help_text="Descrição do período aquisitivo",
        verbose_name="Descrição",
        blank=True,
        null=True,
    )
    notifications = generic.GenericRelation(
        Notification, content_type_field="sender_ct", object_id_field="sender_id"
    )
    pendency = models.BooleanField(default=False, blank=True, verbose_name="Pendência")
    info = models.TextField(verbose_name="Informação", blank=True, default="")

    _conflict = None

    class Meta:
        verbose_name = "Período Aquisitivo"
        permissions = (
            ("dayoffadmin", "Pode administrar os Períodos Aquisitivos"),
            ("can_block_ap", "Pode bloquear os Períodos Aquisitivos"),
            ("can_unblock_ap", "Pode desbloquear os Períodos Aquisitivos"),
            ("can_super_delete", "Pode desbloquear os Períodos Aquisitivos"),
            (
                "dayoff_notify_admin",
                "Recebe notificações sobre alteração de Períodos Aquisitivos",
            ),
        )
        unique_together = ("group_period", "employee")
        ordering = (
            "-group_period__year_reference",
            "employee",
        )

    def __str__(self):
        if self.start_date_acquisition and self.end_date_acquisition:
            return "%s - %s (%s/%s) - %s" % (
                self.employee,
                self.group_period,
                self.start_date_acquisition.year,
                self.end_date_acquisition.year,
                self.get_status_display(),
            )

        return f"{self.employee} - {self.group_period} - {self.get_status_display()}"

    def str_summary(self):
        if self.start_date_acquisition and self.end_date_acquisition:
            return "%s (%s/%s)" % (
                self.configuration.title,
                self.start_date_acquisition.year,
                self.end_date_acquisition.year,
            )

        return f"{self.group_period.title}"

    def validate_unique(self, exclude=None):
        """Check unique constraints on the model and raise  if any failed."""
        try:
            super(AcquisitionPeriod, self).validate_unique(exclude=exclude)
        except Exception as err:
            log.exception(err)
            if "__all__" in err.message_dict:
                raise Exception(err.message_dict.get("__all__"))
            raise err

    def save(self, *args, **kwargs):
        if self.group_period.start_date_fruition and not self.start_date_fruition:
            self.start_date_fruition = self.group_period.start_date_fruition
        if self.group_period.end_date_fruition and not self.end_date_fruition:
            self.end_date_fruition = self.group_period.end_date_fruition

        self._update_days()
        self.booked_days_cache = self.booked_days
        self.real_days_cache = self.real_days
        self.days_to_enjoy_cache = self.days_to_enjoy
        self.days_not_booked_cache = self.days_not_booked
        self.paid_days_cache = self.paid_days

        self.validate(validate_prevent=kwargs.get("validate_prevent", False))
        self.annotate(note_prevent=kwargs.get("note_prevent", False))

        if "validate_prevent" in kwargs:
            kwargs.pop("validate_prevent")
        if "note_prevent" in kwargs:
            kwargs.pop("note_prevent")

        target, action = self._define_status()
        if self.status in (ACQP_FINISHED, ACQP_PROGRESS) and target in (
            ACQP_FINISHED,
            ACQP_PROGRESS,
        ):
            self.status = target

        super(AcquisitionPeriod, self).save(*args, **kwargs)

    def validate_can_delete(self):
        if not (has_perm_super_delete() or is_current_user_system()):
            raise Exception("Não possui permissão para apagar o período aquisitivo.")
        if self.usufructs.exclude(status=USU_CANCELED).exists():
            raise Exception("Só é permitido apagar quando não possui usufrutos.")
        return True

    def delete_cancelleds(self):
        if (
            not self.usufructs.exclude(status=USU_CANCELED).exists()
            and not self.activities.exclude(canceled=True).exists()
        ):
            self.activities.filter(canceled=True).delete()
            self.usufructs.filter(status=USU_CANCELED).delete()
        else:
            raise Exception(
                "Só é permitido apagar quando não possui usufrutos/atividades."
            )

    def delete(self, *args, **kargs):
        self.validate_can_delete()
        self.delete_cancelleds()
        try:
            if self.annotation:
                self.annotation.delete()
        except Exception as err:
            log.exception(err)
        super(AcquisitionPeriod, self).delete(*args, **kargs)

    def _update_days(self, to_save=False):
        if self.pk:
            number_of_days = 0
            for attachment in AcquisitionPeriodAttachment.objects.filter(
                acquisition_period=self
            ).all():
                number_of_days += attachment.days_law

            self.days = number_of_days
            self.update_status()

            if to_save:
                self.save()

    @property
    def tipo_plantao_compensatorias(self):
        if self.group_period.configuration.type_of_usufruct == CONF_DUTTY:
            return True
        return False

    @property
    def get_data_corte_venda(self):
        if self.tipo_plantao_compensatorias:
            data_atual = datetime.today().date()
            configs_sale = self.group_period.configuration.configuration_sale.filter(
                Q(start_date_sale__lte=data_atual, end_date_sale__isnull=True)
                | Q(start_date_sale__lte=data_atual, end_date_sale__gte=data_atual)
            )
            config = configs_sale.first()
            return config.cutoff_date if config else None
        return None

    @property
    def get_total_venda_anexo(self):
        saldo_venda = 0
        if self.tipo_plantao_compensatorias and self.get_data_corte_venda:
            dt_corte_venda = self.get_data_corte_venda
            for attachment in self.attachment_acquisitionperiod.all():
                if (
                    attachment.date_start <= dt_corte_venda
                    and attachment.date_end > dt_corte_venda
                ):
                    saldo_venda = (
                        saldo_venda
                        + NewDateRange(attachment.date_start, dt_corte_venda).days
                    )
                elif attachment.date_end <= dt_corte_venda:
                    saldo_venda = saldo_venda + attachment.days_law
        return saldo_venda

    @property
    def get_saldo_venda(self):
        saldo_final = 0
        if self.tipo_plantao_compensatorias:
            saldo_agendado_vendido = self.booked_days_cache + self.paid_days_cache
            total_venda_anexo = self.get_total_venda_anexo
            if total_venda_anexo > 0:
                saldo_final = total_venda_anexo - saldo_agendado_vendido

        return 0 if saldo_final < 0 else saldo_final

    @property
    def configuration(self):
        """Esta propriedade retorna a Configuration do GroupPeriod

        Returns:
            Configuration:
        """
        return self.group_period.configuration

    # @property
    # def deadline_acquisition(self):
    #     # antigo .data_limite_aquisicao
    #     """Retorna a data limite para que o servidor/membro possa usufruir do período aquisitivo.
    #     Caso o PA possua "month_collective_fruition", que indica PA coletivo, retorna o dia anterior ao mês de fruição,
    #     caso nao possua "month_collective_fruition" retorna a menor data para aquisicao do período

    #     Returns:
    #         datetime.date: retorna uma data de limite ou None
    #     """
    #     deadline = None
    #     if self.configuration.month_collective_fruition and self.group_period.year_collective_fruition:
    #         last_day = calendar.monthrange(self.group_period.year_collective_fruition, self.configuration.month_collective_fruition)[1]
    #         return datetime.date(day=last_day, month=self.configuration.month_collective_fruition, year=self.group_period.year_collective_fruition)
    #         month = int((12 / self.configuracao.quantidade_periodos) * self.periodo)
    #         day = 30 if month == 6 else 31
    #         year = self.group_period.year_collective_fruition
    #         deadline = datetime.date(day=day, month=month, year=year)
    #     return deadline

    @property
    def classcode(self):
        """Esta propriedade retorna o classcode definido para a configuração.

        Returns:
            ClassCode: ClassCode or None
        """
        class_code = self.configuration.class_code
        # if not class_code:
        #     class_code = ClassCode.objects.get(slug='dayoff-base')
        return class_code

    # @ilru_cache()
    def classcode_instance(self):
        """Esta propriedade retorna uma instância do classcode definido para o
        tipo de usufruto ou mostra exceção informando que não possui classcode.

        Returns:
            ClassCode.: ClassCode instance

        Raise:
            Exception: raise exception quando não possuir classcode
        """
        if self.classcode and self.classcode.cls:
            return self.classcode.cls(group_period=self.group_period, acq_period=self)
        raise Exception("Class Code not supplied.")

    @property
    def _payments_to_str(self):
        log.info("********************************************")
        text = ""
        for p in self.payments.all():
            text += f"{p.get_type_of_display()}: {p.entry_payment}<br />"
        return text  # f'Período aquisitivo pago ({self.paycheck_event})'

    @property
    def icons(self):
        icons = []
        if self.finished:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_enjoyed"],
                    "title": "Período aquisitivo concluído",
                    "alt": "Fruido",
                }
            )
        elif self.enjoying:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_enjoying"],
                    "title": "Parcela em fruição",
                    "alt": "Fruindo",
                }
            )
        elif self.status == ACQP_PROGRESS:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["ap_progress"],
                    "title": "Em andamento",
                    "alt": "Andamento",
                }
            )
        elif self.status == ACQP_INDEMNIFIED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["ap_indemnified"],
                    "title": "Período Indenizado",
                    "alt": "Indenizado",
                }
            )
        elif self.status == ACQP_WAIT:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["waiting"],
                    "title": "Aguardando liberação",
                    "alt": "Liberacao",
                }
            )
        elif self.status == ACQP_PRESCRIBED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["prescribed"],
                    "title": "Prescrito",
                    "alt": "Prescrito",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.payments.exists():
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["paid"],
                    "title": self._payments_to_str,
                    "alt": "Pagamentos",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.blocked:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["blocked"],
                    "title": "Período bloqueado",
                    "alt": "Bloqueado",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.pendency:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["pendency"],
                    "title": f"{self.info[0:255]}",
                    "alt": "Pendente",
                }
            )
        # else:
        #     icons.append({'icon': DAYOFF_ICONS_THEME['blank'], 'title': '', 'alt': '--'})
        return icons

    @property
    def disabled(self):
        # antigo .desabilitado
        """Esta propriedade retorna True se esse Período Aquisitivo não pode ser manipulado pelo usuário - para marcação.

        Returns:
            bool:
        """
        return self.blocked or self.status not in [ACQP_PROGRESS]

    @property
    def usufructs(self):
        # antigo .interrompido
        """Esta propriedade retorna os usufrutos do período aquisitivo.

        Returns:
            bool:
        """
        return Usufruct.objects.filter(activity__acquisition_period=self)

    @property
    def has_interruptions(self):
        # antigo .interrompido
        """Esta propriedade retorna se alguma parcela para esse periodo foi interrompida.

        Returns:
            bool:
        """
        return self.activities.usufructs.filter(status=USU_INTERRUPTED).exists()

    @property
    def has_suspensions(self):
        # antigo .suspenso
        """Esta propriedade retorna se alguma parcela para esse periodo foi suspensa.

        Returns:
            bool:
        """
        return self.activities.usufructs.filter(status=USU_SUSPENDED).exists()

    @property
    def finished(self):
        # antigo .fruido
        """Esta propriedade retorna True se o período aquisitivo está concluído.

        Returns:
            bool:
        """
        return self.status == ACQP_FINISHED

    @property
    def enjoying(self):
        # antigo .enjoying
        """Esta propriedade retorna período aquisitivo está fruindo.

        Returns:
            bool:
        """
        return self.usufructs.filter(status=USU_ENJOYING).exists()

    @property
    def homologated(self):
        # antigo .homologado
        """Esta propriedade retorna se o período aquisitivo está homologado.

        Returns:
            bool:
        """
        return self.group_period.publication_date or self.previous_period

    @property
    def provisioned_days(self):
        # antigo .dias_aprovisionados
        """Esta propriedade retorna quantos dias estão aprovisionados.

        Returns:
            int:
        """
        if self.pk:
            dm = self.activities.filter(
                usufructs__status__in=[
                    USU_NEW,
                    USU_AUTORIZED_CI,
                    USU_HOMOLOGATED,
                    USU_SUBSTITUTE,
                    USU_ENJOYING,
                    USU_ENJOYED,
                ]
            ).aggregate(booked_days=models.Sum("usufructs__days"))
            return (dm["booked_days"] or 0) - self.paid_days
        return (0) - self.paid_days

    @property
    def days_not_booked(self):
        # antigo .dias_nao_marcados
        """Esta propriedade retorna quantos dias não estão agendados.

        Returns:
            int:
        """
        days = self.days - self.booked_days - self.paid_days
        return days if days >= 0 else 0

    @property
    def authorized_days(self):
        # antigo .dias_autorizados
        """Esta propriedade retorna quantos dias estão autorizados.

        Returns:
            int:
        """
        if self.pk:
            dm = self.activities.usufructs.exclude(
                status__in=[
                    USU_NEW,
                    USU_CHANGED,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CANCELED,
                    USU_SOLD,
                ]
            ).aggregate(booked_days=models.Sum("days"))
            return dm["booked_days"] or 0
        return 0

    @property
    def not_enjoyed_days(self):
        """Esta propriedade retorna quantos dias não foram fruídos.

        Returns:
            int:
        """
        return self.days - self.days_enjoyed - self.paid_days

    @deprecated
    @property
    def booked_days_minus_enjoyed(self):
        # antigo .dias_agendados
        """Esta propriedade retorna quantos dias estão agendados descontando os dias fruídos.

        Returns:
            int:
        """
        return self.booked_days - self.days_enjoyed

    @classmethod
    def status_usufruct_booked_days(cls):
        return [
            USU_NEW,
            USU_AUTORIZED_CI,
            USU_HOMOLOGATED,
            USU_CHANGING,
            USU_ENJOYING,
            USU_ENJOYED,
        ]

    @property
    def booked_days(self):
        # antigo .dias_marcados
        """Esta propriedade retorna quantos dias estão agendados.

        Returns:
            int:
        """
        if self.pk:
            dm = self.activities.filter(
                usufructs__status__in=self.status_usufruct_booked_days()
            ).aggregate(booked_days=models.Sum("usufructs__days"))
            return dm["booked_days"] or 0
        return 0

    @property
    def days_enjoyed(self):
        # antigo .dias_usufruidos
        """Esta propriedade retorna quantos dias estão fruídos.

        Returns:
            int:
        """
        if self.pk:
            dm = self.activities.filter(usufructs__status=USU_ENJOYED).aggregate(
                booked_days=models.Sum("usufructs__days")
            )
            return dm["booked_days"] or 0
        return 0

    @property
    def days_to_enjoy(self):
        # antigo .dias_ausufruir
        """Esta propriedade retorna quantos dias existem para usufruir.

        Returns:
            int:
        """
        return self.real_days - self.days_enjoyed

    @property
    def real_days(self):
        """Esta propriedade retorna quantos dias existem descontando-se os dias pagos.

        Returns:
            int:
        """
        return self.days - self.paid_days

    @property
    def paid_days(self):
        """Esta Propriedade retorna quantos dias foram vendidos

        Return:
            int:
        """
        return (
            self.usufructs.filter(
                activity__type_of_activity__in=[ACT_SELL, ACT_BOOK_SELL, ACT_RECTIFY],
                status__in=[USU_HOMOLOGATED, USU_SOLD],
                start_date__isnull=True,
            ).aggregate(days=Sum("days"))["days"]
            or 0
        )

    @property
    def payroll(self):
        # antigo .folha
        """Esta propriedade retorna informação da Folha em que o período foi pago.

        Returns:
            str:
        """
        text = None
        if self.paid:
            text = "PAGO (sem informação da folha)"
            if self.paycheck_event:
                text = "%s (%s)" % (
                    self.paycheck_event.folha,
                    self.paycheck_event.evento,
                )
        return text

    @property
    def paid(self):
        # antigo .pago
        """Propriedade que verifica se o período aquisitivo foi pago.Retornando True/False.

        Returns:
            bool:
        """
        return self.paid_without_payroll or self.paycheck_event is not None

    def divisions_usufruct_sum(self, usufructs_exclude=[]):
        """Este método retornará quantas divisões de usufrutos existem.

        Returns:
            int:
        """
        return (
            self.usufructs.exclude(
                status__in=[
                    USU_CHANGED,
                    USU_CANCELED,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_NOT_AUTHORIZED,
                ]
            )
            .exclude(pk__in=usufructs_exclude)
            .count()
        )

    @property
    def alteration_usufruct_sum(self):
        """Esta propriedade retornará o somatório da quantidade de alterações dos usufrutos.

        Returns:
            int:
        """
        return (
            ActivityChange.objects.filter(acquisition_period=self)
            .exclude(status=ACT_ST_CANCELED)
            .count()
        )

    @property
    def employee_exercise_months(self):
        """Esta propriedade contará quantos meses o servidor está em exercício.

        Returns:
            int:
        """
        return 12

    @property
    def division_after_suspension_sum(self):
        """Esta propriedade retornará a quantidade de divisões após suspensão.

        Returns:
            int:
        """
        # TODO: IMPLEMENTAR issue 391 396
        return 0

    @property
    def departures_employee(self):
        """Esta propriedade retornará os afastamentos do servidor.

        Returns:
            queryset:
        """
        return self.employee.departures()

    @property
    def balance_available(self):
        """Esta propriedade retorna o saldo disponível.

        Returns:
            int:
        """
        return self.days_not_booked_cache

    @property
    def status_name(self):
        """Esta propriedade retorna o label do status.

        Returns:
            int:
        """
        return self.get_status_display()

    @property
    def group_period_name(self):
        """Esta propriedade retorna o nome do grupo.

        Returns:
            int:
        """
        return self.group_period.title

    @property
    def get_texto_group_period(self):
        return f"{self.group_period}"

    @property
    def sale_usufruct(self):
        """Esta propriedade retorna se a configuração permite venda.

        Returns:
            bool:
        """
        if self.group_period.configuration.max_days_sale > 0:
            return True
        return False

    @property
    def check_suspend_acquisition_departures(self):
        """Esta propriedade checa se existem afastamentos que suspendem o período aquisitivo.

        Returns:
            queryset:
        """

        return (
            self.departures_employee.filter(
                tipo__in=self.configuration.suspend_acquisition_departures.values(
                    "value"
                ),
                data_inicio__gte=self.start_date_acquisition,
                data_inicio__lte=self.end_date_acquisition,
            )
            if self.start_date_acquisition and self.end_date_acquisition
            else False
        )

    def exist_usufruct(self, start_date, end_date):
        """Esta propriedade checa se existe usufruto para start_date e end_date.

        Args:
            start_date(date):
            end_date(date):

        Returns:
            queryset:
        """

        return (
            self.usufructs.filter(start_date=start_date, end_date=end_date)
            .exclude(status=USU_CANCELED)
            .exists()
        )

    def exist_active_attachment(self):
        """Esta propriedade checa se existe anexo ativo para o usufruto.

        Returns:
            boolean:
        """

        if self.attachment_acquisitionperiod.all().count() > 0:
            for attachment in self.attachment_acquisitionperiod.all():
                if attachment.status == 1:
                    return True
        return False

    @property
    def check_block_usufruct_departures(self):
        """Esta propriedade checa se existem afastamentos que bloqueiam o usufruto.

        Returns:
            queryset:
        """
        return self.configuration.block_usufruct_departures.exists()

    def check_auto_homologation(self):
        """Este método checa se a auto homologação está habilitada.

        Returns:
            bool:
        """
        check = self.configuration.auto_homologation == AUTO_HOMOLOGATION or (
            self.configuration.auto_homologation == AUTO_HOMOLOGATION_AFTER_SCALE
            and self.group_period.homologation_date
            and self.group_period.homologation_date <= datetime.now().date()
        )
        return check

    def check_auto_authorization(self):
        """Este método checa se a auto autorização está habilitada.

        Returns:
            bool:
        """
        return self.configuration.auto_authorization > 0

    @property
    def check_enjoyed(self):
        """Esta propriedade checa se a quantidade de dias reais é igual a quantidade de dias fruídos.
            Caso sejam iguais, retorna True, de outra forma False.

        Returns:
            bool:
        """
        real_days = self.real_days
        days_enjoyed = self.days_enjoyed
        booked_days = self.booked_days
        return (
            real_days == days_enjoyed and days_enjoyed == booked_days
        ) or real_days < days_enjoyed

    @property
    def check_prescribed(self):
        """Esta propriedade checa se a quantidade de dias reais é igual a quantidade de dias fruídos.
            Caso sejam iguais, retorna True, de outra forma False.

        Returns:
            bool:
        """
        if self.classcode:
            return self.classcode_instance().check_prescribed()
        return False

    def annotate(self, note_prevent=False):
        """Este método gera a anotação.

        Returns:
            annotate (AnotacaoGeral):
        """
        if self.note and not note_prevent:
            self.annotation = self._annotate_default()

    def update_annotation(self):
        annotation_old = self.annotation
        self.annotate()
        if self.annotation != annotation_old:
            AcquisitionPeriod.objects.filter(pk=self.pk).update(
                annotation=self.annotation
            )

    def _annotate_default(self):
        """Este método gera a anotação.

        Returns:
            annotate (AnotacaoGeral):
        """
        # raise Exception("TESTANDO")
        first_attachment = None
        if self.pk:
            first_attachment = (
                self.attachment_acquisitionperiod.all().order_by("id").first()
            )
        if self.days > 0:
            if not self.annotation:
                if first_attachment:
                    annotation = self.configuration.annotation_class.manage_instance(
                        servidor=self.employee,
                        tipo_documento=(
                            Publication.get_tipo(
                                first_attachment.attachment.publication
                            )
                            if first_attachment.attachment
                            else 100
                        ),
                        publicacao=(
                            first_attachment.attachment.publication
                            if first_attachment.attachment
                            else None
                        ),
                        data_portaria_inicio=self.start_date_acquisition,
                        texto=self.annotation_text(),
                        resumo=self.annotation_summary(),
                    )
                else:
                    annotation = self.configuration.annotation_class.manage_instance(
                        servidor=self.employee,
                        tipo_documento=100,
                        publicacao=None,
                        data_portaria_inicio=self.start_date_acquisition,
                        texto=self.annotation_text(),
                        resumo=self.annotation_summary(),
                    )
                self.configuration.annotation_class.objects.filter(
                    pk=annotation.pk
                ).update(indireto=True)
                self.annotation = annotation
            else:
                _annotation_class = self.configuration.annotation_class
                if _annotation_class != self.annotation.my_origin.__class__:
                    _annotation_class = self.annotation.my_origin.__class__
                annotation = _annotation_class.objects.get(pk=self.annotation.pk)
                if first_attachment:
                    annotation.publicacao = (
                        first_attachment.attachment.publication
                        if first_attachment.attachment
                        else None
                    )
                    annotation.tipo_documento = (
                        Publication.get_tipo(first_attachment.attachment.publication)
                        if first_attachment.attachment
                        else 100
                    )
                else:
                    annotation.publicacao = None
                    annotation.tipo_documento = 100
                annotation.data_portaria_inicio = self.start_date_acquisition
                annotation.texto = self.annotation_text()
                annotation.resumo = self.annotation_summary()
                annotation.servidor = self.employee
                annotation.indireto = False
                annotation.save()
                self.annotation = annotation
            return self.annotation
        else:
            if self.annotation:
                q = self.configuration.annotation_class.objects.filter(
                    pk=self.annotation.pk
                )
                if q.exists():
                    q.last().delete()
            return None

    def annotation_text(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            texto (str):
        """
        employee_text = "%s %s" % (
            "O membro" if self.employee.membro else "O(A) servidor(a)",
            self.employee.pessoa_fisica,
        )
        acquisition_text = (
            "adquiriu (%s) dia(s), através de %s, para fruição em época oportuna de acordo com as regras de %s."
            % (
                self.days,
                self.group_period,
                self.configuration.get_type_of_usufruct_display(),
            )
        )

        acquisition_period_attachments = (
            self.attachment_acquisitionperiod.all().order_by("date_start")
        )
        doc_text = ""
        if acquisition_period_attachments:
            for acquisition_period_attachment in acquisition_period_attachments:
                doc_text += f"<p>{acquisition_period_attachment.attachment}</p>"

        text = "<p>%s %s</p><p>Documento(s): %s</p>" % (
            employee_text,
            acquisition_text,
            doc_text if doc_text else "----",
        )

        usufructs = ""
        query_usufructs = self.usufructs.exclude(status=USU_CANCELED)
        for usu in query_usufructs.order_by("activity__created_at"):
            buff_document = ""
            if usu.activity.attachment:
                buff_document += f"<p>{usu.activity.attachment}</p>"
            activity = usu.activity_modifieds.last()
            if activity and activity.attachment:
                buff_document += f"<p>{activity.attachment}</p>"
            buff = ""
            if usu.start_date and usu.end_date:
                buff = f" {DateUtils.date_to_str(usu.start_date)} a {DateUtils.date_to_str(usu.end_date)}"
            usufructs += (
                f"<p><b>-{buff} ({usu.days} dias) - {usu.get_status_display()}.</b></p>"
            )
            if buff_document:
                usufructs += f"<p>Documentos:</p>{buff_document}"
        text = "%s<p>Usufrutos:</p>%s" % (text, usufructs)
        return text

    def annotation_summary(self):
        """Esta propriedade retorna o resumo da anotação.

        Returns:
            resumo (str)
        """
        return f"Período aquisitivo {self.group_period}"

    def validate(self, validate_prevent=False):
        if not validate_prevent:
            self.validate_date_acquisition()
            self.validate_type_of_usufruct()
            self.validate_block_on_conflict()
            self.validate_block_after_pay()
            # self.validate_months_max_usufruct()
            self.validate_max_alteration_usufruct()
            # self.validate_months_exercise_sale()

            self.validate_days_per_period()
            # self.validate_periods_per_year()
            self.validate_division_after_suspension()
            self.validate_suspend_acquisition_departures()

    def validate_date_acquisition(self):
        """Este método valida se as datas de Início e Fim aquisição foram preenchidas.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.start_date_acquisition or not self.end_date_acquisition:
            raise Exception("Favor preencher as datas de Início e Fim aquisição.")
        return True

    def validate_type_of_usufruct(self):
        """Este método valida se existe anexo associado ao período aquisitivo com os tipos de usufruto folga_eleitoral e folga_plantao.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.pk:
            type_of_usufruct_id = self.group_period.configuration.type_of_usufruct
            type_of_usufruct = CONFIGURATION_CHOICE[type_of_usufruct_id]

            folga_eleitoral = CONFIGURATION_CHOICE[CONF_ELECTORAL_SLACK]
            folga_plantao = CONFIGURATION_CHOICE[CONF_DUTTY]

            acquisition_period = AcquisitionPeriod.objects.get(pk=self.pk)

            if (
                acquisition_period.start_date_acquisition
                and acquisition_period.end_date_acquisition
            ):
                if (
                    type_of_usufruct == folga_eleitoral
                    or type_of_usufruct == folga_plantao
                ):
                    if not self.attachment_acquisitionperiod.all():
                        raise Exception(
                            "Favor cadastrar um anexo para este Período Aquisitivo."
                        )

        return True

    def validate_block_on_conflict(self):
        """Este método valida se existe configuração de bloqueio através de conflito. Utilizando block_on_conflict e conflict_exists.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # TODO: LEVAR ESSA VALIDAÇÃO PARA O USUFRUTO
        # if self.configuration.block_on_conflict and self.conflict_exists:
        #     raise Exception(
        #         'Bloqueando após conflito com outro(s) servidor(es).')
        return True

    def validate_block_after_pay(self):
        """Este método valida se existe configuração de bloqueio após pagamento. Utilizando block_after_pay e paid.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.configuration.block_after_pay and self.paid:
            raise Exception("Bloqueando alteração de período(s) após pagamento.")
        return True

    def validate_max_alteration_usufruct(self):
        """Este método valida se existe configuração de quantidade máxima para alteração de usufrutos.
        Utilizando max_alteration_usufruct e alteration_usufruct_sum.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.max_alteration_usufruct
            and self.configuration.max_alteration_usufruct
            < self.alteration_usufruct_sum
        ):
            raise Exception(
                "Quantidade máxima(%s) de alterações excedida."
                % self.configuration.max_alteration_usufruct
            )
        return True

    def validate_months_exercise_first_acquitition(self):
        """Este método valida se existe configuração para quantidade mínima de meses em exercício para primeira aquisição de período.
        Utilizando months_exercise_first_acquitition e employee_exercise_months.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        """UTILIZAR NA CRIAÇÃO DOS PERÍODOS AQUISITIVOS QUE EXIGIREM CHECAGEM"""
        # TODO: SERÁ UTILIZADA APENAS NO MOMENTO DA CRIAÇÃO DO ACQUISITIONPERIOD
        if (
            self.configuration.months_exercise_first_acquitition
            and self.configuration.months_exercise_first_acquitition
            > self.employee_exercise_months
        ):
            raise Exception(
                "Tempo de exercício(%s), em meses, para adquirir direito a fruição do primeiro período não alcançado."
                % self.configuration.months_exercise_first_acquitition
            )
        return True

    def validate_months_exercise_next_acquitition(self):
        """Este método valida se existe configuração para quantidade mínima de meses em exercício para próximas aquisições de período.
        Utilizando months_exercise_next_acquitition e employee_exercise_months.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        """UTILIZAR NA CRIAÇÃO DOS PERÍODOS AQUISITIVOS QUE EXIGIREM CHECAGEM"""
        # TODO: SERÁ UTILIZADA APENAS NO MOMENTO DA CRIAÇÃO DO ACQUISITIONPERIOD
        if (
            self.configuration.months_exercise_next_acquitition
            and self.configuration.months_exercise_next_acquitition
            > self.employee_exercise_months
        ):
            raise Exception(
                "Tempo de exercício(%s), em meses, para adquirir direito a fruição a partir do segundo período não alcançado."
                % self.configuration.months_exercise_next_acquitition
            )
        return True

    def validate_days_per_period(self):
        """Este método valida se existe configuração para quantidade de dias por período. Utilizando days_per_period e booked_days.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.days_per_period
            and self.configuration.days_per_period < self.booked_days
        ):
            raise Exception(
                "Quantidade máxima(%s) de dias em um período foi excedida."
                % self.configuration.days_per_period
            )
        return True

    def validate_division_after_suspension(self):
        """Este método valida se existe configuração para quantidade máxima de divisões após suspensão.
        Utilizando division_after_suspension e division_after_suspension_sum.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.division_after_suspension
            < self.division_after_suspension_sum
        ):
            raise Exception(
                "Quantidade máxima(%s) de divisões após suspensão excedida."
                % self.configuration.division_after_suspension
            )
        return True

    def validate_suspend_acquisition_departures(self):
        """Este método valida se existe afastamento que suspende o período aquisitivo. Utilizando check_suspend_acquisition_departures.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.check_suspend_acquisition_departures:
            raise Exception("Existe um afastamento que suspendeu o período aquisitivo.")
        return True

    def transit_status(self, action, target, validate_prevent=False):
        """Este método realiza transição para target caso a action seja valida.
            Utiliza action_check para verificar se é possível a transição.

        Args:
            activity (str): Ação
            target (int): Estado alvo
            validate_prevent (bool): validate_prevent para o save
        Returns:
            bool:
        """
        action_check(action, self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        self.status = target
        self.save(validate_prevent=validate_prevent)

    def _define_status(self):
        action = None
        target = self.status
        if self.check_enjoyed:
            target, action = ACQP_FINISHED, "finalizar"
        elif self.check_prescribed and self.status != ACQP_FINISHED:
            target, action = ACQP_PRESCRIBED, "prescrever"
        elif (
            self.status == ACQP_WAIT
            and self.group_period.start_date_book
            and self.group_period.start_date_book <= datetime.now().date()
        ):
            target, action = ACQP_PROGRESS, "liberar"
        elif self.status == ACQP_FINISHED and not self.check_enjoyed:
            target, action = ACQP_PROGRESS, "liberar"
        return target, action

    def update_status(self, update_usufructs=True, validate_prevent=False):
        """Este método atualiza o status do período aquisitivo através do save.
        Realiza atualização dos usufrutos através de update_usufrutcs.

        Args:
            update_usufructs (bool): Atualizar usufrutos
            validate_prevent (bool): Evitar validação
        Raise:
            Exception: raise exception se a validação for habilitada e não passar
        """
        if update_usufructs:
            self.update_usufructs()

        target, action = self._define_status()

        if self.status != target:
            if not validate_prevent:
                action_check(
                    action, self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE
                )
            self.status = target
            self.save(validate_prevent=validate_prevent)

    def update_usufructs(self, force_status=USU_HOMOLOGATED, validate_prevent=False):
        """Este método atualiza o status dos usufrutos do período aquisitivo.

        Args:
            validate_prevent (bool): Evitar validação
        Raise:
            Exception: raise exception se a validação for habilitada e não passar
        """
        for usu in Usufruct.objects.filter(
            pk__in=self.activities.values("usufructs"),
            status__in=[USU_NEW, USU_AUTORIZED_CI, USU_HOMOLOGATED],
        ):
            usu.update_status(validate_prevent=validate_prevent)

    def notify_release(self, notify_prevent=False):
        """Este método envia a notificação se notify_prevent for False."""
        if not self.blocked and not notify_prevent:
            notify(
                "DOF_RELEASE_NOT",
                self.employee,
                self,
                group="%s" % self.group_period,
                start_date_fruition=DateUtils.date_to_str(self.start_date_fruition),
            )

    def book(
        self,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação book(marcar).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityBook): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityBook.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def change(
        self,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação change(alterar).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityChange): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityChange.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def rectify(
        self,
        days=None,
        usufructs_in=[],
        modifieds=[],
        authorize=True,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação change(alterar).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityRetify): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityRetify.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            days=days,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def remaining(
        self,
        days=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação change(Marcar remanescente).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityRemaining): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityRemaining.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def suspend(
        self,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Este método realiza ação suspend(suspender).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivitySuspend): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivitySuspend.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
        )

    def correct(
        self,
        days=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Este método realiza ação current(corrigir).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityCorrect): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityCorrect.do(
            days=days,
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
        )

    def interrupt(
        self,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Este método realiza ação interrupt(interromper).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityInterrupt): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityInterrupt.do(
            acquisition_period=self,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
        )

    def indemnify(
        self,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        activity=None,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Este método realiza ação indemnify(indenizar).

        Args:
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            activity (int): Activity pk
        Returns:
            activity (ActivityIndemnify): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        # TODO: IMPLEMENTAR INDEMNIFY issue 392
        return None

    def authorize(
        self,
        authorize=None,
        attachment=None,
        note=True,
        activity=None,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Este método realiza ação authorize(autorizar) do AcquisitionPeriod.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            note (bool): anotar
            activity (int): Activity pk
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context (str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("autorizar", self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        if type(activity) in (int, str):
            activity = self.activities.get(pk=int(activity))
        else:
            activity = self.activities.filter(authorized=None).last()
        if not activity:
            raise Exception("Atividade não informada")

        activity = activity.my_origin
        return activity.authorize(
            authorize=authorize,
            attachment=attachment,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def authorize_and_homologate(
        self,
        authorize=None,
        attachment=None,
        note=True,
        activity=None,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Este método realiza ação authorize_and_homologate(autorizar) do AcquisitionPeriod.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            note (bool): anotar
            activity (int): Activity pk
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("autorizar", self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        if type(activity) in (int, str):
            activity = self.activities.get(pk=int(activity))
        else:
            activity = self.activities.filter(authorized=None).last()
        if not activity:
            raise Exception("Atividade não informada")

        activity = activity.my_origin
        return activity.authorize_and_homologate(
            authorize=authorize,
            attachment=attachment,
            note=note,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )

    def homologate(
        self,
        attachment=None,
        note=True,
        activity=None,
        scale_homologation=False,
        context=None,
    ):
        """Este método realiza ação homologate(homologar).

        Args:
            attachment (Attachment): anexo informado
            note (bool): anotar
            activity (list): Activity list of pk
            scale_homologation (bool): se a escala está sendo homologada
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityHomologate): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("homologar", self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        if type(activity) in (int, str):
            activity = self.activities.filter(pk=int(activity))
        else:
            activity = self.activities.filter(homologated=False)
        if not activity:
            raise Exception("Atividade não informada")

        for act in activity:
            act = act.my_origin
            act.homologate(
                homologate=True,
                attachment=attachment,
                note=note,
                scale_homologation=scale_homologation,
                context=context,
            )
        return activity

    @classmethod
    def homologate_batch(
        cls,
        group=None,
        acquisition_period=None,
        activity=None,
        homologation_date=None,
        publication_date=None,
        attachment=None,
        note=True,
        scale_homologation=False,
        context=None,
    ):
        """Homologação em lote.

        Args:
            group (int): GroupPeriod.pk
            acquisition_period (list): list of AcquisitionPeriod.pk
            activity (list): list of Activity.pk
            homologation_date (date): data de publicação
            publication_date (int): data de publicação
            attachment (attachment_pk): pk do anexo
            note (bool): anotar
            scale_homologation (bool): indica se é homologação de escala
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityHomologateBatch): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """

        from rh.dayoff.tasks import homologate

        task = Task.start(
            homologate,
            group=group,
            acquisition_period=acquisition_period,
            activity=activity,
            homologation_date=homologation_date,
            publication_date=publication_date,
            attachment=attachment,
            scale_homologation=scale_homologation,
            context=context,
            user=get_current_user().username,
            success="""<p>
                Homologação de %(type_of_usufruct)s finalizada. Verifique resultado no arquivo
                <a href="/athenas/Action/file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>
                Este arquivo está disponível para download até dia
                <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
        )
        return task

    @classmethod
    def run_batch_homologation(
        cls,
        group=None,
        acquisition_period=[],
        activity=[],
        homologation_date=None,
        publication_date=None,
        attachment=None,
        scale_homologation=False,
        context=None,
        user=None,
        task=None,
    ):
        homologateds = []

        if homologation_date:
            homologation_date = DateUtils.str_to_date(homologation_date)
        if publication_date:
            publication_date = DateUtils.str_to_date(publication_date)

        attachment = Attachment.objects.get(pk=attachment) if attachment else attachment

        def homologate_group_acquisition_period(
            group,
            acquisition_period,
            task,
            homologation_date=None,
            publication_date=None,
            scale_homologation=False,
            attachment=None,
        ):
            acquisition_periods = AcquisitionPeriod.objects.none()
            if group:
                acquisition_periods = AcquisitionPeriod.objects.filter(
                    group_period__pk=group
                )
            elif acquisition_period:
                acquisition_periods = AcquisitionPeriod.objects.filter(
                    pk__in=acquisition_period
                )

            acquisition_periods = acquisition_periods.filter(
                activities__status__in=[ACT_ST_CREATED, ACT_ST_AUTHORIZED]
            )

            total = acquisition_periods.count()
            inc_progress = 100.0 / total
            for acquisition_period in acquisition_periods:
                try:
                    acquisition_period.homologate(
                        scale_homologation=scale_homologation, attachment=attachment
                    )
                    task.info(
                        msg=f"Período aquisitivo de {acquisition_period} homologado.",
                        type_of=1,
                    )
                    homologateds.append(acquisition_period.pk)
                except Exception as err:
                    log.exception(err)
                    print(err)
                    task.info(
                        msg=f"Período aquisitivo de {acquisition_period} não foi homologado: {err}",
                        type_of=3,
                    )
                Task.objects.filter(pk=task.pk).update(
                    progress=models.F("progress") + inc_progress
                )

            countdown = 3000
            count = 0
            while int(task.progress) != 100 and count < countdown:
                task = Task.objects.get(pk=task.pk)
                if int(task.progress) == 100:
                    count = countdown
                count += 1

            if group:
                group = GroupPeriod.objects.get(pk=group)
                group.attachment = attachment
                group.publication_date = publication_date
                group.homologation_date = homologation_date
                group.save()
            return homologateds

        def homologate_activity(activity, task, attachment=None):
            activities = Activity.objects.filter(pk__in=activity)
            total = activities.count()
            inc_progress = 100.0 / total
            for activity in activities:
                try:
                    activity.homologate(scale_homologation=True, attachment=attachment)
                    task.info(
                        msg=f"Período aquisitivo de {activity.acquisition_period} homologado.",
                        type_of=1,
                    )
                except Exception as err:
                    log.exception(err)
                    print(err)
                    task.info(
                        msg=f"Período aquisitivo de {activity.acquisition_period} não foi homologado: {err}",
                        type_of=3,
                    )
                Task.objects.filter(pk=task.pk).update(
                    progress=models.F("progress") + inc_progress
                )
            return homologateds

        if acquisition_period or group:
            homologateds = homologate_group_acquisition_period(
                group,
                acquisition_period,
                task,
                homologation_date,
                publication_date,
                scale_homologation,
                attachment,
            )
        if activity:
            homologateds = homologate_activity(activity, task, attachment)

        return len(homologateds)

    def sell(
        self,
        days,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação sell(vender).

        Args:
            days (int): quantidade de dias para a venda
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivitySell): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivitySell.do(
            acquisition_period=self,
            days=days,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            context=context,
        )

    def book_sell(
        self,
        days,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context="employee",
    ):
        """Este método realiza ação sell(vender).

        Args:
            days (int): quantidade de dias para a venda
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivitySell): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityBookSell.do(
            acquisition_period=self,
            days=days,
            usufructs_in=usufructs_in,
            modifieds=modifieds,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
            context=context,
        )

    def cancel_activity(
        self,
        modified=None,
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Este método realiza ação cancel(Cancelar).

        Args:
            modifieds (int): pk do Usufruct que será modificado/alterado
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityCancel): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        return ActivityCancel.do(
            acquisition_period=self,
            modified=modified,
            authorize=authorize,
            attachment=attachment,
            justification=justification,
            note=note,
        )

    def cancel_activities(self):
        """Este método cancela as atividades quando o total de dias for 0"""

        if self.group_period.configuration.delete_with_zero_days and self.days == 0:

            if self.activities.exclude(
                status__in=[USU_NEW, USU_AUTORIZED_CI, USU_HOMOLOGATED, USU_CANCELED]
            ).exists():
                message = f"Não foi possível cancelar os usufrutos do servidor {self.employee} do periodo {self.group_period}, \
                    pois, o servidor possui usufrutos já concluídos."
                self.notify_rh_admin(message)

            else:
                for activity in self.activities.exclude(canceled=True):
                    try:
                        activity = self.cancel(activity)
                        if activity and activity.canceled:
                            Notification.notify(
                                "DOF_CANCELED_EMPLOYEE",
                                self.employee,
                                type_of=self.group_period.configuration.get_type_of_usufruct_display(),
                                group="%s" % self.group_period,
                            )
                    except Exception as err:
                        log.exception(err)
                        message = f"Não foi possível cancelar os a atividade {activity} do servidor {self.employee}"
                        self.notify_rh_admin(message)

    def notify_rh_admin(self, message):
        """Este método notifica o RH sobre o cancelamento de um usufruto

        Args: message (str): mensagem a ser enviada

        """
        rh_employees = Servidor.objects.filter(
            Q(user__user_permissions__codename="dayoff_notify_admin")
            | Q(user__groups__permissions__codename="dayoff_notify_admin")
        ).distinct()
        for employer in rh_employees:
            Notification.notify("DAYOFF-NOTIFY-ADMIN", employer, msg=message)

    def cancel(self, activity=None):
        """Este método realiza ação cancel(cancelar).

        Args:
            activity (int): Activity pk
        Returns:

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("cancelar", self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        if type(activity) in (int, str):
            activity = self.activities.get(pk=int(activity))
        else:
            activity = self.activities.filter(canceled=False).last()
        if not activity:
            raise Exception("Atividade não informada")

        activity = activity.my_origin
        activity.cancel()
        return activity

    def exclude(self, activity=None):
        """Este método realiza ação exclude(Excluir).

        Args:
            activity (int): Activity pk
        Returns:

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        # action_check('cancelar', self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        if type(activity) in (int, str):
            activity = self.activities.get(pk=int(activity))
        if not activity:
            raise Exception("Atividade não informada")
        activity.exclude()

    def release(self):
        """Este método realiza ação release(liberar).

        Returns:

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("liberar", self.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)
        with transaction.atomic():
            # self.update_status()
            self.transit_status("liberar", ACQP_PROGRESS)
            self.notify_release()

    @classmethod
    def release_batch(cls, group_id):
        """Este método realiza a ação de liberar em lote através de uma Task.

        Args:
            group (int): GroupPeriod.pk
        Returns:
            activity (ActivityHomologateBatch): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        from rh.dayoff.tasks import run_release

        Task.start(run_release, group_id=group_id, user=get_current_user().pk)

    @classmethod
    def auto_authorization(cls):
        """Este método solicita autorização automática para as atividades(Activity) quando:
        - authorized=None
        - auto_authorization > 0
        - e a quantidade de dias após a criação for > auto_authorization
        Utiliza o usuário athenas e authorize_and_homologate.
        As exceções serão suprimidas pois as autorizações pendentes ficarão na interface do admin.
        """
        # TODO: ADICIONAR AO CRON - issue 474
        # TODO: VERIFICAR PERFORMANCE DESSA QUERY
        set_current_user("athenas")
        for activity in Activity.objects.filter(
            authorized=None,
            acquisition_period__group_period__configuration__auto_authorization__gt=0,
        ):
            if (
                NewDateRange(activity.created_at, datetime.now().date()).days - 1
            ) >= activity.configuration.auto_authorization:
                try:
                    activity = activity.my_origin
                    activity.authorize_and_homologate(authorize=True)
                except Exception as err:
                    log.exception(err)

    @classmethod
    def suspend_usufruct_by_departure(cls, departure):
        """Método responsável por verificar se o afastamento informado pode alterar as férias e se ele está nas
        configurações suspend_usufruct_departures. Todos usufrutos conflitantes serão alterados para época oportuna.
        """
        # FIXME: COMUNICAR AO RH QUE PARA FUNCIONAR PARA FÉRIAS É NECESSÁRIO QUE OCORRA MODIFICAÇÃO DO MÉTODO LicencaSaudeJuntaMedica.excluir_conflitos ADICIONANDO EXCLUSÃO DE CHECAGEM COM AFASTAMENTOS DE FÉRIAS
        if BaseLicencaAfastamento.validate_alteracao_ferias(departure, True):
            acquisition_periods = AcquisitionPeriod.objects.filter(
                employee=departure.servidor,
                group_period__configuration__suspend_usufruct_departures__value__in=[
                    departure.tipo
                ],
            ).filter(activities__usufructs__end_date__gte=departure.data_inicio)
            if departure.data_fim:
                acquisition_periods = acquisition_periods.filter(
                    activities__usufructs__start_date__lte=departure.data_fim
                )

            for acqp in acquisition_periods:
                try:
                    # TODO: verificar se será realizado interrupção, suspensão ou só alteração
                    acqp.change(
                        usufructs_in=[],
                        modifieds=acqp.usufructs,
                        context="admin",
                        justification=f"Alteração em função de {departure.situation_unicode}",
                    )
                except Exception as err:
                    log.exception(err)
                    print(err)

    @classmethod
    def authorize_batch(
        cls,
        authorize=None,
        attachment=None,
        note=True,
        activity=None,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Este método realiza ação authorize_and_homologate(autorizar) do AcquisitionPeriod.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            note (bool): anotar
            activity (int): Activity pk
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): ação realizada
        Raise:
            Exception: raise exception quando houver exceção em validações
        """

        from rh.dayoff.tasks import authorize as authorize_task

        task = Task.start(
            authorize_task,
            authorize=authorize,
            attachment=attachment,
            note=note,
            activity=activity,
            mediate_authorization=mediate_authorization,
            immediate_authorization=immediate_authorization,
            context=context,
            user=get_current_user().username,
        )
        return task

    # @deprecated
    @classmethod
    def acquisition_manager(cls, employee, start_date=None, end_date=None):
        """Este método é responsável por rodar a chamada para acquisition_manager, de acordo com classcode,
        de todos períodos aquisitivos de um employee.
        O parâmetro de instância employee é obrigatório para que este método funcione.

        Args:
            start_date (datetime.date): data de início de análise dos períodos aquisitivos
            end_date (datetime.date): data de fim de análise dos períodos aquisitivos

        Raise:
            Exception: raise exception quando self.employee não existe
        """
        from engine.mq.models import Task
        from rh.dayoff.tasks import call_acquisition_manager

        if not employee:
            raise Exception("O parâmetro employee é obrigatório para este método.")

        task = Task.start(
            call_acquisition_manager,
            employee=employee.pk,
            start_date=DateUtils.date_to_str(start_date),
            end_date=DateUtils.date_to_str(end_date) if end_date else None,
            user=get_current_user().username if is_current_user_admin() else "athenas",
            success="""<p>Atualização de Períodos Aquisitivos de %(employee)s finalizada.</p>""",
        )
        return task

    @deprecated
    @classmethod
    def prescription_manager(cls, employee):
        """Este método é responsável por rodar a chamada para acquisition_manager, de acordo com classcode,
        de todos períodos aquisitivos de um employee.
        O parâmetro de instância employee é obrigatório para que este método funcione.

        Raise:
            Exception: raise exception quando self.employee não existe
        """
        if not employee:
            raise Exception("O parâmetro employee é obrigatório para este método.")

        for group in GroupPeriod.objects.filter(acquisitionperiods__employee=employee):
            if group.classcode:
                group.classcode.cls(
                    group_period=group, employee=employee
                ).acquisition_manager()

    @classmethod
    def run_upgrade_aquisition_period(
        cls, acquisition_periods=[], update_usufructs=False
    ):
        """Este método chama atualização de Períodos Aquisitivos.

        Args:
            acquisition_periods (list): []
            update_usufructs (bool): False

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        from rh.dayoff.tasks import run_upgrade_aquisition_period

        task = Task.start(
            run_upgrade_aquisition_period,
            acquisition_periods=acquisition_periods,
            update_usufructs=update_usufructs,
            user=get_current_user().username,
            success="""<p>Atualização de Períodos Aquisitivos de %(employee)s finalizada.</p>""",
        )
        return task

    def upgrade_aquisition_period(self, task=None, update_usufructs=False):
        """Este método é responsável por rodar update_or_create_acquisition_period do Período Aquisitivo.

        Args:
            update_usufructs (bool): False

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        error = None
        mode = ""
        acqp = self
        try:
            _klass = acqp.classcode
            if _klass and _klass.cls:
                _klass = _klass.cls
                class_code_acqp = _klass(
                    group_period=acqp.group_period, acq_period=acqp
                )
                acqp, mode = class_code_acqp.update_or_create_acquisition_period(
                    update_usufructs=update_usufructs
                )
        except Exception as err:
            log.exception(err)
            error = err

        if error:
            if task:
                task.info(msg=f"Erro ao atualizar período {acqp} \n{error}", type_of=3)
            else:
                log.info(f"Erro ao atualizar período {acqp} \n{error}")
        elif mode == ACQP_CREATION_UPDATED:
            if acqp.diff:
                _message = ""
                if acqp.diff.get("pendency"):
                    _pendency_new = "Sim" if acqp.diff.get("pendency")[1] else "Não"
                    _message = f"Com pendência: {_pendency_new}\n"
                if acqp.diff.get("days"):
                    _message = f"{_message}Quantidade de dias mudou de {acqp.diff.get('days')[0]} para {acqp.diff.get('days')[1]}\n"
                if acqp.diff.get("info") and acqp.diff.get("info")[1]:
                    _message = f"{_message}Info: {acqp.diff.get('info')[1]}\n"

                if task and _message:
                    _message = f"Período aquisitivo ({acqp}) atualizado\n{_message}"
                    task.info(msg=_message, type_of=2)
                else:
                    log.info(_message)
            elif acqp.info:
                if task:
                    task.info(
                        msg=f"Período aquisitivo ({acqp}) atualizado: {acqp.info}",
                        type_of=2,
                    )
                else:
                    log.info(f"Período aquisitivo ({acqp}) atualizado: {acqp.info}")
        elif task:
            task.info(msg=f"{mode}: {acqp}", type_of=2)
        else:
            log.info(f"{mode}: {acqp}")

    @classmethod
    def change_homologated_autorized_to_opportune_time(cls, employee):
        status = [USU_HOMOLOGATED, USU_AUTORIZED_CI]
        acqps = AcquisitionPeriod.objects.filter(
            activities__usufructs__end_date__gte=employee.data_desligamento,
            employee=employee,
            activities__usufructs__status__in=status,
        )
        for acqp in acqps:
            usufructs = list(
                acqp.usufructs.filter(
                    status__in=status,
                ).values_list("pk", flat=True)
            )

            if usufructs:
                acqp.change(modifieds=usufructs, context="admin")


class AcquisitionPeriodAttachment(AuditTimestampModel):
    acquisition_period = models.ForeignKey(
        AcquisitionPeriod,
        null=True,
        blank=True,
        verbose_name="Periodo Aquisitivo",
        related_name="attachment_acquisitionperiod",
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        help_text="Descrição do período aquisitivo",
        verbose_name="Descrição",
        blank=True,
        null=True,
    )
    information = models.TextField(verbose_name="Informação", blank=True, default="")
    date_start = models.DateField(
        null=True, blank=True, verbose_name="Data início do exercício"
    )
    date_end = models.DateField(
        null=True, blank=True, verbose_name="Data fim do exercício"
    )
    days_law = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        verbose_name="Quantidade de Dias de direito",
    )
    attachment = models.ForeignKey(
        "Attachment",
        on_delete=models.SET_NULL,
        help_text="Referencia do anexo do periodo aquisitivo",
        verbose_name="Anexo",
        blank=True,
        null=True,
        related_name="attachment_acquisitionperiod",
    )
    status = models.SmallIntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name="Status",
        choices=Choice.get_choices_for(
            "dayoff", "DAYOFF_ACQUISITION_PERIOD_ATTACHMENT_STATUS"
        ),
    )

    class Meta:
        verbose_name = "Anexo Período Aquisitivo"
        ordering = ("-date_end",)

    def __str__(self):
        return self.description if self.description else ""

    @transaction.atomic
    def save(self, *args, **kargs):
        try:
            self.validate()

            super(AcquisitionPeriodAttachment, self).save(*args, **kargs)
            self._sum_days_acquisition_period()
            self.acquisition_period.update_annotation()
            self.acquisition_period.annotation_text()
        except Exception as err:
            log.exception(err)
            raise err

    @property
    def acquisition_period_str(self):
        return self.acquisition_period.__str__

    def delete(self, *args, **kwargs):
        try:
            self._subtract_days_acquisition_period()
            current_acquisition_period = self.acquisition_period

            super(AcquisitionPeriodAttachment, self).delete(*args, **kwargs)
            current_acquisition_period._update_days(to_save=True)
            current_acquisition_period.update_annotation()
            current_acquisition_period.annotation_text()
        except Exception as err:
            log.exception(err)
            raise err

    def validate(self):
        self._validate_start_acquisition()
        self._validate_end_acquisition()

        self._validate_date_start()
        self._validate_date_end()

    def _validate_start_acquisition(self):
        if not self.acquisition_period.start_date_acquisition:
            raise Exception(
                "Favor preencher a data Início aquisição do Período aquisitivo selecionado."
            )
        return True

    def _validate_end_acquisition(self):
        if not self.acquisition_period.end_date_acquisition:
            raise Exception(
                "Favor preencher a data Fim aquisição do Período aquisitivo selecionado."
            )
        return True

    def _validate_date_start(self):
        if not self.date_start:
            raise Exception("Favor preencher a Data início.")
        if self.date_start < self.acquisition_period.start_date_acquisition:
            raise Exception(
                "Data início deve ser maior ou igual à data Início aquisição do Período aquisitivo selecionado."
            )
        if self.date_end and self.date_start > self.date_end:
            raise Exception("Data início deve ser menor ou igual à Data fim.")
        return True

    def _validate_date_end(self):
        if not self.date_end:
            raise Exception("Favor preencher a Data fim.")
        if self.date_end > self.acquisition_period.end_date_acquisition:
            raise Exception(
                "Data fim deve ser menor ou igual à data Fim aquisição do Período aquisitivo selecionado."
            )
        if self.date_end < self.date_start:
            raise Exception("Data fim deve ser maior ou igual à Data início.")
        return True

    def _sum_days_acquisition_period(self):
        number_of_days = 0
        attachments = self.acquisition_period.attachment_acquisitionperiod.all()
        if self.pk:
            for attachment in attachments.exclude(pk=self.pk):
                number_of_days += attachment.days_law
        else:
            for attachment in attachments:
                number_of_days += attachment.days_law

        if self.days_law:
            number_of_days += decimal.Decimal(self.days_law)

        self.acquisition_period.days = number_of_days
        return self.acquisition_period.save()

    def _subtract_days_acquisition_period(self):
        self.acquisition_period.days -= self.days_law
        self.acquisition_period.save()


class Usufruct(AuditTimestampModel):

    YEAR_CHOICES = [(y, y) for y in range(1970, dt.date.today().year + 10)]
    MONTH_CHOICE = [(m, m) for m in range(1, 13)]
    INSTALLMENTS_CHOICE = [(i, i) for i in range(1, 100)]

    activity = models.ForeignKey(
        "Activity",
        on_delete=models.CASCADE,
        help_text="Usufrutos criados",
        verbose_name="Usufrutos criados",
        related_name="usufructs",
    )
    status = models.SmallIntegerField(
        default=USU_NEW,
        help_text="Situação atual desse usufruto",
        verbose_name="Situação",
        choices=Choice.get_choices_for("dayoff", "USUFRUCT_STATUS_CHOICE"),
    )
    start_date = models.DateField(
        help_text="Início da fruição desse período",
        verbose_name="Início",
        blank=True,
        null=True,
    )
    end_date = models.DateField(
        help_text="Fim da fruição desse período",
        verbose_name="Fim",
        blank=True,
        null=True,
    )
    days = models.SmallIntegerField(
        default=0, help_text="Quantidade de dias marcados", verbose_name="Dias marcados"
    )
    from_scale = models.BooleanField(
        default=False,
        help_text="""Informar se o usufruto faz parte da marcação da escala""",
        verbose_name="Marcação da escala",
        blank=True,
    )
    departure = models.ForeignKey(
        BaseLicencaAfastamento,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Afastamento do usufruto",
        related_name="dayoff_usufructs",
    )
    payment_installments = models.IntegerField(
        choices=INSTALLMENTS_CHOICE,
        null=True,
        blank=True,
        verbose_name="Parcelas de pagamento",
    )
    payment_year = models.IntegerField(
        choices=YEAR_CHOICES,
        null=True,
        blank=True,
        verbose_name="Ano de Pagamento",
    )
    payment_month = models.IntegerField(
        choices=MONTH_CHOICE,
        null=True,
        blank=True,
        verbose_name="Mês de pagamento",
    )
    justification = models.TextField(
        verbose_name="Justificativa", null=True, blank=True
    )
    numero_parcela = models.SmallIntegerField(
        verbose_name="Número da parcela",
        null=True,
        blank=True,
    )

    usu_out = None

    @property
    def icons(self):
        icons = []
        if self.status == USU_NEW:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_new"],
                    "title": "Parcela marcada e aguardando autorização",
                    "alt": "Nova",
                }
            )
        elif self.status == USU_AUTORIZED_CI:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_authorized"],
                    "title": "Parcela autorizada pela chefia",
                    "alt": "Autorizado",
                }
            )
        elif self.status == USU_NOT_AUTHORIZED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_not_authorized"],
                    "title": "Parcela indeferida pela chefia",
                    "alt": "Não autorizado",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.status == USU_HOMOLOGATED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["homologated"],
                    "title": "Parcela homologada pelo RH",
                    "alt": "Homologado",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.status == USU_ENJOYED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_enjoyed"],
                    "title": "Parcela fruída",
                    "alt": "Fruída",
                }
            )
        elif self.status == USU_ENJOYING:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_enjoying"],
                    "title": "Parcela em fruíção",
                    "alt": "Fruíndo",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.status == USU_SUSPENDED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_suspended"],
                    "title": "Parcela suspensa pela administração",
                    "alt": "Suspensa",
                }
            )
        elif self.status == USU_INTERRUPTED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_interrupted"],
                    "title": "Parcela interrompida pela administração",
                    "alt": "Interrompida",
                }
            )
        elif self.status == USU_CHANGED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_changed"],
                    "title": "Parcela alterada",
                    "alt": "Alterada",
                }
            )
        elif self.status == USU_CHANGING:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_changing"],
                    "title": "Aguardando autorização de alteração...",
                    "alt": "Em alteração",
                }
            )
        elif self.status == USU_CANCELED:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["denied"],
                    "title": "Cancelado",
                    "alt": "Cancelado",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        if self.conflict_exists:
            icons.append(
                {
                    "icon": DAYOFF_ICONS_THEME["usu_conflict"],
                    "title": "Parcela conflita com a de outro membro/servidor.",
                    "alt": "Conflito",
                }
            )
        else:
            icons.append(
                {"icon": DAYOFF_ICONS_THEME["blank"], "title": "", "alt": "--"}
            )

        return icons

    @property
    def my_origin(self):
        instance = self
        if UsufructSell.objects.filter(pk=self.pk).exists():
            instance = UsufructSell.objects.get(pk=self.pk)
        return instance

    def __str__(self):
        if self.start_date and self.end_date:
            return "%s - %s - %s - %s" % (
                DateUtils.date_to_str(self.start_date),
                DateUtils.date_to_str(self.end_date),
                self.days,
                self.get_status_display(),
            )
        return "%s - %s" % (
            self.days,
            self.get_status_display(),
        )

    @property
    def status_name(self):
        return self.get_status_display()

    @property
    def type_activity(self):
        if not self.start_date:
            return "Venda"
        else:
            return "Usufruto"

    @property
    def origin_of_request(self):
        return (
            ORIGIN_REQUEST[PORTAL]
            if self.activity.activity_requests.filter()
            else ORIGIN_REQUEST[MANUAL]
        )

    @property
    def activity_label(self):
        return self.activity.get_type_of_activity_display()

    @property
    def prev_competence_paid(self):
        tipo_atividade = self.activity.type_of_activity if self.activity else None
        if (
            self.ctrl_payments.filter(payroll_ctrl_status=PAYMENT_FINALIZED).exists()
            and tipo_atividade == ACT_SUSPEND
        ):
            return None
        if self.payment_month and self.payment_year:
            return f"{self.payment_month}/{self.payment_year}"
        return None

    @property
    def competence_paid(self):
        tipo_atividade = self.activity.type_of_activity if self.activity else None
        if self.ctrl_payments.filter(payroll_ctrl_status=PAYMENT_FINALIZED).exists():
            if tipo_atividade == ACT_SUSPEND:
                return None
            text = ""
            for payment in self.ctrl_payments.all():
                text += f"{self.payment_month }/{self.payment_year}| {self.payment_installments}(PAGO)"
            return text
        return None

    @property
    def competence_paid_str(self):
        competencia_paga = self.competence_paid
        if competencia_paga:
            return competencia_paga
        if self.payment_month and self.payment_year:
            return f"{self.payment_month }/{self.payment_year}| {self.payment_installments}(Pendente)"
        return None

    @property
    def _payments_to_str(self):
        text = ""
        return text

    @property
    def ordination_date(self):
        if self.activity_modifieds.filter():
            activity = (
                self.activity_modifieds.filter()
                .exclude(activity__type_of_activity=ACT_CORRECT)
                .first()
            )
            date_relevance = None
            for usufruct in activity.usufructs.filter():
                if date_relevance:
                    if usufruct.start_date < date_relevance:
                        date_relevance = usufruct.start_date
            return date_relevance

    @classmethod
    def create(
        cls,
        activity,
        start_date=None,
        end_date=None,
        days=None,
        numero_parcela=None,
        payment_installments=None,
    ):
        """Este método cria uma instância de Usufruct de acordo com os parâmetros enviados.
        Este método contabiliza quantos dias serão fruídos.

        Args:
            start_date (datetime.date): início do usufruto
            end_date (datetime.date): fim do usufruto
            activity (Activity): atividade
        Returns:
            activity (Activity): atividade realizada
        """
        from_scale = (
            activity.acquisition_period.group_period.homologation_date is not None
        )

        if not days and (start_date and end_date):
            days = NewDateRange(start_date, end_date).days

        if not days and (None in (start_date, end_date)):
            raise Exception("Informe a data de inicio e data de fim do usufruto")

        usufruct = cls(
            start_date=start_date,
            end_date=end_date,
            activity=activity,
            days=days,
            from_scale=from_scale,
            numero_parcela=numero_parcela,
            payment_installments=payment_installments,
        )

        return usufruct

    def atualizar_activity_comp_pgto(self):
        pa = self.activity.acquisition_period

        q_pa = (
            pa.activities.exclude(status=ACT_ST_CANCELED)
            .filter(type_of_activity=ACT_BOOK_SELL)
            .order_by("-created_at")
        )

        for a in q_pa:
            a.usufructs.filter(
                status=USU_SOLD,
            ).update(
                activity=a,
                payment_year=self.payment_year,
                payment_month=self.payment_month,
            )

    def save(self, *args, **kwargs):
        self.set_days()
        self.validate(validate_prevent=kwargs.get("validate_prevent", False))

        if "validate_prevent" in kwargs:
            kwargs.pop("validate_prevent")

        first_save = True if not self.pk else False
        super(Usufruct, self).save(*args, **kwargs)
        self.set_competencia(first_save)
        # self.atualizar_activity_comp_pgto()

    def set_competencia(self, first_save):
        if not self.prev_competence_paid and not self.verifica_vinculo_pgto(
            self.activity.modifieds.filter()
        ):
            self.activity.set_payment_competence(first_save)

    def verifica_vinculo_pgto(self, usufrutos_retificados):
        if (
            self.activity.type_of_activity == ACT_RECTIFY
            and len(usufrutos_retificados) > 0
        ):
            if self.usu_out and self.usu_out.competence_paid:
                return True
        return False

    def set_days(self):
        """Este conta e aplica quantos dias decorrem no usufruto ao campo days."""
        if self.start_date and self.end_date:
            self.days = NewDateRange(self.start_date, self.end_date).days

    def _define_status(self, status=None):
        action = None
        today = datetime.now().date()
        status = status or self.status
        if status == USU_HOMOLOGATED and self.start_date is None:
            action = "homologar"
            status = USU_SOLD
        elif self.end_date and self.end_date < today:
            action = "finalizar"
            status = USU_ENJOYED
            log.debug("FRUIDA: %s" % DateUtils.date_to_str(self.end_date))
        elif self.start_date and self.start_date < today:
            action = "fruir"
            status = USU_ENJOYING
            log.debug("FRUINDO: %s" % DateUtils.date_to_str(self.start_date))
        return status, action

    def update_status(self, validate_prevent=False):
        """Este método atualiza o status.

        Args:
            validate_prevent (bool): Evitar validação
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        status = self._define_status()[0]
        if self.status != status:
            self.status = status
            self.save(validate_prevent=validate_prevent)

    def transit_status(self, action, target, validate_prevent=False):
        """Este método realiza transição para target caso a action seja valida.
        Utiliza action_check para verificar se é possível a transição.

        Args:
            activity (str): Ação
            target (int): Estado alvo
            validate_prevent (bool): validate_prevent para o save
        Returns:
            bool:
        """
        if not validate_prevent:
            action_check(action, self.status, USU_SM, USUFRUCT_STATUS_CHOICE)
        self.status = target
        self.save(validate_prevent=validate_prevent)

    @property
    def configuration(self):
        return self.activity.acquisition_period.configuration

    @property
    def type_usufruct_name(self):
        return (
            self.activity.acquisition_period.configuration.get_sub_type_of_usufruct_display()
        )

    @property
    def type_usufruct(self):
        return self.activity.acquisition_period.configuration.sub_type_of_usufruct

    @property
    def acquisition_period(self):
        return self.activity.acquisition_period

    @property
    def employee(self):
        return self.activity.acquisition_period.employee

    @property
    def start_date_acquisition(self):
        return self.activity.acquisition_period.start_date_acquisition

    @property
    def left_days(self):
        """Esta propriedade calculará quantos dias faltam para o dia de início da fruição.

        Returns:
            int:
        """
        days = 0
        if self.start_date:
            today = datetime.now().date()
            days = (
                NewDateRange(today, self.start_date).days
                if today <= self.start_date
                else 0
            )
        return days

    @property
    def is_interruption_suspension(self):
        """Esta propriedade verificará se a ação é de interrupção ou suspensão.

        Returns:
            bool:
        """
        return self.activity.type_of_activity in (ACT_INTERRUPT, ACT_SUSPEND)

    @property
    def is_sell_usufruct(self):
        """
        Esta propriedade identifica se se trata de venda, retornando True se for usufruto de venda
        e False caso contrário
        :returns: (bool)
        """
        if UsufructSell.objects.filter(pk=self.pk).exists():
            return True
        return False

    @property
    def payment_competence(self):
        return f"{self.payment_month}/{self.payment_year}"

    @property
    def left_work_days(self):
        """Esta propriedade calculará quantos dias úteis faltam para o dia de início da fruição.
        Returns:
            int:
        """
        today = datetime.now().date()
        return (
            working_days(date_range=NewDateRange(today, self.start_date))
            if today <= self.start_date
            else 0
        )

    @property
    def remaining_balance_suspension(self):
        """Esta propriedade calculará o saldo remanescente de suspensão.
        Returns:
            int:
        """
        book_remaining = 0
        activity_modifieds_days = 0
        for mod in self.activity.modifieds.filter(
            activity__type_of_activity=ACT_REMAINING
        ):
            book_remaining = book_remaining + mod.days

        if self.status == USU_SUSPENDED:
            if (
                self.activity_modifieds.exclude(type_of_activity=ACT_CORRECT)
                .first()
                .usufructs.exists()
            ):
                activity_modifieds_days = (
                    self.activity_modifieds.exclude(type_of_activity=ACT_CORRECT)
                    .first()
                    .usufructs.first()
                    .days
                )
            return self.days - activity_modifieds_days - book_remaining

        return 0

    @property
    def retification_usufruct_sum(self):
        """Esta propriedade retornará o somatório da quantidade de retificações do usufruto.

        Returns:
            int:
        """
        modified = self
        is_retification = isinstance(self.activity.my_origin, ActivityRetify)
        count = 0
        while is_retification:
            count = count + 1
            modified = modified.activity.modifieds.first()
            is_retification = isinstance(modified.activity.my_origin, ActivityRetify)

        return count

    @property
    def is_suspension(self):
        return True if self.status == USU_SUSPENDED else False

    @property
    def is_retification(self):
        return True if self.status == USU_CHANGED else False

    @property
    def parcelas_detalhadas(self):
        if self.type_usufruct == INDIVIDUAL_VACATION:
            parcelas_list = []
            usufrutos = self.acquisition_period.usufructs.exclude(
                status__in=[4096, 2048, 16]
            )  # Vendido, Cancelado, Alterado (USUFRUCT_STATUS_CHOICE))
            for usufruto in usufrutos:
                parcelas_list.append(
                    {
                        "parcela": f'Parcela {usufruto.numero_parcela if usufruto.numero_parcela else ""}',
                        "flag": competence_paid_unicode(usufruto),
                    }
                )
            return parcelas_list
        return None

    @property
    def allows_suspend(self):
        if self.status in [USU_HOMOLOGATED, USU_ENJOYED, USU_ENJOYING]:
            return True
        return False

    @property
    def conflict_exists(self):
        # TODO: CRIAR CONFIGURAÇÃO PARA INDICAR SE É PRA CHECAR/VALIDAR CONFLITOS
        # TODO: SEPARAR VALIDAÇÕES QUE ESTÃO EM CONFLICTS PARA CADA CLASSCODE E DEIXAR O BASE APENAS COM O NECESSÁRIO
        # return self.acquisition_period.classcode_instance().conflicts(usufruct=self, limit=1)
        return False

    def get_conflicts(self, limit=1):
        return self.acquisition_period.classcode_instance().get_conflicts(
            usufruct=self, limit=limit
        )

    def checked_validate_recess(self):
        if (
            self.acquisition_period.group_period.configuration.sub_type_of_usufruct
            in [INTERNS_RECESS, RESIDENT_RECESS]
            and self.acquisition_period.group_period.start_date_automatic_usufruct
            == self.start_date
            and self.acquisition_period.group_period.end_date_automatic_usufruct
            == self.end_date
        ):
            return True
        return False

    def validate(self, validate_prevent=False, validate_job=False):
        if not validate_prevent:
            self.validate_start_and_end_date()
            if not self.checked_validate_recess():
                self.validate_range_fruition()
            self.validate_min_days_division()
            self.validate_days_precede_fruition()
            self.validate_work_days_precede_fruition()
            self.validate_retroactive()
            self.validate_conflicts_between_usufructs()
            self.validate_conflict_substitutes()
            self.validate_departure()
            self.validate_chronological_fruition()
            self.validate_start_end_date_book_scale()
            self.validate_usufruct_amendment()
            self.validate_substitution()

            # classcode = self.acquisition_period.classcode
            # _clscode_inst = classcode.cls(employee=self.acquisition_period.employee)
            # _clscode_inst.validate(usufruct=self)
            # _clscode_inst.conflicts(usufruct=self, limit=10)
        return True

    def validate_range_fruition(self):
        """Este método valida se a fruição está dentro do período de fruição.
        Utiliza start_date_fruition e end_date_fruition do AcquisitionPeriod.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        dr_max_fruition = NewDateRange(
            self.acquisition_period.start_date_fruition,
            self.acquisition_period.end_date_fruition,
        )
        dr_usu = NewDateRange(self.start_date, self.end_date)
        if dr_usu.intersect(dr_max_fruition).days != dr_usu.days:
            if self.activity.acquisition_period.employee.type_by_possession in [
                "EST",
                "RES",
            ]:
                return True

            raise Exception(
                "O período marcado(%s a %s) está fora dos limites de fruição %s a %s."
                % (
                    DateUtils.date_to_str(self.start_date),
                    DateUtils.date_to_str(self.end_date),
                    DateUtils.date_to_str(self.acquisition_period.start_date_fruition),
                    (
                        DateUtils.date_to_str(self.acquisition_period.end_date_fruition)
                        if self.acquisition_period.end_date_fruition
                        else "---"
                    ),
                )
            )
        return True

    def validate_min_days_division(self):
        """Este método valida configuração para a quantidade de dias mínimos por divisão de Usufrut.
        Utiliza min_days_division e days.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        if not self.activity.is_interruption_suspension_acquisitionperiod:
            user_admin = is_current_user_admin() and self.activity.context == "admin"
            min_days_division = self.configuration.min_days_division
            if user_admin and self.configuration.min_days_division_admin:
                min_days_division = self.configuration.min_days_division_admin

            if min_days_division > self.days:
                raise Exception(
                    "Quantidade mínima(%s) de dias por parcela excedida pois está marcando %s."
                    % (min_days_division, self.days)
                )

            max_days_division = self.acquisition_period.days - min_days_division

            days_remaining = self.activity.days_remaining
            days_not_booked = abs(
                self.activity.days_out - self.acquisition_period.days_not_booked
            )
            days_remaining_after_this = days_remaining - self.days
            if days_not_booked != self.days or (
                days_not_booked == self.days and days_remaining_after_this > 0
            ):
                if not (
                    self.days == self.acquisition_period.real_days
                    or (min_days_division <= self.days <= max_days_division)
                ):
                    raise Exception(
                        "Você deve marcar uma parcela de %d dias ou entre %d e %d"
                        % (
                            self.acquisition_period.real_days,
                            min_days_division,
                            max_days_division,
                        )
                    )
        return True

    def validate_days_precede_fruition(self):
        """Este método valida configuração para a quantidade de dias mínimos que precedem a fruição.
        Utiliza days_precede_fruition e left_days.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        if (
            not is_current_user_admin()
            and self.configuration.days_precede_fruition
            and self.configuration.days_precede_fruition > self.left_days
        ):
            raise Exception(
                "Quantidade mínima(%s) de dias antes de fruição excedida."
                % self.configuration.days_precede_fruition
            )
        return True

    def validate_work_days_precede_fruition(self):
        """Este método valida configuração para a quantidade de dias úteis mínimos que precedem a fruição.
        Utiliza work_days_precede_fruition e left_work_days.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        if (
            not is_current_user_admin()
            and self.configuration.work_days_precede_fruition > self.left_work_days
        ):
            raise Exception(
                "Quantidade mínima(%s) de dias úteis antes de fruição excedida."
                % self.configuration.work_days_precede_fruition
            )
        return True

    def validate_retroactive(self):
        """Este método verifica se a marcação retroativa está sendo feita por admin.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        if not is_current_user_admin() and self.start_date <= datetime.now().date():
            raise Exception(
                "Sua parcela não pode ser anterior à data de hoje. Para marcação retroativa solicite ao DEPARTAMENTO RESPONSÁVEL."
            )
        return True

    def validate_conflicts_between_usufructs(self):
        """Este método verifica se o usufruto possui conflito de datas com outro usufruto.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        message = ""
        for con in self.conflicts_between_usufructs():
            message = "%s\n%s" % (message, con)
        if message:
            raise Exception("%s conflita com outra já marcada %s" % (self, message))
        return True

    def validate_conflict_substitutes(self):
        """Este método verifica se existe conflito com seus substitutos.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        # TODO: IMPLEMENTAR - ISSUE 394
        # antigo .validate_conflito_externo
        # validação realizada após save
        # if deve_checar: # if not force:
        #     conflicts = self.conflito(self)
        #     if conflicts is not False:
        #         message = """Sua parcela não pode ser marcada para esta data, pois está em conflito com todos os seus
        #             substitutos. Infringindo, contudo, o Art. 3° do Ato 220/2005."""
        #         for conflito in conflicts:
        #             message += "%s - %s" % (conflito.periodo_aquisitivo_servidor.servidor, conflito)
        #         raise Exception(message)
        return True

    def validate_division_after_suspension(self, usufructs_exclude=[]):
        """Este método valida se existe configuração para quantidade máxima de divisões após suspensão.
        Utilizando division_after_suspension e division_after_suspension_sum.

        Params:
            usufructs_exclude(list): list de usufrutos que devem ser excluídos
        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # TODO: ISSUE 391 IMPLEMENTAR, VERIFICAR MÉTODO(DE MESMA ASSINATURA) ACIMA COM CONFIGURAÇÃO
        # def validate_condicionado_a_quantidade_de_parcelas_possíveis_apos_suspensao
        # validação realizada após save
        # # VALIDATE Verifica se ainda possui uma parcela disponível ou se esse periodo aquisitivo servidor ja teve alguma
        # # parcela interrompida, pois caso haja, a parcela a ser marcada deve COMPLETAR a quantidade de dias restantes
        # qtd_dias_restante = self.quantidade_dias - self.dias_marcados + dias_pasus_exclude - self.paid_days
        # if deve_checar: # if not force:
        #     qtd_pasu_valido = self.usufrutos.filter(
        # estado__in=[PASU_NOVO, PASU_AUTORIZADO_CI, USU_HOMOLOGATED, USU_CHANGING, USU_ENJOYING, PASU_FRUIDO, USU_INTERRUPTED]
        # estado__in=[PASU_NOVO, PASU_AUTORIZADO_CI, USU_HOMOLOGATED, USU_CHANGING, USU_ENJOYING, PASU_FRUIDO] usar esse
        #     ).count()
        #     qtd_pasu_disponivel = self.periodo_aquisitivo.configuracao.max_divisoes - (qtd_pasu_valido - len(exclude_pasus))
        #     if qtd_pasu_disponivel == 0 or qtd_pasu_disponivel == 1:
        #         if pasu.dias != qtd_dias_restante:
        #             raise ValidateFeriasError("Você deve marcar todos os %s dias restantes nessa parcela." % (qtd_dias_restante))

        # min_dias_por_divisao = self.periodo_aquisitivo.configuracao.min_dias_por_divisao
        # diff = self.quantidade_dias - min_dias_por_divisao
        # if abs(dias_pasus_exclude - self.dias_nao_marcados) != pasu.dias or (
        #         abs(dias_pasus_exclude - self.dias_nao_marcados) == pasu.dias and (qtd_dias_restante - pasu.dias) > 0):
        #     # VALIDATE Verifica se a quantidade de dias é a quantidade de dias adquiridos ou se é maior que a quantidade mínima permitida
        # if ((not force) and not (pasu.dias == self.quantidade_dias or (min_dias_por_divisao <= pasu.dias <= diff))):
        # if (deve_checar and not (pasu.dias == self.quantidade_dias or (min_dias_por_divisao <= pasu.dias <= diff))):
        #         raise ValidateFeriasError("Você deve marcar uma parcela de %d dias ou entre %d e %d" % (
        #             self.quantidade_dias, min_dias_por_divisao, diff)
        #         )
        # # VALIDATE: Quantidade de dias < do q os dias adquiridos para o período
        # if not self.periodo_aquisitivo.periodo_anterior:
        #     if self.data_fim_usufruto:
        #         log.debug(self.data_fim_usufruto)
        #         if not (self.data_inicio_usufruto <= pasu.data_inicio <= pasu.data_fim <= self.data_fim_usufruto):
        #             raise ValidateFeriasError("Suas férias só podem ser usufruídas entre %s e %s" % (
        #                 self.data_inicio_usufruto.strftime("%d/%m/%Y"), self.data_fim_usufruto.strftime("%d/%m/%Y")))
        #     else:
        #         if not (self.data_inicio_usufruto <= pasu.data_inicio):
        #             raise ValidateFeriasError("Suas férias só podem ser usufruídas após %s" % (
        #                 self.data_inicio_usufruto.strftime("%d/%m/%Y")))
        return True

    def validate_departure(self):
        # antigo .validar_usufrutos_afastamento
        """
        Este método verifica se o pasu novo não possui impedimento para criação.
        """
        if self.acquisition_period.check_block_usufruct_departures:
            _klass = self.configuration.departure_class
            dr_usu = NewDateRange(self.start_date, self.end_date)
            """remove afastamentos de usufrutos que estão sendo alterados"""
            departure_exclude = []
            for usu in self.activity.usufructsout:
                dr_usu_exclude = NewDateRange(usu.start_date, usu.end_date)
                if dr_usu.intersect(dr_usu_exclude).days > 0:
                    for dep in _klass.objects.filter(
                        servidor=self.employee,
                        data_inicio=usu.start_date,
                        data_fim=usu.end_date,
                    ).values("pk"):
                        departure_exclude.append(dep.get("pk"))

            """após cancelamento o usufruto retorna para homologado, mas pode ter vindo de uma (ACT_INTERRUPT, ACT_SUSPEND, ACT_CHANGE) e pode chocar com algum afastamento que ainda está sendo cancelado"""
            if self.pk:
                act_mdf = self.activity_modifieds.filter(
                    type_of_activity__in=(ACT_INTERRUPT, ACT_SUSPEND, ACT_CHANGE)
                ).last()
                if act_mdf and act_mdf.usufructs.exists():
                    for usu in act_mdf.usufructs.filter():
                        dr_usu_exclude = NewDateRange(usu.start_date, usu.end_date)
                        if dr_usu.intersect(dr_usu_exclude).days > 0:
                            for dep in _klass.objects.filter(
                                servidor=self.employee,
                                data_inicio=usu.start_date,
                                data_fim=usu.end_date,
                            ).values("pk"):
                                departure_exclude.append(dep.get("pk"))

            departure = _klass.objects.filter(
                servidor=self.employee,
                data_inicio=self.start_date,
                data_fim=self.end_date,
            ).exclude(estado=CANCELED)
            if (
                self.pk
                and self.status in (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED)
                and departure.count() == 1
            ):
                departure_exclude.append(departure.last().pk)
            try:
                BaseLicencaAfastamento.verifica_sobreposicao_periodo(
                    servidor=self.activity.employee,
                    data_inicio=self.start_date,
                    data_fim=self.end_date,
                    pk=self.pk,
                    cancelado=False,
                    exclude=departure_exclude,
                    query_filter=Q(
                        tipo__in=self.configuration.block_usufruct_departures.values(
                            "value"
                        )
                    ),
                )
            except Exception as err:
                raise Exception("O usufruto %s %s =>" % (self, err))
        return True

    def validate_chronological_fruition(self):
        """Este método valida se existe configuração de fruição cronológica. Utilizando chronological_fruition e check_chronological_fruition.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.configuration.chronological_fruition:
            acquisition_periods = AcquisitionPeriod.objects.filter(
                Q(employee=self.employee)
                & Q(
                    group_period__configuration__type_of_usufruct=self.configuration.type_of_usufruct
                )
            ).exclude(pk=self.acquisition_period.pk)
            if acquisition_periods.filter(
                start_date_acquisition__lt=self.acquisition_period.start_date_acquisition,
                booked_days_cache__lt=F("real_days_cache"),
            ).exists():
                raise Exception(
                    "Fruição cronológica não foi seguida. Existem Períodos Aquisitivos anteriores que não foram marcados."
                )

            usufructs = Usufruct.objects.filter(
                activity__acquisition_period__pk__in=acquisition_periods.filter(
                    start_date_acquisition__lte=self.acquisition_period.start_date_acquisition
                ).values("pk"),
                start_date__gte=self.start_date,
            ).exclude(
                status__in=[
                    USU_CANCELED,
                    USU_CHANGED,
                    USU_INTERRUPTED,
                    USU_SUSPENDED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                ]
            )
            if usufructs.exists():
                message = ""
                for usu in usufructs:
                    message += "%s%s" % ((", " if message else ""), usu)
                raise Exception(
                    "Fruição cronológica não foi seguida. O seu usufruto (%s) deve ser marcado depois de %s."
                    % (self, message)
                )

            usufructs = Usufruct.objects.filter(
                activity__acquisition_period__pk__in=acquisition_periods.filter(
                    start_date_acquisition__gte=self.acquisition_period.start_date_acquisition
                ).values("pk"),
                start_date__lte=self.start_date,
            ).exclude(
                status__in=[
                    USU_CANCELED,
                    USU_CHANGED,
                    USU_INTERRUPTED,
                    USU_SUSPENDED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                ]
            )
            if usufructs.exists():
                message = ""
                for usu in usufructs:
                    message += "%s%s" % ((", " if message else ""), usu)
                raise Exception(
                    "Fruição cronológica não foi seguida. O seu usufruto (%s) deve ser marcado antes de %s."
                    % (self, message)
                )
        return True

    def validate_start_and_end_date(self):
        if self.status != USU_SOLD and self.days == 0:
            if not (self.start_date and self.end_date):
                raise Exception("Data inicial e data final devem ser preenchidas")

            if self.start_date > self.end_date:
                raise Exception("Data final deve ser posterior à data inicial")

    def validate_start_end_date_book_scale(self):
        """Este método verifica se a marcação inicial está ocorrendo. Utilizando GroupPeriod.start_date_book e GroupPeriod.end_date_book.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        today = datetime.now().date()
        if not is_current_user_admin() and (
            self.from_scale
            and self.acquisition_period.group_period.end_date_book
            and self.acquisition_period.group_period.end_date_book < today
        ):
            raise Exception("Marcação finalizada.")
        if not is_current_user_admin() and (
            self.from_scale
            and self.acquisition_period.group_period.start_date_book > today
        ):
            raise Exception("Marcação não iniciada.")
        return True

    def validate_usufruct_amendment(self):
        """
        Este método verifica se o usufruto atual pode emendar com outros definidos na configuração.

        Returns:
            bool:
        Raise:
            Exception: Não pode pode ter emenda entre os usufrutos
        """
        excluded_usufructs_values = [
            usufruct_type.get("value")
            for usufruct_type in self.configuration.excluded_usufructs_amendment.values(
                "value"
            )
        ]

        excluded_usufructs = Usufruct.objects.filter(
            Q(activity__acquisition_period__employee=self.acquisition_period.employee)
            & Q(
                activity__acquisition_period__group_period__configuration__type_of_usufruct__in=excluded_usufructs_values
            )
        ).filter(
            status__in=[USU_AUTORIZED_CI, USU_ENJOYED, USU_ENJOYING, USU_HOMOLOGATED]
        )

        if excluded_usufructs:
            for usufruct in excluded_usufructs:
                dr = NewDateRange(usufruct.start_date, usufruct.end_date)
                _start_date = self.start_date + relativedelta(days=-1)
                _end_date = self.end_date + relativedelta(days=1)
                if dr.in_range(_start_date) or dr.in_range(_end_date):
                    raise Exception(
                        f"O usufruto({self}) não pode ser emendado com o {usufruct}"
                    )
        return True

    def validate_substitution(self):
        """Este método verifica se existem substituições vigentes, apenas no momento da marcação, no período informado. Utiliza classcode.validate_substitution.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.pk and self.acquisition_period.classcode:
            self.acquisition_period.classcode_instance().validate_substitution(
                self.start_date, self.validate_start_and_end_date
            )
        return True

    def conflicts_between_usufructs(self):
        # antigo .conflitos_usufruto_servidor
        """Retorna os conflitos entre parcelas de um mesmo servidor.

        Returns:
            conflicts (list): lista de conflitos
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        """ """
        usu_exclude = [usu.get("pk") for usu in self.activity.usufructsout.values("pk")]
        if self.pk:
            usu_exclude.append(self.pk)

        conflicts = []
        if self.start_date and self.end_date:
            usus = (
                Usufruct.objects.filter(
                    activity__acquisition_period=self.acquisition_period
                )
                .filter(
                    Q(start_date__lte=self.start_date)
                    & (Q(end_date__gte=self.start_date) | Q(end_date=None))
                )
                .exclude(
                    status__in=[
                        USU_CHANGED,
                        USU_SUSPENDED,
                        USU_INTERRUPTED,
                        USU_NOT_AUTHORIZED,
                        USU_SUBSTITUTE,
                        USU_CANCELED,
                        USU_SOLD,
                    ]
                )
                .exclude(pk__in=usu_exclude)
            )
            # dr = NewDateRange(self.start_date, self.end_date)
            # for usu in usus.exclude(pk__in=usu_exclude):
            for usu in usus:
                # dr_usu = NewDateRange(usu.start_date, usu.end_date)
                # if ((usu.start_date <= self.start_date and usu.end_date >= self.start_date) or (
                #         usu.start_date <= self.end_date and usu.end_date >= self.end_date)):
                # if dr_usu.intersect(dr).days > 0:
                conflicts.append(usu)
        return conflicts

    def correct_usufruct(self, usufruct, days_on_sale):
        """
            Método que realizar a correção de datas ou dias de usufrutos.
        Args:
            usufructs_in (list): usufrutos
            days_on_sale (int) inteiro
        """
        days = self.days
        self.start_date = usufruct["start_date"] if usufruct else None
        self.end_date = usufruct["end_date"] if usufruct else None
        self.days = usufruct["days"] if usufruct else days_on_sale
        self.pre_validate_usufruct(days_on_sale, days)
        self.save(validate_prevent=False if not days_on_sale else True)
        if self.departure:
            self.departure.alteracao = CANCELED
            self.departure.save()

    def pre_validate_usufruct(self, days_on_sale, days):
        self.validate_status_usufruct()
        self.validate_update_max_days(days_on_sale, days)
        # self.validate_status_departure()

    def validate_status_usufruct(self):
        """Este método valida o status do usufruto pode ser corrigido.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.status in [
            USU_NEW,
            USU_HOMOLOGATED,
            USU_ENJOYED,
            USU_SOLD,
            USU_ENJOYING,
        ]:
            raise Exception(
                f"Usufruto com status {self.get_status_display()} não pode ser corrigido."
            )
        return True

    def validate_update_max_days(self, days_on_sale, days):
        """Este método valida o saldo de usufruto para venda

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        activity = self.activity
        paid_days_cache = activity.configuration.max_days_sale - (
            self.activity.acquisition_period.paid_days - days
        )
        days_on_cache = self.activity.acquisition_period.days_not_booked_cache + days
        if days_on_sale:
            if days_on_sale > activity.configuration.max_days_sale:
                raise Exception(
                    """Quantidade informada para venda é superior ao permitido para o tipo de usufruto
                    (Máximo permitido %d dias)"""
                    % (activity.configuration.max_days_sale)
                )
            if days_on_sale > days_on_cache or days_on_sale > paid_days_cache:
                raise Exception(
                    "Quantidade de dias (%s) está superior a quantidade de Dias a vender (%s)"
                    % (
                        days_on_sale,
                        (
                            paid_days_cache
                            if paid_days_cache < days_on_cache
                            else days_on_cache
                        ),
                    )
                )
        return True

    def validate_status_departure(self):
        if not self.departure.estado in [SCHEDULED]:
            raise Exception(
                f"Somente usufruto com afastamento agendado pode ser corigido."
            )
        return True

    @classmethod
    def interrupt_if_enjoying_on_turnoff(cls, employee):
        usufructs = Usufruct.objects.filter(
            activity__acquisition_period__employee=employee,
            end_date__gte=employee.data_desligamento,
            start_date__lte=employee.data_desligamento - relativedelta(days=1),
            status=USU_ENJOYING,
        )
        for usufruct in usufructs:
            usufructs_in = [
                {
                    "start_date": usufruct.start_date,
                    "end_date": employee.data_desligamento - relativedelta(days=1),
                },
            ]
            usufruct.acquisition_period.interrupt(
                usufructs_in=usufructs_in, modifieds=[usufruct]
            )


class UsufructSell(Usufruct):

    class Meta:
        proxy = True

    def validate(self, validate_prevent=False):
        return True


class Activity(AuditTimestampModel):
    acquisition_period = models.ForeignKey(
        AcquisitionPeriod,
        on_delete=models.PROTECT,
        help_text="O período aquisitivo refente a que o servidor tem direito",
        verbose_name="Período aquisitivo",
        related_name="activities",
    )
    annotation = models.ForeignKey(
        AnotacaoGeral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dayoff_activities",
    )
    attachment = models.ForeignKey(
        "Attachment",
        on_delete=models.PROTECT,
        verbose_name="Anexo de publicação da ação",
        null=True,
        blank=True,
        related_name="dayoff_activities",
    )
    immediate_authorization_by = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        help_text="Chefe imediato que autorizou.",
        verbose_name="Autorizado por (chefe imediato)",
        related_name="dayoff_activity_immediateauthorizations",
        blank=True,
        null=True,
    )
    immediate_authorization_at = models.DateTimeField(
        help_text="Data de autorização pela chefia imediata",
        verbose_name="Data de autorização (chefia imediata)",
        blank=True,
        null=True,
    )
    mediate_authorization_by = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        help_text="Chefe mediato que autorizou.",
        verbose_name="Autorizado por (chefe mediato)",
        related_name="dayoff_activity_mediateauthorizations",
        blank=True,
        null=True,
    )
    mediate_authorization_at = models.DateTimeField(
        help_text="Data de autorização pela chefia mediata",
        verbose_name="Data de autorização (chefia mediata)",
        blank=True,
        null=True,
    )
    admin_authorization_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Usuário que realizou o procedimento como admin.",
        verbose_name="Admin",
        related_name="dayoff_activities",
        blank=True,
        null=True,
    )
    admin_authorization_at = models.DateTimeField(
        verbose_name="Data do procedimento", blank=True, null=True
    )
    homologation_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Usuário que realizou o procedimento como admin.",
        verbose_name="Admin",
        related_name="dayoff_activities_homologations",
        blank=True,
        null=True,
    )
    homologation_at = models.DateTimeField(
        verbose_name="Data do procedimento", blank=True, null=True
    )
    modifieds = models.ManyToManyField(
        Usufruct,
        help_text="Usufrutos alterados",
        verbose_name="Usufrutos alterados",
        related_name="activity_modifieds",
    )
    status = models.SmallIntegerField(
        default=ACT_ST_CREATED,
        help_text="Situação atual dessa atividade",
        verbose_name="Situação",
        choices=Choice.get_choices_for("dayoff", "ACTIVITY_STATUS_CHOICE"),
    )
    type_of_activity = models.SmallIntegerField(
        default=ACT_BOOK,
        verbose_name="Tipo",
        choices=Choice.get_choices_for("dayoff", "ACTIVITY_TYPE_CHOICE"),
    )
    justification = models.TextField(
        help_text="Justificativa para a alteração da parcela de ususfruto",
        verbose_name="Justificativa",
        null=True,
        blank=True,
    )
    days_in_cache = models.SmallIntegerField(
        default=0, null=True, blank=True, verbose_name="Cache de dias entraram"
    )
    days_out_cache = models.SmallIntegerField(
        default=0, null=True, blank=True, verbose_name="Cache de dias que saíram"
    )
    days_left_cache = models.SmallIntegerField(
        default=0, null=True, blank=True, verbose_name="Cache de dias que sobraram"
    )
    note = models.BooleanField(default=True, blank=True, verbose_name="Anotar?")
    authorized_immediate = models.BooleanField(
        null=True, blank=True, verbose_name="Autorização do chefe imediato"
    )
    authorized_mediate = models.BooleanField(
        null=True, blank=True, verbose_name="Autorização do chefe mediato"
    )
    authorized = models.BooleanField(null=True, blank=True, verbose_name="Autorizado")
    authorized_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Autorizado em"
    )
    homologated = models.BooleanField(
        default=False, blank=True, verbose_name="Homologado"
    )
    canceled = models.BooleanField(default=False, blank=True, verbose_name="Cancelado")
    scale_homologation = models.BooleanField(
        default=False,
        help_text="""Informar se ação homologou a escala""",
        verbose_name="Homologação da escala",
        blank=True,
    )

    class Meta:
        permissions = (
            ("can_homologate", "Pode homologar as Atividades"),
            ("can_authorize_mediate_chief", "Pode autorizar as Atividades"),
        )
        ordering = ("acquisition_period__start_date_acquisition", "created_at")

    AUDITABLE = {
        "fields": [
            "immediate_authorization_by_id",
            "mediate_authorization_by_id",
            "admin_authorization_by_id",
            "homologation_by_id",
            "immediate_authorization_at",
            "mediate_authorization_at",
            "admin_authorization_at",
            "homologation_at",
            "status",
            "days_left_cache",
            "authorized_immediate",
            "authorized_mediate",
            "authorized",
            "homologated",
            "canceled",
            "scale_homologation",
        ]
    }

    def __str__(self):
        if (
            self.acquisition_period.start_date_acquisition
            and self.acquisition_period.end_date_acquisition
        ):
            return "%s - %s - %s (%s/%s)" % (
                self.get_type_of_activity_display(),
                self.get_status_display(),
                self.acquisition_period.configuration.get_type_of_usufruct_display(),
                self.acquisition_period.start_date_acquisition.year,
                self.acquisition_period.end_date_acquisition.year,
            )

        return "{} - {} - {}".format(
            self.get_type_of_activity_display(),
            self.get_status_display(),
            self.acquisition_period.configuration.get_type_of_usufruct_display(),
        )

    def __init__(self, *args, **kwargs):
        self.usufructs_in = []
        self.usufructs_out = []
        self.substitutes = []
        self.days_on_sale = 0
        self.total_days = 0
        self.from_activity = None
        self.context = None
        self.usufruct_modifieds = []
        super().__init__(*args, **kwargs)

    @classmethod
    def create_activity(
        cls,
        acquisition_period=None,
        type_of_activity=ACT_BOOK,
        status=ACT_ST_CREATED,
        usufructs_in=[],
        usufructs_out=[],
        attachment=None,
        justification=None,
        scale_homologation=False,
        note=True,
        validate_prevent=False,
        validate_prevent_usufruct=False,
        context=None,
        days_on_sale=0,
        usufruct_modifieds=[],
        usufructs_out_pks=[],
    ):
        """Este método cria e persiste uma Activity a partir dos parâmetros informados. Adiciona informações aos campos usufructs_in, usufructs_out.

        Args:
            acquisition_period (AcquisitionPeriod): AcquisitionPeriod
            type_of_activity (int): type_of_activity, defautl ACT_BOOK
            status (int): status, defautl ACT_ST_CREATED
            usufructs_in (list): usufrutos que serão marcados
            usufructs_out (list): usufrutos que serão modificados
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            scale_homologation (bool): se a escala está sendo homologada
            note (bool): se esta ação deve anotar
            validate_prevent (bool): Evitar validação
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): ação
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        attachment = (
            Attachment.objects.get(pk=int(attachment))
            if type(attachment) in (int, str)
            else attachment
        )
        activity = cls(
            acquisition_period=acquisition_period,
            type_of_activity=type_of_activity,
            status=status,
            attachment=attachment,
            justification=justification,
            scale_homologation=scale_homologation,
            note=note,
        )
        activity.context = context
        Activity.set_usufructs_in(activity, usufructs_in)
        activity.set_usufructs_out(usufructs_out)
        activity.set_days_on_sale(days_on_sale)
        activity.set_usufructs_modifieds(usufruct_modifieds)
        activity.days_in_cache = activity.days_in
        activity.days_out_cache = activity.days_out

        activity.save(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
            note_prevent=True,
        )
        for modified in activity.usufructs_out:
            activity.modifieds.add(modified)

        return activity

    def set_usufructs_in(self, usufructs_in=[]):
        """Este método seta e atualiza usufructs_in adicionando o campo days.

        Args:
            usufructs_in (list): usufrutos que serão marcados
        """
        self.usufructs_in = usufructs_in
        for usu in self.usufructs_in:
            start_date = (
                DateUtils.str_to_date(usu.get("start_date"))
                if type(usu.get("start_date")) == str
                else usu.get("start_date")
            )
            end_date = (
                DateUtils.str_to_date(usu.get("end_date"))
                if type(usu.get("end_date")) == str
                else usu.get("end_date")
            )
            dr = NewDateRange(start_date, end_date)
            usu.update(
                {"days": dr.days, "start_date": start_date, "end_date": end_date}
            )

    def set_usufructs_out(self, usufructs_out=[]):
        """Este método seta o campo usufructs_out.

        Args:
            usufructs_out (list): usufrutos que serão marcados
        """
        self.usufructs_out_pks = usufructs_out
        if type(usufructs_out) != QuerySet:
            pks = []
            for usu in usufructs_out:
                if type(usu) == Usufruct:
                    pks.append(usu.pk)
                else:
                    pks.append(usu)
            self.usufructs_out = Usufruct.objects.filter(pk__in=pks)
        else:
            self.usufructs_out = usufructs_out

    def set_usufructs_modifieds(self, usufruct_modifieds):
        """Este método seta o campo usufruct_modifieds.

        Args:
            usufructs_out (list): usufrutos que serão marcados
        """
        for usu in usufruct_modifieds:
            self.usufruct_modifieds.append(usu.pk)

    def set_days_on_sale(self, days_on_sale=0):
        self.days_on_sale = days_on_sale

    @property
    def my_origin(self):
        instance = self
        if ActivityBook.objects.filter(pk=self.pk).exists():
            instance = ActivityBook.objects.get(pk=self.pk)
        elif ActivityChange.objects.filter(pk=self.pk).exists():
            instance = ActivityChange.objects.get(pk=self.pk)
        elif ActivityInterrupt.objects.filter(pk=self.pk).exists():
            instance = ActivityInterrupt.objects.get(pk=self.pk)
        elif ActivitySuspend.objects.filter(pk=self.pk).exists():
            instance = ActivitySuspend.objects.get(pk=self.pk)
        elif ActivityIndemnify.objects.filter(pk=self.pk).exists():
            instance = ActivityIndemnify.objects.get(pk=self.pk)
        elif ActivitySell.objects.filter(pk=self.pk).exists():
            instance = ActivitySell.objects.get(pk=self.pk)
        elif ActivityBookSell.objects.filter(pk=self.pk).exists():
            instance = ActivityBookSell.objects.get(pk=self.pk)
        elif ActivityCancel.objects.filter(pk=self.pk).exists():
            instance = ActivityCancel.objects.get(pk=self.pk)
        elif ActivityRetify.objects.filter(pk=self.pk).exists():
            instance = ActivityRetify.objects.get(pk=self.pk)
        elif ActivityRemaining.objects.filter(pk=self.pk).exists():
            instance = ActivityRemaining.objects.get(pk=self.pk)
        elif ActivityCorrect.objects.filter(pk=self.pk).exists():
            instance = ActivityCorrect.objects.get(pk=self.pk)
        return instance

    @property
    def usufructsin(self):
        """Esta propriedade retorna os usufrutos de entrada da ação.

        Returns:
            usufructs (list): usufrutos que serão marcados
        """
        # return self.usufructs.values() if self.pk else self.usufructs_in
        # TODO: VERIFICAR SE A MODIFICAÇÃO ABAIXO NÃO AFETOU NENHUMA IMPLEMENTAÇÃO, NUMA PRIMEIRA ANÁLISE NÃO AFETOU NADA POIS TODAS UTILIZAÇÕES ERAM APÓS TODOS USUFRUTOS ESTAREM EM .usufructs
        usus = []
        if self.pk:
            usus = self.usufructs.filter().values(
                "pk", "start_date", "end_date", "days"
            )

        if len(self.usufructs_in) > len(usus):
            usus = self.usufructs_in
        return usus

    @property
    def usufructsout(self):
        """Esta propriedade retorna os usufrutos de saída da ação.

        Returns:
            usufructs (list): usufrutos que serão alterados
        """
        return (
            self.modifieds.filter()
            if self.pk
            else Usufruct.objects.filter(pk__in=self.usufructs_out)
        )

    @property
    def configuration(self):
        return self.acquisition_period.configuration

    def system_can_authorize(self):
        """Este método verifica se o usuário athenas pode autorizar.
        Verifica se é o usuário athenas que está fazendo.
        Verifica se configuration.auto_authorization > 0.

        Returns:
            usufructs (list): usufrutos que serão marcados
        """
        return (
            is_current_user_system()
            and self.acquisition_period.check_auto_authorization()
        )

    def admin_can_authorize(self):
        """Este método verifica se o usuário é admin e autorizar.

        Returns:
            usufructs (list): usufrutos que serão marcados
        """
        return user_has_perm_authorize_admin()

    def save(self, *args, **kwargs):
        self.days_left_cache = self.days_left
        """ DO SOMETHING BEFORE VALIDATES """
        self.validate(
            validate_prevent=kwargs.get("validate_prevent", False),
            validate_prevent_usufruct=kwargs.get("validate_prevent_usufruct", False),
        )
        self.annotate(note_prevent=kwargs.get("note_prevent", False))
        kwargs = self._pop_before_save()

        super(Activity, self).save(*args, **kwargs)

    def _pop_before_save(self, **kwargs):
        if "validate_prevent" in kwargs:
            kwargs.pop("validate_prevent")

        if "validate_prevent_usufruct" in kwargs:
            kwargs.pop("validate_prevent_usufruct")

        if "note_prevent" in kwargs:
            kwargs.pop("note_prevent")

        return kwargs

    def delete(self, *args, **kargs):
        try:
            if self.annotation:
                self.annotation.delete()
        except Exception as err:
            log.exception(err)
        super(Activity, self).delete(*args, **kargs)

    @property
    def is_interruption_suspension_acquisitionperiod(self):
        """Esta propriedade verificará se houve ação de interrupção ou suspensão no AcquisitionPeriod.

        Returns:
            bool:
        """
        return (
            self.type_of_activity in (ACT_INTERRUPT, ACT_SUSPEND)
            or self.acquisition_period.activities.filter(
                type_of_activity__in=(ACT_INTERRUPT, ACT_SUSPEND)
            ).exists()
        )

    def divisions_usufruct_sum(self, usufructs_exclude=[]):
        """Este método retornará quantas divisões de usufrutos existem.

        Returns:
            int:
        """
        divisions_usufruct_sum = self.acquisition_period.divisions_usufruct_sum(
            usufructs_exclude=usufructs_exclude
        )
        if not self.pk:
            divisions_usufruct_sum += len(self.usufructsin)
        return divisions_usufruct_sum

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent:
            self.validate_can_create()
            self.validate_blocked()
            if self.employee:
                if self.employee.type_by_possession != "EST":
                    self.validate_max_division()

        if not validate_prevent or not validate_prevent_usufruct:
            self.validate_usufructs()

        return True

    def validate_can_create(self):
        """Esta validação verifica se quem tentando criar é o próprio servidor ou o admin.

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            not self.pk
            and not (is_current_user_admin() or is_current_user_system())
            and employee_from_user(get_current_user())
            != self.acquisition_period.employee
        ):
            raise Exception(
                f"Você não possui permissão para realizar atividades pelo servidor {self.acquisition_period.employee}."
            )
        return True

    def validate_update_activity(self):
        """Esta validação verifica se quem está tentando atualizar a atividade tem permissão.

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.pk and not (is_current_user_admin() or is_current_user_system()):
            raise Exception(
                f"Você não possui permissão para realizar atividades pelo servidor {self.acquisition_period.employee}."
            )
        return True

    # FRUICAO
    def validate_max_division(self):
        """Este método valida se existe configuração de quantidade máxima de divisões. Utilizando max_division e divisions_usufruct_sum.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        user_admin = is_current_user_admin() and self.context == "admin"
        max_division = self.configuration.max_division
        if user_admin and self.configuration.max_division_admin:
            max_division = self.configuration.max_division_admin

        if max_division and not self.is_interruption_suspension_acquisitionperiod:

            # divisions_usufruct_sum = self.divisions_usufruct_sum(usufructs_exclude=self.usufructsout)
            # if max_division and (divisions_usufruct_sum > max_division) and not (
            #     self.booked_days == self.acquisition_period.real_days
            # ):
            #     raise Exception('Quantidade máxima(%s) de divisões excedida.' % max_division)
            # if max_division and (max_division == divisions_usufruct_sum) and (self.booked_days < self.acquisition_period.real_days):
            #     raise Exception(
            #         'Quantidade máxima(%s) de divisões excedida. Todos os dias restantes (%s) devem entrar nesta marcação.' % (
            #             max_division, self.acquisition_period.real_days - self.booked_days))
            days_remaining = self.days_remaining
            # qtd_valid_division = self.acquisition_period.usufructs.filter(status__in=AcquisitionPeriod.status_usufruct_booked_days()).count() - self.usufructsout.count()
            qtd_valid_division = (
                self.acquisition_period.usufructs.filter(
                    status__in=AcquisitionPeriod.status_usufruct_booked_days()
                )
                .exclude(pk__in=(rs.get("pk", 0) for rs in self.usufructsin))
                .count()
                - self.usufructsout.count()
            )
            days_in = self.days_in
            qtd_available_division = max_division - qtd_valid_division
            qtd_usufructs_in = len(self.usufructsin)
            last_usufruct = qtd_usufructs_in == 1 and days_remaining == days_in
            if qtd_usufructs_in > qtd_available_division:
                if not last_usufruct and qtd_usufructs_in == 1:
                    raise Exception(
                        "Você deve marcar todos os %s dias restantes nessa parcela."
                        % (days_remaining)
                    )
                elif qtd_usufructs_in > 1 and days_in != days_remaining:
                    raise Exception(
                        "O número máximo de parcelas restantes é %d. "
                        % qtd_available_division
                    )
                elif qtd_usufructs_in > max_division:
                    raise Exception(
                        "O número máximo de parcelas restantes é %d. **"
                        % qtd_available_division
                    )
            elif (
                qtd_usufructs_in == qtd_available_division and days_in != days_remaining
            ):
                raise Exception(
                    "Você deve marcar todos os %s dias restantes nessa parcela."
                    % (days_remaining)
                )
        return True

    @deprecated
    def validate_block_usufruct_departures(self):
        """Este método checa se existe afastamento impedindo a criação do Usufruct.
        Utilizando Usufrut.validate_departure.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.acquisition_period.check_block_usufruct_departures:
            usus = []
            if self.pk:
                usus = self.usufructs.exclude(status=USU_CANCELED)
            for usu in usus:
                usu.validate_departure()
        return True

    def validate_usufructs(self):
        """Este método realiza todas as validações do Usufrut.
        Utilizando Usufrut.validate.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usus = []
        if self.pk:
            usus = self.usufructs.exclude(status=USU_CANCELED)
        for usu in usus:
            usu.my_origin.validate()
        return True

    def validate_admin_can_authorize(self):
        """Esta validação verifica se quem está tentando realizar ação é admin ou o sistema caso seja possível Configuration.auto_autorization.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.context == "admin":
            if self.authorized is not None and not (
                self.admin_can_authorize() or self.system_can_authorize()
            ):
                raise Exception("Você não possui permissão para autorizar.")
            if not self.from_activity and self.employee.is_immediate_chief(
                employee_from_user(self.admin_authorization_by)
            ):
                raise Exception("Você não pode autorizar pela interface admin.")
        return True

    def validate_can_homologate(self):
        """Esta validação verifica se quem está tentando realizar ação possui permissão.

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        valid = False
        if has_perm_homologate_admin():
            valid = True
        elif (
            self.acquisition_period.check_auto_homologation()
            and not self.configuration.mediate_authorization
            and self.immediate_authorization_by
            and self.homologation_by == self.immediate_authorization_by.user
        ):
            valid = True
        elif (
            self.acquisition_period.check_auto_homologation()
            and self.configuration.mediate_authorization
            and self.mediate_authorization_by
            and self.homologation_by == self.mediate_authorization_by.user
        ):
            valid = True
        elif has_perm_homologate():
            valid = True
        if not valid:
            raise Exception("Você não possui permissão para homologar.")
        return True

    def validate_authorized(self):
        """Esta validação verifica se a ação está autorizada.

        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.authorized:
            raise Exception("Ação não autorizada.")

    def validate_immediate_authorization(self):
        """Este método validate a partir da configuração se a autorização imediata é exigida.
        Utiliza mediate_authorization e immediate_authorization_by

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.context in ("admin", "immediate"):
            if self.old_fields.get("immediate_authorization_by_id", None):
                raise Exception(
                    "Já foi autorizado pelo chefe imediato %s"
                    % self.immediate_authorization_by
                )
            if (
                self.immediate_authorization_by
                and not self.employee.is_immediate_chief(
                    self.immediate_authorization_by
                )
            ):
                raise Exception(
                    "%s não é chefe imediato de %s"
                    % (self.immediate_authorization_by, self.employee)
                )
        return True

    def validate_mediate_authorization(self, target_status=None):
        """Este método valida a partir da configuração se a autorização mediata é exigida.
        Utiliza mediate_authorization e mediate_authorization_by

        Params:
            target_status(int): Activity target status
        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.context == "mediate":
            if self.old_fields.get("mediate_authorization_by_id", None):
                raise Exception(
                    "Já foi autorizado pelo chefe mediato %s"
                    % self.immediate_authorization_by
                )
            if (
                self.configuration.mediate_authorization
                and target_status == ACT_ST_AUTHORIZED_M
                and self.authorized_immediate is None
            ):
                raise Exception("É necessário autorização do chefe imediato.")
            if (
                self.configuration.mediate_authorization
                and self.mediate_authorization_by
                and not has_perm_mediate_chief(self.mediate_authorization_by.user)
            ):
                raise Exception("Chefe mediato não possui permissão para autorizar.")
            if (
                not self.configuration.mediate_authorization
                and self.mediate_authorization_by
            ):
                raise Exception("Não é necessário autorização do chefe mediato.")
            if (
                self.mediate_authorization_by
                and not self.employee.is_mediate_chief(self.mediate_authorization_by)
                and not has_perm_mediate_chief()
            ):
                raise Exception(
                    "%s não é chefe mediato de %s"
                    % (self.mediate_authorization_by, self.employee)
                )
        return True

    def validate_mediate_authorized(self):
        """Este método valida se o chefe mediato autorizou quando a Configuration.mediate_authorization exigir.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.mediate_authorization
            and self.status == ACT_ST_AUTHORIZED
        ):
            raise Exception("É necessário autorização do chefe mediato.")
        return True

    def validate_blocked(self):
        """Este método valida se o AcquisitionPeriod está bloqueado para o servidor.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.acquisition_period.blocked and not is_current_user_admin():
            raise Exception("Período aquisitivo bloqueado.")
        return True

    def validate_cancel(self):
        """Este método chama as validações aplicadas ao método undo.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        self.validate_can_cancel()
        # self.validate_cancel_last_activity()
        return True

    def validate_exclude(self):
        """Este método chama as validações aplicadas ao método de exclusão de usufrutos e atividades.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        self.validate_can_exclude()
        if self.type_of_activity != ACT_CORRECT:
            self.validate_exclude_last_activity()
        self.validate_exclude_already_payroll_usufructs()
        return True

    def validate_can_cancel(self):
        """Este método validate se a ação é possível.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not has_perm_cancel_admin():
            if self.type_of_activity not in (
                ACT_BOOK,
                ACT_CHANGE,
                ACT_SELL,
                ACT_BOOK_SELL,
            ):
                raise Exception(
                    "Não possui permissão para cancelar a atividade %s. Permitidas: MARCAÇÃO, ALTERAÇÃO e VENDA."
                    % self
                )
            elif self.status != ACT_ST_CREATED:
                raise Exception(
                    "Não possui permissão para cancelar a atividade %s. Atividade já está %s."
                    % (self, self.get_status_display())
                )
        return True

    def validate_can_exclude(self):
        """Este método validate se a ação é possível.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not has_perm_cancel_admin():
            if self.type_of_activity not in (
                ACT_BOOK,
                ACT_CHANGE,
                ACT_SELL,
                ACT_BOOK_SELL,
            ):
                raise Exception(
                    "Não possui permissão para excluir a atividade %s. Permitidas: MARCAÇÃO, ALTERAÇÃO e VENDA."
                    % self
                )
            elif self.status != ACT_ST_CREATED:
                raise Exception(
                    "Não possui permissão para excluir a atividade %s. Atividade já está %s."
                    % (self, self.get_status_display())
                )
        return True

    def validate_cancel_last_activity(self):
        if (
            self.acquisition_period.activities.filter(canceled=False).latest(
                "created_at"
            )
            != self
        ):
            raise Exception(
                "Cancelamento de (%s) não é permitido. Só é possível cancelar a última ação realizada!"
                % self
            )
        return True

    def validate_exclude_last_activity(self):
        if (
            self.acquisition_period.activities.filter()
            .exclude(type_of_activity=ACT_CORRECT)
            .latest("created_at")
            != self
        ):
            raise Exception(
                "Atenção!<br><br> Só é permitido excluir à atividade mais recente"
            )
        return True

    def validate_exclude_already_payroll_usufructs(self):
        """Verifica se algum usufruto a ser excluido já se encontra em uma folha para pagamento, estando em folha lança-se o erro."""
        if Payment.objects.filter(
            usufruct__in=list(self.usufructs.values_list("pk", flat=True))
        ).exists():
            raise Exception(
                "Um ou mais usufrutos/venda relacionado a essa atividade estão conectados com um lançamento na folha de pagamento. Por isso não é possível excluir"
            )

    def validate_usufruct_in(self):
        if not self.usufructs_in and not self.days_on_sale:
            raise Exception("Informe um novo usufruto.")

    def notify(self, notify_prevent=False):
        """Este método envia a notificação se notify_prevent for False."""
        if not notify_prevent:
            raise Exception("not implemented")

    def notify_authorize(self, notify_prevent=False):
        """Este método envia a notificação quando houver autorização se notify_prevent for False."""
        if self.authorized is not None and not notify_prevent:
            who = ""
            if self.immediate_authorization_by:
                who = "%s%s" % (
                    ("%s, " % who if who else ""),
                    self.immediate_authorization_by,
                )
            if self.mediate_authorization_by:
                who = "%s%s" % (
                    ("%s, " % who if who else ""),
                    self.mediate_authorization_by,
                )

            if (
                not self.immediate_authorization_by
                and not self.mediate_authorization_by
                and self.admin_authorization_by
            ):
                who = "%s" % self.admin_authorization_by

            decision = "foi %s" % ("deferida" if self.authorized else "indeferida")
            decision = "%s por %s" % (decision, who)
            notify(
                "DOF_AUTHORIZATION_NOT",
                self.acquisition_period.employee,
                self,
                type_of=self.configuration.get_type_of_usufruct_display(),
                notification_cfg="deferimento" if self.authorized else "indeferimento",
                type_of_activity=self.my_origin.get_type_of_activity_display().lower(),
                acquisition_period="%s" % self.acquisition_period.str_summary(),
                decision=decision,
            )

    def notify_homologated(self, notify_prevent=False):
        """Este método envia a notificação de homologação se notify_prevent for False."""
        if not notify_prevent:
            notify(
                "DOF_HOMOLOGATION_NOT",
                self.acquisition_period.employee,
                type_of=self.configuration.get_type_of_usufruct_display(),
                group="%s" % self.acquisition_period.group_period,
            )

    @classmethod
    def notify_fruition(cls, list_days=[]):
        """Este método envia a notificação sobre início de fruição."""
        date = datetime.now()
        dates = [date.date() + relativedelta(days=days) for days in list_days]
        dates_unicode = [
            DateUtils.date_to_str(date.date() + relativedelta(days=days))
            for days in list_days
        ]
        print(
            ">>> [%s] Iniciando notificacao de fruicao dayoff >>>>>>>>>>>>> %s"
            % (DateUtils.datetime_to_str(date), dates_unicode)
        )
        for usu in Usufruct.objects.filter(status=USU_HOMOLOGATED).filter(
            start_date__in=dates
        ):
            print("%s: %s" % ((usu.start_date - date.date()).days, usu))
            Notification.notify(
                "DOF_FRUITION_NOT",
                usu.employee,
                group=f"{DateUtils.date_to_str(usu.start_date)} à {DateUtils.date_to_str(usu.end_date)}",
                type_of=usu.acquisition_period.group_period.configuration.get_type_of_usufruct_display(),
                start_date=DateUtils.date_to_str(usu.start_date),
                days=(usu.start_date - date.date()).days,
            )
        print(
            ">>> [%s] Finalizando notificacao de fruicao de dayoff >>>>>>>>>>>>>"
            % (DateUtils.datetime_to_str(date))
        )

    def annotate(self, note_prevent=False):
        """Este método gera a anotação.

        Returns:
            annotate (AnotacaoGeral):
        """
        ANNOTATION_CLASS_TO_ACTIVITY_METHOD = {
            AnotacaoFerias: self._annotate_vacation,
            AnotacaoRecesso: self._annotate_default,
            AnotacaoFolgaAniversario: self._annotate_default,
            AnotacaoFolgaEleitoral: self._annotate_default,
            AnotacaoPlantao: self._annotate_default,
            AnotacaoFolgaCompensacao: self._annotate_default,
        }
        if not self.canceled and self.note and not note_prevent:
            self.annotation = ANNOTATION_CLASS_TO_ACTIVITY_METHOD.get(
                self.configuration.annotation_class, self._annotate_default
            )()
        return self.annotation

    def _annotate_default(self):
        """Este método gera a anotação.

        Returns:
            annotate (AnotacaoGeral):
        """
        if not self.annotation:
            annotation = self.configuration.annotation_class.manage_instance(
                servidor=self.employee,
                tipo_documento=(
                    Publication.get_tipo(self.attachment.publication)
                    if self.attachment
                    else 100
                ),
                publicacao=self.attachment.publication if self.attachment else None,
                data_portaria_inicio=self.annotation_start_date,
                texto=self.annotation_text(),
                resumo=self.annotation_summary(),
            )
            self.configuration.annotation_class.objects.filter(pk=annotation.pk).update(
                indireto=True
            )
            self.annotation = annotation
        else:
            annotation_class = self.annotation.my_origin.__class__
            if not annotation_class:
                annotation_class = self.configuration.annotation_class
            annotation = annotation_class.objects.get(pk=self.annotation.pk)
            annotation.publicacao = (
                self.attachment.publication if self.attachment else None
            )
            annotation.data_portaria_inicio = self.annotation_start_date
            annotation.texto = self.annotation_text()
            annotation.resumo = self.annotation_summary()
            annotation.servidor = self.employee
            annotation.tipo_documento = (
                Publication.get_tipo(self.attachment.publication)
                if self.attachment
                else 100
            )
            annotation.indireto = False
            annotation.save()
            self.annotation = annotation
        return self.annotation

    def _annotate_vacation(self):
        """Este método gera a anotação.

        Returns:
            annotate (AnotacaoGeral):
        """
        if not self.annotation:
            annotation = self.configuration.annotation_class.manage_instance(
                servidor=self.employee,
                tipo_documento=(
                    Publication.get_tipo(self.attachment.publication)
                    if self.attachment
                    else 100
                ),
                publicacao=self.attachment.publication if self.attachment else None,
                data_portaria_inicio=self.annotation_start_date,
                texto=self.annotation_text(),
                resumo=self.annotation_summary(),
                periodo="%s" % self.annotation_period,
                identificador="",
            )
            self.configuration.annotation_class.objects.filter(pk=annotation.pk).update(
                indireto=True
            )
            self.annotation = annotation
        else:
            annotation = self.configuration.annotation_class.objects.get(
                pk=self.annotation.pk
            )
            annotation.publicacao = (
                self.attachment.publication if self.attachment else None
            )
            annotation.data_portaria_inicio = self.annotation_start_date
            annotation.texto = self.annotation_text()
            annotation.resumo = self.annotation_summary()
            annotation.periodo = "%s" % self.annotation_period
            annotation.servidor = self.employee
            annotation.tipo_documento = (
                Publication.get_tipo(self.attachment.publication)
                if self.attachment
                else 100
            )
            annotation.indireto = False
            annotation.save()
        return annotation

    @property
    def annotation_start_date(self):
        """Esta propriedade retorna a data de início da anotação.

        Returns:
            datetatime.now().date (datetatime.date)
        """
        return datetime.now().date()

    @property
    def annotation_period(self):
        """Esta propriedade retorna o período em que ocorreu.

        Returns:
            str:
        """
        return self.acquisition_period.group_period

    def annotation_text(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            texto (str):
        """
        text = " texto da anotação %s" % self.__class__
        if self.homologated:
            text = (
                self._annotation_text_homologate()
                if not self.scale_homologation
                else self._annotation_text_homologate_scale()
            )
        elif self.authorized:
            text = self._annotation_text_authorized()
        return text

    def _annotation_text_homologate(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            str
        """
        text = ""
        change = ActivityChange.objects.filter(pk=self.pk)
        if change.exists():
            text = change.first().annotation_text()
        else:
            msg = Message.objects.get(mid="DOF_ANNOTATION_USU")
            text = msg.formated(
                {
                    "acqp_action": "HOMOLOGAR",
                    "type_of": self.configuration.get_type_of_usufruct_display(),
                    "usus": self.usufructs_display,
                    "group": "%s" % self.acquisition_period.group_period,
                    "homologation_date": DateUtils.datetime_to_str(datetime.now()),
                    "publication": (
                        ""
                        if not (self.attachment and self.attachment.publication)
                        else "conforme %s de %s"
                        % (
                            self.attachment.publication,
                            self.attachment.publication.data_vigencia.strftime(
                                "%d/%m/%Y"
                            ),
                        )
                    ),
                }
            )
        return text

    def _annotation_text_homologate_scale(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            str
        """
        msg = Message.objects.get(mid="DOF_ANNOTATION_HOMOLOGATE")
        return msg.formated(
            {
                "usus": self.usufructs_display,
                "group": "%s" % self.acquisition_period.group_period,
                "homologation_date": DateUtils.datetime_to_str(datetime.now()),
                "publication": (
                    ""
                    if not (self.attachment and self.attachment.publication)
                    else "<br />Conforme %s de %s"
                    % (
                        self.attachment.publication,
                        self.attachment.publication.data_vigencia.strftime("%d/%m/%Y"),
                    )
                ),
            }
        )

    def _annotation_text_authorized(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            str
        """
        msg = Message.objects.get(mid="DOF_ANNOTATION_USU")
        return msg.formated(
            {
                "acqp_action": "AUTORIZAR",
                "type_of": self.configuration.get_type_of_usufruct_display(),
                "usus": self.usufructs_display,
                "group": "%s" % self.acquisition_period.group_period,
                "homologation_date": DateUtils.datetime_to_str(datetime.now()),
                "publication": (
                    ""
                    if not (self.attachment and self.attachment.publication)
                    else "<br />Conforme %s n° %s/%s de %s"
                    % (
                        self.attachment.publication.get_tipo_display(),
                        self.attachment.publication.numero,
                        self.attachment.publication.ano,
                        self.attachment.publication.data_vigencia.strftime("%d/%m/%Y"),
                    )
                ),
            }
        )

    def annotation_summary(self):
        """Esta propriedade retorna o resumo da anotação.

        Returns:
            resumo (str)
        """
        text = " resumo da anotação %s" % self.__class__
        if self.homologated:
            text = "Homologa"
        elif self.authorized:
            text = "Autoriza"
        return f"{text} Usufruto de {self.acquisition_period.group_period}"

    @property
    def usufructs_display(self):
        """Esta propriedade retorna os usufrutos em representação para anotação e notificação.

        Returns:
            usufructs (str)
        """
        usufructs = ""
        for usu in self.usufructs.filter():
            if usu.start_date and usu.end_date:
                usufructs += "\n%s a %s (%s dias)" % (
                    DateUtils.date_to_str(usu.start_date),
                    DateUtils.date_to_str(usu.end_date),
                    usu.days,
                )
            else:
                usufructs += "\n%s dias" % (usu.days)

        return usufructs

    @property
    def modifieds_display(self):
        """Esta propriedade retorna os usufrutos em representação para anotação e notificação.

        Returns:
            modifieds (str)
        """
        modifieds = ""
        for usu in self.modifieds.filter():
            modifieds += "\n%s a %s (%s dias)" % (
                DateUtils.date_to_str(usu.start_date),
                DateUtils.date_to_str(usu.end_date),
                usu.days,
            )
        return modifieds

    @property
    def booked_usufructs_display(self):
        usufructs = ""
        for usu in self.usufructs.filter():
            if usu.start_date and usu.end_date:
                usufructs += "\n%s a %s (%s dias)" % (
                    DateUtils.date_to_str(usu.start_date),
                    DateUtils.date_to_str(usu.end_date),
                    usu.days,
                )
            else:
                usufructs += "\n%s dias" % (usu.days)

        return usufructs

    @property
    def modifieds_usufructs_display(self):
        modifieds = ""
        for usu in self.modifieds.filter():
            if usu.start_date:
                modifieds += "\n%s a %s (%s dias)" % (
                    DateUtils.date_to_str(usu.start_date),
                    DateUtils.date_to_str(usu.end_date),
                    usu.days,
                )
        return modifieds

    @property
    def employee(self):
        """Esta propriedade retorna o servidor do AcquisitionPeriod.

        Returns:
            employee (Employee)
        """
        return self.acquisition_period.employee

    def transit_status(
        self, action, target, validate_prevent=False, validate_prevent_usufruct=False
    ):
        """Este método realiza transição para target caso a action seja valida.
            Utiliza action_check para verificar se é possível a transição.

        Args:
            activity (str): Ação
            target (int): Estado alvo
            validate_prevent (bool): validate_prevent para o save
            validate_prevent_usufruct (bool): Evita a validação de usufrutos

        Returns:
            bool:
        """
        action_check(action, self.status, ACTIVITY_SM, ACTIVITY_STATUS_CHOICE)
        self.status = target
        self.save(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    @property
    def classcode(self):
        """Esta propriedade retorna o classcode definido para a configuração.

        Returns:
            ClassCode: ClassCode or None
        """
        class_code = None
        if self.automated:
            class_code = self.configuration.class_code
            # if class_code is None:
            #     class_code = ClassCode.objects.get(slug='dayoff-base')
        return class_code

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        activity=None,
        transit_status_modifieds=True,
    ):
        """Método fazer da atividade.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            activity (Activity): Activity
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
        Returns:
            activity (Activity): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        raise Exception("Por favor utiliza uma ação válida.")

    def cancel(self, *args, **kwargs):
        """Método desfazer padrão para todas atividade.

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        action_check("cancelar", self.status, ACTIVITY_SM, ACTIVITY_STATUS_CHOICE)

        self.validate_cancel()

        with transaction.atomic():
            self._cancel_usufructs()
            self._homologate_modifieds()
            if self.annotation:
                self.annotation.delete()
            self.annotation = None
            self.canceled = True
            self.authorized = True
            self.authorized_at = datetime.now()
            self.homologated = True

            # self.acquisition_period.transit_status('cancelar', ACQP_PROGRESS)
            self.acquisition_period.update_status(ACQP_PROGRESS)
            self.transit_status("cancelar", ACT_ST_CANCELED, validate_prevent=True)

        return self

    def set_usufruct_modifieds(self, modifieds):
        """
            Método que seta os usufrutos modificados anteriomente.
        Args:
            modifieds (list): usufrutos

        """
        if modifieds:
            for modified in modifieds:
                self.usufruct_modifieds = self.usufruct_modifieds + list(
                    modified.activity.modifieds.values_list("pk", flat=True)
                )
        set(self.usufruct_modifieds)

    def exclude(self, *args, **kwargs):
        """Método para excluir um registro criado acidentalmente.

        Raise:
            Exception: raise exception quando houver exceção em validações
        """
        # action_check('cancelar', self.status, ACTIVITY_SM, ACTIVITY_STATUS_CHOICE)

        self.validate_exclude()

        with transaction.atomic():
            self._exclude_usufructs()
            self._homologate_modifieds()
            # self.acquisition_period.transit_status('cancelar', ACQP_PROGRESS)
            if self.type_of_activity == ACT_CANCEL:
                self.set_usufruct_modifieds(self.modifieds.filter())
            self.acquisition_period.update_status(ACQP_PROGRESS)
            self.delete()

        return self

    # @classmethod
    # def correct(cls,usufructs_in=[],modifieds=[],days_on_sale=None):
    #     """
    #         Método que realizar a correção de datas ou dias de usufrutos.
    #     Args:
    #         usufructs_in (list): usufrutos
    #         modifieds (list) usufrutos
    #         days_on_sale (int) inteiro

    #     Returns:
    #         activity (Activity): uma instância de ação válida

    #     """
    #     usu = Usufruct.objects.get(pk=modifieds[0])
    #     activity = usu.activity.my_origin
    #     usufruct = None
    #     if not days_on_sale:
    #         activity.set_usufructs_in(usufructs_in)
    #         usufruct = activity.usufructs_in[0]
    #     with transaction.atomic():
    #         usu.correct_usufruct(usufruct,days_on_sale)
    #         activity.acquisition_period.update_status(ACQP_PROGRESS)
    #         activity.transit_status('corrigir',ACT_ST_HOMOLOGATED, validate_prevent=False if not days_on_sale else True)
    #     return activity

    @property
    def days_out(self):
        """Esta propriedade retorna quantos dias estão sendo alterados.

        Returns:
            days (int): quantidade de dias alterados
        """
        return (
            self.usufructsout.aggregate(modified_days=models.Sum("days")).get(
                "modified_days"
            )
            or 0
        )

    @property
    def days_in(self):
        """Esta propriedade retorna quantos dias estão sendo marcados.

        Returns:
            days (int): quantidade de dias marcados
        """
        days = 0
        for usu in self.usufructsin:
            days += usu.get("days")
        return days

    @property
    def days_left(self):
        """Esta propriedade retorna quantos sobraram na ação. Retorna a diferença entre days_out e days_in.

        Returns:
            days (int): quantidade de dias marcados
        """
        days = self.days_out - self.days_in
        return days if days > 0 else 0

    @property
    def booked_days(self):
        """Esta propriedade retorna:
        * dias marcados(acquisition_period.booked_days) + estão marcando(usufructs) - estão alterando(usufructsout).
        Utiliza self.acquisition_period.booked_days, days_in e days_out.

        Returns:
            days (int):
        """
        booked_days = self.acquisition_period.booked_days
        if self.usufructsout.filter(
            status__in=AcquisitionPeriod.status_usufruct_booked_days()
        ).exists():
            booked_days -= self.days_out
        if not self.pk:
            booked_days += self.days_in
        elif (
            self.pk
            and not self.usufructs.filter(
                status__in=AcquisitionPeriod.status_usufruct_booked_days()
            ).exists()
        ):
            booked_days += self.days_in

        return booked_days

    @property
    def days_remaining(self):
        """Esta propriedade os dias disponíveis no processo. Levando em conta o que está entrando e saindo com o que já foi marcado.

        Returns:
            days (int):
        """
        days_remaining = self.acquisition_period.real_days
        booked_days = self.acquisition_period.booked_days
        usus = Usufruct.objects.none()
        if self.pk:
            usus = self.usufructs.filter(
                status__in=AcquisitionPeriod.status_usufruct_booked_days()
            )

        if usus.exists():
            booked_days -= self.days_in
        elif not self.usufructsout.filter(
            status__in=AcquisitionPeriod.status_usufruct_booked_days()
        ).exists():
            booked_days += self.days_out
        else:
            booked_days -= self.days_out
        days_remaining -= booked_days
        return days_remaining

    def _set_immediate_authorization(self, immediate_authorization):
        if self.context == "admin" and immediate_authorization:
            self.immediate_authorization_by = immediate_authorization
            self.immediate_authorization_at = datetime.now()
        elif self.context == "immediate":
            self.immediate_authorization_by = employee_from_user(get_current_user())
            self.immediate_authorization_at = datetime.now()

    def _set_mediate_authorization(self, mediate_authorization):
        if self.context == "admin" and mediate_authorization:
            self.mediate_authorization_by = mediate_authorization
            self.mediate_authorization_at = datetime.now()
        elif self.context == "admin" and (
            self.configuration.authorizer_employee
            or self.configuration.authorizer_member
        ):
            self.mediate_authorization_by = self.configuration.authorizer_employee
            if self.employee.membro:
                self.mediate_authorization_by = self.configuration.authorizer_member
            self.mediate_authorization_at = datetime.now()
        elif self.context == "mediate":
            self.mediate_authorization_by = employee_from_user(get_current_user())
            self.mediate_authorization_at = datetime.now()

    def _set_admin_authorization(self):
        """Este método define admin_authorization_by. Utiliza user_has_perm_authorize_admin e system_can_authorize."""
        check_admin = self.admin_can_authorize() and self.context == "admin"
        if check_admin or self.system_can_authorize:
            self.admin_authorization_by = get_current_user()
            self.admin_authorization_at = datetime.now()

    def _set_homologation(self):
        self.homologation_by = get_current_user()
        if (
            self.context == "admin"
            and is_current_user_system()
            and self.acquisition_period.check_auto_homologation()
        ):
            self.homologation_by = User.objects.get(username="athenas")
        self.homologation_at = datetime.now()

    def _homologate_modifieds(self, validate_prevent=False):
        """Este método leva os usufrutos modificados de volta para homologado.

        Args:
            validate_prevent (bool): evitar validação, default é False
            validate_prevent_usufruct (bool): Evita a validação de usufrutos

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.modifieds.filter():
            usu.status = USU_HOMOLOGATED
            usu.save(validate_prevent=validate_prevent)
            usu.refresh_from_db()
            usu.update_status(validate_prevent=validate_prevent)

    def _cancel_usufructs(self, validate_prevent=True):
        """Este método leva os usufrutos marcados para cancelado.

        Args:
            validate_prevent (bool): evitar validação, default é False
        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.usufructs.filter():
            usu.transit_status(
                "cancelar", USU_CANCELED, validate_prevent=validate_prevent
            )

    def _exclude_usufructs(self, validate_prevent=True):
        """Este método leva os usufrutos marcados para excluidos.

        Args:
            validate_prevent (bool): evitar validação, default é False
        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.usufructs.filter():
            usu.delete()

    def authorize_and_homologate(
        self,
        authorize=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        transit_status_modifieds=True,
        validate_prevent_usufruct=False,
        attachment=None,
        context=None,
    ):
        """Este método tenta autorizar e homologar. Utiliza .authorize e homologate.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            attachment (Attachment): anexo informado
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        self.context = context if context else self.context
        with transaction.atomic():
            self.authorize(
                authorize=authorize,
                attachment=attachment,
                note=note,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                transit_status_modifieds=transit_status_modifieds,
                validate_prevent_usufruct=validate_prevent_usufruct,
            )
            if self.authorized:
                self.homologate(
                    attachment=attachment,
                    note=note,
                    transit_status_modifieds=transit_status_modifieds,
                    validate_prevent_usufruct=validate_prevent_usufruct,
                )
        return self

    def _define_authorize_context_admin(self, authorize=None, context=None):
        """Esté método atribui 'admin' ao .context e authorize=True caso seja o admin fazendo e ele possua permissão. Ou seja o system."""
        if authorize is None and (
            (self.admin_can_authorize() and context == "admin")
            or self.system_can_authorize()
        ):
            authorize = True
            context = "admin"
        return authorize, context

    def authorize(
        self,
        authorize=None,
        attachment=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        transit_status_modifieds=True,
        validate_prevent_usufruct=False,
        context=None,
    ):
        """Este método autoriza a Activity.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "autorizar",
            self.acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )

        authorize, self.context = self._define_authorize_context_admin(
            authorize, context if context else self.context
        )

        if authorize is not None:
            self.attachment = attachment if attachment else self.attachment
            self.note = note

            act, target_status = (
                ("autorizar", ACT_ST_AUTHORIZED)
                if authorize
                else ("desautorizar", ACT_ST_NOT_AUTHORIZED)
            )

            self._set_immediate_authorization(immediate_authorization)
            self._set_mediate_authorization(mediate_authorization)
            self._set_admin_authorization()

            if (
                self.immediate_authorization_by
                or self.admin_can_authorize()
                or self.system_can_authorize()
            ):
                self.authorized_immediate = authorize
            if (
                self.mediate_authorization_by
                or self.admin_can_authorize()
                or self.system_can_authorize()
            ):
                self.authorized_mediate = authorize

            if self.configuration.mediate_authorization:
                if self.authorized_mediate is not None:
                    target_status = (
                        ACT_ST_AUTHORIZED_M
                        if target_status == ACT_ST_AUTHORIZED
                        else target_status
                    )
                    self.authorized = (
                        self.authorized_immediate and self.authorized_mediate
                    )
                    self.authorized_at = datetime.now()
            elif self.authorized_immediate is not None:
                self.authorized = authorize
                self.authorized_at = datetime.now()

            self.validate_immediate_authorization()
            self.validate_mediate_authorization(target_status)
            self.validate_admin_can_authorize()

            with transaction.atomic():
                if self.authorized is not None:
                    self._authorize_usufructs(
                        authorize=self.authorized,
                        validate_prevent_usufruct=validate_prevent_usufruct,
                    )
                    if transit_status_modifieds:
                        self._authorize_modifieds(authorize=self.authorized)
                self.transit_status(
                    act,
                    target_status,
                    validate_prevent_usufruct=validate_prevent_usufruct,
                )

            if self.authorized is not None:
                self.notify_authorize()

        return self

    def _authorize_usufructs(self, authorize=False, validate_prevent_usufruct=False):
        """Este método modifica o estado dos usufructs para autorizados/não autorizados.

        Args:
            authorize (bool): Booleano indicando se está autorizado ou não.
            validate_prevent_usufruct (bool): Evita a validação de usufrutos

        """
        act = "autorizar" if authorize else "desautorizar"
        tgt = USU_AUTORIZED_CI if authorize else USU_NOT_AUTHORIZED
        for usu in self.usufructs.filter():
            usu.my_origin.transit_status(
                act, tgt, validate_prevent=validate_prevent_usufruct
            )

    def _authorize_modifieds(self, authorize=False):
        """Este método modifica os modifieds para alterado/homologado do processo de autorização.

        Args:
            authorize (bool): Booleano indicando se está autorizado ou não.
        """
        act = "alterar" if authorize else "desautorizar"
        tgt = USU_CHANGED if authorize else USU_HOMOLOGATED
        for usu in self.modifieds.filter():
            usu.transit_status(
                act, tgt, validate_prevent=True if tgt == USU_CHANGED else False
            )

    def homologate(
        self,
        homologate=False,
        attachment=None,
        note=True,
        transit_status_modifieds=True,
        scale_homologation=False,
        validate_prevent_usufruct=False,
        context=None,
    ):
        """Este método homologa a Activity.

        Args:
            homologate (bool): homologar
            attachment (Attachment): anexo informado
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            scale_homologation (bool): indica se é homologação de escala
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check("homologar", self.status, ACTIVITY_SM, ACTIVITY_STATUS_CHOICE)

        authorize, self.context = self._define_authorize_context_admin(
            context=context if context else self.context
        )

        if homologate is False and self.acquisition_period.check_auto_homologation():
            homologate = True

        self.homologated = homologate

        if self.authorized and self.homologated:
            self._set_homologation()
            self.attachment = attachment if attachment else self.attachment
            self.note = note
            self.scale_homologation = scale_homologation

            self.validate_authorized()
            self.validate_mediate_authorized()
            self.validate_can_homologate()

            self._homologate_usufructs(
                scale_homologation, validate_prevent_usufruct=True
            )

            with transaction.atomic():
                self.transit_status(
                    "homologar",
                    ACT_ST_HOMOLOGATED,
                    validate_prevent=True,
                    validate_prevent_usufruct=validate_prevent_usufruct,
                )
            self.notify_homologated()
        return self

    def _homologate_usufructs(
        self, scale_homologation, validate_prevent_usufruct=False
    ):
        """Este método homologa os usufrutos.

        Args:
            scale_homologation (bool): homologação pela escala
            validate_prevent_usufruct (bool): prevenção de validação de usufruto
        Raise:
            Exception: raise exception caso ocorra problemas na homologação
        """
        for usu in self.usufructs.filter():
            if scale_homologation:
                usu.from_scale = scale_homologation
            # if status not in (USU_ENJOYING, USU_ENJOYED, USU_SOLD):
            #     status = USU_HOMOLOGATED
            status = usu._define_status(USU_HOMOLOGATED)[0]
            usu.transit_status(
                "homologar", status, validate_prevent=validate_prevent_usufruct
            )

    def update_activity(self, attachment=None):
        """Este método é responsável por atualizar Activity.

        Args:
            attachment (Attachment)
        """
        activity = self.my_origin
        activity.validate_update_activity()
        activity.update_attachment(attachment=attachment)
        activity.update_annotation()
        activity.acquisition_period.update_annotation()

    def update_attachment(self, attachment=None):
        """Este método atualiza o Attachment.

        Args:
            attachment (Attachment)
        """
        Activity.objects.filter(pk=self.pk).update(attachment=attachment)
        self.refresh_from_db()

    def update_annotation(self):
        """Este método atualiza a anotação."""
        annotation_old = self.annotation
        self.annotate()
        if self.annotation != annotation_old:
            Activity.objects.filter(pk=self.pk).update(annotation=self.annotation)

    def get_payroll_reference(self):
        today = datetime.now().date()
        folhas = [
            int(x[0])
            for x in FolhaTipo.objects.filter(Q(principal=True), ativo=True)
            .values_list("pk")
            .order_by("pk")
        ]
        return (
            Folha.objects.filter(tipo_folha__in=folhas, dt_corte__gte=today)
            .order_by("-dt_corte")
            .first()
        )

    def next_payroll(self, payroll):
        return (
            Folha.objects.filter(folha_anterior=payroll).order_by("-dt_corte").first()
        )

    def set_payment_for_regular_vacation(
        self, usufructs, usufruct_ref, payroll, nextmonth
    ):
        today = datetime.now().date()
        usufruct_ref.payment_installments = (
            usufruct_ref.payment_installments
            if usufruct_ref.payment_installments
            else 1
        )
        periodo = get_object_or_none(
            Periodo, mes=usufruct_ref.created_at.month, ano=usufruct_ref.created_at.year
        )
        paid_usufruct = False
        if isinstance(self.usufructs_out, QuerySet):
            paid_usufruct = (
                True
                if Payment.objects.filter(
                    usufruct__in=Usufruct.objects.filter(
                        activity__in=self.usufructs_out.values_list(
                            "activity", flat=True
                        )
                    )
                ).exists()
                else False
            )

        usufruto_anterior = self.modifieds.first() if self.modifieds.exists() else None
        existe_pagamento = False
        if usufruto_anterior:
            existe_pagamento = usufruto_anterior.ctrl_payments.filter(
                payroll_ctrl_status=PAYMENT_FINALIZED
            ).exists()

        data_futura = (
            usufruct_ref.start_date.month > usufruct_ref.created_at.date().month
            and usufruct_ref.start_date.year >= usufruct_ref.created_at.date().year
            or (
                usufruct_ref.start_date.year > usufruct_ref.created_at.date().year
                and usufruct_ref.start_date.month < usufruct_ref.created_at.date().month
            )
        )

        if self.type_of_activity == ACT_SUSPEND and existe_pagamento:
            usufruct_ref.payment_month = None
            usufruct_ref.payment_year = None
            usufruct_ref.save_base()
        elif self.type_of_activity == ACT_RECTIFY and existe_pagamento and data_futura:
            set_pagamento_usufruto_retificado_suspensao(usufruct_ref, existe_pagamento)
        elif (
            self.type_of_activity in [ACT_RECTIFY, ACT_SUSPEND]
            and not existe_pagamento
            and periodo
            and periodo.data_corte_ferias
        ):
            set_pagamento_usufruto_retificado_suspensao(
                usufruct_ref, existe_pagamento, periodo, usufruto_anterior
            )
        elif self.type_of_activity in [ACT_RECTIFY, ACT_CHANGE] and paid_usufruct:
            for usufruct in usufructs:
                usufruct.payment_month = (
                    usufruct.payment_month if usufruct.payment_month else None
                )
                usufruct.payment_year = (
                    usufruct.payment_year if usufruct.payment_year else None
                )
        elif payroll and usufruct_ref.start_date <= nextmonth.date():
            year = payroll.dt_pagamento.year
            month = payroll.dt_pagamento.month

            usufruct_ref.payment_year = year
            usufruct_ref.payment_month = month
            usufruct_ref.save_base()
        elif data_futura:
            set_pagamento_usufruto_futuro(usufruct_ref)
        elif periodo and periodo.data_corte_ferias:
            set_pagamento_de_competencia_baseado_em_periodo(periodo, usufruct_ref)
        elif (
            usufruct_ref.start_date.month <= today.month
            and usufruct_ref.start_date.year <= today.year
        ):
            if usufruct_ref.start_date.month == 12:
                month = 1
                year = usufruct_ref.start_date.year + 1
            else:
                month = usufruct_ref.start_date.month + 1
                year = usufruct_ref.start_date.year

            usufruct_ref.payment_year = year
            usufruct_ref.payment_month = month
            usufruct_ref.save_base()

        elif (
            usufruct_ref.start_date.month == today.month + 1
            and usufruct_ref.start_date.year == today.year
        ):
            month = usufruct_ref.start_date.month
            year = usufruct_ref.start_date.year
            usufruct_ref.payment_year = year
            usufruct_ref.payment_month = month
            usufruct_ref.save_base()

        else:
            if usufruct_ref.start_date.month == 1:
                month = 12
                year = usufruct_ref.start_date.year - 1
            else:
                month = usufruct_ref.start_date.month - 1
                year = usufruct_ref.start_date.year

            usufruct_ref.payment_year = year
            usufruct_ref.payment_month = month
            usufruct_ref.save_base()

        for usufruct in usufructs:
            if usufruct.start_date == None:
                usufruct.payment_installments = (
                    usufruct.payment_installments
                    if usufruct.payment_installments
                    else 1
                )
                if payroll and usufruct_ref.start_date < nextmonth.date():
                    usufruct.payment_year = payroll.dt_pagamento.year
                    usufruct.payment_month = payroll.dt_pagamento.month
                elif not payroll and usufruct_ref.start_date < nextmonth.date():
                    usufruct.payment_year = nextmonth.date().year
                    usufruct.payment_month = nextmonth.date().month
                else:
                    usufruct.payment_year = usufruct_ref.start_date.year
                    usufruct.payment_month = usufruct_ref.start_date.month
                usufruct.save_base()

    def set_payment_for_individual_vacation(
        self, usufructs, usufruct_ref, payroll, nextmonth
    ):
        paid_usufruct = False
        if isinstance(self.usufructs_out, QuerySet):
            paid_usufruct = (
                True
                if Payment.objects.filter(
                    usufruct__in=Usufruct.objects.filter(
                        activity__in=self.usufructs_out.values_list(
                            "activity", flat=True
                        )
                    )
                ).exists()
                else False
            )
        for usufruct in usufructs:
            usufruct.payment_installments = (
                usufruct.payment_installments if usufruct.payment_installments else 1
            )
            if usufruct.start_date:
                if self.type_of_activity in [ACT_RECTIFY, ACT_CHANGE] and paid_usufruct:
                    for usufruct in usufructs:
                        usufruct.payment_month = (
                            usufruct.payment_month if usufruct.payment_month else None
                        )
                        usufruct.payment_year = (
                            usufruct.payment_year if usufruct.payment_year else None
                        )
                elif (
                    usufruct.start_date.month <= nextmonth.month
                    and usufruct.start_date.year <= nextmonth.year
                ):
                    if payroll:
                        usufruct.payment_year = payroll.dt_pagamento.year
                        usufruct.payment_month = payroll.dt_pagamento.month
                    else:
                        usufruct.payment_year = nextmonth.year
                        usufruct.payment_month = nextmonth.month

                else:
                    if usufruct_ref.start_date.month == 1:
                        usufruct.payment_month = 12
                        usufruct.payment_year = usufruct.start_date.year - 1
                    else:
                        usufruct.payment_month = usufruct.start_date.month - 1
                        usufruct.payment_year = usufruct.start_date.year
                usufruct.save_base()
            else:
                if payroll and usufruct_ref.start_date < nextmonth.date():
                    usufruct.payment_year = payroll.dt_pagamento.year
                    usufruct.payment_month = payroll.dt_pagamento.month
                elif not payroll and usufruct_ref.start_date < nextmonth.date():
                    usufruct.payment_year = nextmonth.date().year
                    usufruct.payment_month = nextmonth.date().month
                else:
                    usufruct.payment_year = usufruct_ref.start_date.year
                    usufruct.payment_month = usufruct_ref.start_date.month - 1
            usufruct.save_base()

    def set_payment_competence(self, first_save):
        """Função responsável por incluir a competência de pagamento automático"""
        usufructs = Usufruct.objects.filter(activity=self.id)
        usufruct_ref = (
            usufructs.filter(start_date__isnull=False).order_by("end_date").first()
        )
        today = datetime.now().date()
        nextmonth = datetime(today.year, today.month, 1) + relativedelta(months=1)
        payroll = self.get_payroll_reference()
        sub_type_of_usufruct = (
            self.acquisition_period.group_period.configuration.sub_type_of_usufruct
        )
        general_rule_sub_types_usufruct_list = [
            FORENSIC_RECESS,
            BIRTHDAY_BREAK,
            ELECTORAL_SLACK,
            ONCALL_BONUS_SERVERS,
            COMP_CLERARANCE_SERVERS,
            COMP_CLEARANCE_MEMBERS,
            COMP_VACATION_MEMBERS,
            PREMIUM_LICENSE,
            INTERNS_RECESS,
            SUBSTITUTE_PROMOTER_CONTEST,
            INTERNSHIP_COMPETITION,
            BLOOD_DONATION_USUFRUCT,
        ]
        if usufruct_ref:
            payment_link = Payment.objects.filter(usufruct=usufruct_ref).exists()
            if sub_type_of_usufruct == REGULAR_VACATIONS and usufruct_ref.status in [
                USU_NEW
            ]:
                self.set_payment_for_regular_vacation(
                    usufructs, usufruct_ref, payroll, nextmonth
                )

            if sub_type_of_usufruct == INDIVIDUAL_VACATION and usufruct_ref.status in [
                USU_NEW
            ]:
                self.set_payment_for_individual_vacation(
                    usufructs, usufruct_ref, payroll, nextmonth
                )

            # if not payment_link and sub_type_of_usufruct in [INDIVIDUAL_VACATION, REGULAR_VACATIONS] and usufruct_ref.status in [USU_CHANGING]:
            #     for usufruct in usufructs:
            #         usufruct.payment_year = None
            #         usufruct.payment_month = None
            #         usufruct.payment_installments = None
            #         usufruct.save_base()

            if sub_type_of_usufruct in general_rule_sub_types_usufruct_list:
                for usufruct in usufructs:
                    if sub_type_of_usufruct is PREMIUM_LICENSE:
                        usufruct.payment_installments = (
                            usufruct.payment_installments
                            if usufruct.payment_installments
                            else 1
                        )
                        if payroll:
                            usufruct.payment_year = payroll.dt_pagamento.year
                            usufruct.payment_month = payroll.dt_pagamento.month
                        else:
                            if usufruct_ref.start_date < nextmonth.date():
                                usufruct.payment_year = nextmonth.date().year
                                usufruct.payment_month = nextmonth.date().month
                            else:
                                usufruct.payment_year = usufruct_ref.start_date.year
                                usufruct.payment_month = usufruct_ref.start_date.month
                    else:
                        if not usufruct.start_date:
                            usufruct.payment_installments = (
                                usufruct.payment_installments
                                if usufruct.payment_installments
                                else 1
                            )
                            if usufruct_ref.start_date < nextmonth.date():
                                if payroll:
                                    usufruct.payment_year = payroll.dt_pagamento.year
                                    usufruct.payment_month = payroll.dt_pagamento.month
                                else:
                                    usufruct.payment_year = nextmonth.date().year
                                    usufruct.payment_month = nextmonth.date().month
                            else:
                                usufruct.payment_year = usufruct_ref.start_date.year
                                usufruct.payment_month = usufruct_ref.start_date.month

                    usufruct.save_base()

        else:  # Atividades que só tem usufruto de venda
            if first_save:
                usufruct_ref = usufructs.order_by("-start_date").first()
                if (
                    usufruct_ref
                    and sub_type_of_usufruct in general_rule_sub_types_usufruct_list
                ):
                    for usufruct in usufructs:
                        if payroll:
                            usufruct.payment_year = payroll.dt_pagamento.year
                            usufruct.payment_month = payroll.dt_pagamento.month
                        else:
                            usufruct.payment_year = nextmonth.date().year
                            usufruct.payment_month = nextmonth.date().month
                        usufruct.payment_installments = (
                            usufruct.payment_installments
                            if usufruct.payment_installments
                            else 1
                        )
                        usufruct.save_base()

                if (
                    payroll
                    and usufruct_ref
                    and self.acquisition_period.group_period.configuration.type_of_usufruct
                    == CONF_DUTTY
                ):

                    usufruct_ref.payment_year = payroll.dt_pagamento.year
                    usufruct_ref.payment_month = payroll.dt_pagamento.month
                    if not usufruct_ref.payment_installments:
                        usufruct_ref.payment_installments = 1
                    usufruct_ref.save_base()

    @classmethod
    def cancel_if_changing_status_on_turnoff(cls, employee):
        activities = Activity.objects.filter(
            Q(acquisition_period__employee=employee)
            & Q(usufructs__end_date__gte=employee.data_desligamento)
            & Q(usufructs__status=USU_CHANGING)
        )
        for activity in activities:
            activity.my_origin.cancel(context="admin")


class ActivityBookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_BOOK)


class ActivityBook(Activity):
    objects = ActivityBookManager()

    class Meta:
        proxy = True

    def notify(self, notify_prevent=False):
        """Este método envia a notificação se notify_prevent for False."""
        if not notify_prevent:
            self.notify_call_authorization()

    def notify_call_authorization(self, notify_prevent=False):
        """Este método envia a notificação solicitando autorização se notify_prevent for False."""
        if not notify_prevent and self.authorized is None:
            if self.acquisition_period.employee.chefe_imediato:
                notify(
                    "DOF_AUTHORIZATION_CALL_NOT",
                    self.acquisition_period.employee.chefe_imediato,
                    self,
                    employee=self.acquisition_period.employee,
                    type_of="%s" % self.configuration.get_type_of_usufruct_display(),
                )
            else:
                log.info(
                    "O servidor %s não possui chefe imediato!"
                    % self.acquisition_period.employee
                )
                notify(
                    "RH_SERVIDOR_CHEFE_IMEDIATO",
                    self.acquisition_period.employee,
                    self,
                    servidor=self.acquisition_period.employee,
                )

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent:
            self.validate_booked_days()
            self.validate_usufructs_in()
        self.validate_candidate_usufructs_in()
        return super(ActivityBook, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_booked_days(self):
        # antigo . validate_pasu_menor_dias_adquiridos, validate_provisioned_days
        """Valida se a quantidade de dias marcada está dentro da quantidade permitida.
        Utiliza self.booked_days e self.acquisition_period.real_days.

        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.booked_days > self.acquisition_period.real_days:
            raise Exception(
                "Quantidade de dias marcados (%s) está superior a quantidade de dias adquiridos (%s)."
                % (
                    self.booked_days,
                    self.acquisition_period.real_days
                    - self.acquisition_period.days_enjoyed,
                )
            )
        return True

    def validate_candidate_usufructs_in(self):
        """Valida se existe conflito de dias entre os usufrutos de entrada.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for c1 in self.usufructsin:
            for c2 in self.usufructsin:
                days = (
                    NewDateRange(c1.get("start_date"), c1.get("end_date"))
                    .intersect(NewDateRange(c2.get("start_date"), c2.get("end_date")))
                    .days
                )
                if c1 != c2 and days > 0:
                    raise Exception(
                        "Parcela %s - %s conflitou %s dias com %s - %s."
                        % (
                            c1.get("start_date"),
                            c1.get("end_date"),
                            days,
                            c2.get("start_date"),
                            c2.get("end_date"),
                        )
                    )
        return True

    def validate_usufructs_in(self):
        """Valida se existe usufruto marcado quando for book ou sell.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.type_of_activity in (ACT_BOOK, ACT_BOOK_SELL)
            and not len(self.usufructsin)
            and not self.days_on_sale
        ):
            raise Exception("Informe um período de fruição ou venda.")
        return True

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=False,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
        validate_prevent_usufruct=True,
    ):
        """Método fazer da ação MARCAR.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar, default False pois apenas marcação não anota nada
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityBook): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "marcar", acquisition_period.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE
        )

        activity = None
        with transaction.atomic():
            activity = ActivityBook.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_BOOK,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                context=context,
                validate_prevent=validate_prevent_usufruct,
                validate_prevent_usufruct=validate_prevent_usufruct,
            )

            activity._book_usufructs(
                validate_prevent_usufruct=validate_prevent_usufruct
            )
            activity.acquisition_period.save(validate_prevent=validate_prevent_usufruct)
            activity.save(
                validate_prevent=validate_prevent_usufruct,
            )

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize,
                note=True,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=validate_prevent_usufruct,
            )
            activity.notify()

        return activity

    def _book_usufructs(self, notify=True, validate_prevent_usufruct=False):
        """Método utiliza _book_usufruct para marcar os usufrutos de entrada.

        Args:
            notify (datetime.date): notify, default é True
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        qtd_parcelas = get_max_parcel_number(self.usufructs_in)
        for usu in self.usufructs_in:
            self._book_usufruct(
                usu.get("start_date"),
                usu.get("end_date"),
                notify=notify,
                validate_prevent=validate_prevent_usufruct,
                numero_parcela=usu.get("parcel_number"),
                qtd_parcelas=qtd_parcelas,
            )
        return True

    def _book_usufruct(
        self,
        start_date,
        end_date,
        notify=True,
        validate_prevent=False,
        numero_parcela=None,
        qtd_parcelas=None,
    ):
        """Método cria os usufrutos e realiza suas validações. Também Valida o AcquisitionPeriod através de validate.

        Args:
            start_date (datetime.date): start_date
            end_date (datetime.date): end_date
            notify (datetime.date): notify, default é True
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usu = Usufruct.create(
            self,
            start_date,
            end_date,
            validate_prevent,
            numero_parcela,
            payment_installments=qtd_parcelas,
        )
        usu.save(validate_prevent=validate_prevent)
        return True


class ActivityChangeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_CHANGE)


class ActivityChange(ActivityBook):
    objects = ActivityChangeManager()

    class Meta:
        proxy = True

    def annotation_text(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            str
        """
        modifieds = self.modifieds_display
        usufructs = self.usufructs_display

        doc = "solicitação online (via sistema Athenas) n° %s de %s" % (
            self.pk,
            DateUtils.date_to_str(self.created_at),
        )
        if self.attachment and self.attachment.publication:
            doc = "%s de %s" % (
                self.attachment.publication,
                DateUtils.date_to_str(self.attachment.publication.data_vigencia),
            )

        message = Message.objects.get(mid="DOF_ANNOTATION_CHANGE")
        if self.days_left > 0:
            usufructs = "%s %s" % (
                usufructs,
                (
                    "%s%s dias para época oportuna"
                    % ("e " if usufructs else "", self.days_left)
                ),
            )
            message = Message.objects.get(mid="DOF_ANNOTATION_CHANGE_ATHENAS")
        if self.justification:
            doc = "\n%s conforme %s" % (self.justification, doc)

        return message.formated(
            {
                "type_of": self.configuration.get_type_of_usufruct_display(),
                "group": "%s" % self.acquisition_period.group_period,
                "doc": doc.capitalize(),
                "usus": usufructs,
                "modifieds": modifieds,
            }
        )

    def annotation_summary(self):
        """
        Esta propriedade retorna o resumo da anotação.

        :return: str
        """
        return f"Altera Usufruto de {self.acquisition_period.group_period}"

    def notify(self, notify_prevent=False):
        """Este método envia a notificação se notify_prevent for False."""
        if not notify_prevent:
            if self.authorized is None:
                super(ActivityChange, self).notify()
            else:
                self.notify_authorize()

    def notify_authorize(self, notify_prevent=False):
        """Este método envia a notificação quando houver autorização se notify_prevent for False."""
        if self.authorized is not None and not notify_prevent:
            usufructs = self.usufructs_display
            message = f"{self.modifieds_display}"
            if usufructs:
                message = f"{message} para {usufructs}"
            if self.days_left > 0:
                _buff = f"E {self.days_left} dias para época oportuna."
                message = f"{message}. {_buff}"
            if self.justification:
                message = f"{message} {self.justification}."

            notify(
                "DOF_AUTHORIZATION_CHANGE_NOT",
                self.acquisition_period.employee,
                self,
                type_of=self.configuration.get_type_of_usufruct_display(),
                notification_cfg="deferimento" if self.authorized else "indeferimento",
                usus=message,
                decision="deferido" if self.authorized else "indeferido",
            )

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent:
            self.validate_modifieds()
            log.debug(self)
            self.validate_modifieds_quantity()
        return super(ActivityChange, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_modifieds(self, valid_status=[]):
        """Este verifica se os usufrutos podem ser alterados.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not valid_status:
            valid_status = [
                USU_HOMOLOGATED,
            ]
        modifieds = self.usufructsout.exclude(status__in=valid_status)
        if (
            modifieds.exists()
            and not self.usufructsout.filter(
                pk__in=modifieds.values("pk"),
                status__in=[USU_INTERRUPTED, USU_CHANGING, USU_CHANGED, USU_SUSPENDED],
            ).exists()
        ):
            buff = ""
            for st in valid_status:
                buff += "%s%s" % (", " if buff else "", USUFRUCT_STATUS_CHOICE.get(st))
            raise Exception("Estados válidos para os usufrutos alterados: %s." % buff)
        return True

    def validate_modifieds_quantity(self):
        """Este verifica se existe usufrutos enviados para alteração.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.usufructsout.exists():
            raise Exception("Deve-se escolher ao menos 1 usufruto para alterar.")
        return True

    # def validate_installment_amount(self, pasu_new=[], exclude_pasus=[]):
    #     # TODO: IMPLEMENTAR validate_installment_amount, já está implementado em outras validações
    #     qtd_dias_alterados = 0
    #     for excl in self.usufrutos.filter(pk__in=exclude_pasus):
    #         qtd_dias_alterados += excl.dias

    #     days_remaining = self.quantidade_dias - \
    #         (self.dias_marcados - qtd_dias_alterados) - self.paid_days
    #     qtd_pasu_valido = self.usufrutos.filter(
    #         estado__in=[PASU_NOVO, PASU_AUTORIZADO_CI, PASU_HOMOLOGADO,
    #                     PASU_EMALTERACAO, PASU_FRUINDO, PASU_FRUIDO, PASU_INTERROMPIDO]
    #     ).count() - len(exclude_pasus)
    #     qtd_pasu_disponivel = self.periodo_aquisitivo.configuracao.max_divisoes - qtd_pasu_valido
    #     ultima_parcela = len(pasu_new) == 1 and qtd_dias_restante == NewDateRange(
    #         pasu_new[0].get('data_inicio'), pasu_new[0].get('data_fim')).days
    #     if qtd_pasu_disponivel < len(pasu_new):
    #         if not ultima_parcela and len(pasu_new) == 1:
    #             raise FeriasError(
    #                 'Você deve marcar todos os %s dias restantes nessa parcela.' % (qtd_dias_restante))
    #         elif len(pasu_new) > 1:
    #             raise FeriasError(
    #                 'O número máximo de parcelas restantes é %d.' % qtd_pasu_disponivel)
    #     elif qtd_pasu_valido >= self.periodo_aquisitivo.configuracao.max_divisoes and self.interrompido and len(pasu_new) > 1:
    #         raise FeriasError(
    #             'Após interrupção é necessário marcar o restante numa parecela.' % self.periodo_aquisitivo.configuracao.max_divisoes)

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        transit_status_modifieds=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Método fazer da ação ALTERAR.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityChange): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "alterar",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )
        activity = None

        with transaction.atomic():
            activity = ActivityChange.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_CHANGE,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=False,
                context=context,
            )
            activity._transit_status_modifieds(validate_prevent=True)
            activity._book_usufructs()
            activity._transit_status_usufructs()

            activity.acquisition_period.validate()

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize,
                note=True,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )

            activity.acquisition_period.save(validate_prevent=True)

            activity.save(validate_prevent_usufruct=True)
            activity.notify()

        return activity

    def _transit_status_usufructs(
        self, action="alterar", status=USU_SUBSTITUTE, validate_prevent=False
    ):
        """Este método leva os usufrutos de entrada para action e status informados. Por padrão action='alterar' e status=USU_SUBSTITUTE.

        Args:
            activity (str): ação que será realiza no usufruto, default é alterar
            status (int): status que será aplicado ao usufruto, default é USU_SUBSTITUTE
            validate_prevent (bool): evitar validação, default é False
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.usufructs.filter():
            usu.transit_status(action, status, validate_prevent=validate_prevent)

    def _transit_status_modifieds(
        self, action="alterar", status=USU_CHANGING, validate_prevent=False
    ):
        """Este método leva os usufrutos modificados para action e status informados.  Por padrão action='alterar' e status=USU_CHANGING.

        Args:
            activity (str): ação que será realiza no usufruto, default é alterar
            status (int): status que será aplicado ao usufruto, default é USU_CHANGING
            validate_prevent (bool): evitar validação, default é False
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.modifieds.filter():
            usu.transit_status(action, status, validate_prevent=validate_prevent)


class ActivityInterruptManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_INTERRUPT)


class ActivityInterrupt(ActivityChange):
    objects = ActivityInterruptManager()

    MESSAGE_MID = "DOF_ANNOTATION_INTERRUPT"

    class Meta:
        proxy = True

    def annotation_text(self):
        """Esta propriedade retorna o texto da anotação.

        Returns:
            str
        """
        modified = self.modifieds.first()

        doc = ""
        date_doc = ""
        if self.attachment and self.attachment.publication:
            doc = "%s" % self.attachment.publication
            date_doc = DateUtils.date_to_str(self.attachment.publication.data_expedicao)

        msg = Message.objects.get(mid=self.MESSAGE_MID)
        return msg.formated(
            {
                "type_of": self.configuration.get_type_of_usufruct_display(),
                "date": DateUtils.date_to_str(self.from_date),
                "start_date": DateUtils.date_to_str(modified.start_date),
                "end_date": DateUtils.date_to_str(modified.end_date),
                "days": modified.days,
                "group": "%s" % self.acquisition_period.group_period,
                "doc": doc,
                "date_doc": date_doc,
                "usus": self.usufructs_display,
                "days_diff": self.days_out - self.days_in,
            }
        )

    def annotation_summary(self):
        """Esta propriedade retorna o resumo da anotação.

        Returns:
            resumo (str)
        """
        return f"Interrompe Usufruto de {self.acquisition_period.group_period}"

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent:
            self.validate_days_quantity()
            self.validate_modifieds_exceeded()
            self.validate_usufructs_quantity()
            self.validate_usufruct_interval()
        return super(ActivityInterrupt, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_days_quantity(self):
        """Este método valida se a quantidade de dias agendados é maior que a quantidade de dias modificados.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.days_in > self.days_out:
            raise Exception(
                "Quantidade de dias agendados(%s) não pode ser maior que dias interrompidos(%s)."
                % (self.days_in, self.days_out)
            )
        return True

    def validate_modifieds_exceeded(self):
        """Este método verifica se a quantidade de usufrutos foi excedida. Apenas 1 de cada vez é possível.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.usufructsout.count() > 1:
            raise Exception(
                "É possível %s apenas 1 usufruto por vez."
                % self.get_type_of_activity_display()
            )
        return True

    def validate_usufructs_quantity(self):
        """Este método valida a quantidade de usufrutos que está sendo informada. É necessário ao menos 1 usufruto do período de interrupção.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if len(self.usufructsin) == 0:
            raise Exception(
                "É necessário informar ao menos 1 usufruto indicando o périodo interrompido."
            )
        return True

    def validate_usufruct_interval(self):
        """Este método valida se ao menos 1 usufruto marcado está dentro do intervalo do usufruto interrompido.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.days_in > self.days_out:
            raise Exception(
                "Quantidade de dias agendados não pode ser maior que dias interrompidos."
            )
        return True

    def validate_modifieds(
        self, valid_status=[USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED]
    ):
        """Este verifica se os usufrutos podem ser alterados.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        return super(ActivityInterrupt, self).validate_modifieds(
            valid_status=valid_status
        )

    @property
    def from_date(self):
        """Esta propriedade retorna a data a partir de quando será o retorno.

        Returns:
            datetime.date
        """
        return self.usufructs.first().end_date + relativedelta(days=1)

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        transit_status_modifieds=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Método fazer da ação INTERROMPER.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityInterrupt): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "interromper",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )
        activity = None
        with transaction.atomic():
            activity = ActivityInterrupt.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_INTERRUPT,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                context="admin",
            )
            activity._transit_status_modifieds(
                action="interromper", status=USU_INTERRUPTED, validate_prevent=True
            )
            activity._book_usufructs()

            activity.acquisition_period.validate()
            activity._transit_acquisition_period(action="interromper")

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize,
                note=note,
                transit_status_modifieds=False,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )

            activity.notify()
        return activity

    def _transit_acquisition_period(
        self, action=None, status=None, update_usufructs=True, validate_prevent=False
    ):
        status = self.acquisition_period.status if not status else status
        if self.acquisition_period.check_enjoyed:
            status = ACQP_FINISHED
        if action == "suspender":
            self.acquisition_period.end_date_fruition = None
        self.acquisition_period.transit_status(
            action, status, validate_prevent=validate_prevent
        )


class ActivitySuspendManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_SUSPEND)


class ActivitySuspend(ActivityInterrupt):
    objects = ActivitySuspendManager()

    MESSAGE_MID = "DOF_ANNOTATION_SUSPEND"

    class Meta:
        proxy = True

    def set_usufructs_in(self, usufructs_in=[]):
        """Este método seta e atualiza usufructs_in adicionando o campo days.

        Args:
            usufructs_in (list): usufrutos que serão marcados
        """
        self.usufructs_in = usufructs_in
        for usu in self.usufructs_in:
            start_date = (
                DateUtils.str_to_date(usu.get("start_date"))
                if type(usu.get("start_date")) == str
                else usu.get("start_date")
            )
            end_date = (
                DateUtils.str_to_date(usu.get("end_date"))
                if type(usu.get("end_date")) == str
                else usu.get("end_date")
            )
            try:
                if start_date >= end_date:
                    self.usufructs_in.remove(usu)
                else:
                    dr = NewDateRange(start_date, end_date)
                    usu.update(
                        {
                            "days": dr.days,
                            "start_date": start_date,
                            "end_date": end_date,
                        }
                    )

            except:
                raise Exception("Período de suspensão inválido.")

    def annotation_summary(self):
        """Esta propriedade retorna o resumo da anotação.

        Returns:
            resumo (str)
        """
        return f"Suspende Usufruto de {self.acquisition_period.group_period}"

    @property
    def from_date(self):
        """Esta propriedade retorna a data a partir de quando será o retorno.

        Returns:
            datetime.date
        """
        return self.modifieds.first().start_date

    def validate_usufructs_quantity(self):
        """Este método valida a quantidade de usufrutos que está sendo informada. É necessário ao menos 1 usufruto do período de interrupção.
        NÃO REQUERIDO PARA SUSPENSÃO.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        return True

    def validate_usufruct_interval(self):
        """Este método valida se ao menos 1 usufruto marcado está dentro do intervalo do usufruto interrompido.
        NÃO REQUERIDO PARA SUSPENSÃO.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        return True

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        transit_status_modifieds=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Método fazer da ação SUSPENDER.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivitySuspend): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "suspender",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )
        activity = None

        with transaction.atomic():
            activity = ActivitySuspend.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_SUSPEND,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                context="admin",
            )

            activity._transit_status_modifieds(
                action="suspender", status=USU_SUSPENDED, validate_prevent=True
            )
            activity._book_usufructs()

            activity.acquisition_period.validate()
            activity._transit_acquisition_period(
                action="suspender", status=ACQP_PROGRESS
            )

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize,
                note=note,
                transit_status_modifieds=False,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )

            activity.notify()
        return activity


class ActivityIndemnifyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_INDEMNIFY)


class ActivityIndemnify(Activity):
    objects = ActivityIndemnifyManager()

    class Meta:
        proxy = True


class ActivitySellManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_SELL)


class ActivitySell(Activity):
    objects = ActivitySellManager()

    class Meta:
        proxy = True

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent and self.days_on_sale:
            self.validate_allow_sell()
            self.validate_min_days_sale()
            self.validate_max_days_sale()
            self.validate_days_on_sale()
            self.validate_months_exercise_sale()

        return super().validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_allow_sell(self):
        """Este método valida se existe configuração max_days_sale é False, não permite vender.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.configuration.max_days_sale:
            raise Exception("Não é permitido vender.")
        return True

    def validate_min_days_sale(self):
        """Este método valida se existe configuração para quantidade mínima de dias para vender. Utilizando min_days_sale e days_on_sale.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.min_days_sale
            and self.configuration.min_days_sale > self.days_on_sale
        ):
            raise Exception(
                "Quantidade mínima(%s) excedida." % self.configuration.min_days_sale
            )

        return True

    def validate_max_days_sale(self):
        """Este método valida se existe configuração para quantidade máxima de dias para vender. Utilizando max_days_sale e days_on_sale.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.configuration.max_days_sale and self.configuration.max_days_sale < (
            self.days_on_sale + self.acquisition_period.paid_days
        ):
            # raise Exception('Quantidade máxima %d excedida. Vendendo %d. Total vendido %d.' % (
            #     self.configuration.max_days_sale,
            #     self.days_on_sale,
            #     self.acquisition_period.paid_days
            # ))
            raise Exception(
                """Quantidade informada para venda é superior ao permitido para o tipo de usufruto
                (Máximo permitido %d dias)"""
                % (self.configuration.max_days_sale)
            )
        return True

    def validate_days_on_sale(self):
        # antigo . validate_pasu_menor_dias_adquiridos, validate_provisioned_days
        """Valida se a quantidade de dias marcada está dentro da quantidade permitida.

        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.acquisition_period.days_to_enjoy < self.days_on_sale:
            raise Exception(
                "Quantidade de dias (%s) está superior a quantidade de Dias a usufruir (%s)"
                % (self.days_on_sale, self.acquisition_period.days_to_enjoy)
            )
        return True

    def validate_months_exercise_sale(self):
        """Este método valida se existe configuração para indicar quantidade de meses para vender.
        Utilizando months_exercise_sale e employee_exercise_months.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if (
            self.configuration.months_exercise_sale
            and self.configuration.months_exercise_sale
            > self.acquisition_period.employee_exercise_months
        ):
            raise Exception(
                "Servidor ainda não completou a quantidade(%s) mínima de meses em exercício para vender."
                % self.configuration.months_exercise_sale
            )
        return True

    def validate_max_division(self):
        return True

    def authorize(
        self,
        authorize=None,
        attachment=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
        transit_status_modifieds=True,
        validate_prevent_usufruct=False,
        context=None,
    ):
        """Este método autoriza a Activity.

        Args:
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (Attachment): anexo informado
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "autorizar",
            self.acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )

        authorize, self.context = self._define_authorize_context_admin(
            authorize, context if context else self.context
        )

        if authorize:
            self.attachment = attachment if attachment else self.attachment
            self.note = note

            act, target_status = ("vender", ACT_ST_SOLD)

            self.authorized = authorize
            self.authorized_at = datetime.now()

            with transaction.atomic():
                if self.authorized is not None:
                    self._authorize_usufructs(
                        authorize=self.authorize,
                        validate_prevent_usufruct=validate_prevent_usufruct,
                    )
                self.transit_status(
                    act,
                    target_status,
                    validate_prevent_usufruct=validate_prevent_usufruct,
                )

        return authorize

    def _book_usufruct(self, days):
        """Método cria os usufrutos e realiza suas validações. Também Valida o AcquisitionPeriod através de validate.

        Args:
            start_date (datetime.date): start_date
            end_date (datetime.date): end_date
            notify (datetime.date): notify, default é True
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """

        usu = UsufructSell.create(self, days=days)
        usu.save()

        return True

    def _create_sell_usufruct(self):
        pass

    def _change_usufructs_before_sell(self):
        if (
            self.acquisition_period.days_to_enjoy
            >= self.days_on_sale
            >= self.acquisition_period.days_not_booked
        ):
            usufructs_available = (
                Usufruct.objects.filter(
                    activity__acquisition_period=self.acquisition_period,
                    status__in=[
                        USU_NEW,
                        USU_AUTORIZED_CI,
                        USU_HOMOLOGATED,
                        USU_CHANGING,
                    ],
                )
                .exclude(activity__type_of_activity__in=[ACT_INDEMNIFY, ACT_SELL])
                .order_by("start_date")
            )

            needed_usufructs = []
            needed_days = self.acquisition_period.days_not_booked
            for usu in usufructs_available:
                needed_days += usu.days
                needed_usufructs.append(usu)
                if self.days_on_sale <= needed_days:
                    break
            if needed_usufructs:
                self.acquisition_period.change(modifieds=needed_usufructs)

    @classmethod
    def do(
        cls,
        days,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=False,
        context=None,
    ):
        """Método fazer da ação VENDER.

        Args:
            days: quantidade de dias para venda
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar, default False pois apenas marcação não anota nada
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityBook): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # TODO Verificar qual a melhor forma de fazer esse pass para o caso da migração
        if context != "migrate":
            action_check(
                "vender",
                acquisition_period.status,
                AP_SM,
                ACQUISITION_PERIOD_STATUS_CHOICE,
            )

        activity = None
        with transaction.atomic():
            activity = ActivitySell.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_SELL,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                days_on_sale=days,
                context=context,
            )

            if activity.configuration.sell_booked_days:
                activity._change_usufructs_before_sell()

            activity._book_usufruct(days)
            activity.acquisition_period.save()
            activity.save(validate_prevent=True, validate_prevent_usufruct=True)

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize, note=True, validate_prevent_usufruct=True
            )

        return activity


class ActivityBookSellManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_BOOK_SELL)


class ActivityBookSell(ActivityBook, ActivitySell):
    objects = ActivityBookSellManager()

    class Meta:
        proxy = True

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        return super().validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def _book_usufruct_sell(self, days):
        """Método cria os usufrutos e realiza suas validações. Também Valida o AcquisitionPeriod através de validate.

        Args:
            days (int): days
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usu = UsufructSell.create(self, days=days)
        usu.save()

        return True

    def _create_sell_usufruct(self):
        pass

    @classmethod
    def do(
        cls,
        days=None,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=False,
        context=None,
    ):
        """Método fazer da ação MARCAR & VENDER.

        Args:
            days: quantidade de dias para venda
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar, default False pois apenas marcação não anota nada
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityBookSell): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # TODO Verificar qual a melhor forma de fazer esse pass para o caso da migração
        if context != "migrate":
            action_check(
                "vender",
                acquisition_period.status,
                AP_SM,
                ACQUISITION_PERIOD_STATUS_CHOICE,
            )

        action_check(
            "marcar", acquisition_period.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE
        )

        activity = None
        with transaction.atomic():
            activity = ActivityBookSell.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_BOOK_SELL,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                days_on_sale=days,
                context=context,
            )

            if (activity.configuration.sell_booked_days and days) or (
                context == "admin" and days
            ):
                # activity._change_usufructs_before_sell()
                activity._book_usufruct_sell(days)

            activity._book_usufructs()
            activity.acquisition_period.save()
            activity.save(validate_prevent=True, validate_prevent_usufruct=True)

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize, note=True, validate_prevent_usufruct=True
            )

        return activity


class ActivityCancelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_CANCEL)


class ActivityCancel(Activity):
    objects = ActivityCancelManager()

    MESSAGE_MID = "DOF_ANNOTATION_CANCEL"

    class Meta:
        proxy = True

    def annotation_summary(self):
        """Esta propriedade retorna o resumo da anotação.

        Returns:
            resumo (str)
        """
        return f"Cancelar Usufruto de {self.acquisition_period.group_period}"

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent:
            self.validate_status_usufruct()
            self.validate_status_usufruct_modifieds()
            self.validate_can_cancel()
            self.validate_scheduled_payment()

        return super().validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_status_usufruct(self):
        """
            Validar se o usufruto pode ser cancelado
        Returns:
            bool (True/False)
        """
        if self.usufructs_out[0].status not in [
            USU_NEW,
            USU_HOMOLOGATED,
            USU_SOLD,
            USU_ENJOYED,
            USU_ENJOYING,
        ]:
            raise Exception(
                f"Usufruto com status {self.usufructs_out[0].get_status_display()} não pode ser cancelado."
            )
        return True

    def validate_status_usufruct_modifieds(self):
        """
            Validar se os usufrutos modificados podem ser cancelados
        Returns:
            bool (True/False)
        """
        for usufruct in self.usufructs_out[0].activity.modifieds.filter():
            if usufruct.status not in [USU_NEW, USU_HOMOLOGATED, USU_SOLD, USU_CHANGED]:
                raise Exception(
                    f"Usufruto com vinculo de Suspensão não pode ser cancelado."
                )
        return True

    def validate_scheduled_payment(self):
        """
            Validar se o pagamento do usufruto tem pagammento vinculado
        Returns:
            bool (True/False)
        """
        for usu in self.usufructs_out:
            if usu.payments.exists():
                raise Exception(
                    "Somente usufruto sem vinculo com pagamento pode ser cancelado."
                )
        return True

    def set_status_usufruct_modifieds(self, usufruct, created=False):
        """
            Método que seta o status do usufruto

        Args:
            usufruct (Usufruct): usufrutos a ser modificado
            created (bool): criar atividade
        """
        if created:
            usufruct.status = USU_CANCELED
        elif not usufruct.start_date:
            usufruct.status = USU_SOLD
        else:
            usufruct.status = USU_HOMOLOGATED

    def set_status_usufruct_activity_modifieds(
        self, modifieds, usufruct, created=False
    ):
        """
            Método que seta o status do usufruto da atividade modificado anterioriomente

        Args:
            modifieds (list): lista de usufrutos a serem modificados
            created (bool): criar atividade
        """

        for modified in modifieds:
            modified.status = (
                USU_CANCELED
                if created
                else USUFRUCT_STATUS_MODIFIED[usufruct.activity.type_of_activity]
            )
            modified.save(validate_prevent=False)
            modified.refresh_from_db()
            # modified.update_status(validate_prevent=False)
            self.set_status_usufruct_activity_modifieds(
                modified.activity.modifieds.filter(), modified, created=created
            )

    def _homologate_modifieds(self, modifieds=[], created=False):
        """Este método leva os usufrutos modificados de volta para homologado.

        Args:
            modifieds (list): lista de usufrutos
            created (bool): criar atividade
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usufructs = modifieds if created else self.modifieds.filter()
        for usu in usufructs:
            self.set_status_usufruct_activity_modifieds(
                usu.activity.modifieds.filter(), usu, created=created
            )
            self.set_status_usufruct_modifieds(usu, created=created)
            usu.save(validate_prevent=True if usu.status == USU_SOLD else False)
            usu.refresh_from_db()
            # usu.update_status(validate_prevent=False)

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        modified=None,
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        immediate_authorization=None,
        mediate_authorization=None,
    ):
        """Método fazer da ação Cancelar.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            modified (int): pk do Usufruct que será modificado/alterado
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
        Returns:
            activity (ActivityCancel): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "cancelar",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )
        activity = None
        usu = Usufruct.objects.get(pk=modified)

        with transaction.atomic():
            activity = ActivityCancel.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_CANCEL,
                usufructs_out=[modified],
                justification=justification,
                note=note,
                context="admin",
                usufruct_modifieds=usu.activity.modifieds.filter(),
            )
            activity.acquisition_period.save()
            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize, note=True, validate_prevent_usufruct=True
            )

            usu.transit_status("cancelar", USU_CANCELED, validate_prevent=True)
            activity._homologate_modifieds(
                modifieds=usu.activity.modifieds.filter(), created=True
            )
            activity.save(validate_prevent=True, validate_prevent_usufruct=True)

        return activity


class ActivityRetifyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_RECTIFY)


class ActivityRetify(ActivityChange):
    objects = ActivityRetifyManager()

    class Meta:
        proxy = True

    def notify(self, notify_prevent=False):
        """Este método envia a notificação se notify_prevent for False."""
        if not notify_prevent:
            if self.authorized is None:
                super(ActivityRetify, self).notify()
            else:
                self.notify_authorize()

    def _book_usufructs(self, notify=True, validate_prevent_usufruct=False):
        """Método utiliza _book_usufruct para marcar os usufrutos de entrada.

        Args:
            notify (datetime.date): notify, default é True
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.usufructs_in:
            list_usu_pks = [
                element for element in self.usufructs_out_pks if element is not None
            ]
            list_usu_pks.sort(reverse=True)
            index = self.usufructs_in.index(usu)
            usu_out_pk = (
                list_usu_pks[index]
                if index < len(list_usu_pks)
                else list_usu_pks[len(list_usu_pks) - 1]
            )
            if usu_out_pk:
                usu_out = Usufruct.objects.get(pk=usu_out_pk)
            self._book_usufruct(
                usu.get("start_date"),
                usu.get("end_date"),
                notify=notify,
                validate_prevent=validate_prevent_usufruct,
                usu_out=usu_out,
            )
        return True

    def _book_usufruct(
        self, start_date, end_date, notify=True, validate_prevent=False, usu_out=None
    ):
        """Método cria os usufrutos e realiza suas validações. Também Valida o AcquisitionPeriod através de validate.

        Args:
            start_date (datetime.date): start_date
            end_date (datetime.date): end_date
            notify (datetime.date): notify, default é True
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usu = Usufruct.create(self, start_date, end_date, validate_prevent)
        usu.usu_out = usu_out
        usu.save(validate_prevent=validate_prevent)
        return True

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent and self.days_on_sale:
            self.validate_max_days_sale()
        if not validate_prevent_usufruct:
            if not validate_prevent:
                self.validate_usufruct_in()
            self.validate_qtd_usufruct()
        self.validate_status_usufruct()
        # self.validate_max_retification()

        return super(ActivityRetify, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_max_days_sale(self):
        """Este método valida se existe configuração para quantidade máxima de dias para vender. Utilizando max_days_sale e days_on_sale.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if self.configuration.max_days_sale and self.configuration.max_days_sale < (
            self.days_on_sale
            + self.acquisition_period.paid_days
            - self.set_days_sell_usufruct_out()
        ):
            raise Exception(
                """Quantidade informada para venda é superior ao permitido para o tipo de usufruto
                (Máximo permitido %d dias)"""
                % (self.configuration.max_days_sale)
            )
        return True

    def validate_qtd_usufruct(self):
        """Valida se o total de usufruto/venda deverá ser igual ao total de usufrutos/venda selecionado

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        total_usufruct_out = 0
        total_new_usufruct = self.days_on_sale if self.days_on_sale else 0
        for modified in self.usufructsout:
            total_usufruct_out = total_usufruct_out + modified.days

        for usufruct in self.usufructsin:
            total_new_usufruct = total_new_usufruct + usufruct["days"]

        if total_new_usufruct != total_usufruct_out:
            raise Exception(
                "A quantidade de usufruto/venda deve ser igual a selecionada."
            )

        return True

    def validate_status_usufruct(self):
        """
            Validar se o usufruto pode ser retificado
        Returns:
            bool (True/False)
        """
        for usu in self.usufructs_out:
            if usu.status not in [USU_HOMOLOGATED, USU_SOLD, USU_ENJOYED, USU_ENJOYING]:
                raise Exception(
                    f"Usufruto com status {self.usufructs_out[0].get_status_display()} não pode ser alterado."
                )
        return True

    # def validate_max_retification(self):
    #     for usu in  self.usufructs_out:
    #         if not self.acquisition_period.configuration.max_alteration_usufruct > usu.retification_usufruct_sum:
    #             raise Exception(f"Quantidade máxima de retificação ({self.acquisition_period.configuration.max_alteration_usufruct}) excedida.")
    #     return True

    def validate_modifieds(self, valid_status=[]):
        """Este verifica se os usufrutos podem ser retificados.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not valid_status:
            valid_status = [USU_HOMOLOGATED, USU_SOLD, USU_ENJOYED, USU_ENJOYING]
        modifieds = self.usufructsout.exclude(status__in=valid_status)
        if (
            modifieds.exists()
            and not self.usufructsout.filter(
                pk__in=modifieds.values("pk"),
                status__in=[USU_INTERRUPTED, USU_CHANGING, USU_CHANGED, USU_SUSPENDED],
            ).exists()
        ):
            buff = ""
            for st in valid_status:
                buff += "%s%s" % (", " if buff else "", USUFRUCT_STATUS_CHOICE.get(st))
            raise Exception("Estados válidos para os usufrutos retificados: %s." % buff)
        return True

    def set_days_sell_usufruct_out(self):
        """Este método retorna quantidade de dias de venda a ser retificado

        Returns:
            (int)
        """
        days = 0
        for modified in self.usufructsout:
            if not modified.start_date:
                days = days + modified.days
        return days

    def _book_usufruct_sell(self, days):
        """Método cria os usufrutos e realiza suas validações. Também Valida o AcquisitionPeriod através de validate.

        Args:
            days (int): days
        Returns:
            bool
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        usu = UsufructSell.create(self, days=days)
        usu.save()

        return True

    def _transit_status_usufructs(
        self, action="alterar", status=USU_SUBSTITUTE, validate_prevent=False
    ):
        """Este método leva os usufrutos de entrada para action e status informados. Por padrão action='alterar' e status=USU_SUBSTITUTE.

        Args:
            activity (str): ação que será realiza no usufruto, default é alterar
            status (int): status que será aplicado ao usufruto, default é USU_SUBSTITUTE
            validate_prevent (bool): evitar validação, default é False
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.usufructs.filter():
            if not usu.start_date:
                status = USU_NEW
                validate_prevent = True
            usu.transit_status(action, status, validate_prevent=validate_prevent)

    def _transit_status_modifieds(
        self, action="alterar", status=USU_CHANGING, validate_prevent=False
    ):
        """Este método leva os usufrutos modificados para action e status informados.  Por padrão action='alterar' e status=USU_CHANGING.

        Args:
            activity (str): ação que será realiza no usufruto, default é alterar
            status (int): status que será aplicado ao usufruto, default é USU_CHANGING
            validate_prevent (bool): evitar validação, default é False
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.modifieds.filter():
            usu.transit_status(action, status, validate_prevent=validate_prevent)

    @property
    def modifieds_display(self):
        """Esta propriedade retorna os usufrutos em representação para anotação e notificação.

        Returns:
            modifieds (str)
        """
        modifieds = ""
        for usu in self.modifieds.filter():
            if usu.start_date:
                modifieds += "\n%s a %s (%s dias)" % (
                    DateUtils.date_to_str(usu.start_date),
                    DateUtils.date_to_str(usu.end_date),
                    usu.days,
                )
        return modifieds

    def _homologate_modifieds(self, validate_prevent=False):
        """Este método leva os usufrutos modificados de volta para homologado ou vendido.

        Args:
            validate_prevent (bool): evitar validação, default é False
            validate_prevent_usufruct (bool): Evita a validação de usufrutos

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        for usu in self.modifieds.filter():
            usu.status = USU_HOMOLOGATED
            if not usu.start_date:
                usu.status = USU_SOLD
                validate_prevent = True
            usu.save(validate_prevent=validate_prevent)
            usu.refresh_from_db()
            usu.update_status(validate_prevent=validate_prevent)

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=True,
        days=None,
        transit_status_modifieds=True,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Método fazer da ação RETIFICAR.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar
            transit_status_modifieds (bool): indica se deve transitar o status dos usufrutos modificados
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityRetify): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        # if context != 'migrate':
        #     action_check('vender', acquisition_period.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE)

        action_check(
            "alterar",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )
        activity = None

        with transaction.atomic():
            activity = ActivityRetify.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_RECTIFY,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=False,
                days_on_sale=days,
                context=context,
            )

            activity._transit_status_modifieds(validate_prevent=True)
            if activity.configuration.sell_booked_days and days:
                activity._book_usufruct_sell(days)

            activity._book_usufructs()
            activity._transit_status_usufructs()

            # activity.acquisition_period.validate()
            activity.save(validate_prevent_usufruct=True)

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=authorize,
                note=True,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )
            activity.acquisition_period.save(validate_prevent=True)
            activity.notify()

        reordenar_numero_parcela(activity)
        return activity


class ActivityRemainingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_REMAINING)


class ActivityRemaining(ActivityBook):
    objects = ActivityRemainingManager()

    class Meta:
        proxy = True

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent_usufruct:
            self.validate_max_suspension()
            self.validate_usufruct_in()
        return super(ActivityRemaining, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def validate_max_suspension(self):
        """
            Valida a quantidade máxima que pode ser marcado como saldo remanescente
        Returns:
            bool (True/False)
        """
        modified = self.usufructs_out[0]
        days = 0
        for usu in self.usufructs_in:
            days = days + usu["days"]

        if days > modified.remaining_balance_suspension:
            raise Exception(
                f"Limite de saldo remanescente excedido ({modified.remaining_balance_suspension})."
            )
        return True

    def _homologate_modifieds(self, modifieds=[], created=False):
        """Este método leva os usufrutos modificados de volta para homologado.

        Args:
            modifieds (list): lista de usufrutos
            created (bool): criar atividade
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        pass

    @classmethod
    def create_activity(
        cls,
        acquisition_period=None,
        type_of_activity=ACT_REMAINING,
        status=ACT_ST_CREATED,
        usufructs_in=[],
        usufructs_out=[],
        attachment=None,
        justification=None,
        scale_homologation=False,
        note=True,
        validate_prevent=False,
        validate_prevent_usufruct=False,
        context=None,
        days_on_sale=0,
        usufruct_modifieds=[],
    ):
        """Este método cria e persiste uma Activity a partir dos parâmetros informados. Adiciona informações aos campos usufructs_in, usufructs_out.

        Args:
            acquisition_period (AcquisitionPeriod): AcquisitionPeriod
            type_of_activity (int): type_of_activity, defautl ACT_BOOK
            status (int): status, defautl ACT_ST_CREATED
            usufructs_in (list): usufrutos que serão marcados
            usufructs_out (list): usufrutos que serão modificados
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            scale_homologation (bool): se a escala está sendo homologada
            note (bool): se esta ação deve anotar
            validate_prevent (bool): Evitar validação
            validate_prevent_usufruct (bool): Evita a validação de usufrutos
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (Activity): ação
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        attachment = (
            Attachment.objects.get(pk=int(attachment))
            if type(attachment) in (int, str)
            else attachment
        )
        activity = cls(
            acquisition_period=acquisition_period,
            type_of_activity=type_of_activity,
            status=status,
            attachment=attachment,
            justification=justification,
            scale_homologation=scale_homologation,
            note=note,
        )
        activity.context = context
        activity.set_usufructs_in(usufructs_in)
        activity.set_usufructs_out(usufructs_out)
        activity.set_days_on_sale(days_on_sale)
        activity.set_usufructs_modifieds(usufruct_modifieds)
        activity.days_in_cache = activity.days_in
        activity.days_out_cache = activity.days_out
        activity.save(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
            note_prevent=True,
        )
        return activity

    def add_activity_usufruct_modified(self):
        """Metódo que vincula o usufruto marcado ao modifieds da atividade suspensa"""
        activity_modified = self.usufructs_out[0].activity
        for usu in self.usufructs.filter():
            activity_modified.modifieds.add(usu)

    @classmethod
    def do(
        cls,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=False,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Método fazer da ação MARCAR REMANESCENTE.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar, default False pois apenas marcação não anota nada
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityRemaining): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "marcar", acquisition_period.status, AP_SM, ACQUISITION_PERIOD_STATUS_CHOICE
        )

        activity = None
        with transaction.atomic():
            activity = ActivityRemaining.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_REMAINING,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                note=note,
                context=context,
            )

            activity._book_usufructs()
            activity.add_activity_usufruct_modified()
            activity.acquisition_period.save()
            activity.save(validate_prevent_usufruct=True)

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=True,
                note=True,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )
            activity.notify()

        return activity


class ActivityCorrectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type_of_activity=ACT_CORRECT)


class ActivityCorrect(Activity):
    objects = ActivityCorrectManager()

    class Meta:
        proxy = True

    def correct(self):
        """
        Método que realizar a correção de datas ou dias de usufrutos

        """
        usu = self.usufructs_out[0]
        activity = usu.activity.my_origin
        usufruct = None
        if not self.days_on_sale:
            usufruct = self.usufructs_in[0]
        usu.correct_usufruct(usufruct, self.days_on_sale)
        activity.acquisition_period.update_status(ACQP_PROGRESS)
        activity.transit_status(
            "corrigir",
            ACT_ST_HOMOLOGATED,
            validate_prevent=False if not self.days_on_sale else True,
            validate_prevent_usufruct=True,
        )
        self.modifieds.add(usu)

    def validate(self, validate_prevent=False, validate_prevent_usufruct=False):
        if not validate_prevent_usufruct:
            self.validate_usufruct_in()
        return super(ActivityCorrect, self).validate(
            validate_prevent=validate_prevent,
            validate_prevent_usufruct=validate_prevent_usufruct,
        )

    def _homologate_modifieds(self, validate_prevent=False):
        """Este método leva os usufrutos modificados de volta para homologado ou vendido.

        Args:
            validate_prevent (bool): evitar validação, default é False
            validate_prevent_usufruct (bool): Evita a validação de usufrutos

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        pass

    @classmethod
    def do(
        cls,
        days=None,
        acquisition_period=None,
        usufructs_in=[],
        modifieds=[],
        authorize=None,
        attachment=None,
        justification=None,
        note=False,
        immediate_authorization=None,
        mediate_authorization=None,
        context=None,
    ):
        """Método fazer da ação CORRIGIR.

        Args:
            acquisition_period (AcquisitionPeriod): instância de período aquisitivo
            usufructs_in (list): lista de dict com as parcelas agendadas
            modifieds (list): lista de pks de Usufructs que serão modificados/alterados
            authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
            attachment (attachment_pk): pk do anexo
            justification (str): justificativa
            note (bool): anotar, default False pois apenas marcação não anota nada
            immediate_authorization(Servidor): chefe imediato
            mediate_authorization(Servidor): chefe mediato
            context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
        Returns:
            activity (ActivityCorrect): uma instância de ação válida
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        action_check(
            "corrigir",
            acquisition_period.status,
            AP_SM,
            ACQUISITION_PERIOD_STATUS_CHOICE,
        )

        activity = None
        with transaction.atomic():
            activity = ActivityCorrect.create_activity(
                acquisition_period=acquisition_period,
                type_of_activity=ACT_CORRECT,
                usufructs_in=usufructs_in,
                usufructs_out=modifieds,
                attachment=attachment,
                justification=justification,
                days_on_sale=days,
                note=note,
                context=context,
            )

            activity.acquisition_period.save()
            activity.save(validate_prevent_usufruct=True)

            activity.from_activity = activity
            activity.authorize_and_homologate(
                authorize=True,
                note=True,
                immediate_authorization=immediate_authorization,
                mediate_authorization=mediate_authorization,
                validate_prevent_usufruct=True,
            )
            activity.correct()

        return activity


class Attachment(AuditTimestampModel):
    file_descriptor = models.ForeignKey(
        File,
        help_text="Arquivo anexado.",
        verbose_name="Arquivo",
        related_name="dayoff_attachments",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    protocol = models.ForeignKey(
        Protocol,
        help_text="Protocolo anexado.",
        verbose_name="Protocolo",
        related_name="dayoff_attachments",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    publication = models.ForeignKey(
        Publication,
        help_text="Publicação anexada.",
        verbose_name="Publicação",
        related_name="dayoff_attachments",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    sei_url = models.URLField(verbose_name="Url Sei", max_length=200, blank=True)

    class Meta:
        permissions = (
            ("dayoffadmin", "Pode administrar os Anexos"),
            ("dayoffpayment", "Pode modificar as informações de pagamentos"),
        )

    def __str__(self):
        return "%s%s%s%s" % (
            (("%s " % self.file_descriptor) if self.file_descriptor else ""),
            (("%s " % self.protocol) if self.protocol else ""),
            (("%s " % self.publication) if self.publication else ""),
            self.sei_url,
        )

    def validate_mandatory_field(self):
        if (
            not self.file_descriptor
            and not self.protocol
            and not self.publication
            and not self.sei_url
        ):
            raise Exception("Informe pelo menos um anexo.")

        return True

    def validate(self):
        self.validate_mandatory_field()

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)


class Payment(AuditTimestampModel):
    acquisition_period = models.ForeignKey(
        AcquisitionPeriod,
        on_delete=models.PROTECT,
        help_text="O período aquisitivo do servidor",
        verbose_name="Período aquisitivo",
        related_name="payments",
    )
    type_of = models.PositiveSmallIntegerField(
        help_text="Tipo do pagmento.",
        verbose_name="Tipo",
        default=1,
        choices=Choice.get_choices_for("dayoff", "TYPE_OF_PAYMENT"),
    )
    info = models.CharField(
        help_text="Informação sobre o pagamento",
        verbose_name="Informação",
        max_length=50,
        blank=True,
    )
    description = models.CharField(
        help_text="Descrição sobre o pagamento",
        verbose_name="Descrição",
        max_length=400,
        blank=True,
        default="",
    )
    usufruct = models.ForeignKey(
        Usufruct,
        help_text="Usufruto relacionado ao pagamento.",
        verbose_name="Usufruto",
        related_name="payments",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    entry_payment = models.ForeignKey(
        FolhaEvento,
        help_text="Lançamento da folha realacionado ao pagamento",
        verbose_name="Lançamento",
        related_name="dayoff_payments",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    payment_oid = models.PositiveIntegerField(
        help_text="Id do objeto da folha de pagamento",
        verbose_name="FOPAG Id",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.info and self.entry_payment:
            self.info = f"{self.entry_payment} ({self.entry_payment.qnt} dias) - {self.entry_payment.folha}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_of_display()}: {self.acquisition_period} - {self.info}"


class UsufructPaymentControl(AuditTimestampModel):
    """
    Model responsável pelo Controle de Pagamentos de Usufrutos
    """

    employee = models.ForeignKey(
        Servidor,
        verbose_name="Servidor",
        related_name="ctrl_usufruct_payment",
        on_delete=models.PROTECT,
    )
    usufruct = models.ForeignKey(
        Usufruct,
        verbose_name="Usufrutos",
        related_name="ctrl_payments",
        on_delete=models.PROTECT,
    )
    status = models.SmallIntegerField(
        default=1,
        verbose_name="Status de Conferência do RH",
        choices=Choice.get_choices_for("dayoff", "DAYOFF_STATUS_PAYMENT_CONTROL"),
    )
    payroll_ctrl_status = models.SmallIntegerField(
        default=1,
        verbose_name="Status de Conferência de Folha",
        choices=Choice.get_choices_for("dayoff", "DAYOFF_PAYROL_CONTROL_STATUS"),
    )
    checked_by = models.ForeignKey(
        Servidor,
        verbose_name="Conferido por",
        related_name="ctrl_payment_checked",
        on_delete=models.PROTECT,
    )
    checked_at = models.DateTimeField(auto_now_add=True)

    applied_by = models.ForeignKey(
        Servidor,
        verbose_name="Aplicado por",
        related_name="ctrl_payment_applied",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    applied_at = models.DateTimeField(verbose_name="Aplicado em", blank=True, null=True)
    observation = models.TextField(
        help_text="Observação referente a controle do usufruto",
        verbose_name="Obervação",
        null=True,
        blank=True,
    )
    type_of_control = models.SmallIntegerField(
        default=1,
        verbose_name="Tipo da Conferência Conferência",
        choices=Choice.get_choices_for("dayoff", "DAYOFF_TYPE_OF_PAYMENT_CONTROL"),
    )
    calculated_value = models.DecimalField(
        verbose_name="Valor calculado",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    confirmed_value = models.DecimalField(
        verbose_name="Valor confirmado",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    paid_value = models.DecimalField(
        verbose_name="Valor a pagar",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    payment_installments = models.IntegerField(
        verbose_name="Parcelas de Pagamento", null=True, blank=True
    )
    manual_confirmation_payment = models.BooleanField(
        default=False,
        help_text="A confirmação do valor a pagar foi manual?",
        verbose_name="Inclusão manual",
    )
    manual_confirmation_by = models.ForeignKey(
        Servidor,
        verbose_name="Confirmação manual de valor por",
        related_name="manual_confirmed_usufuct_control",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    manual_confirmation_at = models.DateTimeField(
        verbose_name="Confirmação manual de valor em", blank=True, null=True
    )

    class Meta:
        verbose_name = "Controle Controle de Pagamentos de Usufrutos"
        unique_together = ("employee", "usufruct")

    def __str__(self):
        return f"{self.employee}: {self.usufruct}"

    def control_check(self):
        self.status = PAYMENT_CHECKED
        self.save()

    def control_decline(self):
        self.status = PAYMENT_DECLINED
        self.save()


auditlog.register(Usufruct)
auditlog.register(UsufructSell)
auditlog.register(AcquisitionPeriod)
auditlog.register(AcquisitionPeriodAttachment)
auditlog.register(Activity)
auditlog.register(ActivityBook)
auditlog.register(ActivityChange)
auditlog.register(ActivityInterrupt)
auditlog.register(ActivitySuspend)
auditlog.register(ActivityIndemnify)
auditlog.register(ActivitySell)
auditlog.register(ActivityBookSell)
auditlog.register(ActivityCancel)
auditlog.register(ActivityCancel)
auditlog.register(ActivityRetify)
auditlog.register(ActivityRemaining)
auditlog.register(ActivityCorrect)
auditlog.register(Configuration)
auditlog.register(UsufructPaymentControl)
