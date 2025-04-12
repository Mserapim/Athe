# -*- coding: utf-8 -*-
import codecs
import copy
import decimal
import re
import uuid
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from deprecated import deprecated
from django.contrib.auth.models import User
from django.db import IntegrityError, models, transaction
from django.db.models import CASCADE, SET_NULL, Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.template.defaultfilters import slugify

from contrib.cache import delete_cache, make_group_key
from contrib.daterange import NewDateRange
from contrib.decorator import to_search
from contrib.middleware import get_current_user
from contrib.utils import (
    Locker,
    get_json_engine,
    getLogger,
    int_to_roman,
    employee_from_user,
    DateUtils,
)
from engine.models import NullTaskSession, TaskSession, UserHasNotPermission
from esocial.models import ItemTable
from ged.models import Arquivo
from rh import const as rh_const
from rh import templates
from rh.afastamento.models import AfastamentoOutroOrgao
from rh.models import (
    AnotacaoCarreira,
    BenefitMovement,
    Cargo,
    DadoBancarioPessoa,
    Dependencia,
    MovimentacaoPessoal,
    ProcessSuspension,
    Publicacao,
    Servidor,
    SocialSecurity,
    Pessoa,
)
from standard.models import (
    AuditTimestampModel,
    Choice,
    ClassCode,
    Configuration,
    ListDatedModel,
    RunCodeManager,
)
from ged.models import Arquivo as File
from auditlog.registry import auditlog
from rh.pvf.const import (
    REQUEST_STEP_JURIDICAL_ADVISORY_1,
    REQUEST_STEP_PROG_DG,
    REQUEST_STEP_JURIDICAL_ADVISORY_2,
    GROUP_ASS_JUR_1,
    GROUP_PROG_DG,
    GROUP_ASS_JUR_2,
    REQUEST_STEP_GER_DEV,
    REQUEST_ACT_OPEN_SOLICITANTION,
    REQUEST_ACT_SOLICITATION,
)


json = get_json_engine()

log = getLogger(__name__)

GFP_STATUS_WORKFLOW1 = {1: (2, 4), 2: (1, 4), 4: (3, 2), 3: tuple()}

GFP_STATUS_WORKFLOW = {
    1: {
        2: "gfp.can_change_status_payroll",
        4: "gfp.can_process_payroll",
    },  # EM PRODUCAO
    2: {1: "gfp.can_change_status_payroll", 4: "gfp.can_process_payroll"},  # EM ANALISE
    4: {3: "gfp.can_close_payroll", 2: "gfp.can_process_payroll"},  # PROCESSADA
    3: {1: "gfp.can_close_payroll", 2: "gfp.can_close_payroll"},  # FECHADA
}

GFP_TIPO_LANCAMENTO = {"F": "FIXO", "T": "TEMPORÁRIO", "U": "TEMPORÁRIO - ÚNICO"}

GFP_TIPO_EVENTO = {"P": "PROVENTO", "D": "DESCONTO", "I": "INFORMATIVO"}

GFP_TYPEOFEXECUTION = {
    "CALCULO": "Cálculos para FOPAG",
    "LOADER": "Carregadores de arquivos",
}

GFP_STATUS_FOLHAEVENTO = {
    "CT": "CONTABILIZADO",
    "NC": "NÃO CONTABILIZADO",
    "RB": "RECUSADO PELO BANCO",
    "BS": "BASE",
    "CE": "CONTABILIZADO EXTERNO",
}


class CNAE(models.Model):
    chave = models.CharField(max_length=8, unique=True)
    descricao = models.CharField(max_length=60)

    def __str__(self):
        return "{0} - {1}".format(self.chave, self.descricao)


class CNJRais(models.Model):
    chave = models.CharField(max_length=8, unique=True)
    descricao = models.CharField(max_length=60, verbose_name="Descrição")

    def __str__(self):
        return "{0} - {1}".format(self.chave, self.descricao)


@deprecated
class Previdencia(models.Model):
    class Meta:
        ordering = ["-ano_calendario", "-data_vigencia"]

    pessoa_juridica = models.ForeignKey(
        "rh.PessoaJuridica",
        on_delete=models.CASCADE,
        null=True,
        related_name="como_previdencia",
        verbose_name="Previdência",
    )
    identifier = models.PositiveSmallIntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "SOCIALSECURITY_IDENTIFIER"),
        verbose_name="Identificador",
    )
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE)
    dt_lancamento = models.DateTimeField(auto_now_add=True)
    ano_calendario = models.PositiveIntegerField(
        verbose_name="Ano Calendário", blank=True
    )
    data_vigencia = models.DateField(verbose_name="Vigência")
    regime_previdenciario = models.PositiveSmallIntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
        verbose_name="Regime previdenciário",
    )
    progressive_aliquot = models.BooleanField(
        verbose_name="Alícota Progressiva?", default=False
    )

    class FaixasNotFound(Exception):

        def __init__(self):
            Exception.__init__(
                self, "A Previdência %s não possui faixas cadastradas!" % self
            )

    def __str__(self):
        return "%s ANO CALENDARIO %s" % (self.pessoa_juridica, self.ano_calendario)

    @property
    def get_faixas(self):
        if not self.faixas.all():
            raise self.FaixasNotFound()
        return self.faixas.all()

    def save(self, *args, **kwargs):
        self.ano_calendario = self.data_vigencia.year
        super(Previdencia, self).save(*args, **kwargs)


@deprecated
class PrevidenciaFaixa(models.Model):
    class Meta:
        ordering = ["previdencia", "limite_inferior"]

    previdencia = models.ForeignKey(
        Previdencia,
        verbose_name="Previdência",
        related_name="faixas",
        on_delete=models.CASCADE,
    )
    limite_inferior = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Inferior"
    )
    limite_superior = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Superior"
    )
    pct = models.DecimalField(
        verbose_name="Porcentagem do Empregado", max_digits=5, decimal_places=2
    )
    pct_patronal = models.DecimalField(
        verbose_name="Porcentagem do Patrão", max_digits=5, decimal_places=2
    )
    reducer = models.DecimalField(
        verbose_name="Redutor", max_digits=16, decimal_places=4, blank=True, default=0
    )

    def __str__(self):
        return "Faixa de {0} até {1} para {2}".format(
            self.limite_inferior, self.limite_superior, self.previdencia
        )


class FatorRat(models.Model):
    class Meta:
        ordering = [
            "dt_inicio",
        ]
        db_table = "gfp_fatorrat"

    valor = models.DecimalField(verbose_name="Fator", max_digits=5, decimal_places=2)
    dt_inicio = models.DateField(verbose_name="Início Vigência")
    dt_fim = models.DateField(verbose_name="Fim Vigência", null=True, blank=True)

    @classmethod
    def vigente_em(cls, dt):
        fatores = cls.objects.filter(
            Q(dt_inicio__lte=dt) & (Q(dt_fim__gt=dt) | Q(dt_fim=None))
        )
        return float(fatores[0].valor) if fatores else 0.0

    @classmethod
    def vigente(cls):
        dt = datetime.now().date()
        return cls.vigente_em(dt)


class FatorFap(models.Model):
    class Meta:
        ordering = [
            "dt_inicio",
        ]
        db_table = "gfp_fatorfat"

    valor = models.DecimalField(verbose_name="Fator", max_digits=8, decimal_places=4)
    dt_inicio = models.DateField(verbose_name="Início Vigência")
    dt_fim = models.DateField(verbose_name="Fim Vigência", null=True, blank=True)

    @classmethod
    def vigente_em(cls, dt):
        fatores = cls.objects.filter(
            Q(dt_inicio__lte=dt) & (Q(dt_fim__gt=dt) | Q(dt_fim=None))
        )
        return float(fatores[0].valor) if fatores else 0.0

    @classmethod
    def vigente(cls):
        dt = datetime.now().date()
        return cls.vigente_em(dt)


class IRRF(models.Model):

    class Meta:
        ordering = ["-ano_calendario"]

    publicacao = models.ForeignKey(
        Publicacao, verbose_name="Publicação", on_delete=models.CASCADE
    )
    valor_dependente = models.DecimalField(max_digits=16, decimal_places=2)
    dt_lancamento = models.DateTimeField(auto_now_add=True)
    ano_calendario = models.PositiveIntegerField(verbose_name="Ano Calendário")
    data_vigencia = models.DateField(null=True)
    valor_isencao_65_anos = models.DecimalField(
        "Valor isenção 65 anos", max_digits=16, decimal_places=2, null=True, blank=True
    )

    deducao_benefica = models.DecimalField(
        verbose_name="Dedução mais benéfica",
        max_digits=16,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "ANO CALENDARIO {0}".format(self.ano_calendario)


class IRRFFaixa(models.Model):
    irrf = models.ForeignKey(
        IRRF, verbose_name="IRRF", related_name="faixas", on_delete=models.CASCADE
    )
    limite_inferior = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Inferior"
    )
    limite_superior = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Superior"
    )
    percentual = models.DecimalField(
        verbose_name="Aliquota", max_digits=6, decimal_places=3
    )
    desconto = models.DecimalField(
        verbose_name="Dedução", max_digits=16, decimal_places=2
    )

    class Meta:
        ordering = ["irrf", "limite_inferior"]

    def __str__(self):
        return "Faixa de {0} até {1} para {2}".format(
            self.limite_inferior, self.limite_superior, self.irrf
        )


class PeriodQueryset(models.QuerySet):
    def starting_in(self, data):
        return self.exclude(
            Q(ano__lt=data.year)
            | (Q(mes__lt=data.month) & Q(ano=data.year))
            | Q(mes=13)
        )

    def between(self, range_):
        return self.filter(
            (Q(ano=range_.first.year) | Q(ano=range_.last.year))
        ).exclude(
            (Q(mes__lt=range_.first.month) & Q(ano=range_.first.year))
            | (Q(mes__gt=range_.last.month) & Q(ano=range_.last.year))
        )


class Periodo(models.Model):
    mes = models.PositiveIntegerField(
        choices=Choice.get_choices_for("rh", "MONTHS"), verbose_name="Mês"
    )
    ano = models.PositiveIntegerField()
    auxilio_alimentacao = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Aux. Alimentação", null=True
    )
    auxilio_creche = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Aux. Creche", null=True
    )
    salario_minimo = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Salário Mínimo", null=True
    )
    salario_familia = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Salário Família", null=True
    )
    salario_teto_adm = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Salário Teto Adm", null=True
    )
    salario_teto_membros = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Salário Teto Membros", null=True
    )
    data_corte_ferias = models.DateField(
        verbose_name="Data Corte Férias", default=None, null=True, blank=True
    )

    objects = PeriodQueryset.as_manager()

    class Meta:
        unique_together = ("mes", "ano")
        ordering = ("-ano", "-mes")

    def __eq__(self, other) -> bool:
        return True if self.ano == other.ano and self.mes == other.mes else False

    def __lt__(self, other) -> bool:
        return (
            True
            if (self.ano == other.ano and self.mes < other.mes) or self.ano < other.ano
            else False
        )

    def __gt__(self, other):
        return (
            True
            if (self.ano == other.ano and self.mes > other.mes) or self.ano > other.ano
            else False
        )

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __ge__(self, other) -> bool:
        return self > other or self == other

    def __str__(self):
        return "%02d/%04d" % (self.mes, self.ano)

    @property
    def previous(self):
        return self.previous_period()

    @property
    def next(self):
        return self.next_period()

    @property
    def range(self):
        return NewDateRange.from_month(self.ano, min(self.mes, 12))

    @property
    def start_date(self):
        if not hasattr(self, "_start_date"):
            self._start_date = self.range.first
        return self._start_date

    @property
    def end_date(self):
        if not hasattr(self, "_end_date"):
            self._end_date = self.range.last
        return self._end_date

    @property
    def ano_mes_texto(self):
        """
        Property para retornar os valores de ano e mês no formato "ano - mês'
        e com o mês sendo texto
        """

        return f"{self.ano} - {self.get_mes_display().title()}"

    def save(self, *args, **kargs):
        if not self.pk:
            try:
                import calendar

                irrf = IRRF.objects.filter(
                    data_vigencia__lte=datetime(
                        self.ano, self.mes, calendar.monthrange(self.ano, self.mes)[1]
                    )
                ).order_by("-data_vigencia")
                if irrf.count() > 0:
                    self.irrf = irrf[0]
            except Exception:
                pass

        super(Periodo, self).save(*args, **kargs)

    # @property
    # def previous_period(self):
    #     month = self.mes
    #     year = self.ano

    #     def month_year(month, year):
    #         if month == 1:
    #             month = 13
    #             year = year - 1
    #         else:
    #             month = month - 1
    #         return month, year

    #     def find(month, year):
    #         return Periodo.objects.filter(mes=month, ano=year)

    #     month, year = month_year(month, year)
    #     period = find(month, year)
    #     while not period.exists():
    #         month, year = month_year(month, year)
    #         period = find(month, year)
    #         if not Periodo.objects.filter(ano=year).exists():
    #             break
    #     period = period.first()
    #     if period and (period.mes > self.mes and period.ano >= self.ano):
    #         period = None
    #     return period

    # @property
    # def next_period(self):
    #     month = self.mes
    #     year = self.ano

    #     def month_year(month, year):
    #         if month == 13:
    #             month = 1
    #             year = year + 1
    #         else:
    #             month = month + 1
    #         return month, year

    #     def find(month, year):
    #         return Periodo.objects.filter(mes=month, ano=year)

    #     month, year = month_year(month, year)
    #     period = find(month, year)
    #     while not period.exists():
    #         month, year = month_year(month, year)
    #         period = find(month, year)
    #         if not Periodo.objects.filter(ano=year).exists():
    #             break
    #     period = period.first()
    #     if period and (period.mes < self.mes and period.ano <= self.ano):
    #         period = None
    #     return period

    # alteração de lógica dos métodos 'previous_period' e 'next_period' vindas de TO em 2023-Jan
    # lógicas antigas deixados comentadas
    def previous_period(self, pos=1):
        fmonth = self.mes - pos
        fmonth_p = (fmonth // 13) if fmonth != 0 else -1
        month = fmonth - 13 * fmonth_p
        if month == 0:
            month = 13
            fmonth_p -= 1
        year = self.ano + fmonth_p
        return self.__class__.objects.filter(ano=year, mes=month).last()

    def next_period(self, pos=1):
        fmonth = self.mes + pos
        fmonth_r = fmonth % 13
        fmonth_p = fmonth // 13
        if fmonth_r == 0:
            fmonth_p -= 1
        month = fmonth - 13 * fmonth_p
        year = self.ano + fmonth_p

        return self.__class__.objects.filter(ano=year, mes=month).last()


@deprecated
class PeriodoPrevidencia(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    previdencia = models.ForeignKey(Previdencia, on_delete=models.CASCADE)

    def __str__(self):
        return "{periodo} para {previdencia}".format(
            periodo=self.periodo, previdencia=self.previdencia
        )


@to_search(
    [
        {"name": "titulo", "type": "text"},
        {"name": "abreviatura", "type": "text"},
        {"name": "ativo", "type": "boolean"},
    ]
)
class FolhaTipo(models.Model):

    class Meta:
        ordering = ("titulo",)

    titulo = models.CharField(max_length=30, verbose_name="Título")
    ativo = models.BooleanField(default=True)
    carater = models.SmallIntegerField(
        choices=(
            (1, "REMUNERATÓRIO"),
            (2, "INDENIZATÓRIO"),
            (3, "DE AUXÍLIO"),
        ),
        default=1,
    )
    principal = models.BooleanField(default=False)
    modelo = models.ForeignKey(
        "gfp.FolhaModelo",
        verbose_name="Modelo",
        related_name="folhas",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    processo = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Processo"
    )
    publicacao_processo = models.ForeignKey(
        "rh.Publicacao",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Publicação do Processo",
    )
    margem = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Margem Consignável", default=0
    )
    abreviatura = models.CharField(
        max_length=20, verbose_name="Abreviatura", blank=True, default=""
    )
    numero = models.CharField(max_length=4, unique=True, verbose_name="Número")

    def save(self, *args, **kargs):
        self.principal is True and FolhaTipo.objects.filter(principal=True).update(
            principal=False
        )
        super(FolhaTipo, self).save(*args, **kargs)

    def __str__(self):
        return "%s%s" % (
            self.titulo if not self.abreviatura else self.abreviatura,
            "*" if self.ativo is False else "",
        )


@deprecated
class Calculo(models.Model):

    class Meta:
        ordering = ("path",)

    slug = models.CharField(max_length=128, null=True, unique=True)
    path = models.CharField(max_length=128, null=True, unique=True)
    titulo = models.CharField(max_length=128, blank=True)
    descricao = models.CharField(max_length=128, null=True)
    objeto = models.CharField(max_length=128, choices=RunCodeManager.get_choices())
    typeof = models.CharField(
        max_length=20,
        choices=list(GFP_TYPEOFEXECUTION.items()),
        default="CALCULO",
        db_index=True,
        null=False,
    )

    def __str__(self):
        return self.path

    def delete(self, *args, **kargs):
        if self.eventos.filter().exists():
            raise Exception(
                "Não posso apagar este calculo, ele esta associado a pelo menos um evento."
            )

        models.Model.delete(self, *args, **kargs)

    def save(self, *args, **kargs):
        if self.pk is None:
            cls = None
            try:
                exec("cls = calculo.{0}".format(self.objeto))
                self.titulo = cls.titulo
            except Exception:
                self.titulo = "Desconhecido"

        models.Model.save(self, *args, **kargs)


@to_search(
    [
        {"name": "periodo__ano", "type": "number"},
        {"name": "tipo_folha__titulo", "type": "text"},
    ]
)
class Folha(AuditTimestampModel):

    class Meta:
        unique_together = ("periodo", "tipo_folha", "complement")
        ordering = ("-periodo__ano", "-periodo__mes", "tipo_folha__titulo")
        permissions = (
            ("can_process_payroll", 'Mudar estado da folha para "processada"'),
            ("can_close_payroll", 'Mudar estado da folha para "fechada"'),
            (
                "can_change_status_payroll",
                "Mudar estado da folha entre produção/análise",
            ),
        )

    DEFAULT_USER = "athenas"

    AUDITABLE = {
        "fields": ["periodo", "tipo_folha", "folha_anterior", "status", "dt_pagamento"]
    }

    periodo = models.ForeignKey(
        "gfp.Periodo",
        verbose_name="Período",
        related_name="folhas",
        on_delete=models.CASCADE,
    )
    tipo_folha = models.ForeignKey(
        "gfp.FolhaTipo",
        verbose_name="Tipo de Folha",
        related_name="folhas",
        on_delete=models.CASCADE,
    )
    folha_anterior = models.ForeignKey(
        "gfp.Folha",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Folha anterior",
        related_name="folhas_copiadas",
    )
    fechado = models.BooleanField(verbose_name="Fechado", default=False)
    processado = models.BooleanField(verbose_name="processado", default=False)
    ci = models.BooleanField(verbose_name="Conferido", default=False)
    fechado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Responsável pelo fechamento",
        related_name="folhas_fechadas",
        blank=True,
    )
    processado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Responsável pela execução",
        related_name="folhas_executadas",
        blank=True,
    )
    ci_por = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Responsável pelo validação",
        related_name="folhas_validadas",
        blank=True,
    )
    dt_fechamento = models.DateTimeField(
        verbose_name="Data do Fechamento", null=True, blank=True
    )
    dt_processado = models.DateTimeField(
        verbose_name="Data da Execução", null=True, blank=True
    )
    dt_ci = models.DateTimeField(
        verbose_name="Data da Conferência", null=True, blank=True
    )
    dt_pagamento = models.DateField(
        verbose_name="Data de Pagamento", null=True, blank=True
    )
    dt_corte = models.DateField(verbose_name="Data de Corte", null=True, blank=True)
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "STATUS_PAYROLL"),
        verbose_name="Status",
        default=1,
        blank=True,
    )
    dt_criacao = models.DateTimeField(auto_now_add=True)
    unicode_cache = models.CharField(max_length=200, db_index=True, blank=True)
    complement = models.SmallIntegerField(
        verbose_name="Complemento",
        choices=Choice.get_choices_for("gfp", "COMPLEMENT_PAYROLL"),
        default=0,
        blank=True,
    )

    paycheck_locked = models.BooleanField(
        verbose_name="Bloquear Contra-cheques?", default=False
    )
    apply_models = models.BooleanField(
        verbose_name="Aplicar modelos de lançamentos?", default=True
    )
    available_pvf = models.BooleanField(
        verbose_name="Disponível Vida Funcional", default=False
    )

    class CopyAbortedFromAndToEqual(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Copia interrompida uma vez que a origem é igual o destino."
            )

    class CanNotClearFolhaClosed(Exception):
        def __init__(self):
            Exception.__init__(self, "Não posso limpar uma folha fechada.")

    class AlreadyExists(Exception):
        def __init__(self):
            Exception.__init__(self, "Não posso criar uma folha que já existe.")

    class ClosedFolha(Exception):
        def __init__(self):
            Exception.__init__(
                self, "A folha já se encontra processada e não pode sofrer alterações!"
            )

    class OpenedPayroll(Exception):
        def __init__(self):
            Exception.__init__(self, "A folha se encontra aberta para modificações!")

    class ChangeStatusNotPermited(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Por motivos de segurança essa alteração de status da folha não pode ser efetuada!",
            )

    class NotClosedBeforeConfirm(Exception):
        def __init__(self):
            Exception.__init__(
                self, "A folha não pode ser fechada antes de totalmente confirmada!"
            )

    def feedback(self, *args, **kwargs):
        log.info("TASK EMPTY..")

    @property
    def date_range(self):
        return NewDateRange.from_month(self.periodo.ano, min(self.periodo.mes, 12))

    @property
    def previous(self):
        return self.folha_anterior

    @property
    def next(self):
        if self.folhas_copiadas.filter(tipo_folha=self.tipo_folha).exists():
            return self.folhas_copiadas.filter(tipo_folha=self.tipo_folha).first()
        elif self.folhas_copiadas.filter().exists():
            return self.folhas_copiadas.first()
        else:
            return None

    def _clear(self):
        if self.status in [3, 4]:
            raise Folha.CanNotClearFolhaClosed()
        else:
            for p in self.paychecks.all():
                p.delete()

    def _do_copy_eventos_contracheque(
        self, paycheck, paycheck_to, eventos=[], task=None, type_of_copy="CHANGED"
    ):
        result = {"INFO": {"DELETED": []}, "WARN": {}, "ERROR": {}, "total": 0}

        fevs = paycheck.lancamentos.filter()
        if eventos:
            fevs = fevs.filter(evento__numero__in=eventos)

        if type_of_copy == "NEW":  # Apagando eventos copiados anteriormente
            for e in paycheck_to.lancamentos.filter(copia_de__contracheque=paycheck):
                e.delete()

        for ef in fevs.filter().order_by("evento__numero"):
            if ef.evento.lancamento == "T" and (
                (ef.parcela + ef.installments_paid) > ef.prazo or ef.prazo == 0
            ):
                result["INFO"]["DELETED"].append(
                    "Fim do evento {0} para o servidor {1}, por atingir o prazo final.".format(
                        ef.evento, ef.servidor.matricula
                    )
                )
                result["total"] += 1
            elif ef.evento.lancamento == "U":
                result["INFO"]["DELETED"].append(
                    "Fim do evento {0} para o servidor {1}, por ser um evento temporário único.".format(
                        ef.evento, ef.servidor.matricula
                    )
                )
                result["total"] += 1
            else:
                try:
                    # Verificando se o evento ja existe no contracheque (paycheck_to)
                    # log.debug(
                    # 'DO SAVING FOLHAEVENTO %s _do_copy_eventos_contracheque', ef.contracheque.servidor.matricula)
                    value = ef.valor
                    contrib = ef.patronal
                    base_contrib = ef.base_previdencia
                    if ef.paycheck_difference:
                        if ef.paycheck_difference.installments == (
                            ef.parcela + ef.installments_paid
                        ):
                            # ULTIMA PARCELA DEVE FAZER O ACERTO DOS CENTAVOS
                            # log.debug('PD: %s' % ef.paycheck_difference.payables)
                            value = abs(ef.paycheck_difference.payable.get("value", 0))
                            contrib = ef.paycheck_difference.payable.get(
                                "employer_contribution", 0
                            )
                            base_contrib = value
                            log.debug(
                                "LAST-INSTALMMET: %s/%s %s = %s/%s"
                                % (
                                    ef.parcela + ef.installments_paid,
                                    ef.paycheck_difference.installments,
                                    ef.paycheck_difference._payments(),
                                    value,
                                    contrib,
                                )
                            )
                        elif ef.installments_paid > 1:
                            log.debug(
                                "CHANGE-INSTALMMET: %s(%s)/%s %s"
                                % (
                                    ef.parcela,
                                    ef.installments_paid,
                                    ef.paycheck_difference.installments,
                                    ef.paycheck_difference._payments(),
                                )
                            )
                            value = ef.valor / ef.installments_paid
                            contrib = ef.patronal / ef.installments_paid
                            base_contrib = value

                    references = [
                        paycheck_to.folha.periodo.ano,
                        paycheck_to.folha.periodo.mes,
                    ]
                    if ef.paycheck_difference:
                        references = [ef.reference_year, ef.reference_month]
                    else:
                        if references == [ef.reference_year, ef.reference_month]:
                            ref_date = date(
                                ef.reference_year, ef.reference_month, 1
                            ) + relativedelta(months=1)
                            references = [ref_date.year, ref_date.month]

                    ef_to, created = paycheck_to.lancamentos.get_or_create(
                        servidor=ef.contracheque.servidor,
                        evento=ef.evento,
                        info=ef.info,
                        reference_month=references[1],
                        reference_year=references[0],
                        defaults={
                            "copia_de": ef,
                            "lancamento": ef.lancamento,
                            "qnt": ef.qnt,
                            "qnt_max": ef.evento.max_quantity,
                            "parcela": (
                                (ef.parcela + ef.installments_paid)
                                if ef.evento.lancamento == "T"
                                else 0
                            ),
                            "installments_paid": 1,
                            "prazo": ef.prazo if ef.evento.lancamento == "T" else 0,
                            "pct": ef.pct,
                            "valor": value,
                            "valor_base": ef.valor_base,
                            "patronal": contrib,
                            "info": ef.info,
                            "base_previdencia": base_contrib,
                            "json_calc_vars": ef.json_calc_vars,
                            "paycheck_difference": ef.paycheck_difference,
                            "rra_employee": ef.rra_employee,
                            "automated": ef.evento.automated
                            or (ef.automated and ef.paycheck_difference is not None),
                            "insertion_type": ef.insertion_type,
                            "calculation": ef.calculation,
                            "cid": ef.cid,
                        },
                    )
                    # log.debug('EF_TO: (%s) %s - %s: %s' % (ef.pk, ef.evento.numero, ef_to.json_calc_vars, ef.copia_de.pk))
                except Exception as e:
                    # log.debug(('EF_TO EXP (%s) %s' % (ef, str(e)))
                    if task:
                        task.info(
                            "ERRO ao copiar EVENTO: %s - %s!"
                            % (ef.evento, paycheck_to.servidor)
                        )
                    raise e
                else:
                    if float(ef_to.valor) > 0.009 or float(ef_to.patronal) > 0.009:
                        # log.debug('SAVING FOLHAEVENTO %s: %s' % (ef_to.servidor.matricula, ef_to.old_fields.keys()))
                        ef_to.save()
        return result

    def copy_to(
        self, to, to_exists=False, to_can_clear=False, task=None, registrations=[]
    ):

        task = (
            TaskSession.start_execution("Copia da folha - %s > %s" % (self, to))
            if not task
            else task
        )

        if to.pk == self.pk:
            task.info("ERRO ao copiar FOLHA: folha de origem e destinos iguais!", 3)
            task.finish_execution("ERROR")
            raise Folha.CopyAbortedFromAndToEqual()
        else:
            lock_file = Locker.create_lock("copy_payroll")
            if to_exists and to_can_clear:
                task["pctText"] = "LIMPANDO FOLHA existente: %s!" % to
                to._clear()
            elif to_exists:
                task.info("ERRO ao copiar FOLHA: %s já existe!" % to, 3)
                task.finish_execution("ERROR")
                Locker.remove_lock(lock_file)
                raise Folha.AlreadyExists()

            to.dt_criacao = datetime.now()
            to.dt_pagamento = self.dt_pagamento + relativedelta(months=1)
            to.folha_anterior = self
            to.save()

            query = self.paychecks.all()
            if registrations:
                query = query.filter(servidor__matricula__in=registrations)

            if not query:
                log.info("A folha %s não possui contracheques a serem copiados!")
                task.info(
                    "A folha %s não possui contracheques para serem copiados!" % self
                )
            else:
                log.info("COPIANDO FOLHA: %s >> %s" % (self, to))

                task["total"] = query.count()
                task["pct"] = 1

                for paycheck in query.order_by("servidor", "-pensioner"):
                    # log.debug(('>>> CRIANDO CONTRACHEQUE: %s' % paycheck)
                    paycheck_to, created = ContraCheque.objects.get_or_create(
                        folha=to,
                        servidor=paycheck.servidor,
                        pensioner=paycheck.pensioner,
                        defaults={
                            "situacao_funcional": paycheck.situacao_funcional,
                            "situacao_previdenciaria": paycheck.situacao_previdenciaria,
                            "cargo_efetivo": paycheck.cargo_efetivo,
                            "referencia_efetivo_cache": paycheck.referencia_efetivo_cache,
                            "cargo_comissao": paycheck.cargo_comissao,
                            "referencia_comissao_cache": paycheck.referencia_comissao_cache,
                            "cargo_eletivo": paycheck.cargo_eletivo,
                            "referencia_eletivo_cache": paycheck.referencia_eletivo_cache,
                            "data_admissao": paycheck.data_admissao,
                            "lotacao": paycheck.lotacao,
                            "dependentes_ir": paycheck.dependentes_ir,
                            "dependentes_sf": paycheck.dependentes_sf,
                            "margem_consignada_total": paycheck.margem_consignada_total,
                            "margem_consignada_livre": paycheck.margem_consignada_livre,
                            "base_previdenciaria": paycheck.base_previdenciaria,
                            "base_ir": paycheck.base_ir,
                            "dado_bancario_pessoa": paycheck.dado_bancario_pessoa,
                            "total_bruto": paycheck.total_bruto,
                            "total_liquido": paycheck.total_liquido,
                        },
                    )
                    # if created: log.info('ContraCheque criado - %s' % paycheck_to)
                    # log.debug(('>>> CONTRACHEQUE CRIADO: %s' % paycheck)
                    task["pct"] += 1

                    try:
                        # Copia eventos sem recalcular.
                        # log.debug(('>>> COPIANDO EVENTOS DO CONTRACHEQUE CRIADO: %s' % paycheck.servidor)
                        self._do_copy_eventos_contracheque(
                            paycheck, paycheck_to, task=task
                        )
                        # log.debug(('>>> COPIADO EVENTOS DO CONTRACHEQUE CRIADO: %s' % paycheck.servidor)

                        # log.debug(('OK >> RECALCULANDO CONTRACHEQUE (%s): %s' % (
                        #     ['%s/%s' % (
                        #         fe.evento.numero,
                        #         fe.valor) for fe in paycheck_to.lancamentos.all()], paycheck_to.servidor))
                        if (
                            not paycheck_to.pensioner
                        ):  # Recalculating only for employeers, not for pensioners
                            paycheck_to.recalculate(
                                consolidate=ContraCheque.ALL, task=task
                            )

                        # log.debug(('OK >> CONTRACHEQUE RECALCULADO: %s' % (paycheck_to.servidor))
                        if not paycheck_to.lancamentos.exists():
                            # NOTIFY Notificar ao usuário que está copiando que o contracheque foi apagado
                            log.info(
                                "APAGANDO contracheque por não ter lançamentos: %s"
                                % paycheck_to.servidor
                            )
                            task.info(
                                "CONTRACHEQUE APAGADO por não ter lançamentos: %s"
                                % paycheck_to.servidor,
                                2,
                            )
                            paycheck_to.delete()
                        elif paycheck_to.total_liquido <= 0:
                            task.info(
                                "CONTRACHEQUE ZERADO ou NEGATIVO: %s"
                                % paycheck_to.servidor,
                                2,
                            )

                    except Exception as e:
                        log.exception(e)
                        log.info("ERRO Copiando contracheque: %s" % paycheck.servidor)
                        task.info(
                            "ERRO ao copiar CONTRACHEQUE: %s\n%s"
                            % (paycheck.servidor, str(e)),
                            3,
                        )

                to.summarize(task=task)

            Locker.remove_lock(lock_file)
            task.finish_execution()

    def recalculate_with_tasks(self, task=None):
        # lock_file = Locker.create_lock('recalculating_payroll')
        # task = TaskSession.start_execution('Recalculo da folha %s' % self) if not task else task
        q_paychecks = self.paychecks.filter(pensioner=None)
        factor = 100.0 / q_paychecks.count()
        pct = 0.0

        if self.status in [1, 2]:
            for paycheck in q_paychecks:
                msg = ""
                type_of = 2
                try:
                    paycheck.recalculate(consolidate=ContraCheque.ALL, task=task)
                except Exception as e:
                    # log.info('Ocorreu um erro recalculando para o servidor %s' % paycheck.servidor.pessoa_fisica)
                    msg = "ERRO ao RECALCULAR CONTRACHEQUE:  %s" % paycheck.servidor
                    type_of = 3
                    # task.info('ERRO ao RECALCULAR CONTRACHEQUE:  %s' % paycheck.servidor, 3)
                    log.exception(e)
                else:
                    if not paycheck.lancamentos.exists():
                        # NOTIFY Notificar ao usuário que está copiando que o contracheque foi apagado
                        # log.info('APAGANDO contracheque por não ter lançamentos: %s' % paycheck.servidor)
                        msg = (
                            "CONTRACHEQUE APAGADO por não ter lançamentos: %s"
                            % paycheck.servidor
                        )
                        type_of = 2
                        # task.info('CONTRACHEQUE APAGADO por não ter lançamentos: %s' % paycheck.servidor, 2)
                        paycheck.delete()
                    elif paycheck.total_liquido <= 0 and not (
                        paycheck.employee_pays_pension == 2
                        and paycheck.pensioner is None
                    ):
                        # task.info('CONTRACHEQUE ZERADO ou NEGATIVO: %s' % paycheck.servidor, 2)
                        msg = "CONTRACHEQUE ZERADO ou NEGATIVO: %s" % paycheck.servidor
                        type_of = 2

                pct += factor
                self.feedback(pct=pct, msg=msg, type_of=type_of)
                # log.debug(('TASK* %0.1f/%d' % (pct, q_paychecks.count()))
        else:
            msg = (
                "ERRO ao RECALCULAR FOLHA: %s se encontra processada/fechada e não pode ser recalculada!"
                % self
            )
            # task.info(
            #    'ERRO ao RECALCULAR FOLHA: %s se encontra processada/fechada e não pode ser recalculada!' % self, 2)
            self.feedback(msg=msg, type_of=3)

    def recalculate(self, task=None):
        lock_file = Locker.create_lock("recalculating_payroll")
        task = (
            TaskSession.start_execution("Recalculo da folha %s" % self)
            if not task
            else task
        )

        task["total"] = self.paychecks.count()
        task["pct"] = 1
        if self.status in [1, 2]:
            for cc in self.paychecks.all():
                try:
                    cc.recalculate(task=task)
                except Exception as e:
                    # log.info('Ocorreu um erro recalculando para o servidor %s' % cc.servidor.pessoa_fisica)
                    task.info("ERRO ao RECALCULAR CONTRACHEQUE:  %s" % cc.servidor, 3)
                    log.exception(e)
                else:
                    if not cc.lancamentos.exists():
                        # NOTIFY Notificar ao usuário que está copiando que o contracheque foi apagado
                        log.info(
                            "APAGANDO contracheque por não ter lançamentos: %s"
                            % cc.servidor
                        )
                        task.info(
                            "CONTRACHEQUE APAGADO por não ter lançamentos: %s"
                            % cc.servidor,
                            2,
                        )
                        cc.delete()
                    elif cc.total_liquido <= 0:
                        task.info(
                            "CONTRACHEQUE ZERADO ou NEGATIVO: %s" % cc.servidor, 2
                        )
                finally:
                    task["pct"] += 1

            self.summarize(task=task)
        else:
            task.info(
                "ERRO ao RECALCULAR FOLHA: %s se encontra processada/fechada e não pode ser recalculada!"
                % self,
                2,
            )

        task.finish_execution()
        Locker.remove_lock(lock_file)

    def consolidate_payroll(self, task=None, control_by_lock=True):
        # TODO: AVALIAR SE A CRIAÇÃO DE LOCK AINDA É NECESSÁRIA
        if control_by_lock:
            lock_file = Locker.create_lock("consolidate_payroll")
            task = (
                TaskSession.start_execution("Consolidando folha %s" % self)
                if not task
                else task
            )
            task["total"] = self.paychecks.count()
            task["pct"] = 1
        for cc in self.paychecks.all():
            try:
                res = cc.consolidate(changes=ContraCheque.ALL)
                if res and control_by_lock:
                    task.info("Contra-cheque do servidor %s consolidado." % cc.servidor)
                cc.save()
            except Exception as e:
                if control_by_lock:
                    task.info("ERRO AO CONSOLIDAR CONTRACHEQUE: %s" % cc.servidor)
                log.exception(e)
            finally:
                if control_by_lock:
                    task["pct"] += 1

        if control_by_lock:
            task.finish_execution()
            Locker.remove_lock(lock_file)

    def apply_model(self, model, task=None):

        lock_file = Locker.create_lock("apply_model")
        task = (
            TaskSession.start_execution("Aplicando o modelo %s em %s" % (model, self))
            if not task
            else task
        )

        query = model.get_all_new_employees(self)
        count = 0

        task["total"] = query.count()

        for s in query:
            count += 1

            log.info(">>>>>>>>>>>>>> APLICANDO MODELO PARA %s" % s)
            paycheck, created = ContraCheque.objects.get_or_create(
                servidor=s, folha=self, pensioner=None
            )
            try:
                paycheck.apply_model(model, task=task)
                # log.debug(('APPLY MODEL RESULT: (%s) %s' % (((res or created or False) and True), s))
                paycheck.consolidate(task=task)
            except Exception as e:
                log.exception(e)
                task.info("ERRO ao APLICAR modelo em %s" % paycheck.servidor, 3)
            else:
                # log.debug((">>>>>>>>>>>> MODELO %s APLICADO EM %s" % (model, paycheck))
                if not paycheck.lancamentos.all():
                    paycheck.delete()
                    if not created:
                        task.info(
                            "CONTRACHEQUE APAGADO por não ter lançamentos: %s"
                            % paycheck.servidor,
                            2,
                        )

            task["pct"] = count

        self.summarize(task=task)

        task.finish_execution()
        Locker.remove_lock(lock_file)

    def change_status(self, status, save=True):
        if status != self.status:
            if status not in list(GFP_STATUS_WORKFLOW[self.status].keys()):
                raise self.ChangeStatusNotPermited()

            was_processed = self.is_processed
            was_closed = self.is_closed

            if not get_current_user().has_perm(
                GFP_STATUS_WORKFLOW[self.status][status]
            ):
                raise UserHasNotPermission(GFP_STATUS_WORKFLOW[self.status][status])

            self.status = status

            # if force and was_processed and not self.is_processed:
            if was_processed and not self.is_processed:
                self.processado_por = None
                self.dt_processado = None

            # if force and was_closed and not self.is_closed:
            if was_closed and not self.is_closed:
                self.fechado_por = None
                self.dt_fechamento = None

            if status == 3:
                if self.lancamentos.filter(
                    Q(confirma_folha=None) | Q(confirma_controle=None)
                ):
                    raise self.NotClosedBeforeConfirm()
                self.dt_fechamento = datetime.now()
                self.fechado_por = get_current_user()
            elif status == 4:
                self.dt_processado = datetime.now()
                self.processado_por = get_current_user()

            if save:
                self.save()

    def evaluate_differences(self, employeers=[], task=None, number_events=[]):
        # log.debug(('>>>>>>>>> ED: %s' % task)
        lock_file = Locker.create_lock("evaluate_differences")
        task_ = (
            TaskSession.start_execution("Verificação de diferenças - %s" % self)
            if not task
            else task
        )
        dr = NewDateRange.from_month(self.periodo.ano, min(self.periodo.mes, 12))
        employeers = []

        # Procurando por servidores que não entraram na folha
        for e in Servidor.objects.all():
            if (
                e.data_exercicio
                and e.data_exercicio <= dr.last
                and (e.data_desligamento is None or e.data_desligamento > dr.last)
            ):
                paycheck, created = self.paychecks.get_or_create(
                    servidor=e, pensioner=None
                )
                if created:
                    log.debug("EVALUTE - CREATING CC: %s" % paycheck)

        q_paychecks = self.paychecks.all()
        if employeers:
            q_paychecks = q_paychecks.filter(servidor__in=employeers)

        task_["total"] = q_paychecks.count()
        task_["pct"] = 1

        for paycheck in q_paychecks:
            diff = paycheck.evaluate_differences(number_events=number_events)
            if diff["changed"]:
                task_.send_message(
                    "DIFERENÇA(S) ENCONTRADA para %s" % (paycheck.servidor), 2
                )
                # log.debug('EVAL DIFF: %s: %s' % (paycheck.servidor.matricula, diff))
            task_["pct"] += 1
            if not paycheck.lancamentos.exists():
                paycheck.delete()

        if not task:
            task_.finish_execution()
        Locker.remove_lock(lock_file)

    def create_difference(
        self,
        q_entries,
        info="",
        identifier=None,
        status=1,
        installments=1,
        correction_factor_identifier=None,
    ):
        if q_entries:
            entry = q_entries[0]
            employee = entry.contracheque.servidor
            event = entry.evento
            # log.debug(('CD >> 1 IGNORE: %s ENTRY: %s, CFI: %s' % (status, entry, correction_factor_identifier))
            # IMPLEMENT CONTEXT with transaction ATOMIC
            pd, created = PaycheckDifference.objects.get_or_create(
                employee=employee,
                event=event,
                reference_year=entry.contracheque.folha.periodo.ano,
                reference_month=entry.contracheque.folha.periodo.mes,
                identifier=identifier,
                installments=installments,
                correction_factor_identifier=correction_factor_identifier,
                status=status,
                defaults={"title": info},
            )

            # log.debug(('1 CDI: DT: %s' % pd.diff_type)
            pd.create_diff_items(q_entries)
            # log.debug(('2 CDI: DT: %s' % pd.diff_type)

            if not (pd.differences["value"] or pd.differences["employer_contribution"]):
                pd.delete()
                return None

            return pd
        return None

    def apply_differences_for(
        self,
        payrolls=[],
        entries=[],
        employeers=[],
        task=None,
        identifier=None,
        info="",
        status=1,
        installments=1,
        correction_factor_identifier=None,
    ):
        # log.debug(('>>>>>>>>> ADF: (I:%s) %s' % (status, task))
        task_ = NullTaskSession() if not task else task
        if not payrolls and not entries:
            task_.send_message(
                "Nenhuma folha ou lançamentos indicados para gerar as diferenças!"
            )

        else:
            if entries:
                query = entries
            else:
                query = FolhaEvento.with_differences.filter(folha__in=payrolls)

            if employeers:
                query = query.filter(contracheque__servidor__in=employeers)

            task_["pct"] = 1

            cfg = Configuration.get_or_create("gfp")
            process_dif_single = cfg.get(
                "process_difference_single", default="0", type_of=1
            )

            addeds = errors = []

            if eval(process_dif_single):

                task_["total"] = query.count()
                for el in query:
                    try:
                        with transaction.atomic():
                            pd = self.create_difference(
                                query.filter(pk=el.pk),
                                info=el.info,
                                identifier=identifier,
                                status=status,
                                installments=installments,
                                correction_factor_identifier=correction_factor_identifier,
                            )

                            if status not in [6, 7] and pd:
                                addeds += pd.aplly(self, info=info)

                    except Evento.DoesNotExist as e:
                        errors.append(e)
                    except Exception as e:
                        raise e
            else:
                query_values = query.values(
                    "contracheque__servidor",
                    "evento",
                    "reference_year",
                    "reference_month",
                ).distinct()
                task_["total"] = query_values.count()
                for el in query_values:
                    q1 = query.filter(**el)
                    ev = q1.first().evento
                    if ev.separate_for_info_event:
                        for elq1 in q1.values("info").distinct():
                            q2 = q1.filter(**elq1)
                            pd = self.create_difference(
                                q2,
                                identifier=identifier,
                                status=status,
                                installments=installments,
                                correction_factor_identifier=correction_factor_identifier,
                            )
                    else:
                        pd = self.create_difference(
                            q1,
                            info=info,
                            identifier=identifier,
                            status=status,
                            installments=installments,
                            correction_factor_identifier=correction_factor_identifier,
                        )

                    if status not in [6, 7] and pd:
                        addeds += pd.aplly(self, info=info)

            paychecks = set([fe.contracheque for fe in addeds])
            for paycheck in paychecks:
                paycheck.recalculate(task=task)

            task_["pct"] += 1

    def apply_differences_previous_payroll(self, task=None):
        # log.debug(('>>>>>>>>> ADPP: %s' % task)
        prev_payroll = self.folha_anterior
        task_ = (
            TaskSession.start_execution("Gerando diferenças para - %s" % self)
            if not task
            else task
        )
        if prev_payroll:
            self.apply_differences_for(
                payrolls=[prev_payroll],
                task=task_,
                identifier="DIF%04d%02d"
                % (prev_payroll.periodo.ano, prev_payroll.periodo.mes),
                info="DIF. %s %02d/%04d"
                % (self.tipo_folha, prev_payroll.periodo.mes, prev_payroll.periodo.ano),
            )
        else:
            task_.send_message(
                "A folha %s não possui uma folha anterior! Indique a folha anterior e tente novamente."
                % self
            )
        if not task:
            task_.finish_execution()

    def verify_totals_payroll(self, payroll):

        # RESUMO GERAL -------------------------------------------------------
        query_ow = OverviewReport.objects.filter(payroll=payroll)
        p_ow = query_ow.filter(type_of_entry=1).aggregate(
            Sum("value"), Sum("employer_contribution"), Sum("quantity")
        )
        d_ow = query_ow.filter(type_of_entry=2).aggregate(
            Sum("value"), Sum("employer_contribution"), Sum("quantity")
        )
        total_net_ow = round(
            float(p_ow["value__sum"] or 0.00) + float(d_ow["value__sum"] or 0.00), 2
        )
        total_ow = round(
            float(p_ow["value__sum"] or 0.00)
            + float(p_ow["employer_contribution__sum"] or 0.00)
            + float(d_ow["employer_contribution__sum"] or 0.00),
            2,
        )

        # NL -----------------------------------------------------------------
        query_fr = FinancialReportPayroll.objects.filter(payroll=payroll)
        nl_fr = query_fr.filter(account_plan__finalidade=1).aggregate(
            Sum("value"), Sum("quantity")
        )
        nl_net_fr = query_fr.filter(
            account_plan__finalidade=1, account_plan__plano__composes_total_net=True
        ).aggregate(Sum("value"), Sum("quantity"))
        total_net_nl_fr = round(float(nl_net_fr["value__sum"] or 0.00), 2)
        total_nl_fr = round(float(nl_fr["value__sum"] or 0.00), 2)

        # PD -----------------------------------------------------------------
        pd_fr = query_fr.filter(account_plan__finalidade=2).aggregate(
            Sum("value"), Sum("quantity")
        )
        pd_net_fr = query_fr.filter(
            account_plan__finalidade=2, account_plan__plano__composes_total_net=True
        ).aggregate(Sum("value"), Sum("quantity"))
        total_net_pd_fr = round(float(pd_net_fr["value__sum"] or 0.00), 2)
        total_pd_fr = round(float(pd_fr["value__sum"] or 0.00), 2)

        # LIQUIDO BANCARIO ---------------------------------------------------
        query_nb = ContraCheque.objects.filter(folha=payroll).exclude(
            employee_pays_pension=2, pensioner__isnull=True
        )
        net_nb = query_nb.aggregate(Sum("total_liquido"))
        total_net_nb = round(float(net_nb["total_liquido__sum"] or 0.00), 2)

        result = {
            "SUCCESS": total_ow == total_nl_fr == total_pd_fr
            and total_net_ow == total_net_nl_fr == total_net_pd_fr == total_net_nb,
            "RESUMO GERAL": (total_ow, total_net_ow),
            "NL/RESUMO CONTABIL": (total_nl_fr, total_net_nl_fr),
            "PD": (total_pd_fr, total_net_pd_fr),
            "BANCÁRIO": (0, total_net_nb),
        }

        return result

    def hit_payroll_with_sefip(self, simulate=True, task=None):
        new_task = not task
        if self.status in [1, 2]:
            cfg = Configuration.get_or_create("gfp")
            inss_id = int(cfg.get("inss"))
            ss = (
                SocialSecurity.objects.filter(
                    legal_person_id=inss_id, start_validity__lte=self.date_range.last
                )
                .order_by("start_validity")
                .last()
            )
            pct_ss = ss.percentage_of_employer

            # pct_rat_ad = FatorRat.vigente_em(self.date_range.last) / 100 * FatorFap.vigente_em(self.date_range.first)
            # events = Evento.objects.filter(tags__label='rgps').values_list('numero')
            # # events = getattr(settings, 'EVENTOS_INSS', ['5400', '91000'])
            # maternity = self.lancamentos.filter(evento__tags__label='salariomaternidade').aggregate(vb=Sum('valor'))['vb'] or 0.0
            # q = self.lancamentos.filter(evento__numero__in=events).aggregate(vb=Sum('valor_base'), pat=Sum('patronal'))

            # vb, pat = (q['vb'] - maternity) or 0, q['pat'] or 0

            # lógica alterada vinda de TO em 2023-Jan
            # alteração no condicional da query e nos campos
            pct_rat_ad = decimal.Decimal(
                FatorRat.vigente_em(self.date_range.last)
                / 100
                * FatorFap.vigente_em(self.date_range.first)
            )
            events = Evento.objects.filter(tags__label="rgps").values_list("numero")
            maternity = self.lancamentos.filter(
                evento__tags__label__in=["salariomaternidade", "salariomaternidade13"]
            ).aggregate(vb=Coalesce(Sum("valor"), decimal.Decimal(0.0)))["vb"]
            q = self.lancamentos.filter(evento__numero__in=events).aggregate(
                vb=Coalesce(Sum("valor_base"), decimal.Decimal(0.0)),
                pat=Coalesce(Sum("patronal"), decimal.Decimal(0.0)),
            )
            vb, pat = q["vb"] - maternity, q["pat"]
            v_pat = int(vb * pct_ss) / 100.0
            v_rat = int(vb * (pct_rat_ad) * 100) / 100.0
            v = v_pat + v_rat
            dif = round(v - float(pat), 2)

            # print '%s * %s + %s * %s = %s <> %s (%s)' % (vb, pct_ss, vb, pct_rat_ad, v, pat, dif),
            if task:
                task.info(f"Totais SEFIP: Patronal ({v_pat}) RAT ({v_rat})!", 1)
            if dif != 0:
                fe = self.lancamentos.filter(evento__numero__in=events).first()
                fe.patronal += decimal.Decimal(round(dif, 2))
                fe.save()
                if task:
                    task.info(
                        "ACERTANDO SEFIP (R$ %s) no contrachque %s!"
                        % (dif, fe.contracheque),
                        2,
                    )

    def summarize(self, simulate=True, task=None):
        from rh.gfp.planoconta.models import Plano as Plan

        if self.status in [1, 2]:

            q_entries = self.lancamentos.exclude(
                contracheque__employee_pays_pension=2,
                contracheque__pensioner__isnull=True,
            )
            years = [
                y["reference_year"]
                for y in q_entries.order_by("reference_year")
                .values("reference_year")
                .distinct()
            ]
            current_year = self.periodo.ano

            total_events = q_entries.values("evento").distinct().count()
            q_plans = Plan.objects.filter(
                ano_calendario=self.periodo.ano, folha_tipo=self.tipo_folha
            )
            total_plans = q_plans.count()

            OverviewReport.objects.filter(payroll=self.pk).delete()
            FinancialReportPayroll.objects.filter(payroll=self.pk).delete()

            for obj in self.lancamentos.order_by("evento__numero").distinct(
                "evento__numero"
            ):
                ev = obj.evento
                character = 0
                q_ev = q_entries.filter(evento=ev.pk)
                # PENSIONISTAS

                if ev.carater in [4, 5, 6, 7, 8, 16, 17, 19, 20]:  # VERBAS DESCONTOS
                    character = 2
                elif ev.carater in [1, 2, 3, 9, 13, 15, 21]:  # VERBAS DE PROVENTOS
                    character = 1
                for year in years:
                    q_filter = Q(reference_year=year) | (
                        ~Q(reference_year=year) & Q(count_as_previous_exercise=False)
                    )
                    if year != current_year:
                        q_filter = Q(reference_year=year) & Q(
                            count_as_previous_exercise=True
                        )
                    q_pensioner = q_ev.filter(
                        Q(contracheque__pensioner__isnull=False) & q_filter
                    ).aggregate(
                        v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk")
                    )
                    if q_pensioner["c"]:
                        ev.overview_summary.create(
                            payroll=self,
                            type_of_employee=3,
                            type_of_entry=character,
                            value=q_pensioner["v"] or 0,
                            employer_contribution=q_pensioner["ec"] or 0,
                            quantity=q_pensioner["c"],
                            reference_year=year,
                        ),
                    # ATIVOS
                    q_active = q_ev.filter(
                        Q(contracheque__pensioner__isnull=True)
                        & Q(contracheque__servidor__ativo=True)
                        & q_filter
                    ).aggregate(
                        v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk")
                    )
                    if q_active["c"]:
                        ev.overview_summary.create(
                            payroll=self,
                            type_of_employee=1,
                            type_of_entry=character,
                            value=q_active["v"] or 0,
                            employer_contribution=q_active["ec"] or 0,
                            quantity=q_active["c"],
                            reference_year=year,
                        )
                    # INATIVOS
                    q_inactive = q_ev.filter(
                        Q(contracheque__pensioner__isnull=True)
                        & Q(contracheque__servidor__ativo=False)
                        & q_filter
                    ).aggregate(
                        v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk")
                    )
                    if q_inactive["c"]:
                        ev.overview_summary.create(
                            payroll=self,
                            type_of_employee=2,
                            type_of_entry=character,
                            value=q_inactive["v"] or 0,
                            employer_contribution=q_inactive["ec"] or 0,
                            quantity=q_inactive["c"],
                            reference_year=year,
                        )

            for plan in q_plans:
                q_entries_plan = q_entries.filter(
                    evento__genre_event__in=plan.genre_events.all()
                )
                for pc in plan.contas.filter():
                    q_pension_system = q_entries_plan.filter(
                        contracheque__servidor__regime_previdenciario=pc.regime_previdenciario
                    )
                    if q_pension_system.exists():
                        for year in years:
                            q_filter = Q(reference_year=year) | (
                                ~Q(reference_year=year)
                                & Q(count_as_previous_exercise=False)
                            )
                            if year != current_year:
                                q_filter = Q(reference_year=year) & Q(
                                    count_as_previous_exercise=True
                                )
                            q_values = q_pension_system.filter(q_filter).aggregate(
                                v=Sum("value"),
                                ec=Sum("employer_contribution"),
                                c=Count("pk"),
                            )

                            if plan.tipo != 3:  # LIQUIDO/CONSIGNAÇÃO
                                value = (
                                    -(q_values["v"] or 0)
                                    if plan.invert_negative or plan.tipo == 1
                                    else (q_values["v"] or 0)
                                )
                            else:  # PATRONAL
                                value = q_values["ec"] or 0
                            if q_values["c"]:
                                pc.financial_summary.create(
                                    payroll=self,
                                    value=value,
                                    quantity=q_values["c"],
                                    reference_year=year,
                                )

            if task:
                task.info(
                    f"Lançamentos da folha contabilizado com sucesso! Eventos({total_events}) Planos({total_plans})",
                    1,
                )

        else:
            if task:
                task.info(
                    "ERRO ao PROCESSAR FOLHA: %s se encontra processada/fechada e não pode ser processada!"
                    % self,
                    2,
                )

    def generate_report_contribution_cache(self, task=None):
        q_entries = self.lancamentos.exclude(
            contracheque__employee_pays_pension=2, contracheque__pensioner__isnull=True
        ).filter(servidor__social_securities__organ__cnpj="25091307000176")
        SocialSecurityContributionsReport.objects.filter(payroll=self.pk).delete()
        types_by_possession = [
            x[0]
            for x in self.paychecks.order_by("servidor__type_by_possession")
            .distinct("servidor__type_by_possession")
            .values_list("servidor__type_by_possession")
        ]
        mass_segregation_plans = [
            x[0] for x in Choice.get_choices_for("rh", "MASS_SEGREGATION_PLAN")
        ]
        regimes = [x[0] for x in Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO")]
        for plan in mass_segregation_plans:
            for regime in regimes:
                for type_by in types_by_possession:
                    query = q_entries.filter(
                        servidor__type_by_possession=type_by,
                        servidor__social_securities__start_validity__lte=self.periodo.end_date,
                        servidor__social_securities__regime=regime,
                        servidor__social_securities__mass_segregation_plan=plan,
                    ).distinct()
                    if query.exists():
                        employee_quantity = (
                            query.order_by("servidor__id")
                            .distinct("servidor__id")
                            .count()
                        )
                        dependents_quantity = (
                            query.filter(
                                Q(servidor__dependentes__dependencias__tipo=5)
                                & Q(
                                    servidor__dependentes__dependencias__data_inicio__lte=self.periodo.end_date
                                )
                                & Q(
                                    Q(
                                        servidor__dependentes__dependencias__data_fim__gte=self.periodo.start_date
                                    )
                                    | Q(
                                        servidor__dependentes__dependencias__data_fim=None
                                    )
                                )
                            )
                            .order_by("servidor__dependentes__id")
                            .distinct("servidor__dependentes__id")
                            .count()
                        )
                        total_remuneration = query.filter(
                            evento__genre_event__character__in=[1, 9]
                        ).aggregate(total_remuneration=Coalesce(Sum("value"), 0.00))
                        sums = query.filter(
                            evento__genre_event__character__in=[8, 17],
                        ).aggregate(
                            employee_base_calculation=Coalesce(Sum("valor_base"), 0.00),
                            employee_contribution=Coalesce(Sum("value"), 0.00),
                            employer_base_calculation=Coalesce(Sum("valor_base"), 0.00),
                            employer_contribution_sum=Coalesce(
                                Sum("employer_contribution"), 0.00
                            ),
                        )
                        SocialSecurityContributionsReport.objects.create(
                            payroll=self,
                            mass_segregation_plan=plan,
                            regime=regime,
                            type_by_possession=type_by,
                            employee_quantity=employee_quantity,
                            dependents_quantity=dependents_quantity,
                            remuneration_total=total_remuneration["total_remuneration"],
                            employee_base_calculation=sums["employee_base_calculation"],
                            employee_contribution=abs(sums["employee_contribution"]),
                            employer_base_calculation=sums["employer_base_calculation"],
                            employer_contribution=sums["employer_contribution_sum"],
                        )

    def proccess_payroll(self, simulate=True, task=None):
        new_task = not task
        if self.status in [1, 2]:
            # lock_file = Locker.create_lock('summarizing_payroll')

            task = NullTaskSession.start_execution() if not task else task
            task.info("PROCESSANDO folha de pagamento", 1)

            try:
                self.hit_payroll_with_sefip(simulate=simulate, task=task)
            except Exception as e:
                task.info(f"Erro ao tentar acertar patronal {e}")

            self.summarize(simulate, task=task)

            self.generate_report_contribution_cache()

            result = self.verify_totals_payroll(self.pk)

            if not result.get("SUCCESS", False):
                # print_message('>>> SUMMARING %s [\033[92mOK\033[0m]' % (payroll), same_line=True)
                task.info(
                    f"INCONSISTÊNCIA ao PROCESSAR FOLHA: totais com diferença!\n{result}",
                    2,
                )
            else:
                task.info(f"Totais processados com sucesso!\n{result}", 1)

        else:
            task.info(
                "ERRO ao PROCESSAR FOLHA: %s se encontra processada/fechada e não pode ser processada!"
                % self,
                2,
            )

        if new_task:
            task.finish_execution()

    def save(self, *args, **kargs):
        log.info(">>>>>>>>>>>>>>>>> SAVING FOLHA %s" % self)
        if self.complement is None:
            self.complement = 0
        if self.fechado is None:
            self.fechado = False
        if "status" in self.old_fields:
            st = self.status
            self.status = self.old_fields["status"]
            self.change_status(st, False)

        self.unicode_cache = "%s" % self
        # log.debug(('SAVING %s' % self.unicode_cache)

        super(Folha, self).save(*args, **kargs)

    @property
    def is_closed(self):
        return self.status == 3

    @property
    def is_processed(self):
        return self.status in [3, 4]

    def __str__(self):
        complement = "" if not self.complement else f" COMPL. {self.complement}"
        return f"{self.periodo} - {self.tipo_folha}{complement}"


class FolhaAuditoria(AuditTimestampModel):
    class Meta:
        ordering = ("-folha", "-created_at")

    folha = models.ForeignKey(Folha, related_name="changes", on_delete=models.CASCADE)
    resumo = models.CharField(max_length=250, verbose_name="Título")
    texto = models.TextField()
    conferido = models.BooleanField(default=False, verbose_name="Conferido")


class TransparencyChoice(Choice):
    # active1 = models.BooleanField(default=False, verbose_name='Ativo')
    group = models.PositiveSmallIntegerField(
        verbose_name="Grupos",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("gfp", "GROUP_TRANSPARENCY"),
    )


class GenreManager(models.Manager):
    def get_by_natural_key(self, number):
        return self.get(genre_number=number)


class GenreEvent(AuditTimestampModel):

    class Meta:
        ordering = ("genre_number",)

    objects = GenreManager()
    genre_number = models.CharField(max_length=3, unique=True, verbose_name="Número")
    type_event = models.CharField(max_length=1, choices=list(GFP_TIPO_EVENTO.items()))
    character = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "EVENT_CHARACTER"),
        verbose_name="Caráter",
        null=True,
        default=0,
    )
    title = models.CharField(max_length=50, unique=True, verbose_name="Título")
    config_transparency = models.PositiveIntegerField(
        choices=TransparencyChoice.get_choices_for("gfp", "CONFIG_TRANSPARENCY"),
        verbose_name="Portal Transparência",
        null=True,
        blank=True,
    )
    socialsecurity_config = models.ForeignKey(
        "rh.SocialSecurityConfig",
        related_name="genre_events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # consignee = models.ForeignKey(
    #     'rh.PessoaJuridica',
    #     related_name='genre_events',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True
    # )

    def __str__(self):
        return "%s - %s" % (self.genre_number, self.title)

    def save(self, *args, **kwargs):
        super(GenreEvent, self).save(*args, **kwargs)
        for ev in self.events.all():
            ev.save()

    def natural_key(self):
        return (self.genre_number,)

    @classmethod
    def manage_config_transparency(cls, pks, config_transparency):
        for pk in pks:
            inst = cls.objects.get(pk=int(pk))
            inst.config_transparency = config_transparency
            inst.save()


class SpecieManager(models.Manager):
    def get_by_natural_key(self, number):
        return self.get(specie_number=number)


class SpecieEvent(AuditTimestampModel):

    class Meta:
        ordering = ("specie_number",)

    objects = SpecieManager()
    specie_number = models.CharField(max_length=2, unique=True, verbose_name="Número")
    title = models.CharField(max_length=50, unique=True, verbose_name="Título")
    invert_type = models.BooleanField(verbose_name="Inverter Tipo", default=False)
    concatenate_name = models.BooleanField(
        verbose_name="Concatenar Nome?", default=True
    )

    def __str__(self):
        return "%s - %s" % (self.specie_number, self.title)

    def save(self, *args, **kwargs):
        super(SpecieEvent, self).save(*args, **kwargs)
        for ev in self.events.all():
            ev.save()

    def natural_key(self):
        return (self.specie_number,)


class NatureEventManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class NatureEvent(models.Model):

    class Meta:
        ordering = ("code",)

    objects = NatureEventManager()
    code = models.CharField(max_length=4, unique=True, verbose_name="Número")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )
    active = models.BooleanField(verbose_name="Ativo?", default=True)

    def __str__(self):
        return "%s - %s" % (self.code, self.title)

    def natural_key(self):
        return (self.code,)


