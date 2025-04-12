# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.ferias.models import (
    PAS_ALIBERACAO,
    PAS_EMANDAMENTO,
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorUsufruto,
)
from rh.gfp.calcs.mpto.remuneracao import BaseSalary
from standard.models import RunCodeManager

log = getLogger(__name__)


class BaseVacation(BaseSalary):
    title = "Base de cálculo para Férias"
    description = """
        Este calculo pode ser usado como base para os cálculos de férias.
        O redutor será aplicado ao valor do cálculo.
    """
    FULL_SALARY = True
    FULL_VALUE = True
    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    EVALUATE_ON_REFERENCE_PAYROLL = True
    EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {}

    def configure(self):
        range_indemnity = NewDateRange(date(2016, 1, 1), date(2017, 8, 31))
        dt = date(self.range_salary.first.year, self.range_salary.first.month, 1)
        if self.object and range_indemnity.in_range(dt):
            self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {"M": ["CM", "EL"]}

    @property
    def ceiling(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )

    @property
    def references(self):
        # log.debug('REFERENCES: %s/%s' % (self.range_salary.first.month, self.range_salary.first.year))
        return (self.range_salary.first.year, self.range_salary.first.month)

    def quantity(self):
        # qnt = super(self.__class__, self).get_query()
        qnt = 1

        # if self.employee.data_desligamento:
        #     qnt = 0
        #     date_ranges = self.object
        #     related = relativedelta(date_ranges.data_inicio_aquisicao, self.employee.data_desligamento)
        #     qnt += related.months
        #     qnt += 1 if related.days >= 15 else 0

        return qnt

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-mpto-additional-vacation")
class AdditionalVacation(BaseVacation):
    title = "Adicional de Férias"
    description = "Cálculo para adicional de férias"

    JOIN_ON_MULTI = False
    FORCE_PAID_VALUE = [
        "00800",
    ]
    FORCE_FULL_VALUE = []

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):

        super(AdditionalVacation, self).__init__(
            employee, payroll, event, entry, cid=cid, **kwargs
        )

        if self.object and (
            self.object.data_inicio.year != self.year
            or self.object.data_inicio.month != self.month
        ):
            # log.debug('entrou no if pra redefinir range salary')
            self.range_salary = NewDateRange.from_month(
                self.object.data_inicio.year, self.object.data_inicio.month
            )
            self.validity = self.range_salary
        # log.debug(self.range_salary)

    @property
    @cache_return
    def range_vacation_enjoyment(self):
        date_lastday_month = self.range_salary.last + relativedelta(days=1)
        date_firstday_month = self.range_salary.first + relativedelta(days=-1)
        range_vacation_enjoyment = (
            self.range_salary
            + NewDateRange.from_month(date_lastday_month.year, date_lastday_month.month)
            + NewDateRange.from_month(
                date_firstday_month.year, date_firstday_month.month
            )
        )
        return range_vacation_enjoyment

    @property
    def valid_states_for_payment(self):
        return [4, 8, 32, 128, 256]

    def _get_base_query(self):
        query = PeriodoAquisitivoServidorUsufruto.objects.filter(
            models.Q(periodo_aquisitivo_servidor__servidor=self.employee)
            & models.Q(estado__in=self.valid_states_for_payment)
            & models.Q(data_inicio__gte=self.range_vacation_enjoyment.first)
            & models.Q(data_inicio__lte=self.range_vacation_enjoyment.last)
            & (
                models.Q(
                    periodo_aquisitivo_servidor__pago_sem_folha=False,
                    periodo_aquisitivo_servidor__folha_evento_terco_constitucional=None,
                )
                | models.Q(
                    periodo_aquisitivo_servidor__folha_evento_terco_constitucional__contracheque__folha=self.payroll,
                    periodo_aquisitivo_servidor__folha_evento_terco_constitucional__evento=self.event,
                )
            )
        )
        return query

    def _get_query(self):

        pas_ = []
        exclude_pks = [
            fe.oIds[0]
            for fe in self.employee.entries.filter(
                evento=self.event, folha__dt_pagamento__lte=self.payroll.dt_pagamento
            )
            if fe != self.entry and fe.oIds and fe.oIds[0] != ""
        ]
        if self.params.get("oIds", []):
            query = PeriodoAquisitivoServidorUsufruto.objects.filter(
                pk__in=self.params.get("oIds", [])
            )
            if not self.payroll.is_processed:
                query = query.filter(models.Q(estado__in=self.valid_states_for_payment))
        else:
            query = self._get_base_query()
            for pasu in query.order_by("periodo_aquisitivo_servidor", "data_inicio"):
                if pasu.pas in pas_:
                    exclude_pks.append(pasu.pk)
                pas_.append(pasu.pas)

        for pasu in query.order_by("periodo_aquisitivo_servidor", "data_inicio"):
            if (
                pasu.pas.folha_evento_terco_constitucional
                and pasu.pas.folha_evento_terco_constitucional != self.entry
            ):
                exclude_pks.append(pasu.pk)
        if exclude_pks:
            query = query.exclude(pk__in=exclude_pks)
        # log.debug('%s:%s' % (exclude_pks, [pasu.pk for pasu in query]))
        return query

    def percentage(self):
        if self.object:
            pas = self.object.pas
            if (
                pas.data_fim_aquisicao >= date(2018, 6, 12)
                or pas.periodo_aquisitivo.ano_aquisicao < 2012
            ):
                return 33.3333333333
            return 50.0
        return 0.0

    def maximum_quantity(self):
        return 1.0

    def quantity(self):
        return len(self.get_query())

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.payroll.status in [3, 4] and not self.entry:
            txt = "O evento não pode ser adicionado em uma folha fechada."
            raise self.CalculationNotApplicable(txt)
        if not self.get_query():
            txt = (
                "O(A) servidor(a) %s não possui usufrutos compatíveis com esse tipo de adicional de\
                    férias no período de %s a %s"
                % (
                    self.employee,
                    self.range_vacation_enjoyment.first.strftime("%d/%m/%Y"),
                    self.range_vacation_enjoyment.last.strftime("%d/%m/%Y"),
                )
            )
            raise self.CalculationNotApplicable(txt)

    def callback(self, **kargs):
        # log.debug('CALLBACK')
        super(AdditionalVacation, self).callback(**kargs)
        # log.debug('>>>> CALLBACK CALC FERIAS: {}'.format(kargs.get('entry')))
        # for key in kargs:
        #     # log.debug('%s %s' % (key, kargs.get(key)))

        ups1 = ups2 = 0
        if "entry" in kargs:
            # Desmarcando PASs que não serão mais pagos no folha_evento calculado
            ups1 = PeriodoAquisitivoServidor.objects.filter(
                folha_evento_terco_constitucional=kargs["entry"]
                # ).exclude(
                #     pk__in=[p.pas.pk for p in self.get_query()]
            ).update(folha_evento_terco_constitucional=None)

            # Marcando PASs que serão pagos no folha_evento calculado, caso o calculo não seja zerado (R$ 0,00)
            if round(self.valor(), 2) > 0:
                ups2 = (
                    PeriodoAquisitivoServidor.objects.filter(
                        pk__in=[p.pas.pk for p in self.get_query()]
                    )
                    .exclude(folha_evento_terco_constitucional=kargs["entry"])
                    .update(folha_evento_terco_constitucional=kargs["entry"])
                )

            # log.debug('>>>> CALLBACK for %s DESMARCADOS: %s MARCADOS: %s' % (self.__class__.__name__, ups1, ups2))

    def event_information(self):
        return "%s" % self.object.pas.periodo_aquisitivo if self.object else ""

    def base_socialsecurity(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        return self.value()


@RunCodeManager.register("gfp-mpto-additional-vacation-ii")
class AdditionalVacationII(AdditionalVacation):

    CAN_UPDATE_CID = True

    def _get_query(self):

        pas_ = []
        # valid_states = [4, 8, 16, 32, 128, 256]
        oIds = self.params.get("oIds", [])
        exclude_pks = set([])
        for fe in self.employee.entries.filter(evento=self.event):
            if fe != self.entry:
                if fe.oIds and fe.oIds[0] != "":
                    exclude_pks = exclude_pks.union(set(fe.oIds))

        query = self._get_base_query()

        for pasu in query.order_by("periodo_aquisitivo_servidor", "data_inicio"):
            if pasu.pk not in oIds and (
                pasu.pas in pas_
                or pasu.pas.folha_evento_terco_constitucional
                and pasu.pas.folha_evento_terco_constitucional != self.entry
            ):
                exclude_pks.add(pasu.pk)
            pas_.append(pasu.pas)

        if exclude_pks:
            query = query.exclude(pk__in=exclude_pks)

        if oIds and oIds[0] and query.filter(pk__in=oIds):
            query = query.filter(pk__in=oIds)

        return query

    @property
    def valid_states_for_payment(self):
        valids = [4, 8, 32, 128, 256]
        if self.payroll.is_processed and self.entry and self.entry.status == "CT":
            valids.append(
                64
            )  # Adicionando estado PASU_SUSPENSO para quem ja tinha sido pago
            if self.employee.tipo == "M":
                valids.append(16)  # Adicionando estado PASU_ALTERADO para membros
        return valids

    @property
    @cache_return
    def range_vacation_enjoyment(self):
        all_range = NewDateRange()

        m_anterior = self.range_salary.first - relativedelta(days=1)
        m_anterior = NewDateRange.from_month(m_anterior.year, m_anterior.month)
        all_range.add_range(m_anterior.first, m_anterior.last)

        m_atual = self.range_salary
        all_range.add_range(m_atual.first, m_atual.last)

        m_prox = self.range_salary.last + relativedelta(days=1)
        m_prox = NewDateRange.from_month(m_prox.year, m_prox.month)
        all_range.add_range(m_prox.first, m_prox.last)

        # date_lastday_month = self.range_salary.last + relativedelta(days=1)
        # range_vacation_enjoyment = NewDateRange.from_month(date_lastday_month.year, date_lastday_month.month)
        # return range_vacation_enjoyment

        return all_range


@RunCodeManager.register("gfp-mpto-unused-vacation")
class RescissionUnusedVacation(BaseVacation):

    title = "Férias Vencidas"
    description = "Cálculo de acerto para férias vencidas"

    # FULL_SALARY = True
    JOIN_ON_MULTI = False
    IGNORE_DEPARTURE = True

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        last_date = (
            employee.last_day_worked or payroll.date_range.last
        )  # ULTIMO DIA TRABALHADO

        kwargs["year"] = (
            last_date.year if employee.data_desligamento else payroll.periodo.ano
        )
        kwargs["month"] = (
            last_date.month if employee.data_desligamento else payroll.periodo.mes
        )
        # log.debug(kwargs)
        super(RescissionUnusedVacation, self).__init__(
            employee, payroll, event, entry, cid=cid, **kwargs
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.last_day_worked
            and self.month != self.employee.last_day_worked.month
            and self.year != self.employee.last_day_worked.year
        ):
            raise self.CalculationNotApplicable(
                "O pagamento de férias vencidas não pode ser pago em mês diferente do desligamento."
            )
        if (
            not self.employee.last_day_worked
            or self.employee.situacao_funcional_cache in ["INATIVO_DEVOLVIDO"]
        ):
            raise self.CalculationNotApplicable(
                "O Servidor %s não está desligado" % (self.employee)
            )

    def quantity(self):
        return self.object.days_not_enjoyed if self.object else 0

    def maximum_quantity(self):
        return (
            self.object.periodo_aquisitivo.configuracao.dias_por_periodo
            if self.object
            else 1.0
        )

    def _get_query(self):
        if self.params.get("oIds"):
            return self.employee.periodos_aquisitivos.filter(
                pk__in=self.params.get("oIds")
            )
        else:
            if self.employee.data_desligamento:
                return self.employee.periodos_aquisitivos.filter(
                    models.Q(estado__in=[PAS_ALIBERACAO, PAS_EMANDAMENTO])
                    & models.Q(bloqueado=False)
                    & models.Q(data_fim_aquisicao__lt=self.employee.data_desligamento)
                )
        return []

    def event_information(self):
        return "%s" % self.object.periodo_aquisitivo if self.object else ""

    def callback(self, **kargs):
        from rh.ferias.models import PeriodoAquisitivoServidor

        # log.debug('>>>>> CALLBACKs')
        # for karg in kargs:
        #     # log.debug('>>>>> CALLBACK: %s' % karg)

        # log.debug('>>>> CALLBACK CALC FERIAS: %s' % [p.pas.id for p in self.pasus])
        if "entry" in kargs:
            q_pas = PeriodoAquisitivoServidor.objects.filter(pk__in=kargs["entry"].oIds)
            for pas in q_pas:
                # log.debug('>>>>> CALLBACK %s >> %s' % (kargs['entry'].oIds, pas.get_estado_display()))
                pas._indenizar()


@RunCodeManager.register("gfp-mpto-unused-vacation-ii")
class RescissionUnusedVacationII(RescissionUnusedVacation):

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.last_day_worked
            and self.month != self.employee.last_day_worked.month
            and self.year != self.employee.last_day_worked.year
        ):
            raise self.CalculationNotApplicable(
                "O pagamento de férias vencidas não pode ser pago em mês diferente do desligamento."
            )
        if not self.employee.last_day_worked:
            raise self.CalculationNotApplicable(
                "O Servidor %s não está desligado" % (self.employee)
            )

    @property
    def ceiling_base_value(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )


