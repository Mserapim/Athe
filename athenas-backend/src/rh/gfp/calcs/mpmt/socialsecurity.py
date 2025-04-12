# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.db.models import Q, Sum

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpmt.base import PercentageCalculation
from rh.gfp.models import (
    ExtraPaymentPeriod,
    FatorFap,
    FatorRat,
    RemunerationRelationship,
)
from rh.gfp.signals.regime_previdenciario import get_regime_previdenciario
from rh.models import (
    PessoaJuridica as LegalPerson,
    SocialSecurityConfig,
    SocialSecurityEmployee,
)
from rh.models import SocialSecurity, SocialSecurityRange
from standard.models import Configuration, Item, RunCodeManager
from decimal import Decimal

log = getLogger(__name__)


class BaseSocialSecurity(PercentageCalculation):

    RECALCULATE_BASES = 3
    IDENTIFIER = 1
    ONLY_EVENTS = True

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

    @property
    @cache_return
    def sp_previcom(self):
        try:
            pj = LegalPerson.objects.get(cnpj="15401381000198")
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
        ss = (
            SocialSecurity.objects.filter(
                legal_person=pj,
                identifier=self.IDENTIFIER,
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
                lower_limite__lt=repr(base_value),
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

        faixas = ss.ranges.order_by("-upper_limite")
        return faixas[0]

    def percentage(self):
        try:
            range_socialsecurity = self.range_socialsecurity()
            if range_socialsecurity is not None:
                return float(range_socialsecurity.percentage)
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
            # log.debug(f'{get_regime_previdenciario(self.employee, self.range_salary)}=={self.get_pj()}: {get_regime_previdenciario(self.employee, self.range_salary) == self.get_pj()}')
            ss = self.get_socialsecurity()
            return float(ss.percentage_of_employer)
        except self.CalculationNotApplicable as e:
            log.debug("%s" % e)
            return 0.00
        except Exception as e:
            log.exception(e)
            return 0.00

    def _get_focuses_on(self):
        return (
            super()._get_focuses_on() if (self.month != 13 or self.ONLY_EVENTS) else []
        )

    def _get_value_from_entry(self, entry):
        return float(entry.correct_base_previdencia)

    def _value_calc_normatized(self, calc, full_value=False):
        return calc.calculate().get("base_previdencia", 0)

    # @cache_return
    # def base_value(self):
    #     # log.debug('******************************* BASE VALUE %s' % self.__class__)
    #     if 'base_value' in self.params:
    #         return float(self.params['base_value'])

    #     if self.event and self.event.base_value_at(self.range_salary.first):
    #         return float(self.event.base_value_at(self.range_salary.first))

    #     # focuses_on = [e.numero for e in self.event.incide_sobre.all()]
    #     total = 0.00

    #     for fe in self.base_value_query():
    #         value = 0.0
    #         if fe.evento.automated and fe.classcode and\
    #                 (fe.reference_year != self.year or fe.reference_month != self.month or self.FORCE_RECALCULATE_BASE):
    #             # log.debug('*********** CALC FOR %s - %s' % (fe, fe.classcode.cls))
    #             # log.debug('*********** event %s | only_events %s ' % (fe.evento, self.focuses_on))
    #             params = {'pct': fe.pct, 'qnt': fe.qnt, 'info': fe.info,
    #                       'patronal': fe.patronal, 'valor_base': fe.valor_base}
    #             params.update(fe.vars)
    #             calc = fe.classcode.cls(
    #                 fe.servidor,
    #                 fe.folha,
    #                 fe.evento,
    #                 year=self.year,
    #                 month=self.month,
    #                 params=params,
    #                 only_events=self.focuses_on if self.month != 13 or self.ONLY_EVENTS else [],
    #                 group_cache=self.group_key_cache,
    #                 entry=fe,
    #                 pensioner=fe.contracheque.pensioner
    #             )
    #             value = calc.calculate()['base_previdencia']
    #             # log.debug('BASE_SOCIALSECURITY: %s' % value)
    #             value = value if fe.evento.tipo == 'P' else -value
    #         else:
    #             value = float(fe.correct_base_previdencia if fe.evento.tipo == 'P' else -fe.correct_base_previdencia)

    #     value = self._value_calc_normatized(calc, full_value=self.FULL_VALUE)
    #     value = value if fe.evento.tipo == 'P' else -value
    #     # log.debug(f'RECALC > {value}')
    # else:
    #     log.debug(f'>>>> L{self.level} NO CALCULATING {self.event} > {fe.evento}')
    #     value = float(fe.correct_valor if self.FULL_VALUE is False else fe.valor_base)
    #     value = value if fe.evento.tipo == 'P' else -value
    #         # log.debug('>>>> %s >>>> %s : %s + %s = %s' %
    #         #           (self.event.numero if self.event else 'XXX-XX', fe.evento, total, value, total + value))
    #         total += value

    #     base_value = total - self.base_discounts()
    #     # log.debug('>>>> %s >>>>  BASE VALUE %s - %s = %s' %
    #     #           (self.event.numero if self.event else 'XXX-XX', total, self.base_discounts(), base_value))

    #     return base_value if not (self.event and self.event.calculo_invertido) else -base_value

    def base_socialsecurity(self):
        return 0.00

    @property
    @cache_return
    def ceiling(self):
        # log.info('TETO %s: %s' % (self.__class__.__name__, self.range_ceiling.upper_limite))
        try:
            return (
                float(self.range_ceiling.upper_limite * self.range_ceiling.percentage)
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

    def value(self):
        value = super(BaseSocialSecurity, self).value()
        range_socialsecurity = self.range_socialsecurity()
        if range_socialsecurity:
            value -= (
                float(range_socialsecurity.reducer) if range_socialsecurity else 0.0
            )
        return value

    def get_current_socialsecurity(self, pj):
        """Retorna a Previdência vigente de acordo com o parâmetro 'pj'"""

        ss = (
            SocialSecurity.objects.filter(legal_person=pj, end_validity__isnull=True)
            .currents_at(self.payroll.date_range.first)
            .order_by("-start_validity")
        )

        if not ss:
            raise SocialSecurity.DoesNotExist(
                f"Não existe previdência vigente em {self.payroll.date_range.first} para a PJ {pj}."
            )

        return ss.first()

    @property
    def minimum_wage(self):
        return self.payroll.periodo.salario_minimo

    def validate_only_one_ssc(self):
        """O Servidor deve ter apenas um registro de Configuração Previdenciária (SocialSecurityConfig)"""
        if self.employee.social_securities.count() > 1:
            raise self.CalculationNotApplicable(
                "O Servidor possui mais de uma configuração previdenciária."
            )

    def validate_more_than_one_ssc(self):
        """O Servidor deve ter mais de um registro de Configuração Previdenciária (SocialSecurityConfig)"""
        if self.employee.social_securities.count() < 2:
            raise self.CalculationNotApplicable(
                "O Servidor precisa ter mais de uma configuração previdenciária."
            )

    def validate_if_ssc_is_pgjmt_rpps(self):
        """Valida se a Configuração Previdenciária (SocialSecurityConfig) é do PGJ-MT - RPPS (Procuradoria
        Geral de Justiça do Estado de Mato Grosso - Regime RPPS)"""

        ssc = SocialSecurityConfig.objects.filter(
            organ__cnpj=self.CNPJ,  # PGJ-MT
            regime="2",  # RPPS
        ).first()

        if not ssc in self.employee.social_securities.all():
            raise self.CalculationNotApplicable(
                "O Servidor deve ter a configuração previdenciária associada à PGJ-MT - RPPS."
            )

    def validate_if_ssc_only_pgjmt(self):
        """Valida se a Configuração Previdenciária (SocialSecurityConfig) é do PGJ-MT e se está configurada
        para ignorar outras Configurações Previdenciárias"""

        ssc_mpmt = SocialSecurityConfig.objects.filter(
            organ__cnpj=self.CNPJ,  # PGJ-MT
            regime="2",  # RPPS
        ).first()

        if ssc_mpmt in self.employee.social_securities.all():
            ssce = self.employee.social_securities.first()
            sse = SocialSecurityEmployee.objects.filter(
                employee=self.employee,
                social_security_config=ssce,
            )
            if (
                # self.employee.social_securities.count() < 2 and
                sse.exists()
                and sse.first().ignore_others_ssc
            ):
                msg = """
                O Servidor optou por colaborar somente com a previdência do PGJ-MT - RPPS.
                E esta verba não permite esta configuração.
                """
                raise self.CalculationNotApplicable(msg)

    def validate_if_ssc_is_spprevicom_rpps(self):
        """Valida se a Configuração Previdenciária (SocialSecurityConfig) é do SP-PREVICOM - RPPS (Fundação de Previdência
        Complementar do Estado de São Paulo - Regime RPPS)"""

        ssc = SocialSecurityConfig.objects.filter(
            organ__cnpj=15401381000198,  # SP-PREVICOM
            regime="2",  # RPPS
        ).first()

        if not ssc in self.employee.social_securities.all():
            raise self.CalculationNotApplicable(
                "O Servidor deve ter a configuração previdenciária associada à SP-PREVICOM - RPPS."
            )

    def validate_if_ssc_is_inss_rgps(self):
        """Valida se a Configuração Previdenciária (SocialSecurityConfig) é do PGJ-MT - RPPS (Procuradoria
        Geral de Justiça do Estado de Mato Grosso - Regime RPPS)"""

        ssc = SocialSecurityConfig.objects.filter(
            organ__cnpj=29979036000140,  # PGJ-MT
            regime="1",  # RGPS
        ).first()

        if not ssc in self.employee.social_securities.all():
            raise self.CalculationNotApplicable(
                "O Servidor deve ter a configuração previdenciária associada ao INSS - RGPS."
            )

    def validate_only_employee_active(self):
        """Valida se o employee está ativo"""

        if self.employee.is_ativo() is False:
            raise self.CalculationNotApplicable(
                "A verba só pode ser aplicada para Servidores ativos."
            )

    def validate_type_by_possession(self, types_by_possession):
        """Valida os tipos de servidores permitidos para a verba, através do campo type_by_possession"""

        if self.employee.type_by_possession not in types_by_possession:
            raise self.CalculationNotApplicable(
                "A verba não pode ser aplicada a este tipo de Servidor."
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.organ_social_security_employee != self.get_pj():
            raise self.CalculationNotApplicable(
                "Regime previdenciário do servidor é diferente"
            )


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-pf")
class PrevidenciaMPMT(BaseSocialSecurity):
    title = "Cáluclo de Previdência MPMT"
    CNPJ = "14921092000157"

    SLUG_EXCEPTIONS_2X = "CP_EXCECOES_2X"

    @property
    def is_benefit(self):
        return self.employee.type_by_possession in ("SAP", "MAP", "MAP2", "BFP", "APO")

    @property
    def inss_ceiling(self):
        ss_inss = self.get_current_socialsecurity(self.inss)
        range_ceiling = ss_inss.ranges.order_by("-upper_limite").first()
        if range_ceiling:
            return float(range_ceiling.upper_limite)
        return 0.0

    @property
    def _exception_2x(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=self.employee, extra_payment__slug=self.SLUG_EXCEPTIONS_2X
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return q.first()

    def percentage(self):
        return (
            float(self._exception_2x.value)
            if self._exception_2x
            else super().percentage()
        )

    @cache_return
    def base_discounts(self):
        discount = 0
        if self.is_benefit:
            discount = self.minimum_wage
            if self._exception_2x:
                discount = 2 * self.inss_ceiling
            # factor = 2.0 if self.employee.molestia else 1.0
        # log.debug(f'FATOR: {factor} RANGE_MAX: {self.range_max_socialsecurity_inss()}')
        return float(discount)

    @cache_return
    def range_max_socialsecurity_inss(self):
        ss = self.get_current_socialsecurity(self.inss)
        ranges = ss.ranges.order_by("-upper_limite")
        return float(ranges[0].upper_limite) if ranges else 0

    def value(self):
        value = super(BaseSocialSecurity, self).value()

        return value

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_only_one_ssc()
        self.validate_if_ssc_is_pgjmt_rpps()
        self.validate_if_ssc_only_pgjmt()
        self.validate_only_employee_active()

        types_by_possession = [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "EFE",
            "EFC",
            "ECM",
            "MCM2",
            "MEC2",
        ]
        self.validate_type_by_possession(types_by_possession)


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-ii-pf")
class PrevidenciaIIMPMT(BaseSocialSecurity):

    title = "Cáluclo de Previdência II MPMT"
    CNPJ = "14921092000157"

    @cache_return
    def range_socialsecurity(self):
        return self.range_ceiling

    @property
    @cache_return
    def range_ceiling(self):
        ss = self.get_current_socialsecurity(self.inss)

        faixas = ss.ranges.order_by("-upper_limite")
        return faixas.first()

    def base_value(self):
        range_socialsecurity = self.range_socialsecurity()
        return range_socialsecurity.upper_limite

    def base_socialsecurity(self):
        return self.base_value()

    def percentage(self):
        range_socialsecurity = self.range_socialsecurity()
        return range_socialsecurity.percentage

    def value(self):
        value = self.base_value() * (self.percentage() / 100)
        return value

    def maximum_quantity(self):
        return self.range_salary.days

    @cache_return
    def employer_value(self):
        ss_inss = self.get_current_socialsecurity(self.inss)
        ranges_ss_inss = ss_inss.ranges.order_by("-upper_limite")
        value = float(ranges_ss_inss.first().upper_limite)

        ss_mpmt = self.get_current_socialsecurity(self.get_pj())
        percentage = float(ss_mpmt.percentage_of_employer / 100)

        return value * percentage

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_more_than_one_ssc()
        self.validate_if_ssc_is_pgjmt_rpps()
        self.validate_if_ssc_is_spprevicom_rpps()
        self.validate_if_ssc_only_pgjmt()
        self.validate_only_employee_active()

        types_by_possession = [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "EFE",
            "EFC",
            "ECM",
            "MCM2",
            "MEC2",
        ]
        self.validate_type_by_possession(types_by_possession)


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-iii-pf")
class PrevidenciaIIIMPMT(PrevidenciaIIMPMT):

    title = "Cáluclo de Previdência III MPMT"
    CNPJ = "14921092000157"

    def validate_if_ssc_only_pgjmt(self):
        """Valida se a Configuração Previdenciária (SocialSecurityConfig) é do PGJ-MT e se está configurada
        para ignorar outras Configurações Previdenciárias"""

        ssc_mpmt = SocialSecurityConfig.objects.filter(
            organ__cnpj=self.CNPJ,  # PGJ-MT
            regime="2",  # RPPS
        ).first()

        if ssc_mpmt in self.employee.social_securities.all():
            ssce = self.employee.social_securities.first()
            sse = SocialSecurityEmployee.objects.filter(
                employee=self.employee,
                social_security_config=ssce,
            )
            if sse.exists() and sse.first().ignore_others_ssc is False:
                msg = """
                O Servidor optou por ter colaborações previdenciárias além do PGJ-MT - RPPS.
                E esta verba exije que tenha a colaboração somente ao PGJ-MT.
                """
                raise self.CalculationNotApplicable(msg)

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_ssc_is_pgjmt_rpps()
        self.validate_if_ssc_only_pgjmt()
        self.validate_only_employee_active()

        types_by_possession = [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "EFE",
            "EFC",
            "ECM",
            "MCM2",
            "MEC2",
        ]
        self.validate_type_by_possession(types_by_possession)


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-compl-pf")
class PrevidenciaComplementarMPMT(BaseSocialSecurity):

    title = "Cáluclo de Previdência Complementar MPMT"
    CNPJ = "14921092000157"

    @cache_return
    def range_socialsecurity(self):
        return self.range_ceiling

    @property
    @cache_return
    def range_ceiling(self):
        ss = self.get_current_socialsecurity(self.inss)

        faixas = ss.ranges.order_by("-upper_limite")
        return faixas.first()

    def percentage(self):
        ss = self.get_current_socialsecurity(self.sp_previcom)
        max_faixas = ss.ranges.order_by("-upper_limite").first()

        return max_faixas.percentage

    def value(self):
        range_ceiling_inss = self.range_socialsecurity()
        max_value_inss = range_ceiling_inss.upper_limite

        percentage_previcom = self.percentage() / 100

        value = (self.base_value() - float(max_value_inss)) * float(percentage_previcom)

        return value

    @cache_return
    def employer_value(self):
        return self.value()

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_more_than_one_ssc()
        self.validate_if_ssc_is_pgjmt_rpps()
        self.validate_if_ssc_is_spprevicom_rpps()
        self.validate_only_employee_active()

        types_by_possession = [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "EFE",
            "EFC",
            "ECM",
            "MCM2",
            "MEC2",
        ]
        self.validate_type_by_possession(types_by_possession)


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-inativo-pf")
class PrevidenciaInativoMPMT(BaseSocialSecurity):
    title = "Cáluclo de Previdência para inativos MPMT"
    CNPJ = "14921092000157"

    SLUG_EXCEPTIONS_1X = "CP_EXCECOES_1X"
    SLUG_EXCEPTIONS_2X = "CP_EXCECOES_2X"

    @property
    def _exception_2x(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=self.employee, extra_payment__slug=self.SLUG_EXCEPTIONS_2X
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return q.first()

    @property
    def _exception_1x(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=self.employee, extra_payment__slug=self.SLUG_EXCEPTIONS_1X
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return q.first()

    def percentage(self):
        if self._exception_1x or self._exception_2x:
            return (
                float(self._exception_1x.value)
                if self._exception_1x
                else float(self._exception_2x.value)
            )
        else:
            range_ss_employee = self.range_socialsecurity_pgj_employee()
            return range_ss_employee.percentage

    def range_socialsecurity_pgj_employee(self):
        base_value = self.base_value()
        ss = self.get_current_socialsecurity(self.get_pj())

        range_socialsecurity = SocialSecurityRange.objects.get(
            socialsecurity=ss,
            lower_limite__lte=repr(base_value),
            upper_limite__gte=repr(base_value),
        )

        return range_socialsecurity

    def range_ceiling(self, organ, level):
        ss = self.get_current_socialsecurity(organ)
        faixas = ss.ranges.order_by("-upper_limite")

        if level == "min":
            return faixas.last()
        elif level == "max":
            return faixas.first()
        else:
            return faixas[1]

    def set_value_to_calculate(self):
        base_value = self.base_value()
        if self._exception_1x or self._exception_2x:
            range_socialsecurity = self.range_ceiling(self.inss, "max")

            if self._exception_1x:
                range_ss_upper_limite = float(range_socialsecurity.upper_limite)
            else:
                range_ss_upper_limite = float(range_socialsecurity.upper_limite * 2)

            value = base_value - range_ss_upper_limite

            return value
        else:
            base_value = self.base_value()
            ss_range_employee = self.range_socialsecurity_pgj_employee()

            # verifica se Servidor está na faixa inferior da previdência PGJ-MT
            # ISENTO
            if self.range_ceiling(self.get_pj(), "min") == ss_range_employee:
                return 0
            # verifica se Servidor está na faixa superior da previdência PGJ-MT
            # (base_value - salário mínimo) * percentual da faixa de previdência do PGJ
            elif self.range_ceiling(self.get_pj(), "max") == ss_range_employee:
                value = base_value - float(ss_range_employee.reducer)

                return value
            # Servidor está na faixa intermediária da previdência PGJ-MT
            # (base_value - limite superior da primeira faixa da previdência PGJ-MT) * percentual da faixa de previdência do PGJ
            else:
                range_min_inss = self.range_ceiling(self.get_pj(), "min")
                valor_inss = float(range_min_inss.upper_limite)

                value = base_value - valor_inss

                return value

    def value(self):
        percentage = float(self.percentage() / 100)
        value_calculated = self.set_value_to_calculate()

        return value_calculated * percentage

    @cache_return
    def employer_value(self):
        ss = self.get_current_socialsecurity(self.get_pj())
        percentage = float(ss.percentage_of_employer / 100)
        value_calculated = self.set_value_to_calculate()

        return value_calculated * percentage

    def validate_only_one_cp_exception(self):
        if self._exception_1x and self._exception_2x:
            msg = f"O Servidor não pode estar nas duas configurações de verba extra {self.SLUG_EXCEPTIONS_1X} e {self.SLUG_EXCEPTIONS_2X}."
            raise self.CalculationNotApplicable(msg)

    def validate(self):
        self.validate_only_one_ssc()
        self.validate_only_one_cp_exception()
        self.validate_if_ssc_is_pgjmt_rpps()

        types_by_possession = ["MAP", "SAP", "MAP2", "APO", "BFP"]
        self.validate_type_by_possession(types_by_possession)


@RunCodeManager.register("gfp-mpmt-socialsecurity-inss")
class INSS(BaseSocialSecurity):
    title = "Calculo de previdencia social INSS"
    CNPJ = None
    ONLY_EVENTS = False

    class NotConfiguredINSS(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "O parâmentro INSS não foi configurado em FOLHA DE PAGAMENTO->Configuração.",
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

        base_value = min(self.base_value(), self.range_ceiling.upper_limite)
        range_ss = self.range_socialsecurity()
        value = 0
        if range_ss:
            # value = trunc2((float(base_value) - float(range_ss.lower_limite)) * self.percentage()/100) + float(range_ss.reducer)
            value = (
                trunc2(
                    round(float(base_value) - float(range_ss.lower_limite), 4)
                    * self.percentage()
                    / 100
                )
                + float(range_ss.reducer)
                - float(self.extra_inss_value())
            )
        arred_valor_inss = Item.objects.filter(key="arrendondar_calculo_inss").first()
        if base_value == self.range_ceiling.upper_limite and arred_valor_inss:
            value = Decimal(value) + Decimal(float(arred_valor_inss.value))
        return value

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_ssc_is_inss_rgps()
