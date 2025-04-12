from dateutil.relativedelta import relativedelta
from django.db.models import Q
from memoization import cached
from datetime import datetime

from contrib.utils import getLogger
from contrib.daterange import NewDateRange

from standard.models import RunCodeManager, Item
from rh.gfp.models import FolhaEvento as Entry, EstruturaTabelaSalarial

from rh.gfp.calcs.mpmt.base import BaseCalculation, WorkDaysCalculation
from rh.gfp.calcs.mpmt.socialsecurity import (
    INSS,
    PrevidenciaInativoMPMT,
    PrevidenciaMPMT,
    PrevidenciaIIMPMT,
    PrevidenciaComplementarMPMT,
    PrevidenciaIIIMPMT,
)
from rh.gfp.calcs.mpmt.irrf import IRRF
from rh.gfp.calcs.mpmt.aid import (
    AidExtraWithoutDays,
    AidExtraEarningsIncorporated,
    SubDifferenceMPFCI,
    AbonoPermanencia,
)
from rh.gfp.calcs.mpmt.remuneracao import SalaryCommissioned, ReduceSalaryCap


log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-christmas-base-calculation-13")
class BaseCalculation13(BaseCalculation):

    GRATS_CHECK_KEY = None

    TYPES_BY_POSSESSION = []

    def calculate(self):
        result = {
            "qnt": 0,
            "qnt_max": 0,
            "pct": 0,
            "valor_base": 0,
            "valor": 0,
            "base_previdencia": 0,
            "patronal": 0,
            "info": "",
            "vars": {},
            "callback": self.callback,
            "validate": {"message": ""},
            "oIds": [],
            "choices": [],
            "references": self.references,
            "parcela": 0,
            "installments_paid": 1,
            "prazo": 0,
            "memory": [],
        }
        try:
            self.validate()
            result["base_calc"] = self.base_calc
        except Exception as e:
            result["validate"]["message"] = str(e)
            return result

        return self.calculate_single()

    def maximum_quantity(self):
        return 12

    def quantity(self):
        return self.base_calc["qtd"]

    def base_value(self):
        return self.base_calc["base_value"]

    def value(self):
        return self.base_value()

    def gratifications_to_check(self):
        try:
            item = Item.objects.get(key=self.GRATS_CHECK_KEY)

            return item.value.split(",")
        except:
            msg = f"Não há configurações das Gratificações em Painel de Controle > Configurações > Item de configuração > {self.GRATS_CHECK_KEY}."
            raise self.CalculationNotApplicable(msg)

    def get_entrys_grats(self, event):
        return Entry.objects.filter(
            contracheque__servidor=self.employee,
            contracheque__folha__periodo__ano=self.year,
            evento__numero=event,
        )

    @property
    @cached()
    def base_calc(self):
        result = {
            "base_value": 0.00,
            "qtd": 0,
        }
        if self.GRATS_CHECK_KEY is None:
            for salarie in self.extract_base_salary_by_type():
                result["qtd"] += 1
                result["base_value"] += float(salarie["value"]) / float(12)
                result["value"] = salarie["value"]
        else:
            months = 0
            total_entry = 0
            for event in self.gratifications_to_check():
                entrys = self.get_entrys_grats(event)
                if entrys.exists():
                    for entry in entrys:
                        months += 1
                        total_entry += entry.value

            result["qtd"] = months
            result["base_value"] = float(total_entry) / float(self.maximum_quantity())

        return result

    def get_possessions_from_year(self):
        possessions = self.employee.posses.filter(
            Q(financial_effect_date_start__year=self.year)
            | Q(financial_effect_date_end__year__gte=self.year)
            | Q(financial_effect_date_end__isnull=True)
        )

        return possessions.distinct()

    def get_possessions_by_type(self, types=[]):
        if not isinstance(types, list):
            types = [
                types,
            ]

        possessions = (
            self.get_possessions_from_year()
            .filter(quadro__cargo__tipo_lei_cargo__in=types)
            .order_by("-financial_effect_date_start")
        )

        return possessions

    def extract_base_salary_by_type(self):
        salaries = []
        for month in range(1, 13):
            range_month = NewDateRange.range_from_month(self.year, month)
            possessions = self.get_possessions_by_type(["EF", "AC", "CM", "FC", "EL"])
            possessions = possessions.filter(
                financial_effect_date_start__lte=range_month[1]
            ).exclude(financial_effect_date_end__lt=range_month[0])
            for p in possessions:
                if (
                    (
                        p.financial_effect_date_start < range_month[0]
                        and p.financial_effect_date_end is None
                    )
                    or (
                        p.financial_effect_date_start < range_month[0]
                        and p.financial_effect_date_end
                        and p.financial_effect_date_end > range_month[1]
                    )
                    or (
                        p.financial_effect_date_start.month == month
                        and (
                            p.financial_effect_date_end
                            and p.financial_effect_date_start.day
                            <= int((range_month[1].day / 2) + 0.5)
                        )
                        or (
                            p.financial_effect_date_end is None
                            and p.financial_effect_date_start.day
                            <= int((range_month[1].day / 2) + 0.5)
                        )
                    )
                    or (
                        p.financial_effect_date_end
                        and p.financial_effect_date_end.month == month
                        and p.financial_effect_date_end.day >= (range_month[1].day / 2)
                    )
                ):
                    if (
                        p.quadro.cargo.tipo_lei_cargo
                        in [
                            "EF",
                        ]
                        and p.servidor.tipo != "M"
                    ):
                        for prog in p.progressoes.exclude(
                            Q(data_inicio_vigencia__gt=range_month[1])
                            | (
                                ~Q(data_fim_vigencia=None)
                                & Q(data_fim_vigencia__lt=range_month[0])
                            )
                        ):
                            salaries_ = EstruturaTabelaSalarial.salarios_atualizados(
                                p.quadro.cargo
                            )
                    else:
                        salaries_ = EstruturaTabelaSalarial.salarios_atualizados(
                            p.quadro.cargo
                        )

                    for salary in salaries_:
                        if self.employee.tipo == "M":
                            value = salary[1].valor_membro
                            gratification = salary[1].gratificacao_membro
                        else:
                            value = salary[1].valor
                            gratification = salary[1].gratificacao

                        value += gratification
                        salaries.append(
                            {
                                "salary": salary[1],
                                "value": value,
                                "gratification": gratification,
                            }
                        )

        return salaries

    @cached()
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(
                Q(financial_effect_date_start__gt=self.range_salary.last)
            )
            .filter(
                Q(financial_effect_date_end=None)
                | Q(financial_effect_date_end__gte=self.range_salary.first)
            )
            .order_by("-financial_effect_date_start")
        )

        if self.employee.type_by_possession not in ("SAP", "MAP", "MAP2", "EXT", "BFP"):
            possessions = possessions.with_office_valid_in(self.range_salary)

        return possessions.distinct()

    def validate_possessions(self):
        if not self.get_possessions():
            raise self.CalculationNotApplicable(
                f"O Servidor {self.employee} não tem posses ativas no período."
            )

    def validate_type_by_possession(self):
        if self.employee.type_by_possession not in self.TYPES_BY_POSSESSION:
            raise self.CalculationNotApplicable(
                f"Essa verba só pode ser aplicada para os tipos de servidor: {self.TYPES_BY_POSSESSION}"
            )