@RunCodeManager.register("gfp-mpto-additional-unused-vacation")
class RescissionAdditionalUnusedVacation(RescissionUnusedVacationII):

    title = "Adicional de Férias Vencidas"
    description = "Cáculo de acerto para adicional de férias vencidas"

    MULTI_CALCULATE = True

    def _get_query(self):
        # query = super(RescissionAdditionalUnusedVacation, self)._get_query()
        query = self.employee.periodos_aquisitivos.filter(
            models.Q(bloqueado=False)
            & models.Q(data_fim_aquisicao__lt=self.employee.data_desligamento)
            & models.Q(folha_evento_terco_constitucional=None)
        )
        if self.params.get("oIds"):
            return self.employee.periodos_aquisitivos.filter(
                pk__in=self.params.get("oIds")
            )

        return query.exclude(
            models.Q(pago_sem_folha=True)
            | ~models.Q(folha_evento_terco_constitucional=None)
        )

    def percentage(self):
        if self.object:
            pas = self.object.pas
            if (
                pas.data_fim_aquisicao >= date(2018, 6, 12)
                or pas.periodo_aquisitivo.ano_aquisicao < 2012
            ):
                return 33.3333333333
            return 50.0
        return 0.0

    def callback(self, **kargs):
        from rh.ferias.models import PeriodoAquisitivoServidor

        # log.debug('>>>>> CALLBACKs')
        # for karg in kargs:
        #     # log.debug('>>>>> CALLBACK: %s' % karg)
        # log.debug('>>>> CALLBACK CALC FERIAS: %s' % [p.pas.id for p in self.pasus])
        if "entry" in kargs:
            # Desmarcando PASs que não serão mais pagos no folha_evento calculado
            ups1 = (
                PeriodoAquisitivoServidor.objects.filter(
                    folha_evento_terco_constitucional=kargs["entry"]
                )
                .exclude(pk=self.object.pk)
                .update(folha_evento_terco_constitucional=None)
            )

            # Marcando PASs que serão pagos no folha_evento calculado
            ups2 = (
                PeriodoAquisitivoServidor.objects.filter(pk=self.object.pk)
                .exclude(folha_evento_terco_constitucional=kargs["entry"])
                .update(folha_evento_terco_constitucional=kargs["entry"])
            )

            # log.debug('>>>> CALLBACK for %s DESMARCADOS: %s MARCADOS: %s' % (self.__class__.__name__, ups1, ups2))

    @property
    def ceiling_base_value(self):
        return 999999.99


