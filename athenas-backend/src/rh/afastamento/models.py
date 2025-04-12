# -*- coding: utf-8 -*-
"""
    Módulo Afastamento.
"""

import codecs
import os
from datetime import datetime, timedelta
from contrib.helpers import clear_to_ascii
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models, transaction
from django.db.models.query_utils import Q

from standard.models import Configuration
from contrib.daterange import NewDateRange
from contrib.decorator import auditable, to_search, deprecated
from contrib.helpers import get_default_controller_for_model
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, getLogger
from engine.models import UserHasNotPermission

# from rh.models import ProcessSuspension
from ged.models import Arquivo
from rh import models as rh_models
from rh import templates
from rh.const import (
    ACIDENTE_TRANSITO_OUTROS,
    ACTIVE,
    ALTERACAO,
    CANCELADO,
    CANCELED,
    DEFERIDA,
    ESTADO_BASE_LICENCA_AFASTAMENTO,
    FINISHED,
    GRAU_PARENTESCO_DOENCA_CHOICES,
    INDEFERIDA,
    INTERRUPCAO,
    NAO_INFORMADA,
    ORIGEM,
    REVOGACAO,
    SCHEDULED,
    SUSPENSAO,
    TIPO_BASE_LICENCA_AFASTAMENTO,
    TYPE_COMPENSATION_LOW,
    TYPE_DEPARTURE_DISMISSAL_JUDGMENT,
    TYPE_FULL_BIRTHDAY,
    TYPE_MATERNITY_LICENSE,
    TYPE_NEW_FUNCTION,
    TYPE_ORDELY,
    TYPE_RECESS,
    TYPE_TRAVEL,
    TYPE_VACATION,
    TYPE_WORK_GROUP,
    WORK_ASSIGNMENT,
    TYPE_DEPARTURE_OTHER_ORGAN,
    TYPE_DEPARTURE_CANDIDATURE,
)
from rh.models import (
    AnotacaoGeral,
    Cargo,
    Curso,
    Localidade,
    MovimentacaoPessoal,
    MovimentacaoPosse,
    MovimentacaoSubstituicao,
    PessoaFisica,
    ProfissionalSaude,
    Prorrogacao,
    Publicacao,
    Quadro,
    Servidor,
    ServidorLotacao,
    SituacaoFuncional,
    UnidadeAdministrativa,
)
from rh.utils import (
    format_situacao_funcional,
    is_active,
    notify_employee,
    send_mail_and_notify,
)
from standard.models import AuditTimestampModel, Choice
from auditlog.registry import auditlog

log = getLogger(__name__)


def employees_to_notify(employee):
    employees = Servidor.objects.filter(user__groups__name__icontains="rh-afastamento")
    if employee.membro:
        employees = Servidor.objects.filter(
            user__groups__name__icontains="expediente-afastamento"
        )
    return employees


def notify(instance, old_fields):
    from engine.notification.models import Notification

    to_send = False
    message = ""
    try:
        if instance.servidor.membro:
            if old_fields.get("data_fim", None):
                old = old_fields.get("data_fim")
                new = instance.data_fim
                if isinstance(old, (list, tuple)):
                    old = old_fields.get("data_fim")[0]
                    new = old_fields.get("data_fim")[1]
                message = "A data fim mudou de %s para %s" % (
                    DateUtils.date_to_str(old) if old else "",
                    DateUtils.date_to_str(new) if new else "",
                )
                to_send = True
            if old_fields.get("estado", None):
                new = instance.estado
                old = old_fields.get("estado")
                if isinstance(old, (list, tuple)):
                    new = old[1]
                    old = old[0]
                state_old = Choice.objects.filter(
                    app_label="rh", name="ESTADO_BASE_LICENCA_AFASTAMENTO", value=old
                ).last()
                state = Choice.objects.filter(
                    app_label="rh", name="ESTADO_BASE_LICENCA_AFASTAMENTO", value=new
                ).last()
                message = "O estado mudou de %s para %s" % (
                    state_old if state_old else "",
                    state if state else "",
                )
                to_send = True
            employees = [
                employee
                for employee in Servidor.objects.filter(
                    user__groups__name__icontains="afastamento-receber-notificacao"
                )
            ]
            if to_send:
                instance_unicode = "%s - %s" % (
                    instance.servidor,
                    instance.__str_restful__(),
                )
                message = "%s - %s" % (instance_unicode, message)
                params = {"mensagem": "%s" % message}
                Notification.notify_all(
                    "NOTIFICACAO_ATHENAS", employees, instance, **params
                )
    except Exception as err:
        log.exception(err)
        log.info("Notificação não enviada!")


class BaseLicencaAfastamentoQueryset(models.QuerySet):
    def of_employee(self, employee):
        return self.filter(servidor=employee)

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio__gt=range_.last)
                | (~Q(data_fim=None) & Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio__gt=data) | (~Q(data_fim=None) & Q(data_fim__lt=data))
            )

    def unpaid(self):
        return self.filter(remunerado=False)

    def not_canceled(self):
        return self.exclude(estado=CANCELADO)

    def no_cession(self):
        return self.filter(afastamento__afastamentooutroorgao=None)

    def no_vacation(self):
        return self.filter(feriasafastamento=None)

    def maternitylicense(self):
        return self.filter(tipo=TYPE_MATERNITY_LICENSE)

    def esocial(self, *args, **kwargs):
        return self.currents_in(*args, **kwargs).exclude(
            tipo__in=[
                # TYPE_VACATION,
                TYPE_RECESS,
                TYPE_DEPARTURE_OTHER_ORGAN,
                TYPE_TRAVEL,
                TYPE_WORK_GROUP,
                TYPE_NEW_FUNCTION,
                TYPE_ORDELY,
                TYPE_COMPENSATION_LOW,
                TYPE_FULL_BIRTHDAY,
                TYPE_DEPARTURE_DISMISSAL_JUDGMENT,
                TYPE_DEPARTURE_CANDIDATURE,
            ]
        )

    def afastamento_referencia(self, servidor, dt_inicio_ref, dt_fim_ref):
        return self.filter(
            servidor=servidor, data_inicio__lte=dt_fim_ref, data_fim__gte=dt_inicio_ref
        ).exclude(estado=CANCELADO)


