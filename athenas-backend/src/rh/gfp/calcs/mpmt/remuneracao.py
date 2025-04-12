# -*- coding: utf-8 -*-

from datetime import date, datetime
from calendar import monthrange

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count
from memoization import cached

from contrib.cache import get_cache, set_cache
from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento, AfastamentoOutroOrgao
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.calcs.mpmt.base import BaseCalculation, WorkDaysCalculation
from rh.gfp.models import EstruturaTabelaSalarial, ExtraPaymentPeriod, Periodo
from rh.gfp.models import FolhaEvento as Entry, Evento
from rh.models import (
    CargaHoraria,
    EncargoFinanceiro as FinancialBurden,
    MovimentacaoSubstituicao as SubstitutionMovement,
    Cargo,
    WorkplaceConfigTag,
    MovimentacaoAuxiliarCoordenacao,
    ServidorLotacao,
)
from standard.models import RunCodeManager, Choice, Item
from rh.afastamento.afastamento_utils import buscar_afastamentos_periodo

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-basesalary")
class BaseSalary(WorkDaysCalculation):
    title = "Calculo Base para remuneração"
    description = """
        Este cálculo pode ser usado como base para remuneração em geral.
        Se for usado diretamente será retornado o valor da remuneração total
        do servidor (efetivo + (função ou (gratification + comissão) + eletivo + extras)
    """

    INCLUDE_EXTRASPAYMENTS = [
        "VPI",
    ]
    FULL_SALARY = False
    FILTER_CID = 2

    TYPES = ["EF", "AC", "CM", "FC", "EL"]

    """
    Exclude from extract_base_salary_by_type the possessions with match the pairs of type employee(M/S/E) -
    p.servidor.tipo and type of job position('EF', 'AC', 'CM', 'FC', 'EL') - p.quadro.cargo.tipo.
    Ex.: EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {'M': ['CM', 'EL']} # this config exclude all salaries
    comissioned or efective of members
    """

    def get_extras(self, start_date=None, end_date=None):
        start_date = self.range_salary.first if not start_date else start_date
        end_date = self.range_salary.last if not end_date else end_date

        return (
            ExtraPaymentPeriod.objects.filter(
                employee=self.employee,
                extra_payment__slug__in=self.INCLUDE_EXTRASPAYMENTS,
            )
            .exclude(
                Q(start_validity__gt=end_date)
                | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
            )
            .order_by("start_validity")
        )

    def extract_base_salary_by_type(self):
        cache_id = "CSPM%s%s%s%s" % (
            "I" if self.IGNORE_DEPARTURE else "",
            self.identification_payroll,
            self.employee.matricula,
            "".join(
                "%06d%06d" % (t[0], t[1]) for t in self.range_salary_for().toordinals()
            ),
        )

        # if get_cache(cache_id, self.group_key_cache):
        #     return get_cache(cache_id, self.group_key_cache)

        salaries = {}
        for p in self.get_possessions_by_type(["EF", "AC", "CM", "FC", "EL"]):
            range_ = self.range_salary_for(p)

            if (
                p.quadro.cargo.tipo_lei_cargo
                in [
                    "EF",
                ]
                and not p.servidor.tipo == "M"
            ):
                for prog in p.progressoes.exclude(
                    Q(data_inicio_vigencia__gt=self.range_salary.last)
                    | (
                        ~Q(data_fim_vigencia=None)
                        & Q(data_fim_vigencia__lt=self.range_salary.first)
                    )
                ):
                    range_prog = range_.intersect(
                        NewDateRange(prog.data_inicio_vigencia, prog.data_fim_vigencia)
                    )
                    salaries_ = EstruturaTabelaSalarial.salarios(
                        p.quadro.cargo,
                        range_prog.first,
                        range_prog.last,
                        prog.referencia_nivel2d,
                    )
                    for salary in salaries_:
                        idx = "%s%s" % (
                            p.quadro.cargo.tipo_lei_cargo,
                            salary[1].sigla_cache,
                        )
                        if idx not in salaries:
                            salaries[idx] = []
                        range_prog_salary = range_prog.intersect(salary[0])
                        extras = self.get_extras(
                            range_prog_salary.first, range_prog_salary.last
                        )
                        for extra in extras:
                            # log.debug(extra)
                            range_extra = range_prog_salary.intersect(
                                NewDateRange(extra.start_validity, extra.end_validity)
                            )
                            salaries[idx].append(
                                {
                                    "range": range_extra.toordinals(),
                                    "salary": salary[1],
                                    "type": p.quadro.cargo.tipo_lei_cargo,
                                    "value": salary[1].valor,
                                    "gratification": salary[1].gratificacao,
                                    "extra": extra.value,
                                    "percentage": False,
                                    "onus": True,
                                }
                            )
                        else:
                            if not extras:
                                salaries[idx].append(
                                    {
                                        "range": range_prog_salary.toordinals(),
                                        "salary": salary[1],
                                        "type": p.quadro.cargo.tipo_lei_cargo,
                                        "value": salary[1].valor,
                                        "gratification": salary[1].gratificacao,
                                        "extra": 0.0,
                                        "percentage": False,
                                        "onus": True,
                                    }
                                )

            elif p.quadro.cargo.tipo_lei_cargo in [
                "AC",
            ]:
                idx = "ACREQ"
                for ef in FinancialBurden.objects.filter(request_move=p).exclude(
                    Q(data_inicio__gt=self.range_salary.last)
                    | (~Q(data_fim=None) & Q(data_fim__lt=self.range_salary.first))
                ):
                    if idx not in salaries:
                        salaries[idx] = []
                    range_ac = range_.intersect(
                        NewDateRange(ef.data_inicio, ef.data_fim)
                    )
                    salaries[idx].append(
                        {
                            "range": range_ac.toordinals(),
                            "salary": None,
                            "value": ef.remuneracao,
                            "gratification": 0.00,
                            "type": p.quadro.cargo.tipo_lei_cargo,
                            "extra": 0.0,
                            "percentage": False,
                            "onus": (
                                ef.requisicao.onus == 2 if ef.requisicao else None
                            ),  # Onus para requisitante?
                        }
                    )

            else:
                salaries_ = EstruturaTabelaSalarial.salarios(
                    p.quadro.cargo, self.range_salary.first, self.range_salary.last
                )
                for salary in salaries_:
                    idx = "%s%s" % (
                        p.quadro.cargo.tipo_lei_cargo,
                        salary[1].sigla_cache,
                    )
                    if idx not in salaries:
                        salaries[idx] = []
                    range_cm = range_.intersect(salary[0])
                    value = (
                        salary[1].valor
                        if not self.employee.tipo == "M"
                        else salary[1].valor_membro
                    )
                    gratification = (
                        salary[1].gratificacao
                        if not self.employee.tipo == "M"
                        else salary[1].gratificacao_membro
                    )
                    currency_employee = (
                        salary[1].referencia_nivel2d.tipo_gratificacao == 1
                        and self.employee.tipo != "M"
                    )
                    currency_member = (
                        salary[1].referencia_nivel2d.tipo_gratificacao_membro == 1
                        and self.employee.tipo == "M"
                    )
                    percentage = False if currency_member or currency_employee else True
                    if not percentage and not p.quadro.cargo.chefia:
                        value += gratification
                        gratification = 0
                    salaries[idx].append(
                        {
                            "range": range_cm.toordinals(),
                            "salary": salary[1],
                            "type": p.quadro.cargo.tipo_lei_cargo,
                            "value": value,
                            "gratification": gratification,
                            "extra": 0.0,
                            "percentage": percentage,
                            "onus": True,
                        }
                    )

        set_cache(cache_id, salaries, self.group_key_cache)

        return salaries

    def extract_base_salary_by_period(self):
        """ """
        cache_id = "CSP%s%s%s" % (
            self.identification_payroll,
            self.employee.matricula,
            "".join(str(t or "000000") for t in self.validity.toordinals()),
        )

        # if get_cache(cache_id, self.group_key_cache):
        #     return get_cache(cache_id, self.group_key_cache)

        salaries = self.extract_base_salary_by_type()
        ranges = {}
        for key in salaries:
            for salary in salaries[key]:
                aux = NewDateRange.fromordinals(salary["range"])
                # salaries_aux = {salary['type']: salary['salary']}
                salaries_aux = {
                    salary["type"]: {
                        "id": key,
                        "ref": salary["salary"],
                        "value": salary["value"],
                        "gratification": salary["gratification"],
                        "extra": salary["extra"],
                        "percentage": salary["percentage"],
                        "onus": salary["onus"],
                    }
                }
                r = 0
                # log.debug('>>> KEY: %s/%s' % (key, aux))
                while r < len(ranges) and aux.days:  # r in ranges:
                    inter = ranges[r]["range"].intersect(aux)
                    # dif = (ranges[r]['range'] - aux) if inter.days > 0 else ranges[r]['range']
                    if inter.days:
                        if inter == ranges[r]["range"]:
                            ranges[r]["salaries"].update(salaries_aux)
                            aux = aux - inter
                        elif inter == aux:
                            # Retirando o inter de dentro do range corrente (r)
                            ranges[r]["range"] = ranges[r]["range"] - inter
                            # Criando o novo range da intersecao
                            # salaries_aux.update(ranges[r]['salaries'])
                            idx = len(ranges)
                            salaries_copy = ranges[r]["salaries"].copy()
                            salaries_copy.update(salaries_aux)
                            ranges[idx] = {"salaries": salaries_copy, "range": inter}
                            # Retirando o interseçao do AUX
                            aux = aux - inter
                        else:
                            # Retirando o inter de dentro do range corrente (r)
                            ranges[r]["range"] = ranges[r]["range"] - inter
                            # Criando o novo range da intersecao
                            # salaries_aux.update(ranges[r]['salaries'])
                            idx = len(ranges)
                            salaries_copy = ranges[r]["salaries"].copy()
                            salaries_copy.update(salaries_aux)
                            ranges[idx] = {"salaries": salaries_copy, "range": inter}
                            # Retirando o interseçao do AUX
                            aux = aux - inter
                    r += 1
                idx = len(ranges)
                if aux.days:
                    ranges[idx] = {"salaries": salaries_aux, "range": aux}

        ranges__ = []
        # Verificando se necessita avaliar se os ranges podem ser normatizados, que são exceções,
        # para não ficar fazedo avalizações desnecessárias na maioria dos casos em que o calculo
        # tem o range_base igual ao range_salary, ou seja, o servidor trabalhou o mes completo
        # log.debug('RANGE BASE: %s (%s)' % (self.range_base, self.employee))
        normatize_left_days = 0
        normatize_rigth_days = 0
        if self.range_base.days != 0 and self.range_salary.days != 0:
            normatize_left_days = (self.range_base.first - self.range_salary.first).days
            normatize_rigth_days = (self.range_salary.last - self.range_base.last).days
        for value in ranges.values():
            formated_ = {"range": value["range"].toordinals()}
            for tipo in value["salaries"]:
                normatize_days = 0
                # log.debug('%s: %s = %s' % (value['salaries'][tipo]['id'], value['range'].last, self.range_base.last))
                base_gratification = float(value["salaries"][tipo]["gratification"])
                gratification = (
                    base_gratification  # * value['range'].days / self.base_days
                )
                pct_grat = 0.00
                if value["salaries"][tipo]["percentage"]:
                    pct_grat = float(value["salaries"][tipo]["gratification"])
                    ef = value["salaries"].get("EF", value["salaries"].get("AC", None))
                    base_gratification = float(ef["value"])
                    gratification = base_gratification * (
                        pct_grat / 100.0
                    )  # * (value['range'].days / self.base_days)

                if normatize_left_days or normatize_rigth_days:
                    normatize_days += (
                        normatize_left_days
                        if value["range"].first == self.range_base.first
                        else 0
                    )
                    normatize_days += (
                        normatize_rigth_days
                        if value["range"].last == self.range_base.last
                        else 0
                    )

                normal_factor_quantity = round(
                    float(value["range"].days + normatize_days) / self.base_days, 8
                )
                # log.debug(f'>>>> {self.event.numero} normal_factor_quantity: {normal_factor_quantity} {value["salaries"][tipo]["value"]}')
                factor_quantity = round(float(value["range"].days) / self.base_days, 8)
                formated_[tipo] = {
                    "id": value["salaries"][tipo]["id"],
                    "reference": value["salaries"][tipo]["ref"],
                    "base_value": float(value["salaries"][tipo]["value"]),
                    "base_gratification": base_gratification,
                    "normal_value": float(value["salaries"][tipo]["value"])
                    * normal_factor_quantity,
                    "normal_gratification": gratification * normal_factor_quantity,
                    "normal_extra": float(value["salaries"][tipo]["extra"])
                    * normal_factor_quantity,
                    "value": float(value["salaries"][tipo]["value"]) * factor_quantity,
                    "extra": float(value["salaries"][tipo]["extra"]) * factor_quantity,
                    "days": value["range"].days,
                    "gratification": gratification,
                    "percentage": pct_grat,
                }
                # log.debug('>>> NFQ(%s): %s' % (
                #     normal_factor_quantity,
                #     formated_[tipo]
                # ))
            ranges__.append(formated_)

        # log.debug('%s: %s' % (cache_id, ranges__))
        set_cache(cache_id, ranges__, self.group_key_cache)

        return ranges__

    def base_salary_for_type(self, type_):
        cache_id = "CBS%s%s%s" % (
            self.identification_payroll,
            self.employee.matricula,
            type_,
        )

        # if get_cache(cache_id, self.group_key_cache):
        # return get_cache(cache_id, self.group_key_cache)

        periods = self.extract_base_salary_by_period()
        base_value = base_gratification = days = 0
        for range_ in periods:
            if range_.get(type_):
                base_value += range_.get(type_).get("value", 0)
                base_gratification += range_.get(type_).get("gratification", 0)
                days += range_.get(type_).get("days", 0)

        salary = {
            "value": base_value,
            "gratification": base_gratification,
            "days": days,
            "base_value": ((base_value / days) * self.base_days) if days else 0.0,
            "base_gratification": (
                ((base_gratification / days) * self.base_days) if days else 0.0
            ),
        }
        set_cache(cache_id, salary, self.group_key_cache)

        return salary

    def _get_query(self):
        if self.params.get("oIds"):
            return [
                _id
                for _id in self.extract_base_salary_by_type()
                if _id in self.params.get("oIds") and _id[0:2] in self.TYPES
            ]
        return list(self.extract_base_salary_by_type().keys())

    @cached()
    def base_salary(self):
        total = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "normal_base_value": 0.0,
            "normal_base_gratification": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "normal_base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
            "normal_base_extra": 0.0,
        }
        salaries = self.extract_base_salary_by_period()

        for salary in salaries:
            if self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(self.employee.tipo, []):
                ef_ = salary.get("EF", salary.get("AC", {}))
                if "CM" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                    self.employee.tipo, False
                ):
                    cm_ = salary.get("CM", {})
                elif "FC" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                    self.employee.tipo, False
                ):
                    cm_ = salary.get("FC", {})
                elif "EL" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                    self.employee.tipo, False
                ):
                    cm_ = salary.get("EL", {})
                else:
                    cm_ = {}
            else:
                ef_ = salary.get("EF", salary.get("AC", {}))
                cm_ = salary.get("CM", salary.get("FC", salary.get("EL", {})))

            # log.debug('BASE SALARY >> EF: %s CM: %s' % (ef_, cm_))
            range_ = NewDateRange.fromordinals(salary["range"])
            total["gratification"] += cm_.get("gratification", 0.00)
            total["normal_base_extra"] += ef_.get("normal_extra", 0.00)
            total["normal_base_gratification"] += cm_.get("normal_gratification", 0.00)
            total["days"] += range_.days
            value = (
                (ef_.get("value", 0.00) + ef_.get("normal_extra", 0.00))
                if (ef_.get("value", 0.00) + ef_.get("normal_extra", 0.00))
                > cm_.get("value", 0.00)
                else cm_.get("value", 0.00)
            )
            normal_value = (
                (ef_.get("normal_value", 0.00) + ef_.get("normal_extra", 0.00))
                if (ef_.get("normal_value", 0.00) + ef_.get("normal_extra", 0.00))
                > cm_.get("normal_value", 0.00)
                else cm_.get("normal_value", 0.00)
            )
            # normal_base_value = (ef_.get('normal_value', 0.00) + ef_.get('normal_extra', 0.00)) if ef_.get('id', '') in\
            #     self.oIds else 0
            total["value"] += value
            total["normal_base_value"] += normal_value

            # RGPS: NESSE REGIME A BASE É TODA REMUNERAÇÃO, OU SEJA, EF + CM
            if self.employee.regime_previdenciario == 1:
                total["base_socialsecurity"] += cm_.get("gratification", 0.00) + value
                total["normal_base_socialsecurity"] += (
                    cm_.get("normal_gratification", 0.00) + normal_value
                )
            else:
                total["base_socialsecurity"] += ef_.get("value", 0.00) + ef_.get(
                    "extra", 0.00
                )
                total["normal_base_socialsecurity"] += ef_.get(
                    "normal_value", 0.00
                ) + ef_.get("normal_extra", 0.00)

            # Removendo remuneração extra caso o valor da soma do extra e da base for menor que o valor do comissionado
            total["normal_base_extra"] = (
                total["normal_base_extra"]
                if (ef_.get("value", 0.00) + ef_.get("normal_base_extra", 0.00))
                > cm_.get("value", 0.00)
                else 0.00
            )

        # factor = (float(self.base_days) / total['days']) if total['days'] else 0.0
        total["base_value"] = total["normal_base_value"]
        total["normal_base_value"] = (
            total["normal_base_value"]
            if total["normal_base_value"] > 0
            else total["base_value"]
        )
        total["base_gratification"] = total["normal_base_gratification"]
        total["full_base_socialsecurity"] = total["normal_base_socialsecurity"]
        total["base_extra"] = total["normal_base_extra"]
        total["base_days"] = self.base_days

        return total

    @cached()
    def _base_values(self):
        if "base_value" in self.params:
            return float(self.params["base_value"]), float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return (
                float(self.event.base_value_at(self.range_salary.first)),
                float(self.event.base_value_at(self.range_salary.first)),
            )

        base = self.base_salary()
        if self.FULL_SALARY:
            total_base = (
                base["base_value"] + base["base_gratification"]
            )  # + base['base_extra']
        else:
            total_base = base["value"] + base["gratification"]
        total_base_socialsecurity = base["full_base_socialsecurity"]

        if not self.event:
            return total_base, total_base_socialsecurity

        for fe in self.base_value_query():
            value = 0
            base_socialsecurity = 0
            # if fe.evento.automatico and fe.classcode and not issubclass(fe.classcode.cls, BaseSalary):
            if (
                fe.evento.automated
                and fe.classcode
                and (
                    fe.reference_year != self.range_salary.first.year
                    or fe.reference_month != self.range_salary.first.month
                )
            ):
                # log.debug('CALCULATING %2d-%4d: %s' % (self.range_salary.first.year,
                #                                        self.range_salary.first.month,
                #                                        fe.classcode.cls))
                params = {
                    "pct": fe.pct,
                    "qnt": fe.qnt,
                    "info": fe.info,
                    "patronal": fe.patronal,
                    "valor_base": fe.valor_base,
                }
                params.update(fe.vars)
                calc = fe.classcode.cls(
                    self.employee,
                    self.reference_payroll,
                    fe.evento,
                    year=self.range_salary.first.year,
                    month=self.range_salary.first.month,
                    params=params,
                    only_events=self.focuses_on,
                    group_cache=self.group_key_cache,
                    entry=fe,
                    pension=fe.contracheque.pensioner,
                )
                value = self._value_calc_normatized(calc)
                base_socialsecurity = calc.base_socialsecurity()
                value = value if fe.evento.tipo == "P" else -value
                base_socialsecurity = (
                    base_socialsecurity
                    if fe.evento.tipo == "P"
                    else -base_socialsecurity
                )
                # if self.FULL_SALARY and fe.evento.tipo_calculo not in (1, ):
                #     value = ((value / self.factor_quantity()) if self.factor_quantity() else 0.0)
                #     base_socialsecurity = ((base_socialsecurity / self.factor_quantity())
                #                            if self.factor_quantity() else 0.0)
            else:
                value = float(
                    fe.correct_valor if fe.evento.tipo == "P" else -fe.correct_valor
                )
                base_socialsecurity = float(
                    fe.correct_base_previdencia
                    if fe.evento.tipo == "P"
                    else -fe.correct_base_previdencia
                )

            total_base += value
            total_base_socialsecurity += base_socialsecurity
        base_value = total_base - self.base_discounts()

        return (
            (base_value, total_base_socialsecurity)
            if not self.event.calculo_invertido
            else (-base_value, -total_base_socialsecurity)
        )

    @cached()
    def base_value(self):
        base_value = self._base_values()[0]
        return min(base_value, self.ceiling_base_value)

    @cached()
    def quantity_13(self):
        # vai pro base salary; avaliar self._is_christmas_grat
        log.info(self.range_13salary)
        range_period = self.range_13salary
        qtd = 0
        for month in range(12):
            range_month = range_period.intersect(
                NewDateRange.from_month(self.year, month + 1)
            )
            if range_month.days >= 15:
                qtd += 1

        return qtd

    def quantity(self):
        return (
            self.base_salary()["days"]
            if not self._is_christmas_grat
            else self.quantity_13()
        )

    def base_socialsecurity(self):
        return self._base_values()[1]  # * self.factor_quantity()

    def _event_information(self, types=[]):
        info = []
        salaries = self.extract_base_salary_by_period()
        for salary in salaries:
            for type_ in types:
                if type_ in salary:
                    info.append("%s" % salary[type_]["reference"].sigla_cache)
        return "-".join(info)

    @property
    @cached()
    def range_calc(self):
        mdr = NewDateRange()
        list_ = self.extract_base_salary_by_type().get(self.object, [])
        for k in list_:
            mdr += NewDateRange.fromordinals(k["range"])
        return mdr