@RunCodeManager.register("gfp-mpto-proportional-vacation")
class ProportionalVacation(BaseVacation):

    title = "Férias proporcionais"
    description = "Calculo de acerto de férias proporcionais"

    FULL_SALARY = True
    IGNORE_DEPARTURE = True

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        if employee.last_day_worked:
            kwargs["month"] = employee.last_day_worked.month
        super(BaseVacation, self).__init__(
            employee, payroll, event, entry, cid=cid, **kwargs
        )

    @cache_return
    def get_range(self):
        pas = self.get_query()
        range_pas = NewDateRange(
            pas[0].data_inicio_aquisicao, self.employee.last_day_worked
        )

        for afastamento in (
            BaseLicencaAfastamento.objects.filter(
                remunerado=False, servidor=self.employee
            )
            .exclude(
                models.Q(data_fim__lt=range_pas.first)
                | models.Q(data_inicio__gt=range_pas.last)
                | models.Q(estado=4)
            )
            .exclude(~models.Q(afastamento__afastamentooutroorgao=None))
        ):
            range_pas -= range_pas.intersect(
                NewDateRange(afastamento.data_inicio, afastamento.data_fim)
            )

        return range_pas

    def quantity(self):
        qnt = 0
        # qnt = 0
        # date_ranges = self.get_query()[0]
        # related = relativedelta(self.employee.data_desligamento, self.object.data_inicio_aquisicao)
        related = self.get_range()
        if not isinstance(related, NewDateRange):
            related = self.get_range().toordinals()
            rel = relativedelta(
                self.employee.data_desligamento, date.fromordinal(related[0])
            )
            qnt += rel.months
            qnt += 1 if rel.days >= 15 else 0
        else:
            count = 0
            related = self.get_range().toordinals()
            for dt in related:
                count += 1
                date_start = date.fromordinal(dt[0])
                date_end = date.fromordinal(dt[1])
                rel = relativedelta(
                    (
                        date_end
                        if count < len(related)
                        else self.employee.data_desligamento
                    ),
                    date_start,
                )
                qnt += rel.months
                qnt += 1 if rel.days >= 15 else 0

        return qnt

    def maximum_quantity(self):
        return (
            self.object.periodo_aquisitivo.configuracao.meses_exercicio
            if self.object
            else 1.0
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.last_day_worked
            and self.month != self.employee.last_day_worked.month
            and self.year != self.employee.last_day_worked.year
        ):
            raise self.CalculationNotApplicable(
                "O pagamento de férias proporcionais não pode ser pago em mês diferente do desligamento."
            )
        if (
            not self.employee.last_day_worked
            or self.employee.situacao_funcional_cache in ["INATIVO_DEVOLVIDO"]
        ):
            raise self.CalculationNotApplicable(
                "O Servidor %s não está desligado" % (self.employee)
            )

    def _get_query(self):
        return self.employee.periodos_aquisitivos.filter(
            data_inicio_aquisicao__lte=self.employee.last_day_worked,
            data_fim_aquisicao__gt=self.employee.last_day_worked,
        )

    def event_information(self):
        return "%s" % self.object.periodo_aquisitivo

    def callback(self, **kargs):
        from rh.ferias.models import PeriodoAquisitivoServidor

        # log.debug('>>>>> CALLBACKs')
        # for karg in kargs:
        #     # log.debug('>>>>> CALLBACK: %s' % karg)

        # log.debug('>>>> CALLBACK CALC FERIAS: %s' % [p.pas.id for p in self.pasus])
        if "entry" in kargs:
            q_pas = PeriodoAquisitivoServidor.objects.filter(pk__in=kargs["entry"].oIds)
            for pas in q_pas:
                # log.debug('>>>>> CALLBACK %s >> %s' % (kargs['entry'].oIds, pas.get_estado_display()))
                pas._indenizar()