@to_search(
    [
        {"name": "servidor__matricula", "type": "text"},
        {"name": "servidor__pessoa_fisica__cpf", "type": "text"},
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
    ]
)
class BaseLicencaAfastamento(MovimentacaoPessoal):
    """
    Classe base para Licenças e Afastamentos.
    """

    publicacao_fim = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Documento Encerramento",
    )
    remunerado = models.BooleanField(default=True, verbose_name="Remunerado")
    concessao_durante_estagio_prob = models.BooleanField(default=True)
    efetivo_exercicio = models.BooleanField(default=True)
    suspensao_estagio_prob = models.BooleanField(default=False)
    suspensao_contagem_ferias = models.BooleanField(default=False)
    prorroga_progressao = models.BooleanField(default=False)
    data_inicio = models.DateField(verbose_name="Data Início", db_index=True)
    data_fim = models.DateField(
        null=True, blank=True, verbose_name="Data Fim", db_index=True
    )
    data_prevista = models.DateField(
        null=True, blank=True, verbose_name="Data Prevista Fim", db_index=True
    )
    # CAMPO MOTIVO EXISTE POR CAUSA DO ARQUIMEDES
    motivo = models.IntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "MOTIVO_SUBSTITUICAO"),
        blank=True,
    )
    tipo = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "TIPO_BASE_LICENCA_AFASTAMENTO"),
        blank=True,
        db_index=True,
    )
    estado = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "ESTADO_BASE_LICENCA_AFASTAMENTO"),
        blank=True,
        db_index=True,
    )
    alteracao = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "ALTERACAO_BASE_LICENCA_AFASTAMENTO"),
        verbose_name="Tipo Alteração",
    )
    prorrogacao = models.ManyToManyField(
        Prorrogacao,
        verbose_name="Prorrogação",
        related_name="afastamento",
    )
    agendado_arquimedes = models.BooleanField(default=False)
    situation_unicode = models.CharField(
        verbose_name="Motivo Cache", max_length=255, null=True, blank=True
    )
    annotation_class = models.CharField(
        verbose_name="Classe da Anotação", max_length=255, null=True, blank=True
    )
    designation_exercise = models.ManyToManyField(
        "rh.ServidorLotacao", related_name="departures_exercise"
    )
    interrupt_vacation = models.BooleanField(default=True)
    status_change_date = models.DateField(
        null=True,
        blank=True,
        help_text="Será gravado quando o estado mudar para ATIVO, FINALIZADO, CANCELADO",
        verbose_name="Data de mudança de estado",
    )
    event_esocial = models.PositiveIntegerField(blank=True, null=True)
    origin_register = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        choices=Choice.get_choices_for(
            "rh",
            "ORIGIN_REGISTER",
        ),
        verbose_name="Origem do registro",
    )

    desconta_tempo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        default=2,
        verbose_name="Desconta ?",
    )  # 1-Sim para Deconta, 2-Não para não Desconto

    total_parcial = models.IntegerField(
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        default=2,
        verbose_name="Desconto Parcial ?",
    )  # 1-Sim para desconto parcial, 2-Não para desconto total

    total_desconto = models.PositiveIntegerField(default=0)

    objects = BaseLicencaAfastamentoQueryset.as_manager()

    class Meta:
        db_table = "afastamento_baselicencaafast"
        verbose_name = "BaseLicencaAfastamento"
        ordering = ["-data_inicio", "-estado"]

    anotacao_classe = rh_models.AnotacaoGeral
    update_date_end = True

    usuario_nao_informa = [
        "remunerado",
        "concessao_durante_estagio_prob",
        "efetivo_exercicio",
        "suspensao_estagio_prob",
        "suspensao_contagem_ferias",
    ]

    must_validate_employee_departured = True

    permissions = (("can_receive_notify", "Pode receber notificação"),)

    class ErroVigenciaNaoEncontrada(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self,
                "%s"
                % (txt if txt else "Data de vigência do Documento não encontrado."),
            )

    class ErroPrazoMaximo(Exception):
        def __init__(self, txt=None, prazo_maximo=1):
            Exception.__init__(
                self,
                "%s"
                % (
                    txt
                    if txt
                    else "O prazo máximo permitido é de %s dia(s)." % prazo_maximo
                ),
            )

    class ErroPrazoMinimo(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "O prazo mínimo é de 4 dias.")
            )

    class ErroDataFimNone(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Data de fim deve ser preenchida.")
            )

    class ErroAfastamentoIniciado(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Afastamento já foi iniciado.")
            )

    class ExceptionBasePeriodo(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Existe período conflitando.")
            )

    class ErroAfastamentoFinalizado(Exception):
        def __init__(self, txt=None):
            Exception.__init__(self, "%s" % (txt if txt else "Afastamento finalizado."))

    def __str__(self):
        return "%s - %s: %s" % (
            self.servidor.pessoa_fisica,
            self.situation_unicode,
            self.get_estado_display(),
        )

    def __str_restful__(self):
        return "%s: %s - %s à %s" % (
            self.situation_unicode,
            self.get_estado_display(),
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
        )

    @property
    def tipo_classe(self):
        """
        Este método informa 0 __class__.__name__ instância.
        """
        for i in list(TIPO_BASE_LICENCA_AFASTAMENTO.items()):
            if i[1] == self.__class__.__name__:
                if self.__class__.__name__ == "AfastamentoEstudar" and self.parcial:
                    return (
                        Choice.objects.filter(
                            app_label="rh",
                            name="TIPO_BASE_LICENCA_AFASTAMENTO",
                            label="AfastamentoParcialEstudar",
                        )
                        .first()
                        .value
                    )

                elif (
                    self.__class__.__name__ == "LicencaDoencaPessoaFamilia"
                    and self.days_amount >= 6
                ):
                    return (
                        Choice.objects.filter(
                            app_label="rh",
                            name="TIPO_BASE_LICENCA_AFASTAMENTO",
                            label="LicencaDoencaPessoaFamiliaJuntaMedica",
                        )
                        .first()
                        .value
                    )
                return i[0]
        return 1

    @property
    def situacao_funcional(self):
        """
        Este métdo informa a situação funcional padrão de cada classe.
        """
        situacao_funcional = "NOT_FOUND"
        try:
            situacao_funcional = self.instancia_modelo.situacao_funcional
        except Exception:
            pass
        return situacao_funcional

    @property
    def possui_alteracao(self):
        """
        Este método informa se a instância possui alteração.
        """
        return hasattr(self, "alteracao") and self.alteracao is not None

    @property
    def possui_prazo_concedido(self):
        """
        Este método informa se a instância possui alteração.
        """
        return hasattr(self, "prazo_concedido") and self.prazo_concedido is not None

    @property
    def possui_prazo_solicitado(self):
        """
        Este método informa se a instância possui alteração.
        """
        return hasattr(self, "prazo_solicitado") and self.prazo_solicitado is not None

    @property
    def possui_prorrogacao(self):
        """
        Este método informa se a instância possui prorrogação.
        """
        if self.pk and hasattr(self, "prorrogacao") and self.prorrogacao.exists():
            return True
        return False

    @property
    def controller(self):
        """
        Esta propriedade retornará o controller deste modelo.
        """
        controller = get_default_controller_for_model(
            self.instancia_modelo.__class__, False
        )
        return controller.controller if controller is not None else None

    @property
    def is_canceled(self):
        return self.alteracao in (CANCELED, SUSPENSAO) or (
            self.alteracao == REVOGACAO and self.estado == CANCELED
        )

    @property
    def _get_multiple_date_range(self):
        mdr_departure = NewDateRange(self.data_inicio, self.data_fim)
        mdr_substitution = NewDateRange()
        mdr_inactivation = NewDateRange()
        for sub in self.substituicao.filter():
            mdr_substitution += NewDateRange(sub.data_inicio, sub.data_fim)
        for ina in self.inativacaocargomembro.filter():
            mdr_inactivation += NewDateRange(ina.data_inicio, ina.data_fim)
        return mdr_departure, mdr_substitution, mdr_inactivation

    @property
    def pending_period(self):
        mdr_departure, mdr_substitution, mdr_inactivation = (
            self._get_multiple_date_range
        )
        valid = False
        if self.substituicao.exists():
            valid = mdr_substitution.intersect(mdr_departure) == mdr_departure
        if self.inativacaocargomembro.exists():
            valid = mdr_inactivation.intersect(mdr_departure) == mdr_departure
        return valid

    @property
    def pending_period_days(self):
        mdr_departure, mdr_substitution, mdr_inactivation = (
            self._get_multiple_date_range
        )
        days = mdr_departure.days
        days -= mdr_substitution.days
        days -= mdr_inactivation.days
        return days

    @property
    def days_amount(self):
        return NewDateRange(self.data_inicio, self.data_fim).days

    def find_departure_concatenated(self, way=None):
        """
        :py:function:: find_departure_concatenated(self, way=None)

        This method finds concatenated departures without leak days.
        Uses way parameter to define the way to dig in recursively.

        :param str: str 'ASC'/'DESC'/None
        :return: list, list of BaseLicencaAfastamento
        :rtype: list
        """

        if self.data_fim:
            departures_asc = (
                BaseLicencaAfastamento.objects.filter(
                    servidor=self.servidor,
                    data_inicio=(self.data_fim + relativedelta(days=1)),
                )
                .exclude(pk=self.pk)
                .exclude(estado=CANCELED)
            )
        else:
            departures_asc = BaseLicencaAfastamento.objects.none()

        departures_desc = (
            BaseLicencaAfastamento.objects.filter(
                servidor=self.servidor,
                data_fim=(self.data_inicio - relativedelta(days=1)),
            )
            .exclude(pk=self.pk)
            .exclude(estado=CANCELED)
        )

        if not way and departures_asc.exists():
            way = "ASC"
        elif not way and departures_desc.exists():
            way = "DESC"

        concatenated = [self]
        if way == "ASC":
            for departure in departures_asc:
                concatenated += departure.find_departure_concatenated(way=way)
        elif way == "DESC":
            for departure in departures_desc:
                concatenated += departure.find_departure_concatenated(way=way)
        return concatenated

    def date_range_departure_concatenated(self):
        date_start = None
        date_end = None
        for departure in self.find_departure_concatenated():
            if not date_start or date_start > departure.data_inicio:
                date_start = departure.data_inicio
            if not date_end or date_end < departure.data_fim:
                date_end = departure.data_fim
        return NewDateRange(date_start, date_end)

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.data_inicio, date_end=self.data_fim
        )

    @classmethod
    def _query_not_member_departure(cls):
        """
        This method returns a query mandatory which DO NOT generate departure.
        """
        return (
            ~Q(viagem=None)
            |
            # ~Q(desempenhofuncao=None) |
            ~Q(atuacaogrupotrabalho=None)
        )

    @classmethod
    def _raw_employee_departures(cls, employee, date=None):
        """
        :py:function:: _raw_employee_departures(cls, employee, date=None)

        This method returns all departures by a date parameter. If employee is supplied then take his departures.

        :param Servidor employee: employee
        :param date date: Date to determine a period of EmployeeWorkplace
        :return: queryset of BaseLicencaAfastamento
        """
        date = datetime.now().date() if not date else date
        departures = BaseLicencaAfastamento.objects.filter(
            (Q(data_inicio__lte=date) & (Q(data_fim__gte=date) | Q(data_fim=None)))
        ).exclude(estado=CANCELED)
        if employee:
            departures = departures.filter(servidor=employee)
        return departures

    @classmethod
    def employee_departures(cls, employee, date=None):
        """
        This method encapsulates the call class method _raw_employee_departures.
        Returns all departures from the employee. If Hes a member will exclude
        some departures listeds in _query_not_member_departure.
        """
        date = datetime.now().date() if not date else date
        departures = cls._raw_employee_departures(employee, date=date)
        # if employee.membro:
        #     departures = departures.exclude(cls._query_not_member_departure())
        return departures

    @classmethod
    def _intervalo_pertence_afastamento(cls, afastamento, data_inicio, data_fim):
        """
        Este método verifica se o intervalo informado pertence ao afastamento.
        """
        pertence = False
        if data_inicio > data_fim:
            raise Exception("Data Início deve ser menor ou igual a Data Fim!")
        if NewDateRange(afastamento.data_inicio, afastamento.data_fim).contains(
            NewDateRange(data_inicio, data_fim)
        ):
            pertence = True
        elif (
            afastamento.data_fim is None
            and data_fim
            and data_fim >= afastamento.data_inicio
            and data_inicio >= afastamento.data_inicio
        ):
            pertence = True
        elif not data_fim and data_inicio >= afastamento.data_inicio:
            pertence = True
        return pertence

    @classmethod
    def _finalizado(cls, date_end=None, data=None):
        """
        Este método verifica se um período foi finalizado.
        """
        data = datetime.now().date() if not data else data
        finalizado = False
        if date_end and date_end < data:
            finalizado = True
        return finalizado

    @classmethod
    def _iniciado(cls, data_inicio, data_fim, data=None):
        """
        Este método verifica se um perído foi iniciado.
        """
        data = datetime.now().date() if not data else data
        iniciado = False
        if data_inicio <= data and not cls._finalizado(date_end=data_fim, data=data):
            iniciado = True
        return iniciado

    @classmethod
    def verifica_interseccao_periodo(
        cls, servidor, data_inicio, data_fim, departures=None
    ):
        """
        Este método verifica se existe a intersecção de um período com o
        período de um afastamento do servidor informado.
        Retorna todos afastamentos encontrados.
        Trabalha com NewDateRange, assim se a data fim não for informada utilizará o fim como intervalo aberto.
        """
        dr_corrente = NewDateRange(data_inicio, data_fim)
        afastamentos = []
        if not departures:
            departures = BaseLicencaAfastamento.objects.filter(
                servidor=servidor
            ).exclude(estado__in=(CANCELED,))
        for afastamento in departures:
            dr_afastamento = NewDateRange(afastamento.data_inicio, afastamento.data_fim)
            if dr_corrente.intersect(dr_afastamento).days > 0:
                afastamentos.append(afastamento)
        return afastamentos

    @classmethod
    def atualizar_estado(cls, instance=None, data=None, tipo=("S", "M")):
        """
        Este método é responsável por atualizar o estado dos afastamentos.
        """
        data = datetime.now() if not data else data
        log.info("______________________ATUALIZAR_ESTADO______________________")
        mensagem = "Tentando atualizar o estado %s" % instance
        changed = False
        try:
            # afastamentos = BaseLicencaAfastamento.objects.filter(
            #     (
            #         Q(data_fim__gte=(data - relativedelta(months=24))) & Q(data_fim__lt=data)
            #     ) | Q(data_inicio__gte=(data - relativedelta(months=24)))
            # ).exclude(estado__in=(CANCELED, ))
            ontem = data - relativedelta(days=7)
            hoje = datetime.now().date()
            if instance:
                afastamentos = BaseLicencaAfastamento.objects.filter(pk=instance.pk)
            else:
                afastamentos = BaseLicencaAfastamento.objects.filter(
                    (Q(data_fim__gte=ontem) & Q(data_fim__lt=hoje))
                    | (Q(data_inicio__gte=ontem) & Q(data_inicio__lte=hoje))
                    | Q(modified_at=hoje)
                ).exclude(estado__in=(CANCELED,))
                afastamentos = afastamentos.filter(servidor__tipo__in=tipo)
            count = 1
            total = afastamentos.count()
            # import time
            # afastamentos = afastamentos.filter(servidor__tipo='M')
            # afastamentos = afastamentos.filter(servidor__matricula__in=[14393])
            for base in afastamentos.order_by("pk"):
                situation = cls.situation_define(base)
                log.info(
                    "AFASTAMENTO - ATUALIZANDO ESTADO %s de %s..." % (count, total)
                )
                if base.estado != situation:
                    changed = True
                    mensagem = "%s de %s para %s" % (
                        base,
                        base.get_estado_display(),
                        ESTADO_BASE_LICENCA_AFASTAMENTO.get(situation),
                    )
                    log.info(mensagem)
                    try:
                        afastamento = base.instancia_modelo
                        # afastamento.estado = situation
                        afastamento.save()
                    except Exception as err:
                        log.exception(err)
                        BaseLicencaAfastamento.objects.filter(pk=base.pk).update(
                            estado=cls.situation_define(base)
                        )
                        send_mail_and_notify(
                            source="ERRO EM %s" % cls.__name__,
                            message="%s -> %s" % (mensagem, err),
                            err=err,
                        )
                count += 1
        except Exception as err:
            log.exception(err)
        return changed

    @classmethod
    def situation_define(cls, departure):
        """
        :py:function:: situation_define(cls, departure)

        This method defines which situation is actual.

        :param BaseLicencaAfastamento departure: departure
        :return: situation
        :rtype: int
        """
        situation = SCHEDULED
        if departure._afastamento_iniciado():
            situation = ACTIVE
        elif departure._afastamento_finalizado():
            situation = FINISHED

        if departure.alteracao in (CANCELED, SUSPENSAO):
            situation = CANCELED
        elif (
            departure.alteracao == REVOGACAO
            and departure.data_inicio == departure.data_fim
        ):
            situation = CANCELED
        return situation

    @classmethod
    def set_data_fim_por_prorrogacao(cls, instance, exclude=[]):
        """
        Este método é responsável por setar a data fim a partir de prorrogação.
        """
        mensagem = "Tentando modificar data_fim de %s" % instance
        if not instance.alteracao and instance.possui_prorrogacao and instance.data_fim:
            pronlogation_date_end = None
            if instance.prorrogacao.exclude(pk__in=exclude).exists():
                pronlogation_date_end = (
                    instance.prorrogacao.exclude(pk__in=exclude)
                    .latest("data_fim")
                    .data_fim
                )
            afastamento = instance.instancia_modelo
            if afastamento.data_fim != pronlogation_date_end:
                log.info(
                    "%s - Data Fim %s mudou para %s em função de prorrogação."
                    % (
                        afastamento,
                        DateUtils.date_to_str(afastamento.data_fim),
                        (
                            DateUtils.date_to_str(pronlogation_date_end)
                            if pronlogation_date_end
                            else "----"
                        ),
                    )
                )
                afastamento.data_fim = (
                    pronlogation_date_end
                    if pronlogation_date_end
                    else afastamento.data_prevista
                )
                afastamento.update_date_end = False

                try:
                    with transaction.atomic():
                        afastamento.save()
                        notify_employee(sender=afastamento, mensagem=mensagem)
                except Exception as err:
                    log.exception(err)
                return True
        return False

    @classmethod
    def unset_data_fim_por_prorrogacao(cls, instance):
        """
        Este método é responsável por atualizar a data fim quando a prorrogação.
        """
        mensagem = ""
        afastamento = instance.__class__.objects.get(pk=instance.pk)
        data_fim = afastamento.data_fim
        if instance.alteracao is None and instance.possui_prorrogacao:
            data_fim = instance.data_prevista
        elif instance.possui_prorrogacao and instance.possui_alteracao is False:
            data_fim = instance.prorrogacao.latest("data_fim").data_fim

        if afastamento.data_fim != data_fim:
            mensagem = "%s - Data Fim %s mudou para %s em função de prorrogação." % (
                afastamento,
                DateUtils.date_to_str(afastamento.data_fim),
                DateUtils.date_to_str(data_fim),
            )
            log.info(mensagem)
            afastamento.data_fim = data_fim
            try:
                with transaction.atomic():
                    afastamento.save()
                    notify_employee(sender=afastamento, mensagem=mensagem)
            except Exception as err:
                log.exception(err)
                return False
        return True

    def configurar(self):
        """
        Este método deverá ser utilizado para aplicar valores diferentes do
        padrão.
            remunerado: default=True
            concessao_durante_estagio_prob: default=True
            suspensao_estagio_prob: default=True
            efetivo_exercicio: default=True
            suspensao_contagem_ferias: default=True
        """
        pass

    @property
    def license_health(self):
        value = False
        if hasattr(self, "licenca") and hasattr(self.licenca, "licencasaude"):
            value = True
        return value

    def get_texto(self):
        """
        Este método retorna o texto padrão para anotação.
        """
        return "Anotação de %s." % self.situation_unicode

    # -------------------------------VALIDATE-----------------------------------#
    def validate(self):
        """
        Este método reune as validações da classe.
        """
        self.validate_employee_active()
        if self.situation_unicode == "Recesso Forense - Membros":
            self.validate_periodo()
        elif self.situacao_funcional not in [
            "ATIVO_AFA_PARC_ESTUDAR",
            "ATIVO_AFA_SINDICANCIA_ADM",
        ]:
            self.validate_periodo()

        # self.validate_period_extension()
        self.validate_data_prevista()
        self.validate_save_servidor()
        self.validate_designation_exercise()
        self.validar_desconto_antiguidades()

        return super(BaseLicencaAfastamento, self).validate()

    def validar_desconto_antiguidades(self):

        if self.desconta_tempo == 1:  # 1 para descontar dias de afastamento
            if self.total_parcial == 1 and self.total_desconto == 0:
                raise Exception(
                    "O tempo total do desconto aparcial deve ser maior que 0 !!!"
                )
        else:
            self.total_parcial = 2  # 2 para ser um desconto total
            self.total_desconto = 0  # por ser um desconto total, não precisa informar quantos dias de afastamento/licença seram descontados

    def validate_employee_active(self):
        if not self.pk:
            termination_date = self.servidor.data_desligamento
            if (
                self.servidor.type_by_possession in ("REQ", "RFC", "RCM", "REX")
                and termination_date
                and termination_date >= datetime.now().date()
            ):
                """quando servidor é REQ, ele possui uma data de previsão de fim"""
                # FIXME: MODIFICAR ESTA ABORDAGEM QUANDO termination_date de REQ mudar
                termination_date = None

            # if not self.servidor.ativo:
            #     raise Exception('Não é possível lançar afastamento para servidor inativo.')
            elif self.servidor.data_exercicio > self.data_inicio:
                raise Exception("Não é possível lançar afastamento antes do exercício.")
            # elif termination_date and termination_date < self.data_inicio:
            #     raise Exception('Não é possível lançar afastamento após o desligamento.')
        return True

    def validate_designation_exercise(self):
        if (
            self.pk
            and self.designation_exercise.exclude(servidor=self.servidor).exists()
        ):
            raise Exception("Exercício não pertence ao servidor.")
        return True

    def nao_validar_data_prevista(self):
        """
        Este método contem regras para informar quando não haverá validação da data_prevista.
        """
        validar = False
        if (
            isinstance(self, FeriasAfastamento)
            or isinstance(self, FolgaAniversario)
            or isinstance(self, Viagem)
        ):
            validar = True
        elif self.possui_alteracao is False and self.pk and self.possui_prorrogacao:
            validar = True
        elif (
            (
                isinstance(self, LicencaDoencaPessoaFamilia)
                or isinstance(self, LicencaMaternidade)
                or isinstance(self, LicencaSaudeJuntaMedica)
                or isinstance(self, LicencaAdocao)
            )
            and self.prazo_concedido != self.prazo_solicitado
            and self.alteracao is None
        ):
            validar = True
        elif (
            isinstance(self, LicencaSaude3Dias) or isinstance(self, LicencaSaude30Dias)
        ) and self.alteracao is None:
            validar = True
        return validar

    def validate_data_prevista(self):
        """
        Este método realiza as validações relacionadas a data prevista.
        """
        if not self.nao_validar_data_prevista():
            if (
                self.alteracao
                and self.alteracao not in (CANCELED, SUSPENSAO)
                and self.data_fim == self.data_prevista
            ):
                raise Exception(
                    "Quando o campo Tipo Alteração for preenchido a Data Fim deve ser diferente da Data Prevista Fim."
                )
            elif self.alteracao is None and self.data_fim != self.data_prevista:
                raise Exception(
                    "Quando o campo Data Fim for diferente da Data Prevista o Tipo Alteração deve ser preenchida."
                )
            elif self.pk and not self.old_fields.get("data_prevista", None) is None:
                raise Exception(
                    "A Data Prevista não pode ser alterada. Utilize a Data Fim."
                )
        return True

    @classmethod
    def substitutions_conflicts(
        cls, departure=None, employee=None, date_start=None, date_end=None
    ):
        if (
            departure
            and departure.is_canceled
            or isinstance(departure, DesempenhoFuncao)
            or isinstance(departure, AtuacaoGrupoTrabalho)
        ):
            return MovimentacaoSubstituicao.objects.none()

        substitutions = MovimentacaoSubstituicao.objects.filter(
            Q(servidor=employee)
            & (
                Q(data_inicio__gte=date_start)
                | Q(data_fim__gte=date_start)
                | Q(data_fim=None)
            )
        )
        if date_end:
            substitutions = substitutions.exclude(data_inicio__gt=date_end)

        if departure and departure.pk and departure.designation_exercise.exists():
            substitutions = substitutions.exclude(
                designation_substitute__pk__in=departure.designation_exercise.values(
                    "pk"
                )
            )
        return substitutions

    def validate_substitutions(self):
        substitutions = BaseLicencaAfastamento.substitutions_conflicts(
            self, self.servidor, self.data_inicio, self.data_fim
        )
        if substitutions.exists():
            substitution = substitutions.latest("pk")
            raise Exception(
                "Substituição vigente %s a: %s - %s"
                % (
                    substitution.servidor,
                    substitution.servidor_substituido,
                    substitution,
                )
            )

    def validate_periodo(self):
        """
        Este método verifica se já existe algum afastamento vigente para o período de cadastro.
        """
        self.validate_substitutions()
        self.verifica_sobreposicao_periodo(
            servidor=self.servidor,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            pk=self.pk,
            cancelado=(True if self.alteracao in (CANCELED, SUSPENSAO) else False),
        )
        return True

    @deprecated
    def validate_period_extension(self):
        """
        :py:function:: validate_period_extension(self)

        This method validates if the period of the extension is in conflicts with another.

        :raises Exception: Message exception
        """
        for p in self.prorrogacao.filter():
            self.verifica_sobreposicao_periodo(
                servidor=self.servidor,
                data_inicio=p.data_inicio,
                data_fim=p.data_fim,
                pk=self.pk,
                cancelado=False,
            )
        return True

    # -------------------------------VALIDATE-SERVIDOR--------------------------#
    def validate_save_servidor(self):
        """
        Este método realiza a chamada das validações de save para servidores.
        """
        return True

    def validate_delete_servidor(self):
        """
        Este método realiza a chamada das validações de delete para servidores.
        """
        return True

    # -------------------------------VALIDATE-MEMBRO----------------------------#
    def validate_afastamento_iniciado(self):
        """
        Este método valida se o afastamento já foi iniciado.
        """
        if self._afastamento_iniciado():
            raise self.ErroAfastamentoIniciado()
        return True

    def validate_afastamento_finalizado(self):
        """
        Este método valida se o afastamento já foi finalizado.
        """
        if self._afastamento_finalizado():
            raise Exception("Afastamento finalizado.")
        return True

    def validate_data_inicio_maior_data_fim(self):
        """
        Este método valida se a data_inicio é maior que a data_fim.
        """
        if self.data_inicio > self.data_fim:
            raise Exception(
                "Data de início maior que data fim. Corrija a ordem das datas."
            )
        if self.data_inicio > self.data_prevista:
            raise Exception(
                "Data de início maior que data prevista. Corrija a ordem das datas."
            )
        if self.data_prevista > self.data_fim:
            raise Exception(
                "Data prevista maior que data fim. Corrija a ordem das datas."
            )
        return True

    def validate_delete(self):
        """
        Este método valida se o afastamento pode ser removido.
        """
        if self.substituicao.filter().exists():
            raise Exception(
                "É necessário remover a(as) substituição(ões) antes de apagar o afastamento."
            )
        elif self.inativacaocargomembro.filter().exists():
            raise Exception(
                "É necessário remover a(as) inativação(ões) antes de apagar o afastamento."
            )
        return True

    def validate_prazo_maximo(self):
        if hasattr(self, "prazo_maximo") and NewDateRange(
            self.data_inicio, self.data_fim
        ).days > self.prazo_maximo.get("days"):
            raise self.ErroPrazoMaximo(prazo_maximo=self.prazo_maximo.get("days"))
        return True

    def _afastamento_iniciado(self):
        """
        Este método verifica se o afastamento foi iniciado.
        """
        return self._iniciado(self.data_inicio, self.data_fim)

    def _afastamento_finalizado(self):
        """
        Este método verifica se o afastamento foi finalizado.
        """
        return self._finalizado(date_end=self.data_fim)

    @classmethod
    def verifica_sobreposicao_periodo(
        cls,
        servidor=None,
        data_inicio=None,
        data_fim=None,
        pk=None,
        cancelado=False,
        exclude=None,
        query_filter=None,
    ):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        exclude = exclude or []
        if servidor is None:
            raise Exception("Servidor é obrigatório.")
        if data_inicio is None:
            raise Exception("Data de início obrigatória.")
        sobreposicao = False
        if cancelado is False:
            query = Q(servidor=servidor) & (
                Q(data_inicio__gte=data_inicio)
                | Q(data_fim__gte=data_inicio)
                | Q(data_fim=None)
            )
            departures = cls.excluir_conflitos(
                servidor=servidor,
                query=BaseLicencaAfastamento.objects.filter(query).exclude(
                    estado=CANCELED
                ),
                data_inicio=data_inicio,
                data_fim=data_fim,
                pk=pk,
                cancelado=cancelado,
            )
            if not isinstance(departures, list) and len(exclude) > 0:
                departures = departures.exclude(pk__in=exclude)
            if pk and departures and not isinstance(departures, list):
                departures = departures.exclude(pk=pk)
            if not isinstance(departures, list) and query_filter:
                departures = departures.filter(query_filter)

            # Caso o servidorfor um estagiario ou residente
            # e se a data fim esta no dia 20 do mes 12 não sera
            #  execultado o teste   cls.match_date_range(data_inicio, data_fim, departures, pk)
            if not (
                (servidor and servidor.type_by_possession in ["RES", "EST"])
                and (data_fim and (data_fim.month == 12 and data_fim.day == 20))
            ):
                cls.match_date_range(data_inicio, data_fim, departures, pk)

            if cls in (AtuacaoGrupoTrabalho, DesempenhoFuncao):
                same_class = cls.objects.filter(query).exclude(estado=CANCELED)
                if pk:
                    same_class = same_class.exclude(pk=pk)
                cls.match_date_range(data_inicio, data_fim, same_class)
        return sobreposicao

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(estado=CANCELED)
            query = query.exclude(~Q(desempenhofuncao=None))
            query = query.exclude(~Q(atuacaogrupotrabalho=None))
            query = query.exclude(~Q(licenca__licencamandatoclassista=None))
            query = query.exclude(~Q(afastamento__afastamentooutroorgao=None))
            query = query.exclude(~Q(afastamento__afastamentoestudar=None))
        return query

    @classmethod
    def match_date_range(cls, date_start, date_end, departures, pk=None):
        """
        :py:function:: match_date_range(cls, date_start, date_end, departures)

        This method tries to match departures conflicting.
        Uses date_start and date_end for NewDateRange new and search for a departure intersect.

        :param BaseLicencaAfastamento departure: departure
        :return: situation
        :rtype: int
        """
        usufruct = None
        if pk:
            # Importando no início do arquivo é apresentado um erro de importação
            from rh.dayoff.models import Usufruct

            try:
                usufruct = Usufruct.objects.get(pk=pk)
            except Exception as err:
                return usufruct

        matched = False
        dr_new = NewDateRange(date_start, date_end)
        for departure in departures:
            dr_old = NewDateRange(departure.data_inicio, departure.data_fim)
            if usufruct:
                if usufruct.departure and usufruct.departure.pk != departure.pk:
                    if dr_new.intersect(dr_old).days > 0:
                        matched = True
                        raise Exception(
                            "Conflitou com o período: %s de %s a %s"
                            % (
                                departure,
                                DateUtils.date_to_str(departure.data_inicio),
                                (
                                    DateUtils.date_to_str(departure.data_fim)
                                    if departure.data_fim
                                    else ""
                                ),
                            )
                        )
            else:
                if dr_new.intersect(dr_old).days > 0:
                    matched = True
                    raise Exception(
                        "Conflitou com o período: %s de %s a %s"
                        % (
                            departure,
                            DateUtils.date_to_str(departure.data_inicio),
                            (
                                DateUtils.date_to_str(departure.data_fim)
                                if departure.data_fim
                                else ""
                            ),
                        )
                    )

        return matched

    def set_estado(self):
        """
        Este método realiza o set do campo estado.
        """
        # if self.estado != CANCELED:
        #     self.estado = SCHEDULED
        #     if self._afastamento_iniciado():
        #         self.estado = ACTIVE
        #     elif self._afastamento_finalizado():
        #         self.estado = FINISHED
        self.estado = self.situation_define(self)
        return True

    def set_data_prevista(self):
        """
        Este método realiza o set da data_prevista.
        """
        if (
            self.data_prevista is None
            and hasattr(self, "prazo_maximo")
            and self.data_inicio
        ):
            if "days" in list(self.prazo_maximo.keys()):
                self.data_prevista = (
                    (
                        self.data_inicio
                        + relativedelta(days=self.prazo_maximo.get("days") - 1)
                    )
                    if self.prazo_maximo.get("days") > 1
                    else self.data_inicio
                )
            if "months" in list(self.prazo_maximo.keys()):
                self.data_prevista = self.data_inicio + relativedelta(
                    months=self.prazo_maximo.get("months")
                )
            if "years" in list(self.prazo_maximo.keys()):
                self.data_prevista = self.data_inicio + relativedelta(
                    years=self.prazo_maximo.get("days")
                )
            self.data_fim = self.data_prevista

        if (
            self.possui_prazo_solicitado
            and self.possui_prorrogacao is False
            and self.possui_alteracao is False
        ):
            self.data_prevista = self.data_inicio + relativedelta(
                days=self.prazo_solicitado - 1
            )
            self.data_fim = self.data_inicio + relativedelta(
                days=self.prazo_solicitado - 1
            )
        if (
            self.possui_prazo_concedido
            and self.possui_prorrogacao is False
            and self.possui_alteracao is False
            and self.aprovacao == DEFERIDA
        ):
            self.data_fim = self.data_inicio + relativedelta(
                days=self.prazo_concedido - 1
            )

        if self.data_fim is None:
            self.data_fim = self.data_prevista
        return True

    def cancelamento(self, mandatory=False):
        """
        Este método realiza o cancelamento do afastamento.
        Ele apaga substituições/inativações e a situação funcional.
        """
        if self.is_canceled:
            try:
                self.delete_substitutions()
                self.delete_inativations()
            except Exception as err:
                if not mandatory:
                    raise err
            if self.situation_unicode == "Recesso Forense - Membros":
                SituacaoFuncional.delete_functional_status(
                    employee=self.servidor,
                    date_start=self.data_inicio,
                    date_end=self.data_inicio,
                    situation="NOT_FOUND",
                    instance=self,
                )
            else:
                SituacaoFuncional.delete_functional_status(
                    employee=self.servidor,
                    date_start=self.data_inicio,
                    date_end=self.data_inicio,
                    situation=self.situacao_funcional,
                    instance=self,
                )
        if (
            self.alteracao == CANCELED
            and self.estado == CANCELED
            and self.anotacao_geral
        ):
            try:
                self.anotacao_geral.delete()
            except Exception:
                log.info("Não apagou anotação de afastamento CANCELADO!")
        return True

    def delete_substitutions(self):
        for sub in self.substituicao.all():
            if hasattr(sub, "movimentacaosubstituicaomembro"):
                sub.movimentacaosubstituicaomembro.delete()
            else:
                sub.delete()

    def delete_inativations(self):
        for ina in self.inativacaocargomembro.all():
            ina.delete()

    def suspensao(self):
        if self.alteracao == SUSPENSAO:
            self.data_fim = self.data_prevista

    def set_situation_unicode(self):
        """
        :py:function:: set_situation_unicode(self)
        This method set situation_unicode
        """
        if not self.situation_unicode or self.situation_unicode == "Não encontrada!":
            try:
                self.situation_unicode = format_situacao_funcional(
                    self.situacao_funcional
                )
            except Exception as err:
                log.exception(err)
            if self.situacao_funcional == "ATIVO_LIC_SAUDE":
                self.situation_unicode = self._meta.verbose_name
            if not self.situacao_funcional:
                self.situation_unicode = "Não encontrada!"

    def set_annotation_class(self):
        """
        :py:function:: set_annotation_class(self)
        This method set set_annotation_class
        """
        try:
            self.annotation_class = "rh.anotacao.anotacaocarreira.Window"
            name = self.anotacao_classe.__name__
            if name == "AnotacaoAfastamento":
                self.annotation_class = "rh.anotacao.anotacaoafastamento.Window"
            elif name == "AnotacaoAusencia":
                self.annotation_class = "rh.anotacao.anotacaoausencia.Window"
            elif name == "AnotacaoLicenca":
                self.annotation_class = "rh.anotacao.anotacaolicenca.Window"
            elif name == "AnotacaoFerias":
                self.annotation_class = "rh.anotacao.anotacaoferias.Window"
            elif name == "AnotacaoFolgaCompensacao":
                self.annotation_class = "rh.anotacao.anotacaofolgacompensacao.Window"
            elif name == "AnotacaoFolgaEleitoral":
                self.annotation_class = "rh.anotacao.anotacaofolgaeleitoral.Window"
            elif name == "AnotacaoFolgaAniversario":
                self.annotation_class = "rh.anotacao.anotacaofolgaaniversario.Window"
            elif name == "AnotacaoViagem":
                self.annotation_class = "rh.anotacao.anotacaoviagem.Window"
            elif name == "AnotacaoRecesso":
                self.annotation_class = "rh.anotacao.anotacaorecesso.Window"
            elif name == "AnotacaoPlantao":
                self.annotation_class = "rh.anotacao.anotacaoplantao.Window"
            elif name == "AnotacaoBancoDeHoras":
                self.annotation_class = "rh.anotacao.anotacaobancodehoras.Window"
        except Exception as err:
            log.exception(err)

    @property
    def can_run_process(self):
        """Esta propriedade verifica retorna um boolean.
        True quando: status_change_date < today e estado for ativo, ou status_change_date igual a today e estado em
            ATIVO, FINALIZADO, CANCELADO
        False nos outros casos
        OBS: Lançamentos retroativos por padrão não vão executar processamento de exercícios.
        """
        today = datetime.now().date()
        if self.status_change_date:
            if self.status_change_date < today and self.estado == ACTIVE:
                return True
            elif self.status_change_date == today and self.estado in (
                ACTIVE,
                FINISHED,
                CANCELED,
            ):
                return True
        return False

    def set_status_change_date(self):
        """Este método definir status_change_date.
        Será marcado com a datetime.now() quando o estado mudar para ATIVO, FINALIZADO, CANCELADO.
        Caso seja um lançamento retroativo, será definido com data_fim."""
        old_status = self.old_fields.get("estado", self.estado)
        new_status = self.estado
        if isinstance(old_status, (list, tuple)):
            old_status = old_status[0]
        if old_status != new_status and new_status in (ACTIVE, FINISHED, CANCELED):
            today = datetime.now().date()
            if (
                old_status == FINISHED
                and new_status == CANCELED
                and self.status_change_date != today
            ):
                return
            self.status_change_date = today
            if (
                not self.pk
                and self.data_fim
                and self.data_fim < self.status_change_date
            ):
                self.status_change_date = self.data_fim

    @transaction.atomic
    def save(self, *args, **kargs):
        mandatory = kargs.get("mandatory", False)
        if "mandatory" in kargs:
            kargs.pop("mandatory")

        if "must_validate_employee_departured" in kargs:
            self.must_validate_employee_departured = kargs.pop(
                "must_validate_employee_departured"
            )
        self.configurar()
        if not self.pk:
            self.tipo = self.tipo_classe
        self.set_data_prevista()
        self.suspensao()
        self.set_estado()

        self.set_status_change_date()

        self.set_situation_unicode()
        self.set_annotation_class()
        old_fields = self.old_fields
        super(BaseLicencaAfastamento, self).save(*args, **kargs)
        self.cancelamento(mandatory=mandatory)
        notify(self, old_fields)

    def call_update_vacation_reference_from_employee(self):
        """
        :py:function:: call_update_vacation_reference_from_employee(self)

        This method calls Servidor.update_vacation_reference.

        """
        self.servidor.update_vacation_reference(departure=self)

    @transaction.atomic
    def delete(self, *args, **kargs):
        self.validate_delete()
        if not get_current_user().has_perm("afastamento.delete_baselicencaafastamento"):
            raise UserHasNotPermission("Apagar um afastamento.")
        # super(BaseLicencaAfastamento, self).delete(*args, **kargs)
        self.alteracao = CANCELED
        self.save()

    def anotacao(self, *args, **kargs):
        tipo = Publicacao.get_tipo(self.publicacao_movimentacao)
        if self.estado != SCHEDULED:
            if self.anotacao_geral is None:
                annotation = self.anotacao_classe.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=self.data_inicio,
                    data_inicio=self.data_inicio,
                    data_fim=self.data_fim,
                    texto=self.get_texto() + " " + (self.texto if self.texto else ""),
                    resumo=self.situation_unicode[0:150],
                )
                self.anotacao_classe.objects.filter(pk=annotation.pk).update(
                    indireto=True
                )
                self.anotacao_geral = annotation
            else:
                annotation = self.anotacao_classe.objects.get(pk=self.anotacao_geral.pk)
                annotation.publicacao = self.publicacao_movimentacao
                annotation.data_portaria_inicio = self.data_inicio
                if hasattr(annotation, "data_inicio"):
                    annotation.data_inicio = self.data_inicio
                if hasattr(annotation, "data_fim"):
                    annotation.data_fim = self.data_fim
                annotation.texto = (
                    self.get_texto() + " " + (self.texto if self.texto else "")
                )
                annotation.servidor = self.servidor
                annotation.tipo_documento = tipo
                annotation.indireto = False
                annotation.resumo = self.situation_unicode[0:150]
                annotation.save()
                self.anotacao_classe.objects.filter(pk=annotation.pk).update(
                    indireto=True
                )
        return self.anotacao_geral

    def anotacao_alteracao(self, *args, **kargs):
        """
        Este método realiza a anotação de alteração junto à anotação.
        """
        try:
            if (
                self.estado != SCHEDULED
                and self.alteracao
                and self.anotacao_geral
                and self.anotacao_classe.objects.filter(
                    pk=self.anotacao_geral.pk
                ).exists()
            ):
                anotacao_geral = self.anotacao_classe.objects.get(
                    pk=self.anotacao_geral.pk
                )
                anotacao_geral.texto = (
                    self.get_texto()
                    + " "
                    + self.get_texto_alteracao()
                    + " "
                    + (self.texto if self.texto else "")
                )
                anotacao_geral.indireto = False
                anotacao_geral.save()
                self.anotacao_classe.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
                self.anotacao_post_save()
        except Exception as err:
            log.exception(err)

    def get_tipo_texto_alteracao(self):
        """
        Este método retorna o texto do tipo da alteração.
        Ex:  self.ateracao == ALTERACAO: Altera-se a pedido(condicional) o afastamento(condicional).
        """
        alteracao = {
            REVOGACAO: "Revoga-se",
            ALTERACAO: "Altera-se a pedido",
            SUSPENSAO: "Suspende-se",
            INTERRUPCAO: "Interrompe-se",
            CANCELED: "Cancela-se",
        }
        texto = alteracao.get(self.alteracao)

        if hasattr(self, "afastamento"):
            texto += " o afastamento"
        elif hasattr(self, "licenca"):
            texto += " a licença"
        elif hasattr(self, "ausencia"):
            texto += " a ausência"
        elif hasattr(self, "recesso"):
            texto += " o recesso"
        elif hasattr(self, "viagem"):
            texto += " a viagem"
        elif hasattr(self, "folgacompensacao"):
            texto += " a folga compensação"
        elif hasattr(self, "folgaeleitoral"):
            texto += " a folga eleitoral"
        elif hasattr(self, "folgaaniversario"):
            texto += " a folga aniversário"
        elif hasattr(self, "atuacaogrupotrabalho"):
            texto += " a atuação em grupo de trabalho"
        elif hasattr(self, "desempenhofuncao"):
            texto += " a desempenho de função"
        elif hasattr(self, "plantao"):
            texto += " a plantão"
        elif hasattr(self, "bancodehoras"):
            texto += " a banco de horas"
        return texto

    def get_texto_alteracao(self):
        """
        Este método retorna o texto da alteração para anotação.
        """
        texto = ""
        if self.alteracao in (ALTERACAO, SUSPENSAO, INTERRUPCAO):
            """
            %(tipo_alteracao)s %(documento)s a partir de %(data_alteracao)s.
            """
            tipo_alteracao = self.get_tipo_texto_alteracao()
            documento = (
                ("através do documento %s" % self.publicacao_alteracao)
                if self.publicacao_alteracao
                else ""
            )
            data_alteracao = DateUtils.date_to_str(self.data_fim)
            if self.alteracao == INTERRUPCAO:
                data_alteracao = DateUtils.date_to_str(
                    self.data_fim + relativedelta(days=1)
                )
            if self.alteracao == SUSPENSAO:
                data_alteracao = DateUtils.date_to_str(self.data_inicio)
            with codecs.open(
                "%s/baselicencaafastamento_alteracao.txt" % templates.__path__[0],
                "r",
                "utf-8",
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "tipo_alteracao": tipo_alteracao,
                    "documento": documento,
                    "data_alteracao": data_alteracao,
                }
        elif self.alteracao == REVOGACAO:
            """
            %(tipo_alteracao)s %(documento)s a partir de %(data_alteracao)s.
            """
            tipo_alteracao = self.get_tipo_texto_alteracao()
            documento = (
                ("através do documento %s" % self.publicacao_alteracao)
                if self.publicacao_alteracao
                else ""
            )
            data_alteracao = DateUtils.date_to_str(self.data_fim)
            with codecs.open(
                "%s/baselicencaafastamento_revogacao.txt" % templates.__path__[0],
                "r",
                "utf-8",
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "tipo_alteracao": tipo_alteracao,
                    "documento": documento,
                    "data_alteracao": data_alteracao,
                }
        return texto

    def get_texto_modelo(self):
        """
        Este método retorna o texto do modelo.
        """
        return "------"

    def anotacao_post_save(self, *args, **kargs):
        """
        Executar somente após o post_save.
        A anotação deste modelo só poderá ser criada após a persistência do
        mesmo. Pois apenas desta forma saberemos se objeto é uma prorrogação
        ou não.
        """
        try:
            afastamento = self.__class__.objects.get(pk=self.pk)
            if (
                self.estado != SCHEDULED
                and afastamento.anota
                and afastamento.prorrogacao.exists()
            ):
                afastamento.anotacao()
                anotacao = afastamento.anotacao_classe.objects.get(
                    pk=afastamento.anotacao_geral.pk
                )
                text = anotacao.texto
                text += " " + afastamento.get_texto_prorrogacao()
                text += " " + self.get_texto_alteracao()
                afastamento.anotacao_classe.objects.filter(
                    pk=afastamento.anotacao_geral.pk
                ).update(texto=text)
        except Exception as err:
            log.exception(err)

    def get_texto_prorrogacao(self):
        """
        Este método retorna o texto de anotação para as prorrogações dos afastamentos.
        """
        prorrogacoes = self.prorrogacao.all()
        texto = ""
        for prorrogacao in prorrogacoes:
            documento = (
                (" através do documento %s" % prorrogacao.publicacao)
                if prorrogacao.publicacao
                else ""
            )
            texto += "Prorrogada de %s até %s%s.<br>" % (
                DateUtils.date_to_str(prorrogacao.data_inicio),
                DateUtils.date_to_str(prorrogacao.data_fim),
                documento,
            )
        return texto

    @classmethod
    def verify_active_vacation(cls, **kargs):
        """
        py:function:: verify_active_vacation(cls, **kargs)

        This method verifies at departures if exists a vacation active.

        :param dict kargs: Dict with keys: servidor, data_inicio, data_fim and pk
        :return: list of BaseLicencaAfastamento
        :rtype: boolean
        """
        return [
            base
            for base in BaseLicencaAfastamento.verifica_interseccao_periodo(
                kargs.get("servidor"), kargs.get("data_inicio"), kargs.get("data_fim")
            )
            if (
                base.instancia_modelo.__class__ == FeriasAfastamento
                and base.pk != kargs.get("pk", None)
                and NewDateRange(datetime.now().date(), datetime.now().date())
                .intersect(NewDateRange(base.data_inicio, base.data_fim))
                .days
                > 0
            )
        ]

    @classmethod
    def validate_alteracao_ferias(cls, departure, to_validade=True):
        """
        Este método é responsável por realizar as validações necessárias para alteração de férias.
        """
        valido = True
        message = "Validação para alteração de férias sem restrições."
        if not to_validade:
            message += (
                "Parâmetro validar %s. Não aplicou regras de validação!" % to_validade
            )
        elif departure.interrupt_vacation:
            if departure.alteracao in (SUSPENSAO, CANCELED):
                message = "%s está %s." % (departure, departure.get_estado_display())
                valido = False
            elif departure.servidor.membro:
                message = "Não realiza alteração de férias para membros."
                valido = False
            elif (
                len(
                    BaseLicencaAfastamento.verify_active_vacation(
                        servidor=departure.servidor,
                        data_inicio=departure.data_inicio,
                        data_fim=departure.data_fim,
                        pk=departure.pk,
                    )
                )
                > 0
            ):
                message = (
                    "Conflito de %s com férias iniciadas %s à %s. Não é possível colocar em época oportuna."
                    % (
                        departure,
                        DateUtils.date_to_str(departure.data_inicio),
                        DateUtils.date_to_str(departure.data_fim),
                    )
                )
                valido = False
            elif (
                isinstance(departure, LicencaDoencaPessoaFamilia)
                or isinstance(departure, LicencaMaternidade)
                or isinstance(departure, LicencaSaudeJuntaMedica)
                or isinstance(departure, LicencaAdocao)
            ) and departure.aprovacao in (NAO_INFORMADA, INDEFERIDA):
                message = "Não é possível alterar as férias para época oportuna quando a aprovação do afastamento for:"
                message += " Não informada ou Indeferida."
                valido = False
            elif departure.data_inicio is None or departure.data_fim is None:
                message = "Não é possível alterar as férias para época oportuna do servidor caso as datas de início"
                message += " e fim não sejam informadas."
                valido = False
            try:
                query_dates = Q(data_inicio__gte=departure.data_inicio)
                if departure.data_fim:
                    query_dates = Q(Q(data_fim__lte=departure.data_fim) & query_dates)
                departures_out = AfastamentoOutroOrgao.objects.filter(
                    Q(servidor=departure.servidor) & query_dates
                ).exclude(estado=CANCELED)
                if (
                    departures_out.filter(
                        Q(Q(transito_pela_folha=True) | Q(onus=ORIGEM))
                    ).exists()
                    or departures_out.filter(estado=FINISHED).exists()
                ):
                    message = "Não é possível alterar as férias para época oportuna se o servidor possuir afastamentos por"
                    message += "trânsito em folha/ônus origem ou estiver ENCERRADO."
                    valido = False
            except Exception as err:
                log.exception(err)
        else:
            valido = False
            message = "%s não altera férias." % departure.get_tipo_display()

        if message:
            log.info("%s - %s" % (message, valido))
        return valido

    @classmethod
    def alteracao_ferias(cls, **kargs):
        """
        Este método é responsável por alterar as férias que fazem intersecção com o afastamento
        para época oportuna.
        """
        from rh.ferias.models import AlteracaoPASU

        if len(kargs) == 1 and kargs.get("afastamento", False):
            kargs.update({"servidor": kargs.get("afastamento").servidor})
            kargs.update({"data_inicio": kargs.get("afastamento").data_inicio})
            kargs.update({"data_fim": kargs.get("afastamento").data_fim})
            kargs.update(
                {"instancia_verbose_name": kargs.get("afastamento")._meta.verbose_name}
            )
            kargs.update(
                {"publicacao": kargs.get("afastamento").publicacao_movimentacao}
            )

        if not BaseLicencaAfastamento.validate_alteracao_ferias(
            kargs.get("afastamento"), kargs.get("validar", True)
        ):
            return False
        return AlteracaoPASU.alteracao_ferias_epoca_oportuna(
            get_current_user(),
            kargs.get("afastamento"),
            kargs.get("servidor"),
            kargs.get("data_inicio"),
            kargs.get("data_fim"),
            kargs.get("instancia_verbose_name"),
            kargs.get("publicacao"),
        )

    @classmethod
    def interrupt(cls, employee, date_end, publication):
        """
        :py:function:: interrupt(cls, departure)

        This method interrupts departures. Except FeriasAfastamento.

        :param Servidor employee: employee
        :param date date_end: date_end
        :param Publicacao publication: publication
        """
        if employee and date_end and publication:
            for base in (
                BaseLicencaAfastamento.objects.filter(servidor=employee)
                .filter(
                    Q(data_inicio__lte=date_end)
                    & Q(Q(data_fim__gt=date_end) | Q(data_fim=None))
                )
                .exclude(~Q(feriasafastamento=None))
            ):
                try:
                    instance = base.instancia_modelo
                    instance.data_fim = date_end - relativedelta(days=1)
                    instance.alteracao = INTERRUPCAO
                    instance.publicacao_alteracao = publication
                    instance.save()
                except Exception as err:
                    log.exception(err)
                    print(err)

    @classmethod
    def mark_exercise_departure(cls):
        print(
            """Esta implementacao tentara marcar pelo menos um exercicio do membro como alterado por um afastamento ativo."""
        )
        query = (
            BaseLicencaAfastamento.objects.filter(servidor__tipo="M")
            .exclude(
                ~Q(licenca__licencamandatoclassista=None)
                | ~Q(desempenhofuncao=None)
                | ~Q(atuacaogrupotrabalho=None)
            )
            .exclude(estado__in=[FINISHED, CANCELED, SCHEDULED])
        )
        for base in query.order_by("estado"):
            instance = base.instancia_modelo
            work_locations_effective_exercise = (
                instance.servidor.work_locations_effective_exercise
            )
            if not work_locations_effective_exercise.exists():
                print(instance.pk)
                wa = instance.servidor.get_work_assignment(
                    date=instance.data_inicio - relativedelta(days=1)
                )
                if not wa.exists():
                    wa = instance.servidor._raw_locations(option=WORK_ASSIGNMENT)
                    if wa.exists():
                        wa = wa.filter(pk=wa.last().pk)
                for work_assignment in wa:
                    print(work_assignment.pk)
                    ServidorLotacao.objects.filter(pk=work_assignment.pk).update(
                        changed_by_departure=instance
                    )
                    if instance.servidor.work_locations_effective_exercise.exists():
                        print("GRAVOU")
                print("----------------")

    @classmethod
    def create_batch_recess(
        cls,
        start_date,
        end_date,
        user,
        insert_registry={},
        exclude_registry=[],
        employee_type="S",
        employee_status=True,
        task=None,
    ):
        """
        Este método cria recesso em Lote
        """
        start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date, "%d/%m/%Y").date()
        absences = BaseLicencaAfastamento.objects.filter(
            servidor__tipo=employee_type
        ).exclude(
            Q(estado=CANCELADO) | Q(data_fim__lte=(start_date - timedelta(days=1)))
        )
        date_range_absence = NewDateRange(start_date, end_date)

        excluded = []

        for absence in absences.order_by("-data_inicio"):
            days = date_range_absence.intersect(
                NewDateRange(absence.data_inicio, absence.data_fim)
            ).days
            if days > 0 and absence.servidor.matricula not in excluded:
                excluded.append(absence.servidor.matricula)

        employees = Servidor.objects.filter(tipo=employee_type, ativo=employee_status)
        total_excluded = exclude_registry + excluded
        employees_to_create = employees.exclude(matricula__in=total_excluded)

        count = 0
        err = []
        processed_registry = []
        for registry, values in insert_registry.items():
            period_to_create = NewDateRange(start_date, end_date)
            if registry not in total_excluded:
                for value in values:
                    new_range = NewDateRange(
                        datetime.strptime(value[0], "%d/%m/%Y"),
                        datetime.strptime(value[1], "%d/%m/%Y"),
                    )
                    period_to_create = period_to_create.subtraction(new_range)

                if period_to_create:
                    for new_start_date, new_end_date in period_to_create.ranges():
                        count += 1
                        returned = cls._create_recess(
                            employees.get(matricula=registry),
                            new_start_date,
                            new_end_date,
                            start_date.year,
                        )

                        if returned:
                            err.append(
                                "%s - %s"
                                % (employees.get(matricula=registry), returned)
                            )
                            count -= 1

                processed_registry.append(str(registry))

        for e in employees_to_create:
            if str(e.matricula) not in processed_registry:
                count += 1
                returned = cls._create_recess(e, start_date, end_date, start_date.year)
                if returned:
                    err.append("%s - ativo: %s: %s" % (e, e.is_ativo(), returned))
                    count -= 1

        data = datetime.today()
        filename = "demonstrativo_recessos_%s.txt" % (
            datetime.strftime(data, "%d_%m_%Y_%H_%M")
        )

        cache_path = os.path.join(settings.CACHE_PATH, "afastamento")
        file_path = os.path.join(cache_path, filename)
        if not os.path.exists(cache_path):
            os.makedirs(cache_path, 0o755)

        with open(file_path, "wt") as fd:
            fd.write(
                "Total de servidores sem os excluidos pelo ato: %s\n"
                % employees.count()
            )
            fd.write("Total de afastamentos criados: %s\n" % count)
            fd.write(
                "Servidores com pendencias(por outros afastamentos) devem ser removidos: %s\n\n"
                % len(excluded)
            )
            for e in employees:
                if e.matricula in excluded:
                    reason = []
                    for absence in e.get_afastamentos(start_date, end_date):
                        date_start = ""
                        if absence.baselicencaafastamento.data_inicio:
                            date_start = (
                                absence.baselicencaafastamento.data_inicio.strftime(
                                    "%d/%m/%Y"
                                )
                            )
                        if absence.baselicencaafastamento.data_fim:
                            date_end = absence.baselicencaafastamento.data_fim.strftime(
                                "%d/%m/%Y"
                            )
                        reason.append(
                            "Motivo: %s - %s a %s"
                            % (
                                absence.baselicencaafastamento.get_motivo_display(),
                                date_start,
                                date_end,
                            )
                        )
                    fd.write(
                        str(e.matricula)
                        + str(" - ")
                        + clear_to_ascii(e.pessoa_fisica.nome)
                        + " - "
                        + clear_to_ascii(reason[0])
                        + str("\n")
                    )

    @classmethod
    def _create_recess(cls, employee, start_date, end_date, year):
        # print 'CRIANDO RECESSO PARA O SERVIDOR.....', employee
        err = None
        try:
            recess = Recesso(
                servidor=employee,
                data_inicio=start_date,
                data_prevista=end_date,
                data_fim=end_date,
                ano=year,
            )
            recess.save()
        except Exception as e:
            err = e
        return err


class Afastamento(BaseLicencaAfastamento):
    class Meta:
        verbose_name = "Afastamento"
        db_table = "afastamento_afastamento"

    anotacao_classe = rh_models.AnotacaoAfastamento

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada(
                txt="Documento Início não encontrado."
            )
        return True

    def validate_data_vigencia(self):
        if self.publicacao_movimentacao.data_vigencia is None:
            raise self.ErroVigenciaNaoEncontrada()
        return True

    def validate(self):
        self.validate_publicacao()
        #        self.validate_data_vigencia()
        return super(Afastamento, self).validate()


class Licenca(BaseLicencaAfastamento):
    class Meta:
        verbose_name = "Licença"
        db_table = "afastamento_licenca"

    anotacao_classe = rh_models.AnotacaoLicenca

    def validate_publicacao(self):
        return True

    def validate(self):
        self.validate_publicacao()
        return super(Licenca, self).validate()

    def get_texto_modelo(self):
        return "Licença"


class Ausencia(BaseLicencaAfastamento):
    class Meta:
        verbose_name = "Ausência"
        db_table = "afastamento_ausencia"

    prazo_maximo = {"days": 1}

    anotacao_classe = rh_models.AnotacaoAusencia

    def validate(self):
        return super(Ausencia, self).validate()


