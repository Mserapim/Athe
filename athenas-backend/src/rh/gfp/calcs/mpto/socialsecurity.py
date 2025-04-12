# -*- coding: utf-8 -*-

import datetime

from django.db.models import Sum

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import PercentageCalculation
from rh.gfp.models import Evento, FatorFap, FatorRat, RemunerationRelationship
from rh.models import PessoaJuridica as LegalPerson, SocialSecurity, SocialSecurityRange
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)


class BaseSocialSecurity(PercentageCalculation):

    FORCE_RECALCULATE_BASE = True
    IDENTIFIER = 1
    ONLY_EVENTS = True
    MEMORY = True

    @property
    def organ_social_security_employee(self):
        return self.employee.organ_social_security_employee(range=self.range_salary)

    @property
    def _get_cnpj(self):
        return self.CNPJ if self.CNPJ else None

    @property
    @cache_return
    def inss(self):
        try:
            cfg = Configuration.get_or_create("gfp")
            pj = LegalPerson.objects.get(pk=cfg.get("inss"))
        except Exception as e:
            log.exception(e)
            return None
        else:
            return pj

    @cache_return
    def get_pj(self):
        try:
            pj = LegalPerson.objects.get(cnpj=self.CNPJ)
        except LegalPerson.DoesNotExist:
            # log.debug('A pessoa jurídica com o CNPJ %s não existe na base de dados!' % self.CNPJ)
            pj = None
        except Exception as e:
            log.exception(e)
            pj = None
        finally:
            return pj

    @cache_return
    def get_socialsecurity(self):
        pj = self.get_pj()
        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        regime_social_security = ssc.regime if ssc else None
        ss = (
            SocialSecurity.objects.filter(
                legal_person=self.organ_social_security_employee,
                identifier=self.IDENTIFIER,
                socialsecurity_regime=regime_social_security,
            )
            .currents_at(self.payroll.date_range.first)
            .order_by("-start_validity")
        )
        if not ss:
            raise SocialSecurity.DoesNotExist(
                "Não existe previdência vigente em %s para a PJ %s(%s)"
                % (self.payroll.date_range.first, pj, pj.cnpj)
            )

        return ss[0]

    @cache_return
    def range_socialsecurity(self):
        # log.debug('FAIXA: %s' % self.range_salary)
        # if not self.get_employee_social_security_organ.exists():
        #     raise self.CalculationNotApplicable('Regime previdenciário do servidor é diferente')

        ss = self.get_socialsecurity()

        base_value = self.base_value()
        if base_value == 0:
            return None
        try:
            range_socialsecurity = SocialSecurityRange.objects.get(
                socialsecurity=ss,
                lower_limite__lt=repr(base_value),
                upper_limite__gte=repr(base_value),
            )
            return range_socialsecurity
        except SocialSecurityRange.DoesNotExist:
            # log.debug('Não consegui localizar a faixa da previdencia para o valor %s' % base_value)
            # log.debug('Prev %s: %s' % (prev, base_value))
            if float(self.range_ceiling.upper_limite) < base_value:
                # log.debug('Utilizando faixa teto do %s para o valor %s' % (prev, base_value))
                return self.range_ceiling
            else:
                log.info(f">>>>>>>>>>>>>>>>>>>>>>>> {self.__class__}")
                log.info(f">>>>>>>>>>>>>>>>>>>>>>>> {self.employee} {self.payroll}")
                log.error(
                    f"Não existe faixa da previdencia {ss} para o valor {base_value}"
                )
                return None

    @property
    @cache_return
    def range_ceiling(self):

        # if not self.get_employee_social_security_organ.exists():
        #     raise self.CalculationNotApplicable('Regime previdenciário do servidor é diferente')

        ss = self.get_socialsecurity()

        faixas = ss.ranges.order_by("-upper_limite")
        return faixas[0]

    def percentage(self):
        try:
            range_socialsecurity = self.range_socialsecurity()
            if range_socialsecurity is not None:
                return float(range_socialsecurity.percentage)
            else:
                return 0.00
        except self.CalculationNotApplicable:
            # log.debug("%s" % e)
            return 0.00
        except Exception as e:
            log.exception(e)
            return 0.00

    @cache_return
    def rat_adjusted(self):
        if self.get_pj() == self.inss:
            return (
                FatorRat.vigente_em(self.range_salary.last)
                / 100
                * FatorFap.vigente_em(self.range_salary.first)
            )
        return 0.0

    @cache_return
    def employer_value(self):
        return self.base_value() * (self.percentage_employer() / 100.00) + (
            self.base_value() * self.rat_adjusted()
        )

    def percentage_employer(self):
        try:
            # if not self.get_employee_social_security_organ.exists():
            #     raise self.CalculationNotApplicable('Regime previdenciário do servidor é diferente')

            # else:
            ss = self.get_socialsecurity()
            return float(ss.percentage_of_employer)
        except self.CalculationNotApplicable:
            # log.debug("%s" % e)
            return 0.00
        except Exception as e:
            log.exception(e)
            return 0.00

    def _get_value_from_entry(self, entry):
        return float(entry.correct_base_previdencia)

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.calculate().get("base_previdencia", 0)

    def base_socialsecurity(self):
        return 0.00

    @property
    @cache_return
    def ceiling(self):
        # log.debug('TETO %s: %s' % (self.__class__.__name__, self.range_ceiling.upper_limite))
        try:
            return (
                float(self.range_ceiling.upper_limite * self.range_ceiling.percentage)
                / 100.0
            )
        except self.CalculationNotApplicable:
            # log.debug("%s" % e)
            return 0.00
        except Exception:
            log.exception(
                "ERRO: %s: %s: %s" % (self.employee, self.event, self.__class__)
            )
            return 0.00

    def factor_quantity(self):
        return 1.0

    def value(self):
        value = super(BaseSocialSecurity, self).value()
        range_socialsecurity = self.range_socialsecurity()
        if range_socialsecurity:
            value -= (
                float(range_socialsecurity.reducer) if range_socialsecurity else 0.0
            )
        return value

    @property
    def exercise_employee(self):
        exercicio_req = self.employee.posses.filter(requestmove__isnull=False).last()
        return (
            self.employee.exercise_date
            if not self.employee.is_requested()
            else exercicio_req.my_origin.possession_origin_date
        )

    def validate_pj(self):
        if self.get_pj() != self.organ_social_security_employee:
            raise self.CalculationNotApplicable(
                "Regime previdenciário do servidor é diferente"
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_pj()


@RunCodeManager.register("gfp-mpto-socialsecurity-igeprev-pf")
class IgeprevTocantinsPF(BaseSocialSecurity):
    title = "Calculo de previdencia social IGEPREV-TO : Plano Financeiro"
    CNPJ = "25091307000176"

    def validate(self):
        super().validate()
        if self.exercise_employee >= datetime.date(year=2012, month=6, day=1):
            raise self.CalculationNotApplicable(
                "O servidor %s não faz parte da massa PF (Plano Financeiro) do Igeprev Tocantins"
                % (self.employee)
            )


@RunCodeManager.register("gfp-mpto-socialsecurity-igeprev-pp")
class IgeprevTocantinsPP(BaseSocialSecurity):
    title = "Calculo de previdencia social IGEPREV-TO : Plano Previdenciário"
    CNPJ = "25091307000176"

    def validate(self):
        super().validate()
        if self.exercise_employee < datetime.date(year=2012, month=6, day=1):
            raise self.CalculationNotApplicable(
                "O servidor %s não faz parte da massa PP (Plano Previdenciário) do Igeprev Tocantins"
                % (self.employee)
            )


@RunCodeManager.register("gfp-mpto-socialsecurity-prevpalmas")
class PrevPalmas(BaseSocialSecurity):
    title = "Calculo de previdencia social Prev-Palmas"
    CNPJ = "05278848000109"


@RunCodeManager.register("gfp-mpto-socialsecurity-previporto")
class PreviPorto(BaseSocialSecurity):
    title = "Calculo de previdencia social Previ-Porto"
    CNPJ = "19331029000184"


@RunCodeManager.register("gfp-mpto-socialsecurity-inss")
class INSS(BaseSocialSecurity):
    title = "Calculo de previdencia social INSS"
    CNPJ = None
    ONLY_EVENTS = False

    class NotConfiguredINSS(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "O parâmentro INSS não foi configurado em payroll DE PAGAMENTO->Configuração.",
            )

    def get_pj(self):
        try:
            cfg = Configuration.get_or_create("gfp")
            pj = LegalPerson.objects.get(pk=cfg.get("inss"))
        except Exception as e:
            log.exception(e)
            return None
        else:
            return pj

    def _query_remuneration_relationship(self):
        return RemunerationRelationship.objects.filter(
            employee=self.employee
        ).currents_between(self.payroll.date_range.first, self.payroll.date_range.last)

    def vars(self):
        """Indicador de desconto da contribuição previdenciária do trabalhador.
        Valores válidos:
            1 - O declarante aplica a(s) alíquota(s) de desconto do segurado sobre a remuneração por ele informada (o percentual da(s)
            alíquota(s) será(ão) obtido(s) considerando a remuneração total do trabalhador)
            2 - O declarante aplica a(s) alíquota(s) de desconto do segurado sobre a diferença entre o limite máximo do salário de
            contribuição e a remuneração de outra(s) empresa(s) para as quais o trabalhador informou que houve o desconto
            3 - O declarante não realiza desconto do segurado, uma vez que houve desconto sobre o limite máximo de salário de
            contribuição em outra(s) empresa(s)"""
        _vars = super().vars()
        if self._query_remuneration_relationship().exists():
            ind_mv = 1
            if self.value() <= 0:
                ind_mv = 3
            _vars.update({"indMV": ind_mv})
        return _vars

    @cache_return
    def extra_base_value(self):
        return float(
            self._query_remuneration_relationship()
            .aggregate(total=Sum("remuneration"))
            .get("total")
            or 0.00
        )

    @cache_return
    def extra_inss_value(self):
        return float(
            self._query_remuneration_relationship()
            .aggregate(total=Sum("inss_value"))
            .get("total")
            or 0.00
        )

    def value(self):
        def trunc2(f):
            return int(float(f) * 100) / 100

        base_value = self.base_value() + self.extra_base_value()
        base_value = min(base_value, self.range_ceiling.upper_limite)
        range_ss = self.range_socialsecurity()
        value = 0
        if range_ss:
            # log.debug(f'BASE: {base_value} LI: {range_ss.lower_limite} PCT: {self.percentage()} REDUTOR: {range_ss.reducer}')
            value = (
                trunc2(
                    round(float(base_value) - float(range_ss.lower_limite), 4)
                    * self.percentage()
                    / 100
                )
                + float(range_ss.reducer)
                - float(self.extra_inss_value())
            )
        return value


@RunCodeManager.register("gfp-mpto-socialsecurity-inss-ii")
class INSS2(INSS):

    EXCLUDE_EVENTS = ["salariomaternidade"]

    def employer_value(self):
        exclude = [
            x.numero for x in Evento.objects.filter(tags__label__in=self.EXCLUDE_EVENTS)
        ]
        new = INSS2(
            self.employee,
            self.payroll,
            self.event,
            self.entry,
            exclude_events=exclude,
            only_events=self.only_events,
        )
        base_value = new.base_value()
        return base_value * (self.percentage_employer() / 100.00) + (
            base_value * self.rat_adjusted()
        )


@RunCodeManager.register("gfp-mpto-socialsecurity-goiasprev-pf")
class GoiasPrevPF(BaseSocialSecurity):
    title = "Calculo de previdencia social GOIASPREV-GO : Plano Financeiro"
    CNPJ = "11991625000189"


@RunCodeManager.register("gfp-mpto-socialsecurity-arraiasprev-pf")
class ArraiasPrev(BaseSocialSecurity):
    title = "Calculo de previdencia social ARRAIAS PREV"
    CNPJ = "31781951000179"


@RunCodeManager.register("gfp-mpto-socialsecurity-imparprev-pf")
class ImparPrev(BaseSocialSecurity):
    title = "Calculo de previdencia social IMPARPREV"
    CNPJ = "02664384000172"


@RunCodeManager.register("gfp-mpto-socialsecurity-gurupiprev-pf")
class GurupiPrev(BaseSocialSecurity):
    title = "Calculo de previdencia social GURUPIPREV"
    CNPJ = "14120591000145"