@RunCodeManager.register("gfp-mpto-proportional-vacation-ii")
class ProportionalVacationII(ProportionalVacation):

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.last_day_worked
            and self.month != self.employee.last_day_worked.month
            and self.year != self.employee.last_day_worked.year
        ):
            raise self.CalculationNotApplicable(
                "O pagamento de férias vencidas não pode ser pago em mês diferente do desligamento."
            )
        if not self.employee.last_day_worked:
            raise self.CalculationNotApplicable(
                "O Servidor %s não está desligado" % (self.employee)
            )

    @property
    def ceiling_base_value(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )


@RunCodeManager.register("gfp-mpto-additional-proportional-vacation")
class AdditionalProportionalVacation(ProportionalVacationII):

    title = "Adicional de proporcional de férias"
    description = "Cálculo de acerto para adicional de férias proporcionais"

    def percentage(self):
        if self.object.pas.data_fim_aquisicao >= date(2018, 6, 12):
            return 33.3333333333
        return (
            33.3333333333
            if self.object.pas.periodo_aquisitivo.ano_aquisicao < 2012
            else 50.0
        )

    def callback(self, **kargs):
        from rh.ferias.models import PeriodoAquisitivoServidor

        # log.debug('>>>>> CALLBACK: %s' % kargs)
        # log.debug('>>>> CALLBACK CALC FERIAS: %s' % [p.pas.id for p in self.pasus])
        if "entry" in kargs:
            # Desmarcando PASs que não serão mais pagos no folha_evento calculado
            ups1 = (
                PeriodoAquisitivoServidor.objects.filter(
                    folha_evento_terco_constitucional=kargs["entry"]
                )
                .exclude(pk=self.object.pk)
                .update(folha_evento_terco_constitucional=None)
            )

            # Marcando PASs que serão pagos no folha_evento calculado
            ups2 = (
                PeriodoAquisitivoServidor.objects.filter(pk=self.object.pk)
                .exclude(folha_evento_terco_constitucional=kargs["entry"])
                .update(folha_evento_terco_constitucional=kargs["entry"])
            )

            # log.debug('>>>> CALLBACK for %s DESMARCADOS: %s MARCADOS: %s' % (self.__class__.__name__, ups1, ups2))

    @property
    def ceiling_base_value(self):
        return 999999.99