@RunCodeManager.register("gfp-mpmt-christmas-aid-benefit-13-pensionistas")
class AidExtraBenefit13Pensionistas(AidExtraWithoutDays):

    title = "Cálculo de 13° para pensionista"

    SLUG_EXTRA_PAYMENT_FOR_AID = "BENEFICIO"

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_type_by_possession(
            [
                "BFP",
            ]
        )
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-christmas-aid-benefit-13-aposentados")
class AidExtraBenefit13Aposentados(AidExtraWithoutDays):

    title = "Cálculo de 13° para aposentados"

    SLUG_EXTRA_PAYMENT_FOR_AID = (
        "PROVENTO_MEMBRO",
        "PROVENTO_SERVIDOR",
    )

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_type_by_possession(["SAP", "MAP", "MAP2", "APO"])
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-christmas-aid-end-career-13")
class AidExtraEndCareer13(AidExtraWithoutDays):

    title = "Adicional Fim de Carreira - 13°"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ADD-FIM-CARREIRA"

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-christmas-aid-end-career-inc-ir-13")
class AidExtraEndCareerIncIr13(AidExtraWithoutDays):

    title = "Adicional Fim de Carreira - INC. IR - 13°"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ADD-FIM-CARREIRA-INC-IR"

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-christmas-aid-art37xv-13")
class AidExtraEarningsArt37XV13(AidExtraWithoutDays):

    title = "Cálculo de Vantagem Constitucional Art. 37 XV - 13°"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VANTAGEM_ART37XV"

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-christmas-aid-art37xv-inc-ir-13")
class AidExtraEarningsArt37XVIncIr13(AidExtraWithoutDays):

    title = "Cálculo de Vantagem Constitucional Art. 37 XV - INC. IR - 13°"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VANTAGEM_ART37XV-INC-IR"

    FILTER_EMPLOYEE = True

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_employee_not_in_slug_extra()
        self.validate_possessions()


@RunCodeManager.register("gfp-mpmt-aid-incorporated-vantage-13")
class AidExtraEarningsIncorporated13(AidExtraEarningsIncorporated):

    title = "Cálculo de Vantagem Incorporada - 13°"

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()


@RunCodeManager.register("gfp-mpmt-dif-submp-fc-i-13")
class SubDifferenceMPFCI13(SubDifferenceMPFCI):

    title = "Diferença Sub MP-FC-I - 13°"

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def value(self):
        return (super().value() / self.maximum_quantity()) * self.quantity()


@RunCodeManager.register("gfp-mpmt-abono-permanencia-13")
class AbonoPermanencia13(AbonoPermanencia):

    title = "Abono Permanencia - 13°"

    def maximum_quantity(self):
        return 12.00

    def quantity(self):
        return self.quantity_13_extra_pay()

    def value(self):
        return (super().value() / self.maximum_quantity()) * self.quantity()


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-pf-13")
class PrevidenciaMPMT13(PrevidenciaMPMT):

    title = "Cáluclo de Previdência MPMT - 13"

    def maximum_quantity(self):
        return 12.00


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-ii-pf-13")
class PrevidenciaIIMPMT13(PrevidenciaIIMPMT):

    title = "Cáluclo de Previdência II MPMT - 13"

    def maximum_quantity(self):
        return 12.00


@RunCodeManager.register("gfp-mpmt-christmas-salaryeffectivemember13")
class SalaryEffectiveMember13(BaseCalculation13):

    title = "Vencimento de efetivo/membro - 13°"
    GRATS_CHECK_KEY = None
    TYPES_BY_POSSESSION = [
        "MBR",
        "MBR2",
        "MEL",
        "MCM",
        "MEC",
        "MEL2",
        "MCM2",
        "MEC2",
        "EFE",
        "ECM",
        "EFC",
    ]

    def get_possessions_from_year(self):
        possessions = self.employee.posses.filter(
            Q(financial_effect_date_start__year=self.year)
            | Q(financial_effect_date_end__year__gte=self.year)
            | Q(financial_effect_date_end__isnull=True)
        )
        return possessions.distinct()

    def extract_base_salary_by_type(self):
        salaries = []
        dt_ano_vigente_fim = datetime(self.year, 12, 31).date()

        month = self.month if self.month < 13 else 12
        range_month = NewDateRange.range_from_month(self.year, month)
        possessions = self.get_possessions_by_type(
            [
                "EF",
            ]
        ).filter(
            Q(financial_effect_date_start__lte=dt_ano_vigente_fim)
            | Q(financial_effect_date_end__lte=dt_ano_vigente_fim)
        )

        p = possessions[0]
        if (
            (
                p.financial_effect_date_start < range_month[0]
                and p.financial_effect_date_end is None
            )
            or (
                p.financial_effect_date_start < range_month[0]
                and p.financial_effect_date_end
                and p.financial_effect_date_end > range_month[1]
            )
            or (
                p.financial_effect_date_start.month == month
                and (
                    p.financial_effect_date_end
                    and p.financial_effect_date_start.day
                    <= int((range_month[1].day / 2) + 0.5)
                )
                or (
                    p.financial_effect_date_end is None
                    and p.financial_effect_date_start.day
                    <= int((range_month[1].day / 2) + 0.5)
                )
            )
            or (
                p.financial_effect_date_end
                and p.financial_effect_date_end.month == month
                and p.financial_effect_date_end.day >= (range_month[1].day / 2)
            )
        ):
            if (
                p.quadro.cargo.tipo_lei_cargo
                in [
                    "EF",
                ]
                and p.servidor.tipo != "M"
            ):
                for prog in p.progressoes.exclude(
                    Q(data_inicio_vigencia__gt=range_month[1])
                    | (
                        ~Q(data_fim_vigencia=None)
                        & Q(data_fim_vigencia__lt=range_month[0])
                    )
                ):
                    salaries_ = EstruturaTabelaSalarial.salarios(
                        p.quadro.cargo,
                        range_month[0],
                        range_month[1],
                        prog.referencia_nivel2d,
                    )
            else:
                salaries_ = EstruturaTabelaSalarial.salarios(
                    p.quadro.cargo, range_month[0], range_month[1]
                )

            for salary in salaries_:
                if self.employee.tipo == "M":
                    value = salary[1].valor_membro
                    gratification = salary[1].gratificacao_membro
                else:
                    value = salary[1].valor
                    gratification = salary[1].gratificacao

                value += gratification
                salaries.append(
                    {
                        "salary": salary[1],
                        "value": value,
                        "gratification": gratification,
                    }
                )
        return salaries

    def quantity(self):
        dt_ano_vigente_inicio = datetime(self.year, 1, 1).date()
        dt_ano_vigente_fim = datetime(self.year, 12, 31).date()
        dt_range_vigente = NewDateRange(dt_ano_vigente_inicio, dt_ano_vigente_fim)

        q_works = self.employee.get_work_assignment(date=dt_ano_vigente_fim).order_by(
            "data_vigencia_inicio"
        )
        works_ranges = []
        for workplace in q_works:
            dt_fim = (
                workplace.data_vigencia_fim
                if workplace.data_vigencia_fim
                else dt_ano_vigente_fim
            )
            if dt_fim > dt_ano_vigente_inicio:
                works_ranges.append((workplace.data_vigencia_inicio, dt_fim))

        range_consolidado = NewDateRange.consolidate_ranges_of_date(works_ranges)[0]
        range_inter = dt_range_vigente.intersect(
            NewDateRange(range_consolidado[0], range_consolidado[1])
        )

        qtd = range_inter.last.month

        return qtd

    @property
    @cached()
    def base_calc(self):
        result = {
            "base_value": 0.00,
            "qtd": 0,
        }
        if self.GRATS_CHECK_KEY is None:
            salarios = self.extract_base_salary_by_type()
            valor = (
                float(salarios[0]["value"]) / self.maximum_quantity()
            ) * self.quantity()

            result["qtd"] = self.quantity()
            result["base_value"] = valor
            result["value"] = valor
        else:
            months = 0
            total_entry = 0
            for event in self.gratifications_to_check():
                entrys = self.get_entrys_grats(event)
                if entrys.exists():
                    for entry in entrys:
                        months += 1
                        total_entry += entry.value

            result["qtd"] = months
            result["base_value"] = float(total_entry) / float(self.maximum_quantity())

        return result

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_type_by_possession()


@RunCodeManager.register("gfp-mpmt-christmas-salarycommissionedcomplete13")
class SalaryCommissionedComplete13(BaseCalculation13):

    title = "Vencimento de comissionado - 13°"

    TYPES = ["CM", "EL"]
    TYPES_BY_POSSESSION = [
        "CMS",
    ]

    def validate_if_type_is_commissioned(self):
        possessions = self.get_possessions_by_type(types=self.TYPES)
        if not possessions:
            raise self.CalculationNotApplicable(
                f"O Servidor {self.employee} não possui cargo comissionado no período"
            )

    def validate_is_employee_active(self):
        if not self.employee.ativo:
            raise self.CalculationNotApplicable(
                "Essa verba só pode ser aplicada para os servidores ativos."
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_possessions()
        self.validate_if_type_is_commissioned()
        self.validate_type_by_possession()
        self.validate_is_employee_active()


@RunCodeManager.register("gfp-mpmt-christmas-anteciped13thsalary")
class AntecipedChristmasGratification(WorkDaysCalculation):

    title = "Adiantamento de 13° Salário - 1° Parcela"

    reference_entry = None

    def check_if_has_grat_entry(self):
        reference_entry = None
        q_entry = (
            Entry.objects.filter(servidor=self.employee)
            .filter(contracheque__folha__periodo__ano=self.payroll.periodo.ano)
            .filter(evento__numero__in=["01600", "02300"])
        )
        if q_entry.exists():
            reference_entry = q_entry.first()

        log.info(">>> reference_entry")
        log.info(reference_entry)
        return reference_entry

    def validate_if_has_grat_entry(self):
        if self.reference_entry is None:
            raise self.CalculationNotApplicable(
                "O servidor não possui nenhuma das verbas aplicadas em seu Contra Cheque: 01600 ou 02300"
            )

    def validate(self):
        self.validate_possessions()
        self.reference_entry = self.check_if_has_grat_entry()
        self.validate_if_has_grat_entry()

    def quantity(self):
        return self.reference_entry.qnt

    def maximum_quantity(self):
        return self.reference_entry.qnt_max

    def percentage(self):
        return self.reference_entry.pct

    def installment(self):
        return self.reference_entry.parcela

    def installments_paid(self):
        return self.reference_entry.prazo

    def base_socialsecurity(self):
        return self.reference_entry.base_previdencia

    def employer_value(self):
        return self.reference_entry.patronal

    def base_value(self):
        return self.reference_entry.valor_base

    def value(self):
        return self.reference_entry.correct_value


@RunCodeManager.register("gfp-mpmt-christmas-socialsecurity-igeprev-inativo-13-pf")
class PrevidenciaInativo13MPMT(PrevidenciaInativoMPMT):

    title = "Cáluclo de Previdência para inativos sobre 13°MPMT"


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-compl-pf-13")
class PrevidenciaComplementarMPMT13(PrevidenciaComplementarMPMT):

    title = "Cáluclo de Previdência Complementar MPMT - 13°"

    def maximum_quantity(self):
        return 12.00


@RunCodeManager.register("gfp-mpmt-christmas-irrf-13")
class IRRF13(IRRF):

    title = "Calculo de imposto retido na fonte sobre 13"


@RunCodeManager.register("gfp-mpmt-redutor-teto-13")
class ReduceSalaryCap13(ReduceSalaryCap):

    title = "Redutor de Teto Constitucional - 13°"

    def maximum_quantity(self):
        return 12.00


@RunCodeManager.register("gfp-mpmt-christmas-socialsecurity-inss-base-13")
class INSSBase13(INSS):

    title = "Base calculo de previdencia social INSS - 13°"

    def get_possessions_from_year(self):
        possessions = self.employee.posses.filter(
            Q(financial_effect_date_start__year=self.year)
            | Q(financial_effect_date_end__year=self.year)
            | Q(financial_effect_date_end__isnull=True)
        )

        return possessions.distinct()

    def get_possessions_by_type(self, types=[]):
        if not isinstance(types, list):
            types = [
                types,
            ]

        possessions = (
            self.get_possessions_from_year()
            .filter(quadro__cargo__tipo_lei_cargo__in=types)
            .order_by("-financial_effect_date_start")
        )

        return possessions


@RunCodeManager.register("gfp-mpmt-christmas-socialsecurity-inss-commissioned-13")
class INSSCommissioned13(INSSBase13):

    title = "Calculo de previdencia social INSS para comissionados - 13°"

    TYPES = ["CM", "EL"]

    def validate_if_type_is_commissioned(self):
        possessions = self.get_possessions_by_type(types=self.TYPES)
        if not possessions:
            raise self.CalculationNotApplicable(
                f"O Servidor {self.employee} não possui cargo comissionado no período"
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_ssc_is_inss_rgps()
        self.validate_if_type_is_commissioned()


@RunCodeManager.register("gfp-mpmt-average-member-13")
class AverageMember13(BaseCalculation13):

    title = "Calculo da Média de Gratificações de Membros - 13°"

    GRATS_CHECK_KEY = "average_gratifications_member"

    TYPES_BY_POSSESSION = ["MBR", "MBR2", "MEL", "MCM", "MEC", "MEL2", "MCM2", "MEC2"]

    def validate(self):
        self.validate_type_by_possession()
        self.validate_not_paycheck_pension()
        self.validate_possessions()
        self.gratifications_to_check()


@RunCodeManager.register("gfp-mpmt-average-effective-13")
class AverageEffective13(BaseCalculation13):

    title = "Calculo da Média de Gratificações de Efetivos - 13°"

    GRATS_CHECK_KEY = "average_gratifications_effective"

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_possessions()
        self.gratifications_to_check()


@RunCodeManager.register("gfp-mpmt-average-member-effective-13")
class AverageMemberEffective13(BaseCalculation13):

    title = "Calculo da Média de Gratificações para Membros e Efetivos - 13°"

    GRATS_CHECK_KEY = "average_gratifications_member_effective"

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_possessions()
        self.gratifications_to_check()


@RunCodeManager.register("gfp-mpmt-socialsecurity-igeprev-iii-pf-13")
class PrevidenciaIIIMPMT13(PrevidenciaIIIMPMT):

    title = "Cáluclo de Previdência III MPMT"

    def maximum_quantity(self):
        return 12

    def quantity(self):
        dt_ano_vigente_inicio = datetime(self.year, 1, 1).date()
        dt_ano_vigente_fim = datetime(self.year, 12, 31).date()
        dt_range_vigente = NewDateRange(dt_ano_vigente_inicio, dt_ano_vigente_fim)

        q_works = self.employee.get_work_assignment(date=dt_ano_vigente_fim).order_by(
            "data_vigencia_inicio"
        )
        works_ranges = []
        for workplace in q_works:
            dt_fim = (
                workplace.data_vigencia_fim
                if workplace.data_vigencia_fim
                else dt_ano_vigente_fim
            )
            if dt_fim > dt_ano_vigente_inicio:
                works_ranges.append((workplace.data_vigencia_inicio, dt_fim))

        range_consolidado = NewDateRange.consolidate_ranges_of_date(works_ranges)[0]
        range_inter = dt_range_vigente.intersect(
            NewDateRange(range_consolidado[0], range_consolidado[1])
        )

        qtd = range_inter.last.month

        return qtd
