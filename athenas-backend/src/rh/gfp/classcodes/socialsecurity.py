# -*- coding: utf-8 -*-

import datetime

from contrib.decorator import cache_return
from contrib.helpers import roundrfb
from contrib.utils import getLogger
from rh.gfp.classcodes.base import PercentageCalculation
from rh.gfp.models import FatorFap, FatorRat
from rh.gfp.models import PrevidenciaFaixa as RangeSocialSecurity
from rh.gfp.signals.regime_previdenciario import get_regime_previdenciario
from rh.models import PessoaJuridica as LegalPerson
from rh.models import SocialSecurity
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)


class BaseSocialSecurity(PercentageCalculation):

    FORCE_RECALCULATE_BASE = True
    IDENTIFIER = 1
    ONLY_EVENTS = True
    FIELD_RETURN_TO_BASE_VALUE = "correct_contribution_base"

    @property
    def _get_cnpj(self):
        return self.CNPJ if self.CNPJ else None

    @property
    @cache_return
    def object(self):
        log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None

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
            log.debug(
                "A pessoa jurídica com o CNPJ %s não existe na base de dados!"
                % self.CNPJ
            )
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
                legal_person=pj,
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
        if get_regime_previdenciario(self.employee, self.range_salary) != self.get_pj():
            raise self.CalculationNotApplicable(
                "Regime previdenciário do servidor é diferente"
            )

        ss = self.get_socialsecurity()

        base_value = self.base_value()
        try:
            range_socialsecurity = SocialSecurityRange.objects.get(
                socialsecurity=ss,
                lower_limite__lte=repr(base_value),
                upper_limite__gte=repr(base_value),
            )
            return range_socialsecurity
        except SocialSecurityRange.DoesNotExist:
            # log.info('Não consegui localizar a faixa da previdencia para o valor %s' % base_value)
            # log.info('Prev %s: %s' % (prev, base_value))
            if float(self.range_ceiling.upper_limite) < base_value:
                # log.info('Utilizando faixa teto do %s para o valor %s' % (prev, base_value))
                return self.range_ceiling
            else:
                raise SocialSecurityRange.DoesNotExist(
                    "Não existe faixa da previdencia (%s) para o valor %s"
                    % (ss, base_value)
                )

    @property
    @cache_return
    def range_ceiling(self):

        if get_regime_previdenciario(self.employee, self.range_salary) != self.get_pj():
            raise self.CalculationNotApplicable(
                "Regime previdenciário do servidor é diferente"
            )

        ss = self.get_socialsecurity()

        faixas = ss.get_faixas.order_by("-limite_superior")
        return faixas[0]

    def percentage(self):
        try:
            range_socialsecurity = self.range_socialsecurity()
            if range_socialsecurity is not None:
                return float(range_socialsecurity.pct)
            else:
                return 0.00
        except self.CalculationNotApplicable as e:
            log.debug("%s" % e)
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
            range_socialsecurity = self.range_socialsecurity()

            if range_socialsecurity is not None:
                return float(range_socialsecurity.pct_patronal)
            else:
                return 0.00
        except self.CalculationNotApplicable as e:
            log.debug("%s" % e)
            return 0.00
        except Exception as e:
            log.exception(e)
            return 0.00

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.base_socialsecurity()

    def _get_value_from_entry(self, entry):
        return float(entry.correct_contribution_base)

    def _get_base_ss_from_calc(self, calc):
        return 0

    def _get_base_ss_from_entry(self, entry):
        return 0

    def base_socialsecurity(self):
        return 0.00

    @property
    @cache_return
    def ceiling(self):
        # log.info(u'TETO %s: %s' % (self.__class__.__name__, self.range_ceiling.limite_superior))
        try:
            return (
                float(self.range_ceiling.limite_superior * self.range_ceiling.pct)
                / 100.0
            )
        except self.CalculationNotApplicable as e:
            log.debug("%s" % e)
            return 0.00
        except Exception:
            log.exception(
                "ERRO: %s: %s: %s" % (self.employee, self.event, self.__class__)
            )
            return 0.00

    def factor_quantity(self):
        return 1.0

    def validate(self):
        self.validate_not_paycheck_pension()
        if get_regime_previdenciario(self.employee, self.range_salary) != self.get_pj():
            raise self.CalculationNotApplicable(
                "Regime previdenciário do servidor é diferente"
            )


@RunCodeManager.register("gfp-socialsecurity-igeprev-pf")
class IgeprevTocantinsPF(BaseSocialSecurity):
    title = "Calculo de previdencia social IGEPREV-TO : Plano Financeiro"
    CNPJ = "25091307000176"

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.data_exercicio >= datetime.date(year=2012, month=6, day=1):
            raise self.CalculationNotApplicable(
                "O servidor %s não faz parte da massa PF (Plano Financeiro) do Igeprev Tocantins"
                % (self.employee)
            )


@RunCodeManager.register("gfp-socialsecurity-igeprev-pp")
class IgeprevTocantinsPP(IgeprevTocantinsPF):
    title = "Calculo de previdencia social IGEPREV-TO : Plano Previdenciário"

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.data_exercicio < datetime.date(year=2012, month=6, day=1):
            raise self.CalculationNotApplicable(
                "O servidor %s não faz parte da massa PP (Plano Previdenciário) do Igeprev Tocantins"
                % (self.employee)
            )


@RunCodeManager.register("gfp-socialsecurity-prevpalmas")
class PrevPalmas(BaseSocialSecurity):
    title = "Calculo de previdencia social Prev-Palmas"
    CNPJ = "05278848000109"


@RunCodeManager.register("gfp-classcodes-socialsecurity-previporto")
class PreviPorto(BaseSocialSecurity):
    title = "Calculo de previdencia social Previ-Porto"
    CNPJ = "19331029000184"


@RunCodeManager.register("gfp-socialsecurity-inss")
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

    def value(self):
        # v = super(INSS, self).value()
        # return int(v * 100) / 100.0
        return roundrfb(super(INSS, self).value())


@RunCodeManager.register("gfp-socialsecurity-goiasprev-pf")
class GoiasPrevPF(BaseSocialSecurity):
    title = "Calculo de previdencia social GOIASPREV-GO : Plano Financeiro"
    CNPJ = "11991625000189"