class FeriasAfastamento(BaseLicencaAfastamento):
    """
    Usufruto de férias.
    """

    anotacao_classe = rh_models.AnotacaoFerias

    class Meta:
        verbose_name = "Férias"
        db_table = "afastamento_feriasafastamento"

    def configurar(self):
        self.interrupt_vacation = False

    @property
    def situacao_funcional(self):
        return "ATIVO_FERIAS"

    def validate(self):
        return super(FeriasAfastamento, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s em razão de usufruto de férias.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/feriasafastamento.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from vacation.
        """
        return True

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        servidor = kargs.get("servidor", None)
        if query:
            if servidor and servidor.membro:
                query = query.exclude(~Q(afastamento__afastamentoestudar=None))
                query = query.exclude(~Q(afastamento__afastamentooutroorgao=None))
            else:
                query = query.exclude(
                    afastamento__afastamentooutroorgao__transito_pela_folha=True
                )
                query = query.exclude(afastamento__afastamentooutroorgao__onus=1)
        query = query.exclude(
            afastamento__afastamentooutroorgao__estado__in=(FINISHED, CANCELED)
        )
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 1
        kargs.update({"mandatory": True})
        super(FeriasAfastamento, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class Viagem(BaseLicencaAfastamento):
    """
    Viagem à serviço.
    """

    class Meta:
        verbose_name = "Viagem"
        db_table = "afastamento_viagem"

    anotacao_classe = rh_models.AnotacaoViagem

    @property
    def situacao_funcional(self):
        return "ATIVO_VIAGEM"

    def configurar(self):
        self.interrupt_vacation = False

    def validate(self):
        return super(Viagem, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para viagem à serviço.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/viagem.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "viagem"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(~Q(viagem=None))
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 5
        super(Viagem, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from viagem.
        """
        return True


# @auditable('data_inicio', 'data_fim', 'publicacao_fim')
class Recesso(BaseLicencaAfastamento):
    """
    Usufruto recesso natalino.
    """

    anotacao_aquisicao = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usufrutorecesso",
        verbose_name="Anotação de Aquisição",
    )
    ano = models.CharField(max_length=9, verbose_name="Ano do Recesso", default="")

    class Meta:
        verbose_name = "Recesso"
        db_table = "afastamento_recesso"

    anotacao_classe = rh_models.AnotacaoRecesso

    @property
    def situacao_funcional(self):
        return "ATIVO_RECESSO"

    def validate(self):
        return super(Recesso, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período de
        %(data_inicio)s à %(data_fim)s em razão de usufruto de folgas
        referente ao plantão no recesso natalino de %(ano_recesso)s.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            ano_recesso = self.ano
            with codecs.open(
                "%s/recesso.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                    "ano_recesso": ano_recesso,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "recesso"

    def valide_year_length(self):
        if len(self.year) > 5:
            raise Exception("O tamanho do ano não pode ser maior que 4 dígitos.")
        return True

    def validade(self):
        self.valide_year_length()
        return super(Recesso, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 3
        super(Recesso, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from recesso.
        """
        return True


@auditable("data_inicio", "data_fim", "publicacao_fim")
class FolgaCompensacao(BaseLicencaAfastamento):
    """
    Usufruto Folga Compensação.
    """

    anotacao_aquisicao = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usufrutofolgacompensacao",
        verbose_name="Anotação de Aquisição",
    )

    class Meta:
        verbose_name = "Folga Compensação"
        db_table = "afastamento_folgacompensacao"

    anotacao_classe = rh_models.AnotacaoFolgaCompensacao

    @property
    def situacao_funcional(self):
        return "ATIVO_FOLGA_COMPENSACAO"

    def validate(self):
        return super(FolgaCompensacao, self).validate()

    def get_texto(self):
        """
        O(A) %(texto_servidor)s %(servidor)s ausentou-se no período de %(data_inicio)s à %(data_prevista)s
        em razão de usufruto de folga compensação %(documento)s.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            documento = "através do documento %s" % self.publicacao_movimentacao
            with codecs.open(
                "%s/folgacompensacao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                    "documento": documento,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "folga compensação"

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 2
        super(FolgaCompensacao, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from folga compensação.
        """
        return True


@auditable("data_inicio", "data_fim", "publicacao_fim")
class BancoDeHoras(BaseLicencaAfastamento):
    """
    Usufruto Folga Compensação.
    """

    class Meta:
        verbose_name = "Folga Compensação"
        db_table = "afastamento_bancodehoras"

    anotacao_classe = rh_models.AnotacaoBancoDeHoras

    @property
    def situacao_funcional(self):
        return "ATIVO_USU_BANCO_DE_HORAS"

    def validate(self):
        return super(BancoDeHoras, self).validate()

    def get_texto(self):
        """
        O(A) %(texto_servidor)s %(servidor)s ausentou-se no período de %(data_inicio)s à %(data_prevista)s
        em razão de usufruto de folga compensação %(documento)s.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            documento = "através do documento %s" % self.publicacao_movimentacao
            with codecs.open(
                "%s/usufrutobancodehoras.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                    "documento": documento,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "banco de horas"

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 2
        super(BancoDeHoras, self).save(*args, **kargs)


@auditable("data_fim", "publicacao_fim")
class FolgaEleitoral(BaseLicencaAfastamento):
    """
    Usufruto de folga eleitoral.
    """

    anotacao_aquisicao = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usufrutofolgaeleitoral",
        verbose_name="Anotação de Aquisição",
    )
    ano = models.PositiveIntegerField(verbose_name="Ano de Eleição")
    turno = models.PositiveIntegerField(
        choices=Choice.get_choices_for("rh", "TURNO_ELEITORAL"), default=1
    )

    class Meta:
        verbose_name = "Folga Eleitoral"
        db_table = "afastamento_folgaeleitoral"

    anotacao_classe = rh_models.AnotacaoFolgaEleitoral

    @property
    def situacao_funcional(self):
        return "ATIVO_FOLGA_ELEITORAL"

    def validate(self):
        return super(FolgaEleitoral, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período de
        %(data_inicio)s à %(data_fim)s em razão de usufruto de folgas
        referente à convocação eleitoral no ano de %(ano)s no %(turno)s turno.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            ano = self.ano
            turno = self.get_turno_display()
            with codecs.open(
                "%s/folgaeleitoral.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                    "ano": ano,
                    "turno": turno,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "folga eleitoral"

    @transaction.atomic
    def save(self, *args, **kargs):
        super(FolgaEleitoral, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from folga eleitoral.
        """
        return True


class FolgaAniversario(BaseLicencaAfastamento):
    """
    Usufruto de folga eleitoral.
    """

    anotacao_aquisicao = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usufrutofolgaaniversario",
        verbose_name="Anotação de Aquisição",
    )
    data_referencia = models.DateField(verbose_name="Data de referência")
    ano = models.IntegerField()

    anotacao_classe = rh_models.AnotacaoFolgaAniversario
    prazo_maximo = {"days": 1}

    class Meta:
        verbose_name = "Folga Aniversário"
        db_table = "afastamento_folgaaniversario"

    @property
    def situacao_funcional(self):
        return "ATIVO_FOLGA_ANIVERSARIO"

    def set_data_prevista(self):
        self.data_prevista = self.data_inicio
        self.data_fim = self.data_inicio

    def validate_periodo_maximo_marcacao(self):
        self.data_referencia = datetime(
            self.ano,
            self.servidor.pessoa_fisica.data_nascimento.month,
            self.servidor.pessoa_fisica.data_nascimento.day,
        ).date()
        data_limite = (self.data_referencia + relativedelta(years=1)) - relativedelta(
            days=1
        )
        if self.data_fim > (
            (self.data_referencia + relativedelta(years=1)) - relativedelta(days=1)
        ):
            raise self.ErroPrazoMaximo(
                txt="Prazo máximo de marcação do usufruto é de 1 ano. E deve ser até o dia %s."
                % DateUtils.date_to_str(data_limite)
            )
        if self.data_fim < self.data_referencia:
            raise Exception(
                "Marcação de folga deve ser a partir da data de aniversário %s"
                % DateUtils.date_to_str(self.data_referencia)
            )
        return True

    def validate_ano(self):
        validate = FolgaAniversario.objects.filter(
            servidor=self.servidor, ano=self.ano
        ).exclude(estado=CANCELED)
        if self.pk is not None:
            validate = validate.exclude(pk=self.pk)
        if validate.exists():
            raise Exception("Apenas uma folga é permitida por ano.")

    def get_texto(self):
        """
        O(A) %(texto_servidor)s %(servidor)s ausentou-se no período de %(data_inicio)s à %(data_prevista)s em
        razão de usufruto de folga aniversário do dia %(data_referencia)s.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            with codecs.open(
                "%s/folgaaniversario.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "ano": self.ano,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "folga eleitoral"

    @transaction.atomic
    def save(self, *args, **kargs):
        super(FolgaAniversario, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from folga aniversário.
        """
        return True


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AtuacaoGrupoTrabalho(BaseLicencaAfastamento):
    """
    Atuação em Grupo de Trabalho.
    """

    class Meta:
        verbose_name = "Atuação Grupo de Trabalho"
        db_table = "afastamento_atuacaogrupotrabalho"

    anotacao_classe = rh_models.AnotacaoCarreira

    def configurar(self):
        self.interrupt_vacation = False

    @property
    def situacao_funcional(self):
        return "ATIVO_ATUACAO_GRUPO_TRAB"

    def validate(self):
        return super(AtuacaoGrupoTrabalho, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 9
        # self.anota = False
        super(AtuacaoGrupoTrabalho, self).save(*args, **kargs)

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        kargs.update({"query": []})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class DesempenhoFuncao(BaseLicencaAfastamento):
    """
    Desempenho de Função.
    """

    class Meta:
        verbose_name = "Desempenho de Função"
        db_table = "afastamento_desempenhofuncao"

    anotacao_classe = rh_models.AnotacaoCarreira

    def configurar(self):
        self.interrupt_vacation = False

    @property
    def situacao_funcional(self):
        return "ATIVO_DESEMPENHO_FUNCAO"

    def validate(self):
        return super(DesempenhoFuncao, self).validate()

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        kargs.update({"query": []})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 6
        # self.anota = False
        super(DesempenhoFuncao, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class Plantao(BaseLicencaAfastamento):
    """
    Usufruto de Plantão.
    """

    anotacao_aquisicao = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usufrutoplantao",
        verbose_name="Anotação de Aquisição",
    )

    class Meta:
        verbose_name = "Plantão"
        db_table = "afastamento_plantao"

    anotacao_classe = rh_models.AnotacaoPlantao

    @property
    def situacao_funcional(self):
        return "ATIVO_PLANTAO"

    def validate(self):
        return super(Plantao, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período de
        %(data_inicio)s à %(data_fim)s em razão de usufruto de folgas
        referente ao plantão.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/plantao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "plantão"

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 4
        super(Plantao, self).save(*args, **kargs)

    def validate_substitutions(self):
        """
        :py:function:: validate_substitutions(self)

        This method overwrite validate_substitutions to avoid error from plantão.
        """
        return True


class CIDCode(models.Model):
    """
    Model que representa os códigos da CID-10 (Classificação Estatística Internacional
    de Doenças e Problemas Relacionados à Saúde).
    """

    code = models.CharField(
        verbose_name="Códigos da CID-10",
        max_length=50,
    )

    class Meta:
        verbose_name = "CIDCode"
        verbose_name_plural = "CIDCodes"

    def __str__(self):
        return self.code


class CID(models.Model):
    """
    Model que representa uma CID (Classificação Internacional de Doenças) com base na CID-10.
    """

    chapter = models.CharField(
        verbose_name="Capítulo da CID",
        max_length=50,
    )
    code = models.CharField(
        verbose_name="Código da CID",
        max_length=50,
    )
    description = models.CharField(
        verbose_name="Descrição da CID",
        max_length=244,
    )
    cid_code = models.ManyToManyField(
        CIDCode,
        verbose_name="Códigos da CID-10",
        related_name="cids",
    )

    class Meta:
        verbose_name = "CID"
        verbose_name_plural = "CIDs"

    @property
    def codigos_cid(self):
        codigos = ""
        for name in self.cid_code.all():
            if not codigos:
                codigos += str(name)
            else:
                codigos += "|" + str(name)
        return codigos

    def __str__(self):
        return f"{self.chapter}-{self.code} | {self.description} | {self.codigos_cid}"


class HealthCertificate(AuditTimestampModel):
    healthcare_professional = models.ForeignKey(
        ProfissionalSaude,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="healthcertificate",
        verbose_name="Profissional Saúde",
    )
    cid = models.CharField(max_length=4, null=True, blank=True, verbose_name="CID")
    days_granted = models.IntegerField(verbose_name="Dias concedidos")

    def __str__(self):
        return "%s - %s" % (self.cid, self.healthcare_professional)


class LicencaSaude(Licenca):
    atestado_medico = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="atestado_licensa_saude",
    )
    health_certificate = models.ManyToManyField(
        HealthCertificate,
        verbose_name="Atestados",
        related_name="health_license",
    )
    consequence_of = models.ForeignKey(
        "Licenca",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="license_consequence_of",
    )
    prazo_solicitado = models.IntegerField(verbose_name="Prazo Solicitado")
    prazo_concedido = models.IntegerField(
        null=True, blank=True, verbose_name="Prazo Concedido"
    )
    aprovacao = models.PositiveIntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_APROVACAO"), default=NAO_INFORMADA
    )
    codigo_internacional_doenca = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="CID"
    )
    profissional_saude = models.ForeignKey(
        ProfissionalSaude,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="licencasaude",
        verbose_name="Profissional Saúde",
    )
    acidente_transito = models.IntegerField(
        choices=Choice.get_choices_for("rh", "ACIDENTE_TRANSITO"), blank=True, null=True
    )
    related_work = models.BooleanField(default=False)
    process_rectification = models.ForeignKey(
        "rh.LegalProcess",
        on_delete=models.SET_NULL,
        verbose_name="Processo de Retificação",
        related_name="health_license",
        null=True,
        blank=True,
    )
    classification = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "HEALTH_LICENSE_CLASSIFICATION"),
        blank=True,
    )
    cid = models.ForeignKey(
        CID,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="cid",
        verbose_name="CID-10",
        help_text="CID-10 - Classificação Internacional de Doenças versão 10",
    )

    class Meta:
        verbose_name = "Licença Saúde"
        db_table = "afastamento_licencasaude"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_SAUDE"

    def validate(self):
        self.valdiate_active_vacation()
        return super(LicencaSaude, self).validate()

    def valdiate_active_vacation(self):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        cancelado = True if self.alteracao in (CANCELED, SUSPENSAO) else False
        verify_active_vacation = BaseLicencaAfastamento.verify_active_vacation(
            servidor=self.servidor,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            pk=self.pk,
            cancelado=cancelado,
        )
        if not cancelado and len(verify_active_vacation) > 0:
            raise self.ExceptionBasePeriodo(
                txt="Licença conflitando com férias iniciadas: %s de %s a %s. Não é possível colocar para época oportuna."
                % (
                    verify_active_vacation[0],
                    DateUtils.date_to_str(verify_active_vacation[0].data_inicio),
                    (
                        DateUtils.date_to_str(verify_active_vacation[0].data_fim)
                        if verify_active_vacation[0].data_fim
                        else ""
                    ),
                )
            )
        return True

    def validate_prazo_maximo(self):
        """
        Incluir validação em que sinalize prazo maximo de dias baseado em prazo_maximo.
        """
        if (
            hasattr(self, "prazo_maximo")
            and (
                self.prazo_solicitado > self.prazo_maximo.get("days")
                or NewDateRange(self.data_inicio, self.data_fim).days
                > self.prazo_maximo.get("days")
            )
        ) and not self.possui_prorrogacao:
            raise self.ErroPrazoMaximo(prazo_maximo=self.prazo_maximo.get("days"))
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        if self.prazo_solicitado is None and hasattr(self, "prazo_maximo"):
            self.prazo_solicitado = self.prazo_maximo.get("days")
        super(LicencaSaude, self).save(*args, **kargs)

    def get_texto_modelo(self):
        return "licença para tratamento de saúde"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        # employee = kargs.get('servidor', None)
        # if query and employee and not employee.membro:
        #     query = query.exclude(~Q(feriasafastamento=None))
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaSaude3Dias(LicencaSaude):
    class Meta:
        verbose_name = "Licença Saúde Atestado Médico"
        db_table = "afastamento_licencasaude3dias"

    #  TODO: inserir a configuração de dias
    @property
    def prazo_maximo(self):
        cfg = Configuration.get_or_create("afastamento")
        prazo = int(cfg.get("prazo_maximo_licenca_atestado", 3) or 0)
        return {"days": prazo}

    def validate(self):
        """
        Incluir validação em que sinalize prazo maximo de 3 dias.
        """
        self.validate_prazo_maximo()
        return super(LicencaSaude3Dias, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.prazo_concedido = self.prazo_solicitado
        self.aprovacao = DEFERIDA
        super(LicencaSaude3Dias, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se por %(prazo_solicitado)s
        dia(s) a partir de %(data_inicio) até %(data_prevista) em razão de
        tratamento de saúde.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            prazo_solicitado = self.prazo_solicitado
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/licencasaude3dias.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "prazo_solicitado": prazo_solicitado,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaSaude30Dias(LicencaSaude):
    class Meta:
        verbose_name = "Licença Saúde de até 30 Dias"
        db_table = "afastamento_licencasaude30dias"

    prazo_maximo = {"days": 30}

    def validate(self):
        """
        Incluir validação em que sinalize prazo maximo de 3 dias.
        """
        self.validate_prazo_maximo()
        if not self.servidor.membro:
            raise Exception("Licença até 30 dias é exclusiva para membros.")
        return super(LicencaSaude30Dias, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.prazo_concedido = self.prazo_solicitado
        self.aprovacao = DEFERIDA
        super(LicencaSaude30Dias, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se por %(prazo_solicitado)s
        dia(s) a partir de %(data_inicio) até %(data_prevista) em razão de
        tratamento de saúde.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            prazo_solicitado = self.prazo_solicitado
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/licencasaude30dias.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "prazo_solicitado": prazo_solicitado,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaSaudeHoras(LicencaSaude):

    hours = models.IntegerField(verbose_name="Quatidade de horas em licença", null=True)

    class Meta:
        verbose_name = "Licença Saúde Horas"
        db_table = "afastamento_licencasaudehoras"

    prazo_maximo = {"days": 1}

    def validate(self):
        """
        Validações específicas do modelo
        """
        self.validate_prazo_maximo()
        return super(LicencaSaudeHoras, self).validate()

    def set_data_prevista(self):
        """
        Este método realiza o set da data_prevista.
        """
        self.data_fim = self.data_inicio
        self.data_prevista = self.data_inicio

        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        self.prazo_concedido = self.prazo_solicitado
        self.aprovacao = DEFERIDA
        super(LicencaSaudeHoras, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se por %(hours)s
        horas(s) a partir de %(data_inicio) até %(data_prevista) em razão de
        tratamento de saúde.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            hours = self.hours
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/licencasaudehoras.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "hours": hours,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "licença para tratamento de saúde em horas"


class BaseLicencaSaudeJuntaMedica(LicencaSaude):
    """
    - Licenças superiores devem ir pra Junta Medica (criar campo com a informação
        da data do envio, do retorno, se homologada (deferida ou indeferida) pela Junta,
        prazo pedido e prazo concedido pela Junta, inclusão do pedido, atestado e parecer da
        Junta escaneado, se prorrogada a licença após o prazo de vencimento com
        nova perícia, codigo da doença):
        -data envio para junta;
        -data retorno da junta;
        -deferida/indeferida da junta;
        -prazo pedido para junta;
        -prazo concedido pela junta;
        -inclusão de pedido para junta;
        -atestado da junta;
        -parecer da junta escaneado;
        -se prorrogada a licença após o prazo de vencimento com
        nova perícia, codigo da doença)

    """

    data_envio = models.DateField(
        null=True, blank=True, verbose_name="Data envio Junta"
    )
    data_retorno = models.DateField(
        null=True, blank=True, verbose_name="Data retorno Junta"
    )
    documento_solicitacao = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documento_avaliacao_junta_medica",
    )
    atestado_junta_medica = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="atestado_avaliacao_junta_medica",
    )
    documento = models.ManyToManyField(
        Arquivo,
        verbose_name="Documentação Complementar",
        symmetrical=False,
        related_name="documentos_licencasaudejunta",
        blank=True,
    )
    parecer = models.TextField(verbose_name="Parecer", null=True, blank=True)

    prazo_minimo = 4

    class Meta:
        verbose_name = "BaseLicencaAfastamentoJuntaMedica"
        db_table = "afastamento_baselicsaudejuntamed"

    def configurar(self):
        if NewDateRange(self.data_inicio, self.data_fim).days > 120:
            self.suspensao_estagio_prob = True

    def validate_prazo_minimo(self):
        """
        Incluir validação em que sinalize prazo mínimo de 4 dias.
        """
        if (
            not isinstance(self, LicencaDoencaPessoaFamilia)
            and not isinstance(self, LicencaMaternidade)
            and not isinstance(self, LicencaSaudeJuntaMedica)
            and not isinstance(self, LicencaAdocao)
        ) and (
            self.prazo_solicitado < self.prazo_minimo
            or NewDateRange(self.data_inicio, self.data_fim).days < self.prazo_minimo
        ):
            raise self.ErroPrazoMinimo()
        return True

    def validate_deferida(self):
        if self.aprovacao == DEFERIDA and (
            self.prazo_solicitado is None or self.prazo_solicitado == 0
        ):
            raise Exception(
                "O prazo solicitado deve ser informado quando a licença for deferida."
            )
        elif self.aprovacao == DEFERIDA and (
            self.prazo_concedido is None or self.prazo_concedido == 0
        ):
            raise Exception(
                "O prazo concedido deve ser informado quando a licença for deferida."
            )
        return True

    def validate(self):
        """
        Incluir validação em que sinalize prazo mínimo de 4 dias.
        """
        self.validate_deferida()
        return super(BaseLicencaSaudeJuntaMedica, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        if self.aprovacao == INDEFERIDA:
            self.alteracao = SUSPENSAO
        super(BaseLicencaSaudeJuntaMedica, self).save(*args, **kargs)

    def get_data_fim_prazo_concedido(self):
        return DateUtils.date_to_str(
            (self.data_inicio + relativedelta(days=self.prazo_concedido - 1))
            if self.possui_prazo_concedido
            else self.data_fim
        )

    def get_deferimento(self):
        deferimento = ""
        if self.aprovacao == DEFERIDA:
            deferimento = """<p>%s pela Junta Médica Oficial pedido de %s por %s dias, no período de %s à %s.</p>"""
            deferimento = deferimento % (
                self.get_aprovacao_display(),
                self.get_texto_modelo(),
                self.prazo_concedido,
                DateUtils.date_to_str(self.data_inicio),
                self.get_data_fim_prazo_concedido(),
            )
        elif self.aprovacao == INDEFERIDA:
            deferimento = """<p>%s pela Junta Médica Oficial pedido de %s.</p>""" % (
                self.get_aprovacao_display(),
                self.get_texto_modelo(),
            )
        return deferimento

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se por %(prazo_solicitado)s
        dia(s) a partir de %(data_inicio) até %(data_prevista) em razão de
        tratamento de saúde.
        """
        texto = ""
        try:
            servidor = self.servidor.pessoa_fisica
            prazo_solicitado = self.prazo_solicitado
            data_inicio = DateUtils.date_to_str(self.data_inicio)
            data_prevista = (
                DateUtils.date_to_str(self.data_prevista)
                if self.data_prevista
                else "data prevista de fim não informada"
            )
            with codecs.open(
                "%s/licencasaudejunta.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "servidor": servidor,
                    "motivo": self.get_texto_modelo(),
                    "prazo_solicitado": prazo_solicitado,
                    "data_inicio": data_inicio,
                    "data_prevista": data_prevista,
                    "deferimento": self.get_deferimento(),
                }
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_modelo(self):
        return "licença para tratamento de saúde"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaSaudeJuntaMedica(BaseLicencaSaudeJuntaMedica):
    class Meta:
        verbose_name = "Licença Saúde Junta Médica"
        db_table = "afastamento_licsaudejuntamed"

    def get_texto_modelo(self):
        return "licença para tratamento de saúde"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        query = kargs.get("query", [])
        # employee = kargs.get('servidor', None)
        # if query and employee and not employee.membro:
        #     query = query.exclude(~Q(feriasafastamento=None))
        # kargs.update({'query': query})
        return query


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaDoencaPessoaFamilia(BaseLicencaSaudeJuntaMedica):
    """
    - Campo que indique o dependente acompanhado (conjuge ou companheiro, pais,
        filhos, padrasto, madrasta, enteado ou dependente que viva às expensas
        do servidor e conste de seu assentamento funcional);
    - A patologia e o prazo;
    """

    acompanhado = models.ForeignKey(
        PessoaFisica,
        on_delete=models.PROTECT,
        related_name="licencadoenca",
        verbose_name="Acompanhado",
    )
    grau_parentesco = models.IntegerField(
        default=1,
        choices=list(GRAU_PARENTESCO_DOENCA_CHOICES.items()),
        verbose_name="Tipo de Parentesco",
    )

    class Meta:
        verbose_name = "Licença Doença Pessoa da Família"
        db_table = "afastamento_licencadoenca"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_DOENCA"

    def configurar(self):
        if NewDateRange(self.data_inicio, self.data_fim).days > 90:
            self.suspensao_estagio_prob = True
        if NewDateRange(self.data_inicio, self.data_fim).days > 365:
            self.suspensao_contagem_ferias = True

    def get_texto_modelo(self):
        return "licença em razão de doença em pessoa da família"

    def validate(self):
        if not self.acompanhado:
            raise Exception("É necessário incluir um acompanhado.")
        return super(LicencaDoencaPessoaFamilia, self).validate()


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaMaternidade(BaseLicencaSaudeJuntaMedica):
    """
    - Incluir campo específico em que deve constar o nome da criança;
    - Campo data de nascimento;
    - Limitar em 180 dias
    """

    data_parto = models.DateField(
        null=True, blank=True, verbose_name="Data Parto/Aborto"
    )
    crianca = models.ForeignKey(
        PessoaFisica,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="licencamaternidade",
        verbose_name="Filho(a)",
    )
    natimorto = models.BooleanField(
        default=False, verbose_name="Natimorto/Neomorto ou Aborto"
    )

    prazo_maximo = {"days": 180}

    class Meta:
        verbose_name = "Licença Maternidade"
        db_table = "afastamento_licencamaternidade"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_MATERNIDADE"

    def validate(self):
        super(LicencaMaternidade, self).validate()
        self.validate_prazo_maximo()
        return True

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(~Q(recesso=None))
            query = query.exclude(~Q(afastamento__afastamentooutroorgao=None))
        kargs.update({"query": query})
        return BaseLicencaSaudeJuntaMedica.excluir_conflitos(**kargs)

    def get_texto_modelo(self):
        return "licença maternidade"

    def save(self, *args, **kargs):
        if self.natimorto:
            self.prazo_maximo = {"days": 30}
        super(LicencaMaternidade, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaAdocao(BaseLicencaSaudeJuntaMedica):
    """
    - Incluir campo específico em que deve constar o nome da criança;
    - Informação do documento hábil que comprove a tutoria (termo de guarda judicial ou termo de concretização da adoção)
    """

    crianca = models.ForeignKey(
        PessoaFisica,
        null=True,
        verbose_name="Adotado(a)",
        on_delete=models.PROTECT,
        related_name="licencaadocao",
    )

    prazo_maximo = {"days": 180}

    class Meta:
        verbose_name = "Licença Adoção"
        db_table = "afastamento_licencaadocao"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_ADOCAO"

    def validate(self):
        self.validate_prazo_maximo()
        return super(LicencaAdocao, self).validate()

    def get_texto_modelo(self):
        return "licença tutoria/adoção"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaAfastamentoConjuge(Licenca):
    conjuge = models.ForeignKey(
        PessoaFisica,
        null=True,
        verbose_name="Cônjuge",
        on_delete=models.PROTECT,
        related_name="licencaafastamentoconjuge_conjuge",
    )
    orgao = models.ForeignKey(
        UnidadeAdministrativa,
        related_name="afastamentoconjuge_orgaoconjuge",
        on_delete=models.PROTECT,
        verbose_name="Orgão/Entidade do Cônjuge",
    )
    orgao_destino = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.PROTECT,
        related_name="afastamentoconjuge",
        verbose_name="Destino da transferência",
    )

    class Meta:
        verbose_name = "Licença Afastamento Cônjuge/Companheiro"
        db_table = "afastamento_licafastamentoconj"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_AFAST_CONJUGE"

    def configurar(self):
        self.remunerado = False
        self.suspensao_estagio_prob = True
        self.suspensao_contagem_ferias = True
        self.efetivo_exercicio = False
        self.prorroga_progressao = True

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s em razão de afastamento do
        cônjuge/companheiro %(conjuge)s para %(orgao_destino)s no(a) %(localidade)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        conjuge = self.conjuge
        orgao_destino = self.orgao_destino
        localidade = (
            self.orgao_destino.address.latest("pk").municipio
            if self.orgao_destino and self.orgao_destino.address.exists()
            else "localidade"
        )
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencaafastamentoconjuge.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "conjuge": conjuge,
                "orgao_destino": orgao_destino,
                "localidade": localidade,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença afastamento do cônjuge/companheiro"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaServicoMilitar(Licenca):
    data_inicio_servico = models.DateField(verbose_name="Data Início Serviço")
    data_fim_servico = models.DateField(verbose_name="Data Fim Seriço")

    prazo_maximo = {"days": 30}

    class Meta:
        verbose_name = "Licença Serviço Militar"
        db_table = "afastamento_licservicomil"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_MILITAR"

    def configurar(self):
        self.remunerado = False
        self.suspensao_estagio_prob = True
        self.efetivo_exercicio = False

    def validate(self):
        self.validate_fim_previsto()
        return super(LicencaServicoMilitar, self).validate()

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def validate_fim_previsto(self):
        if NewDateRange(
            self.data_fim_servico, self.data_fim
        ).days > self.prazo_maximo.get("days"):
            raise self.ErroPrazoMaximo(
                txt="Prazo máximo permitido para esta licença é de %s dias após o fim do Serviço Militar."
                % self.prazo_maximo.get("days")
            )
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de %(data_inicio)s à
        %(data_prevista)s em razão de convocação para o serviço militar obrigatório.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencaservicomilitar.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "serviço militar obrigatório"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaAtividadePolitica(Licenca):
    cargo_eletivo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CARGO_ELETIVO_CHOICES"),
        verbose_name="Cargo Eletivo",
        default=1,
    )
    partido = models.CharField(
        verbose_name="Partido Político", max_length=100, default=""
    )
    localidade = models.ForeignKey(
        Localidade, null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Licença Atividade Política"
        db_table = "afastamento_licencapolitica"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_POLITICA"

    def configurar(self):
        # self.remunerado = False
        self.suspensao_estagio_prob = True

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se  para atividade política
        de %(data_inicio)s à %(data_prevista)s, período que mediou sua
        escolha em convenção partidária, como candidato ao cargo eletivo de
        %(cargo_eletivo)s pelo partido %(partido)s, na cidade %(localidade)s .
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        cargo_eletivo = self.get_cargo_eletivo_display()
        partido = self.partido
        localidade = "localidade"
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencaatividadepolitica.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "cargo_eletivo": cargo_eletivo,
                "partido": partido,
                "localidade": localidade,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença atividade política"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaCapacitacao(Licenca):
    """
    - Campo onde se informe o curso e a instituição
    """

    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    instituicao = models.ForeignKey(UnidadeAdministrativa, on_delete=models.PROTECT)

    prazo_maximo = {"days": 90}

    class Meta:
        verbose_name = "Licença Capacitação"
        db_table = "afastamento_licencacapacitacao"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_CAPACITACAO"

    def configurar(self):
        if NewDateRange(self.data_inicio, self.data_fim).days > self.prazo_maximo.get(
            "days"
        ):
            self.remunerado = False
        self.concessao_durante_estagio_prob = False
        self.efetivo_exercicio = False

    def validate(self):
        self.validate_quinquenio()
        super(LicencaCapacitacao, self).validate()

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def validate_quinquenio(self):
        log.info(
            """
            - Incluir crítica de que o servidor terá até 3 meses a cada quinquênio (período mínimo para aquisição do direito: 5 anos)
            """
        )
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s em razão de
        capacitação/especialização no curso %(curso)s ministrado pela instituição %(instituicao)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        curso = self.curso
        instituicao = self.instituicao
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencacapacitacao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "curso": curso,
                "instituicao": instituicao,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença capacitação/especialização"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaInteresseParticular(Licenca):
    class Meta:
        verbose_name = "Licença Interesse Particular"
        db_table = "afastamento_licencainteresse"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_INTERESSE"

    def configurar(self):
        self.remunerado = False
        self.concessao_durante_estagio_prob = True
        self.efetivo_exercicio = False
        self.prorroga_progressao = True

    def validate(self):
        log.info(
            """- Crítica do sistema de que nova licença só pode ser
            concedida após decorrido igual período a partir do término da
            licença anterior."""
        )
        log.info(
            """
            Exigência de inclusão manual de data inicio e fim previsto, visto que o tempo pode variar, limitando em 3 anos
            - Incluir crítica de que nova licença só pode ser concedida após decorrido igual período a partir do término da licença anterior
            - Incluir opção de "Prorrogação" na aba de Alterações limitando em 3 anos de prazo máximo
        """
        )
        self.validate_erro_data_fim()
        self.validate_prazo_maximo()
        return super(LicencaInteresseParticular, self).validate()

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def validate_erro_data_fim(self):
        if self.data_fim is None:
            raise self.ErroDataFimNone()
        return True

    def validate_prazo_maximo(self):
        # TODO VERIFICAR SE EXISTE QUANTIDADE MÁXIMA DE DIAS
        licenca_particular = LicencaInteresseParticular.objects.filter(
            servidor=self.servidor, data_fim__lt=self.data_inicio
        )
        if self.pk:
            licenca_particular = licenca_particular.exclude(pk=self.pk)
        licenca_particular = (
            licenca_particular.latest("data_fim")
            if licenca_particular.count()
            else licenca_particular
        )
        if licenca_particular:
            days_ausente = NewDateRange(
                licenca_particular.data_inicio, licenca_particular.data_fim
            )
            days_trabalhados = NewDateRange(
                licenca_particular.data_fim, self.data_inicio
            )
            if days_trabalhados < days_ausente:
                raise self.ErroPrazoMaximo(
                    txt="É necessário permanecer o mesmo período da licença trabalhando na instituição."
                )
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s para tratar de interesses particulares.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencainteresseparticular.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença interesse particular"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class LicencaMandatoClassista(Licenca):
    entidade = models.ForeignKey(
        UnidadeAdministrativa, on_delete=models.PROTECT, verbose_name="Entidade"
    )
    cargo = models.CharField(verbose_name="Cargo", max_length=100, default="")
    tipo_entidade = models.IntegerField(
        choices=Choice.get_choices_for("rh", "MANDATO_CLASSISTA_TIPO_ENTIDADE_CHOICES"),
        verbose_name="Tipo Entidade",
        default=1,
    )
    onus_payment = models.IntegerField(
        choices=Choice.get_choices_for("rh", "ONUS_PAYMENT"),
        default=1,
        verbose_name="Ônus",
    )

    class Meta:
        verbose_name = "Licença Mandato Classista"
        db_table = "afastamento_licencaclassista"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_CLASSISTA"

    def validate_publicacao(self):
        if not self.servidor.membro and self.publicacao_movimentacao is None:
            raise self.ErroPublicacaoNaoEncontrada()
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s para desempenho de mandato
        classista no(a) %(entidade)s
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        entidade = self.entidade
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/licencamandatoclassista.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "entidade": entidade,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença desempenho mandato classista"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(~Q(recesso=None))
            query = query.exclude(~Q(feriasafastamento=None))
            query = query.exclude(~Q(licenca__licencasaude=None))
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 8
        super(LicencaMandatoClassista, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AwardLicense(Licenca):

    class Meta:
        verbose_name = "Licença Prêmio"
        db_table = "afastamento_awardlicense"

    @property
    def situacao_funcional(self):
        return "ATIVO_LIC_PREMIO"

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s por Licença Prêmio.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/awardlicense.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença prêmio"


class AfastamentoOutroOrgaoQueryset(BaseLicencaAfastamentoQueryset):

    def not_through_payroll(self):
        return self.exclude(Q(onus=1) | Q(transito_pela_folha=True))


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoOutroOrgao(Afastamento):
    posse = models.ForeignKey(
        MovimentacaoPosse, on_delete=models.PROTECT, related_name="afastamento"
    )
    quadro_destino = models.ForeignKey(
        Quadro,
        verbose_name="Cargo no destino",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    orgao = models.ForeignKey(UnidadeAdministrativa, on_delete=models.PROTECT)
    onus = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_ONUS"),
        default=1,
        verbose_name="Ônus",
    )
    contribuicao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        default=2,
        verbose_name="Opção de contribuição",
    )
    transito_pela_folha = models.BooleanField(
        default=False, verbose_name="Trânsito/FOPAG"
    )

    objects = AfastamentoOutroOrgaoQueryset.as_manager()

    class Meta:
        verbose_name = "Afastamento para Outro Órgão"
        db_table = "afastamento_afastoutroorgao"

    @property
    def situacao_funcional(self):
        try:
            self.onus = int(self.onus)
        except Exception:
            self.onus = 0
        return (
            "ATIVO_AFA_OUT_ORG_ONUS_MP"
            if self.onus == 1
            else "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP"
        )

    def __str__(self):
        return "%s - PARA: %s - De %s a %s" % (
            self.posse,
            self.orgao,
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "",
        )

    def configurar(self):
        try:
            self.onus = int(self.onus)
        except Exception:
            self.onus = 0
        self.remunerado = False if self.onus == 2 else True
        self.suspensao_contagem_ferias = False

    def validate(self):
        self.validate_publicacao()
        self.validate_employee_active()
        self.validate_data_prevista()
        self.validate_save_servidor()
        self.validate_designation_exercise()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 7
        self.servidor = self.posse.servidor
        super(AfastamentoOutroOrgao, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período
        de %(data_inicio)s à %(data_prevista)s para servir a outro Órgão/Entidade.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentooutroorgao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para servir a outro órgão/entidade"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(~Q(feriasafastamento=None))
            query = query.exclude(
                ~Q(
                    licenca__licencasaude__baselicencasaudejuntamedica__licencamaternidade=None
                )
            )
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoMandatoEletivo(Afastamento):
    """
    - Incluir campo com data inicio, fim do afastamento e prorrogação;
    - Remunerado: se mandato federal, estadual ou distrital não remunerado; se prefeito
    ou vice pode optar pela remuneração; se vereador acumula as remunerações
    ou opte por uma delas.
    """

    cargo_eletivo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CARGO_ELETIVO_CHOICES"), default=1
    )
    partido = models.CharField(
        verbose_name="Partido Político", max_length=100, default=""
    )
    localidade = models.ForeignKey(
        Localidade, null=True, blank=True, on_delete=models.PROTECT
    )
    organ_location = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.PROTECT,
        verbose_name="Órgão de destino",
        related_name="afastamentomandatoeletivo_organ_location",
    )

    class Meta:
        verbose_name = "Afastamento Mandato Eletivo"
        db_table = "afastamento_afastmandatoeletivo"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_ELETIVO"

    def configurar(self):
        self.suspensao_estagio_prob = True
        self.suspensao_contagem_ferias = True
        self.remunerado = False

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para exercício de mandato
        eletivo no cargo de %(cargo)s em %(organ_location)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        cargo = self.get_cargo_eletivo_display()
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentomandatoeletivo.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "cargo": cargo,
                "organ_location": self.organ_location,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para exercício de mandato eletivo"

    def validate_organ_location(self):
        if not self.organ_location:
            raise Exception("O Órgão de Destino é obrigatório.")
        elif not self.organ_location.pessoa_juridica:
            raise Exception("O cnpj do Órgão de Destino é obrigatório.")
        elif not self.organ_location.pessoa_juridica.cnpj:
            raise Exception("O cnpj do Órgão de Destino é obrigatório.")

    def validate(self):
        self.validate_organ_location()
        return super(AfastamentoMandatoEletivo, self).validate()


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoEstudar(Afastamento):
    """
    - Campo que conste instituição de estudo, curso, local (cidade, estado, pais), data retorno;
    - Limitar em máximo de 4 anos
    """

    instituicao = models.ForeignKey(
        UnidadeAdministrativa, on_delete=models.PROTECT, verbose_name="Instituição"
    )
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    localidade = models.ForeignKey(Localidade, on_delete=models.PROTECT)
    parcial = models.BooleanField("Parcial", default=False, blank=True)

    class Meta:
        verbose_name = "Afastamento para Estudar"
        db_table = "afastamento_afastestudar"

    @property
    def situacao_funcional(self):
        if self.parcial:
            return "ATIVO_AFA_PARC_ESTUDAR"
        else:
            return "ATIVO_AFA_ESTUDAR"

    def configurar(self):
        self.concessao_durante_estagio_prob = False

    def validate(self):
        self.validate_prazo_maximo()
        return super(AfastamentoEstudar, self).validate()

    def validate_prazo_maximo(self):
        if (
            NewDateRange(self.data_inicio, self.data_fim).days
            > NewDateRange(
                self.data_inicio, self.data_inicio + relativedelta(years=4)
            ).days
        ):
            raise self.ErroPrazoMaximo(txt="O tempo máximo de afastamento é de 4 anos.")
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para estudo em outra unidade da
        federação ou no exterior no curso %(curso)s, na
        instituição %(instituicao)s em %(local)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        curso = self.curso
        instituicao = self.instituicao
        localidade = self.localidade
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentoestudar.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "curso": curso,
                "instituicao": instituicao,
                "localidade": localidade,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para estudo em outra unidade da federação ou no exterior"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        servidor = kargs.get("servidor", None)
        if servidor and servidor.membro:
            query = query.exclude(~Q(feriasafastamento=None))
            kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoMissao(Afastamento):
    """
    - Campo para constar Ato de designação, periodo de afastamento, objetivo da missao
    """

    orgao = models.ForeignKey(UnidadeAdministrativa, on_delete=models.PROTECT)
    objetivo = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Afastamento para Missão"
        db_table = "afastamento_afastmissao"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_MISSAO"

    def configurar(self):
        self.concessao_durante_estagio_prob = False

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para para missão oficial no exterior.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentomissao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para missão oficial no exterior"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoEleitoral(Afastamento):
    """
    Afastamento por Convocação Eleitoral.
    - Incluir campo que permita controle da dispensa ao serviço
        (usufruto das folgas), limitado ao dobro do tempo de afastamento.
        O usufruto pode ocorrer a qualquer momento? precisa ser contínuo?
    """

    class Meta:
        verbose_name = "Afastamento Convocação Eleitoral"
        db_table = "afastamento_afasteleitoral"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_ELEITORAL"

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para atender à convocação da Justiça Eleitoral.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentoeleitoral.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para atender à convocação da Justiça Eleitoral"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoServirJuri(Afastamento):
    localidade = models.ForeignKey(
        Localidade, null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Afastamento para Servir ao Júri"
        db_table = "afastamento_afastjuri"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_JURI"

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s licenciou-se no período de
        %(data_inicio)s à %(data_prevista)s para servir no tribunal do juri.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentoservirjuri.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "licença para servir no tribunal do juri"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoTreinamento(Afastamento):
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="afatreinamento_curso",
        null=True,
        blank=True,
    )
    carga_horaria = models.IntegerField(null=True, blank=True)
    instituicao = models.ManyToManyField(
        UnidadeAdministrativa, related_name="afastamentotreinamento", blank=True
    )

    class Meta:
        verbose_name = "Afastamento Treinamento"
        db_table = "afastamento_afasttreinamento"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_TREINAMENTO"

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período
        de %(data_inicio)s à %(data_prevista)s para participar de
        programa de treinamento regularmente instituído.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentotreinamento.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para participar de programa de treinamento"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoDeslocamento(Afastamento):
    """
    - Deve pedir nova lotação;
    - Limitar em maximo de 10 dias.
    """

    localidade_origem = models.ForeignKey(
        Localidade, related_name="deslocamento_origem", on_delete=models.PROTECT
    )
    localidade_destino = models.ForeignKey(
        Localidade, related_name="deslocamento_destino", on_delete=models.PROTECT
    )

    prazo_maximo = {"days": 10}

    class Meta:
        verbose_name = "Afastamento Deslocamento"
        db_table = "afastamento_afastdeslocamento"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_DESLOCAMENTO"

    def validate(self):
        self.validate_prazo_maximo()
        self.validate_local_origem_destino()
        return super(AfastamentoDeslocamento, self).validate()

    def validate_local_origem_destino(self):
        if (
            not self.servidor.get_workplace_only()
            .filter(lotacao__localidade__pk=self.localidade_origem.pk)
            .exists()
        ):
            workplace_only = ""
            for lot in self.servidor.get_workplace_only():
                workplace_only += " %s, " % (lot)
            raise Exception(
                "A localidade de origem não está nas lotações do servidor. Lotações do servidor:%s"
                % workplace_only
            )
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s de %(local_origem) à %(localidade_destino)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentodeslocamento.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
                "localidade_origem": self.localidade_origem,
                "localidade_destino": self.localidade_destino,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para deslocar-se até nova sede em outro município"

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 10
        # self.anota = False
        super(AfastamentoDeslocamento, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoCompeticao(Afastamento):
    class Meta:
        verbose_name = "Afastamento para Competição"
        db_table = "afastamento_afastcompeticao"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_COMPETICAO"

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para participar de competição
        desportiva nacional ou internacional ou atender a convocação para
        integrar representação cultural e artística ou desportiva no País ou exterior.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentocompeticao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para participar de competição desportiva ou integrar representação"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoCursoConcurso(Afastamento):
    """
    - Possibilidade de concessão durante o Estágio Probatório: Sim,
        somente se para outro cargo da Administração Publica Estadual (Art 20, §11);
    - Remunerado: A Lei não explicita que é sem remuneração,
        portanto é remunerado, porém sabe-se que se o curso for remunerado,
        então o servidor pode optar por qual remuneração receber, sem acumular.
    """

    orgao = models.ForeignKey(UnidadeAdministrativa, on_delete=models.PROTECT)
    cargo = models.ForeignKey(Cargo, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Afastamento Curso de Concurso"
        db_table = "afastamento_afastcursoconcurso"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_CURSO_CONCURSO"

    def configurar(self):
        if self.orgao.esfera_governamental != 2:
            self.concessao_durante_estagio_prob = False
        self.suspensao_estagio_prob = True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s para participar de curso de
        formação relativo à etapa de concurso público %(cargo)s no órgão %(orgao)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        cargo = ("no cargo de %s," % self.cargo) if self.cargo else ""
        orgao = self.orgao
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentocursoconcurso.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "cargo": cargo,
                "orgao": orgao,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para participar de curso de formação relativo à etapa de concurso público"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoPrisao(Afastamento):
    prazo_anos = models.IntegerField(
        default=0, blank=True, verbose_name="Prazo em anos"
    )
    prazo_meses = models.IntegerField(
        default=0, blank=True, verbose_name="Prazo em meses"
    )
    prazo_dias = models.IntegerField(verbose_name="Prazo em dias")
    motivo_prisao = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Afastamento Prisão"
        db_table = "afastamento_afastprisao"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_PRISAO"

    def configurar(self):
        self.concessao_durante_estagio_prob = False
        self.suspensao_contagem_ferias = True
        self.suspensao_estagio_prob = True
        self.efetivo_exercicio = False

    def set_data_prevista(self):
        if self.data_prevista is None:
            self.data_prevista = (
                self.data_inicio
                + relativedelta(days=self.prazo_dias)
                + relativedelta(months=self.prazo_meses)
                + relativedelta(years=self.prazo_anos)
            )
        if self.data_fim is None:
            self.data_fim = self.data_prevista
        return True

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s afastou-se no período de
        %(data_inicio)s à %(data_prevista)s em razão de prisão.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentoprisao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento por prisão"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoSuspensao(Afastamento):
    prazo_dias = models.IntegerField(verbose_name="Prazo em dias")
    convertido_multa = models.BooleanField(
        verbose_name="Convertido em Multa", default=False, blank=True, null=True
    )

    class Meta:
        verbose_name = "Afastamento Suspensão"
        db_table = "afastamento_afastsuspensao"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_SUSPENSAO"

    def configurar(self):
        # self.remunerado = False
        pass

    def set_data_prevista(self):
        if self.data_prevista is None:
            self.data_prevista = self.data_inicio + relativedelta(days=self.prazo_dias)
        if self.data_fim is None:
            self.data_fim = self.data_prevista
        return True

    def get_nome_arquivo(self):
        return "afastamentosuspensao"

    def get_texto(self):
        """
        SUSPENDER por %(dias)s dias, a partir de %(data_inicio)s, %(servidor)s do exercício do cargo,
            em face do art. 179, da Lei Complementar nº 51/08, com as consequências do § 2º do mesmo dispositivo.
        """
        texto = ""
        servidor = self.servidor.posses_ativas.latest("data_exercicio")
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        nome_arquivo = self.get_nome_arquivo()
        with codecs.open(
            f"{templates.__path__[0]}/{nome_arquivo}.txt", "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "dias": self.prazo_dias,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento por suspensao"

    def save(self, *args, **kargs):
        self.motivo = 12
        super(AfastamentoSuspensao, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoSindicanciaAdm(Afastamento):
    prazo_dias = models.IntegerField(verbose_name="Prazo em dias")

    class Meta:
        verbose_name = "Afastamento Sindicância Administrativa"
        db_table = "afastamento_afastsindicanciaadm"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_SINDICANCIA_ADM"

    def get_nome_arquivo(self):
        return "afastamentosindicanciaadm"

    def get_texto_modelo(self):
        return "afastamento por sindicância administrativa"

    def save(self, *args, **kargs):
        self.motivo = 62
        super(AfastamentoSindicanciaAdm, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoComparecimentoJuizo(Afastamento):

    class Meta:
        verbose_name = "Afastamento comparecer a juízo"
        db_table = "afastamento_afastcompjuizo"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_COMPJUIZO"

    def get_texto(self):
        """
        O(A) %(texto_servidor)s %(servidor)s afastou-se das suas funções no período de %(data_inicio)s à
            %(data_prevista)s para comparecer a juízo.
        """
        texto = ""
        servidor = self.servidor.posses_ativas.latest("data_exercicio")
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = DateUtils.date_to_str(self.data_prevista)
        with codecs.open(
            "%s/afastamentocompjuizo.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para comparecer a juízo"

    def save(self, *args, **kargs):
        self.motivo = 2
        super(AfastamentoComparecimentoJuizo, self).save(*args, **kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoCandidatura(Afastamento):

    class Meta:
        verbose_name = "Afastamento candidatura"
        db_table = "afastamento_afastcandidatura"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_CANDIDATURA"

    def get_texto(self):
        """
        O(A) %(texto_servidor)s %(servidor)s afastou-se das suas funções no período de %(data_inicio)s à
            %(data_prevista)s para candidatura em Lista Tríplice do PGJ.
        """
        texto = ""
        servidor = self.servidor.posses_ativas.latest("data_exercicio")
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = DateUtils.date_to_str(self.data_prevista)
        with codecs.open(
            "%s/afastamentoccandidatura.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento para candidatura em Lista Tríplice do PGJ"

    def save(self, *args, **kargs):
        self.validate()
        self.motivo = 2
        super(AfastamentoCandidatura, self).save(*args, **kargs)

    def validate(self):
        self.validate_type_by_possession()

    def validate_type_by_possession(self):
        if self.servidor.type_by_possession != "MBR":
            raise Exception(
                "Só é permitido cadastrar Afastamento Candidatura para Membros"
            )


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaDoacaoSangue(Ausencia):

    prazo_maximo = {"days": 1}

    class Meta:
        verbose_name = "Ausência Doação de Sangue"
        db_table = "afastamento_ausenciasangue"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_SANGUE"

    def validate(self):
        self.validate_prazo_maximo()
        return super(AusenciaDoacaoSangue, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no dia %(data_inicio)s em razão de doação de sangue.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        with codecs.open(
            "%s/ausenciadoacao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
            }
        return texto


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaEleitor(Ausencia):
    """
    Ausência para alistamento eleitoral.
    """

    prazo_maximo = {"days": 2}

    class Meta:
        verbose_name = "Ausência Alistamento Eleitoral"
        db_table = "afastamento_ausenciaeleitor"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_ELEITOR"

    def validate(self):
        self.validate_prazo_maximo()
        return super(AusenciaEleitor, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se nos dias %(data_inicio)s e %(data_prevista)s em razão de alistamento como eleitor.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/ausenciaeleitor.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "concessão de ausência em razão de alistamento como eleitor"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaCasamento(Ausencia):
    data_casamento = models.DateField(verbose_name="Data Casamento")
    conjuge = models.ForeignKey(
        PessoaFisica,
        on_delete=models.PROTECT,
        related_name="ausenciacasamento",
        verbose_name="Conjuge",
    )

    prazo_maximo = {"days": 8}

    class Meta:
        verbose_name = "Ausência Casamento"
        db_table = "afastamento_ausenciacasamento"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_CASAMENTO"

    def validate(self):
        self.validate_prazo_maximo()
        return super(AusenciaCasamento, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período
            de %(data_inicio)s à %(data_prevista)s em razão de casamento
            com %(conjuge)s, ocorrido em %(data_casamento)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        conjuge = self.conjuge
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        data_casamento = DateUtils.date_to_str(self.data_casamento)
        with codecs.open(
            "%s/ausenciacasamento.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
                "conjuge": conjuge,
                "data_casamento": data_casamento,
            }
        return texto

    def get_texto_modelo(self):
        return "concessão de ausência em razão de casamento"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaNascimento(Ausencia):
    crianca = models.ForeignKey(
        PessoaFisica,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ausencianascimento",
        verbose_name="Filho(a)",
    )

    prazo_maximo = {"days": 20}

    class Meta:
        verbose_name = "Ausência Nascimento"
        db_table = "afastamento_ausencianascimento"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_NASCIMENTO"

    def validate_pai(self):
        if self.servidor.pessoa_fisica.sexo == "F":
            raise Exception("Esta ausência é exclusiva para Homens.")

    def validate(self):
        if not self.crianca and self.alteracao != CANCELED:
            raise Exception("Preencha o campo criança.")
        if self.crianca and self.crianca.data_nascimento is None:
            raise Exception("A data de nascimento deve ser preenchida.")
        if self.crianca:
            aus = AusenciaNascimento.objects.filter(crianca=self.crianca).exclude(
                estado=CANCELED
            )
            if self.pk:
                aus = aus.exclude(pk=self.pk)
            if aus.exists():
                raise Exception("É permitido apenas um afastamento para cada criança.")
        self.validate_prazo_maximo()
        self.validate_pai()
        return super(AusenciaNascimento, self).validate()

    def get_texto(self):
        """
        O servidor %(servidor)s ausentou-se no período de %(data_inicio)s à
            %(data_prevista)s em razão de nascimento/adoção de seu(sua)
            filho(a) %(filho)s, ocorrido em %(data_nascimento)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        filho = self.crianca
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        data_nascimento = DateUtils.date_to_str(self.crianca.data_nascimento)
        with codecs.open(
            "%s/ausencianascimento.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
                "filho": filho,
                "data_nascimento": data_nascimento,
            }
        return texto

    def get_texto_modelo(self):
        return "concessão de ausência em razão de nascimento/adoção de filho(a)"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaFalecimento(Ausencia):
    pessoa = models.ForeignKey(
        PessoaFisica,
        on_delete=models.PROTECT,
        related_name="ausenciafalecimento",
        verbose_name="Pessoa",
    )
    vinculo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Tipo de Vínculo",
        default=10,
    )

    prazo_maximo = {"days": 8}

    class Meta:
        verbose_name = "Ausência Falecimento"
        db_table = "afastamento_ausenciafalecimento"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_FALECIMENTO"

    def validate_date_person_death(self):
        if not self.pessoa.data_obito:
            raise Exception("A data de óbito da pessoa deve ser preenchida.")
        return True

    def validate_duplicated_person(self):
        check = AusenciaFalecimento.objects.filter(
            servidor=self.servidor, pessoa=self.pessoa
        ).exclude(estado=CANCELED)
        if self.pk:
            check = check.exclude(pk=self.pk)
        if check.exists():
            raise Exception(
                "A pessoa informada já possui uma ausência do mesmo motivo."
            )
        return True

    def validate(self):
        self.validate_date_person_death()
        self.validate_duplicated_person()
        self.validate_prazo_maximo()
        return super(AusenciaFalecimento, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período de
        %(data_inicio)s à %(data_prevista)s em razão de falecimento
        de seu(sua) %(parentesco)s %(pessoa)s, ocorrido em %(data_falecimento)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        parentesco = self.get_vinculo_display()
        pessoa = self.pessoa
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        data_falecimento = (
            DateUtils.date_to_str(self.pessoa.data_obito)
            if self.pessoa.data_obito
            else DateUtils.date_to_str(self.data_inicio)
        )
        with codecs.open(
            "%s/ausenciafalecimento.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
                "parentesco": parentesco,
                "pessoa": pessoa,
                "data_falecimento": data_falecimento,
            }
        return texto

    def get_texto_modelo(self):
        return "concessão de ausência em razão de falecimento"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AusenciaConclusao(Ausencia):
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="ausenciaconclusao",
        verbose_name="Curso",
    )

    prazo_maximo = {"days": 10}

    class Meta:
        verbose_name = "Ausência Conclusão"
        db_table = "afastamento_ausenciaconclusao"

    @property
    def situacao_funcional(self):
        return "ATIVO_AUS_CONCLUSAO"

    def validate(self):
        self.validate_prazo_maximo()
        return super(AusenciaConclusao, self).validate()

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s ausentou-se no período
            de %(data_inicio)s à %(data_prevista)s em razão de finalização
            de trabalho de conclusão do curso de nível %(nivel)s em %(curso)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        nivel = self.curso.get_grau_instrucao_display()
        curso = self.curso
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/ausenciaconclusao.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
                "nivel": nivel,
                "curso": curso,
            }
        return texto

    def get_texto_modelo(self):
        return "ausência em razão de finalização de trabalho de conclusão de curso"


@auditable("data_inicio", "data_fim", "publicacao_fim")
class AfastamentoDisponibilidade(Afastamento):
    posse = models.ForeignKey(
        MovimentacaoPosse, on_delete=models.PROTECT, related_name="disponibilidade"
    )

    class Meta:
        verbose_name = "Afastamento Disponibilidade"
        db_table = "afastamento_disponibilidade"

    @property
    def situacao_funcional(self):
        return "ATIVO_AFA_DISPONIBILIDADE"

    def __str__(self):
        return "%s - Em Disponibilidade" % (self.posse)

    def validate(self):
        return super(AfastamentoDisponibilidade, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 2
        self.servidor = self.posse.servidor
        super(AfastamentoDisponibilidade, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s está Em Disponibilidade
        de %(data_inicio)s à %(data_prevista)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/afastamentodisponibilidade.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "afastamento em disponibilidade"

    @classmethod
    def excluir_conflitos(cls, **kargs):
        """
        Este método contem as clausulas para excluir algum tipo de conflito nos afastamentos.
        Ex: afastamentos CANCELED não geram conflitos de períodos.
        Cada classe deve possuir sua sobrescrita.
        """
        query = kargs.get("query", [])
        if query:
            query = query.exclude(~Q(feriasafastamento=None))
            query = query.exclude(
                ~Q(
                    licenca__licencasaude__baselicencasaudejuntamedica__licencamaternidade=None
                )
            )
        kargs.update({"query": query})
        return BaseLicencaAfastamento.excluir_conflitos(**kargs)


@auditable("data_inicio", "data_fim", "publicacao_fim")
class HealthPrevent(BaseLicencaAfastamento):
    year = models.IntegerField()

    anotacao_classe = rh_models.AnotacaoAfastamento
    prazo_maximo = {"days": 1}
    age_woman = 30
    age_man = 45

    class Meta:
        verbose_name = "Usufruto Prevenção Saúde"
        db_table = "afastamento_healthprevent"

    @property
    def situacao_funcional(self):
        return "ATIVO_USU_PREVENCAOSAUDE"

    def __str__(self):
        return "%s - Em Usufruto Prevenção de Saúde " % (self.servidor)

    def validate_year(self):
        validate = HealthPrevent.objects.filter(
            servidor=self.servidor, year=self.year
        ).exclude(estado=CANCELED)
        if self.pk is not None:
            validate = validate.exclude(pk=self.pk)
        if validate.exists():
            raise Exception("Apenas uma folga é permitida por ano.")

    def validate_woman(self):
        if self.servidor.pessoa_fisica.sexo == "F" and (
            (
                NewDateRange(
                    self.servidor.pessoa_fisica.data_nascimento, datetime.now().date()
                ).days
                / 365
            )
            < self.age_woman
        ):
            raise Exception(
                "Apenas para sexo %s que possue acima de %s anos."
                % (self.servidor.pessoa_fisica.get_sexo_display(), self.age_woman)
            )

    def validate_man(self):
        if self.servidor.pessoa_fisica.sexo == "M" and (
            (
                NewDateRange(
                    self.servidor.pessoa_fisica.data_nascimento, datetime.now().date()
                ).days
                / 365
            )
            < self.age_man
        ):
            raise Exception(
                "Apenas para sexo %s que possue acima de %s anos."
                % (self.servidor.pessoa_fisica.get_sexo_display(), self.age_man)
            )

    def validate(self):
        self.validate_year()
        self.validate_woman()
        self.validate_man()
        self.validate_prazo_maximo()
        return super(HealthPrevent, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.motivo = 2
        super(HealthPrevent, self).save(*args, **kargs)

    def get_texto(self):
        """
        O(A) servidor(a) %(servidor)s está Em Usufruto Prevenção de Saúde
        de %(data_inicio)s à %(data_prevista)s.
        """
        texto = ""
        servidor = self.servidor.pessoa_fisica
        data_inicio = DateUtils.date_to_str(self.data_inicio)
        data_prevista = (
            DateUtils.date_to_str(self.data_prevista)
            if self.data_prevista
            else "data prevista de fim não informada"
        )
        with codecs.open(
            "%s/healthprevent.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "servidor": servidor,
                "data_inicio": data_inicio,
                "data_prevista": data_prevista,
            }
        return texto

    def get_texto_modelo(self):
        return "usufruto saúde da mulher"


auditlog.register(BaseLicencaAfastamento)
auditlog.register(Afastamento)
auditlog.register(Licenca)
auditlog.register(Ausencia)
auditlog.register(FeriasAfastamento)
auditlog.register(Viagem)
auditlog.register(Recesso)
auditlog.register(FolgaCompensacao)
auditlog.register(FolgaEleitoral)
auditlog.register(FolgaAniversario)
auditlog.register(DesempenhoFuncao)
auditlog.register(AtuacaoGrupoTrabalho)
auditlog.register(Plantao)
auditlog.register(HealthCertificate)
auditlog.register(LicencaSaude)
auditlog.register(LicencaSaude3Dias)
auditlog.register(LicencaSaude30Dias)
auditlog.register(BaseLicencaSaudeJuntaMedica)
auditlog.register(LicencaSaudeJuntaMedica)
auditlog.register(LicencaDoencaPessoaFamilia)
auditlog.register(LicencaMaternidade)
auditlog.register(LicencaAdocao)
auditlog.register(LicencaAfastamentoConjuge)
auditlog.register(LicencaServicoMilitar)
auditlog.register(LicencaAtividadePolitica)
auditlog.register(LicencaCapacitacao)
auditlog.register(LicencaInteresseParticular)
auditlog.register(LicencaMandatoClassista)
auditlog.register(AwardLicense)
auditlog.register(AfastamentoOutroOrgao)
auditlog.register(AfastamentoMandatoEletivo)
auditlog.register(AfastamentoEstudar)
auditlog.register(AfastamentoMissao)
auditlog.register(AfastamentoEleitoral)
auditlog.register(AfastamentoServirJuri)
auditlog.register(AfastamentoTreinamento)
auditlog.register(AfastamentoDeslocamento)
auditlog.register(AfastamentoCompeticao)
auditlog.register(AfastamentoCursoConcurso)
auditlog.register(AfastamentoPrisao)
auditlog.register(AfastamentoSuspensao)
auditlog.register(AfastamentoComparecimentoJuizo)
auditlog.register(AfastamentoCandidatura)
auditlog.register(AusenciaDoacaoSangue)
auditlog.register(AusenciaEleitor)
auditlog.register(AusenciaCasamento)
auditlog.register(AusenciaNascimento)
auditlog.register(AusenciaFalecimento)
auditlog.register(AusenciaConclusao)
auditlog.register(AfastamentoDisponibilidade)
auditlog.register(HealthPrevent)
auditlog.register(AfastamentoSindicanciaAdm)
auditlog.register(CID)
auditlog.register(CIDCode)