@RunCodeManager.register("gfp-mpmt-salaryalaryeffective")
class SalaryEffective(BaseSalary):
    title = "Remuneração de efetivo apenas"
    description = """
        Este cálculo retorna o valor do salário de efetivo, caso o servidor seja efetivo, ou seja,
        apenas o valor da tabela salarial do cargo efetivo do servidor.
    """

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    FILTER_CID = 2

    TYPES = ["EF", "AC", "EL"]

    @property
    @cached()
    def object(self):
        ids = self.get_query()
        if "ELSUPPGJ" in ids and "EFPROMFIN" in ids:
            return "ELSUPPGJ"
        else:
            if len(ids) == 1:
                return ids[0]
            return None

    def _get_query(self):
        ids = super(SalaryEffective, self)._get_query()

        if "ELSUPPGJ" in ids and "EFPROMFIN" in ids:
            return ["ELSUPPGJ"]
        else:
            return [id_ for id_ in ids if id_[0:2] in self.TYPES]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "EF" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é efetivo no período" % (self.employee)
            )

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days
            base_value = salarie["value"]
        log.debug(f"dt days: {days} e base_days: {self.base_days}")
        return base_value, days

    def quantity(self):
        qtd = self._base_value[1] if not self._is_christmas_grat else self.quantity_13()

        return qtd if qtd <= self.maximum_quantity() else self.maximum_quantity()

    def base_value(self):
        return float(self._base_value[0])

    def base_socialsecurity(self):
        base_salary = self.extract_base_salary_by_type()
        if "ELSUPPGJ" in base_salary.keys() and "EFPROMFIN" in base_salary.keys():
            for salarie in base_salary["EFPROMFIN"]:
                base_ss = salarie["value"]

            return float(base_ss)
        else:
            return self.value()

    def event_information(self):
        return "" if self.object is None else str(self.object[2:])

    def normal_value(self):
        return (
            self.base_salary()["normal_base_value"]
            - self.base_salary()["normal_base_extra"]
        )

    def full_value(self):
        return self.normal_value()

    @cached()
    def value(self):
        if self._is_christmas_grat:
            fquantity_days = float(self._base_value[1]) / float(self.base_days)
            base_value = float(self._base_value[0]) * (fquantity_days)
            value = (
                base_value
                * (float(self.percentage()) / 100.00)
                * self.factor_quantity()
            )
            if value:
                value = min(value, self.ceiling)
                value = max(value, self.floor)
            return value
        else:
            return super().value()

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = super()._exclude_ranges_for_range_salary(range_salary=range_salary)
        tipos = [18, 44]
        map_suspend_after = {}

        if self.employee.type_by_possession in ["CMS", "EFE", "ECM", "EFC"]:
            tipos = [9, 10, 11, 14, 16, 18, 37, 44]
            if self.employee.type_by_possession != "CMS":
                tipos = [11, 14, 16, 18, 44]

            map_suspend_after = {
                9: 15,  # Licença saúde 30 dias
                10: 15,  # Licença saúde junta médica
                11: 5,  # Licença saúde pessoa da familia suspender após 5 dias
                37: 15,  # Licença saúde
            }

        q = (
            self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            )
            .filter(Q(tipo__in=tipos))
            .filter(~Q(afastamento__afastamentooutroorgao__transito_pela_folha=True))
        )

        if map_suspend_after:
            for l in q.filter():
                days_suspend_after = map_suspend_after.get(l.tipo, 0)
                dt_start = l.data_inicio + relativedelta(days=days_suspend_after)
                if dt_start <= l.data_fim:
                    range_ += NewDateRange(dt_start, l.data_fim)
                    log.info(f"dias: {range_}")
                elif not days_suspend_after == 0:
                    range_ = NewDateRange(0, 0)

        return range_


@RunCodeManager.register("gfp-mpmt-salaryrequested")
class SalaryRequested(BaseSalary):
    title = "Remuneração de servidor requisitado"
    description = """
    """

    INCLUDE_EXTRASPAYMENTS = ["VPI", "INCENTIVO-A-DOCENCIA"]
    FILTER_CID = 2
    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    TYPES = [
        "AC",
    ]

    def _get_query(self):
        ids = super()._get_query()
        log.info(ids)
        return [id_ for id_ in ids if id_[0:2] in self.TYPES]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "AC" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é requisitado no período" % (self.employee)
            )

    def quantity(self):
        return (
            self.base_salary_for_type("AC").get("days")
            if not self._is_christmas_grat
            else self.quantity_13()
        )

    def base_value(self):
        return self.base_salary_for_type("AC").get("base_value")

    def base_socialsecurity(self):
        return self.value()

    @property
    @cached()
    def range_calc(self):
        mdr = NewDateRange()
        list_ = self.extract_base_salary_by_type().get("ACREQ")
        for k in list_:
            mdr += NewDateRange.fromordinals(k["range"])
        return mdr


@RunCodeManager.register("gfp-mpmt-gratificationfunction")
class GratificationFunction(SalaryEffective):
    title = "Gratificação de função de confiança"
    description = """
    Usado exclusivamente para quem possui função de confiança.
    O calculo retornará o valor da gratificação da função proporcional aos
    dias trabalhos com a função!
    """

    TYPES = [
        "FC",
    ]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "FC" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui função de confiança no período"
                % (self.employee)
            )

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0, 0.0

        # _type = self.object[0:2]
        base_value = pct = 0.00
        days = 0
        salaries = self.extract_base_salary_by_period()
        count = 0
        is_equal = True
        last_base = 0

        for salary in salaries:
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                count += 1
                if not last_base:
                    last_base = salary[self.object[0:2]]["base_gratification"]
                elif salary[self.object[0:2]]["base_gratification"] != last_base:
                    is_equal = False
        for salary in salaries:
            dr = NewDateRange.fromordinals(salary["range"])
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                if count > 1 and not is_equal and not self._is_christmas_grat:
                    base_value += (
                        salary[self.object[0:2]]["base_gratification"]
                        / self.payroll.date_range.days
                        * dr.days
                    )
                else:
                    base_value = salary[self.object[0:2]]["base_gratification"]
                    log.info(f"{self.object[0:2]} {salary[self.object[0:2]]} {dr}")
                pct = salary[self.object[0:2]]["percentage"]
                days += dr.days

        return base_value, days, pct

    def percentage(self):
        return float(self._base_value[2]) or 100.0

    def base_socialsecurity(self):
        base_socialsecurity = super(GratificationFunction, self).base_socialsecurity()
        return (
            base_socialsecurity
            if self.employee.regime_previdenciario
            in [
                1,
            ]
            else 0.0
        )

    def normal_value(self):
        return self.base_salary()["normal_base_gratification"]

    @cache_return
    def value(self):
        return super(BaseSalary, self).value()


@RunCodeManager.register("gfp-mpmt-salarycommissioned")
class SalaryCommissioned(SalaryEffective):
    title = "Vencimento de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão ou eletivo (Ex.: DAM, PGJ, AEPGJ, CGJ, etc).
    O calculo retornará o valor da parte vencimental do cargo, proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    @property
    @cached()
    def range_13salary(self):
        # vai pro base salary
        year = NewDateRange(datetime(self.year, 1, 1), datetime(self.year, 12, 31))
        range_year = self.range_maternity() if self.is_range_maternity_on_13() else year
        return self.range_salary_for(
            range_salary=range_year, get_possessions_from13=True
        )

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days
            base_value = salarie["value"]

        return base_value, days

    @cached()
    def value(self):
        return super(BaseSalary, self).value()

    @cached()
    def is_range_maternity_on_13(self):
        intersect_range = super()._intersect_ranges_for_range_salary()
        range_ = self.range_maternity()
        result = False
        if intersect_range.intersect(range_).days >= self.range_salary.days:
            result = True

        return result

    def range_maternity(self):
        range_ = NewDateRange()
        if not self.employee.is_efetivo:
            query_advances_maternity = self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            ).filter(tipo=12)
            for lm in query_advances_maternity:
                # Excluindo os periodos de salario maternidade (INSS - 120 dias)
                # range_ += NewDateRange(lm.data_inicio, min(lm.data_fim, lm.data_inicio + relativedelta(days=119)))
                range_ += NewDateRange(lm.data_inicio, lm.data_fim)
        return range_

    def validate(self):
        self.validate_not_paycheck_pension()
        if not set(self.employee_types).intersection(["CM", "EL"]):
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui cargo comissionado no período"
                % (self.employee)
            )
        if set(self.employee_types).intersection(["AC", "EF"]):
            raise self.CalculationNotApplicable(
                "Essa verba é para servidor exclusivamente comissionado!"
            )

    # Removendo exclusão de range de datas - MPMT continua pagando para servidoras em licença maternidade
    # @cached()
    # def _exclude_ranges_for_range_salary(self, range_salary=None):
    #     range_ = NewDateRange()
    #     if not set(self.employee_types).intersection(['AC', 'EF']):
    #         # if self.is_range_maternity_on_13() or not self._is_christmas_grat:
    #         range_ = self.range_maternity()

    #     # print(f'>>>> CALCULANDO RSF ERFRS: {self._exclude_ranges_for_range_salary()}')
    #     return range_ + super(SalaryCommissioned, self)._exclude_ranges_for_range_salary(range_salary=range_salary)


@RunCodeManager.register("gfp-mpmt-salarycommissionedcomplete")
class SalaryCommissionedComplete(SalaryCommissioned):

    title = "Vencimento de comissionado Completo"

    description = """
    Usado exclusivamente para quem possui cargo em comissão ou eletivo (Ex.: DAM, PGJ, AEPGJ, CGJ, etc).
    O calculo retornará o valor da parte vencimental e gratificação do cargo, proporcional aos
    dias trabalhos no mesmo!
    """

    TYPES = ["CM", "EL"]

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days
            base_value = salarie["value"] + salarie["gratification"]
        log.debug(f"dt days: {days} e base_days: {self.base_days}")

        q = self.payroll.lancamentos.filter(
            servidor=self.employee, evento__numero="04000"
        )

        if q.exists():
            days = days - q.first().qnt

        return base_value, days


@RunCodeManager.register("gfp-mpmt-maternitypay")
class MaternitySalary(SalaryCommissioned):
    title = "Salário Maternidade"
    description = """
    Usado exclusivamente para quem possui exclusivamente cargo em comissão(Ex.: DAM, AEPGJ, etc) e .
    está em licença maternidade. O calculo retornará o valor da parte vencimental +
    gratificação do cargo, proporcional aos dias de licença no periodo!
    """
    TYPES = [
        "CM",
    ]

    @property
    @cached()
    def range_13salary(self):
        # vai pro base salary
        year = NewDateRange(datetime(self.year, 1, 1), datetime(self.year, 12, 31))
        range_year = (
            self.range_maternity() if not self.is_range_maternity_on_13() else year
        )
        # log.debug('   ******CALCULANDO QTD 13º SALARIO --------------------------')
        return self.range_salary_for(
            range_salary=range_year, get_possessions_from13=True
        )

    def validate_type_by_possession(self):
        if self.employee.type_by_possession not in [
            "CMS",
        ]:
            raise self.CalculationNotApplicable(
                "Essa verba é somente para servidor comissionado (CMS)!"
            )

    def validate_employee_genre(self):
        if self.employee.pessoa_fisica.sexo != "F":
            raise self.CalculationNotApplicable("Essa verba é somente para mulheres!")

    def validate_if_has_maternity_licence(self):
        q = self.employee.departures(
            self.payroll.periodo.range.first, self.payroll.periodo.range.last
        ).filter(
            tipo=12,
            # estado=2
        )
        if not q.exists():
            raise self.CalculationNotApplicable(
                f"Não há licença maternidade para o período da folha: {self.payroll.periodo.mes}/{self.payroll.periodo.ano}"
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_employee_genre()
        self.validate_type_by_possession()
        self.validate_if_has_maternity_licence()

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        return NewDateRange()

    def _intersect_ranges_for_range_salary(self):
        intersect_range = super(
            MaternitySalary, self
        )._intersect_ranges_for_range_salary()
        range_ = self.range_maternity()
        if self._is_christmas_grat:
            if not self.is_range_maternity_on_13():
                return NewDateRange([])
            else:
                return self.range_salary

        return intersect_range.intersect(range_)

    @property
    # @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            base_value = salarie["value"] + salarie["gratification"]
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days

        return base_value, days


@RunCodeManager.register("gfp-mpmt-gratificationcomissioned")
class GratificationCommissioned(GratificationFunction, SalaryCommissioned):
    """Usado exclusivamente para quem possui cargo em comissão.

    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """

    title = "Gratificação do cargo em comissão"
    description = """
    Usado exclusivamente para quem possui cargo em comissão.
    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    def configure(self):
        if self.employee.tipo == "M" and self.object:
            if self.object[2:] in ["CSUP", "CGPGJ", "CGAECO", "DAM7", "AEPGJ"]:
                # 06/01/2016 data de início da indenização
                self.validity = NewDateRange(None, datetime(2016, 1, 6))
            elif self.object[2:] in ["PGJ", "SUBPGJ", "OGJ", "CGJ"]:
                # 27/03/2016 data de início da indenização para esses cargos
                self.validity = NewDateRange(None, datetime(2016, 3, 27))

            self.validity += NewDateRange(datetime(2017, 9, 1), None)
        # log.debug('CONFIGURE OBJ: %s/%s %s' % (self.object, self.object[2:], unicode(self.validity)))

    def validate(self):
        self.validate_not_paycheck_pension()
        if not set(self.employee_types).intersection(["CM", "EL"]):
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui cargo comissionado no período"
                % (self.employee)
            )
        # if set(self.employee_types).intersection(['AC', 'EF']):
        #     raise self.CalculationNotApplicable('Essa verba é para servidor exclusivamente comissionado!')

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = NewDateRange()
        if not set(self.employee_types).intersection(["AC", "EF"]):
            if self.is_range_maternity_on_13() or not self._is_christmas_grat:
                range_ = self.range_maternity()
        range_ = range_ + super(
            GratificationCommissioned, self
        )._exclude_ranges_for_range_salary(range_salary=range_salary)

        if self.employee.type_by_possession in ["MBR", "MEL", "MCM", "MEC"]:
            q = self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            ).filter(tipo=62)

            for l in q.filter():
                dt_start = l.data_inicio
                dt_end = (
                    self.payroll.periodo.range.last
                    if l.data_fim is None
                    else l.data_fim
                )
                if dt_start <= dt_end:
                    range_ += NewDateRange(dt_start, l.data_fim)

        return range_


@RunCodeManager.register("gfp-mpmt-indemnificationcomissioned")
class IndemnificationCommissioned(GratificationCommissioned):
    """Usado exclusivamente para quem possui cargo em comissão.

    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """

    title = "Gratificação do cargo em comissão"
    description = """
    Usado exclusivamente para quem possui cargo em comissão.
    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    def configure(self):
        if self.employee.tipo == "M" and self.object:
            if self.object[2:] in ["CSUP", "CGPGJ", "CGAECO", "DAM7", "AEPGJ"]:
                self.validity = NewDateRange(
                    datetime(2016, 1, 7), datetime(2017, 8, 31)
                )
            elif self.object[2:] in ["PGJ", "SUBPGJ", "OGJ", "CGJ"]:
                # 28/03/2016 data de início da indenização para esses cargos
                self.validity = NewDateRange(
                    datetime(2016, 3, 28), datetime(2017, 8, 31)
                )
        else:
            self.validity = NewDateRange()
        # log.debug('CONFIGURE OBJ: %s/%s %s' % (self.object, self.object[2:], unicode(self.validity)))

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.employee.tipo == "M" or not set(self.employee_types).intersection(
            ["CM", "EL"]
        ):
            raise self.CalculationNotApplicable(
                "Cálculo exclusivo para membros com cargos comissionados/eletivos!"
                % (self.employee)
            )


@RunCodeManager.register("gfp-mpmt-complementsalarycommissioned")
class ComplementSalaryCommissioned(SalaryCommissioned):
    title = "Complemento do vencimento de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a parte vencimental do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    FULL_SALARY = True

    def validate(self):
        self.validate_not_paycheck_pension()
        if not (
            "CM" in self.employee_types
            and ("EF" in self.employee_types or "AC" in self.employee_types)
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser efetivo e comissionado no período!"
            )

    def _calc_real_value(self, ef, cm):
        real_value = cm.get("value") - ef.get("value") - ef.get("extra")
        return real_value if real_value >= 0.0 else 0.0

    @property
    @cached()
    def _base_value(self):
        base_value = days = 0.0
        salaries = self.extract_base_salary_by_period()
        for salary in salaries:
            dr = NewDateRange.fromordinals(salary["range"])
            if (
                ("EF" in salary or "AC" in salary)
                and "CM" in salary
                and salary["CM"]["id"] == self.object
            ):
                ef_ = salary.get("EF", salary.get("AC"))
                cm_ = salary.get("CM")
                real_value = self._calc_real_value(ef_, cm_)
                base_value += real_value
                days += ef_.get("days")

        if self.FULL_SALARY:
            base_value *= (self.base_days / days) if days else 0.0

        return base_value, days

    def normal_value(self):
        return self.value() if self.value() > 0 else 0.0


@RunCodeManager.register("gfp-mpmt-complementsalarycommissionedcomplete")
class ComplementSalaryCommissionedComplete(ComplementSalaryCommissioned):
    title = "Complemento do vencimento de comissionado completo"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a remuneração do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    FULL_SALARY = True

    def _calc_real_value(self, ef, cm):
        # percent_value = cm.get('value') * 0.3
        real_value = (
            cm.get("value")
            + cm.get("gratification")
            - ef.get("value")
            - ef.get("extra")
        )
        # log.info(f'_calc_real_value: {ef.get("value")} {cm.get("value")} {percent_value} {real_value}')
        real_value = real_value if real_value >= cm.get("gratification") else 0
        return real_value


@RunCodeManager.register("gfp-mpmt-complementsalarycommissionedcomplete30")
class ComplementSalaryCommissionedComplete30(ComplementSalaryCommissioned):
    title = "Complemento do vencimento de comissionado 30%"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a remuneração do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    FULL_SALARY = True

    def buscar_config_niveis_cargos_excluir(self):
        q_item = Item.objects.filter(
            configuration__application="gfp", key="01119_exclude_niveis_cargos"
        )

        if q_item.exists():
            return q_item.first().value.split(",")
        else:
            return []

    @property
    @cached()
    def _base_value(self):
        base_value = days = 0.0
        salaries = self.extract_base_salary_by_period()
        niveis_exclude = self.buscar_config_niveis_cargos_excluir()
        for salary in salaries:
            if (
                ("EF" in salary or "AC" in salary)
                and "CM" in salary
                and salary["CM"]["id"] == self.object
            ):
                ef_ = salary.get("EF", salary.get("AC"))
                cm_ = salary.get("CM")
                real_value = self._calc_real_value(ef_, cm_)

                if (cm_.get("id") not in niveis_exclude) and (
                    cm_.get("base_value") < ef_.get("base_value")
                ):
                    base_value += real_value
                    days += ef_.get("days")

        return base_value, days

    def _calc_real_value(self, ef, cm):
        real_value = cm.get("base_value") + cm.get("base_gratification")

        return real_value


@RunCodeManager.register("gfp-mpmt-complementgratificationcommissioned")
class ComplementGratificationCommissioned(GratificationCommissioned):
    title = "Complemento da grtificação de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da gratificação do cargo comissionado, proporcional
    aos dias trabalhos no mesmo!
    """

    def validate(self):
        self.validate_not_paycheck_pension()
        if not (
            ("CM" in self.employee_types or "EL" in self.employee_types)
            and ("EF" in self.employee_types or "AC" in self.employee_types)
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser efetivo e comissionado no período!"
            )


@RunCodeManager.register("gfp-mpmt-extra")
class IdentifiedPersonalAdvantage(SalaryEffective):
    title = "Cálculo de Vantagem Pessoal Identificada"
    description = """
    Usado exclusivamente para quem possui VPI (servidores efetivos antigos).
    O calculo retornará o valor da VPI do servidor, cadastrada no Gestor de Verbas Adicionais,
    proporcional aos dias trabalhados
    """

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        # _type = self.object[0:2]
        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            base_value = salarie["extra"]
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days

        return base_value, days

    def base_socialsecurity(self):
        return self.value()

    def normal_value(self):
        return self.base_salary()["normal_base_extra"]

    # def event_information(self):
    #     return ''


@RunCodeManager.register("gfp-mpmt-redutor-teto")
class ReduceSalaryCap(BaseCalculation):
    title = "Redutor de Teto Constitucional"
    description = """
    Usado para todos os servidores. No entanto, o teto é configurado separadamente para
    servidores e membros no menu FOLHA DE PAGAMENTO > Parâmentros > Período.
    O calculo retornará a diferença entre a remuneração recebida e o teto
    """

    FULL_VALUE = False

    RECALCULATE_BASES = 3

    @property
    def salary_cap(self):
        if self.employee.tipo == "M":
            return float(self.reference_payroll.periodo.salario_teto_membros or 0.00)
        else:
            return float(self.reference_payroll.periodo.salario_teto_adm or 0.00)

    @cached()
    def value(self):
        cap_value = self.salary_cap
        base_value = float(self.base_value())
        log.debug(
            "REDUTOR TETO(%s): %s - %s"
            % (cap_value, base_value, self.reference_payroll)
        )
        if cap_value and base_value > cap_value:
            return base_value - cap_value
        else:
            return 0.0

    @cached()
    def base_socialsecurity(self):
        sum_base = sum_base_ss = 0.00
        value = self.value()

        for fe in self.reference_payroll.lancamentos.exclude(
            evento__numero__in=self.exclude_events
        ).filter(evento__numero__in=self.focuses_on, servidor=self.employee):
            sum_base += float(
                fe.correct_valor if fe.evento.tipo == "P" else -fe.correct_valor
            )
            sum_base_ss += float(
                fe.correct_base_previdencia
                if fe.evento.tipo == "P"
                else -fe.correct_base_previdencia
            )

        diff_ss = sum_base - sum_base_ss

        if diff_ss > value:
            return 0.00
        else:
            return value - diff_ss


class BaseSubstitution(BaseSalary):
    title = "Calculo Base para substituição"
    description = """
        Este cálculo pode ser usado como base para substituições em geral.
    """
    MULTI_CALCULATE = True

    def get_substitutions(self):
        return (
            SubstitutionMovement.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=self.range_salary.first)
                | Q(data_inicio__gt=self.range_salary.last)
            )
            .filter(posse__quadro__cargo__tipo_lei_cargo__in=["CM", "FC", "EL"])
        )

    @cached()
    def _get_query(self):
        query = self.get_substitutions()

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.reference_payroll,
                evento=self.event,
            )
            if self.entry:
                log.debug("%s:%s" % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            cache_id = "CBSUB%s%s" % (self.identification_payroll, self.object.pk)

            ranges_ = []

            log.debug(
                "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                % (
                    self.object.posse.quadro.cargo.pk,
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
            )
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )

            type_employee = "S"
            if self.employee.is_member:
                type_employee = "M"

            for salary_sub in salaries_substitution:
                salaries = self.extract_base_salary_by_period()
                for salary in salaries:
                    log.debug(
                        "RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s"
                        % (
                            salary,
                            salary_sub[0],
                            NewDateRange.fromordinals(salary["range"]),
                        )
                    )
                    dr = NewDateRange.fromordinals(salary["range"]).intersect(
                        salary_sub[0]
                    )
                    if dr.days > 0:
                        if (
                            salary_sub[1]
                            and (
                                salary_sub[
                                    1
                                ].referencia_nivel2d.tipo_gratificacao_membro
                                == 2
                                and type_employee == "M"
                            )
                            or (
                                salary_sub[1].referencia_nivel2d.tipo_gratificacao == 2
                                and type_employee == "S"
                            )
                        ):
                            ef_ = salary.get("EF", salary.get("AC", base))
                            fc_ = salary.get("FC", base)
                            cm_ = salary.get("CM", salary.get("EL", base))
                            base_value = 0
                            base_gratification = 0
                            value = 0
                            v_gratification = (
                                salary_sub[1].gratificacao_membro
                                if type_employee == "M"
                                else salary_sub[1].gratificacao
                            )
                            gratification = (
                                float(v_gratification) / 100 * ef_.get("normal_value")
                            )
                            # log.debug('%s BV: %s BG: %s V: %s G: %s' % (dr,
                            #                                             value,
                            #                                             gratification,
                            #                                             salary_sub[1].valor_membro,
                            #                                             v_gratification))
                            config = {
                                "range": dr.toordinals(),
                                "EF": ef_,
                                "FC": fc_,
                                "CM": cm_,
                                "CMSUB": salary_sub[1],
                                "base_value": value if value > 0.00 else 0.00,
                                "base_gratification": gratification,  # if gratification > 0.00 else 0.00,
                            }
                            # log.debug('CONFIG: %s' % config)
                            ranges_.append(config)
                        else:
                            # factor = dr.days / float(range_.days)
                            ef_ = salary.get("EF", salary.get("AC", base))
                            fc_ = salary.get("FC", base)
                            cm_ = salary.get("CM", salary.get("EL", base))
                            base_value = (
                                (ef_["base_value"] + ef_["extra"])
                                if (ef_["base_value"] + ef_["extra"])
                                > cm_["base_value"]
                                else cm_["base_value"]
                            )
                            # base_value *= factor
                            base_gratification = (
                                cm_["base_gratification"] + fc_["base_gratification"]
                            )  # * factor
                            value = float(salary_sub[1].valor) - base_value
                            gratification = (
                                float(salary_sub[1].gratificacao) - base_gratification
                            )
                            log.debug(
                                "%s BV: %s BG: %s V: %s G: %s"
                                % (
                                    dr,
                                    value,
                                    gratification,
                                    salary_sub[1].valor,
                                    salary_sub[1].gratificacao,
                                )
                            )
                            config = {
                                "range": dr.toordinals(),
                                "EF": ef_,
                                "FC": fc_,
                                "CM": cm_,
                                "CMSUB": salary_sub[1],
                                "base_value": value if value > 0.00 else 0.00,
                                "base_gratification": gratification,  # if gratification > 0.00 else 0.00,
                            }
                            log.debug("CONFIG: %s" % config)
                            ranges_.append(config)

            set_cache(cache_id, ranges_, self.group_key_cache)

            return ranges_
        else:
            return {}

    @property
    @cached()
    def range_substitution(self):
        range_ = NewDateRange()
        for config in self.extract_salaries_substitution():
            log.debug(
                "RANGE SUBSTITUION: %s" % NewDateRange.fromordinals(config["range"])
            )
            range_ += NewDateRange.fromordinals(config["range"])
        log.debug("RECALCULATE ESS: %s" % range_.days)
        return range_
        # return self.range_salary.intersect(NewDateRange(self.object.data_inicio, self.object.data_fim))

    def maximum_quantity(self):
        return self.base_days

    def quantity(self):
        return (
            self.base_days
            if self.range_salary == self.range_substitution
            else self.range_substitution.days
        )

    def base_socialsecurity(self):
        return self.value()

    def event_information(self):
        return (
            (
                "%s ID%06d"
                % (
                    self.object.publicacao_alteracao
                    or self.object.publicacao_movimentacao,
                    self.object.pk,
                )
            )
            if self.object
            else ""
        )

    def unicode_for_obj(self, obj):
        return "%s" % obj


class BaseCumulation(BaseSubstitution):
    title = "Calculo base para cumulação por substituição"
    description = """
        Este cálculo pode ser usado como base para substituições em geral.
    """
    MULTI_CALCULATE = True

    def get_substitutions(self):
        return (
            SubstitutionMovement.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=self.range_salary.first)
                | Q(data_inicio__gt=self.range_salary.last)
            )
            .filter(
                posse__quadro__cargo__tipo_lei_cargo="EF",
                posse__quadro__cargo__indicativo="M",
            )
        )

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            substitute_possession = self.get_possessions_by_type(["EF"]).filter(
                quadro__cargo__indicativo="M"
            )[0]
            if (
                substitute_possession.quadro.cargo.entrancia > 0
                and substitute_possession.quadro.cargo.entrancia
                < self.object.posse.quadro.cargo.entrancia
            ):

                if (
                    hasattr(self.employee, "_cache_diffs_substitution_by_periods")
                    and self.identification_payroll
                    in self.employee._cache_diffs_substitution_by_periods
                    and self.object.pk
                    in self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ]
                ):
                    return self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ][self.object.pk]

                ranges_ = {}

                log.debug(
                    "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                    % (
                        self.object.posse.quadro.cargo.pk,
                        self.object.posse.quadro.cargo,
                        self.object.data_inicio,
                        self.object.data_fim,
                    )
                )
                salaries_substitution = EstruturaTabelaSalarial.salarios(
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
                for salary_sub in salaries_substitution:
                    salaries = self.extract_base_salary_by_period()
                    for salary in salaries:
                        log.debug("RECALCULATE: DRs %s : %s" % (salary, salary_sub[0]))
                        dr = NewDateRange.fromordinals(salary).intersect(salary_sub[0])
                        if dr.days > 0:
                            # factor = dr.days / float(range_.days)
                            ef_ = salary.get("EF", salary.get("AC", base))
                            fc_ = salary.get("FC", base)
                            cm_ = salary.get("CM", salary.get("EL", base))
                            base_value = ef_["base_value"]
                            # base_value *= factor
                            # base_gratification = 0.00
                            value = float(salary_sub[1].valor) - base_value
                            gratification = 0.00
                            log.debug(
                                "%s BV: %s BG: %s V: %s G: %s"
                                % (
                                    dr,
                                    value,
                                    gratification,
                                    salary_sub[1].valor,
                                    salary_sub[1].gratificacao,
                                )
                            )
                            config = {
                                "EF": ef_,
                                "FC": fc_,
                                "CM": cm_,
                                "CMSUB": salary_sub[1],
                                "base_value": value,
                                "base_gratification": gratification,
                            }
                            log.debug("CONFIG: %s" % config)
                            ranges_[dr] = config
                if not (hasattr(self.employee, "_cache_diffs_substitution_by_periods")):
                    self.employee._cache_diffs_substitution_by_periods = {}
                if (
                    self.identification_payroll
                    not in self.employee._cache_diffs_substitution_by_periods
                ):
                    self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ] = {}

                self.employee._cache_diffs_substitution_by_periods[
                    self.identification_payroll
                ][self.object.pk] = ranges_
                return self.employee._cache_diffs_substitution_by_periods[
                    self.identification_payroll
                ][self.object.pk]
            else:
                return {}
        else:
            return {}

    @property
    @cached()
    def range_substitution(self):
        range_ = NewDateRange()
        for dr in self.extract_salaries_substitution().keys():
            range_ += dr
        log.debug("RECALCULATE: %s" % range_.days)
        return range_
        # return self.range_salary.intersect(NewDateRange(self.object.data_inicio, self.object.data_fim))

    def quantity(self):
        return (
            self.base_days
            if self.range_salary == self.range_substitution
            else self.range_substitution.days
        )

    def base_socialsecurity(self):
        return self.value()

    def event_information(self):
        return (
            (
                "%s ID%06d"
                % (
                    self.object.publicacao_alteracao
                    or self.object.publicacao_movimentacao,
                    self.object.pk,
                )
            )
            if self.object
            else ""
        )

    def unicode_for_obj(self, obj):
        return obj

    def base_value(self):
        base_value = 0.0
        days = 0.0
        ranges = self.extract_salaries_substitution()
        for range_ in ranges:
            base_value += ranges[range_].get("base_value", 0.00) * range_.days
            days += range_.days

        return (base_value / days) if days else 0.0


@RunCodeManager.register("gfp-mpmt-cumulation")
class Cumulation(SalaryEffective):
    title = "Cálculo de porcetagem de cumulação para membros"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "qnt", "pct"]

    MULTI_CALCULATE = False
    JOIN_ON_MULTI = False

    @cached()
    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)
            if self.event.quantity_at(self.range_salary.first) is not None:
                return float(self.event.quantity_at(self.range_salary.first))
        return 0

    @cached()
    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""


@RunCodeManager.register("gfp-mpmt-substituion-efective")
class EfectiveSubstitution(BaseSubstitution):
    title = "Calculo Substituição de Efetivos."
    description = """
        Calculo retorna toda a diferença de substituição (vencimento/gratificação) juntos.
        Esse método é usualmente utilizado no MP-TO, mas está sendo revisto para que a diferença de
        vencimento seja retornada separada da diferença de gratificação, sendo assim, necessitará de
        2 rubricas/eventos diferentes.
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += (
                config.get("base_value", 0.00) + config.get("base_gratification", 0.00)
            ) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-mpmt-substituion-complement")
class ComplementSubstitution(BaseSubstitution):
    title = "Complemento de substituição para a remuneração"
    description = """
        Calculo retorna o complemento entre a remuneração do servidor e o salário do cargo a ser substituído!
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += (
                config.get("base_value", 0.00) + config.get("base_gratification", 0.00)
            ) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-mpmt-substituion-complement-member")
class ComplementSubstitutionMember(ComplementSubstitution):
    title = "Complemento de substituição para membros"
    description = """
        Calculo retorna o complemento entre o subsídio do membro substituído e do substituto!
    """

    def __init__(self, employee, payroll, event=None, **kwargs):
        super(ComplementSubstitutionMember, self).__init__(
            employee, payroll, event=None, **kwargs
        )
        self.possession_substitute = (
            self.employee.get_posses_ativas(
                self.range_salary.first, self.range_salary.last
            )
            .filter(
                servidor__tipo="M",
                quadro__cargo__tipo_lei_cargo="EF",
                quadro__cargo__level_instance__in=[1, 2, 3],
            )
            .first()
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.tipo != "M"
            or not self.possession_substitute
            or self.possession_substitute.quadro.cargo.level_instance is None
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser membro já titularizado de 1ª instância!"
            )

    def get_substitutions(self):
        return SubstitutionMovement.objects.exclude(
            Q(data_fim__lt=self.range_salary.first)
            | Q(data_inicio__gt=self.range_salary.last)
        ).filter(
            Q(servidor=self.employee)
            & Q(posse__quadro__cargo__tipo_lei_cargo__in=["EF"])
            & Q(servidor__tipo="M")
            & Q(servidor_substituido__tipo="M")
            & Q(
                Q(posse__quadro__cargo__level_instance__in=[2, 3])
                | Q(posse__quadro__cargo__instance=2)
            )
            & Q(
                Q(
                    posse__quadro__cargo__level_instance__gt=self.possession_substitute.quadro.cargo.level_instance
                )
                | Q(posse__quadro__cargo__instance=2)
            )
        )

    @cached()
    def _get_query(self):
        query = self.get_substitutions()

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.reference_payroll,
                evento=self.event,
            )
            if self.entry:
                log.debug("%s:%s" % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            cache_id = "CBSUBM%s%s" % (self.identification_payroll, self.object.pk)

            ranges_ = []

            log.debug(
                "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                % (
                    self.object.posse.quadro.cargo.pk,
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
            )
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )

            for salary_sub in salaries_substitution:
                salaries = self.extract_base_salary_by_period()
                for salary in salaries:
                    log.debug(
                        "RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s"
                        % (
                            salary,
                            salary_sub[0],
                            NewDateRange.fromordinals(salary["range"]),
                        )
                    )
                    dr = NewDateRange.fromordinals(salary["range"]).intersect(
                        salary_sub[0]
                    )
                    if dr.days > 0:
                        # factor = dr.days / float(range_.days)
                        ef_ = salary.get("EF", base)
                        fc_ = base
                        cm_ = base
                        base_value = ef_["base_value"]
                        value = float(salary_sub[1].valor) - base_value
                        gratification = 0
                        log.debug(
                            "%s BV: %s BG: %s V: %s G: %s"
                            % (
                                dr,
                                value,
                                gratification,
                                salary_sub[1].valor,
                                salary_sub[1].gratificacao,
                            )
                        )
                        config = {
                            "range": dr.toordinals(),
                            "EF": ef_,
                            "FC": fc_,
                            "CM": cm_,
                            "CMSUB": salary_sub[1],
                            "base_value": value if value > 0.00 else 0.00,
                            "base_gratification": (
                                gratification if gratification > 0.00 else 0.00
                            ),
                        }
                        log.debug("CONFIG: %s" % config)
                        ranges_.append(config)

            set_cache(cache_id, ranges_, self.group_key_cache)

            return ranges_
        else:
            return {}

    def event_information(self):
        return (
            ("%s ID%06d" % (self.object.posse.quadro.cargo, self.object.pk))
            if self.object
            else ""
        )


@RunCodeManager.register("gfp-mpmt-substituion-salary")
class CommissionedSubstitution(BaseSubstitution):
    title = "Calculo Substituição para a parte vencimental da remuneração."
    description = """
        Calculo retorna o complemento da parte vencimental do cargo comissionado do substituído.
        Lembrando que se o servidor possui subsídio/vencimento + vpi maior que o vencimento do cargo,
        o calculo retornará zerado (0,00), pois não há o que complementar na parte vencimental
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_value", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-mpmt-substituion-gratification")
class GratificationSubstitution(BaseSubstitution):
    title = "Calculo Substituição para a parte vencimental da remuneração."
    description = """
        Calculo retorna o complemento da parte vencimental do cargo comissionado do substituído.
        Lembrando que se o servidor possui subsídio/vencimento + vpi maior que o vencimento do cargo,
        o calculo retornará zerado (0,00), pois não há o que complementar na parte vencimental
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_gratification", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


class BaseChristmasGratification(BaseSalary):

    title = "Base para os cálculos de 13° Salário"

    advance_christmas_gratification_number = "01600"
    anticipated_christmas_gratification_number = "02300"

    FULL_SALARY = True
    # FULL_VALUE = True

    def configure(self):
        range_indemnity = NewDateRange(date(2016, 1, 1), date(2017, 8, 31))
        dt = date(self.range_salary.first.year, self.range_salary.first.month, 1)
        if self.object and range_indemnity.in_range(dt):
            self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {"M": ["CM", "EL"]}

    def maximum_quantity(self):
        return 12.00

    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_unpaid_absences = NewDateRange()

        if self.IGNORE_DEPARTURE is False:
            range_year = NewDateRange(
                datetime(self.year, 1, 1), datetime(self.year, 12, 31)
            )

            for absence in BaseLicencaAfastamento.objects.filter(
                Q(servidor=self.employee)
            ).exclude(
                Q(estado=AFASTAMENTO_CANCELADO)
                | Q(data_fim__lt=range_year.first)
                | Q(data_inicio__gt=range_year.last)
                | Q(remunerado=True)
                | Q(afastamento__afastamentooutroorgao__transito_pela_folha=True)
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )
        # log.debug('SFE ERANGES: %s' % range_unpaid_absences)

        return range_unpaid_absences

    @cached()
    def quantity(self):
        # vai pro base salary; avaliar self._is_christmas_grat
        range_period = self.range_13salary
        log.info(self.range_13salary)
        qtd = 0
        for month in range(12):
            range_month = range_period.intersect(
                NewDateRange.from_month(self.year, month + 1)
            )
            if range_month.days >= 15:
                qtd += 1

        return qtd

    @cached()
    def get_possessions(self):
        range_year = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        possessions = self.employee.posses.exclude(
            Q(financial_effect_date_start__gt=range_year.last)
            | (
                ~Q(financial_effect_date_end=None)
                & Q(financial_effect_date_end__lte=range_year.first)
            )
        ).order_by("-financial_effect_date_start")

        for k in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.keys():
            possessions = possessions.exclude(
                servidor__tipo=k,
                quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB[
                    k
                ],
            )

        # log.debug('AdvanceChristmasGratification: %s' % possessions)
        return possessions

    def base_socialsecurity(self):
        return self._base_values()[1] * self.factor_quantity()


@RunCodeManager.register("gfp-mpmt-13thsalary")
class ChristmasGratification(BaseChristmasGratification):

    title = "13° Salário"

    def base_value_query(self):
        # print(self.focuses_on)
        month_recision = self.range_13salary.last.month
        q_entries = Q(
            contracheque__servidor=self.employee,
            evento__numero__in=self.focuses_on,
            contracheque__folha__periodo__ano=self.payroll.periodo.ano,
            contracheque__folha__periodo__mes=month_recision,  # SEMPRE UTILIZAR DO MES DE DEZEMBRO (12)
        )
        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))

        return Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    def base_socialsecurity(self):
        return self._base_values()[1]  # * self.factor_quantity()


@RunCodeManager.register("gfp-mpmt-13thsalary-amountpaid")
class ChristmasGratificationAmountPaid(ChristmasGratification):
    FULL_VALUE = False

    # TODO Verificar se não tem como configurar para inibir que um evento sobre o qual o calculo
    # incide seja recalculado.
    @cached()
    def base_value(self):
        log.debug(
            f"******************************* 2 BASE VALUE {self.__class__} > {self.base_value_query()}"
        )
        if "base_value" in self.params:
            return float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return float(self.event.base_value_at(self.range_salary.first))

        total = 0.00

        for fe in self.base_value_query():

            # log.debug('correct_valor >> %s' % (fe.correct_valor))
            value = float(
                fe.correct_valor if self.FULL_VALUE is False else fe.valor_base
            )
            value = value if fe.evento.tipo == "P" else -value

            self._memory.append(
                f"VALOR BASE = {total} + {value} = {total + value} ({fe.evento.numero})"
            )
            # log.debug('>>>> %s >>>> %s : %s + %s = %s' %
            #           (self.event.numero if self.event else 'XXX-XX', fe.evento.numero, total, value, total + value))
            total += value
        base_discounts = self.base_discounts()
        base_value = total - base_discounts
        if base_discounts:
            self._memory.append(
                f"VALOR BASE = {total} - {base_discounts} = {base_value} (DESCONTOS VALOR BASE)"
            )
        base_value = (
            base_value
            if not (self.event and self.event.calculo_invertido)
            else -base_value
        )
        return min(base_value, self.ceiling_base_value)


@RunCodeManager.register("gfp-mpmt-13thsalary-gratification")
class ChristmasGratificationComissioned(GratificationCommissioned):

    @property
    @cached()
    def range_base(self):
        return self.range_salary_for()

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0, 0.0

        # _type = self.object[0:2]
        base_value = pct = 0.00
        days = 0
        salaries = self.extract_base_salary_by_period()
        count = 0
        is_equal = True
        last_base = 0

        for salary in salaries:
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                count += 1
                if not last_base:
                    last_base = salary[self.object[0:2]]["base_gratification"]
                elif salary[self.object[0:2]]["base_gratification"] != last_base:
                    is_equal = False

        for salary in salaries:
            dr = NewDateRange.fromordinals(salary["range"])
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                log.info(f"{count} {is_equal} {self._is_christmas_grat}")

                if count > 1 and not is_equal and not self._is_christmas_grat:
                    base_value += (
                        salary[self.object[0:2]]["base_gratification"]
                        / self.payroll.date_range.days
                        * dr.days
                    )
                else:
                    key = (
                        "base_gratification"
                        if dr == self.range_base and self.employee.tipo != "M"
                        else "normal_gratification"
                    )
                    base_value += salary[self.object[0:2]][key]
                    log.info(
                        f"{self.object[0:2]} {salary[self.object[0:2]]} DR: {dr} RS: {self.range_salary} RB: {self.range_base}"
                    )
                pct = 0
                days += dr.days

        return base_value, days, pct


@RunCodeManager.register("gfp-mpmt-13thsalary-salaryrequested")
class ChristmasSalaryRequested(SalaryRequested):
    title = "Remuneração de servidor requisitado no 13º"
    description = """
    """

    def base_value(self):
        log.info(self.base_salary_for_type("AC"))
        return self.base_salary_for_type("AC").get("base_value")


@RunCodeManager.register("gfp-mpmt-13thsalary-complementsalarycommissioned")
class ChristmasComplementSalaryCommissioned(ComplementSalaryCommissioned):
    title = "Complemento do vencimento de comissionado 13º"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a parte vencimental do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    FULL_SALARY = False


@RunCodeManager.register("gfp-mpmt-13thsalary-salaryalaryeffective")
class ChristmasSalaryEffective(BaseSalary):
    title = "Remuneração de efetivo apenas 13º"
    description = """
        Este cálculo retorna o valor do salário de efetivo, caso o servidor seja efetivo, ou seja,
        apenas o valor da tabela salarial do cargo efetivo do servidor.
    """


@RunCodeManager.register("gfp-mpmt-13thsalary-gratificationfunction")
class ChristmasGratificationFunction(GratificationFunction):
    title = "Gratificação de função de confiança"
    description = """
    Usado exclusivamente para quem possui função de confiança.
    O calculo retornará o valor da gratificação da função proporcional aos
    dias trabalhos com a função!
    """

    TYPES = [
        "FC",
    ]

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0, 0.0

        # _type = self.object[0:2]
        base_value = pct = 0.00
        days = 0
        salaries = self.extract_base_salary_by_period()
        count = 0
        is_equal = True
        last_base = 0

        for salary in salaries:
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                count += 1
                if not last_base:
                    last_base = salary[self.object[0:2]]["base_gratification"]
                elif salary[self.object[0:2]]["base_gratification"] != last_base:
                    is_equal = False
        for salary in salaries:
            dr = NewDateRange.fromordinals(salary["range"])
            if (
                self.object[0:2] in salary
                and salary[self.object[0:2]]["id"] == self.object
            ):
                if count > 1 and not is_equal and not self._is_christmas_grat:
                    base_value += (
                        salary[self.object[0:2]]["base_gratification"]
                        / self.payroll.date_range.days
                        * dr.days
                    )
                else:
                    key = (
                        "base_gratification"
                        if dr == self.range_base and self.employee.tipo != "M"
                        else "normal_gratification"
                    )
                    base_value += salary[self.object[0:2]][key]
                    log.info(f"{self.object[0:2]} {salary[self.object[0:2]]} {dr}")
                pct = salary[self.object[0:2]]["percentage"]
                days += dr.days

        return base_value, days, pct


@RunCodeManager.register("gfp-mpmt-Advance13thsalary")
class AdvanceChristmasGratification(BaseChristmasGratification):

    title = "Adiantamento de 13° Salário"
    GENERAL_RULE_TYPES = [
        "MAP",
        "MAP2",
        "SAP",
        "APO",
        "BFP",
    ]  # types_by_possession onde serão aplicadas as regras gerais para calculo da verba

    def _base_values(self):
        if self.employee.type_by_possession in ["ECM"]:
            self.exclude_events += [
                "01100",
                "01119",
            ]  # Remover Evento 'DIFERENÇA CNE' | DIFERENÇA CNE % - INDENIZ ATO 037 /2023E 1.164/2023
            self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {
                "S": [
                    "CM",
                ]
            }

        if "base_value" in self.params:
            return float(self.params["base_value"]), float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return (
                float(self.event.base_value_at(self.range_salary.first)),
                float(self.event.base_value_at(self.range_salary.first)),
            )

        base = self.base_salary()
        if self.FULL_SALARY:
            total_base = base["base_value"] + base["base_gratification"]
        else:
            total_base = base["value"] + base["gratification"]
        total_base_socialsecurity = base["full_base_socialsecurity"]

        if not self.event:
            return total_base, total_base_socialsecurity

        for fe in self.base_value_query():
            only_events = self.focuses_on

            if fe.evento.numero in ["05200", "10500"]:
                only_events = []

            value = 0
            base_socialsecurity = 0
            if (
                fe.evento.automated
                and fe.classcode
                and (
                    fe.reference_year != self.range_salary.first.year
                    or fe.reference_month != self.range_salary.first.month
                )
            ):
                params = {
                    "pct": fe.pct,
                    "qnt": fe.qnt,
                    "info": fe.info,
                    "patronal": fe.patronal,
                    "valor_base": fe.valor_base,
                }
                params.update(fe.vars)
                calc = fe.classcode.cls(
                    self.employee,
                    self.reference_payroll,
                    fe.evento,
                    year=self.range_salary.first.year,
                    month=self.range_salary.first.month,
                    params=params,
                    only_events=only_events,
                    group_cache=self.group_key_cache,
                    entry=fe,
                    pension=fe.contracheque.pensioner,
                )
                value = self._value_calc_normatized(calc)
                base_socialsecurity = calc.base_socialsecurity()

                value = value if fe.evento.tipo == "P" else -value
                base_socialsecurity = (
                    base_socialsecurity
                    if fe.evento.tipo == "P"
                    else -base_socialsecurity
                )
            else:
                value = float(
                    fe.correct_valor if fe.evento.tipo == "P" else -fe.correct_valor
                )
                base_socialsecurity = float(
                    fe.correct_base_previdencia
                    if fe.evento.tipo == "P"
                    else -fe.correct_base_previdencia
                )

            total_base += value
            total_base_socialsecurity += base_socialsecurity
        base_value = total_base - self.base_discounts()

        return (
            (base_value, total_base_socialsecurity)
            if not self.event.calculo_invertido
            else (-base_value, -total_base_socialsecurity)
        )

    def validate_month_valid(self):
        """Valida se o mês igual do 13º mês retornando erro se verdadeiro"""
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

    def validate_first_christmas_gratification_on_year(self, event_number: str):
        """Valida se o servidor já recebeu a antencipação ou adiantamento do 13º salário no corrente ano."""
        year = self.payroll.periodo.ano
        query = self.employee.entries.filter(
            (
                Q(evento=self.event)
                | Q(evento=self.event.previous_event)
                | Q(evento__numero=event_number)
            )
            & Q(contracheque__folha__periodo__ano=year)
        ).exclude(pk=self.entry.pk if self.entry else None)
        if query.exists():
            raise self.CalculationNotApplicable(
                "O servidor já possui adiantamento para o exercício %s" % year
            )

    def validate_right_months_for_be_applied(self):
        """Valida se o mês de recebimento é outubro ou o mês do aniversário do servidor, para aniversariantes em
        Nov/Dez, deve ser requerido no mês de outubro"""
        mes_aniversario = self.employee.pessoa_fisica.data_nascimento.month
        valid_months = [
            10,
            mes_aniversario if mes_aniversario not in [11, 12] else None,
        ]
        if self.payroll.periodo.mes not in valid_months:
            raise self.CalculationNotApplicable(
                "Apenas pode ser requerido no mês de aniversário (para aniversariantes em Nov/Dez, deve ser requerido no mês de outubro)"
            )

    def validate_is_employee_active(self):
        if not self.employee.ativo:
            raise self.CalculationNotApplicable(
                "O servidor não está ativo no presente momento."
            )

    def validate(self):
        self.validate_is_employee_active()
        self.validate_not_paycheck_pension()
        # self.validate_month_valid()
        self.validate_right_months_for_be_applied()
        self.validate_first_christmas_gratification_on_year(
            self.anticipated_christmas_gratification_number
        )

    def base_socialsecurity(self):
        return self.value()

    def extract_base_salary_by_type(self):
        if self.employee.type_by_possession in self.GENERAL_RULE_TYPES:
            return super().extract_base_salary_by_type()
        self.range_salary = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        cache_id = "CSPM%s%s%s%s" % (
            "I" if self.IGNORE_DEPARTURE else "",
            self.identification_payroll,
            self.employee.matricula,
            "".join(
                "%06d%06d" % (t[0], t[1]) for t in self.range_salary_for().toordinals()
            ),
        )

        salaries = {}
        for p in self.get_possessions_by_type(["EF", "AC", "CM", "EL"]):
            range_ = self.range_13salary
            if (
                p.quadro.cargo.tipo_lei_cargo
                in [
                    "EF",
                ]
                and not p.servidor.tipo == "M"
            ):
                for prog in p.progressoes.exclude(
                    Q(data_inicio_vigencia__gt=self.range_salary.last)
                    | (
                        ~Q(data_fim_vigencia=None)
                        & Q(data_fim_vigencia__lt=self.range_salary.first)
                    )
                ):
                    range_prog = range_.intersect(
                        NewDateRange(prog.data_inicio_vigencia, prog.data_fim_vigencia)
                    )
                    salaries_ = EstruturaTabelaSalarial.salarios(
                        p.quadro.cargo,
                        range_prog.first,
                        range_prog.last,
                        prog.referencia_nivel2d,
                    )
                    for salary in salaries_:
                        idx = "%s%s" % (
                            p.quadro.cargo.tipo_lei_cargo,
                            salary[1].sigla_cache,
                        )
                        if idx not in salaries:
                            salaries[idx] = []
                        range_prog_salary = range_prog.intersect(salary[0])
                        extras = self.get_extras(
                            range_prog_salary.first, range_prog_salary.last
                        )
                        for extra in extras:
                            # log.debug(extra)
                            range_extra = range_prog_salary.intersect(
                                NewDateRange(extra.start_validity, extra.end_validity)
                            )
                            salaries[idx].append(
                                {
                                    "range": range_extra.toordinals(),
                                    "salary": salary[1],
                                    "type": p.quadro.cargo.tipo_lei_cargo,
                                    "value": salary[1].valor,
                                    "gratification": salary[1].gratificacao,
                                    "extra": extra.value,
                                    "percentage": False,
                                    "onus": True,
                                }
                            )
                        else:
                            if not extras:
                                salaries[idx].append(
                                    {
                                        "range": range_prog_salary.toordinals(),
                                        "salary": salary[1],
                                        "type": p.quadro.cargo.tipo_lei_cargo,
                                        "value": salary[1].valor,
                                        "gratification": salary[1].gratificacao,
                                        "extra": 0.0,
                                        "percentage": False,
                                        "onus": True,
                                    }
                                )

            elif p.quadro.cargo.tipo_lei_cargo in [
                "AC",
            ]:
                idx = "ACREQ"
                for ef in FinancialBurden.objects.filter(
                    requisicao__posse_origem=p
                ).exclude(
                    Q(data_inicio__gt=self.range_salary.last)
                    | (~Q(data_fim=None) & Q(data_fim__lt=self.range_salary.first))
                ):
                    if idx not in salaries:
                        salaries[idx] = []
                    range_ac = range_.intersect(
                        NewDateRange(ef.data_inicio, ef.data_fim)
                    )
                    salaries[idx].append(
                        {
                            "range": range_ac.toordinals(),
                            "salary": None,
                            "value": ef.remuneracao,
                            "gratification": 0.00,
                            "type": p.quadro.cargo.tipo_lei_cargo,
                            "extra": 0.0,
                            "percentage": False,
                            "onus": ef.requisicao.onus == 2,  # Onus para requisitante?
                        }
                    )

            else:
                initial_date = (
                    p.financial_effect_date_start
                    if p.financial_effect_date_start > self.range_salary.first
                    else self.range_salary.first
                )
                end_date = (
                    p.financial_effect_date_end
                    if p.financial_effect_date_end
                    and p.financial_effect_date_end < self.range_salary.last
                    else self.range_salary.last
                )
                salaries_ = EstruturaTabelaSalarial.salarios_atualizados(
                    p.quadro.cargo, initial_date, end_date
                )
                for salary in salaries_:
                    idx = "%s%s" % (
                        p.quadro.cargo.tipo_lei_cargo,
                        salary[1].sigla_cache,
                    )
                    if idx not in salaries:
                        salaries[idx] = []
                    range_cm = range_.intersect(salary[0])
                    value = (
                        salary[1].valor
                        if not self.employee.tipo == "M"
                        else salary[1].valor_membro
                    )
                    gratification = (
                        salary[1].gratificacao
                        if not self.employee.tipo == "M"
                        else salary[1].gratificacao_membro
                    )
                    currency_employee = (
                        salary[1].referencia_nivel2d.tipo_gratificacao == 1
                        and self.employee.tipo != "M"
                    )
                    currency_member = (
                        salary[1].referencia_nivel2d.tipo_gratificacao_membro == 1
                        and self.employee.tipo == "M"
                    )
                    percentage = False if currency_member or currency_employee else True
                    if not percentage and not p.quadro.cargo.chefia:
                        value += gratification
                        gratification = 0
                    salaries[idx].append(
                        {
                            "range": range_cm.toordinals(),
                            "salary": salary[1],
                            "type": p.quadro.cargo.tipo_lei_cargo,
                            "value": value,
                            "gratification": gratification,
                            "extra": 0.0,
                            "percentage": percentage,
                            "onus": True,
                        }
                    )

        set_cache(cache_id, salaries, self.group_key_cache)
        return salaries

    def extract_base_salary_by_period(self):
        if self.employee.type_by_possession in self.GENERAL_RULE_TYPES:
            return super().extract_base_salary_by_period()

        cache_id = "CSP%s%s%s" % (
            self.identification_payroll,
            self.employee.matricula,
            "".join(str(t or "000000") for t in self.validity.toordinals()),
        )

        # if get_cache(cache_id, self.group_key_cache):
        # return get_cache(cache_id, self.group_key_cache)

        salaries = self.extract_base_salary_by_type()
        ranges = {}
        for key in salaries:
            for salary in salaries[key]:
                # log.debug('I %s >>>>>>>>>>>>>>>>>>>>>>>>>>>' % key)
                # log.debug('SALARIO: %s >> %s' % (key, salaries[key]))
                aux = NewDateRange.fromordinals(salary["range"])
                # salaries_aux = {salary['type']: salary['salary']}
                salaries_aux = {
                    salary["type"]: {
                        "id": key,
                        "ref": salary["salary"],
                        "value": salary["value"],
                        "gratification": salary["gratification"],
                        "extra": salary["extra"],
                        "percentage": salary["percentage"],
                        "onus": salary["onus"],
                    }
                }
                r = 0
                # log.debug('>>> KEY: %s/%s' % (key, aux))
                while r < len(ranges) and aux.days:  # r in ranges:
                    inter = ranges[r]["range"].intersect(aux)
                    # dif = (ranges[r]['range'] - aux) if inter.days > 0 else ranges[r]['range']
                    if inter.days:
                        if inter == ranges[r]["range"]:
                            ranges[r]["salaries"].update(salaries_aux)
                            aux = aux - inter
                        elif inter == aux:
                            # Retirando o inter de dentro do range corrente (r)
                            ranges[r]["range"] = ranges[r]["range"] - inter
                            # Criando o novo range da intersecao
                            # salaries_aux.update(ranges[r]['salaries'])
                            idx = len(ranges)
                            salaries_copy = ranges[r]["salaries"].copy()
                            salaries_copy.update(salaries_aux)
                            ranges[idx] = {"salaries": salaries_copy, "range": inter}
                            # Retirando o interseçao do AUX
                            aux = aux - inter
                        else:
                            # Retirando o inter de dentro do range corrente (r)
                            ranges[r]["range"] = ranges[r]["range"] - inter
                            # Criando o novo range da intersecao
                            # salaries_aux.update(ranges[r]['salaries'])
                            idx = len(ranges)
                            salaries_copy = ranges[r]["salaries"].copy()
                            salaries_copy.update(salaries_aux)
                            ranges[idx] = {"salaries": salaries_copy, "range": inter}
                            # Retirando o interseçao do AUX
                            aux = aux - inter
                    r += 1
                idx = len(ranges)
                if aux.days:
                    ranges[idx] = {"salaries": salaries_aux, "range": aux}

        ranges__ = []
        # Verificando se necessita avaliar se os ranges podem ser normatizados, que são exceções,
        # para não ficar fazedo avalizações desnecessárias na maioria dos casos em que o calculo
        # tem o range_base igual ao range_salary, ou seja, o servidor trabalhou o mes completo
        # log.debug('RANGE BASE: %s (%s)' % (self.range_base, self.employee))
        normatize_left_days = 0
        normatize_rigth_days = 0
        if self.range_base.days != 0 and self.range_salary.days != 0:
            normatize_left_days = (self.range_base.first - self.range_salary.first).days
            normatize_rigth_days = (self.range_salary.last - self.range_base.last).days
        for value in ranges.values():
            formated_ = {"range": value["range"].toordinals()}
            for tipo in value["salaries"]:
                normatize_days = 0
                log.debug(
                    "%s: %s = %s"
                    % (
                        value["salaries"][tipo]["id"],
                        value["range"].last,
                        self.range_base.last,
                    )
                )
                base_gratification = float(value["salaries"][tipo]["gratification"])
                gratification = (
                    base_gratification  # * value['range'].days / self.base_days
                )
                pct_grat = 0.00
                if value["salaries"][tipo]["percentage"]:
                    pct_grat = float(value["salaries"][tipo]["gratification"])
                    ef = value["salaries"].get("EF", value["salaries"].get("AC", None))
                    base_gratification = float(ef["value"])
                    gratification = base_gratification * (
                        pct_grat / 100.0
                    )  # * (value['range'].days / self.base_days)

                if normatize_left_days or normatize_rigth_days:
                    normatize_days += (
                        normatize_left_days
                        if value["range"].first == self.range_base.first
                        else 0
                    )
                    normatize_days += (
                        normatize_rigth_days
                        if value["range"].last == self.range_base.last
                        else 0
                    )

                # if not self.employee.type_by_possession in ['CMS']:
                # base_month = value['range'].last.month - value['range'].first.month +1
                if (
                    value["range"]
                    .intersect(
                        NewDateRange(
                            self.payroll.periodo.range.first,
                            self.payroll.periodo.range.last,
                        )
                    )
                    .days
                    > 0
                ):
                    normal_factor_quantity = 1
                    factor_quantity = 1
                else:
                    normal_factor_quantity = 0
                    factor_quantity = 0

                # else:
                #     # Validação em meses
                #     if value['range'].first.day == 1 and value['range'].last.month != (value['range'].last +relativedelta(days=1)).month:
                #         base_month = value['range'].last.month - value['range'].first.month +1
                #         normal_factor_quantity = round(float(base_month) / self.quantity_13(), 8)
                #         factor_quantity = round(float(base_month) / 12, 8)
                #         log.debug(f'>>>> {self.event.numero} base month:{base_month} normal_factor_quantity: {normal_factor_quantity} {value["salaries"][tipo]["value"]}')
                #     else:
                #         qnt_days_range_init = monthrange(value['range'].first.year, value['range'].first.month)[1]
                #         qnt_days_range_end = monthrange(value['range'].last.year, value['range'].last.month)[1]

                #         if len(ranges.values()) > 1 and value['range'].first.day != 1:
                #             if value['range'].first.month != value['range'].last.month:
                #                 for range_value in ranges.values():
                #                     if range_value['range'].last.month == value['range'].first.month:
                #                         day_conference = monthrange(range_value['range'].last.year, range_value['range'].last.month)[1]
                #                         date_conference = datetime(range_value['range'].last.year, range_value['range'].last.month, 1).date()

                #                         date_range_conference = NewDateRange(date_conference, range_value['range'].last )
                #                         qnt_days_range_init = monthrange(value['range'].first.year, value['range'].first.month)[1]
                #                         end_date = datetime(value['range'].first.year, value['range'].first.month, qnt_days_range_init ).date()
                #                         date_range_ref = NewDateRange(value['range'].first, end_date)

                #                         if date_range_ref.days + date_range_conference.days == day_conference or date_range_ref.days + date_range_conference.days > day_conference/2:
                #                             if date_range_ref.days < date_range_conference.days:
                #                                 base_month = value['range'].last.month - value['range'].first.month
                #                             else:
                #                                 base_month = value['range'].last.month - value['range'].first.month +1
                #                             break
                #                         else:
                #                             base_month = value['range'].last.month - value['range'].first.month
                #                             break

                #             else:
                #                 #regra para quando tiver mais de um no mesmo mês
                #                 base_month = value['range'].last.month - value['range'].first.month
                #         elif value['range'].last.day < qnt_days_range_end:
                #             base_month = value['range'].last.month - value['range'].first.month
                #         elif value['range'].first.day != 1 and value['range'].first.day > round(qnt_days_range_init / 2):
                #             base_month = value['range'].last.month - value['range'].first.month
                #         else:
                #             base_month = value['range'].last.month - value['range'].first.month +1

                #         normal_factor_quantity = round(float(base_month) / self.quantity_13(), 8)
                #         factor_quantity = round(float(base_month) / 12, 8)

                #         log.debug(f'>>>> {self.event.numero} base month:{base_month} normal_factor_quantity: {normal_factor_quantity} {value["salaries"][tipo]["value"]}')

                formated_[tipo] = {
                    "id": value["salaries"][tipo]["id"],
                    "reference": value["salaries"][tipo]["ref"],
                    "base_value": float(value["salaries"][tipo]["value"]),
                    "base_gratification": base_gratification,
                    "normal_value": float(value["salaries"][tipo]["value"])
                    * normal_factor_quantity,
                    "normal_gratification": gratification * normal_factor_quantity,
                    "normal_extra": float(value["salaries"][tipo]["extra"])
                    * normal_factor_quantity,
                    "value": float(value["salaries"][tipo]["value"]) * factor_quantity,
                    "extra": float(value["salaries"][tipo]["extra"]) * factor_quantity,
                    "days": value["range"].days,
                    "gratification": gratification,
                    "percentage": pct_grat,
                }
                log.debug(">>> NFQ(%s): %s" % (normal_factor_quantity, formated_[tipo]))
            ranges__.append(formated_)

        # log.debug('%s: %s' % (cache_id, ranges__))
        set_cache(cache_id, ranges__, self.group_key_cache)
        return ranges__


@RunCodeManager.register("gfp-mpmt-DevolutionAdvance13thsalary")
class DevolutionAdvanceChristmasGratification(BaseCalculation):
    titulo = "Desconto devido adiantamento de 13° Salário"

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.month in [12]:
            raise self.CalculationNotApplicable(
                "A devolução de adiantamento de 13º não deve ser cobrado em dezembro! Utilize a folha do 13º."
            )

    @property
    @cached()
    def query_advances(self):
        q1 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano)
            & Q(folha__periodo__mes__range=[1, 11])
        )
        q2 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano - 1)
            & Q(folha__periodo__mes=12)
        )

        return self.employee.entries.filter(
            Q(evento__numero__in=self.focuses_on, status="CT") & Q(q1 | q2)
        )

    @cached()
    def exclude_advances(self):
        q1 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano)
            & Q(folha__periodo__mes__range=[1, 11])
        )
        return self.employee.entries.filter(
            Q(evento__in=self.event.relationships, status="CT") & Q(q1)
        )

    @cached()
    def _get_query(self):
        query = self.query_advances
        q_exclude = self.exclude_advances()
        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            if self.entry:
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
        exclude_ids = []
        log.debug(q_exclude)
        for e in q_exclude:
            log.debug(e.folha)
            for id_ in e.oIds or []:
                exclude_ids.append(id_)
                if (
                    self.entry
                    and e.paycheck_difference
                    and e.paycheck_difference.payment_event != self.entry
                ):
                    exclude_ids.remove(id_)

        query = query.exclude(pk__in=exclude_ids)

        return query

    def quantity(self):
        return self.query_advances.count()

    def maximum_quantity(self):
        return 1.00

    def base_value(self):
        if self.object:
            return float(self.object.valor)
        return 0.00

    def unicode_for_obj(self, obj):
        return "%02d/%04d (%s)" % (obj.reference_month, obj.reference_year, obj.evento)


# @RunCodeManager.register('gfp-mpmt-DevolutionAdvance13thsalary-ii')
# class DevolutionAdvanceChristmasGratificationII(DevolutionAdvanceChristmasGratification):

#     @property
#     @cached()
#     def query_advances(self):
#         q1 = Q(Q(folha__periodo__ano=self.payroll.periodo.ano) & Q(folha__periodo__mes__range=[1, 11]))
#         # q2 = Q(Q(folha__periodo__ano=self.payroll.periodo.ano - 1) & Q(folha__periodo__mes=12))

#         return self.employee.entries.filter(Q(evento__numero__in=self.focuses_on) & Q(q1 | q2))


@RunCodeManager.register("gfp-mpmt-rescission-13thsalary")
class ChristmasGratificationRescission(ChristmasGratification):

    title = "13° proporcional"

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        if employee.last_day_worked:
            kwargs["month"] = employee.last_day_worked.month
        super(ChristmasGratification, self).__init__(employee, payroll, event, **kwargs)

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.last_day_worked
            and self.month != self.employee.last_day_worked.month
            and self.year != self.employee.last_day_worked.year
        ):
            raise self.CalculationNotApplicable(
                "13º proporcional não pode ser pago em mês diferente do desligamento."
            )
        if self.employee.situacao_funcional_cache not in [
            "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
            "ATIVO_LIC_INTERESSE",
        ]:
            if (
                not self.employee.last_day_worked
                and not self.get_possessions()
                and not self.employee.get_afastamentos(
                    self.range_salary.first, self.range_salary.last
                ).filter(
                    baselicencaafastamento__estado__in=[1, 2, 3],
                    baselicencaafastamento__tipo__in=[14, 18],
                )
            ):
                raise self.CalculationNotApplicable(
                    "O Servidor %s não está desligado" % (self.employee)
                )
        if self.month in [12, 13]:
            raise self.CalculationNotApplicable(
                "13º proporcional não deve ser pago em dezembro! Para isso utilize a folha do 13º."
            )

    @property
    @cached()
    def range_base(self):
        return self.range_salary_for()

    # def base_socialsecurity(self):
    #     return self.value()

    def base_value(self):
        base = super(ChristmasGratificationRescission, self).base_value()
        ceiling = (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )
        return min(ceiling, base)

    @property
    def ceiling(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )

    def value(self):
        value = super(ChristmasGratificationRescission, self).value()
        if value:
            value = min(value, self.ceiling)
        return value

    @property
    @cached()
    def range_13salary(self):
        range_year = NewDateRange(
            datetime(self.year, 1, 1),
            datetime(self.year, self.month, self.range_salary.last.day),
        )
        return self.range_salary_for(range_salary=range_year)

    @property
    def references(self):
        return (self.year, 13)

    def base_socialsecurity(self):
        base = min(self._base_values()[1], self.ceiling)
        return base * self.factor_quantity()


@RunCodeManager.register("gfp-mpmt-anticipated13thsalary")
class AnticipatedChristmasGratification(AdvanceChristmasGratification):

    title = "Antecipação de 13° Salário"

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_month_valid()
        self.validate_first_christmas_gratification_on_year(
            self.advance_christmas_gratification_number
        )

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-mpmt-working-hours-reducer")
class WorkingHoursReducer(BaseCalculation):
    title = "Calculo para redução de jornada"
    description = """
        Este calculo deve ser usado para o desconto de jornada com base
        na carga horaria cadastrada do servidor.
    """
    MULTI_CALCULATE = True

    FULL_VALUE = False

    RECALCULATE_BASES = 3

    @cached()
    def percentage(self):
        pct_map = {35: 12.495625, 30: 24.998125}
        return pct_map.get(self.object.quantidade if self.object else 40, 0)
        # if self.object and self.object.quantidade in [30, 35]:
        #     return (1 - self.object.quantidade / 40) * 100
        # return 0

    def get_workloads(self):
        return CargaHoraria.objects.filter(servidor=self.employee).currents_in(
            range=self.range_salary
        )

    @cached()
    def _get_query(self):
        query = self.get_workloads()

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.reference_payroll,
                evento=self.event,
            )
            if self.entry:
                log.debug("%s:%s" % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def range_for_obj(self, obj):
        if self.object:
            return NewDateRange(self.object.data_inicio, self.object.data_fim)
        return NewDateRange()

    @property
    @cached()
    def range_calc(self):
        if self.object:
            return self.range_base.intersect(self.range_for_obj(self.object))
        return super().range_calc

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.value()

    def event_information(self):
        if self.object:
            return f"{self.object.quantidade:02}h"
        return ""

    # def unicode_for_obj(self, obj):
    #     return '%s' % obj


@RunCodeManager.register("gfp-mpmt-competing-gratification")
class CompetingGratification(BaseSalary):

    GRATIFICATIONS_NUMBER = ""

    TAG = ""

    # BASE_VALUE_FROM default: base_value calculado a partir do subsídio
    BASE_VALUE_FROM = "subsidio"

    # EMPLOYEE_TIPO default: tipo de Employee como Membro
    EMPLOYEE_TIPO = "M"

    # POSSESSION_TYPE default: 'EF' (Efetivo)
    POSSESSION_TYPE = ["EF"]

    # POSSESSION_TYPE default: cargo de Promotor de Justiça Substituto - MPMT
    CARGO_CODIGO = "00085"

    holder_aux_coord = None
    substitute_aux_coord = None

    def gratifications_to_check(self):
        try:
            item = Item.objects.get(key="gratifications_check")

            return item.value.split(",")
        except:
            msg = "Não há configurações das Gratificações Concorrentes em Painel de Controle > Configurações > Item de configuração > gratifications_check."
            raise self.CalculationNotApplicable(msg)

    def query_entry_competing_gratifications(self):
        query = Entry.objects.filter(
            contracheque__servidor=self.employee,
            contracheque__folha__periodo=self.payroll.periodo,
            evento__numero__in=self.gratifications_to_check(),
        ).exclude(evento__numero__in=[self.GRATIFICATIONS_NUMBER])

        return query

    def check_has_competing_gratifications(self):
        competing_events = self.query_entry_competing_gratifications()
        return competing_events.exists()

    def get_priority_gratification(self, num):
        try:
            tag_config = Choice.objects.get(
                app_label="rh", name="WORKPLACE_TAG", active=True, description=num
            )

            return tag_config.order_weight
        except:
            return 0

    def get_works_assignment(self):
        employee = self.employee
        if self.employee.tipo == "S" and self.is_substitute:
            employee = self.get_substitute_aux_coord().first().servidor

        query = employee.servidor_lotacao.filter(servidor=employee)
        query = query.exclude(
            Q(data_vigencia_inicio__gt=self.range_salary.last)
            | (
                ~Q(data_vigencia_fim=None)
                & Q(data_vigencia_fim__lt=self.range_salary.first)
            )
        )
        return query.filter(designacao=True).order_by("-data_vigencia_inicio")

    def get_fixed_office(self):
        return Cargo.objects.get(codigo=self.CARGO_CODIGO)

    def return_to_base_value(self, salarie):
        if self.employee.tipo == "M":
            return salarie.valor_membro
        else:
            return salarie.valor

    def get_salaries(self, cargo_recebe):
        range_ = self.payroll.date_range

        salaries = EstruturaTabelaSalarial.salarios(
            cargo_recebe, range_.first, range_.last
        )

        return salaries[0][1]

    def get_salarie_from_initial_salary(self, cargo_recebe):
        salarie = self.get_salaries(cargo_recebe)

        initial_salary = salarie.tabela_salarial.salarios.order_by(
            "referencia_nivel2d__ordem"
        ).first()

        return self.return_to_base_value(initial_salary)

    def get_initial_salary(self):
        base_value = 0.0
        if self.employee.tipo == "M":
            possession = self.get_possessions_by_type(self.POSSESSION_TYPE).first()
        else:
            self.CARGO_CODIGO = "00099"
            possession = self.get_possessions().first()

        if possession:
            cargo_recebe = self.get_fixed_office()
            base_value = self.get_salarie_from_initial_salary(cargo_recebe)

        return float(base_value)

    def get_salary_cap_member(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            base_value = periodo.first().salario_teto_membros
        else:
            base_value = (
                Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
            )

        return float(base_value)

    def get_works_assignment_without_substitution(self):
        workplaces = self.get_works_assignment()

        return workplaces.exclude(from_substitution=True)

    def get_day_in_competing_gratification(self, return_days=True):
        if self.employee.tipo == "M":
            query = self.get_works_assignment_without_substitution()
        else:
            query = self.get_works_assignment()

        days = 0
        range_salary_total_ds = None
        for ds in query:
            lotacao = ds.lotacao
            configs_tags = []
            configs_tags = lotacao.workplace_config_tags.filter(tag=self.TAG)
            range_salary_ds = self.range_salary.intersect(
                NewDateRange(ds.data_vigencia_inicio, ds.data_vigencia_fim)
            )

            range_tags_ds_salary = None
            for ct in configs_tags:
                if not range_tags_ds_salary:
                    range_tags_ds_salary = NewDateRange(
                        ct.start_validity, ct.end_validity
                    )
                else:
                    range_tags_ds_salary += NewDateRange(
                        ct.start_validity, ct.end_validity
                    )

            if not range_salary_total_ds and range_tags_ds_salary:
                range_salary_total_ds = range_salary_ds.intersect(range_tags_ds_salary)
            elif range_tags_ds_salary:
                range_salary_total_ds += range_salary_ds.intersect(range_tags_ds_salary)

        if return_days:
            if range_salary_total_ds:
                days = range_salary_total_ds.days
            return days
        else:
            return range_salary_total_ds

    def get_aux_coord(self):
        return MovimentacaoAuxiliarCoordenacao.objects.filter(
            Q(data_inicio__gte=self.payroll.date_range.first)
            | Q(data_fim__gt=self.payroll.date_range.first)
            | Q(data_fim__isnull=True)
        )

    def get_holder_aux_coord(self):
        return self.get_aux_coord().filter(servidor=self.employee)

    def get_substitute_aux_coord(self):
        return self.get_aux_coord().filter(substituto=self.employee)

    def get_ranges_holder_aux_coord(self):
        holder_ranges = []
        for aux_coord in self.get_holder_aux_coord():
            holder_ranges.append(
                NewDateRange.range_intersect(
                    [
                        aux_coord.data_inicio,
                        (
                            self.payroll.date_range.last
                            if aux_coord.data_fim is None
                            else aux_coord.data_fim
                        ),
                    ],
                    [self.payroll.date_range.first, self.payroll.date_range.last],
                )
            )

        return holder_ranges

    def get_ranges_substitute_aux_coord(self):
        substitute_ranges = []
        for aux_coord in self.get_substitute_aux_coord():
            if aux_coord.data_inicio < self.payroll.date_range.first:
                dt_inicio_range = self.payroll.date_range.first
            else:
                dt_inicio_range = aux_coord.data_inicio

            if aux_coord.data_fim is None or (
                aux_coord.data_fim > self.payroll.date_range.last
            ):
                dt_fim_range = self.payroll.date_range.last
            else:
                dt_fim_range = aux_coord.data_fim

            if dt_fim_range > dt_inicio_range:
                departures_holder = self._exclude_ranges_for_range_salary_aux_coord(
                    range_salary=NewDateRange(dt_inicio_range, dt_fim_range),
                    employee=aux_coord.servidor,
                )
                for dep_holder in departures_holder._ranges:
                    substitute_ranges.append(
                        NewDateRange.range_intersect(
                            [dt_inicio_range, dt_fim_range],
                            [dep_holder[0], dep_holder[1]],
                        )
                    )

        return substitute_ranges

    def _exclude_ranges_for_range_salary_aux_coord(
        self, range_salary=None, employee=None
    ):
        if employee is None:
            employee = self.employee

        if not range_salary:
            range_salary = self.range_salary

        range_unpaid_absences = NewDateRange()
        if self.IGNORE_DEPARTURE is False:
            for mc in AfastamentoOutroOrgao.objects.filter(servidor=employee).exclude(
                Q(data_inicio__gt=range_salary.last)
                | Q(onus=1)
                | Q(transito_pela_folha=True)
                | Q(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)
            for absence in (
                BaseLicencaAfastamento.objects.filter(servidor=employee)
                .exclude(
                    Q(data_fim__lt=range_salary.first)
                    | Q(data_inicio__gt=range_salary.last)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )

        return range_unpaid_absences

    def validate_employee_type(self):
        if self.employee.tipo != self.EMPLOYEE_TIPO:
            raise self.CalculationNotApplicable(
                "Não tem direito! Verba somente para Membros."
            )

    def validate_employee_workplace(self):
        workplaces = self.get_works_assignment()
        lotacoes = []
        for wp in workplaces:
            lotacoes.append(wp.lotacao)

        query = WorkplaceConfigTag.objects.filter(workplace__in=lotacoes)
        query = query.filter(tag=self.TAG)
        query = query.exclude(
            Q(start_validity__gt=self.range_salary.last)
            | (~Q(end_validity=None) & Q(end_validity__lt=self.range_salary.first))
        )

        if not query.exists():
            raise self.CalculationNotApplicable(
                f"WORKPLACE_TAG {self.TAG}: o Servidor não tem exercicio em lotação ou a lotação não tem a configuração!"
            )

    def validate_competing_gratif_with_greater_value(self):
        if self.check_has_competing_gratifications():
            competing_event = self.query_entry_competing_gratifications().first()

            if float(competing_event.valor) > float(self.valor()):
                raise self.CalculationNotApplicable(
                    "Há uma verba de gratificação concorrente de maior valor aplicada neste período na folha do Servidor!"
                )

    def validate_competing_gratif_with_eq_value(self):
        if self.check_has_competing_gratifications():
            competing_event = self.query_entry_competing_gratifications().first()
            competing_event_prior = self.get_priority_gratification(
                competing_event.evento.numero
            )
            competing_event_value = round(float(competing_event.valor), 2)

            gratif_prior = self.get_priority_gratification(self.GRATIFICATIONS_NUMBER)
            calc_value = round(float(self.valor()), 2)

            if (
                competing_event_value == calc_value
            ) and competing_event_prior > gratif_prior:
                msg = "Há uma verba de gratificação concorrente com mesmo valor e maior prioridade aplicada neste período na folha do Servidor!"
                raise self.CalculationNotApplicable(msg)

    def validate_if_employee_in_aux_coord(self):
        if self.employee.tipo == "S":
            if (
                MovimentacaoAuxiliarCoordenacao.objects.filter(
                    Q(servidor=self.employee) | Q(substituto=self.employee)
                ).exists()
                is False
            ):
                raise self.CalculationNotApplicable(
                    "O Servidor não está em Designação para Auxiliar de Coordenação!"
                )

    def set_if_is_holder_or_subtitute(self):
        self.holder_aux_coord = self.get_holder_aux_coord()
        self.substitute_aux_coord = self.get_substitute_aux_coord()

        self.is_holder = True if self.holder_aux_coord.exists() else False
        self.is_substitute = True if self.substitute_aux_coord.exists() else False

    def validate_if_has_aux_coord_in_payroll_period(self):
        if (
            self.employee.tipo == "S"
            and self.is_holder is False
            and self.is_substitute is False
        ):
            raise self.CalculationNotApplicable(
                f"""
            O Servidor não tem período de Designação para Auxiliar de Coordenação em concomitância com o período da folha: {self.payroll}!
            """
            )

    def validate_member_in_workplaces_substitution(self):
        if self.employee.tipo == "M":
            workplaces = self.get_works_assignment_without_substitution()

            if workplaces.count() == 0:
                raise self.CalculationNotApplicable(
                    """Desconsiderando as designações de substituição, o membro não
                tem designações para para aplicar a verba."""
                )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_employee_type()
        self.validate_employee_workplace()
        # self.validate_competing_gratif_with_greater_value()
        # self.validate_competing_gratif_with_eq_value()
        self.validate_member_in_workplaces_substitution()

    def base_value(self):
        if self.BASE_VALUE_FROM == "subsidio":
            return super().base_value()

        if self.BASE_VALUE_FROM == "inicial_carreira":
            return self.get_initial_salary()

        if self.BASE_VALUE_FROM == "salary_cap_member":
            return self.get_salary_cap_member()

        if self.BASE_VALUE_FROM == "salary_cap_member_inicial_carreira_servidor":
            if self.employee.tipo == "M":
                return self.get_salary_cap_member()
            else:
                return self.get_initial_salary()

    def base_socialsecurity(self):
        return self.value()

    @cached()
    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"] or 0)
        else:
            if self.employee.tipo == "M":
                return self.get_day_in_competing_gratification()
            else:
                days = 0
                if self.is_holder:
                    exclude_ranges = self._exclude_ranges_for_range_salary_aux_coord()
                    for holder_range in self.get_ranges_holder_aux_coord():
                        date_range = NewDateRange(holder_range[0], holder_range[1])
                        days += (date_range - exclude_ranges).days

                if self.is_substitute:
                    exclude_ranges = self._exclude_ranges_for_range_salary_aux_coord()
                    for substitute_range in self.get_ranges_substitute_aux_coord():
                        date_range = NewDateRange(
                            substitute_range[0], substitute_range[1]
                        )
                        days += (date_range - exclude_ranges).days

                return days


@RunCodeManager.register("gfp-mpmt-grat-procurador-juridico")
class GratSubProcuradorJuridico(CompetingGratification):

    title = "GRAT. SUB. PROCURADOR JURÍDICO"

    RECALCULATE_BASES = 3

    TAG = "21"

    GRATIFICATIONS_NUMBER = "04100"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-procurador-adm")
class GratSubProcuradorAdm(CompetingGratification):

    title = "GRAT. SUB. PROCURADOR ADM"

    RECALCULATE_BASES = 3

    TAG = "20"

    GRATIFICATIONS_NUMBER = "04200"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-procurador-plan")
class GratSubProcuradorPlan(CompetingGratification):

    title = "GRAT. SUB. PROCURADOR PLAN"

    RECALCULATE_BASES = 3

    TAG = "24"

    GRATIFICATIONS_NUMBER = "04300"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-func-coord-10")
class GratFuncCoord10(CompetingGratification):

    title = "GRAT. FUNÇÃO COORD. 10%"

    RECALCULATE_BASES = 3

    TAG = "12"

    GRATIFICATIONS_NUMBER = "11400"

    BASE_VALUE_FROM = "salary_cap_member_inicial_carreira_servidor"

    def validar_se_tem_verba_indeniz_comp_grat_coord_art4E3582011(self):
        evento = Evento.objects.get(numero="15443")
        contracheque = self.payroll.paychecks.filter(servidor=self.employee)

        if contracheque.exists() and contracheque.first().lancamentos.filter(
            evento=evento
        ):
            msg = f"""Não é possível aplicar a verba.
            O contracheque possui a verba {evento}."""
            raise self.CalculationNotApplicable(msg)

    def _exclude_ranges_for_range_salary_aux_coord(
        self, range_salary=None, employee=None
    ):
        """
        Método responsável por buscar os afastamentos em relação ao mês anterior ao que está sendo calculado.
        """

        if employee is None:
            employee = self.employee

        if not range_salary:
            range_salary = self.range_salary

        mes_anterior = self.payroll.date_range.first - relativedelta(months=1)
        dt_range_mes_anterior = NewDateRange.from_month(
            mes_anterior.year, mes_anterior.month
        )
        mes_anterior_inicio = dt_range_mes_anterior.first
        mes_anterior_fim = dt_range_mes_anterior.last

        range_unpaid_absences = NewDateRange()
        if self.IGNORE_DEPARTURE is False:
            for mc in AfastamentoOutroOrgao.objects.filter(servidor=employee).exclude(
                Q(data_inicio__gt=mes_anterior_fim)
                | Q(onus=1)
                | Q(transito_pela_folha=True)
                | Q(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)
            for absence in (
                BaseLicencaAfastamento.objects.filter(servidor=employee)
                .exclude(
                    Q(data_fim__lt=mes_anterior_inicio)
                    | Q(data_inicio__gt=mes_anterior_fim)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )

        return range_unpaid_absences

    def get_ranges_substitute_aux_coord(self):
        """
        Método responsável por buscar as atuações de auxílio coordenação do substituto, que tem como
        base os afastamentos do titulas.
        """

        mes_anterior = self.payroll.date_range.first - relativedelta(months=1)
        dt_range_mes_anterior = NewDateRange.from_month(
            mes_anterior.year, mes_anterior.month
        )
        mes_anterior_inicio = dt_range_mes_anterior.first
        mes_anterior_fim = dt_range_mes_anterior.last

        substitute_ranges = []
        for aux_coord in self.get_substitute_aux_coord():
            if aux_coord.data_inicio < self.payroll.date_range.first:
                dt_inicio_range = self.payroll.date_range.first
            else:
                dt_inicio_range = aux_coord.data_inicio

            if aux_coord.data_fim is None or (
                aux_coord.data_fim > self.payroll.date_range.last
            ):
                dt_fim_range = self.payroll.date_range.last
            else:
                dt_fim_range = aux_coord.data_fim

            if dt_fim_range > dt_inicio_range:
                departures_holder = self._exclude_ranges_for_range_salary_aux_coord(
                    range_salary=NewDateRange(mes_anterior_inicio, mes_anterior_fim),
                    employee=aux_coord.servidor,
                )
                for dep_holder in departures_holder._ranges:
                    substitute_ranges.append(
                        NewDateRange.range_intersect(
                            [mes_anterior_inicio, mes_anterior_fim],
                            [dep_holder[0], dep_holder[1]],
                        )
                    )

        return substitute_ranges

    def quantity(self):
        qtd = super().quantity()

        if self.employee.tipo == "M" or self.is_substitute:
            return qtd
        else:
            return self.maximum_quantity()

    def validate(self):
        self.set_if_is_holder_or_subtitute()
        self.validate_not_paycheck_pension()
        self.validate_employee_workplace()
        self.validate_if_employee_in_aux_coord()
        self.validate_if_has_aux_coord_in_payroll_period()
        self.validate_member_in_workplaces_substitution()
        self.validar_se_tem_verba_indeniz_comp_grat_coord_art4E3582011()


@RunCodeManager.register("gfp-mpmt-grat-func-coord-30-caad")
class GratFuncCoord30CAAD(GratFuncCoord10):

    title = "GRAT. FUNÇÃO COORD. 30% - CAAD"

    RECALCULATE_BASES = 3

    TAG = "14"

    GRATIFICATIONS_NUMBER = "12400"

    BASE_VALUE_FROM = "salary_cap_member_inicial_carreira_servidor"


@RunCodeManager.register("gfp-mpmt-grat-func-coord-8")
class GratFuncCoord8(CompetingGratification):

    title = "GRAT. FUNÇÃO COORD. 8%"

    RECALCULATE_BASES = 3

    TAG = "5"

    GRATIFICATIONS_NUMBER = "11500"

    BASE_VALUE_FROM = "inicial_carreira"

    def validate(self):
        self.set_if_is_holder_or_subtitute()
        self.validate_not_paycheck_pension()
        self.validate_employee_workplace()
        self.validate_if_employee_in_aux_coord()
        self.validate_if_has_aux_coord_in_payroll_period()
        self.validate_member_in_workplaces_substitution()


@RunCodeManager.register("gfp-mpmt-grat-func-coord-7")
class GratFuncCoord7(CompetingGratification):

    title = "GRAT. FUNÇÃO COORD. 7%"

    RECALCULATE_BASES = 3

    TAG = "4"

    GRATIFICATIONS_NUMBER = "11600"

    BASE_VALUE_FROM = "inicial_carreira"

    def validate(self):
        self.set_if_is_holder_or_subtitute()
        self.validate_not_paycheck_pension()
        self.validate_employee_workplace()
        self.validate_if_employee_in_aux_coord()
        self.validate_if_has_aux_coord_in_payroll_period()
        self.validate_member_in_workplaces_substitution()


@RunCodeManager.register("gfp-mpmt-grat-func-coord-6")
class GratFuncCoord6(CompetingGratification):

    title = "GRAT. FUNÇÃO COORD. 6%"

    RECALCULATE_BASES = 3

    TAG = "3"

    GRATIFICATIONS_NUMBER = "11700"

    BASE_VALUE_FROM = "inicial_carreira"

    def validate(self):
        self.set_if_is_holder_or_subtitute()
        self.validate_not_paycheck_pension()
        self.validate_employee_workplace()
        self.validate_if_employee_in_aux_coord()
        self.validate_if_has_aux_coord_in_payroll_period()
        self.validate_member_in_workplaces_substitution()


@RunCodeManager.register("gfp-mpmt-grat-func-coord-5")
class GratFuncCoord5(CompetingGratification):

    title = "GRAT. FUNÇÃO COORD. 5%"

    RECALCULATE_BASES = 3

    TAG = "2"

    GRATIFICATIONS_NUMBER = "11800"

    BASE_VALUE_FROM = "inicial_carreira"

    def validate(self):
        self.set_if_is_holder_or_subtitute()
        self.validate_not_paycheck_pension()
        self.validate_employee_workplace()
        self.validate_if_employee_in_aux_coord()
        self.validate_if_has_aux_coord_in_payroll_period()
        self.validate_member_in_workplaces_substitution()


@RunCodeManager.register("gfp-mpmt-grat-gaeco")
class GratGaeco(CompetingGratification):

    title = "GRAT. GAECO"

    RECALCULATE_BASES = 3

    TAG = "11"

    GRATIFICATIONS_NUMBER = "09819"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-naco")
class GratNaco(CompetingGratification):

    title = "GRAT. NACO"

    RECALCULATE_BASES = 3

    TAG = "13"

    GRATIFICATIONS_NUMBER = "09719"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-cons-superior")
class GratConsSuperior(CompetingGratification):

    title = "GRAT. CONSELHO SUPERIOR"

    RECALCULATE_BASES = 3

    TAG = "7"

    GRATIFICATIONS_NUMBER = "11319"

    BASE_VALUE_FROM = "salary_cap_member"

    def validate_if_member_elective(self):
        if self.employee.type_by_possession == "MEL":
            raise self.CalculationNotApplicable("Membros eletivos não tem direito!")

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_employee_type()
        self.validate_employee_workplace()
        # self.validate_competing_gratif_with_greater_value()
        # self.validate_competing_gratif_with_eq_value()
        self.validate_member_in_workplaces_substitution()
        self.validate_if_member_elective()


@RunCodeManager.register("gfp-mpmt-exerc-cumulativo-subst-prom-proc")
class ExercCumulSubstPromProc(WorkDaysCalculation):

    title = "Exercício Cumulativo - Substituição - Prom-Proc"

    def validate_employee_type(self):
        if self.employee.tipo != "M":
            raise self.CalculationNotApplicable(
                "Não tem direito! Verba somente para Membros."
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_employee_type()

    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"] or 0)
        else:
            return (
                self.range_salary_for().business_days
                if self.BASE_BUSINESSDAYS
                else self.range_salary_for().days
            )

    def base_value(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            base_value = periodo.first().salario_teto_membros
        else:
            base_value = (
                Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
            )

        return float(base_value)


@RunCodeManager.register("gfp-mpmt-grat-cao")
class GratCao(CompetingGratification):

    title = "GRAT. CAO"

    RECALCULATE_BASES = 3

    TAG = "8"

    GRATIFICATIONS_NUMBER = "11219"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-ceaf")
class GratCeaf(CompetingGratification):

    title = "GRAT. CEAF"

    RECALCULATE_BASES = 3

    TAG = "10"

    GRATIFICATIONS_NUMBER = "11019"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-nare")
class GratNare(CompetingGratification):

    title = "GRAT. NARE"

    RECALCULATE_BASES = 3

    TAG = "9"

    GRATIFICATIONS_NUMBER = "11119"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-ouvidor")
class GratOuvidor(CompetingGratification):

    title = "GRAT. OUVIDOR"

    RECALCULATE_BASES = 3

    TAG = "19"

    GRATIFICATIONS_NUMBER = "08719"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-ouvidor-adjunto")
class GratOuvidorAdjunto(CompetingGratification):

    title = "GRAT. OUVIDOR ADJUNTO"

    RECALCULATE_BASES = 3

    TAG = "27"

    GRATIFICATIONS_NUMBER = "08800"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-aux-adm-superior")
class GratAuxAdmSuperior(CompetingGratification):

    title = "GRAT. AUXILIAR ADM. SUPERIOR"

    RECALCULATE_BASES = 3

    TAG = "25"

    GRATIFICATIONS_NUMBER = "08919"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-grat-func-aux-gab-coger")
class GratFuncAuxGabCoger(CompetingGratification):

    title = "GRAT. FUNÇÃO AUX. GAB COGER"

    RECALCULATE_BASES = 3

    TAG = "22"

    GRATIFICATIONS_NUMBER = "09400"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-func-aux-gab-pgj")
class GratFuncAuxGabPgj(CompetingGratification):

    title = "GRAT. FUNÇÃO AUX. GAB PGJ"

    RECALCULATE_BASES = 3

    TAG = "23"

    GRATIFICATIONS_NUMBER = "09500"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-grat-func-orgao-aux")
class GratFuncOrgaoAux(CompetingGratification):

    title = "GRAT. FUNÇÃO ORGÃOS AUXILIARES"

    RECALCULATE_BASES = 3

    TAG = "26"

    GRATIFICATIONS_NUMBER = "09600"

    BASE_VALUE_FROM = "subsidio"


@RunCodeManager.register("gfp-mpmt-indeniz-compens-isento-ir")
class GratIndenizCompensIsentoIR(CompetingGratification):

    title = "GRAT. INDENIZAÇÃO COMPENSATÓRIA - ISENTO IR - ART.4°-E-358/2011"

    RECALCULATE_BASES = 3

    TAG = "31"

    GRATIFICATIONS_NUMBER = "15400"

    BASE_VALUE_FROM = "salary_cap_member"


@RunCodeManager.register("gfp-mpmt-gratiffication-collection")
class GratificationCollection(CompetingGratification):

    RECALCULATE_BASES = 3

    TAG = "6"

    GRATIFICATIONS_NUMBER = "13600"

    BASE_VALUE_FROM = "subsidio"

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        if not range_salary:
            range_salary = self.range_salary

        range_unpaid_absences = NewDateRange()

        for mc in AfastamentoOutroOrgao.objects.filter(servidor=self.employee).exclude(
            Q(data_inicio__gt=range_salary.last)
            | Q(onus=1)
            | Q(transito_pela_folha=True)
            | Q(estado=AFASTAMENTO_CANCELADO)
        ):
            range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)

        for absence in (
            BaseLicencaAfastamento.objects.filter(
                # remunerado=False,
                servidor=self.employee
            )
            .exclude(
                tipo__in=[
                    7,
                ]
            )
            .exclude(
                Q(data_fim__lt=range_salary.first)
                | Q(data_inicio__gt=range_salary.last)
            )
            .exclude(~Q(afastamento__afastamentooutroorgao=None))
            .exclude(estado=AFASTAMENTO_CANCELADO)
        ):
            range_unpaid_absences += NewDateRange(absence.data_inicio, absence.data_fim)

        return range_unpaid_absences

    @cached()
    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"] or 0)
        else:
            range = self.get_day_in_competing_gratification(return_days=False)

            return range.days

    def base_value(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            payroll_period = periodo.first()
        else:
            payroll_period = Periodo.objects.order_by("-ano", "-mes").first()

        return float(payroll_period.salario_teto_membros)

    def value(self):
        # o cálculo é 1/3 do valor do teto de membro da config de Periodo do mês calculado

        value = self.base_value() * float(0.33333333333)
        value = (value / self.maximum_quantity()) * self.quantity()

        return value


@RunCodeManager.register("gfp-mpmt-difficult-access-base")
class DifficultAccessProsecutionDesignationBase(BaseSalary):
    title = "DESIGNAÇÃO DE PROMOTORIA DIFICIL PROV."
    description = """
        Este calculo deve ser usado para o quantidade dias no mes em lotacoes e dificial acesso.
    """
    MULTI_CALCULATE = True

    FULL_VALUE = False

    RECALCULATE_BASES = 3

    TYPES = ["EF", "CM"]

    POSSESSION_TYPE = ["EF", "CM"]

    EMPLOYEE_TIPO = "M"

    # POSSESSION_TYPE default: cargo de Promotor de Justiça Substituto - MPMT
    CARGO_CODIGO_MEMBER = "00085"

    CARGO_CODIGO_NOT_MEMBER = "00099"

    TYPES_BY_POSSESSION = []

    def get_fixed_office(self):
        codigo = (
            self.CARGO_CODIGO_MEMBER
            if self.employee.tipo == "M"
            else self.CARGO_CODIGO_NOT_MEMBER
        )
        return Cargo.objects.get(codigo=codigo)

    def get_last_possession_office(self):
        return self.employee.posses_ativas.last().quadro.cargo

    def get_salaries(self, cargo_recebe):
        range_ = self.payroll.date_range

        salaries = EstruturaTabelaSalarial.salarios(
            cargo_recebe, range_.first, range_.last
        )

        return salaries[0][1]

    def return_to_base_value(self, salarie):
        if self.employee.tipo == "M":
            return salarie.valor_membro
        else:
            return salarie.valor

    def get_salarie_from_initial_salary(self, cargo_recebe):
        salarie = self.get_salaries(cargo_recebe)

        initial_salary = salarie.tabela_salarial.salarios.order_by(
            "referencia_nivel2d__ordem"
        ).first()

        return self.return_to_base_value(initial_salary)

    def get_salarie_from_salaries(self, cargo_recebe):
        salarie = self.get_salaries(cargo_recebe)

        return self.return_to_base_value(salarie)

    def base_value(self):
        possession = self.get_possessions_by_type(self.POSSESSION_TYPE).first()
        base_value = 0.0

        if possession:
            cargo_recebe = self.get_fixed_office()
            base_value = self.get_salarie_from_initial_salary(cargo_recebe)

        base_value = float(base_value) * (float(10.0) / 100.00)
        return float(base_value)

    def _get_query(self):
        ids = super(DifficultAccessProsecutionDesignationBase, self)._get_query()
        return [id_ for id_ in ids if id_[0:2] in self.TYPES]

    def __init__(self, employee, payroll, event, **kwargs):
        super(DifficultAccessProsecutionDesignationBase, self).__init__(
            employee, payroll, event, **kwargs
        )

    def validate_type_by_possession(self):
        if self.employee.type_by_possession not in self.TYPES_BY_POSSESSION:
            raise self.CalculationNotApplicable(
                "O tipo do Servidor não tem diretiro à verba!"
            )

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_type_by_possession()
        if not self.validate_in_difficulty_access():
            raise self.CalculationNotApplicable(
                "O Servidor %s não tem exercicio em lotação de díficil acesso!"
                % (self.employee)
            )

    def validate_in_difficulty_access(self):

        workplaces = self.get_works_assignment()
        lotacoes = []
        for wp in workplaces:
            lotacoes.append(wp.lotacao)

        query = WorkplaceConfigTag.objects.filter(workplace__in=lotacoes)
        query = query.filter(tag="1")
        query = query.exclude(
            Q(start_validity__gt=self.range_salary.last)
            | (~Q(end_validity=None) & Q(end_validity__lt=self.range_salary.first))
        )

        return query.exists()

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        """
        Art. 5º. O pagamento da verba indenizatória de que trata o presente Ato será suspenso nos seguintes casos:
        I – licença médica superior a 15 (quinze) dias;
        II – licença por motivo de doença em pessoa da família superior a 05 (cinco) dias;
        III – licença por motivo de afastamento de cônjuge ou companheiro;
        IV – licença para serviço militar;
        V – licença para atividade política;
        VI – licença para tratar de interesses particulares;
        VII – outras licenças previstas em lei, exceto a licença-maternidade, a licença-paternidade e o afastamento para exercício de mandato classista;
        VIII – afastamento para exercício de mandato eletivo;
        X – afastamento para servir em organismo internacional;
        XI – suspensão em virtude de penalidade disciplinar, durante o período de sua duração;
        XII - afastamento preventivo;
        XIII – não encaminhamento da folha de frequência ao Departamento de Gestão de Pessoas;
        XIV - faltas injustificadas.
        """
        range_ = super(
            DifficultAccessProsecutionDesignationBase, self
        )._exclude_ranges_for_range_salary(range_salary=range_salary)
        q = self.employee.departures(
            self.payroll.periodo.range.first, self.payroll.periodo.range.last
        ).filter(tipo=62)

        if q.exists() is False:
            q = (
                q.filter(
                    # Q(tipo__in=[9, 10, 11, 14, 15, 16, 17, 18, 20, 21, 23, 24, 25, 26, 27, 28, 29, 37, 44])
                    Q(
                        tipo__in=[
                            44,
                        ]
                    )
                )
                .filter(
                    ~Q(afastamento__afastamentooutroorgao__transito_pela_folha=True)
                )
                .exclude(
                    # Excluindo os membros que estão afastado por processo disciplinar (44), pois os mesmos não podems ser
                    # punidos de acordo com Art. 202 da Lei 51/2008
                    Q(tipo=44)
                    & Q(servidor__tipo="M")
                )
            )

        map_suspend_after = {
            9: 15,  # Licença saúde suspender após 15 dias
            10: 15,  # Licença saúde suspender após 15 dias
            11: 5,  # Licença saúde pessoa da familia suspender após 5 dias
            37: 15,  # Licença saúde suspender após 15 dias
        }
        for l in q.filter():
            days_suspend_after = map_suspend_after.get(l.tipo, 0)
            dt_start = l.data_inicio + relativedelta(days=days_suspend_after)
            if dt_start <= l.data_fim:
                range_ += NewDateRange(dt_start, l.data_fim)
                log.info(f"dias: {range_}")
            elif not days_suspend_after == 0:
                range_ = NewDateRange(0, 0)

        # log.debug('RANGE LICENSES: %s' % range_)

        return range_

    def get_works_assignment(self):

        query = self.employee.servidor_lotacao.filter(servidor=self.employee)

        query = query.exclude(
            Q(data_vigencia_inicio__gt=self.range_salary.last)
            | (
                ~Q(data_vigencia_fim=None)
                & Q(data_vigencia_fim__lt=self.range_salary.first)
            )
        )

        query = query.filter(designacao=True)

        return query.order_by("-data_vigencia_inicio")

    def get_day_in_difficult_access(self):
        query = self.get_works_assignment()
        days = 0
        range_salary_total_ds = None
        for ds in query:
            lotacao = ds.lotacao
            configs_tags = []
            configs_tags = lotacao.workplace_config_tags.filter(tag="1")
            range_salary_ds = self.range_salary.intersect(
                NewDateRange(ds.data_vigencia_inicio, ds.data_vigencia_fim)
            )

            range_tags_ds_salary = None
            for ct in configs_tags:
                if not range_tags_ds_salary:
                    range_tags_ds_salary = NewDateRange(
                        ct.start_validity, ct.end_validity
                    )
                else:
                    range_tags_ds_salary += NewDateRange(
                        ct.start_validity, ct.end_validity
                    )

            if not range_salary_total_ds and range_tags_ds_salary:
                range_salary_total_ds = range_salary_ds.intersect(range_tags_ds_salary)
            elif range_tags_ds_salary:
                range_salary_total_ds += range_salary_ds.intersect(range_tags_ds_salary)

        if range_salary_total_ds:
            ranges = range_salary_total_ds - self._exclude_ranges_for_range_salary(
                range_salary=range_salary_total_ds
            )
            # days = range_salary_total_ds.days
            days = ranges.days

        return days

    @cached()
    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"] or 0)
        else:
            return self.get_day_in_difficult_access()

    def base_socialsecurity(self):
        return self.value()

    # def percentage(self):
    #     return float(10.00)


@RunCodeManager.register("gfp-mpmt-difficult-access-member")
class DifficultAccessProsecutionDesignationMember(
    DifficultAccessProsecutionDesignationBase
):

    TYPES_BY_POSSESSION = ["MBR", "MBR2", "MEL", "MCM", "MEC", "MEL2", "MCM2", "MEC2"]

    def base_value(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            base_value = periodo.first().salario_teto_membros
        else:
            base_value = (
                Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
            )

        return float(base_value)


@RunCodeManager.register("gfp-mpmt-difficult-access-employee")
class DifficultAccessProsecutionDesignationEmployee(
    DifficultAccessProsecutionDesignationBase
):

    TYPES_BY_POSSESSION = ["EFE", "ECM", "EFC", "CMS"]


@RunCodeManager.register("gfp-mpmt-cumulative-exercises-permanent")
class CumulativeExercisesPermanent(SalaryEffective):

    title = "Exercício Cumulativo Permanente"

    EMPLOYEE_TIPO = "M"  # Membro

    PARAMS_ = ["info", "oIds", "qnt", "pct"]

    def validate_if_is_member(self):
        if self.employee.tipo != self.EMPLOYEE_TIPO:
            raise self.CalculationNotApplicable(
                "Somente Membros tem direito a essa verba!"
            )

    def validar_se_tem_verba_indeniz_comp_exerc_cumul_art4E3582011(self):
        evento = Evento.objects.get(numero="15444")
        contracheque = self.payroll.paychecks.filter(servidor=self.employee)

        if contracheque.exists() and contracheque.first().lancamentos.filter(
            evento=evento
        ):
            msg = f"""Não é possível aplicar a verba.
            O contracheque possui a verba {evento}."""
            raise self.CalculationNotApplicable(msg)

    def validate(self):
        self.validate_if_is_member()
        self.validar_se_tem_verba_indeniz_comp_exerc_cumul_art4E3582011()

    def get_config_period(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            return periodo.first()
        else:
            return Periodo.objects.order_by("-ano", "-mes").first()

    def base_value(self):
        payroll_period = self.get_config_period()

        return float(payroll_period.salario_teto_membros)

    def buscar_desigs(self, dt_range, by_employee=True):
        q = (
            ServidorLotacao.objects.filter(
                servidor__type_by_possession__in=[
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                ],
                designacao=True,
                from_substitution=False,
                data_vigencia_inicio__lte=dt_range.last,
            )
            .filter(
                Q(
                    Q(data_vigencia_fim__isnull=True)
                    | Q(data_vigencia_fim__gte=dt_range.first)
                )
            )
            .filter(
                Q(lotacao__nome__icontains="PROMOTORIA ")
                | Q(lotacao__nome__icontains="PROCURADORIA ")
            )
            .exclude(
                main=True,
            )
        )

        if by_employee:
            q = q.filter(servidor=self.employee)

        return q

    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            try:
                return float(self.params["qnt"])
            except Exception:
                return 0
        else:
            desigs_servidor = self.buscar_desigs(self.range_salary)

            qtd_dias_consolidado = 0
            qtd_dias_afastamento = 0
            for desig in desigs_servidor:
                dt_fim_desig = (
                    self.range_salary.last
                    if desig.data_vigencia_fim is None
                    else desig.data_vigencia_fim
                )
                dt_range_desig = NewDateRange(desig.data_vigencia_inicio, dt_fim_desig)

                dt_range_intersect_desig = dt_range_desig.intersect(self.range_salary)
                qtd_dias_afast_desig = buscar_afastamentos_periodo(
                    desig.servidor, dt_range_intersect_desig
                )

                qtd_dias_consolidado += dt_range_intersect_desig.days
                qtd_dias_afastamento += qtd_dias_afast_desig

            if qtd_dias_consolidado > self.range_salary.days:
                qtd_dias_consolidado = self.range_salary.days

            if qtd_dias_afastamento > self.range_salary.days:
                qtd_dias_afastamento = self.range_salary.days

            return qtd_dias_consolidado - qtd_dias_afastamento

    def percentage(self):
        if "pct" in self.params and self.params["pct"] not in ["", 0]:
            try:
                return float(self.params["pct"])
            except Exception:
                return 0
        else:
            desigs_servidor = self.buscar_desigs(self.range_salary)
            if not desigs_servidor:
                return 0
            else:
                pcts = []
                for desig in desigs_servidor:
                    q = self.buscar_desigs(self.range_salary, by_employee=False).filter(
                        lotacao=desig.lotacao
                    )

                    qtd = (
                        q.values("servidor")
                        .annotate(total=Count("servidor"))
                        .order_by("servidor")
                        .count()
                    )
                    if qtd == 1:
                        pcts.append(
                            float(15) if desig.data_vigencia_fim is None else float(10)
                        )
                    else:
                        pcts.append(float(15) / float(qtd))

                pcts.sort()
                return pcts[-1]

    def value(self):
        valor_perc = (self.base_value() * self.percentage()) / 100

        return (valor_perc / self.maximum_quantity()) * self.quantity()

    def installments_paid(self):
        return 1

    def installment(self):
        return 1

    def employer_value(self):
        return 0


@RunCodeManager.register("gfp-mpmt-indeniz-comp-grat-coord-art-4e3582001")
class IndenizCompGratCoordArt4E3582011(GratFuncCoord10):

    title = "Indeniz. Comp. Art 4°-E 358/2011 - Grat. Coordenador"

    def validate(self):
        pass


@RunCodeManager.register("gfp-mpmt-indeniz-comp-exerc-cumul-art-4e3582011")
class IndenizCompExercCumuldArt4E3582011(CumulativeExercisesPermanent):

    title = "Indeniz. Comp. Art 4°-E 358/2011 - Exercício Cumulativo"

    def validate(self):
        pass