class EventManager(models.Manager):
    # def get_queryset(self):
    #     return super(EventManager, self).get_queryset().exclude(genre_event=None)

    def get_by_natural_key(self, number):
        return self.get(numero=number)


class Evento(AuditTimestampModel):

    class Meta:
        ordering = ("numero", "titulo")
        unique_together = ("genre_event", "specie_event")

    objects = EventManager()
    order = models.PositiveIntegerField(
        verbose_name="Ordem", default=1, null=False, blank=True
    )
    numero = models.CharField(
        max_length=5, unique=True, verbose_name="Número", blank=True
    )
    genre_event = models.ForeignKey(
        GenreEvent,
        blank=True,
        null=True,
        verbose_name="Gênero do evento",
        related_name="events",
        on_delete=models.PROTECT,
    )
    specie_event = models.ForeignKey(
        SpecieEvent,
        blank=True,
        null=True,
        verbose_name="Espécie do evento",
        related_name="events",
        on_delete=models.PROTECT,
    )
    lancamento = models.CharField(
        max_length=1,
        choices=list(GFP_TIPO_LANCAMENTO.items()),
        verbose_name="Lançamento",
    )
    tipo = models.CharField(max_length=1, choices=list(GFP_TIPO_EVENTO.items()))
    tipo_calculo = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_CALC"),
        verbose_name="Tipo Cálculo",
    )
    carater = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "EVENT_CHARACTER"),
        verbose_name="Caráter",
        null=True,
        default=0,
    )
    nature_event = models.ForeignKey(
        ItemTable,
        verbose_name="Natureza (eSocial)",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    nature_of_event = models.ForeignKey(
        NatureEvent,
        verbose_name="Natureza (eSocial)",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    titulo = models.CharField(max_length=100, verbose_name="Título")
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Publicação",
        related_name="publicacao",
    )
    base_de_calculo = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "BASE_OF_CALC"),
        verbose_name="Base de cálculo",
        default=0,
    )
    previous_event = models.ForeignKey(
        "Evento",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Evento anterior",
        related_name="replacement_events",
    )
    description = models.CharField(
        max_length=400, verbose_name="Decrição", default="", blank=True
    )
    active = models.BooleanField(verbose_name="Ativo?", default=True)
    consignment_manager = models.BooleanField(
        verbose_name="Gerenciar Consig?", default=False
    )
    suspension_process = models.ManyToManyField(
        "rh.LegalProcess", verbose_name="Eventos", related_name="gfp_events"
    )
    evaluate_difference = models.BooleanField(
        verbose_name="Avaliar diferença?", default=False
    )
    separate_for_competencies = models.BooleanField(
        verbose_name="Separar por competências?", default=True
    )
    separate_for_info_event = models.BooleanField(
        verbose_name="Separar por info?", default=False
    )
    config_value = models.CharField(
        max_length=400, verbose_name="Cofiguração - valor", default="", blank=True
    )
    portal_classification = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "PORTAL_CLASS"),
        verbose_name="Classificação Portal",
        default=9999,
    )

    tags = models.ManyToManyField(
        Choice,
        help_text="Tags de Eventos",
        verbose_name="Tags",
        related_name="event_tags",
    )

    conta_contabil = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "CONTA_CONTABIL"),
        verbose_name="Conta Contábil",
        default=None,
        null=True,
    )

    # DEPRECATED
    consignatario = models.ForeignKey(
        "rh.PessoaJuridica",
        blank=True,
        null=True,
        related_name="eventos_consignacoes",
        on_delete=models.CASCADE,
    )
    aplica_consignado = models.BooleanField(verbose_name="Consignado", default=False)
    aplica_consignavel = models.BooleanField(verbose_name="Consignavel", default=False)
    config_transparencia = models.PositiveIntegerField(
        choices=Choice.get_choices_for("rh", "CONFIG_TRANSPARENCY"),
        verbose_name="Portal Transparência",
        null=True,
        blank=True,
    )
    aplic_classification = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "APLIC_CLASS"),
        verbose_name="Classificação Aplic",
        default=9999,
    )
    aplic_type = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "APLIC_TYPE"),
        verbose_name="Tipo Aplic",
        default=9999,
    )
    banco_consignacao = models.ForeignKey(
        "rh.Banco",
        related_name="banco_eventos_consignacoes",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    def natural_key(self):
        return (self.numero,)

    def get_configs(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        configs = self.configs.exclude(
            Q(start_validity__gt=end_date)
            | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
        ).order_by("start_validity")
        return configs

    @property
    def current_config(self):
        return self.get_configs().last()

    @property
    @deprecated
    def automatico(self):
        # log.debug(('>>>>>>>>>> %s' % self)
        return self.automated

    @property
    def automated(self):
        return self.automated_at()

    def automated_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.automated if config else False

    @property
    def calculo_invertido(self):
        return self.current_config.inverted_calculation if self.current_config else None

    @property
    @deprecated
    def calculo(self):
        return self.calculation

    @property
    def calculation(self):
        return self.calculation_at()

    def calculation_at(self, start_date=None):
        # log.debug('>>>>>>>>>> %s' % self)
        config = self.get_configs(start_date).first()
        return config.calculation if config else None

    @property
    @deprecated
    def quantidade_max(self):
        return self.max_quantity_at()

    @property
    def max_quantity(self):
        return self.max_quantity_at()

    def max_quantity_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.max_quantity if config else None

    @property
    @deprecated
    def quantidade(self):
        return self.quantity_at()

    @property
    def quantity(self):
        return self.quantity_at()

    def quantity_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.quantity if config else None

    @property
    @deprecated
    def porcentagem(self):
        return self.percentage_at()

    @property
    def percentage(self):
        return self.percentage_at()

    def percentage_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.percentage if config else None

    @property
    @deprecated
    def valor_base(self):
        return self.base_value_at()

    @property
    def base_value(self):
        return self.base_value_at()

    def base_value_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.base_value if config else None

    @property
    @deprecated
    def piso(self):
        return self.floor_at()

    @property
    def floor(self):
        return self.floor_at()

    def floor_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.floor if config else 0

    @property
    def relationships(self):
        return self.relationships_at()

    def relationships_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.relationships.all() if config else []

    @property
    @deprecated
    def teto(self):
        return self.ceiling_at()

    @property
    def ceiling(self):
        return self.ceiling_at()

    def ceiling_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.ceiling if config else 99999999

    def focuses_on_at(self, start_date=None):
        config = self.get_configs(start_date).first()
        return config.focuses_on.all() if config else []

    def get_class_calculo(self):
        if self.automated and self.calculation:
            return self.calculation.cls
        else:
            return None

    def get_event_type(self, genre, specie):
        if specie.invert_type is True:
            if genre.type_event == "P":
                return "D"
            else:
                return "P"
        else:
            return genre.type_event

    def get_event_name(self, genre, specie):
        if specie.concatenate_name is not True:
            return genre.title
        else:
            return "%s - %s" % (genre.title, specie.title)

    def base_event(self):
        if self.genre_event:
            rs = Evento.objects.filter(
                genre_event__genre_number=self.genre_event.genre_number,
                specie_event__specie_number="00",
            )
            if rs:
                return rs.first()
        return self

    def validar_consignacao(self):
        """
        Método responsável por validar comportamento das verbas de consignação.
        Se a verba for de caráter de consignação deve ser obrigatório o preenchimento do campo
        banco consignação.

        Caráter CONSIGNAÇÃO é o ID 7 do model Choice, para a constante EVENT_CHARACTER.
        """

        if self.carater == 7 and self.banco_consignacao is None:
            raise Exception(
                "Para as verbas de caráter Consignação é obrigatório a escolha do Banco Consignação."
            )

    def save(self, *args, **kargs):
        # if self.aplica_consignado is True and self.aplica_consignado == self.aplica_consignavel:
        #     raise Exception("Não é possivel inserir um evento ao mesmo tempo CONSIGNADO e CONSIGNAVEL.")
        # elif self.aplica_consignado and self.tipo == 'P':
        #     raise Exception("Um evento positivo não pode ser somando a CONSIGNADO.")

        # if not self.quantidade_max:
        #     self.quantidade_max = '0.0'

        # self.validar_consignacao()

        if self.genre_event and self.specie_event:
            self.numero = "%s%s" % (
                self.genre_event.genre_number,
                self.specie_event.specie_number,
            )
            self.titulo = self.get_event_name(self.genre_event, self.specie_event)
            self.carater = self.genre_event.character
            if not self.tipo:
                self.tipo = self.get_event_type(self.genre_event, self.specie_event)

        super(Evento, self).save(*args, **kargs)

        if not self.configs.exists():
            self.configs.create(start_validity=self.created_at)

    def __str__(self):

        return "{0}: {1}".format(self.numero, self.titulo)


class ConfigEventQuerySet(models.QuerySet):
    def current_in(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        return self.exclude(
            Q(start_validity__gt=end_date)
            | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
        ).order_by("start_validity")

    def validity_in(self, start_date, end_date=None):
        query = self.exclude(
            Q(end_validity__isnull=False) & Q(end_validity__lt=start_date)
        )
        if end_date:
            query = query.exclude(start_validity__gt=end_date)

        return query


class ConfigEventManager(models.Manager):
    def get_by_natural_key(self, event, start_validity):
        return self.get(event=event, start_validity=start_validity)

    def get_queryset(self):
        return ConfigEventQuerySet(self.model, using=self._db)  # Important!

    def current_in(self, start_date=None, end_date=None):
        return self.get_queryset().current_in(start_date, end_date)

    def validity_in(self, start_date, end_date=None):
        return self.get_queryset().validity_in(start_date, end_date)


class ConfigEvent(AuditTimestampModel):
    event = models.ForeignKey(
        "Evento",
        verbose_name="Evento",
        related_name="configs",
        on_delete=models.CASCADE,
    )
    max_quantity = models.DecimalField(
        verbose_name="Quantidade máxima", max_digits=10, decimal_places=6, default=0
    )
    quantity = models.DecimalField(
        verbose_name="Quantidade",
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    percentage = models.DecimalField(
        verbose_name="Porcentagem",
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    base_value = models.DecimalField(
        verbose_name="Valor base",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    floor = models.DecimalField(
        verbose_name="Teto", max_digits=10, decimal_places=2, null=True, blank=True
    )
    ceiling = models.DecimalField(
        verbose_name="Piso", max_digits=10, decimal_places=2, null=True, blank=True
    )
    automated = models.BooleanField(verbose_name="Automático", default=False)
    inverted_calculation = models.BooleanField(
        verbose_name="Cálculo invertido", default=False
    )
    calculation = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Cálculo",
        related_name="config_events",
        on_delete=models.PROTECT,
    )
    focuses_on = models.ManyToManyField(
        "Evento", verbose_name="Incide sobre", related_name="aplica_em"
    )
    relationships = models.ManyToManyField(
        "Evento", verbose_name="Relacionamentos", related_name="relations"
    )
    relationships_help = models.CharField(max_length=400, null=True, blank=True)

    # has_incidence_irrf = models.BooleanField(verbose_name='Incidência no IRRF?', default=False)
    # has_incidence_prev = models.BooleanField(verbose_name='Incidência na Prev?', default=False)
    # has_incidence_sind = models.BooleanField(verbose_name='Incidência na Sind?', default=False)
    # has_incidence_fgts = models.BooleanField(verbose_name='Incidência no FGTS?', default=False)
    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    nature_event = models.ForeignKey(
        ItemTable,
        verbose_name="Natureza (eSocial)",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    manual_incidence_esocial = models.BooleanField(
        verbose_name="Incidência eSocial manual?", default=False
    )
    esocial_cp = models.ForeignKey(
        ItemTable,
        verbose_name="Incidência CP",
        blank=True,
        null=True,
        related_name="configevent_cp",
        on_delete=models.SET_NULL,
    )
    esocial_irrf = models.ForeignKey(
        ItemTable,
        verbose_name="Incidência IRRF",
        blank=True,
        null=True,
        related_name="configevent_irrf",
        on_delete=models.SET_NULL,
    )
    esocial_cprp = models.ForeignKey(
        ItemTable,
        verbose_name="Incidência CPRP",
        blank=True,
        null=True,
        related_name="configevent_cprp",
        on_delete=models.SET_NULL,
    )
    descricao = models.TextField(
        verbose_name="Descrição das regras", blank=True, null=True
    )

    objects = ConfigEventManager()

    def natural_key(self):
        return (self.event, self.start_validity)

    def __str__(self):
        return "%s - %s: %s" % (
            self.start_validity.strftime("%d/%m/%Y"),
            self.end_validity.strftime("%d/%m/%Y") if self.end_validity else "---",
            self.event,
        )

    @property
    def next(self):
        return (
            self.event.configs.exclude(pk=self.pk)
            .filter(start_validity__gt=self.start_validity)
            .order_by("start_validity")
            .first()
        )

    @property
    def previous(self):
        return (
            self.event.configs.exclude(pk=self.pk)
            .filter(start_validity__lt=self.start_validity)
            .order_by("start_validity")
            .last()
        )

    def set_esocial_cp(self):
        base_event = self.event.base_event()
        from_to_character = {}
        focuses_on_monthly_cp = base_event.aplica_em.filter(
            event__carater__in=(
                8,  # previdenciario
                17,  # previdenciario 13
                # 18,  # previdenciario Férias
                19,  # previdenciario RRA
            ),
            event__tags__label="rgps",
        ).validity_in(start_date=self.start_validity, end_date=self.end_validity)

        if focuses_on_monthly_cp:
            from_to_character = {
                # Base de cálculo das contribuições sociais - Salário de contribuição:
                1: "11",  # Mensal;
                9: "12",  # 13o Salário;
                # FIXME: 13, 14, 15, 16, ANALISAR OPÇÕES PARA DESCOBRIR O SIGNIFICADO
            }
        elif base_event.tags.filter(label="rgps"):
            from_to_character = {
                # Contribuição descontada do Segurado sobre salário de contribuição:
                8: "31" if self.event.tipo == "D" else "00",  # Mensal;
                17: "32" if self.event.tipo == "D" else "00",  # 13o Salário;
                # # Outros
                # 11: '51',  # 51 - Salário-família;
            }

        cod_inc_cp = from_to_character.get(base_event.carater, "00")

        carater = base_event.carater

        if (
            cod_inc_cp == "00"
            and carater == 3
            and base_event.tags.filter(label="salariofamilia").exists()
        ):
            cod_inc_cp = "51"
        elif (
            cod_inc_cp == "11"
            and carater == 1
            and base_event.tags.filter(label="salariomaternidade").exists()
        ):
            cod_inc_cp = "21"
        elif (
            cod_inc_cp == "12"
            and carater == 9
            and base_event.tags.filter(label="salariomaternidade13").exists()
        ):
            cod_inc_cp = "22"

        self.esocial_cp = ItemTable.objects.by_code_table(cod_inc_cp, "98")

    def set_esocial_irrf(self):
        focuses_on_monthly = self.event.aplica_em.filter(
            event__carater__in=(
                4,  # IMPORTO MENSAL
                16,  # IMPOSTO RRA
                20,  # IMPOSTO 13
            )
        ).validity_in(start_date=self.start_validity, end_date=self.end_validity)

        has_inc = focuses_on_monthly.exists()

        if has_inc:
            from_to_character = {
                # Código de incidência tributária da rubrica para o IRRF:
                # Rendimentos tributáveis - base de cálculo do IRRF:
                1: 11,  # Remuneração mensal;
                21: 11,  # Remuneração mensal;
                9: 12,  # 13o Salário;
                13: 13,  # Férias;
                15: 11,  # Rendimentos Recebidos Acumuladamente - RRA;
                # Deduções da base de cálculo do IRRF:
                8: (
                    41 if self.event.tipo == "D" else 9
                ),  # 41 - Previdência Social Oficial - PSO - Remuner. mensal;
                17: 42 if self.event.tipo == "D" else 9,  # 42 - PSO - 13° salário;
                19: 41 if self.event.tipo == "D" else 9,  # 44 - PSO - RRA;
                5: 51,  # 51 - Pensão Alimentícia - Remuneração mensal;
                # FIXME: (43 - PSO - Férias) NÃO EXISTE NO ATHENAS, CASO SEJA EXIGIDO PELO ESOCIAL, DEVERÁ SER IMPLEMENTADO
                # FIXME: (52 - PENSÃO SOBRE - 13) NÃO EXISTE NO ATHENAS, CASO SEJA EXIGIDO PELO ESOCIAL, DEVERÁ SER IMPLEMENTADO
                # FIXME: (53 - PENSÃO SOBRE - Férias) NÃO EXISTE NO ATHENAS, CASO SEJA EXIGIDO PELO ESOCIAL, DEVERÁ SER IMPLEMENTADO
                # FIXME: (67 - PLANO PRIVADO COLETIVO DE ASSISTÊNCIA À SAÚDE) NÃO EXISTE NO ATHENAS, CASO SEJA EXIGIDO PELO ESOCIAL,
            }
        else:
            from_to_character = {
                # Rendimento não tributável ou isento do IRRF:
                # Outras Isenções
                0: 9,
                1: 9,  # FIXME: OPÇÃO DEFAULT QUANDO NÃO POSSUIR INCIDÊNCIA E FOR REMUNERATÓRIA - GERAL, AVALIAR PARA COLOCAR VALOR CORRETO
                5: 9,  # FIXME: OPÇÃO DEFAULT QUANDO NÃO POSSUIR INCIDÊNCIA E FOR REMUNERATÓRIA - GERAL, AVALIAR PARA COLOCAR VALOR CORRETO
                9: 9,  # FIXME: OPÇÃO DEFAULT QUANDO NÃO POSSUIR INCIDÊNCIA E FOR REMUNERATÓRIA - GERAL, AVALIAR PARA COLOCAR VALOR CORRETO
                2: 79,  # 79	Outras isenções (o nome da rubrica deve ser claro para identificação da natureza dos valores)	01/10/2015	-
                3: 79,  # 79	Outras isenções (o nome da rubrica deve ser claro para identificação da natureza dos valores)	01/10/2015	-
                6: 9,  # Verba transitada pela folha de pagamento de natureza diversa de rendimento ou retenção/isenção/dedução de IR (exemplo: desconto de convênio farmácia, desconto de consignações, etc.)
                7: 9,  # Verba transitada pela folha de pagamento de natureza diversa de rendimento ou retenção/isenção/dedução de IR (exemplo: desconto de convênio farmácia, desconto de consignações, etc.)
                # 2 poderá mudar 72 caso a tag seja diarias # 72	Diárias	01/10/2015	-
                # 2 poderá mudar 73 caso a tag seja ajudadecusto # 73	Ajuda de custo	01/10/2015	-
                # 2 poderá mudar 74 caso a tag seja indenizacaoerescisao # 74	Indenização e rescisão de contrato,
                #   inclusive a título de PDV e acidentes de trabalho	01/10/2015	-
                # 2 poderá mudar 75 caso a tag seja abonopecuniario # 75	Abono pecuniário	01/10/2015	-
                # 2 poderá mudar 700 caso a tag seja auxiliomoradia # 700	Auxílio moradia	01/10/2015	-
                # FIXME: ANALISAR AS OPÇÕES ABAIXO
                22: 70,  # Parcela isenta 65 anos - Remuneração mensal	01/10/2015	-
                # 71	Parcela isenta 65 anos - 13º salário	01/10/2015	-
                23: 76,  # Rendimento de beneficiário com moléstia grave ou acidente em serviço - Remuneração mensal	01/10/2015	-
                # 77	Rendimento de beneficiário com moléstia grave ou acidente em serviço - 13º salário	01/10/2015	-
                # Retenções do IRRF efetuadas sobre:
                4: (
                    31 if self.event.tipo == "D" else 9
                ),  # Retenções do IRRF sobre Remuneração mensal
                20: 32 if self.event.tipo == "D" else 9,  # Retenções do IRRF sobre 13º
                16: 31 if self.event.tipo == "D" else 9,  # Retenções do IRRF sobre RRA
                # FIXME: RETENÇÃO SOBRE FÉRIAS (33) NÃO EXISTE NO ATHENAS, CASO SEJA EXIGIDO PELO ESOCIAL, DEVERÁ SER IMPLEMENTADO
            }

        value = from_to_character.get(self.event.carater, None)

        if value == 79 and self.event.tags.filter(label="diarias").exists():
            value = 72
        elif value == 79 and self.event.tags.filter(label="ajudadecusto").exists():
            value = 73
        elif (
            value == 79
            and self.event.tags.filter(label="indenizacaoerescisao").exists()
        ):
            value = 74
        elif value == 79 and self.event.tags.filter(label="abonopecuniario").exists():
            value = 75
        elif value == 51 and self.event.tags.filter(label="decimoterceiro").exists():
            value = 52

        self.esocial_irrf = None
        if value:
            self.esocial_irrf = ItemTable.objects.validity_in(
                self.start_validity, self.end_validity
            ).by_code_table(str(value), "21")

    def set_esocial_cprp(self):
        base_event = self.event.base_event()

        focuses_on_monthly_cp = base_event.aplica_em.filter(
            event__carater__in=(
                8,  # previdenciario
                17,  # previdenciario 13
                # 18,  # previdenciario Férias
                19,  # previdenciario RRA
            ),
            event__tags__label="rpps",
        ).validity_in(start_date=self.start_validity, end_date=self.end_validity)
        from_to_character = {}
        if focuses_on_monthly_cp:
            from_to_character = {
                1: "11",  # Mensal;
                9: "12",  # 13o Salário;
            }
        elif base_event.tags.filter(label="rpps"):
            from_to_character = {
                # Contribuição descontada do Segurado sobre salário de contribuição:
                8: "31" if self.event.tipo == "D" else "00",  # Mensal;
                17: "32" if self.event.tipo == "D" else "00",  # 13o Salário;
                # # Outros
                # 11: '51',  # 51 - Salário-família;
            }

        value = from_to_character.get(base_event.carater, "00")
        self.esocial_cprp = ItemTable.objects.by_code_table(value, "96")

    def save(self, *args, **kwargs):
        if not self.manual_incidence_esocial:
            self.set_esocial_cp()
            self.set_esocial_irrf()
            self.set_esocial_cprp()

        if self.previous and self.previous.end_validity is None:
            p = self.previous
            p.end_validity = self.start_validity - relativedelta(days=1)
            p.save()
        if self.next and (
            self.end_validity is None or self.end_validity >= self.next.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo! (%s)"
                % (self.next, self.event.numero)
            )
        if self.previous and (
            self.previous.end_validity is None
            or self.previous.end_validity >= self.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo(%s)"
                % (self.previous, self.event.numero)
            )
        # log.debug(('SAVING %s' % self)

        super(ConfigEvent, self).save(*args, **kwargs)


class GroupEvents(TransparencyChoice):
    events = models.ManyToManyField(Evento, related_name="+", verbose_name="Eventos")
    genre_events = models.ManyToManyField(
        GenreEvent, related_name="+", verbose_name="Gêneros"
    )
    type_event = models.CharField(
        max_length=1, null=True, blank=True, choices=(("D", "DÉBITO"), ("C", "CRÉDITO"))
    )


class DifferencesEntryManager(models.Manager):

    def get_queryset(self):
        return (
            super(DifferencesEntryManager, self)
            .get_queryset()
            .filter(
                ~Q(value=F("correct_value") - F("diff_value_provisioned"))
                | ~Q(
                    employer_contribution=F("correct_employer_contribution")
                    - F("diff_employer_contribution_provisioned")
                )
            )
            .filter(evento__evaluate_difference=True)
        )


class EntryQueryset(models.QuerySet):
    pass


class FolhaEvento(AuditTimestampModel):

    class Meta:
        unique_together = (
            "contracheque",
            "evento",
            "info",
            "servidor",
            "reference_year",
            "reference_month",
            "cid",
        )
        permissions = (
            (
                "can_validate_event_payroll",
                "Validar eventos pendentes na folha de pagamento",
            ),
            (
                "can_validate_event_internal_control",
                "Validar eventos pendentes no controle interno",
            ),
        )
        ordering = [
            "contracheque__folha",
            "contracheque__servidor",
            "evento__numero",
            "reference_year",
            "reference_month",
            "info",
        ]

    AUDITABLE = {
        "fields": [
            "qnt",
            "qnt_max",
            "parcela",
            "prazo",
            "valor",
            "valor_base",
            "patronal",
            "info",
            "base_previdencia",
            "correct_valor",
            "automated",
            "insertion_type",
            "correct_patronal",
            "correct_base_previdencia",
            "diff_valor_aprovisionado",
            "diff_patronal_aprovisionado",
            "value",
            "calculation",
            "correct_value",
            "diff_value_provisioned",
            "employer_contribution",
            "correct_employer_contribution",
            "diff_employer_contribution_provisioned",
            "json_calc_vars",
            "_json_calc_vars",
            "reference_month",
            "reference_year",
            "correct_pct",
            "correct_qnt",
            "correct_base_value",
            "count_as_previous_exercise",
        ],
    }

    # MAKE_PENDENCE = ['qnt', 'pct', 'valor', 'valor_base', 'patronal']
    MAKE_PENDENCE = ["valor", "patronal", "info"]

    sum_correct_valor = 0
    event_description = ""

    objects = EntryQueryset.as_manager()
    with_differences = DifferencesEntryManager()

    contracheque = models.ForeignKey(
        "ContraCheque",
        related_name="lancamentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    servidor = models.ForeignKey(
        Servidor, related_name="entries", blank=True, on_delete=models.PROTECT
    )
    folha = models.ForeignKey(
        Folha, related_name="lancamentos", blank=True, on_delete=models.PROTECT
    )
    evento = models.ForeignKey(
        Evento, related_name="lancamentos", blank=True, on_delete=models.PROTECT
    )
    lancamento = models.CharField(
        max_length=1, choices=list(GFP_TIPO_LANCAMENTO.items()), blank=True
    )
    qnt = models.DecimalField(max_digits=10, decimal_places=6, blank=True, default=0)
    qnt_max = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    parcela = models.PositiveIntegerField(blank=True, default=0)
    installments_paid = models.PositiveSmallIntegerField(blank=True, default=1)
    prazo = models.PositiveIntegerField(blank=True, default=0)
    pct = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    valor = models.DecimalField(max_digits=16, decimal_places=2, blank=True, default=0)
    correct_valor = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    diff_valor_aprovisionado = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    valor_base = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    patronal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    correct_patronal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    diff_patronal_aprovisionado = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    info = models.CharField(max_length=150, default="", null=True, blank=True)
    base_previdencia = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, blank=True
    )
    correct_base_previdencia = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, blank=True
    )
    dt_criado = models.DateTimeField(auto_now_add=True)
    dt_confirma_folha = models.DateTimeField(blank=True, null=True)
    dt_confirma_controle = models.DateTimeField(blank=True, null=True)
    confirma_folha = models.ForeignKey(
        User,
        related_name="confirma_folha_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    confirma_controle = models.ForeignKey(
        User,
        related_name="confirma_controle_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    copia_de = models.ForeignKey(
        "gfp.FolhaEvento",
        on_delete=models.SET_NULL,
        related_name="origem_para",
        null=True,
        blank=True,
    )

    # Estes campos irão substituir os atuais "valor" e "patronal". Poder ser positivos ou negativos
    value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, default=0)
    employer_contribution = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    # -----------------------------------------------------
    rra_employee = models.ForeignKey(
        "RRAEmployee",
        related_name="entries",
        null=True,
        blank=True,
        verbose_name="RRA Servidor",
        on_delete=models.PROTECT,
    )
    correct_value = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    correct_employer_contribution = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    correct_contribution_base = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    correct_qnt = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, default=0
    )
    correct_qnt_max = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, default=0
    )
    correct_pct = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, null=True
    )
    correct_base_value = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    # normal_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, default=0)
    # correct_normal_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, default=0)
    diff_value_provisioned = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )
    diff_employer_contribution_provisioned = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )
    reason_difference = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Motivo",
        choices=Choice.get_choices_for("gfp", "DIFFERENCE_TYPE"),
    )
    paycheck_difference = models.ForeignKey(
        "PaycheckDifference",
        null=True,
        related_name="entries_payment",
        on_delete=models.CASCADE,
    )
    reference_year = models.PositiveSmallIntegerField(
        verbose_name="Ano Referência", blank=True, null=True
    )
    reference_month = models.PositiveSmallIntegerField(
        verbose_name="Mês Referência", blank=True, null=True
    )
    status = models.CharField(
        max_length=2,
        choices=list(GFP_STATUS_FOLHAEVENTO.items()),
        default="CT",
        db_index=True,
        blank=True,
    )
    json_calc_vars = models.CharField(max_length=256, default="{}")
    automated = models.BooleanField(verbose_name="Automatizado?", default=False)
    insertion_type = models.PositiveSmallIntegerField(
        verbose_name="Tipo de Inserção",
        choices=Choice.get_choices_for("gfp", "ENTRY_INSERTION_TYPE"),
        default=3,
    )
    entry_pension = models.ForeignKey(
        "gfp.FolhaEvento",
        on_delete=models.CASCADE,
        related_name="entries_pay_pension",
        null=True,
        blank=True,
    )
    calculation = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Cálculo",
        related_name="entries",
        on_delete=models.SET_NULL,
    )
    cid = models.IntegerField(default=0)
    count_as_previous_exercise = models.BooleanField(
        verbose_name="Exercício anterior?", default=False, blank=True
    )
    event_esocial = models.PositiveIntegerField(blank=True, null=True)

    class ZeroValueOrNegativeValue(Exception):
        def __init__(self, evento, value):
            Exception.__init__(
                self,
                "O evento %s não será salvo pois seu valor foi igual a %s!"
                % (evento, value),
            )

    class RRAEmployeeDifferentEmployee(Exception):
        def __init__(self, servidor):
            Exception.__init__(
                self,
                "O lançamento %s não será salvo pois o RRA definido não está atribuído ao servidor %s!"
                % (self, servidor),
            )

    class AccountingNotAllowed(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "O lançamento possui referência igual ao período e por isso não deve ser contabilizado em exercício anterior!",
            )

    def __str__(self):
        return "%s%s" % (
            self.evento,
            (": %s" % self.info) if self.info else "",
        )  # (' : %s%s' % (self.info, (cid)) if self.info else cid))

    @property
    def vars(self):
        if not hasattr(self, "_json_calc_vars"):
            self._json_calc_vars = json.decode(self.json_calc_vars)
        return self._json_calc_vars

    @vars.setter
    def vars(self, value):
        if value != self.vars:
            self._json_calc_vars = value
            self.json_calc_vars = json.encode(value)
            # self.save()

    @property
    def get_cid_oids(self):
        if len(self.oIds) == 1 and self.oIds[0] == "":
            return [self.cid]
        return self.oIds

    @property
    def oIds(self):
        return self.vars.get("oIds", [])

    @oIds.setter
    def oIds(self, value):
        if value != self.vars.get("oIds", []):
            self.vars.update({"oIds": value})
            self.json_calc_vars = json.encode(self.vars)

    @property
    def auto_calc_difference(self):
        return (
            self.automated and self.paycheck_difference and self.calculation and True
        ) or False

    @property
    def classcode(self):
        calc = None
        current_config = self.evento.get_configs(
            self.folha.periodo.range.first, self.folha.periodo.range.last
        ).last()
        if self.automated:
            calc = current_config.calculation if current_config else self.calculation
            if self.paycheck_difference:
                calc = ClassCode.objects.get(slug="mpto-gfp-difference")
            # elif self.contracheque.folha.is_processed:
            #     calc = self.calculation or current_config.calculation
        # log.debug('CLASSCODE FOR %s: %s' % (self.evento.numero, calc))
        return calc

    def instance_calc(self, exclude_events=[], only_events=[], **kwargs):

        dr = NewDateRange.from_month(self.reference_year, min(self.reference_month, 12))
        config = (
            self.evento.configs.current_in(dr.first, dr.last)
            .filter(automated=True, calculation__isnull=False)
            .first()
        )
        if not config and not self.paycheck_difference:
            return None

        qtd = kwargs.get("qnt", self.correct_qnt)
        params = {
            "pct": self.correct_pct,
            "qnt": qtd,
            "info": self.info,
            "patronal": self.correct_patronal,
            "valor_base": self.correct_base_value,
            "parcela": self.parcela,
        }

        calc = self.classcode.cls(
            self.servidor,
            self.folha,
            self.evento,
            entry=self,
            params=params,
            pensioner=self.contracheque.pensioner,
            exclude_events=list(exclude_events),
            only_events=list(only_events),
            **kwargs,
        )
        return calc

    def _set_has_base(self):
        try:
            contracheque_old = self.contracheque.folha.folha_anterior.paychecks.get(
                servidor=self.contracheque.servidor,
                pensioner=self.contracheque.pensioner,
                benefit_number=self.contracheque.benefit_number,
            )
            folha_evento_old = contracheque_old.lancamentos.get(
                evento=self.evento, info=self.info
            )
        except (
            FolhaEvento.DoesNotExist,
            ContraCheque.DoesNotExist,
            Folha.DoesNotExist,
            AttributeError,
        ):
            pass
        except (
            FolhaEvento.MultipleObjectsReturned,
            ContraCheque.MultipleObjectsReturned,
        ) as e:
            # log.debug(('%s:%s' % (self.contracheque, self.contracheque.pensioner))
            log.exception(e)
        except Exception as e:
            log.exception(e)
        else:
            self.copia_de = folha_evento_old
            # log.info('SETTING copy_from of %s to %s' % (self, self.copia_de))

    def _igual_copia_de(self):
        diffs = []
        if not self.copia_de:
            return False

        diffs = self._differences(self.copia_de, only=self.MAKE_PENDENCE)

        return not (diffs and True or False)

    def confirma(self, tipo, responsavel):
        # log.debug(('call confirma')
        if tipo == "CI":
            self._controle_interno_flag = True
            if not self.confirma_controle:
                self._confirm_dep_control()
        else:
            self._controle_interno_flag = False
            if not self.confirma_folha:
                self._confirm_dep_payroll()

    @property
    def is_confirmed_dep_control(self):
        return (self.dt_confirma_controle and self.confirma_controle and True) or False

    @property
    def is_confirmed_dep_payroll(self):
        return (self.dt_confirma_folha and self.confirma_folha and True) or False

    def _confirm_dep_control(self):
        sponsor = get_current_user()
        if not sponsor.has_perm("gfp.can_validate_event_internal_control"):
            return False

        if not self.is_confirmed_dep_control:
            self.dt_confirma_controle = datetime.now()
            self.confirma_controle = sponsor
            self.save()

            for fev in self.origem_para.filter(confirma_controle=None):
                fev._igual_copia_de() and fev._confirm_dep_control()

    def _confirm_dep_payroll(self):
        sponsor = get_current_user()
        if not sponsor.has_perm("gfp.can_validate_event_payroll"):
            return False

        if not self.is_confirmed_dep_payroll:
            self.dt_confirma_folha = datetime.now()
            self.confirma_folha = sponsor
            self.save()

            for fev in self.origem_para.filter(confirma_folha=None):
                fev._igual_copia_de() and fev._confirm_dep_payroll()

    @property
    def pendente(self):
        pendencias = []
        if not self.confirma_folha:
            pendencias.append("FP")
        if not self.confirma_controle:
            pendencias.append("CI")
        # log.debug('PENDENTE: (%s) %s' % (self, pendencias))
        return pendencias

    @property
    def has_pendencies(self):
        if not self.pk:
            return True
        # keys = set(['qnt', 'prazo', 'valor', 'valor_base', 'patronal', 'info'])
        keys = set(self.MAKE_PENDENCE)
        # log.debug('HAS_PENDENCIES: %s: %s: %s' % (keys, self.old_fields.keys(), keys & set(self.old_fields.keys())))
        return keys & set(self.old_fields.keys()) and True or False

    @property
    def has_visual_changes(self):
        diffs = set(self.diff.keys()).intersection(
            set(
                [
                    "valor",
                    "correct_valor",
                    "patronal",
                    "correct_patronal",
                    "info",
                ]
            )
        )
        return (diffs and True) or False

    @property
    def has_differences(self):
        # log.debug(
        #   '%s - %s >> VALOR: %s DVP: %s CV: %s PAT: %s DECP: %s CEC: %s' % (
        #       self, self.pk, self.valor,
        #       self.diff_valor_aprovisionado,
        #       self.correct_valor,
        #       self.patronal,
        #       self.diff_patronal_aprovisionado,
        #       self.correct_patronal))
        return round(
            float(self.value) + float(self.diff_value_provisioned), 2
        ) != round(float(self.correct_value), 2) or round(
            float(self.employer_contribution)
            + float(self.diff_employer_contribution_provisioned),
            2,
        ) != round(
            float(self.correct_employer_contribution), 2
        )

    @property
    def differences(self):
        if self.has_differences:
            return {
                "valor": round(
                    float(self.correct_value)
                    - float(self.value)
                    - float(self.diff_value_provisioned),
                    2,
                ),
                "patronal": round(
                    float(self.correct_employer_contribution)
                    - float(self.employer_contribution)
                    - float(self.diff_employer_contribution_provisioned),
                    2,
                ),
            }
        else:
            return {}

    @property
    def prazo_desc(self):
        return "" if not self.prazo else "%d/%s" % (self.parcela, self.prazo)

    @property
    def entries_conference_previous(self):
        event_payroll_previous = self.conference_event_payroll_previous.filter(
            event_payroll_previous__isnull=False
        ).first()
        return event_payroll_previous

    @property
    def entries_conference_current(self):
        event_payroll_current = self.conference_event_payroll_current.filter(
            event_payroll_current__isnull=False
        ).first()
        return event_payroll_current

    def confirm_if_equals(self):
        """ """
        # log.debug('EGUALS: %s - %s' % (self._igual_copia_de(), self))
        if self._igual_copia_de():
            self.dt_confirma_folha = self.copia_de.dt_confirma_folha
            self.confirma_folha = self.copia_de.confirma_folha
            self.confirma_controle = self.copia_de.confirma_controle
            self.dt_confirma_controle = self.copia_de.dt_confirma_controle

    def set_pendente(self, folha=True, controle_interno=True):
        if folha:
            self.dt_confirma_folha = None
            self.confirma_folha = None
        if controle_interno:
            self.dt_confirma_controle = None
            self.confirma_controle = None
        # self.save()

    def update_provisions(self):
        res = self.difference_items.aggregate(
            value=Sum("value"), employer_contribution=Sum("employer_contribution")
        )
        value = res.get("value") or 0
        self.diff_valor_aprovisionado = -value if self.evento.tipo == "D" else value
        self.diff_patronal_aprovisionado = res.get("employer_contribution") or 0
        if self.changed:
            # log.debug('UPDATE PROVISIONS: %s [%s:%s] %s' % (
            #       self, self.diff_valor_aprovisionado, self.diff_patronal_aprovisionado, self.old_fields))
            self.save()

    def delete(self, *args, **kargs):
        # log.info('DELETING ST: %s FE: %s' % (self.status, self))

        # TODO: Avaliar se necessita proibir a deleção em outros estados
        if self.folha.is_processed and self.status == "CT":
            raise Folha.ClosedFolha()

        recalculate = kargs.pop("recalculate", True)
        super(FolhaEvento, self).delete(*args, **kargs)

        # Deixando o contracheque em estado de ALTERADO = True
        # Para alterar para ALTERADO = False deve-se executar o método consolidar de contracheque
        paycheck = self.contracheque
        if self.status in ("CT", "CE"):
            paycheck.set_changes(ContraCheque.EVENTS)
        if self.evento.margins_base.filter(
            type_of_payroll=self.folha.tipo_folha, active=True
        ) or self.evento.margins_consigneds.filter(
            type_of_payroll=self.folha.tipo_folha, active=True
        ):
            paycheck.set_changes(ContraCheque.MARGINS)

        if self.paycheck_difference:
            pd = self.paycheck_difference
            pd.save()

        if recalculate:
            paycheck.recalculate()

    def change_status(self, new_status):
        if self.contracheque.folha.is_processed:
            raise Folha.ClosedFolha()
        if self.status != new_status:
            # TODO fazer via workflow
            self.status = new_status
            self.save()

    def save(self, *args, **kargs):
        pendencies = self.has_pendencies

        if self.rra_employee and self.rra_employee.employee != self.servidor:
            raise self.RRAEmployeeDifferentEmployee(self.servidor)

        if self.contracheque:  # and not (self.folha or self.servidor):
            self.folha_id = self.contracheque.folha_id
            self.servidor = self.contracheque.servidor

        if not self.lancamento:
            self.lancamento = self.evento.lancamento
        if self.lancamento in ["T", "U"]:
            self.prazo = 1 if not self.prazo else self.prazo
            self.parcela = 1 if not self.parcela and self.prazo > 0 else self.parcela

        if not (self.reference_year and self.reference_month):
            self.reference_year = self.contracheque.folha.periodo.ano
            self.reference_month = self.contracheque.folha.periodo.mes
        if self.reference_year == self.contracheque.folha.periodo.ano:
            self.count_as_previous_exercise = False

        if self.contracheque.folha.is_processed:
            if not self.pk:
                if self.status in ("CT", "CE"):
                    self.status = "NC"
                self.dt_confirma_folha = self.dt_confirma_controle = datetime.now()
                self.confirma_folha = self.confirma_controle = get_current_user()

            if self.status in ("CT", "CE"):
                # self.correct_valor = self.valor
                # self.correct_base_previdencia = self.base_previdencia
                # self.correct_patronal = self.patronal
                self.clear_changes(
                    [
                        "qnt",
                        "qnt_max",
                        "prazo",
                        "parcela",
                        "valor_base",
                        "base_previdencia",
                    ]
                )

            self.clear_changes(["valor", "patronal"])
            if not self.calculation and self.automated:
                self.calculation = self.evento.calculation

            # log.debug('SFE: %s VALOR: %s CVALOR: %s' % (self.pk, self.valor, self.correct_valor))

        else:
            if not self.status:
                self.status = "CT"

            if not self.copia_de or self.copia_de.folha != self.folha.folha_anterior:
                self._set_has_base()

            self.prazo = (
                1 if self.lancamento == "T" and not self.prazo else (self.prazo or 0)
            )
            self.parcela = 1 if not self.parcela and self.prazo > 0 else self.parcela
            self.installments_paid = (
                1
                if not self.installments_paid and self.prazo > 0
                else self.installments_paid
            )
            # self.qnt = 1 if self.qnt is None and self.lancamento == 'T' else (self.qnt or 0)

            if self.has_pendencies or self.pk is None:
                self.set_pendente()

            if self.pendente:
                self.confirm_if_equals()

            if self.status in ("CT", "CE", "BS"):
                self.correct_valor = self.valor
                self.correct_base_value = self.valor_base
                self.correct_base_previdencia = self.base_previdencia
                self.correct_patronal = self.patronal
                self.correct_qnt = self.qnt
                self.correct_qnt_max = self.qnt_max
                self.correct_pct = self.pct
            else:
                self.valor = 0
                self.valor_base = 0
                self.base_previdencia = 0
                self.patronal = 0
                self.qnt = 0
                self.qnt_max = 0
                self.pct = 0

            # log.debug(self.__dict__)
            res = (
                self.difference_items.aggregate(
                    value=Sum("value"),
                    employer_contribution=Sum("employer_contribution"),
                )
                if self.pk
                else {}
            )

            self.diff_valor_aprovisionado = res.get("value") or 0
            self.diff_patronal_aprovisionado = res.get("employer_contribution") or 0

            if hasattr(self, "_json_calc_vars"):
                self.json_calc_vars = json.encode(self._json_calc_vars)

            if not (self.paycheck_difference and self.automated and self.calculation):
                self.calculation = (
                    self.evento.calculation if self.evento.automated else None
                )

        self.value = (
            float(self.valor) if self.evento.tipo == "P" else -float(self.valor)
        )
        self.correct_value = (
            float(self.correct_valor)
            if self.evento.tipo == "P"
            else -float(self.correct_valor)
        )
        self.diff_value_provisioned = (
            float(self.diff_valor_aprovisionado)
            if self.evento.tipo == "P"
            else -float(self.diff_valor_aprovisionado)
        )
        self.correct_contribution_base = (
            float(self.correct_base_previdencia)
            if self.evento.tipo == "P"
            else -float(self.correct_base_previdencia)
        )

        self.employer_contribution = self.patronal
        self.correct_employer_contribution = self.correct_patronal
        self.diff_employer_contribution_provisioned = self.diff_patronal_aprovisionado

        # if not self.qnt_max:
        #     self.qnt_max = self.qnt
        if len(self.oIds) == 1 and isinstance(self.oIds[0], int):
            self.cid = self.oIds[0]

        # log.debug(('SAVING FOLHAEVENTO: 1. (%s) %s automated: %s PARCELA: %s' % (
        #     self.id, self.evento.numero, self.automated, self.parcela))
        self.automated &= self.evento.automated or (
            self.automated and self.paycheck_difference is not None
        )

        # log.debug(('SAVING FOLHAEVENTO: 2. (%s) %s automated: %s PARCELA: %s' % (
        #     self.id, self.evento.numero, self.automated, self.parcela))

        if self.reason_difference == 1:
            period = Periodo.objects.filter(
                mes=self.reference_month, ano=self.reference_year
            ).last()
            if period and period < self.folha.periodo:
                self.reason_difference = 4

        super(FolhaEvento, self).save(*args, **kargs)
        # log.debug((self.correct_value)
        # Deixando o contracheque em estado de ALTERADO= True
        # Para alterar para ALTERADO = False deve-se executar o método consolidar de contracheque
        paycheck = self.contracheque
        if pendencies and self.status in ("CT", "CE"):
            paycheck.set_changes(ContraCheque.EVENTS)
            # ContraCheque.objects.filter(pk=self.pk).update(alterado=True)
        if self.evento.margins_base.filter(
            type_of_payroll=self.folha.tipo_folha, active=True
        ) or self.evento.margins_consigneds.filter(
            type_of_payroll=self.folha.tipo_folha, active=True
        ):
            paycheck.set_changes(ContraCheque.MARGINS)

        if self.paycheck_difference:
            pd = self.paycheck_difference
            pd.save()


class ContraChequeHistorico(AuditTimestampModel):
    """
    Modelo para armazenar dados de histórico de uma ação de recálculo do ContraChque
    """

    # Os campos abaixo que são IDs e não são FKs servem de valores de referência, e não devem mesmo serem FKs
    # Pois a estratégia do 'on_delete' no campo 'contracheque' é SET_NULL, ou seja, o registro de histórico
    # não deve ser apagado quando o ContraCheque for apagado
    contracheque = models.ForeignKey(
        "ContraCheque",
        related_name="historico",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    contracheque_ref_id = models.BigIntegerField(
        "ContraCheque ID", null=True, blank=True
    )
    servidor_ref_id = models.BigIntegerField("Servidor ID", null=True, blank=True)
    contracheque_ref_ano = models.CharField(
        "Ano ContraCheque", max_length=100, null=True, blank=True
    )
    contracheque_ref_mes = models.CharField(
        "Mês ContraCheque", max_length=100, null=True, blank=True
    )

    class Meta:
        verbose_name = "Histórico de ContraCheque"
        verbose_name_plural = "Históricos de ContraCheque"

    def __str__(self):
        if self.contracheque:
            return f"Histórico do ContraCheque ID: {self.contracheque.pk} - {self.contracheque.folha.periodo.ano}/{self.contracheque.folha.periodo.mes}"
        else:
            return f"Histórico do ContraCheque ID: {self.contracheque_id} - {self.contracheque_ano}/{self.contracheque_mes}"


class FolhaEventoHistorico(models.Model):
    """
    Modelo para armazenar dados de histórico do modelo FolhaEvento
    """

    contracheque_historico = models.ForeignKey(
        ContraChequeHistorico,
        related_name="historico_lancamentos",
        blank=True,
        on_delete=models.PROTECT,
    )
    evento = models.ForeignKey(
        Evento,
        related_name="historico_lancamentos",
        blank=True,
        on_delete=models.PROTECT,
    )
    lancamento = models.CharField(
        max_length=1, choices=list(GFP_TIPO_LANCAMENTO.items()), blank=True
    )
    qnt = models.DecimalField(max_digits=10, decimal_places=6, blank=True, default=0)
    qnt_max = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    parcela = models.PositiveIntegerField(blank=True, default=0)
    prazo = models.PositiveIntegerField(blank=True, default=0)
    pct = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    valor = models.DecimalField(max_digits=16, decimal_places=2, blank=True, default=0)
    valor_base = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    patronal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, default=0
    )
    info = models.CharField(max_length=150, default="", null=True, blank=True)
    base_previdencia = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, blank=True
    )
    status = models.CharField(
        max_length=2,
        choices=list(GFP_STATUS_FOLHAEVENTO.items()),
        default="CT",
        db_index=True,
        blank=True,
    )
    json_calc_vars = models.CharField(max_length=256, default="{}")
    automated = models.BooleanField(verbose_name="Automatizado?", default=False)
    insertion_type = models.PositiveSmallIntegerField(
        verbose_name="Tipo de Inserção",
        choices=Choice.get_choices_for("gfp", "ENTRY_INSERTION_TYPE"),
        default=3,
    )

    class Meta:
        verbose_name = "Histórico de FolhaEvento"
        verbose_name_plural = "Históricos de FolhaEvento"

    def __str__(self):
        return f"FolhaEvento Histórico - evento: {self.evento} - ContraCheque: {self.contracheque_historico}"


@to_search(
    [
        {"name": "servidor__pessoafisica__nome", "type": "text"},
        {"name": "texto", "type": "text"},
    ]
)
class FolhaMensagem(models.Model):

    class Meta:
        unique_together = (("folha", "paycheck", "entry"),)
        # unique_together = (('folha', 'servidor'), )

    folha = models.ForeignKey(
        Folha,
        verbose_name="Folha",
        related_name="messages",
        blank=True,
        on_delete=models.CASCADE,
    )
    paycheck = models.ForeignKey(
        "ContraCheque",
        on_delete=models.CASCADE,
        verbose_name="Contracheque",
        related_name="messages",
        blank=True,
        null=True,
    )
    entry = models.ForeignKey(
        "FolhaEvento",
        verbose_name="Lançamento",
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    texto = models.CharField(max_length=400, verbose_name="Texto")
    label = models.PositiveSmallIntegerField(
        verbose_name="Referência", blank=True, null=True, default=0
    )
    # DEPRECATED
    servidor = models.ForeignKey(
        Servidor,
        verbose_name="Servidor",
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.entry:
            self.folha = self.entry.contracheque.folha
            self.paycheck = self.entry.contracheque
        if self.paycheck:
            self.folha = self.paycheck.folha
            self.servidor = self.paycheck.servidor
        if self.entry and not self.label:
            self.label = self.next_label()

        super(FolhaMensagem, self).save(*args, **kwargs)

    def next_label(self):
        labels = [m.label for m in self.paycheck.messages.all()]
        label = 1
        while label in labels:
            label += 1
        return label

    def __str__(self):
        return self.texto


class Gerente(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    nivel = models.PositiveIntegerField(
        choices=(
            (1, "Folha de Pagamento"),
            (2, "Controle Iterno"),
            (3, "Financeiro"),
            (4, "Outros"),
        )
    )


class ConfigSalaryProgression(AuditTimestampModel):
    class_code = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Código",
        related_name="config_salaryprogression",
        on_delete=models.PROTECT,
    )
    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)

    def __str__(self):
        return "%s - %s: %s" % (
            self.start_validity.strftime("%d/%m/%Y"),
            self.end_validity.strftime("%d/%m/%Y") if self.end_validity else "---",
            self.class_code,
        )

    @property
    def next(self):
        return (
            ConfigSalaryProgression.objects.exclude(pk=self.pk)
            .filter(start_validity__gt=self.start_validity)
            .order_by("start_validity")
            .first()
        )

    @property
    def previous(self):
        return (
            ConfigSalaryProgression.objects.exclude(pk=self.pk)
            .filter(start_validity__lt=self.start_validity)
            .order_by("start_validity")
            .last()
        )

    def save(self, *args, **kwargs):
        if self.previous and self.previous.end_validity is None:
            p = self.previous
            p.end_validity = self.start_validity - relativedelta(days=1)
            p.save()
        if self.next and (
            self.end_validity is None or self.end_validity >= self.next.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo!" % self.next
            )
        if self.previous and (
            self.previous.end_validity is None
            or self.previous.end_validity >= self.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo"
                % self.previous
            )

        super(ConfigSalaryProgression, self).save(*args, **kwargs)


class ProgressionQueryset(models.QuerySet):
    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio_vigencia__gt=range_.last)
                | (~Q(data_fim_vigencia=None) & Q(data_fim_vigencia__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio_vigencia__gt=data)
                | (~Q(data_fim_vigencia=None) & Q(data_fim_vigencia__lt=data))
            )


class MovimentacaoProgressao(MovimentacaoPessoal):

    class Meta:
        verbose_name = "Movimentação Pessoal"
        ordering = [
            "-data_inicio_vigencia",
            "-movimentacao_posse__servidor__pessoa_fisica__nome",
        ]

    objects = ProgressionQueryset.as_manager()

    progressao_anterior = models.ForeignKey(
        "gfp.MovimentacaoProgressao",
        related_name="progressoes",
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )
    movimentacao_posse = models.ForeignKey(
        "rh.MovimentacaoPosse",
        related_name="progressoes",
        blank=True,
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(max_length=60, null=True, blank=True)
    referencia_nivel2d = models.ForeignKey(
        "ReferenciaNiveis2D",
        verbose_name="Referência Níveis",
        related_name="referencia_progressoes",
        blank=True,
        on_delete=models.PROTECT,
    )
    data_referencia_inicial = models.DateField(
        verbose_name="Data Referência", blank=True
    )
    data_referencia = models.DateField(verbose_name="Data Referência", blank=True)
    data_inicio_vigencia = models.DateField(verbose_name="Início Vigência")
    data_fim_vigencia = models.DateField(
        verbose_name="Fim Vigência", null=True, blank=True
    )
    dias_suspenso = models.PositiveIntegerField(
        verbose_name="Dias suspensos", default=0
    )
    dias_suspenso_afastamento = models.PositiveIntegerField(
        verbose_name="Dias suspensos afastamento", default=0
    )
    indireto = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    expected_date = models.DateField(
        verbose_name="Data Prevista", blank=True, null=True
    )
    initial_expected_date = models.DateField(
        verbose_name="Data Prevista", blank=True, null=True
    )
    months_progression = models.PositiveSmallIntegerField(
        default=12, verbose_name="Meses progressão", blank=True
    )
    period_absences = models.PositiveSmallIntegerField(
        default=0, verbose_name="Faltas no período"
    )
    configuration = models.ForeignKey(
        ConfigSalaryProgression,
        verbose_name="Configuração",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    # DEPRECATED
    data_vigencia = models.DateField(verbose_name="Data Vigência", blank=True)

    _classcode = None

    class UnfitRequirementsNotForward(Exception):
        def __init__(self, employee):
            Exception.__init__(
                self,
                "O servidor %s está inapto para progredir, pois possui requisitos insatisfeitos!"
                % employee,
            )

    class FitRequirementsNotExtend(Exception):
        def __init__(self, employee):
            Exception.__init__(
                self,
                "O servidor %s está apto para progredir, pois não possui requisitos insatisfeitos!"
                % employee,
            )

    def __str__(self):
        return "%s" % self.referencia_nivel2d

    @property
    def tipo_movcarreira(self):
        return "PROGRESSAO"

    @property
    def type_progression(self):
        if not hasattr(self, "_type_progression"):
            if not self.progressao_anterior:
                self._type_progression = "I"
            else:
                if (
                    self.progressao_anterior.referencia_nivel2d.vertical
                    == self.referencia_nivel2d.vertical
                ):
                    self._type_progression = "H"
                else:
                    self._type_progression = "V"
        return self._type_progression

    @property
    def next_type_progression(self):
        if self.next_reference.horizontal == self.referencia_nivel2d.horizontal:
            next_type_progression = "H"
        else:
            next_type_progression = "V"
        return next_type_progression

    @property
    def salario(self):
        return self.referencia_nivel2d

    def is_ativo(self, data=None):
        data = datetime.now() if not data else data
        if self.data_fim_vigencia and data.date() > self.data_fim_vigencia:
            return False
        return True

    @property
    def mov_posse_str(self):
        return self.movimentacao_posse.__str__

    def validate(self, *args, **kwargs):
        self.classcode.cls(self).validate(*args, **kwargs)

    def gera_texto_anotacao(self):
        """
        PROGREDIR {tipo_progressao}, a partir de {data_vigencia}, conforme {doc},
        o servidor {nome} inscrito sob a matrícula {matricula}, ocupante do cargo de {cargo},
        da referência {ref_atual} para a referência {ref_nova}. O servidor cumpriu os requisitos
        exigidos na {lei} e suas atualizações.
        """
        texto_progressao = ""
        # if self.progressao_anterior:
        #     if self.progressao_anterior.referencia_nivel2d.nivel_vertical != self.referencia_nivel2d.nivel_vertical:
        #         tipo_progressao = 'V'  # Progressao vertical
        #     else:
        #     tipo_progressao = 'H' if  # Progressao horizontal
        # else:
        #     tipo_progressao = 'I'  # Progressao inicial
        file_template = "progressaoI" if self.type_progression == "I" else "progressao"
        try:
            with codecs.open(
                "%s/%s.txt" % (templates.__path__[0], file_template), "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_progressao = tpl % {
                    "tipo_progressao": (
                        "horizontalmente"
                        if self.type_progression == "H"
                        else "verticalmente"
                    ),
                    "data_vigencia": self.data_inicio_vigencia.strftime("%d/%m/%Y"),
                    "doc": "%s" % self.publicacao_movimentacao,
                    "nome": "%s" % self.servidor.pessoa_fisica.nome,
                    "matricula": self.servidor.matricula,
                    "cargo": "%s - %s"
                    % (
                        self.movimentacao_posse.quadro.cargo.nome,
                        self.movimentacao_posse.quadro.especialidade,
                    ),
                    "ref_atual": "%s" % self.progressao_anterior,
                    "ref_nova": "%s" % self,
                    "lei": "%s" % self.referencia_nivel2d.estrutura_salarial.publicacao,
                }
        except Exception as e:
            texto_progressao = "OCORREU UM ERRO PREENCHENDO ANOTAÇÃO PROGRESSÃO"
            self.log.exception(e)
            raise e
        return texto_progressao

    def anotacao(self, *args, **kargs):
        self.log = getLogger("MovimentacaoProgressao:Model")
        texto_anotacao = self.gera_texto_anotacao() + (
            "<p>%s</p>" % self.get_texto_alteracao()
        )

        try:
            tipo = 3
            if self.publicacao_movimentacao and self.publicacao_movimentacao.tipo == 4:
                tipo = 3
            elif (
                self.publicacao_movimentacao and self.publicacao_movimentacao.tipo == 7
            ):
                tipo = 5
            if self.anotacao_geral is None:
                anotacao_geral = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=(
                        self.publicacao_movimentacao.data_vigencia
                        if self.publicacao_movimentacao
                        else None
                    ),
                    texto=texto_anotacao,
                    resumo=self.tipo_movcarreira,
                    data_documento=datetime.now(),
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
                self.anotacao_geral = anotacao_geral
            else:
                anotacao_geral = AnotacaoCarreira.objects.filter(
                    pk=self.anotacao_geral.pk
                ).first()
                if anotacao_geral:
                    anotacao_geral.publicacao = self.publicacao_movimentacao
                    anotacao_geral.data_portaria_inicio = (
                        self.publicacao_movimentacao.data_vigencia
                        if self.publicacao_movimentacao
                        else None
                    )
                    anotacao_geral.texto = texto_anotacao
                    anotacao_geral.servidor = self.servidor
                    anotacao_geral.tipo_documento = tipo
                    anotacao_geral.indireto = False
                    anotacao_geral.resumo = self.tipo_movcarreira
                    anotacao_geral.save_base()
                    AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                        indireto=True
                    )
        except Exception as e:
            self.log.exception(e)
            # self.log.warnning("Falha na criação da Anotação desta Progressão!")
            raise Exception("Falha na criação da Anotação desta Progressão!")

    @property
    def requirements(self, *args, **kwargs):
        return self.classcode.cls(self).requirements(*args, **kwargs)

    def get_current_configuration(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        configs = ConfigSalaryProgression.objects.exclude(
            Q(start_validity__gt=end_date)
            | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
        )

        return configs.latest("start_validity") if configs.exists() else None

    @property
    def classcode(self):
        if not self._classcode:
            if self.configuration:
                self._classcode = self.configuration.class_code
            else:
                self._classcode = ClassCode.objects.filter(
                    slug="salaryprogression-base"
                ).last()
        return self._classcode

    def validate_if_progressao_arterior_is_the_same(self):
        if self.progressao_anterior and self.progressao_anterior.pk == self.pk:
            raise Exception("A progressão anterior não pode ser a própria progressão.")

    def validate(self):
        self.validate_if_progressao_arterior_is_the_same()

    # @transaction.atomic
    def save(self, *args, **kargs):
        if self.ativo is True:
            self.configuration = self.get_current_configuration(
                start_date=self.data_inicio_vigencia, end_date=self.data_fim_vigencia
            )

            self.servidor = self.movimentacao_posse.servidor

            self.data_vigencia = self.data_inicio_vigencia
            if not self.data_referencia:
                self.data_referencia = self.data_inicio_vigencia
                self.data_referencia_inicial = self.data_inicio_vigencia

            if (
                self.progressao_anterior
                and self.progressao_anterior
                != self.progressao_anterior.progressao_anterior
                and self.progressao_anterior.data_fim_vigencia
                != (self.data_inicio_vigencia + relativedelta(days=-1))
            ):
                self.progressao_anterior.data_fim_vigencia = (
                    self.data_inicio_vigencia + relativedelta(days=-1)
                )
                self.progressao_anterior.save()

            # self.validate(*args, **kargs)
            # TODO Fazer a anotação com um texto homologado pelo RH
            # self.anota and self.anotacao(*args, **kargs)
            # log.debug(('anota??? %s' % self.anota)

            result = self.classcode.cls(self).calculate()

            self.expected_date = result.get("expected_date")
            self.dias_suspenso_afastamento = result.get("dias_suspenso_afastamento")
            if not self.initial_expected_date:
                self.initial_expected_date = result.get("initial_expected_date")
            self.period_absences = result.get("period_absences")

            self.months_progression = self.referencia_nivel2d.months_progression

            self.ativo = self.is_ativo()
        super(MovimentacaoProgressao, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        if self.progressao_anterior:
            self.progressao_anterior.ativo = True
            self.data_fim_vigencia = None
            self.progressao_anterior.save()

        if self.anotacao_geral:
            # MovimentacaoProgressao.objects.filter(pk= self.pk).update(anotacao_geral= None)
            self.anotacao_geral.delete()
        super(MovimentacaoProgressao, self).delete(*args, **kargs)

    def _get_previous(self):
        return (
            MovimentacaoProgressao.objects.filter(
                movimentacao_posse=self.movimentacao_posse
            )
            .exclude(data_inicio_vigencia__gte=self.data_inicio_vigencia)
            .latest("data_inicio_vigencia")
        )

    @property
    def next_reference(self):
        if not hasattr(self, "_next_reference"):
            self._next_reference = (
                self.referencia_nivel2d.estrutura_salarial.references.exclude(
                    ordem__lte=self.referencia_nivel2d.ordem
                )
                .order_by("ordem")
                .first()
            )
        return self._next_reference

    def anotacao_alteracao(self, *args, **kargs):
        """
        Não deve ser igual à implementação da classe base.
        """
        pass

    def get_texto_alteracao(self):
        texto = ""
        if self.publicacao_alteracao:
            texto = "RETIFICADO pelo %s." % self.publicacao_alteracao
        return texto

    def set_expected_date(self, new_reference):
        self.expected_date = new_reference
        self.save_base()

    def extend(self, motivo, new_date, date_reference):
        # requirements = self.requirements
        # if not requirements['unfit']:
        #     raise self.FitRequirementsNotExtend(self.servidor)
        try:
            # day, month, year = new_date.split('/')
            # new_reference = datetime(int(year), int(month), int(day)).date()
            new_reference = datetime.strptime(new_date, "%d/%m/%Y")
            date_reference = datetime.strptime(date_reference, "%d/%m/%Y")
            # self.data_referencia = self.expected_date
            dr = NewDateRange(self.expected_date, new_reference)
            self.extensions.create(
                start_date_extension=datetime.now().date(), days=dr.days, purpose=motivo
            )
            self.ativo = False
            self.save_base()

            new_progression_movimentation = MovimentacaoProgressao.objects.create(
                progressao_anterior=self.progressao_anterior,
                # data_inicio_vigencia=new_reference,
                data_inicio_vigencia=self.data_inicio_vigencia,
                data_referencia_inicial=self.data_referencia_inicial,
                initial_expected_date=self.initial_expected_date,
                # expected_date=new_reference,
                # data_referencia=self.data_referencia_inicial,
                data_referencia=date_reference,
                referencia_nivel2d=self.referencia_nivel2d,
                movimentacao_posse=self.movimentacao_posse,
                publicacao_movimentacao=self.publicacao_movimentacao,
            )
            new_progression_movimentation.set_expected_date(new_reference)
            # new_progression_movimentation.save()

        except Exception as err:
            log.error(err)

    def forward(self, publication):
        requirements = self.requirements
        if requirements["unfit"]:
            raise self.UnfitRequirementsNotForward(self.servidor)

        novo_inicio_vigencia = self.expected_date
        novo_expected_date = self.expected_date.replace(self.expected_date.year + 5)

        MovimentacaoProgressao.objects.get_or_create(
            progressao_anterior=self,
            data_inicio_vigencia=novo_inicio_vigencia,
            expected_date=novo_expected_date,
            referencia_nivel2d=self.next_reference,
            defaults={
                "movimentacao_posse": self.movimentacao_posse,
                "publicacao_movimentacao": publication,
            },
        )

    def forward_h(self, publication, solicitation):
        from rh.pvf.models import PortalRequestHistory

        if not publication:
            raise Exception("Favor selecionar a Publicação!")

        self.validate_doc_approver(solicitation)

        requirements = self.requirements
        if requirements["unfit"]:
            raise self.UnfitRequirementsNotForward(self.servidor)

        target_reference = ReferenciaNiveis2D.objects.get(
            estrutura_salarial=solicitation.config.schooling,
            horizontal=solicitation.config.target_level,
            vertical=self.referencia_nivel2d.vertical,
        )

        if target_reference == self.referencia_nivel2d:
            raise Exception("A Progressão Destino é igual a Progressão Atual!")

        pub = Publicacao.objects.get(pk=int(publication))

        prh = (
            PortalRequestHistory.objects.filter(
                portal_request=solicitation,
                action__in=[REQUEST_ACT_OPEN_SOLICITANTION, REQUEST_ACT_SOLICITATION],
            )
            .order_by("date")
            .last()
        )
        MovimentacaoProgressao.objects.get_or_create(
            progressao_anterior=self,
            data_inicio_vigencia=prh.date.date(),
            expected_date=self.expected_date,
            referencia_nivel2d=target_reference,
            data_referencia=self.data_referencia,
            data_referencia_inicial=self.data_referencia,
            defaults={
                "movimentacao_posse": self.movimentacao_posse,
                "publicacao_movimentacao": pub,
            },
        )

        self.data_fim_vigencia = prh.date.date() - timedelta(days=1)
        self.save()

    def validate_doc_approver(self, solicitation):
        if not solicitation.document.filter(doc_origin__in=[REQUEST_STEP_GER_DEV]):
            raise Exception("Favor adicionar o documento!")

    @classmethod
    def finish_progression_by_fire(cls, fire_move, undo=False):
        """
        :py:function:: finish_progression_by_fire(fire_move, undo=True):

        This method finishes progression of employee.

        """
        if fire_move.termination_process:
            progressions = MovimentacaoProgressao.objects.filter(
                movimentacao_posse=fire_move.movimentacao_posse,
                movimentacao_posse__quadro__cargo__tipo_lei_cargo="EF",
                servidor__tipo="S",
            )
            date_fired = fire_move.data_desligamento + relativedelta(days=-1)
            if undo:
                progressions = progressions.filter(data_fim_vigencia=date_fired)
                date_fired = None
            else:
                progressions = progressions.filter(data_fim_vigencia=None)
            for progression in progressions:
                try:
                    with transaction.atomic():
                        progression.data_fim_vigencia = date_fired
                        progression.save()
                except Exception as err:
                    log.exception(err)

    @classmethod
    def cmd_update_lacks_and_suspensions(cls):
        """
        Este método é responsável por atualizar os campos Faltas e Suspensões
        da Movimentação Progressão
        """
        for movimentacao_prog in MovimentacaoProgressao.objects.filter(ativo=True):
            result = movimentacao_prog.classcode.cls(movimentacao_prog).calculate()
            movimentacao_prog.dias_suspenso_afastamento = result.get(
                "dias_suspenso_afastamento"
            )
            movimentacao_prog.period_absences = result.get("period_absences")
            movimentacao_prog.save_base()


class ExtensionSalaryProgression(models.Model):

    progression = models.ForeignKey(
        MovimentacaoProgressao, related_name="extensions", on_delete=models.CASCADE
    )
    days = models.PositiveIntegerField(default=0, verbose_name="Dias")
    start_date_extension = models.DateField(
        verbose_name="Data início prorrogação", blank=True
    )
    purpose = models.TextField(verbose_name="Motivo", default="")


class ProgressionDocument(AuditTimestampModel):
    class Meta:
        verbose_name = "Documentos de Progressão"

    progression = models.ForeignKey(
        MovimentacaoProgressao, related_name="document", on_delete=models.CASCADE
    )
    description = models.CharField(
        verbose_name="Descrição", max_length=250, null=True, blank=True
    )
    attachment = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attachment_progression_doc",
    )
    doc_origin = models.SmallIntegerField(
        verbose_name="Origem do Documento", null=True, blank=True
    )

    def __str__(self):
        return "%s" % self.description

    def get_doc_origin_display(self, value):
        if value:
            return Choice.objects.get(
                app_label="pvf",
                name="REQUEST_STEP",
                value=value,
            ).label
        else:
            return ""

    def add_step_ass_jur(self, prpv, employee):
        if (
            employee.user.groups.filter(
                name__in=[GROUP_ASS_JUR_1, GROUP_ASS_JUR_2]
            ).count()
            > 0
        ):
            self.doc_origin = prpv.step_current
        else:
            raise Exception(
                f"""Só é permitido adicionar documento nesta estapa, os usuários dos grupos 
                {self.get_doc_origin_display(REQUEST_STEP_JURIDICAL_ADVISORY_1)} e {self.get_doc_origin_display(REQUEST_STEP_JURIDICAL_ADVISORY_2)}"""
            )

    def add_step_prog_dg(self, prpv, employee):
        if employee.user.groups.filter(name__in=[GROUP_PROG_DG]).count() > 0:
            self.doc_origin = prpv.step_current
        else:
            raise Exception(
                f"Só é permitido adicionar documento nesta estapa, os usuários do grupo {self.get_doc_origin_display(REQUEST_STEP_PROG_DG)}"
            )

    def validate_step_ass_jur(self, prpv, employee):
        if (
            employee.user.groups.filter(
                name__in=[GROUP_ASS_JUR_1, GROUP_ASS_JUR_2]
            ).count()
            > 0
        ):
            self.doc_origin = prpv.step_current
        else:
            raise Exception(
                f"Só é permitido editar/remover este documento, os usuários do grupo {self.get_doc_origin_display(self.doc_origin)}"
            )

    def validate_step_prog_dg(self, prpv, employee):
        if employee.user.groups.filter(name__in=[GROUP_PROG_DG]).count() > 0:
            self.doc_origin = prpv.step_current
        else:
            raise Exception(
                f"Só é permitido editar/remover este documento, os usuários do grupo {self.get_doc_origin_display(self.doc_origin)}"
            )

    def validate_attachment(self):
        if not self.attachment:
            raise Exception("Favor selecionar um documento!")

    def validate(self):
        from rh.pvf.models import PortalRequestProgression

        self.validate_attachment()
        employee = employee_from_user(get_current_user())
        step_ass_jur = [
            REQUEST_STEP_JURIDICAL_ADVISORY_1,
            REQUEST_STEP_JURIDICAL_ADVISORY_2,
        ]
        if self.pk:
            # Editar
            prpv = PortalRequestProgression.objects.filter(
                progression__document__pk=self.pk
            )
            if prpv:
                if (
                    prpv.first().step_current in step_ass_jur
                    and self.doc_origin in step_ass_jur
                ):
                    self.validate_step_ass_jur(prpv.first(), employee)
                if prpv.first().step_current == self.doc_origin and self.doc_origin in [
                    REQUEST_STEP_PROG_DG
                ]:
                    self.validate_step_prog_dg(prpv.first(), employee)
            else:
                self.doc_origin = 13  # Gerência de Desenvolvimento
        else:
            # Criar
            prpv = PortalRequestProgression.objects.filter(
                progression__pk=self.progression.pk
            )
            if prpv:
                if prpv.first().step_current in step_ass_jur:
                    self.add_step_ass_jur(prpv.first(), employee)
                if prpv.first().step_current in [REQUEST_STEP_PROG_DG]:
                    self.add_step_prog_dg(prpv.first(), employee)
            else:
                self.doc_origin = 13  # Gerência de Desenvolvimento

    def save(self, *args, **kwargs):
        self.validate()
        super(ProgressionDocument, self).save(*args, **kwargs)

    def delete(self, *args, **kargs):
        self.validate()
        super(ProgressionDocument, self).delete(*args, **kargs)


class HorizontalProgressionConfig(AuditTimestampModel):
    class Meta:
        verbose_name = "Configuração de Progressão Horizontal"

    schooling = models.ForeignKey(
        "gfp.EstruturaTabelaSalarial",
        related_name="horizontal_prog_config",
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name="Nome", max_length=100, null=True, blank=True)
    description = models.CharField(
        verbose_name="Descrição", max_length=250, null=True, blank=True
    )
    target_level = models.CharField(
        verbose_name="Progressão Destino", max_length=1, null=True, blank=True
    )
    contribution_time = models.SmallIntegerField(
        verbose_name="Tempo de Casa (anos)", null=True, blank=True
    )
    qtd_documents = models.SmallIntegerField(
        verbose_name="Quantidade de Documentos", null=True, blank=True
    )

    def __str__(self):
        return "%s" % self.name

    def validate_name(self):
        if not self.name:
            raise Exception("Favor preencher o Nome")

    def validate_description(self):
        if not self.description:
            raise Exception("Favor preencher a Descrição")

    def validate_schooling(self):
        if not self.schooling:
            raise Exception("Favor preencher a Escolaridade")

    def validate_target_level(self):
        if not self.target_level:
            raise Exception("Favor preencher a Progressão Destino")

    @property
    def schooling_str(self):
        return self.schooling.__str__

    def validate(self):
        self.validate_name()
        self.validate_description()
        self.validate_schooling()
        self.validate_target_level()

    def save(self, *args, **kwargs):
        self.validate()
        super(HorizontalProgressionConfig, self).save(*args, **kwargs)


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "data", "type": "date"},
        {"name": "referencia_nivel2d__estrutura_salarial__codigo", "type": "text"},
        {"name": "movimentacao_posse__servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "movimentacao_posse__quadro__cargo__nome", "type": "text"},
        {"name": "movimentacao_posse__quadro__especialidade__nome", "type": "text"},
        {"name": "publicacao_movimentacao__numero", "type": "text"},
    ]
)
class MovimentacaoEnquadramento(MovimentacaoProgressao):
    class Meta:
        verbose_name = "Movimentação de Enquadramento"

    @property
    def tipo_movcarreira(self):
        return "ENQUADRAMENTO"

    def validate(self, *args, **kargs):
        self.log = getLogger("MovimentacaoEnquadramento:Model")
        self.log.info("VALIDATE MovimentacaoEnquadramento...")
        super(MovimentacaoEnquadramento, self).validate(*args, **kargs)

        return True

    def gera_texto_anotacao(self):
        """
        ENQUADRAR, a partir de %(data_vigencia)s, conforme %(doc)s, o servidor %(nome)s inscrito sob
        a matrícula %(matricula)s, ocupante do cargo %(cargo)s e nesta data posicionado na
        referência %(ref_atual)s da estrutura definida pela %(lei_atual)s, na referência %(ref_nova)s
        definida pela %(lei_nova)s. O servidor cumpriu os requisitos exigidos na %(lei_nova)s para o
        presente enquadramento.
        """
        texto_progressao = ""
        try:
            with codecs.open(
                "%s/enquadramento.txt" % (templates.__path__[0]), "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_progressao = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "data_vigencia": self.data_vigencia.strftime("%d/%m/%Y"),
                    "doc": "%s" % self.publicacao_movimentacao,
                    "nome": "%s" % self.servidor.pessoa_fisica.nome,
                    "matricula": self.servidor.matricula,
                    "cargo": "%s - %s"
                    % (
                        self.movimentacao_posse.quadro.cargo.nome,
                        self.movimentacao_posse.quadro.especialidade,
                    ),
                    "ref_atual": "%s" % self.progressao_anterior,
                    "ref_nova": "%s" % self,
                    "lei_atual": "%s"
                    % self.progressao_anterior.referencia_nivel2d.estrutura_salarial.publicacao,
                    "lei_nova": "%s"
                    % self.referencia_nivel2d.estrutura_salarial.publicacao,
                }
        except Exception as e:
            texto_progressao = "OCORREU UM ERRO PREENCHENDO ANOTAÇÃO ENQUADRAMENTO"
            self.log.exception(e)
            raise e
        return texto_progressao


@deprecated
class DadoBancarioServidorFolha(AuditTimestampModel):

    AUDITABLE = {"exclude": ["abstract_fields", "data_vigencia", "criado_em", "id"]}

    class Meta:
        ordering = [
            "dado_bancario_pessoa__pessoa",
            "tipo_folha",
            "-data_inicio_vigencia",
        ]
        db_table = "gfp_dadobancariopessoafolha"

    dado_bancario_pessoa = models.ForeignKey(
        "rh.DadoBancarioPessoa",
        related_name="dado_bancario_folhas",
        on_delete=models.CASCADE,
    )
    tipo_folha = models.ForeignKey(
        "gfp.FolhaTipo",
        blank=True,
        null=True,
        related_name="banco_servidores",
        on_delete=models.CASCADE,
    )
    data_vigencia = models.DateTimeField(
        blank=True, null=True, verbose_name="Início Vigência"
    )
    data_inicio_vigencia = models.DateField(null=True, verbose_name="Início Vigência")
    data_fim_vigencia = models.DateField(
        blank=True, null=True, verbose_name="Fim Vigência"
    )
    # criado_em = models.DateField(auto_now_add=True, verbose_name='Criado em')

    class NotValidateDBSF(Exception):
        def __init__(self, texto=None):
            Exception.__init__(
                self, texto or "Erro na validação do dado bancário do servidor"
            )

    # @transaction.atomic
    def save(self, set_finally=False, *args, **kargs):

        # log.debug(('SAVE DBSF INI')
        dbsfs = DadoBancarioServidorFolha.objects.filter(
            dado_bancario_pessoa__pessoa=self.dado_bancario_pessoa.pessoa,
            tipo_folha=self.tipo_folha,
        ).order_by("-data_inicio_vigencia")

        if not self.pk:
            # log.debug(('CRIANDO DBSF')
            # Inserindo um novo dado bancario para a pessoa
            if dbsfs.filter(data_fim_vigencia=None).count() > 1:
                # log.debug(('CRIANDO DBSF 1')
                raise self.NotValidateDBSF(
                    "Existe mais de um dado bancario para o servidor %s sem data final de vigência na folha %s. \
                        Corrija-as e tente adicionar o novo dado bancario novamente"
                    % (self.dado_bancario_pessoa.pessoa, self.tipo_folha)
                )
            elif (
                dbsfs.filter(data_fim_vigencia=None)
                and dbsfs.get(data_fim_vigencia=None).dado_bancario_pessoa
                == self.dado_bancario_pessoa
            ):
                # log.debug(('CRIANDO DBSF 2')
                log.exception(
                    "O dado bancário (%s:%s:%s) já está vigente nessa data para a folha %s e por isso não necessita \
                        ser adicionado"
                    % (
                        self.dado_bancario_pessoa,
                        dbsfs[0].data_inicio_vigencia,
                        dbsfs[0].data_fim_vigencia,
                        self.tipo_folha,
                    )
                )
                raise self.NotValidateDBSF(
                    "O dado bancário (%s) já está vigente nessa data para a folha %s e por isso não necessita ser \
                        adicionado"
                    % (self.dado_bancario_pessoa, self.tipo_folha)
                )
            elif dbsfs.filter(data_inicio_vigencia__gte=self.data_inicio_vigencia):
                # log.debug(('CRIANDO DBSF 3')
                log.exception(
                    "Já existe um dado bancário para o servidor %s na folha %s com início de vigência em %s. \
                        Indique uma data posterior a %s"
                    % (
                        self.dado_bancario_pessoa.pessoa,
                        self.tipo_folha,
                        self.data_inicio_vigencia.strftime("%d/%m/%Y"),
                        dbsfs.filter(
                            data_inicio_vigencia__gte=self.data_inicio_vigencia
                        )[0].data_inicio_vigencia.strftime("%d/%m/%Y"),
                    )
                )
                raise self.NotValidateDBSF(
                    "Já existe um dado bancário para o servidor %s na folha %s com início de vigência em %s. Indique \
                        uma data posterior a %s"
                    % (
                        self.dado_bancario_pessoa.pessoa,
                        self.tipo_folha,
                        self.data_inicio_vigencia.strftime("%d/%m/%Y"),
                        dbsfs.filter(
                            data_inicio_vigencia__gte=self.data_inicio_vigencia
                        )[0].data_inicio_vigencia.strftime("%d/%m/%Y"),
                    )
                )

            # log.debug(dbs)
            # log.debug(dbsfs.filter(data_fim_vigencia=None))
            if dbsfs.filter(data_fim_vigencia=None):
                dbsf_prev = dbsfs.get(data_fim_vigencia=None)
                # log.debug(('ALTERANDO DBSF ANTERIOR: %s:%s:%s' % (
                #     dbsf_prev, dbsf_prev.data_inicio_vigencia, dbsf_prev.data_fim_vigencia))
                dbsf_prev.data_fim_vigencia = self.data_inicio_vigencia - relativedelta(
                    days=1
                )
                dbsf_prev.save(set_finally=True)
                # log.debug(('ALTERANDO DBSF ANTERIOR: %s:%s:%s' % (
                #     dbsf_prev, dbsf_prev.data_inicio_vigencia, dbsf_prev.data_fim_vigencia))
                # DadoBancarioServidorFolha.objects.filter(pk=dbsfs.get(data_fim_vigencia=None).pk)
                # dbsfs.filter(data_fim_vigencia=None).update(
                #   data_fim_vigencia=(self.data_inicio_vigencia - relativedelta(days=1)))
        else:
            # log.debug(('ATUALIZANDO DBSF')
            # Atualizando o dado bancario de uma pessoa
            # Apenas possível para inclusao da data_fim_vigencia
            if "data_fim_vigencia" in self.old_fields and len(self.old_fields) == 1:
                log.debug("UPDATING DATA_FIM_VIGENCIA")
            else:
                raise self.NotValidateDBSF(
                    "O dado bancário do servidor não pode ser alterado!"
                )

        super(DadoBancarioServidorFolha, self).save(*args, **kargs)
        # log.debug(('SAVE DBSF FIM')

    def delete(self, *args, **kargs):

        dbsfs = (
            DadoBancarioServidorFolha.objects.filter(
                dado_bancario_pessoa__pessoa=self.dado_bancario_pessoa.pessoa,
                tipo_folha=self.tipo_folha,
            )
            .exclude(pk=self.pk)
            .order_by("-data_inicio_vigencia")
        )
        log.info("DELETE DBSF INI")

        if dbsfs.filter(data_inicio_vigencia__gt=self.data_inicio_vigencia):
            raise self.NotValidateDBSF(
                "O dado bancário (%s) não pode ser apagado pois possui outros dadas bancários de vigência posterior!"
                % self.dado_bancario_pessoa
            )

        super(DadoBancarioServidorFolha, self).delete(*args, **kargs)

        if dbsfs.filter(data_inicio_vigencia__lt=self.data_inicio_vigencia):
            dbfs_last = dbsfs.filter(
                data_inicio_vigencia__lt=self.data_inicio_vigencia
            )[0]
            dbfs_last.data_fim_vigencia = None
            dbfs_last.save(set_finally=True)


class BankingEmployeeTypePayroll(AuditTimestampModel):
    AUDITABLE = {
        "exclude": [
            "abstract_fields",
        ]
    }

    class Meta:
        unique_together = [
            ("person", "type_of_payroll"),
        ]
        ordering = ["banking_person__pessoa", "type_of_payroll"]

    class DifferentPerson(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Dados bancários e servidor não possuem mesma pessoa física!"
            )

    person = models.ForeignKey(
        "rh.Pessoa",
        related_name="bankings_employee_payroll",
        verbose_name="Pessoa",
        on_delete=models.CASCADE,
    )
    type_of_payroll = models.ForeignKey(
        "gfp.FolhaTipo",
        on_delete=models.CASCADE,
        related_name="bankings_employee_payroll",
        verbose_name="Tipo de folha",
    )
    banking_person = models.ForeignKey(
        "rh.DadoBancarioPessoa",
        related_name="bankings_employee_payroll",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.person != self.banking_person.pessoa:
            raise self.DifferentPerson()
        super(BankingEmployeeTypePayroll, self).save(*args, **kwargs)


@deprecated
class RRAServidorFolhaTipo(models.Model):
    class Meta:
        ordering = ["-folha_tipo", "servidor__pessoa_fisica__nome"]
        db_table = "gfp_rraservidorfolhatipo"
        unique_together = ("servidor", "folha_tipo", "quantidade")

    servidor = models.ForeignKey(
        Servidor, related_name="com_rra_folhatipo", on_delete=models.CASCADE
    )
    folha_tipo = models.ForeignKey(
        FolhaTipo, related_name="rra_servidores", on_delete=models.CASCADE
    )
    quantidade = models.DecimalField(max_digits=7, decimal_places=2)


class RRA(AuditTimestampModel):

    class Meta:
        ordering = [
            "title",
        ]

    title = models.CharField(max_length=50, unique=True, verbose_name="Título")
    slug = models.SlugField(max_length=50, verbose_name="Identificação", blank=True)
    process = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Processo"
    )
    events = models.ManyToManyField(
        Evento, related_name="rra_event", verbose_name="Eventos"
    )
    process_type = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "PROCESS_TYPE_RRA"), default=1
    )

    def __str__(self):
        return "%s" % self.title

    def save(self, *args, **kwargs):

        if not self.pk:
            self.slug = slugify(self.title).upper()

        super(RRA, self).save(*args, **kwargs)


class RRAEmployee(AuditTimestampModel):

    class Meta:
        ordering = ["employee", "rra__title", "months"]
        unique_together = ("employee", "rra")

    employee = models.ForeignKey(
        Servidor,
        verbose_name="Servidor",
        related_name="rra_references",
        on_delete=models.CASCADE,
    )
    rra = models.ForeignKey(
        RRA, verbose_name="RRA", related_name="employeers", on_delete=models.PROTECT
    )
    months = models.PositiveSmallIntegerField(
        verbose_name="Quantidade de meses", default=0
    )
    factor = models.DecimalField(
        verbose_name="Fator", decimal_places=4, max_digits=8, default=0
    )

    def __str__(self):
        return "%s - %s" % (self.rra, self.employee)


@to_search(
    [
        {"name": "titulo__icontains", "type": "text"},
        {"name": "slug__icontains", "type": "text"},
        {"name": "principais__numero__icontains", "type": "text"},
        {"name": "principais__titulo__icontains", "type": "text"},
        {"name": "acessorios__numero__icontains", "type": "text"},
        {"name": "acessorios__titulo__icontains", "type": "text"},
    ]
)
class FolhaModelo(models.Model):
    titulo = models.CharField(max_length=120, verbose_name="Título")
    slug = models.SlugField(
        max_length=120, unique=True, blank=True, verbose_name="Identificador"
    )
    principais = models.ManyToManyField(
        Evento, related_name="como_principal", verbose_name="Verbas principais"
    )
    acessorios = models.ManyToManyField(
        Evento, related_name="come_acessorio", verbose_name="Verbas acessório"
    )
    para_indicativo = models.CharField(
        max_length=1,
        choices=rh_const.INDICATIVO,
        verbose_name="Para os",
        null=True,
        default=None,
        blank=True,
    )
    servidores = models.ManyToManyField(Servidor, related_name="nos_modelos")
    types_of_employee = models.ManyToManyField(
        "standard.Choice", related_name="models_payroll"
    )
    previdencia = models.BooleanField(verbose_name="Previdência", default=False)
    somente_ativo = models.BooleanField(
        verbose_name="Somente para ativos na folha", default=False
    )
    somente_folha = models.BooleanField(
        verbose_name="Somente servidores da folha", default=False
    )

    class Meta:
        ordering = [
            "titulo",
        ]

    def __str__(self):
        return self.titulo

    @property
    def all_servidores(self):

        if self.servidores.exists():
            query = self.servidores.filter()
        else:
            types = [c.cvalue for c in self.types_of_employee.all()]
            query = Servidor.objects.filter(type_by_possession__in=types)

        return query

    def get_all_new_employees(self, payroll, only_not_in_payroll=True):
        model_payroll = payroll.tipo_folha.modelo or self
        if self.servidores.exists() and model_payroll.servidores.exists():
            query = Servidor.objects.filter(
                Q(pk__in=[s.pk for s in self.servidores.all()])
                | Q(pk__in=[s.pk for s in model_payroll.servidores.all()])
            )
        else:
            types = [c.cvalue for c in self.types_of_employee.all()]
            types += [c.cvalue for c in model_payroll.types_of_employee.all()]
            query = Servidor.objects.filter(type_by_possession__in=types)

        only_payroll = self.somente_folha and model_payroll.somente_folha
        only_actives = self.somente_ativo and model_payroll.somente_ativo
        if only_payroll:
            return query.filter(paychecks__folha=payroll)

        # Encontrando os novos servidores com possibilidade de entrar na folha
        new_pks = []
        for s in query.exclude(paychecks__folha=payroll):
            # log.debug('************ %s:%s' % (s.data_exercicio, payroll.date_range))
            if payroll.paychecks.filter(servidor=s).exists():
                continue
            if only_actives:
                if (
                    s.data_exercicio and s.data_exercicio <= payroll.date_range.last
                ) and (
                    s.data_desligamento is None
                    or s.data_desligamento > payroll.date_range.first
                ):
                    new_pks.append(s.pk)
            else:
                new_pks.append(s.pk)

        if only_not_in_payroll:
            query = query.filter(pk__in=new_pks)
        else:
            query = query.filter(Q(pk__in=new_pks) | Q(paychecks__folha=payroll))

        return query

    def save(self, *args, **kargs):

        if self.slug in [None, "", 0]:
            slug = slugify(self.titulo)
            self.slug = slug

            count = 0
            while FolhaModelo.objects.filter(slug=self.slug).exists():
                count += 1
                self.slug = slugify("%s %d" % (self.slug, count))

        models.Model.save(self, *args, **kargs)


class SalaryStructureManager(models.Manager):

    def get_by_natural_key(self, title):
        return self.get(titulo=title)


class EstruturaTabelaSalarial(AuditTimestampModel):
    class Meta:
        ordering = ["-ativo", "-data_vigencia_inicio", "codigo"]
        db_table = "gfp_estruturasalarial"
        unique_together = ("codigo", "publicacao", "identifier")

    AUDITABLE = {
        "exclude": [
            "titulo",
            "descricao",
            "ativo",
        ],
        "clear_after_save": True,
    }

    # objects = SalaryStructureManager()
    titulo = models.CharField(max_length=100, verbose_name="Título", blank=True)
    codigo = models.CharField(
        max_length=10, verbose_name="Código", blank=True, null=True
    )
    identifier = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("gfp", "STRUCTURE_IDENTIFIER")
    )
    formatacao = models.CharField(
        max_length=100, verbose_name="Formatação", blank=True, null=True
    )
    descricao = models.CharField(
        max_length=400, verbose_name="Descrição", blank=True, null=True
    )
    meses_progressao_inicial = models.SmallIntegerField(
        verbose_name="Progressões inicial", default=36, blank=True
    )
    meses_progressao = models.SmallIntegerField(
        verbose_name="Progressões", default=12, blank=True
    )
    data_vigencia_inicio = models.DateField(
        verbose_name="Início vigência", blank=True, null=True
    )
    data_vigencia_fim = models.DateField(
        verbose_name="Fim vigência", blank=True, null=True
    )
    modelo_tabela = models.ForeignKey(
        "ModeloTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Modelo",
        related_name="estruturas",
        null=True,
        blank=True,
    )
    publicacao = models.ForeignKey(
        Publicacao,
        verbose_name="Publicação",
        related_name="estruturas_salariais",
        on_delete=models.CASCADE,
    )
    ativo = models.BooleanField(default=True, blank=True)
    horizontal_name = models.CharField(max_length=20, default="REFERÊNCIA")
    vertical_name = models.CharField(max_length=20, default="CLASSE")
    horizontal_labels = models.CharField(max_length=100, default="")
    vertical_labels = models.CharField(max_length=100, default="")
    estrutura_revogacao = models.ForeignKey(
        "EstruturaTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Revogado por",
        related_name="estrutura_revogadas",
        null=True,
        blank=True,
    )
    salary_unit = models.PositiveSmallIntegerField(
        "Unidade de salário fixo",
        choices=Choice.get_choices_for("gfp", "SALARY_UNIT"),
        default=5,
        blank=True,
    )

    def __str__(self):
        return "%s" % self.titulo

    @property
    def referencia_niveis(self):
        return self.modelo_tabela.referencias

    def save(self, *args, **kargs):
        new = self.pk is None

        if not self.formatacao:
            self.formatacao = "{CODIGO}-{VERTICAL}{HORIZONTAL}"

        h_values = self.horizontal_labels.split("|")
        v_values = self.vertical_labels.split("|")

        if len(h_values) != len(set(h_values)):
            raise self.LevelsRepeatedNotAllowed("H")
        if len(v_values) != len(set(v_values)):
            raise self.LevelsRepeatedNotAllowed("V")

        if (
            "vertical_labels" in self.old_fields
            and not self.vertical_labels.startswith(self.old_fields["vertical_labels"])
        ):
            raise self.ChangeLevelsNotAllowed()
        if (
            "horizontal_labels" in self.old_fields
            and not self.horizontal_labels.startswith(
                self.old_fields["horizontal_labels"]
            )
        ):
            raise self.ChangeLevelsNotAllowed()

        if not self.titulo:
            self.titulo = "%s - %s" % (self.codigo, self.publicacao)

        change_format = "formatacao" in self.old_fields
        change_end_date = "data_vigencia_fim" in self.old_fields

        super(EstruturaTabelaSalarial, self).save(*args, **kargs)

        # Criando as referencias iniciais do Modelo e ordenando de acordo com os niveis (v_values X h_values)
        if (
            new
            or "vertical_labels" in self.old_fields
            or "horizontal_labels" in self.old_fields
        ):
            ordem = 1
            for v in v_values:
                for h in h_values:
                    rn2d, created = self.references.get_or_create(
                        horizontal=h,
                        vertical=v,
                        ordem=ordem,
                        defaults={
                            "months_progression": (
                                self.meses_progressao_inicial
                                if ordem == 1
                                else self.meses_progressao
                            )
                        },
                    )
                    ordem += 1

        #  Updataing sigla_cache for all referencia_nivel2d of this object
        if change_format:
            for rn in self.references.all():
                rn.sigla_cache = self.formatacao.format(
                    VERTICAL=rn.vertical or "",
                    HORIZONTAL=rn.horizontal or "",
                    CODIGO=self.codigo or "",
                )
                rn.save()
                rn.referencias_salarios.filter(
                    tabela_salarial__estrutura_salarial=self
                ).update(sigla_cache=rn.sigla_cache)

        if change_end_date:
            # TODO Verificar se é necessário usar o save ou pode ser pelo update mesmo
            self.tabelas_vigentes.filter(
                data_vigencia_fim=self.old_fields["data_vigencia_fim"]
            ).update(data_vigencia_fim=self.data_vigencia_fim)
            self.cargos_estrutura.filter(
                data_vigencia_fim=self.old_fields["data_vigencia_fim"]
            ).update(data_vigencia_fim=self.data_vigencia_fim)

    def delete(self, *args, **kargs):
        pass

    @classmethod
    def salarios(cls, cargo, data_inicio=None, data_fim=None, referencia=None):
        from rh.gfp.plugins.rh_models import ReferenciaSalarialNotFound

        salarios_ = []
        if data_inicio is None:
            data_inicio = datetime.today()

        if data_fim is None:
            data_fim = data_inicio
        range_ = NewDateRange(data_inicio, data_fim)
        tabelas = TabelaSalarial.tabelas_vigente(cargo, data_inicio, data_fim)

        ces = (
            CargosEstrutura.objects.filter(
                estrutura_salarial__in=[t.estrutura_salarial for t in tabelas],
                cargo=cargo,
            )
            .exclude(
                Q(data_vigencia_inicio__gt=data_fim)
                | (~Q(data_vigencia_fim=None) & Q(data_vigencia_fim__lt=data_inicio))
            )
            .order_by("data_vigencia_inicio")
        )

        salarios_query = ReferenciaSalario.objects.filter(tabela_salarial__in=tabelas)
        if referencia:
            salarios_query = salarios_query.filter(referencia_nivel2d=referencia)
        # log.debug("SALARIOS: %s DI: %s DF: %s REF: %s - %s" % (
        #   salarios_query, data_inicio, data_fim, referencia, cargo))

        for ce in ces:
            for salario in salarios_query.filter(
                referencia_nivel2d__in=ce.referencias.all()
            ):
                salarios_.append(
                    (
                        range_.intersect(
                            NewDateRange(
                                ce.data_vigencia_inicio, ce.data_vigencia_fim
                            ).intersect(
                                NewDateRange(
                                    salario.tabela_salarial.start_validity,
                                    salario.tabela_salarial.end_validity,
                                )
                            )
                        ),
                        salario,
                    )
                )

        if not salarios_:
            raise ReferenciaSalarialNotFound(
                "Não existe salario para o cargo %s na(s) tabela(s) vigente(s) %s"
                % (cargo, [str(t) for t in tabelas])
            )

        return salarios_

    @classmethod
    def salarios_atualizados(
        cls, cargo, data_inicio=None, data_fim=None, referencia=None
    ):
        from rh.gfp.plugins.rh_models import ReferenciaSalarialNotFound

        salarios_ = []
        if data_inicio is None:
            data_inicio = datetime.today()

        if data_fim is None:
            data_fim = data_inicio
        range_ = NewDateRange(data_inicio, data_fim)
        tabelas = TabelaSalarial.tabelas_vigente(cargo)
        ces = CargosEstrutura.objects.filter(
            estrutura_salarial__in=[t.estrutura_salarial for t in tabelas], cargo=cargo
        ).order_by("data_vigencia_inicio")

        salarios_query = ReferenciaSalario.objects.filter(tabela_salarial__in=tabelas)
        if referencia:
            salarios_query = salarios_query.filter(referencia_nivel2d=referencia)
        for ce in ces:
            for salario in salarios_query.filter(
                referencia_nivel2d__in=ce.referencias.all()
            ):
                salarios_.append(
                    (
                        range_.intersect(
                            NewDateRange(ce.data_vigencia_inicio, ce.data_vigencia_fim)
                        ),
                        salario,
                    )
                )

        if not salarios_:
            raise ReferenciaSalarialNotFound(
                "Não existe salario para o cargo %s na(s) tabela(s) vigente(s) %s"
                % (cargo, [str(t) for t in tabelas])
            )

        return salarios_


# DEPRECATED CLASS


@deprecated
class CategoriaSalarial(models.Model):
    class Meta:
        db_table = "gfp_categoriasalarial"
        ordering = ["tipo", "titulo"]

    titulo = models.CharField(max_length=50, verbose_name="Nome")
    tipo = models.CharField(
        max_length=1,
        choices=(("H", "HORIZONTAL"), ("V", "VERTICAL")),
        verbose_name="Nível Salarial",
    )

    def __str__(self):
        return "%s - %s" % (self.titulo, self.tipo)


class ReferenciaSalarioQuerySet(models.QuerySet):
    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(tabela_salarial__data_vigencia_inicio__gt=range_.last)
                | (
                    ~Q(tabela_salarial__data_vigencia_fim=None)
                    & Q(tabela_salarial__data_vigencia_fim__lt=range_.first)
                )
            )
        else:
            return self.exclude(
                Q(tabela_salarial__data_vigencia_inicio__gt=data)
                | (
                    ~Q(tabela_salarial__data_vigencia_fim=None)
                    & Q(tabela_salarial__data_vigencia_fim__lt=data)
                )
            )


class ReferenciaSalario(AuditTimestampModel):
    class Meta:
        db_table = "gfp_referenciasalarial"
        unique_together = ("tabela_salarial", "referencia_nivel2d")
        ordering = (
            "tabela_salarial",
            "referencia_nivel2d__ordem",
        )

    class TabelaSalarialEmVigencia(Exception):
        pass

    AUDITABLE = {
        "exclude": [
            "dt_criacao",
            "dt_alteracao",
        ]
    }

    tabela_salarial = models.ForeignKey(
        "TabelaSalarial",
        verbose_name="Tabela Salarial",
        related_name="salarios",
        on_delete=models.CASCADE,
    )
    referencia_nivel2d = models.ForeignKey(
        "ReferenciaNiveis2D",
        on_delete=models.CASCADE,
        verbose_name="Referência Níveis",
        related_name="referencias_salarios",
        null=True,
    )
    valor = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Valor Servidor"
    )
    gratificacao = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Gratif. Servidor"
    )
    valor_membro = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Valor Membro"
    )
    gratificacao_membro = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Gratif. Membro"
    )
    sigla_cache = models.CharField(max_length=30, null=True, blank=True)

    # DEPRECATEDs fields -------------------
    dt_criacao = models.DateField(
        auto_now_add=True, editable=False, verbose_name="Data Criação"
    )
    dt_alteracao = models.DateField(
        auto_now=True, editable=False, verbose_name="Data Alteração"
    )

    objects = ReferenciaSalarioQuerySet.as_manager()

    def __str__(self):
        return self.sigla_cache

    def save(self, *args, **kargs):
        if (
            self.referencia_nivel2d
            not in self.tabela_salarial.estrutura_salarial.references.all()
        ):
            raise Exception(
                "A referência salarial %s não faz parte da estrutura da tabela salarial %s"
                % (self.referencia_nivel2d, self.tabela_salarial.estrutura_salarial)
            )

        self.sigla_cache = self.referencia_nivel2d.sigla_cache

        super(ReferenciaSalario, self).save(*args, **kargs)


class TabelaSalarial(ListDatedModel, AuditTimestampModel):
    class Meta:
        db_table = "gfp_tabelasalarialsalario"
        unique_together = (
            "estrutura_salarial",
            "info_adicional",
            "publicacao",
            "identifier",
        )
        ordering = ("estrutura_salarial", "-start_validity")

    AUDITABLE = {
        "fields": [
            "estrutura_salarial",
            "tabela_anterior",
            "start_validity",
            "end_validity",
        ]
    }
    OVERLAP_FIELDS = ["estrutura_salarial", "info_adicional", "identifier"]
    AUTO_CLOSE_PERIOD_OVERLAP = True
    ONLY_CONTINUOUS_PERIOD = True

    extraFields = [
        "percentual",
    ]

    estrutura_salarial = models.ForeignKey(
        "EstruturaTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Estrutura Salarial",
        related_name="tabelas_vigentes",
    )
    tabela_anterior = models.ForeignKey(
        "TabelaSalarial",
        verbose_name="Tabela Salarial",
        on_delete=models.SET_NULL,
        related_name="tabela_atualizada",
        null=True,
        blank=True,
    )
    info_adicional = models.CharField(max_length=30, null=False, blank=True, default="")
    identifier = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("gfp", "STRUCTURE_IDENTIFIER")
    )
    # data_vigencia_inicio = models.DateField(verbose_name='Início vigência', blank=True)
    # data_vigencia_fim = models.DateField(verbose_name='Fim vigência', blank=True, null=True)
    publicacao = models.ForeignKey(
        Publicacao,
        verbose_name="Publicação",
        related_name="tabelas_salariais",
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kargs):
        percentual = None
        if "percentual" in kargs:
            percentual = float(kargs["percentual"])
            del kargs["percentual"]

        super(TabelaSalarial, self).__init__(*args, **kargs)
        self.percentual = percentual

    def __str__(self):
        return "%s%s (%s)" % (
            self.estrutura_salarial,
            ("-%s" % self.info_adicional) if self.info_adicional else "",
            self.start_validity,
        )

    @transaction.atomic
    def save(self, *args, **kargs):

        percentual = (
            getattr(self, "percentual") if hasattr(self, "percentual") else 0.0
        ) or 0.0

        new = self.pk is None

        if not self.start_validity:
            self.start_validity = self.publicacao.data_vigencia

        super(TabelaSalarial, self).save(*args, **kargs)

        if new:
            for rns in self.estrutura_salarial.references.filter(ativo=True).order_by(
                "ordem"
            ):
                salario = {"valor": 0, "gratificacao": 0}
                if self.tabela_anterior:
                    try:
                        if rns.referencia_anterior and rns.fator_atualizacao:
                            base_ref = self.salarios.get(
                                referencia_nivel2d=rns.referencia_anterior
                            )
                            pct = float(rns.fator_atualizacao) / 100.0 + 1.0
                        else:
                            base_ref = self.tabela_anterior.salarios.get(
                                referencia_nivel2d=rns
                            )
                            pct = percentual / 100.0 + 1.0

                        if rns.tipo_valor == 1:  # MOEDA
                            salario = {
                                "valor": float(base_ref.valor) * pct,
                                "gratificacao": float(base_ref.gratificacao) * pct,
                            }
                        else:  # PERCENTUAL
                            salario = {
                                "valor": base_ref.valor,
                                "gratificacao": base_ref.gratificacao,
                            }

                    except ReferenciaSalario.DoesNotExist:
                        log.debug(
                            "%s não existe na tabela anterior (%s)!"
                            % (str(rns), self.tabela_anterior)
                        )
                    except Exception as e:
                        log.exception(e)
                        raise e

                obj, created = self.salarios.get_or_create(
                    tabela_salarial=self,
                    referencia_nivel2d=rns,
                    defaults={
                        "valor": salario["valor"],
                        "gratificacao": salario["gratificacao"],
                    },
                )

        if self.tabela_anterior:
            tsa = self.tabela_anterior
            tsa.end_validity = self.start_validity - relativedelta(days=1)
            tsa.save()
            # log.debug(('SETTING end_validity %s to %s' % (tsa, tsa.end_validity))

    @transaction.atomic
    def delete(self, *args, **kargs):
        super(TabelaSalarial, self).delete(*args, **kargs)

        if self.tabela_anterior:
            tsa = self.tabela_anterior
            tsa.end_validity = None
            tsa.save()

    @classmethod
    def tabelas_vigente(cls, cargo, data_inicio=None, data_fim=None):
        data_inicio = datetime.today() if not data_inicio else data_inicio
        if not data_fim:
            data_fim = data_inicio

        salary_structures = [
            cs.estrutura_salarial.pk
            for cs in CargosEstrutura.objects.filter(cargo=cargo).exclude(
                Q(data_vigencia_inicio__gt=data_fim)
                | (~Q(data_vigencia_fim=None) & Q(data_vigencia_fim__lt=data_inicio))
            )
        ]

        tabelas = (
            cls.objects.filter(estrutura_salarial__in=salary_structures)
            .exclude(
                Q(start_validity__gt=data_fim)
                | (~Q(end_validity=None) & Q(end_validity__lt=data_inicio))
            )
            .order_by("-start_validity")
        )

        if not tabelas:
            raise Cargo.TabelaSalarialNotFound(
                "Não existe tabela salarial vigente para o cargo %s!" % cargo
            )

        return tabelas.distinct()


class ModeloTabelaSalarial(AuditTimestampModel):
    class Meta:
        db_table = "gfp_modelotabelasalarial"

    AUDITABLE = {
        "fields": ["labels_horizontal", "labels_vertical", "formatacao"],
        "exclude": ["id", "abstract_fields"],
    }

    titulo = models.CharField(max_length=255)
    quantidade_horizontal = models.PositiveSmallIntegerField(
        verbose_name="Quantidade níveis horizontais", default=0, blank=True
    )
    quantidade_vertical = models.PositiveSmallIntegerField(
        verbose_name="Quantidade níveis verticais", default=0, blank=True
    )
    titulo_horizontal = models.CharField(max_length=100, default="REFERÊNCIA")
    titulo_vertical = models.CharField(max_length=100, default="CLASSE")
    labels_horizontal = models.CharField(max_length=100, default="")
    labels_vertical = models.CharField(max_length=100, default="", blank=True)
    formatacao = models.CharField(
        max_length=100, verbose_name="Formatação", blank=True, null=True
    )
    # configuracao = models.CharField(max_length=400, default='')

    class LevelsRepeatedNotAllowed(Exception):
        def __init__(self, tipo="H"):
            Exception.__init__(
                self,
                (
                    "Níveis %s repetidos não são permitidos!" % "horizontais"
                    if tipo == "H"
                    else "verticais"
                ),
            )

    class ChangeLevelsNotAllowed(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Alteração na ordem ou dimunuição dos níveis horizontais e verticais não são permitidos!",
            )

    def __str__(self):
        return self.titulo

    def save(self, *args, **kargs):
        # TODO Possibilitar que o modelo possa ser alterado de forma que as referencias ja existententes
        # não sejam alteradas. A possibilidade seria de crescimento da tabela, seja na horizontal ou vertical

        new = (not self.pk or False) and True

        if not self.formatacao:
            self.formatacao = "{VERTICAL}{HORIZONTAL}"

        horizontais = self.labels_horizontal.split("|")
        verticais = self.labels_vertical.split("|")

        if len(horizontais) != len(set(horizontais)):
            raise self.LevelsRepeatedNotAllowed("H")
        if len(verticais) != len(set(verticais)):
            raise self.LevelsRepeatedNotAllowed("V")

        self.quantidade_horizontal = len(horizontais)
        self.quantidade_vertical = len(verticais)

        if (
            "labels_vertical" in self.old_fields
            and not self.labels_vertical.startswith(self.old_fields["labels_vertical"])
        ):
            raise self.ChangeLevelsNotAllowed()
        if (
            "labels_horizontal" in self.old_fields
            and not self.labels_horizontal.startswith(
                self.old_fields["labels_horizontal"]
            )
        ):
            raise self.ChangeLevelsNotAllowed()

        if not self.titulo:
            self.titulo = "Modelo"
        if not self.titulo.endswith(
            "(%s X %s)" % (self.quantidade_vertical, self.quantidade_horizontal)
        ):
            self.titulo += " (%s X %s)" % (
                self.quantidade_vertical,
                self.quantidade_horizontal,
            )

        super(ModeloTabelaSalarial, self).save(*args, **kargs)

        if (
            new
            or "labels_vertical" in self.old_fields
            or "labels_horizontal" in self.old_fields
        ):
            # Criando as referencias iniciais do Modelo e ordenando de acordo com os niveis (verticais X horizontais)
            ordem = 1
            for v in verticais:
                for h in horizontais:
                    rn2d, created = self.referencias.get_or_create(
                        horizontal=h, vertical=v, ordem=ordem
                    )
                    ordem += 1

        #  Updataing sigla_cache for all referencia_nivel2d of this modelo_tabela
        if "formatacao" in self.old_fields:
            for rn in self.referencias.all():
                rn.sigla_cache = self.formatacao.format(
                    VERTICAL=rn.vertical or "", HORIZONTAL=rn.horizontal or ""
                )
                rn.save()


@to_search(
    [
        {"name": "horizontal", "type": "text"},
        {"name": "vertical", "type": "text"},
        {"name": "sigla_cache", "type": "text"},
    ]
)
class ReferenciaNiveis2D(models.Model):
    class Meta:
        db_table = "gfp_referencianiveis2d"
        unique_together = (("estrutura_salarial", "horizontal", "vertical"),)
        ordering = ("estrutura_salarial", "ordem")

    class ReferenciaSalarioAlreadyPopulated(Exception):
        pass

    class ReferenciaSalarioNotExist(Exception):
        pass

    class TabelaSalarioNotExist(Exception):
        pass

    class LabelNotExistInModel(Exception):
        def __init__(self, label, tipo):
            Exception.__init__(
                self,
                'O label "%s" não existe na lista de labels %s do modelo!'
                % (label, "verticais" if tipo == "V" else "horizontais"),
            )

    estrutura_salarial = models.ForeignKey(
        "EstruturaTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Estrutura Salarial",
        related_name="references",
        null=True,
        blank=True,
    )
    modelo_tabela = models.ForeignKey(
        "ModeloTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Modelo",
        related_name="referencias",
        null=True,
        blank=True,
    )
    horizontal = models.CharField(
        max_length=6, verbose_name="Valor", null=True, blank=True
    )
    vertical = models.CharField(
        max_length=6, verbose_name="Valor", null=True, blank=True
    )
    sigla_cache = models.CharField(max_length=30, null=True, blank=True)
    ordem = models.SmallIntegerField(verbose_name="Ordem", default=0)
    tipo_valor = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_VALUE"),
        verbose_name="Valor Servidor",
        default=1,
    )
    tipo_gratificacao = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_VALUE"),
        verbose_name="Gratif. Servidor",
        default=1,
    )
    tipo_valor_membro = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_VALUE"),
        verbose_name="Valor Membro",
        default=1,
    )
    tipo_gratificacao_membro = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_VALUE"),
        verbose_name="Gratif. Membro",
        default=1,
    )
    referencia_anterior = models.ForeignKey(
        "ReferenciaNiveis2D",
        on_delete=models.CASCADE,
        verbose_name="Referência anterior",
        null=True,
        blank=True,
    )
    fator_atualizacao = models.DecimalField(
        verbose_name="Fator de atualização",
        max_digits=16,
        decimal_places=6,
        null=True,
        blank=True,
    )
    months_progression = models.PositiveSmallIntegerField(
        verbose_name="Progressões", default=12, blank=True
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.sigla_cache

    def save(self, *args, **kargs):
        if not self.sigla_cache:
            self.sigla_cache = "%s%s" % (self.vertical, self.horizontal)
        if (
            self.horizontal
            and self.horizontal
            not in self.estrutura_salarial.horizontal_labels.split("|")
        ):
            raise self.LabelNotExistInModel(self.horizontal, "H")
        if (
            self.vertical
            and self.vertical not in self.estrutura_salarial.vertical_labels.split("|")
        ):
            raise self.LabelNotExistInModel(self.vertical, "V")
        super(ReferenciaNiveis2D, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        if self.referencias_salarios.all().count() > 0:
            raise self.ReferenciaSalarioAlreadyPopulated(
                "Existem salários nas tabelas salariais com a referencia %s" % self
            )
        super(ReferenciaNiveis2D, self).delete(*args, **kargs)

    @staticmethod
    def get_by_cargo(cargo, data=None):
        data = datetime.now().date() if not data else data
        # refs = cargo.referencias_salariais.order_by('-estrutura_salarial__publicacao__data_vigencia_inicio', 'ordem')
        refs = (
            ReferenciaNiveis2D.objects.filter(cargos_estrutura__cargo=cargo)
            .exclude(
                Q(cargos_estrutura__data_vigencia_inicio__gt=data)
                | (
                    ~Q(cargos_estrutura__data_vigencia_fim=None)
                    & Q(cargos_estrutura__data_vigencia_fim__lt=data)
                )
            )
            .distinct()
            .order_by("-estrutura_salarial__data_vigencia_inicio", "ordem")
        )

        if not refs:
            raise ReferenciaNiveis2D.ReferenciaSalarioNotExist(
                "Não existe Referência Salarial vigente em %s para o cargo %s"
                % (data.strftime("%d/%m/%Y"), cargo)
            )
        return refs[0]

    @staticmethod
    def get_by_posse(posse, data=None):
        data = datetime.now().date() if not data else data
        progs = (
            posse.progressoes.exclude(data_inicio_vigencia__gt=data).order_by(
                "-data_inicio_vigencia"
            )
            if posse.quadro.cargo.tipo_lei_cargo in ["EF", "AC"]
            else None
        )
        return (
            ReferenciaNiveis2D.get_by_cargo(posse.quadro.cargo, data)
            if not progs
            else progs[0].referencia_nivel2d
        )


class CargosEstrutura(models.Model):
    class Meta:
        db_table = "gfp_cargosestrutura"
        unique_together = ("estrutura_salarial", "cargo", "data_vigencia_inicio")

    estrutura_salarial = models.ForeignKey(
        "EstruturaTabelaSalarial",
        on_delete=models.CASCADE,
        verbose_name="Estrutura Salarial",
        related_name="cargos_estrutura",
    )
    cargo = models.ForeignKey(
        "rh.Cargo",
        verbose_name="Cargo",
        related_name="cargos_estrutura",
        on_delete=models.CASCADE,
    )
    data_vigencia_inicio = models.DateField(verbose_name="Início vigência", blank=True)
    data_vigencia_fim = models.DateField(
        verbose_name="Fim vigência", blank=True, null=True
    )
    referencias = models.ManyToManyField(
        "ReferenciaNiveis2D", related_name="cargos_estrutura"
    )
    publicacao = models.ForeignKey(
        Publicacao,
        verbose_name="Publicação",
        related_name="cargos_estrutura",
        on_delete=models.CASCADE,
    )


class ContraChequeQuerySet(models.QuerySet):

    def by_month_year(self, month, year):
        return self.filter(folha__periodo__mes=month, folha__periodo__ano=year)

    def consolidate(self):
        result = []
        for cc in self:
            result.append(cc.consolidate(save=True, force=True))
        return result


class ContraCheque(AuditTimestampModel):
    class Meta:
        db_table = "gfp_contracheque"
        unique_together = (("servidor", "folha", "pensioner", "benefit_number"),)
        ordering = ("folha", "servidor", "-pensioner", "benefit_number")

    VALIDATIONS = {
        1: "Contracheque sem dado bancário",
        2: "Partilha ou pensão devida e não realizada",
        4: "Partilha não zerada",
        8: "Contracheque negativo",
        16: "Contracheque não consolidado",
    }

    AUDITABLE = {
        "fields": [
            "dado_bancario_pessoa_id",
            "margem_consignada_livre",
            "lotacao_id",
            "situacao_funcional",
            "blocked",
            "margem_consignada_total",
            "situacao_previdenciaria",
            "cargo_efetivo_id",
            "referencia_salario_efetivo_id",
            "cargo_comissao_id",
            "referencia_salario_comissao_id",
            "cargo_eletivo_id",
            "referencia_salario_eletivo_id",
            "classification",
            "dependentes_ir",
            "dependentes_sf",
            "total_bruto",
            "total_liquido",
            "employee_source",
            "employee_pays_pension",
            "error_validations",
            "benefit_number",
        ],
        "exclude": ["id", "abstract_fields", "changed"],
    }

    objects = ContraChequeQuerySet.as_manager()

    servidor = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.PROTECT,
        verbose_name="Servidor",
        related_name="paychecks",
    )
    folha = models.ForeignKey(
        Folha, on_delete=models.PROTECT, verbose_name="Folha", related_name="paychecks"
    )
    pensioner = models.ForeignKey(
        "rh.PessoaFisica",
        on_delete=models.PROTECT,
        verbose_name="Pensionista",
        related_name="pension_paychecks",
        null=True,
        blank=True,
    )
    benefit_number = models.CharField(
        max_length=20, default="", blank=True, db_index=True
    )

    situacao_funcional = models.CharField(max_length=250, null=True, blank=True)
    situacao_previdenciaria = models.CharField(max_length=250, null=True, blank=True)
    cargo_efetivo = models.ForeignKey(
        "rh.Cargo",
        on_delete=models.PROTECT,
        related_name="contra_cheques_cargo_efetivo",
        null=True,
        blank=True,
    )
    referencia_efetivo_cache = models.CharField(max_length=100, default="", blank=True)
    referencia_salarial_efetivo = models.ForeignKey(
        ReferenciaNiveis2D,
        on_delete=models.PROTECT,
        related_name="contracheques_efetivo",
        null=True,
        blank=True,
    )
    referencia_salario_efetivo = models.ForeignKey(
        ReferenciaSalario,
        on_delete=models.PROTECT,
        related_name="contracheques_efetivo",
        null=True,
        blank=True,
    )
    cargo_comissao = models.ForeignKey(
        "rh.Cargo",
        on_delete=models.PROTECT,
        related_name="contra_cheques_cargo_comissao",
        null=True,
        blank=True,
    )
    referencia_comissao_cache = models.CharField(max_length=100, default="", blank=True)
    referencia_salarial_comissao = models.ForeignKey(
        ReferenciaNiveis2D,
        on_delete=models.PROTECT,
        related_name="contracheques_comissao",
        null=True,
        blank=True,
    )
    referencia_salario_comissao = models.ForeignKey(
        ReferenciaSalario,
        on_delete=models.PROTECT,
        related_name="contracheques_comissao",
        null=True,
        blank=True,
    )
    cargo_eletivo = models.ForeignKey(
        "rh.Cargo",
        on_delete=models.PROTECT,
        related_name="contra_cheques_cargo_eletivo",
        null=True,
        blank=True,
    )
    referencia_eletivo_cache = models.CharField(max_length=100, default="", blank=True)
    referencia_salarial_eletivo = models.ForeignKey(
        ReferenciaNiveis2D,
        on_delete=models.PROTECT,
        related_name="contracheques_eletivo",
        null=True,
        blank=True,
    )
    referencia_salario_eletivo = models.ForeignKey(
        ReferenciaSalario,
        on_delete=models.PROTECT,
        related_name="contracheques_eletivo",
        null=True,
        blank=True,
    )
    data_admissao = models.DateField(
        verbose_name="Data Admissão", null=True, blank=True
    )
    lotacao = models.ForeignKey(
        "rh.Lotacao",
        on_delete=models.PROTECT,
        verbose_name="Lotação",
        related_name="+",
        null=True,
        blank=True,
    )
    dependentes_ir = models.SmallIntegerField(
        verbose_name="Dep. IR", default=0, blank=True
    )
    dependentes_sf = models.SmallIntegerField(
        verbose_name="Dep. SF", default=0, blank=True
    )
    margem_consignada_total = models.DecimalField(
        verbose_name="Margem Total", max_digits=16, decimal_places=2, default=0
    )
    margem_consignada_livre = models.DecimalField(
        verbose_name="Margem Livre", max_digits=16, decimal_places=2, default=0
    )
    base_previdenciaria = models.DecimalField(
        verbose_name="Base Previdência", max_digits=16, decimal_places=2, default=0
    )
    base_ir = models.DecimalField(
        verbose_name="Base IR", max_digits=16, decimal_places=2, default=0
    )
    dado_bancario_pessoa = models.ForeignKey(
        "rh.DadoBancarioPessoa",
        on_delete=models.PROTECT,
        verbose_name="Dado Bancário",
        related_name="contracheques",
        null=True,
        blank=True,
    )
    total_bruto = models.DecimalField(
        verbose_name="Total bruto", max_digits=16, decimal_places=2, default=0
    )
    total_liquido = models.DecimalField(
        verbose_name="Total líquido", max_digits=16, decimal_places=2, default=0
    )
    alterado = models.BooleanField(verbose_name="Alterado", default=False, blank=True)
    status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "STATUS_PAYCHECK"),
        verbose_name="Status",
        default=1,
        blank=True,
    )
    blocked = models.BooleanField(verbose_name="Bloqueado", default=False, blank=True)
    employee_source = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "EMPLOYEE_SOURCE_PAYCHECK"),
        verbose_name="Tipo de servidor",
        default=1,
    )
    employee_pays_pension = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "EMPLOYEE_PAYS_PENSION"),
        verbose_name="Pensão",
        default=0,
    )
    classification = models.PositiveIntegerField(
        choices=Choice.get_choices_for("gfp", "CLASSIFICATION_EMPLOYEE"),
        verbose_name="Classificação",
        default=1,
    )
    error_validations = models.PositiveIntegerField(
        verbose_name="Erro de validações", default=0, blank=True
    )
    changes = models.PositiveIntegerField(default=0, blank=True)

    NOCHANGES = 0
    EVENTS = 1
    JOB = 2
    BANKDATA = 4
    FUNCTIONAL = 8
    DEPENDENTS = 16
    WORKPLACE = 32
    MARGINS = 64
    ALL = 8191  # WARN: This option should be the sum of all other

    class DuplicateFolhaEvento(Exception):
        pass

    class DoesNotChangeClosedFolha(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "A folha (%s) já se encontra fechada e por isso não pode ser alterada!"
                % self.folha,
            )

    class PensionerIvalid(Exception):
        def __init__(self):
            Exception.__init__(
                self, "O pensionista não possui vínculo para o servidor!"
            )

    def __str__(self):
        return "%s : %s%s" % (
            self.folha,
            self.servidor,
            "(%s)" % str(self.pensioner) if self.pensioner else "",
        )

    def save(self, group_cache=None, **kargs):
        # log.debug(('>>>>>>>>> SAVING PAYCHECK...')

        if not self.pk:
            pensioners = [p.pensionista for p in self._pensions_of_employee()]
            if self.pensioner and self.pensioner not in pensioners:
                raise self.PensionerIvalid()

        if self.servidor.type_by_possession in rh_const.TYPE_BY_POSSESSION_BENEFICIARY:
            benefits = BenefitMovement.objects.filter(
                servidor=self.servidor, benefit_role__isnull=False, ativo=True
            ).values_list("benefit_number", flat=True)

            if len(benefits) == 1 and not self.benefit_number:
                self.benefit_number = benefits[0]
            if benefits:
                if self.benefit_number not in benefits:
                    raise Exception(
                        "Número de um benefício válido do beneficiaário é obrigatório!"
                    )
        elif self.benefit_number:
            raise Exception(
                "Benefício só deve ser informado para servidores beneficiários!"
            )

        super(ContraCheque, self).save(**kargs)

    def delete(self, **kargs):
        if self.lancamentos.count() and self.folha.is_processed:
            raise Folha.ClosedFolha

        for fe in self.lancamentos.all():
            fe.delete(recalculate=False)

        super(ContraCheque, self).delete(**kargs)

    def _distributing_death_benefits_events(self, current_pension, pensions, task=None):
        # log.info('>>>>>>>>> * DISTRIBUTION PENSION *: %s' % (self.servidor))

        objs = {
            "changed": False,
            "added": [],
            "deleteds": [],
            "updateds": [],
            "erros": [],
        }

        if current_pension.type_of_pension == 2 and self.pensioner:
            principal_pension = pensions.order_by(
                "-pensionista__data_nascimento", "pk"
            ).first()

            # log.info('RECALCULATE FOR PENSION %s CP %s PP %s' % (self, current_pension.pk, principal_pension.pk))

            try:
                paycheck_employee = self.folha.paychecks.get(
                    servidor=self.servidor, pensioner=None
                )
                for fe in paycheck_employee.lancamentos.exclude(
                    evento__genre_event__character__in=[6, 7]
                ).exclude(
                    evento__in=[
                        current_pension.event_employee,
                        current_pension.event_employee_13,
                    ]
                ):
                    # log.info('PARTITION FOR %s' % fe)
                    created = False

                    pensioner_entry = self.lancamentos.filter(
                        evento=fe.evento,
                        info=fe.info,
                        reference_month=fe.reference_month,
                        reference_year=fe.reference_year,
                    ).first()

                    if not pensioner_entry:
                        pensioner_entry = copy.copy(fe)
                        pensioner_entry.pk = None
                        pensioner_entry.contracheque = self
                        created = True

                    value = round(float(fe.valor * current_pension.valor) / 100.0, 2)
                    total_value = 0.0
                    if current_pension == principal_pension:
                        for p in pensions:
                            total_value += round(float(fe.valor * p.valor) / 100.0, 2)
                        # log.info('RECALCULATE FOR PENSION %s FEV %s PV %s DIFF %s' % (
                        #     self, fe.valor, total_value, round(float(fe.valor) - total_value, 2)))
                        value += round(float(fe.valor) - total_value, 2)

                    pensioner_entry.valor = value
                    pensioner_entry.patronal = round(
                        float(fe.patronal * current_pension.valor) / 100.0, 2
                    )
                    pensioner_entry.valor_base = fe.valor_base
                    pensioner_entry.pct = (
                        current_pension.valor
                        if not pensioner_entry.pct
                        else pensioner_entry.pct
                    )
                    pensioner_entry.automated = False
                    pensioner_entry.insertion_type = (
                        2  # Choice id 2 - Tipo de Inserção: Manual
                    )
                    pensioner_entry.entry_pension = fe
                    pensioner_entry.save()

                    if not created and pensioner_entry.is_dirty:
                        fup = {"pk": pensioner_entry.pk}
                        for key in pensioner_entry.old_fields:
                            fup.update(
                                {
                                    key: {
                                        "old": pensioner_entry.old_fields[key],
                                        "new": getattr(fe, key),
                                    }
                                }
                            )
                        pensioner_entry.save()

                        if task and pensioner_entry.has_pendencies:
                            task.info(
                                "LANÇAMENTO MODIFICADO: %s - %s!"
                                % (pensioner_entry.evento, pensioner_entry.servidor),
                                1,
                            )
                        objs["updateds"].append(fup)
                        objs["changed"] = True

                    elif created:
                        # log.debug('DO SAVING FOLHAEVENTO %s _distributing_death_benefits_events',
                        #           pensioner_entry.servidor.matricula)
                        pensioner_entry.save()
                        if task and pensioner_entry.has_pendencies:
                            task.info(
                                "LANÇAMENTO CRIADO: %s - %s!"
                                % (pensioner_entry.evento, pensioner_entry.servidor),
                                1,
                            )
                        objs["added"].append(pensioner_entry)
                        objs["changed"] = True
            except ContraCheque.DoesNotExist as e:
                raise e
            except Exception as e:
                raise e
            else:
                pass

        return objs

    def _recalculate(self, ids=[], task=None, group_cache=None, model=None):

        # log.info('>>>>>>>>> RECALCULATE (PENSION): %s GCACHEK: %s' % (self.servidor, group_cache))

        objs = {
            "changed": False,
            "added": [],
            "deleteds": [],
            "updateds": [],
            "erros": [],
        }

        if self.folha.is_processed:
            return objs

        only_events = []
        exclude_events = []
        pensions = []
        pensions = self.servidor.pensao_pagador.filter(
            type_of_pension__in=[1, 2]
        ).exclude(
            Q(data_inicio__gt=self.folha.date_range.last)
            | (~Q(data_fim=None) & Q(data_fim__lt=self.folha.date_range.first))
        )
        # log.info('>>>>>>>>> *RECALCULATE* %s PENSIONS: %s ' % (self, pensions.count()))
        if pensions:
            if self.pensioner:
                current_pension = (
                    pensions.filter(pensionista=self.pensioner)
                    .order_by("data_inicio")
                    .first()
                )

                if current_pension.type_of_pension == 1:
                    only_events = [
                        current_pension.event_pensioner.numero,
                    ]
                elif current_pension.type_of_pension == 2:
                    # log.info('RECALCULATE FOR PENSION %s' % (self))
                    exclude_events = [ev.numero for ev in current_pension.events.all()]

                    objs = self._distributing_death_benefits_events(
                        current_pension, pensions, task=task
                    )

            #     exclude_events = [p.event_employee.numero for p in pensions]

        if self.folha.tipo_folha.modelo and self.folha.apply_models:
            # log.debug('>>>>>>>>>>>>>>> APPLYMODEL %s EE: %s OE: %s' % (
            #     self.folha.tipo_folha.modelo, exclude_events, only_events))
            added = self.apply_model(
                self.folha.tipo_folha.modelo,
                recalculate=False,
                task=task,
                group_cache=group_cache,
                only_events=only_events,
                exclude_events=exclude_events,
            )
            # log.debug('<<<<<<<<<<<<<<< APPLYMODEL')
            objs["added"] = added
            # objs['changed'] = (added and True) or False

        if model and model != self.folha.tipo_folha.modelo:
            # log.debug('>>>>>>>>>>>>>>> APPLYMODEL %s EE: %s OE: %s' % (model, exclude_events, only_events))
            added = self.apply_model(
                model,
                recalculate=False,
                task=task,
                group_cache=group_cache,
                only_events=only_events,
                exclude_events=exclude_events,
                force=True,
            )
            # log.debug('<<<<<<<<<<<<<<< APPLYMODEL')
            objs["added"] += added
            # objs['changed'] = (added and True) or objs['changed']

        current_configs = (
            ConfigEvent.objects.current_in(
                self.folha.date_range.first, self.folha.date_range.last
            )
            .filter(automated=True, calculation__isnull=False)
            .values_list("pk")
        )
        query = self.lancamentos.filter(
            Q(automated=True)
            & (
                Q(evento__configs__in=current_configs)
                | Q(paycheck_difference__isnull=False, calculation__isnull=False)
            )
        ).order_by("evento__numero")

        if ids:
            query = query.filter(id__in=ids)

        for fe in query:
            calc = None
            params = {
                "pct": fe.pct,
                "qnt": fe.qnt,
                "info": fe.info,
                "patronal": fe.patronal,
                "valor_base": fe.valor_base,
                "parcela": fe.parcela,
            }

            params.update(fe.vars)

            if fe.evento.numero in ["13502", "12302"]:
                calc = fe.instance_calc(qnt=params["qnt"])
            else:
                calc = fe.instance_calc(group_cache=group_cache)

            rcalc = calc.calculate()

            if rcalc.get("valor", 0) == 0 and len(rcalc["choices"]) > 1:
                params["oIds"] = [x[0] for x in rcalc["choices"] if x[0] == fe.oIds[0]]
                classcode = fe.evento.calculation_at(self.folha.date_range.first)
                cls = classcode.cls
                calc = cls(self.servidor, self.folha, fe.evento, params=params)
                rcalc = calc.calculate()

            if (
                (rcalc.get("valor", 0) <= 0 and rcalc.get("patronal", 0) <= 0)
                and not (
                    self.folha.is_processed
                    or fe.difference_items.exclude(
                        difference__entries_payment=None
                    ).exists()
                )
                or (params.get("info") != rcalc.get("info"))
            ):
                formatted_desc = "\n\rID: {} CID: {} INFO: {}".format(
                    fe.id, fe.cid, fe.info
                )
                fe.delete(recalculate=False)
                objs["deleteds"].append(str(fe))
                objs["changed"] = True
                if task:
                    task.info(
                        "LANÇAMENTO zerado ou negativo REMOVIDO: %s - %s!%s"
                        % (fe.evento, fe.servidor, formatted_desc),
                        2,
                    )
            else:
                fe.valor = fe.correct_valor = rcalc.get("valor", 0.0)
                fe.qnt = fe.correct_qnt = rcalc.get("qnt", 0.0)
                fe.qnt_max = fe.correct_qnt_max = rcalc.get("qnt_max", 0.0)
                fe.pct = fe.correct_pct = rcalc.get("pct", None)
                fe.prazo = rcalc.get("prazo", 0)
                fe.info = rcalc.get("info", "")
                fe.valor_base = fe.correct_base_value = rcalc.get("valor_base", 0.0)
                fe.patronal = fe.correct_patronal = rcalc.get("patronal", 0.0)
                fe.base_previdencia = fe.correct_base_previdencia = rcalc.get(
                    "base_previdencia", 0.0
                )
                fe.reference_year, fe.reference_month = rcalc.get(
                    "references", (None, None)
                )
                fe.oIds = rcalc.get("oIds", [])
                fe.vars = rcalc.get("vars", {})

                if fe.is_dirty:
                    fup = {"pk": fe.pk}.update(fe.diff)
                    # for key in fe.old_fields:
                    #     fup.update({
                    #         key: {"old": fe.old_fields[key], "new": getattr(fe, key)}
                    #     })

                    # log.debug('AA DO SAVING FOLHAEVENTO %s _recalculate: %s' % (fe.servidor.matricula, self.diff))
                    fe.save()

                    if task and fe.has_pendencies:
                        # log.debug('> LANÇAMENTO MODIFICADO:(%s) [%s] %s - %s!' % (
                        #     fe.has_pendencies, fe.old_fields, fe.evento, fe.servidor))
                        task.info(
                            "LANÇAMENTO MODIFICADO: %s - %s!"
                            % (fe.evento, fe.servidor),
                            1,
                        )
                    objs["updateds"].append(fup)
                    # objs['changed'] = True

                if "callback" in rcalc:
                    rcalc["callback"](entry=fe)

        if not self.pensioner:
            # RECALCULATING PAYCHECKS OF BENEFITS
            for pension in pensions:
                paycheck, created = self.folha.paychecks.get_or_create(
                    servidor=self.servidor, pensioner=pension.pensionista
                )
                # log.debug('%s AAA RECALCULATING PAYCHECKP %s: %s' % (paycheck.lancamentos.count(), paycheck, res))
                res = paycheck.recalculate(consolidate=self.ALL)
                # log.debug('%s AAA RECALCULATING PAYCHECKP %s: %s' % (paycheck.lancamentos.count(), paycheck, res))
                if paycheck.lancamentos.count() == 0:
                    paycheck.delete()
                if res["changed"] or created:
                    objs["changed"] = True
            pensioners = [p.pensionista for p in pensions]
            for paycheckp in (
                self.folha.paychecks.filter(
                    servidor=self.servidor, benefit_number=self.benefit_number
                )
                .exclude(pk=self.pk)
                .exclude(pensioner__in=pensioners)
            ):
                paycheckp.delete()
                # log.debug(
                #     'APAGANDO CONTRACHEQUE de pensionista/partilha (%s) por não possuir pensão ativa!' % (self))
                if task:
                    task.info(
                        "APAGANDO CONTRACHEQUE de pensionista/partilha (%s) por não possuir pensão ativa!"
                        % (self),
                        2,
                    )

        objs["changed"] = (
            (objs["added"] or objs["deleteds"] or objs["updateds"]) and True
        ) or False

        return objs

    def set_changes(self, value):
        self.changes |= value

    def unset_changes(self, value):
        self.changes ^= self.changes & value

    def clear_changes(self):
        self.changes = 0

    def consolidate(
        self, changes=0, save=True, force=False, task=None, group_cache=None
    ):
        """
        Teste de DOCSTRING.

        Teste
        """

        if not changes:
            changes = self.changes
        # log.debug((changes)
        if changes or force:
            if not force and self.folha.is_processed and self.pk:
                return {}

            # log.debug((">>> CONSOLIDATE %s - %s" % (self.folha, self.servidor))

            if (changes & self.JOB) or force:
                # log.debug((">>> CONSOLIDATE CARGOS...")
                cargos = self._get_cargos_referencia()
                if "ES" in cargos:
                    self.cargo_efetivo, self.referencia_salario_efetivo = cargos["ES"]
                if "AC" in cargos:
                    self.cargo_efetivo, self.referencia_salario_efetivo = cargos["AC"]
                if "EF" in cargos:
                    self.cargo_efetivo, self.referencia_salario_efetivo = cargos["EF"]
                if "CM" in cargos:
                    self.cargo_comissao, self.referencia_salario_comissao = cargos["CM"]
                if "EL" in cargos:
                    self.cargo_eletivo, self.referencia_salario_eletivo = cargos["EL"]
                if "FC" in cargos:
                    self.cargo_comissao, self.referencia_salario_comissao = cargos["FC"]
                self.referencia_salarial_efetivo = (
                    self.referencia_salario_efetivo.referencia_nivel2d
                    if self.referencia_salario_efetivo
                    else None
                )
                self.referencia_salarial_comissao = (
                    self.referencia_salario_comissao.referencia_nivel2d
                    if self.referencia_salario_comissao
                    else None
                )
                self.referencia_salarial_eletivo = (
                    self.referencia_salario_eletivo.referencia_nivel2d
                    if self.referencia_salario_eletivo
                    else None
                )

                if not ("ES" in cargos or "AC" in cargos or "EF" in cargos):
                    self.cargo_efetivo, self.referencia_salario_efetivo = None, None
                if not ("CM" in cargos or "FC" in cargos):
                    self.cargo_comissao, self.referencia_salario_comissao = None, None
                if not ("EL" in cargos):
                    self.cargo_eletivo, self.referencia_salario_eletivo = None, None

                self.classification = self._get_classification()

                self.unset_changes(self.JOB)

            if (changes & self.EVENTS) or force:
                # log.debug((">>> CONSOLIDATE EVENTOS...")
                self.base_previdenciaria = 0
                self.base_ir = 0
                self.total_bruto = self._get_total_bruto()
                self.total_liquido = self._get_total_liquido()
                self.dependentes_ir = self._get_dependentes_irrf()
                self.dependentes_sf = self._get_dependentes_salario_familia()

                self.unset_changes(self.EVENTS)

            if (changes & self.MARGINS) or force:
                # log.debug((">>> CONSOLIDATE MARGINS...")
                self._update_or_create_margins()

                self.unset_changes(self.MARGINS)

            if (changes & self.DEPENDENTS) or force:
                # log.debug((">>> CONSOLIDATE DEPENDENTS...")
                self.dependentes_ir = self._get_dependentes_irrf()
                self.dependentes_sf = self._get_dependentes_salario_familia()

                self.unset_changes(self.DEPENDENTS)

            if (changes & self.BANKDATA) or force:
                # log.debug((">>> CONSOLIDATE BANKDATA 1... %s >> %s %s" % (
                #     self.dado_bancario_pessoa, self._get_dado_bancario(), self.diff))
                self.dado_bancario_pessoa = self._get_dado_bancario()
                # log.debug((">>> CONSOLIDATE BANKDATA 2... %s %s" % (self.dado_bancario_pessoa, self.diff))

                self.unset_changes(self.BANKDATA)
                # log.debug((">>> CONSOLIDATE BANKDATA 3... %s %s" % (self.dado_bancario_pessoa, self.diff))

            if (changes & self.FUNCTIONAL) or force:
                # log.debug((">>> CONSOLIDATE FUNCTIONAL...")
                self.situacao_funcional = self._get_situacao_funcional()
                self.situacao_previdenciaria = self._get_situacao_previdenciaria()
                self.employee_source = self._get_employee_source()
                self.employee_pays_pension = self._get_pays_pension()
                # self.classification = self._get_classification()

                self.unset_changes(self.FUNCTIONAL)

            if (changes & self.WORKPLACE) or force:
                # log.debug((">>> CONSOLIDATE WORKPLACE...")
                self.lotacao = self._get_lotacao()

                self.unset_changes(self.WORKPLACE)

            self.error_validations = self._get_error_validations()

            self.alterado = False

            diff = self.old_fields
            # log.debug(('CONSOLIDATE DIFF: %s' % diff)

            if save and (self.old_fields or force):
                # log.debug(('SAVE PAYCHECK *************************************')
                self.save()

            return diff
        else:
            return {}

    def recalculate(
        self, ids=[], consolidate=0, task=None, group_cache=None, model=None
    ):
        group_key_cache = group_cache if group_cache else make_group_key()

        # log.info('>>>>>>>>> RECALCULATE: %s GCACHEK: %s' % (self.servidor, group_key_cache))

        result = {}
        objs = {
            "changed": False,
            "added": [],
            "deleteds": [],
            "updateds": [],
            "erros": [],
        }

        loop_control = 5
        changed = True
        while changed and loop_control > 0:
            result = self._recalculate(
                ids, task=task, group_cache=group_key_cache, model=model
            )
            # log.info('AA (%s) RECALCULATE RESULT %s: %s' % (loop_control, self, result))
            changed = result["changed"]
            objs["changed"] |= result.get("changed")
            objs["added"] += result.get("added", [])
            objs["deleteds"] += result.get("deleteds", [])
            objs["updateds"] += result.get("updateds", [])
            objs["erros"] += result.get("erros", [])
            loop_control -= 1

        if loop_control <= 0:
            log.info(f">>WARNING<< LOOP CONTROL FOR {self}")
        # if changed:
        #     log.info(f'>>WARNING<< LOOP CONTROL CHANGED:  {objs}')

        self.consolidate(changes=consolidate, group_cache=group_key_cache)

        if not group_cache:
            delete_cache(group_key_cache)

        return objs

    def evaluate_differences(
        self, ids=[], task=None, group_cache=None, number_events=[]
    ):
        group_key_cache = group_cache if group_cache else make_group_key()

        # log.info('>>>>>>>>> EVALUATE DIFF: %s GCACHEK: %s' % (self.servidor, group_key_cache))
        # log.debug(ids)
        result = {}
        objs = {
            "changed": False,
            "added": [],
            "deleteds": [],
            "updateds": [],
            "erros": [],
        }

        loop_control = 5
        changed = True
        while changed and loop_control:
            result = self._evaluate_differences(
                ids, task, group_key_cache, number_events
            )
            # log.info('AA (%s) EVALUATE DIFF RESULT %s' % (loop_control, self))
            changed = result["changed"]
            objs["changed"] |= result.get("changed")
            objs["added"] += result.get("added", [])
            objs["deleteds"] += result.get("deleteds", [])
            objs["updateds"] += result.get("updateds", [])
            objs["erros"] += result.get("erros", [])
            loop_control -= 1

        if not loop_control:
            log.info(">>WARNING<< LOOP CONTROL FOR %s" % self)

        # self.consolidate(changes=consolidate, group_cache=group_key_cache)

        if not group_cache:
            delete_cache(group_key_cache)

        return objs

    def _evaluate_differences(
        self, ids=[], task=None, group_cache=None, number_events=[], can_delete=True
    ):
        group_key_cache = group_cache if group_cache else make_group_key()

        # log.info('>>>>>>>>> EVALUATE DIFFERENCES: %s EVENTS: %s' % (self, number_events))
        if not (self.folha.is_processed or self.folha.is_closed):
            raise Folha.OpenedPayroll()
        objs = {"changed": False, "added": [], "updateds": [], "erros": []}

        if self.folha.tipo_folha.modelo:

            # log.debug('>>>>>>>>>>>>>>> APPLYMODEL %s' % self.folha.tipo_folha.modelo)
            added = self.apply_model(
                self.folha.tipo_folha.modelo,
                recalculate=False,
                task=task,
                group_cache=group_cache,
                only_events=[],
            )
            # log.debug('<<<<<<<<<<<<<<< APPLYMODEL')
            objs["added"] = added
            objs["changed"] = (added and True) or False
        # log.debug(self)
        query = self.lancamentos.filter(
            Q(evento__evaluate_difference=True)
            & Q(automated=True)
            & Q(evento__configs__calculation__isnull=False)
        ).order_by("evento__order", "evento__numero")
        if ids:
            query = query.filter(id__in=ids)
        # if number_events:
        #     query = query.filter(evento__numero__in=number_events)
        for fe in query.order_by("evento__order", "evento__numero"):
            # log.debug(('AQUI NO FORO with: %s' % fe)
            calc = None
            params = {
                "pct": fe.correct_pct,
                "qnt": fe.correct_qnt,
                "info": fe.info,
                "patronal": fe.correct_patronal,
                "valor_base": fe.correct_base_value,
            }
            params.update(fe.vars)
            calc = fe.instance_calc(group_cache=group_cache)

            rcalc = calc.calculate()

            fe.correct_valor = rcalc.get("valor", 0)
            fe.correct_base_value = rcalc.get("valor_base", 0)
            fe.correct_base_previdencia = rcalc.get("base_previdencia", 0)
            fe.correct_patronal = rcalc.get("patronal", 0)
            fe.correct_qnt = rcalc.get("qnt", 0)
            fe.correct_qnt_max = rcalc.get("qnt_max", 0)
            fe.correct_pct = rcalc.get("pct", 0)
            if calc.CAN_UPDATE_CID:
                fe.oIds = rcalc.get("oIds", [])
                fe.cid = rcalc.get("cid", 0)
            fe.save()

            if fe.has_visual_changes:
                objs["changed"] = True
                fup = {"pk": fe.pk}.update(fe.diff)
                objs["updateds"].append(fup)
            if can_delete:
                if not fe.difference_items.exclude(
                    difference__entries_payment=None
                ).exists() and (
                    (
                        fe.valor <= 0
                        and fe.patronal <= 0
                        and fe.correct_valor <= 0
                        and fe.correct_patronal <= 0
                    )
                ):

                    fe.delete(recalculate=False)

            if "callback" in rcalc:
                rcalc["callback"](entry=fe)

        if not group_cache:
            delete_cache(group_key_cache)

        return objs

    def generate_differences(self, target_payroll):
        self.evaluate_differences()

    def add_evento(self, recalc=True, confirma_folha=False, **kargs):
        kargs.update(contracheque=self)
        # log.debug((kargs)
        try:

            fe = FolhaEvento(
                contracheque=self,
                evento=kargs.get("evento", kargs.get("evento_id")),
                info=kargs.get("info", None),
                insertion_type=kargs.get("insertion_type", 3),
            )

            for key in kargs:
                # log.debug(('ADDEVENTO: KEY: %s V: %s' % (key, kargs[key]))
                setattr(fe, key, kargs[key])

            # Deixando o lancamento em estado de PENDENTE
            # fe.set_pendente(folha=confirma_folha)
            fe.save()  # Salvando apenas se tiver tido alterações
            self.recalculate()
            log.debug("ADDEVENTO: CREATING EVENTO %s" % (fe))
            if "callback" in kargs:
                kargs["callback"](entry=fe)

        except IntegrityError:
            # log.exception(e.message)
            raise self.DuplicateFolhaEvento(
                "O evento %s ja existe no contracheque %s e nao pode ser sobrescrito!"
                % (kargs["evento"], self.servidor)
            )
        else:
            if recalc:
                self.recalculate()

            # self.alterado = True
            # self.save()
            return fe, True

    @transaction.atomic
    def delete_evento(self, ids, recalc=True):
        log.info(ids)
        deleteds = []
        for id in ids:
            log.info("DELETING FOLHAEVENTO: %s" % id)
            fe = self.lancamentos.get(pk=id)
            fe.delete()
            if fe.status in ("CT", "CE", "BS"):
                deleteds.append(fe)

        if recalc and deleteds:
            self.recalculate()

        return deleteds

    @transaction.atomic
    def update_evento(self, recalc=True, confirma_folha=False, **kargs):
        # log.debug((kargs)
        kargs.update(contracheque=self)
        try:

            # fe = FolhaEvento.objects.get(
            #       contracheque= self, evento= kargs.get('evento'), info= kargs.get('info', None))
            # log.debug(('EDITING CC: %s' % str(self))
            fe = self.lancamentos.get(
                id=kargs.get("id"), evento=kargs.get("evento", kargs.get("evento_id"))
            )
            # log.debug(('EDITING: %s' % (fe))

            for key in kargs:
                setattr(fe, key, kargs[key])

            # log.debug(('UPDATING ENTRY: %s' % fe)

            old_fields = fe.old_fields

            # if fe.old_fields:
            fe.save()  # Salvando apenas se tiver tido alterações

            if recalc and old_fields:
                self.recalculate()

        except FolhaEvento.DoesNotExist:
            raise Exception(
                "O evento %s não existe no contracheque e por isso não pode ser editado!"
                % kargs["evento"]
            )
        else:
            return fe, (fe.old_fields and True or False)

    @transaction.atomic
    def update_or_create_entry(self, recalc=True, confirma_folha=False, **kargs):
        kargs.update(contracheque=self)
        cid = kargs.get("cid", None)

        try:
            created = False
            if "id" in kargs and kargs.get("id"):
                fe = self.lancamentos.get(
                    id=kargs.get("id"),
                    evento_id=kargs.get("evento_id") or kargs.get("evento").id,
                )
                fe.rra_employee = kargs.get("rra_employee")
            else:
                automated = kargs.get("automated", True)
                # Choice id 1 - Tipo de Inserção vinda do kargs ou 1 - Automática ou 2 - Manual
                insertion_type = kargs.get("insertion_type", 1 if automated else 2)

                fe, created = self.lancamentos.get_or_create(
                    evento_id=kargs.get("evento_id") or kargs.get("evento").id,
                    info=kargs.get("info", ""),
                    cid=cid if cid else 0,
                    reference_month=kargs.get(
                        "reference_month", self.folha.periodo.mes
                    ),
                    reference_year=kargs.get("reference_year", self.folha.periodo.ano),
                    paycheck_difference=kargs.get("paycheck_difference", None),
                    defaults={"insertion_type": insertion_type},
                )

            if "id" in kargs and not kargs["id"]:
                kargs.pop("id")

            for key in kargs:
                # log.debug('APPLY TO2: %s > %s' % (key, kargs[key]))
                if kargs[key] is not None:
                    setattr(fe, key, kargs[key])

            if fe.old_fields or created or fe.qnt != 0:
                fe.save()  # Salvando apenas se tiver tido alterações

            if recalc:
                self.recalculate()

        except FolhaEvento.DoesNotExist:
            raise Exception(
                "O evento %s não existe no contracheque e por isso não pode ser editado!"
                % kargs["evento"]
            )
        else:
            return fe, created, fe.old_fields

    def _pensions_of_employee(self):
        return self.servidor.pensao_pagador.exclude(
            Q(data_inicio__gt=self.folha.date_range.last)
            | (~Q(data_fim=None) & Q(data_fim__lt=self.folha.date_range.first))
        )

    def _get_pays_pension(self):
        pensions = self._pensions_of_employee()
        pensions_food = pensions.filter(type_of_pension=1)
        pensions_death = pensions.filter(type_of_pension=2)
        if pensions_death.exists():
            return 2
        elif pensions_food.exists() and (
            self.lancamentos.filter(evento__pension_events__in=pensions_food).exists()
            or self.pensioner
        ):
            return 1
        return 0

    def _get_is_cedido(self):
        start_date = self.folha.date_range.first
        end_date = self.folha.date_range.last
        afoo = AfastamentoOutroOrgao.objects.filter(
            posse__servidor=self.servidor
        ).exclude(
            Q(data_inicio__gt=end_date)
            | (~Q(data_fim=None) & Q(data_fim__lt=start_date))
        )
        return afoo.exists()

    def _get_employee_source(self):
        if self.pensioner:
            return 6
        elif self.servidor.is_acordo_cooperacao:
            return 3
        elif self._get_is_cedido():
            return 2
        return 1

    def _get_margens(self, group_cache=None):
        # from rh.gfp.calcs.mpto.utils import ConsignableMargin
        consignado = consignavel = 0.0
        # log.debug("Lancamentos: %s" % self.lancamentos.count())
        if self.pk and self.folha.tipo_folha.margem > 0:
            # consignavel = ConsignableMargin(self.servidor, self.folha, Evento.objects.all()[0]).value()
            consignado = float(
                self.lancamentos.filter(evento__aplica_consignado=True).aggregate(
                    total=Sum("valor")
                )["total"]
                or 0.00
            )
            only_events = [
                fe.evento.numero
                for fe in self.lancamentos.filter(evento__aplica_consignavel=True)
            ]
            for fe in self.lancamentos.filter(Q(evento__aplica_consignavel=True)):
                params = {
                    "pct": fe.pct,
                    "qnt": fe.qnt,
                    "info": fe.info,
                    "patronal": fe.patronal,
                    "valor_base": fe.valor_base,
                }
                params.update(fe.vars)
                valor = (
                    round(
                        fe.classcode.cls(
                            self.servidor,
                            self.folha,
                            fe.evento,
                            only_events=only_events,
                            group_cache=group_cache,
                            params=params,
                            pensioner=self.pensioner,
                        ).valor(),
                        2,
                    )
                    if fe.evento.automated and not self.pensioner
                    else fe.valor
                )
                # log.debug('GET MARGEM: %s - %s' % (valor, fe.evento))
                consignavel += (
                    float(fe.valor) if fe.evento.tipo == "P" else -float(valor)
                )

            # log.debug("%s: %s M[%s:%s] %s" % (fe.evento, fe.valor, consignado, consignavel, exclude_events))
        return (
            (
                round(consignavel * float(self.folha.tipo_folha.margem) / 100.0, 2),
                round(consignado, 2),
            )
            if consignavel > 0
            else (0.0, 0.0)
        )

    def _update_or_create_margins(self, group_cache=None):
        # from rh.gfp.calcs.mpto.utils import ConsignableMargin
        if not self.pk:
            return []

        margins = [mp.pk for mp in self.margin_paychecks.all()]
        for mc in self.folha.tipo_folha.margins.filter(active=True):
            if self.folha.dt_pagamento >= mc.start_validity:
                # if self.pk and self.folha.tipo_folha.margem > 0:
                # log.debug("GET MARGEM FOR %s: %s" % (mc.identification, self))
                # consignavel = ConsignableMargin(self.servidor, self.folha, Evento.objects.all()[0]).value()
                consigned_value = float(
                    self.lancamentos.filter(evento__in=mc.consigneds.all()).aggregate(
                        total=Sum("valor")
                    )["total"]
                    or 0.00
                )
                consignable_value = 0.0
                query_entries = self.lancamentos.filter(
                    evento__in=mc.consignables.all()
                )
                only_events = [fe.evento.numero for fe in query_entries]
                for fe in query_entries:
                    if fe.automated and not self.pensioner:
                        params = {
                            "pct": fe.pct,
                            "qnt": fe.qnt,
                            "info": fe.info,
                            "patronal": fe.patronal,
                            "valor_base": fe.valor_base,
                        }
                        params.update(fe.vars)
                        value = round(
                            fe.classcode.cls(
                                self.servidor,
                                self.folha,
                                fe.evento,
                                entry=fe,
                                only_events=only_events,
                                group_cache=group_cache,
                                params=params,
                                pensioner=self.pensioner,
                            ).value(),
                            2,
                        )
                    else:
                        value = fe.valor
                    # log.debug('GET MARGEM 2: %s > %s - %s' % (mc.identification, value, fe.evento))
                    consignable_value += (
                        float(value) if fe.evento.tipo == "P" else -float(value)
                    )

                consignable_value *= float(mc.percentage) / 100.0

                mp, created = self.margin_paychecks.get_or_create(margin=mc)
                mp.total_value = round(consignable_value, 2)
                mp.value = round(consignable_value, 2) - round(consigned_value, 2)
                mp.save()
                if mp.pk in margins:
                    margins.remove(mp.pk)
                self.margin_paychecks.filter(pk__in=margins).delete()

        self.margem_consignada_total = (
            self.margin_paychecks.all().aggregate(total=Sum("total_value")).get("total")
            or 0
        )
        self.margem_consignada_livre = (
            self.margin_paychecks.filter(value__gt=0)
            .aggregate(total=Sum("value"))
            .get("total")
            or 0
        )
        return [mp1 for mp1 in self.margin_paychecks.all()]

    def _get_lotacao(self):
        return (
            self.servidor.workplace_by_date(self.folha.date_range.last)
            or self.servidor.workplace_by_date(self.folha.date_range.first)
            or None
        )

    def _get_situacao_funcional(self):
        from rh.utils import verifica_situacao_funcional

        texto = "EM ATIVIDADE"
        if self.pensioner and self._get_pays_pension() == 2:
            texto = "PARTILHA"
        elif self.pensioner and self._get_pays_pension() == 1:
            texto = "PENSÃO ALIMENTÍCIA"
        elif (
            verifica_situacao_funcional(self.servidor.situacao_funcional_cache)
            == "INATIVO"
        ):
            texto = "INATIVO"
        elif (
            verifica_situacao_funcional(self.servidor.situacao_funcional_cache)
            == "NOT_FOUND"
        ):
            texto = "----"
        return texto

    def _get_situacao_previdenciaria(self):
        return (
            "ATIVO"
            if self.servidor.is_trainee()
            or self.servidor.get_posses_ativas(
                self.folha.date_range.first, self.folha.date_range.last
            )
            else "INATIVO"
        )

    def _get_cargos_referencia(self, tipos=None):
        cargos = {}
        # TODO Criar um método que devolva a referencia salarial de uma posse em uma determinada data,
        # talvez seja melhor adicioanr à classe da posse
        # mas como posse está no módulo de RH, creio ser plausivel adicionar o metodo à classe em runtime, com plugin
        data_ = datetime.now().date()
        if self.folha.dt_pagamento and self.folha.dt_pagamento < data_:
            data_ = self.folha.dt_pagamento

        posses = self.servidor.get_posses_ativas(
            self.folha.date_range.first, self.folha.date_range.last
        ).order_by("data_exercicio")
        if tipos:
            posses = posses.filter(quadro__cargo__tipo_lei_cargo__in=tipos)

        # Servidor sem posse ativa na data de pagamento
        if posses:
            for posse in posses.with_office_valid_in(self.folha.date_range):
                if hasattr(posse, "requestmove"):
                    cargos["AC"] = None, None

                elif posse.quadro.cargo.tipo_lei_cargo in ["AC", "ES"]:
                    cargos[posse.quadro.cargo.tipo_lei_cargo] = posse.quadro.cargo, None

                else:
                    ref = self._get_referencia_from_posse(
                        posse, self.folha.date_range.first, self.folha.date_range.last
                    )
                    cargos[posse.quadro.cargo.tipo_lei_cargo] = posse.quadro.cargo, ref
        return cargos

    @classmethod
    def _get_referencia_from_posse(cls, posse, data_inicio=None, data_fim=None):
        data_inicio = datetime.now().date() if not data_inicio else data_inicio
        # log.debug('POSSE: %s DATA: %s' % (posse, data_inicio))
        salarios = None

        if data_fim is None:
            data_fim = data_inicio

        if posse:
            if posse.my_type == "requestmove":
                salarios = None
            elif (
                posse.quadro.cargo.tipo_lei_cargo in ["CM", "FC", "EL", "ES"]
                or posse.quadro.cargo.indicativo == "M"
            ):
                salarios = EstruturaTabelaSalarial.salarios(
                    posse.quadro.cargo, data_inicio, data_fim
                )
            elif posse.quadro.cargo.tipo_lei_cargo in [
                "EF",
            ]:
                progs = posse.progressoes.exclude(
                    Q(data_inicio_vigencia__gt=data_fim)
                    | (
                        ~Q(data_fim_vigencia=None)
                        & Q(data_fim_vigencia__lt=data_inicio)
                    )
                ).order_by("-data_inicio_vigencia")
                if progs:
                    salarios = EstruturaTabelaSalarial.salarios(
                        posse.quadro.cargo,
                        data_inicio,
                        data_fim,
                        referencia=progs[0].referencia_nivel2d,
                    )
                else:
                    # NOTIFY WARNING Notificar que o servidor está sem progressão para a posse efetiva
                    log.warning(
                        "NOTIFY WARNING: O servidor %s não possui progressão para o cargo %s em %s."
                        % (posse.servidor, posse.quadro, data_inicio)
                    )
            else:
                # NOTIFY ERROR Notificar que o sistema encontrou uma condição desconhecida
                log.warning(
                    "NOTIFY ERROR: O sistema encontrou uma condição desconhecida em _get_referencia_from_posse(%s, %s)"
                    % (posse, data_inicio)
                )

        return salarios[-1][1] if salarios else None

    def _get_base_previdenciaria(self):
        return (
            self.lancamentos.filter().aggregate(total=Sum("base_previdencia"))["total"]
            or 0.0
        )

    def _get_base_irrf(self):
        return 0.0

    def _get_dado_bancario(self):
        # t = datetime.now()

        person = self.servidor.pessoa_fisica
        if self.pensioner:
            pension = self.pensioner.pensao_pensionista.filter(
                Q(data_inicio__lte=self.folha.date_range.last)
                & (Q(data_fim=None) | Q(data_fim__gte=self.folha.date_range.first))
            ).first()
            if not pension:
                return None
            person = pension.representante_legal
        betp = BankingEmployeeTypePayroll.objects.filter(
            person=person, type_of_payroll=self.folha.tipo_folha
        ).first()
        db = (
            betp.banking_person
            if betp
            else DadoBancarioPessoa.objects.filter(
                pessoa=person, principal=True
            ).first()
        )

        return db

    def _get_total_bruto(self):
        return round(
            self.lancamentos.filter(status__in=("CT", "CE"), evento__tipo="P")
            .exclude(evento__tipo="I")
            .aggregate(total=Sum("value"))["total"]
            or 0,
            2,
        )

    def _get_total_liquido(self):
        return round(
            self.lancamentos.filter(status__in=("CT", "CE"))
            .exclude(evento__tipo="I")
            .aggregate(total=Sum("value"))["total"]
            or 0,
            2,
        )

    def _get_dependentes_irrf(self):
        # return self.servidor.dependentes.filter(dep_ir = True).count()
        return Dependencia.objects.irrf_actives(
            self.servidor, self.folha.date_range.last
        ).count()

    def _get_dependentes_salario_familia(self):
        return self.servidor.dependentes.filter(dep_sf=True).count()

    def _get_error_validations(self):

        errors = 0
        if self.employee_pays_pension != 2 and not self.dado_bancario_pessoa:
            # VERIFIY BANKING DATA FOR VALIDS PAYCHECKS
            errors |= 1

        if self.employee_pays_pension and self.pensioner is None:
            # VERIFY ERROR PAYCHECKS PEYING PENSION
            if self.employee_pays_pension == 2:
                # PARTITION
                if self.total_liquido != 0:
                    errors |= 4  # 4: 'Partilha não zerada'
            elif self.employee_pays_pension == 1:
                # FOOD PENSION
                pass
        if self.total_liquido < 0:
            errors |= 8

        return errors

    def _get_classification(self):
        map_classification = {
            "EFE": 1,
            "ECM": 1,
            "EFC": 1,
            "MBR": 2,
            "MEL": 2,
            "MCM": 2,
            "MEC": 2,
            "MBR2": 2,
            "MEL2": 2,
            "MCM2": 2,
            "MEC2": 2,
            "CMS": 3,
            "REQ": 4,
            "RCM": 4,
            "RFC": 4,
            "CTR": 8,
            "EST": 5,
            "TCR": 8,
            "VOL": 8,
            "EXT": 8,
            "MAP": 9,
            "MAP2": 9,
            "SAP": 9,
            "BNF": 10,
        }
        # cargos = [p.quadro.cargo.tipo_lei_cargo for p in self.servidor.posses.all()]
        # cargos = [('AC' if p.my_type == 'requestmove' else p.quadro.cargo.tipo_lei_cargo) for p in self.servidor.posses.all()]

        classification = 8
        if self.pensioner:
            if self._get_pays_pension() == 2:
                classification = 7  # PARTILHA
            else:
                classification = 6  # PENSIONISTA
        else:
            classification = map_classification.get(self.servidor.type_by_possession, 8)

        return classification

    @property
    def validations(self):
        errors = []
        for k in self.VALIDATIONS:
            if (self.error_validations & k) == k:
                errors.append(self.VALIDATIONS[k])

        return errors

    @property
    def total_liquido_lancamentos(self):
        total_prov = self.lancamentos.filter(evento__tipo="P").aggregate(Sum("valor"))[
            "valor__sum"
        ]
        if total_prov is None:
            total_prov = decimal.Decimal(0)
        total_desc = self.lancamentos.filter(evento__tipo="D").aggregate(Sum("valor"))[
            "valor__sum"
        ]
        if total_desc is None:
            total_desc = decimal.Decimal(0)

        return total_prov - total_desc

    @property
    def previous_paycheck(self):
        conf_paycheck_current = self.conference_event_paycheck_current.filter()
        if conf_paycheck_current:
            conf_paycheck_previous = conf_paycheck_current.filter(
                event_paycheck_previous__isnull=False
            ).first()
            if conf_paycheck_previous:
                return conf_paycheck_previous.event_paycheck_previous.pk
        return None

    @property
    def next_paycheck(self):
        month = 1 if self.folha.periodo.mes == 12 else self.folha.periodo.mes + 1
        year = (
            self.folha.periodo.ano + 1
            if self.folha.periodo.mes == 12
            else self.folha.periodo.ano
        )
        next_paycheck = ContraCheque.objects.filter(
            folha__periodo__mes=month,
            folha__periodo__ano=year,
            servidor=self.servidor,
            pensioner=self.pensioner,
            folha__tipo_folha=self.folha.tipo_folha,
        ).first()
        if next_paycheck:
            return next_paycheck
        return None

    def apply_model(
        self,
        modelo,
        recalculate=True,
        task=None,
        group_cache=None,
        only_events=[],
        exclude_events=[],
        force=False,
    ):
        # eventos_paycheck = [fe.evento for fe in self.lancamentos.all()]
        added_or_updated = []
        if self.folha.complement and not force:
            return added_or_updated

        group_key_cache = group_cache if group_cache else make_group_key()
        currents_config = ConfigEvent.objects.current_in(
            self.folha.date_range.first, self.folha.date_range.last
        ).filter(automated=True, calculation__isnull=False)
        # query = modelo.principais.filter(configs__in=currents_config).order_by('order', 'numero')
        query = currents_config.filter(event__in=modelo.principais.all())
        if only_events:
            query = query.filter(event__numero__in=only_events)
        if exclude_events:
            query = query.exclude(event__numero__in=exclude_events)

        for cfg_event in query:
            # log.info('Calculando evento %s para o servidor %s.' % (evento, self.servidor))
            evento = cfg_event.event

            try:
                calc = cfg_event.calculation.cls(
                    self.servidor,
                    self.folha,
                    evento,
                    group_cache=group_key_cache,
                    pensioner=self.pensioner,
                )
            except Exception as e:
                log.exception(e)
            else:
                if getattr(calc, "MULTI_CALCULATE", False):
                    calcs = calc.calculate_multi()
                else:
                    calcs = [
                        calc.calculate(),
                    ]
                for rcalc in calcs:
                    if rcalc.get("valor") > 0.00 or rcalc.get("patronal") > 0.00:

                        rcalc.update(
                            {
                                "folha": self.folha,
                                "evento": evento,
                                "servidor": self.servidor,
                                "lancamento": evento.lancamento,
                                "reference_year": rcalc.get("references", None)[0],
                                "reference_month": rcalc.get("references", None)[1],
                                "correct_valor": rcalc.get("valor", 0),
                                "correct_base_value": rcalc.get("valor_base", 0),
                                "correct_qnt": rcalc.get("qnt", 0),
                                "correct_qnt_max": rcalc.get("qnt_max", 0),
                                "correct_pct": rcalc.get("pct", 0),
                                "correct_patronal": rcalc.get("patronal", 0),
                                "correct_base_previdencia": rcalc.get(
                                    "base_previdencia", 0
                                ),
                                "cid": rcalc.get("cid", 0),
                            }
                        )
                        exists = self.lancamentos.filter(
                            evento=rcalc.get("evento"),
                            info=rcalc.get("info", ""),
                            reference_month=rcalc.get(
                                "reference_month", self.folha.periodo.mes
                            ),
                            reference_year=rcalc.get(
                                "reference_year", self.folha.periodo.ano
                            ),
                            # cid=rcalc.get('cid', None)  # TODO Aguardando classcodes
                        ).exists()

                        if not exists:

                            fe, created, old_fields = self.update_or_create_entry(
                                False, False, **rcalc
                            )
                            # log.debug('RCALC: %s (%s) %s' % (fe, old_fields, rcalc))
                            formatted_desc = "\n\rID: {} CID: {} INFO: {}".format(
                                fe.id, fe.cid, fe.info
                            )

                            if created:
                                added_or_updated.append(fe)
                                task and task.info(
                                    "EVENTO ADICIONADO pelo modelo: %s - %s!%s"
                                    % (fe.evento, fe.servidor, formatted_desc),
                                    2,
                                )
                            elif old_fields:
                                added_or_updated.append(fe)
                                if fe.has_pendencies:
                                    log.debug(
                                        ">> LANÇAMENTO MODIFICADO: (%s) [%s] %s - %s!"
                                        % (
                                            fe.has_pendencies,
                                            old_fields,
                                            fe.evento,
                                            fe.servidor,
                                        )
                                    )
                                    task and task.info(
                                        "LANÇAMENTO MODIFICADO: %s - %s!%s"
                                        % (fe.evento, fe.servidor, formatted_desc),
                                        1,
                                    )

                            if "callback" in rcalc:
                                rcalc.get("callback")(entry=fe)

                            # log.info('APPLYMODEL: %s EVENTO %s' % (
                            #     'CREATED/UPDATED' if created else 'NOT CHANGED', fe.evento))

        if recalculate:
            result = self.recalculate(task=task, group_cache=group_key_cache)
            added_or_updated += result.get("added", [])
            added_or_updated += result.get("updateds", [])
            added_or_updated += result.get("deleteds", [])

        if not group_cache:
            delete_cache(group_key_cache)

        return added_or_updated

    def confirm(self, entries_pk):
        user = get_current_user()

        is_rh = user.has_perm("gfp.can_validate_event_payroll")
        is_ci = user.has_perm("gfp.can_validate_event_internal_control")

        if not (is_rh or is_ci):
            raise UserHasNotPermission("VALIDAÇÃO DE LANÇAMENTOS")

        for entry in self.lancamentos.filter(pk__in=entries_pk):
            is_rh and entry._confirm_dep_payroll()
            is_ci and entry._confirm_dep_control()


@deprecated
class ContraChequePensionista(AuditTimestampModel):
    class Meta:
        db_table = "gfp_contrachequepensionista"
        unique_together = ("contracheque_servidor", "pensionista")

    AUDITABLE = {
        "fields": [
            "dado_bancario_pessoa",
        ],
        "exclude": ["id", "abstract_fields"],
    }

    pensionista = models.ForeignKey(
        "rh.PessoaFisica",
        on_delete=models.CASCADE,
        related_name="contracheque_pensionista",
        verbose_name="Pensionista",
    )
    contracheque_servidor = models.ForeignKey(
        ContraCheque,
        verbose_name="Contrachque",
        related_name="paychecks",
        on_delete=models.CASCADE,
    )
    dado_bancario_pessoa = models.ForeignKey(
        "rh.DadoBancarioPessoa",
        on_delete=models.PROTECT,
        verbose_name="Dado Bancário",
        related_name="contracheques_pensionista",
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s:%s" % (self.contracheque_servidor, self.pensionista.abbreviation)

    def _get_dado_bancario(self):
        pensions = self.pensionista.pensao_pensionista.filter(
            Q(servidor=self.contracheque_servidor.servidor)
            & Q(data_inicio__lte=self.contracheque_servidor.folha.date_range.last)
            & (
                Q(data_fim=None)
                | Q(data_fim__gte=self.contracheque_servidor.folha.date_range.first)
            )
        ).order_by("-data_inicio")
        pension = pensions[0] if pensions else None
        if pension:
            betp = BankingEmployeeTypePayroll.objects.filter(
                person=pension.representante_legal,
                type_of_payroll=self.contracheque_servidor.folha.tipo_folha,
            ).first()
            return betp.banking_person
        return None

    def save(self, *args, **kargs):
        self.dado_bancario_pessoa = self._get_dado_bancario()
        super(ContraChequePensionista, self).save(*args, **kargs)


class ContraChequeAuditoria(AuditTimestampModel):
    class Meta:
        ordering = ("-contracheque__folha", "-created_at")

    contracheque = models.ForeignKey(
        ContraCheque, related_name="audit_changes", on_delete=models.CASCADE
    )
    contracheque_info = models.CharField(
        max_length=250, verbose_name="Contracheque", default=""
    )
    resumo = models.CharField(max_length=250, verbose_name="Título")
    texto = models.TextField()
    conferido = models.BooleanField(default=False, verbose_name="Conferido")
    folha_aplicada = models.ForeignKey(
        Folha, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )


class Enquadramento(models.Model):
    class Meta:
        db_table = "enquadramento"
        managed = False

    matricula = models.IntegerField(
        verbose_name="Matricula", primary_key=True, default=0, blank=True
    )
    cargo = models.CharField(
        max_length=400, verbose_name="Cargo", blank=True, null=True
    )
    classe_padrao_atual = models.CharField(
        max_length=20, verbose_name="classe_padrao", blank=True, null=True
    )
    classe_padrao_prox = models.CharField(
        max_length=20, verbose_name="classe_padrao", blank=True, null=True
    )
    data_exercicio = models.DateField(null=True)
    prox_progressao = models.DateField(null=True)
    data_referencia = models.DateField(null=True)
    dias_sem_contar = models.IntegerField(
        verbose_name="dias_neg", default=0, blank=True
    )
    status = models.CharField(
        max_length=1, verbose_name="status", blank=True, null=True
    )


class ExtraPayment(AuditTimestampModel):

    class Meta:
        ordering = ("name",)

    slug = models.SlugField(verbose_name="slug")
    name = models.CharField(max_length=64, verbose_name="Nome")

    def __str__(self):
        return str(self.name)

    def update_periods(self, value, start_validity, pct=True, add=True):
        # log.debug(('UPDATE PERIODS: %s:%s: pct:%s add:%s' % (value, start_validity, pct, add))
        if pct:
            value = value / 100.0
        for period in self.periods.filter(end_validity=None):
            _value = float(period.value)
            if add:
                _value = (_value * (1 + value)) if pct else (_value + value)
            else:
                _value = (_value * value) if pct else value

            self.periods.create(
                start_validity=start_validity, employee=period.employee, value=_value
            )

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.slug:
                self.slug = slugify(self.name).upper()
        super(ExtraPayment, self).save(*args, **kwargs)


class ExtraPaymentPeriodQueryset(models.QuerySet):
    def of_employee(self, employee):
        return self.filter(employee=employee)

    def of_slugs(self, slug):
        return self.filter(extra_payment__slug__in=slug)

    def no_cumulation(self):
        return self.exclude(extra_payment__slug="CUMULATION")

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(decision_date__gt=range_.last)
                | (~Q(end_validity=None) & Q(end_validity__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(decision_date__gt=data)
                | (~Q(end_validity=None) & Q(end_validity__lt=data))
            )


class ExtraPaymentPeriod(AuditTimestampModel):
    class Meta:
        ordering = ("extra_payment", "-start_validity", "employee")

    AUDITABLE = {
        "fields": [
            "value",
            "start_validity",
            "end_validity",
            "decision_date",
            "extra_payment",
            "employee",
        ]
    }

    extra_payment = models.ForeignKey(
        "ExtraPayment",
        verbose_name="Pagamento",
        related_name="periods",
        on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.CASCADE,
        verbose_name="Servidor",
        null=True,
        blank=True,
        related_name="extrapaymentperiods",
    )
    type_value = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_OF_VALUE"),
        verbose_name="Tipo",
        default=1,
    )
    value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    start_validity = models.DateField(verbose_name="Início efeito financeiro")
    end_validity = models.DateField(
        verbose_name="Fim efeito financeiro", null=True, blank=True
    )
    decision_date = models.DateField("Data da Decisão", null=True, blank=True)
    information = models.CharField(
        max_length=50, verbose_name="Info", default="", blank=True
    )
    close_prev_period = models.BooleanField(default=False)
    main_salary = models.BooleanField("Aplica-se à remuneração principal", default=True)
    gratification = models.BooleanField("Aplica-se à gratificação", default=False)

    objects = ExtraPaymentPeriodQueryset.as_manager()

    def __str__(self):
        return "%s - %s: %s/%s - %s" % (
            self.extra_payment.slug,
            self.employee,
            self.start_validity,
            self.end_validity,
            self.value,
        )

    @property
    def _prev(self):
        q = (
            ExtraPaymentPeriod.objects.exclude(pk=self.pk)
            .filter(
                extra_payment=self.extra_payment,
                employee=self.employee,
                start_validity__lt=self.start_validity,
            )
            .order_by("-start_validity")
        )
        return q[0] if q.exists() else None

    @property
    def _next(self):
        q = (
            ExtraPaymentPeriod.objects.exclude(pk=self.pk)
            .filter(
                extra_payment=self.extra_payment,
                employee=self.employee,
                start_validity__gt=self.start_validity,
            )
            .order_by("start_validity")
        )
        return q[0] if q.exists() else None

    def delete(self, *args, **kwargs):
        _prev = self._prev

        super(ExtraPaymentPeriod, self).delete(*args, **kwargs)

        if _prev:
            _prev.save()

    def save(self, *args, **kwargs):
        _prev = self._prev
        _next = self._next
        # log.debug(('PREV: %s' % _prev)

        if self.close_prev_period is True:
            if _prev:
                _prev.end_validity = self.start_validity - relativedelta(days=1)

            if _next:
                self.end_validity = _next.start_validity - relativedelta(days=1)
            else:
                self.end_validity = None

        if not self.pk or self.changed:
            if not self.decision_date:
                self.decision_date = self.start_validity
            super(ExtraPaymentPeriod, self).save(*args, **kwargs)
            # log.debug(('Saving %s' % self)
        else:
            log.debug("No changes in %s" % self)

        if _prev and _prev.changed:
            _prev.save()
            # log.debug(('Save PREV >> %s' % _prev)


class CorrectionFactor(AuditTimestampModel):
    class Meta:
        ordering = (
            "identifier",
            "-ref_payment_year",
            "-ref_payment_month",
            "-ref_difference_year",
            "-ref_difference_month",
        )
        unique_together = (
            (
                "identifier",
                "ref_payment_year",
                "ref_payment_month",
                "ref_difference_year",
                "ref_difference_month",
            ),
        )

    identifier = models.CharField(
        max_length=8, verbose_name="Identificador", db_index=True
    )
    factor = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    ref_payment_year = models.PositiveSmallIntegerField(verbose_name="Ref. Pag. - ANO")
    ref_payment_month = models.PositiveSmallIntegerField(verbose_name="Ref. Pag. - MÊS")
    ref_difference_year = models.PositiveSmallIntegerField(
        verbose_name="Ref. Dif. - ANO"
    )
    ref_difference_month = models.PositiveSmallIntegerField(
        verbose_name="Ref. Dif. - MÊS"
    )
    ref_payment_cache = models.CharField(
        max_length=15,
        verbose_name="Identificador",
        default="",
        blank=True,
        db_index=True,
    )
    ref_difference_cache = models.CharField(
        max_length=6,
        verbose_name="Identificador",
        default="",
        blank=True,
        db_index=True,
    )

    def save(self, *args, **kwargs):
        self.ref_difference_cache = "%02d%04d" % (
            self.ref_difference_month,
            self.ref_difference_year,
        )
        self.ref_payment_cache = "%s.%02d%04d" % (
            self.identifier,
            self.ref_payment_month,
            self.ref_payment_year,
        )
        super(CorrectionFactor, self).save(*args, **kwargs)


class PaycheckDifference(AuditTimestampModel):

    DEFAULT_USER = "athenas"

    SINGLE_MODE = 1
    SEPARETE_REF_MODE = 2

    title = models.CharField(max_length=256, verbose_name="Título", blank=True)
    identifier = models.CharField(
        max_length=32, verbose_name="Identificador", db_index=True, blank=True
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        related_name="paycheck_differences",
        verbose_name="Servidor",
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        "Evento",
        related_name="paycheck_differences",
        verbose_name="Evento",
        on_delete=models.CASCADE,
    )
    payment_event = models.ForeignKey(
        "Evento",
        on_delete=models.CASCADE,
        related_name="differences_payment",
        verbose_name="Evento de pagamento",
        null=True,
        blank=True,
    )
    rra_employee = models.ForeignKey(
        "RRAEmployee",
        on_delete=models.CASCADE,
        related_name="differences",
        null=True,
        blank=True,
        verbose_name="RRA Servidor",
    )
    installments = models.PositiveSmallIntegerField(default=1, verbose_name="Parcelas")
    reference_year = models.PositiveSmallIntegerField(
        verbose_name="Ano Referência", blank=True, default=2015
    )
    reference_month = models.PositiveSmallIntegerField(
        verbose_name="Mês Referência", blank=True, default=1
    )
    status = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Situação",
        choices=Choice.get_choices_for("gfp", "STATUS_PAYCHECK_DIFFERENCE"),
    )
    reason_difference = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Motivo",
        choices=Choice.get_choices_for("gfp", "DIFFERENCE_TYPE"),
    )
    description = models.CharField(
        max_length=400, verbose_name="Descrição", default="", blank=True
    )
    entries = models.ManyToManyField(
        "FolhaEvento",
        through="PaycheckDifferenceItem",
        through_fields=("difference", "entry_difference"),
    )
    diff_type = models.CharField(
        max_length=3, verbose_name="Tipo", default="", blank=True
    )
    correction_factor_identifier = models.CharField(
        max_length=15,
        verbose_name="Fator de correção",
        db_index=True,
        null=True,
        blank=True,
    )
    focuses_on = models.ManyToManyField(
        "Evento", verbose_name="Incide sobre", related_name="focuses_by_differences"
    )
    total_value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0
    )
    expected_end_year = models.PositiveSmallIntegerField(
        verbose_name="Ano Referência", blank=True, default=2017
    )
    expected_end_month = models.PositiveSmallIntegerField(
        verbose_name="Mês Referência", blank=True, default=1
    )
    source_differences = models.BooleanField(
        verbose_name="Gestor de diferenças?", default=False
    )
    employer_contribution_to_pay = models.DecimalField(
        default=0,
        verbose_name="Valor/Empregador a Pagar",
        blank=True,
        max_digits=19,
        decimal_places=2,
    )
    value_to_pay = models.DecimalField(
        default=0,
        verbose_name="Valor a Pagar",
        blank=True,
        max_digits=19,
        decimal_places=2,
    )

    class Meta:
        unique_together = (("identifier", "employee", "event"),)
        ordering = ("-reference_year", "-reference_month", "employee", "event")

    class EventsCanNotBeTogether(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Os eventos não podem estar juntos em uma mesma diferença! Os eventos \
                devem ser de um mesmo servidor, mesmo evento e mesmas referências",
            )

    class DifferenceNotApplayable(Exception):
        def __init__(self, uuid, state):
            Exception.__init__(
                self,
                "Apenas diferenças abertas ou aguardando decisão podem ser aplicadas! \
                A diferença %s encontra-se %s"
                % (uuid, state),
            )

    class DifferenceCalculationIncompatible(Exception):
        def __init__(self):
            Exception.__init__(
                self, "O evento de pagamento da diferença não pode ser automático!"
            )

    def __str__(self):
        return "%s : %s : %s" % (self.employee, self.event, self.identifier)

    @classmethod
    def factory(
        cls,
        q_entries,
        identifier=None,
        title="",
        status=1,
        installments=1,
        correction_factor_identifier=None,
        rra=None,
        reason_difference=4,
    ):
        if q_entries:
            entry = q_entries[0]
            # log.debug(('CD >> 1 IGNORE: %s ENTRY: %s, CFI: %s' % (status, entry, correction_factor_identifier))
            employee = entry.contracheque.servidor
            event = entry.evento
            rra_employee = None
            if rra:
                rra_employee = RRAEmployee.objects.filter(
                    employee=employee, rra=rra
                ).first()
                if not rra_employee:
                    raise Exception(
                        f"RRA {rra} não encontrado para o servidor {employee}!"
                    )
            # IMPLEMENT CONTEXT with transaction ATOMIC
            pd, created = cls.objects.get_or_create(
                employee=employee,
                event=event,
                reference_year=entry.contracheque.folha.periodo.ano,
                reference_month=entry.contracheque.folha.periodo.mes,
                identifier=identifier,
                installments=installments,
                correction_factor_identifier=correction_factor_identifier,
                status=status,
                defaults={
                    "title": title,
                    "source_differences": True,
                    "rra_employee": rra_employee,
                    "reason_difference": reason_difference,
                },
            )

            # log.debug(('1 CDI: DT: %s TV: %s' % (pd.diff_type, pd.total_value))
            pd.create_diff_items(q_entries)
            # log.debug(('2 CDI: DT: %s TV: %s' % (pd.diff_type, pd.total_value))

            if (
                not (
                    pd.differences["value"] != 0
                    or pd.differences["employer_contribution"] != 0
                )
                and not pd.difference_items.exists()
            ):
                pd.delete()
                # log.debug(('DEL: %s' % pd)
                return None

            return pd
        return None

    @classmethod
    def create_differences(
        cls,
        to_payroll,
        apply_diff=True,
        payrolls=[],
        entries=[],
        employeers=[],
        title="",
        task=None,
        status=1,
        identifier=None,
        diff_mode=1,
        installments=1,
        correction_factor_identifier=None,
        rra=None,
        reason_difference=4,
    ):
        # log.debug(('>>>>>>>>> CD: (I:%s) DM:%s %s' % (status, diff_mode, task))
        task_ = NullTaskSession() if not task else task

        errors = []

        if not payrolls and not entries:
            task_.send_message(
                "Nenhuma folha ou lançamentos indicados para gerar as diferenças!"
            )

        else:
            if entries:
                query = entries
            else:
                query = FolhaEvento.with_differences.filter(folha__in=payrolls)

            if employeers:
                query = query.filter(contracheque__servidor__in=employeers)

            task_["pct"] = 1

            addeds = vq1 = []

            if diff_mode & cls.SINGLE_MODE:
                vq1 = ["pk"]
            else:
                vq1 = ["contracheque__servidor", "evento"]

            dq1 = query.order_by(*vq1).values(*vq1).distinct()
            task_["total"] = dq1.count()
            # log.debug(('DQ1: %s' % [d for d in dq1])
            for el in dq1:
                q2 = query.filter(**el)
                # log.debug(('ELQ1(%d): %s' % (q2.count(), el))
                ev = q2.first().evento

                vq2 = (
                    ["reference_year", "reference_month"]
                    if diff_mode & cls.SEPARETE_REF_MODE
                    else []
                )

                if ev.separate_for_info_event:
                    vq2.append("info")

                vq = vq2 if vq2 else vq1
                # log.debug(('*************** VQ: %s' % vq)
                dq2 = q2.order_by(*vq).values(*vq)

                # log.debug(('DQ1: %s' % [d for d in dq2.distinct()])
                for elq1 in dq2.distinct():
                    q3 = q2.filter(**elq1)
                    # log.debug(('ELQ2(%d): %s' % (q3.count(), elq1))

                    try:
                        with transaction.atomic():
                            pd = cls.factory(
                                q3,
                                title=title,
                                identifier=identifier,
                                status=status,
                                installments=installments,
                                correction_factor_identifier=correction_factor_identifier,
                                rra=rra,
                                reason_difference=reason_difference,
                            )
                            if apply_diff and status not in [6, 7] and pd:
                                addeds += pd.apply(to_payroll, title=title)

                    except Exception as e:
                        log.exception(e)
                        errors.append(e)
                        # raise e

                task_["pct"] += 1

            paychecks = set([fe.contracheque for fe in addeds])

            for paycheck in paychecks:
                paycheck.recalculate(task=task)

        return errors

    @property
    def initial_period(self):
        if self.entries_payment.exists():
            first = self.entries_payment.order_by(
                "contracheque__folha__periodo"
            ).first()
            period = first.contracheque.folha.periodo
            return (period.ano, period.mes)
        return None

    @property
    def initial_expected_end_period(self):
        if self.initial_period:
            end_date = date(
                self.initial_period[0], self.initial_period[1], 1
            ) + relativedelta(months=self.installments - 1)
            return (end_date.year, end_date.month)
        return None

    @property
    def expected_end_period(self):
        if self.initial_period:
            # last = self.entries_payment.order_by('contracheque__folha__periodo').last()
            # installments_payable = self.installments - (
            #     self.entries_payment.aggregate(total=Sum('installments_paid'))['total'] or 0)
            end_date = date(
                self.initial_period[0], self.initial_period[1], 1
            ) + relativedelta(months=self.installments - 1)
            return (end_date.year, end_date.month)
        return None

    @property
    def differences(self):
        result = self.difference_items.aggregate(
            value=Sum("fixed_value"),
            employer_contribution=Sum("fixed_employer_contribution"),
        )
        result.update(
            value=round(result["value"] or 0.00, 2),
            employer_contribution=round(result["employer_contribution"] or 0.00, 2),
        )
        return result

    @property
    def payable(self):
        _payable = {"value": 0.0, "employer_contribution": 0.0}

        # Se a diferença for manual, ou seja, não possui origem em lançamentos da folha
        if not self.source_differences:
            pp = {
                "value": self.total_value,
                "employer_contribution": self.total_employer_contribution,
            }
        else:
            pp = self.difference_items.aggregate(
                value=Sum("fixed_value"),
                employer_contribution=Sum("fixed_employer_contribution"),
            )
        _payable["value"] = round(float(pp["value"] or 0) - self.payments["value"], 2)
        _payable["employer_contribution"] = round(
            float(pp["employer_contribution"] or 0)
            - float(self.payments["employer_contribution"]),
            2,
        )

        return _payable

    @property
    def payables(self):
        _events = {}
        for diff in self._evalute_config_string:
            # log.debug('%s---------------------------------------------------------' % diff)
            _payable = {"value": 0.0, "employer_contribution": 0.0}
            _payable["value"] = round(
                self._evalute_config_string[diff]["value"] - self.payments["value"], 2
            )
            _payable["employer_contribution"] = round(
                self._evalute_config_string[diff]["employer_contribution"]
                - self.payments["employer_contribution"],
                2,
            )
            _events[diff] = _payable

        return _events

    def _payments(self, event=None):
        if event:
            result = self.entries_payment.filter(evento=event).aggregate(
                value=Sum("value"), employer_contribution=Sum("employer_contribution")
            )
        else:
            result = self.entries_payment.aggregate(
                value=Sum("value"), employer_contribution=Sum("employer_contribution")
            )

        result.update(
            value=float(result["value"] or 0.00),
            employer_contribution=float(result["employer_contribution"] or 0.00),
        )
        return result

    @property
    def all_payments(self):
        result = {}
        for ev in list(self._evalute_config_string.keys()):
            result[ev] = self._payments(ev)
        return result

    @property
    def payments(self):
        return self._payments()

    @property
    def paid(self):
        return self.payable["value"] == 0 and self.payable["employer_contribution"] == 0

    @property
    def next_intallment_to_pay(self):
        return (
            self.entries_payment.aggregate(qnt=Sum("installments_paid")).get("qnt") or 1
        )

    @property
    def config_to_next_installment(self):
        installment = self.next_intallment_to_pay
        return self.differences_config.exclude(
            initial_installment__gt=installment
        ).first()

    @property
    def dict_config_strings(self):
        # if not hasattr(self, '_dict_config_strings'):
        gn = self.event.genre_event.genre_number
        self._dict_config_strings = {}
        config_value = (
            self.event.config_value
            if self.event.config_value
            else """MEA:{GN}06.VALOR={DV},{GN}06.PATRONAL={DP};\
               DIF:{GN}01.VALOR={DV},{GN}01.PATRONAL={DP};\
               DEV:{GN}02.VALOR=-{DV},{GN}02.PATRONAL={DP};\
               ESD:{GN}07.VALOR=-{DV},{GN}07.PATRONAL={DP};\
               ESC:{GN}08.VALOR=-{DV},{GN}08.PATRONAL={DP};"""
        )
        for cv in config_value.replace("\n", "").replace(" ", "").split(";"):
            if cv:
                tp, roles = cv.split(":")
                if tp not in self._dict_config_strings:
                    self._dict_config_strings[tp] = []
                for role in (
                    roles.lower().format(gn=gn, dv="{dv}", dp="{dp}").split(",")
                ):
                    if role:
                        self._dict_config_strings[tp].append(role)
        return self._dict_config_strings

    @property
    def config_string(self):
        return self.dict_config_strings.get(self.diff_type, [])

    @property
    def _evalute_config_string(self):
        configs = {}
        dv = float(self.differences["value"])
        dp = float(self.differences["employer_contribution"])

        # log.debug('EVALUATING DIFFS %s : %s DV: %s, DP:%s' % (self.event, self.differences, dv, dp))

        to_prop = {"valor": "value", "patronal": "employer_contribution"}

        for txt in self.config_string:
            res = re.match(
                r"^([0-9]{4,6})\.(valor|patronal)\=(.*)$", txt.replace(" ", "")
            )
            # log.debug(
            #       'EVALUATE: %s: %s' % (
            #           txt, res.groups() if hasattr(res, 'groups') else '>>>>>>>>>> ERRO ON EVALUATE <<<<<<<<<<<'))
            groups = res.groups()
            if len(groups) == 3:
                ev = Evento.objects.filter(numero=groups[0]).first()
                if not ev:
                    raise Exception("Evento de número %s não existe!" % groups[0])
                if ev not in configs:
                    configs[ev] = {"value": 0.0, "employer_contribution": 0.0}
                # log.debug('>>> %s: (dv=%s, dp=%s)' % (groups[2], dv, dp))
                configs[ev][to_prop[groups[1]]] = round(
                    eval(groups[2].format(dv=dv, dp=dp)), 2
                )
            else:
                raise Exception("Sintaxe inválida! Verifique o formato da configuração")

        # log.debug('ECS: %s' % configs)
        # log.debug('EVALUATING DIFFS: %s' % configs)
        for ev in list(configs.keys()):
            if configs[ev]["value"] == 0 and configs[ev]["employer_contribution"] == 0:
                configs.pop(ev)
        return configs

    def create_diff_items(self, entries, correction_factor=1):
        # log.debug(('CD1 1 COUNT: %s' % entries.count())
        totals = entries.aggregate(
            tv=Sum("value"),
            tcv=Sum("correct_value"),
            tdpv=Sum("diff_value_provisioned"),
            tec=Sum("employer_contribution"),
            tcec=Sum("correct_employer_contribution"),
            tdecp=Sum("diff_employer_contribution_provisioned"),
        )

        totals["tv"] = round(totals["tv"] or 0, 2)
        totals["tcv"] = round(totals["tcv"] or 0, 2)
        totals["tdpv"] = round(totals["tdpv"] or 0, 2)
        totals["tec"] = round(totals["tec"] or 0, 2)
        totals["tcec"] = round(totals["tcec"] or 0, 2)
        totals["tdecp"] = round(totals["tdecp"] or 0, 2)

        total_paid = totals["tv"] + totals["tdpv"]
        total_paid_employer = totals["tec"] + totals["tdecp"]
        if total_paid == 0 and totals["tcv"] != 0:  # PAGAMENTO DEVIDO E NÃO EFETUADO
            self.diff_type = "MEA"
        elif totals["tcv"] == 0 and total_paid != 0:  # PAGAMENTO EFETUADO E NÃO DEVIDO
            self.diff_type = "ESC" if self.event.tipo == "D" else "ESD"
        elif abs(totals["tcv"]) > abs(total_paid) or (
            totals["tcv"] == total_paid
            and abs(totals["tcec"]) > abs(total_paid_employer)
        ):
            self.diff_type = "DIF"
        elif abs(totals["tcv"]) < abs(total_paid) or (
            totals["tcv"] == total_paid
            and abs(totals["tcec"]) < abs(total_paid_employer)
        ):
            self.diff_type = "DEV"
        else:
            self.diff_type = "DIF"

        for entry in entries:
            self.difference_items.get_or_create(
                entry_difference=entry,
                defaults={"correction_factor": correction_factor},
            )
            entry.update_provisions()

        self.save()

    def apply_correction_factor(self, ref_payroll_payment):
        if self.correction_factor_identifier:

            params = self.correction_factor_identifier.split(".")
            if len(params) != 2:
                pay_year = ref_payroll_payment.periodo.ano
                pay_month = min(int(ref_payroll_payment.periodo.mes), 12)
            else:
                pay_month = int(params[1][0:2])
                pay_year = int(params[1][2:6])

            for di in self.difference_items.all():
                q_factor = CorrectionFactor.objects.filter(
                    ref_payment_year=pay_year,
                    ref_payment_month=pay_month,
                    ref_difference_year=di.entry_difference.contracheque.folha.periodo.ano,
                    ref_difference_month=min(
                        di.entry_difference.contracheque.folha.periodo.mes, 12
                    ),
                    identifier=params[0],
                )

                factor = q_factor.first().factor if q_factor.exists() else 1.0
                di.correction_factor = factor
                di.save()

    def apply(self, payroll, title="", task=None, recalculate=False):
        addeds = []

        if self.source_differences:
            addeds = self.apply_to(payroll, title, task, recalculate)
        else:
            addeds = self.apply_to2(payroll, title, task, recalculate)

        if addeds:
            if recalculate:
                paycheck = addeds[0].contracheque
                paycheck.recalculate(task=task)
            self.status = 1  # Modificando para status aberto
            self.save()

        return addeds

    def apply_to(self, payroll, title="", task=None, recalculate=False):
        addeds = []
        # log.debug(('APPLY TO: %s:%s' % (self, payroll))
        paycheck, created = self.employee.paychecks.get_or_create(
            folha=payroll, pensioner=None
        )
        if self.correction_factor_identifier:
            self.apply_correction_factor(payroll)
        try:
            entries = self._evalute_config_string
        except Exception as e:
            raise e
        else:
            # log.debug('APPLY TO: %s:%s' % ('teste', entries))
            oids_ = []
            infs = set()

            for di in self.difference_items.all():
                oids_ += di.entry_difference.oIds
                if di.entry_difference.info:
                    infs.add(di.entry_difference.info)
            title_notnull = " - " + title if title else ""
            info = title if not infs else "/ ".join(infs) + title_notnull
            ref_entry = self.difference_items.last().entry_difference

            for event in entries:
                if (
                    entries[event]["value"] != 0
                    or entries[event]["employer_contribution"] != 0
                ):
                    value = entries[event]["value"] / float(self.installments)
                    contrib = entries[event]["employer_contribution"] / float(
                        self.installments
                    )
                    installment = (
                        self.entries_payment.filter(evento=event)
                        .exclude(contracheque=paycheck)
                        .count()
                        + 1
                    )
                    # log.debug(('APLLY TO %s: %s %s %s' % (event, info, self.reference_year, self.reference_month))
                    kwargs = {
                        "evento": event,
                        "info": info,
                        "valor": abs(value),
                        "patronal": contrib,
                        "prazo": self.installments,
                        "parcela": installment,
                        "paycheck_difference": self,
                        "base_previdencia": abs(value),
                        "reference_year": ref_entry.reference_year,
                        "reference_month": ref_entry.reference_month,
                        "rra_employee": self.rra_employee,
                        "diff_type": self.diff_type,
                        "oIds": oids_,
                        "reason_difference": self.reason_difference,
                    }
                    try:
                        fe, created, old_fields = paycheck.update_or_create_entry(
                            False, True, **kwargs
                        )
                    except IntegrityError:
                        raise Exception(
                            "Já tem outro lançamento com essa chave, que tal definir um info (descrição) \
                            ou juntar (apagar o existente e gerar um só)?"
                        )
                    log.debug(
                        "APLLY TO %s: %s:%s >> oIds %s"
                        % (created, fe, old_fields, fe.oIds)
                    )
                    addeds.append(fe)

        return addeds

    def apply_to2(self, payroll, info="", task=None, recalculate=False):
        addeds = []
        # log.debug(('APPLY TO2: %s:%s' % (self, payroll))

        if self.status not in [1, 2, 7]:
            raise self.DifferenceNotApplayable(
                self.identifier, self.get_status_display()
            )

        paycheck, created = self.employee.paychecks.get_or_create(
            folha=payroll, pensioner=None
        )
        calculation = ClassCode.objects.get(slug="mpto-gfp-difference")

        if self.payment_event:
            if (
                self.payment_event.automated
                and self.payment_event.calculation != calculation
            ):
                raise self.DifferenceCalculationIncompatible()

            if self.total_value or self.total_employer_contribution:
                calc = calculation.cls(
                    self.employee,
                    payroll,
                    self.payment_event,
                    difference=self,
                    pensioner=None,
                ).calculate()
                # log.debug(('CALC DIF: %s' % calc)
                fe, created, old_fields = paycheck.update_or_create_entry(
                    False,
                    True,
                    **{
                        "evento": self.payment_event,
                        "info": "DIF%d" % self.pk,
                        "valor": calc.get("valor"),
                        "patronal": calc.get("patronal"),
                        "prazo": calc.get("prazo"),
                        "parcela": calc.get("parcela"),
                        "paycheck_difference": self,
                        "automated": True,
                        "insertion_type": 1,  # Choice id 1 - Tipo de Inserção: Automático
                        "calculation": calculation,
                    },
                )
                # log.debug(('APPLY TO2 %s: %s:%s >> oIds %s %s' % (created, fe, old_fields, fe.oIds, fe.calculation))
                addeds.append(fe)

        return addeds

    def adjust_difference(self):
        if not self.paid:
            pass

    @property
    def total_value_differences(self):
        return 0

    @property
    def total_employer_contribution_differences(self):
        return 0

    def delete(self, *args, **kwargs):

        for fe in self.entries_payment.all():
            fe.delete()

        for di in self.difference_items.all():
            di.delete()

        super(PaycheckDifference, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk and not self.identifier:
            self.identifier = uuid.uuid4().hex

        changed_installments = "installments" in self.old_fields
        self.employer_contribution_to_pay = (
            self.payable["employer_contribution"]
            if self.payable and self.payable["employer_contribution"]
            else 0.0
        )
        self.value_to_pay = (
            self.payable["value"] if self.payable and self.payable["value"] else 0.0
        )

        if self.source_differences:
            totals_di = self.difference_items.aggregate(
                value=Sum("fixed_value"),
                v1=Sum("value"),
                employer_contribution=Sum("fixed_employer_contribution"),
                e1=Sum("employer_contribution"),
            )
            # log.debug(('TDI: %s > %s' % (totals_di, self.payable))
            self.total_value = totals_di["value"] or 0
            self.total_employer_contribution = totals_di["employer_contribution"] or 0

        if self.pk and self.status not in [
            4,
            6,
            7,
        ]:  # [PAGO SEM INFORMAÇÃO ou IGNORADO]
            if self.paid:
                self.status = 5  # PAGO
            elif not self.entries_payment.exists():
                self.status = 1
            elif int(self.installments) > 1:
                self.status = 2  # PAGANDO
            else:
                self.status = 3  # PAGAMENTO PARCIAL

        super(PaycheckDifference, self).save(*args, **kwargs)

        if changed_installments:
            last_installment_config = self.differences_config.order_by(
                "initial_installment"
            ).last()
            if last_installment_config:
                last_installment_config.save()


class PaycheckDifferenceItem(AuditTimestampModel):
    class Meta:
        unique_together = ("difference", "entry_difference")

    difference = models.ForeignKey(
        "PaycheckDifference", related_name="difference_items", on_delete=models.CASCADE
    )
    entry_difference = models.ForeignKey(
        "FolhaEvento", related_name="difference_items", on_delete=models.PROTECT
    )

    value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    paid_value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    fixed_value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0
    )
    paid_employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0
    )
    fixed_employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0
    )
    correction_factor = models.DecimalField(max_digits=19, decimal_places=8, default=1)

    def save(self, *args, **kwargs):
        fe = FolhaEvento.objects.get(pk=self.entry_difference.pk)
        # res = self.entry_difference.differences
        res = fe.differences
        if not self.pk:
            self.value = res.get("valor", 0.0)  # * (-1 if fe.evento.tipo == 'D' else 1)
            self.employer_contribution = res.get("patronal", 0.0)
        # else:
        #     self.value = float(self.value) + res.get('valor', 0.0)  # * (-1 if fe.evento.tipo == 'D' else 1)
        #     self.employer_contribution = float(self.employer_contribution) + res.get('patronal', 0.0)

        self.fixed_value = float(self.value) * float(self.correction_factor)
        self.fixed_employer_contribution = float(self.employer_contribution) * float(
            self.correction_factor
        )

        super(PaycheckDifferenceItem, self).save(*args, **kwargs)
        # log.debug(('PAYCHECK DIFFERENCE ITEM: %s.%s > %s DIF: %s OF: %s PD: %s' % (
        #     fe.pk, fe, fe.folha, res, fe.old_fields, self.difference))

        if self.old_fields:
            self.difference.save()

        #  TODO RETIRAR O SAVE DO FOLHAEVENTO PARA UM SIGNAL
        fe.update_provisions()

    def delete(self, *args, **kwargs):
        super(PaycheckDifferenceItem, self).delete(*args, **kwargs)
        self.entry_difference.update_provisions()


class PaycheckDifferenceConfig(AuditTimestampModel):

    difference = models.ForeignKey(
        "PaycheckDifference",
        related_name="differences_config",
        on_delete=models.CASCADE,
    )
    initial_installment = models.PositiveSmallIntegerField(
        verbose_name="Parcela", default=1
    )
    final_installment = models.PositiveSmallIntegerField(
        verbose_name="Parcela", default=1, blank=True
    )
    value = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0
    )
    typeof = models.PositiveSmallIntegerField(
        verbose_name="Base",
        choices=Choice.get_choices_for("gfp", "TYPE_OF_BASE"),
        default=1,
    )

    class Meta:
        ordering = ("difference", "initial_installment")

    @property
    def next(self):
        return (
            self.difference.differences_config.filter(
                initial_installment__gt=self.initial_installment
            )
            .order_by("initial_installment")
            .first()
        )

    @property
    def previous(self):
        return (
            self.difference.differences_config.filter(
                initial_installment__lt=self.initial_installment
            )
            .order_by("-initial_installment")
            .first()
        )

    def save(self, *args, **kwargs):
        self.final_installment = (
            (self.next.initial_installment - 1)
            if self.next
            else (self.difference.installments or self.initial_installment)
        )
        if self.pk and not self.previous and self.initial_installment != 1:
            self.initial_installment = 1

        save_previous = (
            not self.pk
            or "final_installment" in self.old_fields
            or "initial_installment" in self.old_fields
        )
        super(PaycheckDifferenceConfig, self).save(*args, **kwargs)
        if save_previous and self.previous:
            self.previous.save()

    def delete(self, *args, **kwargs):
        prev = self.previous
        next_ = self.next
        super(PaycheckDifferenceConfig, self).delete(*args, **kwargs)
        if prev:
            prev.save()
        elif next_:
            next_.save()


class LoadedEntryHistory(AuditTimestampModel):

    class Meta:
        unique_together = ("payroll", "identification", "entry", "typeof")

    DEFAULT_USER = "athenas"

    payroll = models.ForeignKey(
        "Folha",
        related_name="loaded_entries",
        verbose_name="Folha",
        on_delete=models.CASCADE,
    )
    typeof = models.CharField(
        max_length=64, verbose_name="Tipo", default="GFP", db_index=True
    )
    identification = models.CharField(
        max_length=64, verbose_name="Identificador", default="", db_index=True
    )
    entry = models.OneToOneField(
        "FolhaEvento",
        related_name="loaded_entry",
        verbose_name="Lançamento",
        null=True,
        on_delete=models.CASCADE,
    )
    line_text = models.CharField(max_length=400, verbose_name="Linha", default="")
    status = models.PositiveSmallIntegerField(
        verbose_name="Status",
        default=1,
        choices=Choice.get_choices_for("gfp", "STATUS_LOADER_OBJ"),
    )


class MarginConsignable(AuditTimestampModel):

    class Meta:
        ordering = ("identification",)

    identification = models.CharField(
        max_length=32, verbose_name="Margem", db_index=True
    )
    title = models.CharField(max_length=64, verbose_name="Título", default="")
    percentage = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    consignables = models.ManyToManyField(
        "Evento", verbose_name="Eventos base", related_name="margins_base"
    )
    consigneds = models.ManyToManyField(
        "Evento", verbose_name="Consignados", related_name="margins_consigneds"
    )
    type_of_payroll = models.ForeignKey(
        "FolhaTipo",
        verbose_name="Tipo de Folha",
        related_name="margins",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(verbose_name="Ativo?", default=False)
    start_validity = models.DateField(
        verbose_name="Início vigência", default=date(1900, 1, 1)
    )
    maximum_installment = models.PositiveSmallIntegerField(
        default=200, verbose_name="Prazo máximo", blank=True
    )
    maximum_cet = models.DecimalField(
        max_digits=19, decimal_places=2, default=5, verbose_name="CET máximo"
    )

    def __str__(self):
        return "%s - %s (%0.2f%%)" % (self.title, self.type_of_payroll, self.percentage)


class MarginPaycheck(models.Model):

    class Meta:
        unique_together = (("paycheck", "margin"),)

    paycheck = models.ForeignKey(
        "Contracheque",
        verbose_name="Contracheque",
        related_name="margin_paychecks",
        on_delete=models.CASCADE,
    )
    margin = models.ForeignKey(
        "MarginConsignable",
        verbose_name="Margem",
        related_name="margin_paychecks",
        on_delete=models.CASCADE,
    )
    total_value = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    value = models.DecimalField(max_digits=19, decimal_places=2, default=0)

    def __str__(self):
        return "%0.2f/%0.2f - %s" % (self.total_value, self.value, self.margin)


class OverviewReport(AuditTimestampModel):
    DEFAULT_USER = "athenas"

    payroll = models.ForeignKey(
        Folha,
        verbose_name="Folha",
        related_name="overview_summary",
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        Evento,
        verbose_name="Evento",
        related_name="overview_summary",
        on_delete=models.CASCADE,
    )
    type_of_employee = models.PositiveSmallIntegerField(verbose_name="Tipo", default=1)
    value = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, verbose_name="Valor total"
    )
    employer_contribution = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, verbose_name="Patronal total"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantidade")
    type_of_entry = models.PositiveSmallIntegerField(
        default=1, verbose_name="Tipo de Lançamento"
    )
    reference_year = models.PositiveSmallIntegerField(
        default=2020, verbose_name="Exercicio"
    )

    def save(self, *args, **kwargs):
        if not self.reference_year:
            self.reference_year = self.payroll.periodo.ano
        super(OverviewReport, self).save(*args, **kwargs)


class FinancialReportPayroll(AuditTimestampModel):

    DEFAULT_USER = "athenas"

    payroll = models.ForeignKey(
        Folha,
        verbose_name="Folha",
        related_name="financial_summary",
        on_delete=models.CASCADE,
    )
    account_plan = models.ForeignKey(
        "planoconta.PlanoConta",
        on_delete=models.CASCADE,
        verbose_name="PlanoConta",
        related_name="financial_summary",
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantidade")
    value = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, verbose_name="Valor total"
    )
    reference_year = models.PositiveSmallIntegerField(
        default=2020, verbose_name="Exercicio"
    )

    class Meta:
        unique_together = (("payroll", "account_plan", "reference_year"),)

    def save(self, *args, **kwargs):
        if not self.reference_year:
            self.reference_year = self.payroll.periodo.ano
        super(FinancialReportPayroll, self).save(*args, **kwargs)


class SocialSecurityContributionsReport(AuditTimestampModel):

    DEFAULT_USER = "athenas"

    payroll = models.ForeignKey(
        Folha, verbose_name="Folha", related_name="+", on_delete=models.CASCADE
    )
    mass_segregation_plan = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("rh", "MASS_SEGREGATION_PLAN"),
        null=True,
        blank=True,
    )
    regime = models.PositiveSmallIntegerField(
        "Regime Previdenciário",
        default=2,
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
    )
    type_by_possession = models.CharField(
        default="EFE",
        max_length=5,
        blank=True,
        choices=Choice.get_choices_for(
            "rh", "CLASSIF_EMPLOYEE_BY_POSSESSION", char_field=True
        ),
        verbose_name="Tipo do Servidor",
    )
    employee_quantity = models.IntegerField(verbose_name="Qtd. Servidores")
    dependents_quantity = models.IntegerField(verbose_name="Qtd. Dependentes")
    remuneration_total = models.FloatField(verbose_name="Remuneração Total")
    employee_base_calculation = models.FloatField(verbose_name="Base Cálculo Servidor")
    employee_contribution = models.FloatField(verbose_name="Contribuição Servidor")
    employer_base_calculation = models.FloatField(verbose_name="Base Cálculo Patronal")
    employer_contribution = models.FloatField(verbose_name="Contribuição Patronal")


class EmployersSummaryReport(AuditTimestampModel):
    pass


class BankingConvenant(models.Model):
    """Classe para manipular os convênios bancarios que geram arquivos de creditos.

    Attributes:
        bank (BANK): Banco do convenio
        convenant (CHAR): Identificador do canvenio
        generator (CLASSCODE): ClassCode do gerador de arquivo de credito
        identification (CHAR): Identificador humanizavel
    """

    identification = models.CharField(
        max_length=64, verbose_name="Identificador", default="", db_index=True
    )
    bank = models.ForeignKey("rh.Banco", verbose_name="Banco", on_delete=models.CASCADE)
    convenant = models.CharField(max_length=64, verbose_name="Convênio", db_index=True)
    generator = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Gerador",
        related_name="banking_conventants",
        on_delete=models.SET_NULL,
    )
    counter = models.PositiveIntegerField(
        verbose_name="Contador", default=1, blank=True
    )
    active = models.BooleanField(verbose_name="Ativo?", default=True)
    type_convenant = models.PositiveSmallIntegerField(
        verbose_name="Tipo Conênio",
        default=2,
        choices=Choice.get_choices_for("gfp", "TYPE_BANK_CONVENANT"),
    )
    agency_cod = models.CharField(max_length=4, verbose_name="Agência")
    agency_cod_dv = models.CharField(max_length=2, verbose_name="Agência/DV")
    account_cod = models.CharField(max_length=20, verbose_name="Conta")
    account_cod_dv = models.CharField(max_length=1, verbose_name="Conta/DV")
    chave_pix = models.CharField(
        max_length=50, verbose_name="Chave PIX", null=True, blank=True
    )

    excluded_bank = models.ManyToManyField(
        "rh.Banco", verbose_name="Bancos excluídos", related_name="excluded_bank"
    )

    class Meta:
        ordering = ("bank__numero", "identification")

    def __str__(self):
        """Unicode para o objeto.

        Returns:
            CHAR: Identificador do objeto
        """
        return "%s" % self.identification


class RemunerationBaseQuerySet(models.QuerySet):
    def of_employee(self, employee):
        return self.filter(employee=employee)

    def of_period(self, period):
        return self.filter(periods__period=period).distinct()

    def of_period_create(self, period, create=None):
        if create:
            from rh.gfp.signals.remuneration_base import (
                generate_remunerations_by_employee,
            )

            [
                generate_remunerations_by_employee(x.employee, period)
                for x in self.select_related("employee").distinct()
            ]
        return self.filter(periods__period=period).distinct()

    def periods(self):
        return RemunerationPeriod.objects.filter(remuneration__in=self)

    def objects(self):
        return ["%s%s" % (x.link, x.identifier) for x in self]

    def extras(self):
        return self.filter(link="EX")

    def only_with_onus(self):
        return self.filter(onus=True)

    def ordered_by_link(self):
        links = ["EF", "AC", "CM", "SM", "FC", "EL", "EX"]
        clauses = " ".join(
            ["WHEN link='%s' THEN %s" % (link, i) for i, link in enumerate(links)]
        )
        ordering = "CASE %s END" % clauses
        return self.extra(select={"ordering": ordering}, order_by=("ordering",))

    def lasts(self):
        qs = self.order_by("link", "-periods__start").distinct("link").values("pk")
        return self.filter(pk__in=qs)


class RemunerationBase(models.Model):

    employee = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    identifier = models.CharField("Identificador", max_length=10)
    link = models.CharField("Tipo", max_length=2)
    salary = models.PositiveIntegerField("Referência Salário", null=True)
    base_gratification = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    base_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    percentage = models.BooleanField("Porcentagem", default=False)
    onus = models.BooleanField("Ônus", default=False)

    objects = RemunerationBaseQuerySet.as_manager()

    def __str__(self):
        return "{0} - {1}, {2}".format(self.salary, self.identifier, self.link)

    def days_by_period(self, period):
        return self.periods.of_period(period).aggregate(Sum("days"))["days__sum"]

    @staticmethod
    def clear(employee=None, period=None):
        # log.debug(('CLEAR PERIODS AND BASE REMUNERATION BY %s %s' % (employee, period))
        q_remove = RemunerationPeriod.objects.all()
        if employee:
            q_remove = q_remove.filter(remuneration__employee=employee)
        if period:
            q_remove = q_remove.filter(period=period)
        q_remove.delete()
        RemunerationBase.objects.annotate(qp=Count("periods")).filter(qp=0).delete()


class RemunerationPeriodQueryset(models.QuerySet):
    def of_period(self, period):
        return self.filter(period=period)

    def of_employee(self, employee):
        return self.filter(remuneration__employee=employee)


class RemunerationPeriod(models.Model):
    remuneration = models.ForeignKey(
        RemunerationBase,
        related_name="periods",
        default=None,
        null=True,
        on_delete=CASCADE,
    )
    start = models.DateField("Início do Período")
    end = models.DateField("Final do Período")
    period = models.ForeignKey(Periodo, null=True, on_delete=models.CASCADE)
    gratification = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    value = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    normal_gratification = models.DecimalField(
        max_digits=20, decimal_places=6, default=0
    )
    normal_value = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    base_gratification = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    base_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    days = models.PositiveIntegerField("Dias", default=0)

    objects = RemunerationPeriodQueryset.as_manager()

    class Meta:
        ordering = ("-start", "remuneration__identifier")

    def __str__(self):
        return "{0}-{1}, {2}({3})".format(
            self.start.day,
            self.end.day,
            self.period,
            self.remuneration.employee.pessoa_fisica.nome,
        )

    def range_period(self):
        return NewDateRange(self.start, self.end)


class FamilySalary(models.Model):
    publication = models.ForeignKey(
        Publicacao,
        verbose_name="Publicação",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "{0} - Vigência Inicio: {1}".format(
            self.description,
            self.start_date.strftime("%d/%m/%Y"),
        )


class FamilySalaryRange(models.Model):
    inferior_limit = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Inferior"
    )
    upper_limit = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Superior"
    )
    value = models.DecimalField(verbose_name="Valor", max_digits=16, decimal_places=2)
    family_salary = models.ForeignKey(
        FamilySalary,
        verbose_name="Salário Familia",
        related_name="ranges",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Faixa de {0} até {1} para {2}".format(
            self.inferior_limit, self.upper_limit, self.value
        )


class PeriodPayroll(models.Model):
    month = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS"), null=True, blank=True
    )
    year = models.PositiveIntegerField("Ano", null=True, blank=True)
    qtd_diff = models.PositiveIntegerField("Qtd Diferença", null=True, blank=True)
    qtd_diff_applied = models.PositiveIntegerField(
        "Qtd Dif. Aplicada", null=True, blank=True
    )
    qtd_diff_ignored = models.PositiveIntegerField(
        "Qtd Dif. Ignorada", null=True, blank=True
    )
    calculate_last_date = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )
    folha = models.ForeignKey(
        Folha,
        verbose_name="Folha",
        related_name="folha_period_payrolls",
        on_delete=models.PROTECT,
        null=True,
    )

    class Meta:
        unique_together = ("month", "year")
        ordering = ("-year", "-month")

    def __str__(self):
        return f"{self.month}/{self.year}"

    def validate_if_same_period_exists(self):
        if PeriodPayroll.objects.filter(folha=self.folha).exists():
            raise Exception("Já existe um período com esse mês e ano.")

    def validate(self):
        if self.pk is None:
            self.validate_if_same_period_exists()

    def full_clean(self):
        pass

    def save(self, *args, **kwargs):
        self.validate()

        super(PeriodPayroll, self).save(*args, **kwargs)


class DifferencePayroll(models.Model):
    types_status = (
        ("AVAL", "Avaliar"),
        ("APLI", "Aplicado"),
        ("IGNO", "Ignorado"),
    )

    types_diff = (
        ("DESC", "Desconto"),
        ("PROV", "Provimento"),
    )

    period = models.ForeignKey(
        PeriodPayroll,
        related_name="period_differences_payroll",
        on_delete=models.PROTECT,
    )
    employee = models.ForeignKey(
        Servidor,
        verbose_name="Servidor",
        related_name="employee_differences_payroll",
        on_delete=models.PROTECT,
    )
    event = models.ForeignKey(
        Evento,
        verbose_name="Evento",
        related_name="event_differences_payroll",
        on_delete=models.PROTECT,
    )
    paycheck_event = models.ForeignKey(
        ContraCheque,
        verbose_name="Contra Cheque",
        related_name="paycheck_differences_payroll",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    qtd_event = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    qtd_max_event = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    correct_value_event = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    base_value_event = models.DecimalField(
        "Valor Base - Origem",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    installment_paid_event = models.PositiveIntegerField(
        "Parcela - Origem", null=True, blank=True, default=0
    )
    installments_event = models.PositiveIntegerField(
        "Prazo - Origem", null=True, blank=True, default=0
    )
    pct_event = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True, default=0
    )
    info_event = models.CharField(max_length=150, default="")
    contribution_base_event = models.DecimalField(
        "Base Previdenciária - Origem",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    employer_value_event = models.DecimalField(
        "Patronal - Origem",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    qtd_diff = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    qtd_max_diff = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    correct_value_diff = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    value_diff = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    event_diff = models.ForeignKey(
        Evento,
        verbose_name="Evento de Diferença",
        related_name="event_diff_differences_payroll",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    base_value_diff = models.DecimalField(
        "Valor Base - Diferença",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    installment_paid_diff = models.PositiveIntegerField(
        "Parcela - Diferença", null=True, blank=True, default=0
    )
    installments_diff = models.PositiveIntegerField(
        "Prazo - Diferença", null=True, blank=True, default=0
    )
    pct_event_diff = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True, default=0
    )
    contribution_base_diff = models.DecimalField(
        "Base Previdenciária - Diferença",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    employer_value_diff = models.DecimalField(
        "Patronal - Diferença",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    info_diff = models.CharField(max_length=150, default="")
    paycheck_applied = models.ForeignKey(
        ContraCheque,
        verbose_name="Contra Cheque - Aplicado",
        related_name="paycheck_applied_differences_payroll",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    status = models.CharField(max_length=4, choices=types_status, default="AVAL")
    type_diff = models.CharField(
        max_length=4, choices=types_diff, null=True, blank=True
    )
    from_others_diffs = models.BooleanField(
        verbose_name="Vinculado à outras diferenças", default=False
    )
    created_at = models.DateTimeField(verbose_name="Criado Em", auto_now_add=True)

    class Meta:
        ordering = ("-period", "employee", "event", "-created_at")

    def update_period_payroll_stats(self, period):
        qtd_diff_count = period.period_differences_payroll.count()
        qtd_diff_applied_count = period.period_differences_payroll.filter(
            status="APLI"
        ).count()
        qtd_diff_ignored_count = period.period_differences_payroll.filter(
            status="IGNO"
        ).count()

        period.qtd_diff = qtd_diff_count
        period.qtd_diff_applied = qtd_diff_applied_count
        period.qtd_diff_ignored = qtd_diff_ignored_count

        period.save()

    def save(self, *args, **kwargs):
        super(DifferencePayroll, self).save(*args, **kwargs)
        self.update_period_payroll_stats(self.period)

    @property
    def qtd_normalize(self):
        if self.qtd_event is None:
            return 0

        if self.qtd_event == self.qtd_max_event:
            return str(int(self.qtd_event))
        else:
            return f"{int(self.qtd_event)}/{int((self.qtd_max_event))}"

    @property
    def qtd_diff_normalize(self):
        if self.qtd_diff is None:
            return 0

        if self.qtd_diff == self.qtd_max_diff:
            return str(int(self.qtd_diff))
        else:
            return f"{int(self.qtd_diff)}/{int(self.qtd_max_diff)}"

    @property
    def payroll_event(self):
        if self.paycheck_event:
            return str(self.paycheck_event.folha)
        else:
            return ""

    @property
    def payroll_applied(self):
        return str(self.paycheck_applied.folha) if self.paycheck_applied else ""

    @property
    def event_info(self):
        return (
            f"{self.event}: {self.info_event}" if self.info_event else str(self.event)
        )

    @property
    def diff_info(self):
        return (
            f"{self.event_diff}: {self.info_diff}"
            if self.info_diff
            else str(self.event_diff)
        )

    def __str__(self):
        return f"{self.period} - {self.employee} - {self.event_info} - {self.get_type_diff_display()}"


class ConferencePayroll(models.Model):
    created_by = models.ForeignKey(
        Servidor,
        blank=True,
        null=True,
        verbose_name="Criado Por",
        related_name="created_conference_payroll",
        on_delete=models.PROTECT,
    )
    finished_by = models.ForeignKey(
        Servidor,
        blank=True,
        null=True,
        verbose_name="Finalizado Por",
        related_name="finished_conference_payroll",
        on_delete=models.PROTECT,
    )
    payroll = models.OneToOneField(
        Folha,
        verbose_name="Folha",
        related_name="payroll_conference",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(verbose_name="Criado Em", auto_now_add=True)
    finished_at = models.DateTimeField(
        verbose_name="Finalizado Em",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.created_by} - {self.payroll}"

    @property
    def payroll_pendencies(self):
        """
            Propriedade que calcula a porcentagem da confêrencia de folha
        Returns:
            percent:(float)
        """
        percent = 0
        total_event_payroll = self.conference_payroll.filter().count()
        checked_event_payroll = self.conference_payroll.filter(checked=True).count()
        if checked_event_payroll and total_event_payroll:
            percent = (checked_event_payroll * 100) / total_event_payroll
        return percent

    def finish(self):
        """Função que finaliza a confêrencia de folha"""
        if not self.finished_by:
            self.finished_by = employee_from_user(get_current_user())
            self.finished_at = datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = employee_from_user(get_current_user())
        super(ConferencePayroll, self).save(*args, **kwargs)


class ConferenceEventPayroll(models.Model):
    conference = models.ForeignKey(
        ConferencePayroll,
        verbose_name="Conferência Folha",
        related_name="conference_payroll",
        on_delete=models.CASCADE,
    )
    event_payroll_previous = models.ForeignKey(
        FolhaEvento,
        blank=True,
        null=True,
        verbose_name="Folha Evento Anterior",
        related_name="conference_event_payroll_previous",
        on_delete=models.SET_NULL,
    )
    event_payroll_current = models.ForeignKey(
        FolhaEvento,
        blank=True,
        null=True,
        verbose_name="Folha Evento Atual",
        related_name="conference_event_payroll_current",
        on_delete=models.SET_NULL,
    )
    event_paycheck_previous = models.ForeignKey(
        ContraCheque,
        blank=True,
        null=True,
        verbose_name="Contracheque Anterior",
        related_name="conference_event_paycheck_previous",
        on_delete=models.SET_NULL,
    )
    event_paycheck_current = models.ForeignKey(
        ContraCheque,
        blank=True,
        null=True,
        verbose_name="Contracheque Atual",
        related_name="conference_event_paycheck_current",
        on_delete=models.SET_NULL,
    )
    checked = models.BooleanField(default=False, verbose_name="Conferido")

    def __str__(self):
        return f"{self.conference}"


class RemunerationRelationship(ListDatedModel, AuditTimestampModel):
    """Relação de múltiplos vínculos pagadores do servidor"""

    OVERLAP_FIELDS = ["employee", "person_payer", "start_validity"]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    employee = models.ForeignKey(
        Servidor,
        on_delete=models.CASCADE,
        verbose_name="Servidor",
        related_name="remunerationrelationship",
    )
    person_payer = models.ForeignKey(
        Pessoa,
        verbose_name="Fonte pagadora",
        on_delete=models.PROTECT,
        related_name="remunerationrelationship",
    )
    category_esocial = models.IntegerField(
        verbose_name="Categoria eSocial",
        choices=Choice.get_choices_for("rh", "CATEGORY_WORKER"),
    )
    remuneration = models.DecimalField("Remuneração", max_digits=14, decimal_places=2)
    inss_value = models.DecimalField("Valor do INSS", max_digits=14, decimal_places=2)
    attachment = models.ForeignKey(
        Arquivo,
        related_name="remunerationrelationship",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    order = models.PositiveSmallIntegerField("Ordem", null=True, blank=True)
    protocol = models.CharField("Número do EDOC", max_length=50, null=True, blank=True)

    class Meta:
        ordering = ("-start_validity",)

    def __str__(self):
        end_validity = (
            DateUtils.date_to_str(self.end_validity) if self.end_validity else "----"
        )
        return f"{self.employee} - {self.person_payer} - {DateUtils.date_to_str(self.start_validity)} {end_validity}"

    def validate(self):
        natural_person = getattr(self.person_payer, "pessoafisica", None)
        legal_person = getattr(self.person_payer, "pessoajuridica", None)

        if not natural_person and not legal_person:
            raise Exception("Escolha uma pessoa física ou jurídica.")
        elif natural_person and natural_person.cpf is None:
            raise Exception("A pessoa física deve possuir CPF.")
        elif legal_person and legal_person.cnpj is None:
            raise Exception("A pessoa física deve possuir CNPJ.")

        if self.category_esocial == 1:
            raise Exception("Escolha um valor válido.")

        if not self.inss_value and not self.ordem:
            raise Exception(
                "Caso não possua Valor do INSS deve ser informada a Ordem para cálculo."
            )

        return True

    def save(self, *args, **kargs):
        self.validate()
        super().save(*args, **kargs)


auditlog.register(ConfigEvent)
auditlog.register(Evento)
auditlog.register(SpecieEvent)
auditlog.register(GenreEvent)
auditlog.register(ExtraPayment)
auditlog.register(ExtraPaymentPeriod)
auditlog.register(MovimentacaoProgressao)
auditlog.register(Folha)
auditlog.register(FolhaModelo)
auditlog.register(
    ContraCheque,
    include_fields=["dado_bancario_pessoa", "total_bruto", "total_liquido", "status"],
)