@RunCodeManager.register("gfp-mpto-compensated-vacation")
class CompensatedVacation(BaseSalary):
    title = "Férias Indenizadas"
    description = "Cálculo de acerto para férias vencidas"

    FULL_SALARY = True
    FULL_VALUE = True
    JOIN_ON_MULTI = False
    MULTI_CALCULATE = True
    EVALUATE_ON_REFERENCE_PAYROLL = True
    PARAMS_ = ["qnt", "oIds"]

    def quantity(self):
        qnt = 0
        if self.event:
            # log.debug(self.params.get('qnt', 0))
            if "qnt" in self.params and self.event.tipo_calculo in [3, 5]:
                qnt = float(self.params.get("qnt", 0) or 0)
        if self.payroll.is_processed:
            return qnt
        return min(self.object.days_not_enjoyed if self.object else 0, qnt)

    def maximum_quantity(self):
        return 30

    def _get_query(self):
        if self.params.get("oIds"):
            return self.employee.periodos_aquisitivos.filter(
                pk__in=self.params.get("oIds")
            )
        else:
            return self.employee.periodos_aquisitivos.filter(
                models.Q(estado__in=[PAS_ALIBERACAO, PAS_EMANDAMENTO])
                & models.Q(bloqueado=False)
            ).order_by("data_fim_aquisicao")
        return []

    def event_information(self):
        return "%s" % self.object.periodo_aquisitivo if self.object else ""

    @property
    def ceiling_base_value(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )
