# -*- coding: utf-8 -*-

from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from memoization import cached

from contrib.cache import get_cache, set_cache
from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.calcs.mpto.base import BaseCalculation, WorkDaysCalculation
from rh.gfp.models import EstruturaTabelaSalarial, ExtraPaymentPeriod
from rh.gfp.models import FolhaEvento as Entry, Folha as Payroll
from rh.models import EncargoFinanceiro as FinancialBurden
from rh.models import MovimentacaoSubstituicao as SubstitutionMovement
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpto-basesalary")
class BaseSalary(WorkDaysCalculation):
    title = "Calculo Base para remuneração"
    description = """
        Este cálculo pode ser usado como base para remuneração em geral.
        Se for usado diretamente será retornado o valor da remuneração total
        do servidor (efetivo + (função ou (gratification + comissão) + eletivo + extras)
    """

    # EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {'S': ['AC']}
    EXCLUDE_BY_JOB = ["AC"]
    INCLUDE_EXTRASPAYMENTS = [
        "VPI",
    ]
    FULL_SALARY = False
    FILTER_QUERY = 2
    FILTER_BY = 2

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

        if get_cache(cache_id, self.group_key_cache):
            # log.debug('USINGCACHE: %s' % cache_id)
            return get_cache(cache_id, self.group_key_cache)
        # log.debug('NOTCACHE: %s [%s]' % (cache_id, self.range))

        # log.debug('CREATING CACHE SALARY BY TYPE FOR %s (%s)' % (cache_id, self))

        salaries = {}
        for p in self.get_possessions():
            # log.debug('%s, %s' %(p, p.instancia_modelo.__class__.__name__))
            range_ = self.range_salary_for(p)

            if (
                p.quadro
                and p.quadro.cargo.tipo_lei_cargo
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

            elif hasattr(p, "requestmove"):
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
                            "type": "AC",
                            "extra": 0.0,
                            "percentage": False,
                            "onus": p.requestmove.onus == 2,  # Onus para requisitante?
                        }
                    )

            elif p.quadro and not p.quadro.cargo.tipo_lei_cargo == "AC":
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
                    salaries[idx].append(
                        {
                            "range": range_cm.toordinals(),
                            "salary": salary[1],
                            "type": p.quadro.cargo.tipo_lei_cargo,
                            "value": (
                                salary[1].valor
                                if not self.employee.tipo == "M"
                                else salary[1].valor_membro
                            ),
                            "gratification": (
                                salary[1].gratificacao
                                if not self.employee.tipo == "M"
                                else salary[1].gratificacao_membro
                            ),
                            "extra": 0.0,
                            "percentage": (
                                False
                                if (
                                    salary[1].referencia_nivel2d.tipo_gratificacao == 1
                                    and self.employee.tipo != "M"
                                )
                                or (
                                    salary[
                                        1
                                    ].referencia_nivel2d.tipo_gratificacao_membro
                                    == 1
                                    and self.employee.tipo == "M"
                                )
                                else True
                            ),
                            "onus": True,
                        }
                    )

        set_cache(cache_id, salaries, self.group_key_cache)

        return salaries

    def extract_base_salary_by_period(self):
        cache_id = "CSP%s%s%s" % (
            self.identification_payroll,
            self.employee.matricula,
            "".join(str(t or "000000") for t in self.validity.toordinals()),
        )

        if get_cache(cache_id, self.group_key_cache):
            # log.debug('USINGCACHE: %s' % cache_id)
            return get_cache(cache_id, self.group_key_cache)
        # log.debug('NOTCACHE: %s' % cache_id)

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
                # log.debug(float(value['salaries'][tipo]['value'] * value['range'].days) / self.base_days)
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

        if get_cache(cache_id, self.group_key_cache):
            # log.debug('USINGCACHE: %s' % cache_id)
            return get_cache(cache_id, self.group_key_cache)
        # log.debug('NOTCACHE: %s' % cache_id)

        # log.debug('CREATING CACHE BASE SALARY BY PERIOD FOR %s (%s)' % (cache_id, self))

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
            normal_base_value = (
                (ef_.get("normal_value", 0.00) + ef_.get("normal_extra", 0.00))
                if ef_.get("id", "") in self.oIds
                else 0
            )
            total["value"] += value
            total["normal_base_value"] += normal_value

            # RGPS: NESSE REGIME A BASE É TODA REMUNERAÇÃO, OU SEJA, EF + CM
            ssc = self.employee.get_socialsecurity_by_validity(
                range=self.payroll.date_range
            )
            regime_social_security = ssc.regime if ssc else None
            if regime_social_security == 1:
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
                value = self._get_value_from_calc(calc, self.FULL_SALARY)
                value = value if fe.evento.tipo == "P" else -value
                base_socialsecurity = calc.base_socialsecurity()
                base_socialsecurity = (
                    base_socialsecurity
                    if fe.evento.tipo == "P"
                    else -base_socialsecurity
                )
            else:
                # log.debug(f'RECALC > {fe}')
                value = self._get_value_from_entry(fe)
                # log.debug(f'RECALC > {fe}  {value} ')
                value = value if fe.evento.tipo == "P" else -value
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
        # log.debug(self.range_13salary)
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


@RunCodeManager.register("gfp-mpto-salaryalaryeffective")
class SalaryEffective(BaseSalary):
    title = "Remuneração de efetivo apenas"
    description = """
        Este cálculo retorna o valor do salário de efetivo, caso o servidor seja efetivo, ou seja,
        apenas o valor da tabela salarial do cargo efetivo do servidor.
    """

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    FILTER_QUERY = 2
    FILTER_BY = 2

    TYPES = ["EF", "AC"]

    def _get_query(self):
        ids = super(SalaryEffective, self)._get_query()
        return [id_ for id_ in ids if id_[0:2] in self.TYPES]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "EF" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é efetivo no período" % (self.employee)
            )

    def normalize_range(self, range):
        ...
        diff_range = self.range_salary - self.range_salary_for()
        normal_range = diff_range + range
        # log.debug(f'{range} {self.range_salary} {self.range_salary_for()} {diff_range} {normal_range}')
        return normal_range if normal_range.is_continuous else range

    @property
    @cached()
    def _base_value(self):
        if not self.object:
            return 0.00, 0

        # _type = self.object[0:2]
        base_value = 0.00
        days = 0
        range = NewDateRange()
        for salarie in self.extract_base_salary_by_type()[self.object]:
            dt = NewDateRange.fromordinals(salarie["range"])
            range += dt
            days += dt.days
            base_value = salarie["value"]
        # log.debug(f'dt days: {days} e base_days: {self.base_days}')
        nrange = self.normalize_range(range)
        return base_value, days, range, nrange

    def quantity(self):
        # log.debug(f'QTD 13: {self.range_13salary}')
        return (
            self._base_value[1] if not self._is_christmas_grat else self.quantity_13()
        )

    def base_value(self):
        # log.debug('>>>>>>>>>>>>>>>>> BASE VALUE: %s' % self.__class__.__name__)
        return float(self._base_value[0])

    def base_socialsecurity(self):
        # log.debug(self.__class__)
        return self.value()

    def event_information(self):
        return "%s" % self.object[2:]

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
            fquantity_days = float(self._base_value[3].days) / float(self.base_days)
            base_value = float(self._base_value[0]) * fquantity_days
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


@RunCodeManager.register("gfp-mpto-salaryrequested")
class SalaryRequested(BaseSalary):
    title = "Remuneração de servidor requisitado"
    description = """
    """

    INCLUDE_EXTRASPAYMENTS = ["VPI", "INCENTIVO-A-DOCENCIA"]
    FILTER_QUERY = 2
    FILTER_BY = 2
    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    TYPES = [
        "AC",
    ]

    def _get_query(self):
        ids = super()._get_query()
        # log.debug(ids)
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


@RunCodeManager.register("gfp-mpto-gratificationfunction")
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
                    # log.debug(f'{self.object[0:2]} {salary[self.object[0:2]]} {dr}')
                pct = salary[self.object[0:2]]["percentage"]
                days += dr.days

        return base_value, days, pct

    def percentage(self):
        return float(self._base_value[2]) or 100.0

    def base_socialsecurity(self):
        base_socialsecurity = super(GratificationFunction, self).base_socialsecurity()
        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        regime_social_security = ssc.regime if ssc else None
        return (
            base_socialsecurity
            if regime_social_security
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


@RunCodeManager.register("gfp-mpto-salarycommissioned")
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
        # log.debug(f'dt days: {days} e base_days: {self.base_days}')
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
            # log.debug(self.payroll.periodo.range)
            for lm in query_advances_maternity:
                # Excluindo os periodos de salario maternidade (INSS - 120 dias)
                range_ += NewDateRange(
                    lm.data_inicio,
                    min(lm.data_fim, lm.data_inicio + relativedelta(days=119)),
                )
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

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = NewDateRange()
        if not set(self.employee_types).intersection(["AC", "EF"]):
            # if self.is_range_maternity_on_13() or not self._is_christmas_grat:
            range_ = self.range_maternity()

        # print(f'>>>> CALCULANDO RSF ERFRS: {self._exclude_ranges_for_range_salary()}')
        return range_ + super(
            SalaryCommissioned, self
        )._exclude_ranges_for_range_salary(range_salary=range_salary)


@RunCodeManager.register("gfp-mpto-maternitypay")
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

        # log.debug('SFE %s' % range_)
        return intersect_range.intersect(range_)

    @property
    # @cached()
    def _base_value(self):
        # log.debug('SFE _base_value %s: %s' % (self.object, self.extract_base_salary_by_type()))
        if not self.object:
            return 0.00, 0

        # _type = self.object[0:2]
        base_value = 0.00
        days = 0
        for salarie in self.extract_base_salary_by_type()[self.object]:
            base_value = salarie["value"] + salarie["gratification"]
            dt = NewDateRange.fromordinals(salarie["range"])
            days += dt.days

        return base_value, days

    def employer_value(self):
        return -self.value()


@RunCodeManager.register("gfp-mpto-gratificationcomissioned")
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
        return range_ + super(
            GratificationCommissioned, self
        )._exclude_ranges_for_range_salary(range_salary=range_salary)


@RunCodeManager.register("gfp-mpto-indemnificationcomissioned")
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


@RunCodeManager.register("gfp-mpto-complementsalarycommissioned")
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

    @property
    @cached()
    def _base_value(self):
        base_value = days = 0.0
        # log.debug('%s' % )
        salaries = self.extract_base_salary_by_period()
        for salary in salaries:
            dr = NewDateRange.fromordinals(salary["range"])
            # log.debug('SAL PERIOD: %s' % salary)
            if (
                ("EF" in salary or "AC" in salary)
                and "CM" in salary
                and salary["CM"]["id"] == self.object
            ):
                ef_ = salary.get("EF", salary.get("AC"))
                cm_ = salary.get("CM")
                # log.debug(f"{dr}: {cm_.get('value')} - {ef_.get('value')} - {ef_.get('extra')}")
                real_value = cm_.get("value") - ef_.get("value") - ef_.get("extra")
                real_value = real_value if real_value >= 0.0 else 0.0
                base_value += real_value
                days += ef_.get("days")

        if self.FULL_SALARY:
            base_value *= (self.base_days / days) if days else 0.0

        return base_value, days

    def normal_value(self):
        return self.value() if self.value() > 0 else 0.0


@RunCodeManager.register("gfp-mpto-complementgratificationcommissioned")
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


@RunCodeManager.register("gfp-mpto-extra")
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
        range = NewDateRange()
        for salarie in self.extract_base_salary_by_type()[self.object]:
            dt = NewDateRange.fromordinals(salarie["range"])
            range += dt
            days += dt.days
            base_value = salarie["extra"]
        # log.debug(f'dt days: {days} e base_days: {self.base_days}')
        nrange = self.normalize_range(range)
        return base_value, days, range, nrange

    def base_socialsecurity(self):
        return self.value()

    def normal_value(self):
        return self.base_salary()["normal_base_extra"]

    # def event_information(self):
    #     return ''


@RunCodeManager.register("gfp-mpto-redutor-teto")
class ReduceSalaryCap(BaseCalculation):
    title = "Redutor de Teto Constitucional"
    description = """
    Usado para todos os servidores. No entanto, o teto é configurado separadamente para
    servidores e membros no menu FOLHA DE PAGAMENTO > Parâmentros > Período.
    O calculo retornará a diferença entre a remuneração recebida e o teto
    """

    FORCE_RECALCULATE_BASE = True
    MEMORY = True

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
        value = base_value - cap_value
        self.set_memory(f"TETO = {cap_value:0.2f}")
        self.set_memory(f"VALOR = {base_value:0.2f} - {cap_value} = {value:0.2f}")
        return value if value > 0 else 0.0

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
                # log.debug('%s:%s' % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    if not id_ == "":
                        exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        # log.debug('RECALCULATE: OBJ %s' % self.object)

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

            # log.debug('SALARIES SUBSTITUION: (%s)%s - %s:%s' % (self.object.posse.quadro.cargo.pk,
            # self.object.posse.quadro.cargo,
            # self.object.data_inicio,
            # self.object.data_fim))
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )
            log.debug(f"SAL SUBS: {salaries_substitution}")
            type_employee = "S"
            if self.employee.is_member:
                type_employee = "M"
            # elif self.employee.is_servidor:
            #     type_employee = 'S'

            for salary_sub in salaries_substitution:
                # log.debug(f'salary_sub: {salary_sub}')
                salaries = self.extract_base_salary_by_period()
                # log.debug(f'SALARIES: {salaries}')
                for salary in salaries:
                    dr = NewDateRange.fromordinals(salary["range"]).intersect(
                        salary_sub[0]
                    )
                    if dr.days > 0:
                        # log.debug(f'>>>> {salary_sub[1].referencia_nivel2d.tipo_gratificacao_membro}, {type_employee}, {salary_sub[1].referencia_nivel2d.tipo_gratificacao}')
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
                            # log.debug(
                            #     'RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s' % (salary, salary_sub,
                            #                                                          NewDateRange.fromordinals(salary['range'])))
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
                            # log.debug('%s BV: %s BG: %s V: %s G: %s' % (dr,
                            #                                             value,
                            #                                             gratification,
                            #                                             salary_sub[1].valor,
                            #                                             salary_sub[1].gratificacao))
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

            set_cache(cache_id, ranges_, self.group_key_cache)

            return ranges_
        else:
            return {}

    @property
    @cached()
    def range_substitution(self):
        range_ = NewDateRange()
        for config in self.extract_salaries_substitution():
            # log.debug('RANGE SUBSTITUION: %s' % NewDateRange.fromordinals(config['range']))
            range_ += NewDateRange.fromordinals(config["range"])
        # log.debug('RECALCULATE ESS: %s' % range_.days)
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
        # log.debug('RECALCULATE: OBJ %s' % self.object)

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

                # log.debug('SALARIES SUBSTITUION: (%s)%s - %s:%s' % (self.object.posse.quadro.cargo.pk,
                # self.object.posse.quadro.cargo,
                # self.object.data_inicio,
                # self.object.data_fim))
                salaries_substitution = EstruturaTabelaSalarial.salarios(
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
                for salary_sub in salaries_substitution:
                    salaries = self.extract_base_salary_by_period()
                    for salary in salaries:
                        # log.debug('RECALCULATE: DRs %s : %s' % (salary, salary_sub[0]))
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
                            # log.debug('%s BV: %s BG: %s V: %s G: %s' % (dr,
                            # value,
                            # gratification,
                            # salary_sub[1].valor,
                            # salary_sub[1].gratificacao))
                            config = {
                                "EF": ef_,
                                "FC": fc_,
                                "CM": cm_,
                                "CMSUB": salary_sub[1],
                                "base_value": value,
                                "base_gratification": gratification,
                            }
                            # log.debug('CONFIG: %s' % config)
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
        # log.debug('RECALCULATE: %s' % range_.days)
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


@RunCodeManager.register("gfp-mpto-cumulation")
class Cumulation(SalaryEffective):
    title = "Cálculo de porcetagem de cumulação para membros"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "qnt", "pct"]

    MULTI_CALCULATE = False
    JOIN_ON_MULTI = False

    @cached()
    def quantity(self):
        # log.debug('PARAMS[QNT]: %s TC: %s' % (self.params.get('qnt', None), self.event.tipo_calculo))
        if self.event:
            if "qnt" in self.params and self.event.tipo_calculo in [3, 5]:
                # log.debug(self.params['qnt'])
                return float(self.params["qnt"] or 0)
            if self.event.quantity_at(self.range_salary.first) is not None:
                return float(self.event.quantity_at(self.range_salary.first))
        return 0

    @cached()
    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""


@RunCodeManager.register("gfp-mpto-substituion-efective")
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


@RunCodeManager.register("gfp-mpto-substituion-complement")
class ComplementSubstitution(BaseSubstitution):
    title = "Complemento de substituição para a remuneração"
    description = """
        Calculo retorna o complemento entre a remuneração do servidor e o salário do cargo a ser substituído!
    """
    JOIN_ON_MULTI = False

    # SE QUISER HABILITAR O validate por substituição existente
    # def validate(self):
    #     super().validate()
    #     if not self.get_substitutions().exists():
    #         raise self.CalculationNotApplicable('Servidor não possui substituições registradas')

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        # log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += (
                config.get("base_value", 0.00) + config.get("base_gratification", 0.00)
            ) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-mpto-substituion-complement-member")
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
                # log.debug('%s:%s' % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        # log.debug('RECALCULATE: OBJ %s' % self.object)

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

            # log.debug('SALARIES SUBSTITUION: (%s)%s - %s:%s' % (self.object.posse.quadro.cargo.pk,
            # self.object.posse.quadro.cargo,
            # self.object.data_inicio,
            # self.object.data_fim))
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )

            for salary_sub in salaries_substitution:
                salaries = self.extract_base_salary_by_period()
                for salary in salaries:
                    # log.debug(
                    # 'RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s' % (salary, salary_sub[0],
                    #                                                      NewDateRange.fromordinals(salary[
                    #                                                          'range'])))
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
                        # log.debug('%s BV: %s BG: %s V: %s G: %s' % (dr,
                        # value,
                        # gratification,
                        # salary_sub[1].valor,
                        # salary_sub[1].gratificacao))
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
                        # log.debug('CONFIG: %s' % config)
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


@RunCodeManager.register("gfp-mpto-substituion-salary")
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
        # log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_value", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-mpto-substituion-gratification")
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
        # log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_gratification", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


class BaseChristmasGratification(BaseSalary):

    title = "Base para os cálculos de 13° Salário"

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
        # log.debug(self.range_13salary)
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
            Q(data_exercicio__gt=range_year.last)
            | (
                ~Q(desligamento=None)
                & Q(desligamento__data_desligamento__lte=range_year.first)
            )
        ).order_by("-data_exercicio")

        for k in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.keys():
            possessions = possessions.exclude(
                servidor__tipo=k,
                quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB[
                    k
                ],
            )

        # log.debug('AdvanceChristmasGratification: %s' % possessions)
        return possessions  # .exclude(quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_BY_JOB)

    def base_socialsecurity(self):
        return self._base_values()[1] * self.factor_quantity()


@RunCodeManager.register("gfp-mpto-13thsalary")
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


@RunCodeManager.register("gfp-mpto-13thsalary-amountpaid")
class ChristmasGratificationAmountPaid(ChristmasGratification):
    FULL_VALUE = False
    FORCE_RECALCULATE_BASE = False

    # TODO Verificar se não tem como configurar para inibir que um evento sobre o qual o calculo
    # incide seja recalculado.
    @cached()
    def base_value(self):
        # log.debug(f'******************************* 2 BASE VALUE {self.__class__} > {self.base_value_query()}')
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

            self.set_memory(
                f"VALOR BASE = {total} + {value} = {total + value} ({fe.evento.numero})"
            )
            # log.debug('>>>> %s >>>> %s : %s + %s = %s' %
            #           (self.event.numero if self.event else 'XXX-XX', fe.evento.numero, total, value, total + value))
            total += value
        base_discounts = self.base_discounts()
        base_value = total - base_discounts
        if base_discounts:
            self.set_memory(
                f"VALOR BASE = {total} - {base_discounts} = {base_value} (DESCONTOS VALOR BASE)"
            )
        base_value = (
            base_value
            if not (self.event and self.event.calculo_invertido)
            else -base_value
        )
        return min(base_value, self.ceiling_base_value)


@RunCodeManager.register("gfp-mpto-13thsalary-gratification")
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
                # log.debug(f'{count} {is_equal} {self._is_christmas_grat}')

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
                    # log.debug(f'{self.object[0:2]} {salary[self.object[0:2]]} DR: {dr} RS: {self.range_salary} RB: {self.range_base}')
                pct = 0
                days += dr.days

        return base_value, days, pct


@RunCodeManager.register("gfp-mpto-13thsalary-salaryrequested")
class ChristmasSalaryRequested(SalaryRequested):
    title = "Remuneração de servidor requisitado no 13º"
    description = """
    """

    def base_value(self):
        # log.debug(self.base_salary_for_type('AC'))
        return self.base_salary_for_type("AC").get("base_value")


@RunCodeManager.register("gfp-mpto-13thsalary-complementsalarycommissioned")
class ChristmasComplementSalaryCommissioned(ComplementSalaryCommissioned):
    title = "Complemento do vencimento de comissionado 13º"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a parte vencimental do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    FULL_SALARY = False


@RunCodeManager.register("gfp-mpto-13thsalary-salaryalaryeffective")
class ChristmasSalaryEffective(BaseSalary):
    title = "Remuneração de efetivo apenas 13º"
    description = """
        Este cálculo retorna o valor do salário de efetivo, caso o servidor seja efetivo, ou seja,
        apenas o valor da tabela salarial do cargo efetivo do servidor.
    """


@RunCodeManager.register("gfp-mpto-13thsalary-gratificationfunction")
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
                    # log.debug(f'{self.object[0:2]} {salary[self.object[0:2]]} {dr}')
                pct = salary[self.object[0:2]]["percentage"]
                days += dr.days

        return base_value, days, pct


@RunCodeManager.register("gfp-mpto-Advance13thsalary")
class AdvanceChristmasGratification(BaseChristmasGratification):

    title = "Adiantamento de 13° Salário"

    def percentage(self):
        return 50.0000

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

        year = (
            self.payroll.periodo.ano
            if self.payroll.periodo.mes < 12
            else self.payroll.periodo.ano + 1
        )
        q1 = Q(contracheque__folha__periodo__ano=year) & Q(
            contracheque__folha__periodo__mes__range=[1, 11]
        )
        q2 = Q(contracheque__folha__periodo__ano=year - 1) & Q(
            contracheque__folha__periodo__mes=12
        )
        query = self.employee.entries.filter(
            (Q(evento=self.event) | Q(evento=self.event.previous_event)) & Q(q1 | q2)
        ).exclude(contracheque__folha=self.payroll)
        if query.exists():
            raise self.CalculationNotApplicable(
                "O servidor já possui adiantamento para o exercício %s" % year
            )

        valid_months = [
            6,
            max(self.employee.pessoa_fisica.data_nascimento.month - 1, 1),
        ]
        if self.payroll.periodo.mes not in valid_months:
            raise self.CalculationNotApplicable(
                "Apenas pode ser requerido no mês de junho ou anterior ao mês de aniversário!"
            )

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-mpto-Advance13thsalary-1382018")
class AdvanceChristmasGratification1382018(AdvanceChristmasGratification):

    title = "Adiantamento de 13° Salário - Ato 138/2018"

    def _query_event(self):
        year = self._year()
        q1 = Q(contracheque__folha__periodo__ano=year) & Q(
            contracheque__folha__periodo__mes__range=[1, 11]
        )
        q2 = Q(contracheque__folha__periodo__ano=year - 1) & Q(
            contracheque__folha__periodo__mes=12
        )
        query = self.employee.entries.filter(
            (Q(evento=self.event) | Q(evento=self.event.previous_event))
            & Q(q1 | q2)
            & Q(status="CT")
        ).exclude(contracheque__folha=self.payroll)
        return query

    def _year(self):
        year = (
            self.payroll.periodo.ano
            if self.payroll.periodo.mes < 12
            else self.payroll.periodo.ano + 1
        )
        return year

    def _old_validate(self):
        self.validate_not_paycheck_pension()
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

        query = self._query_event()
        if query.exists():
            raise self.CalculationNotApplicable(
                "O servidor já possui adiantamento para o exercício %s" % self._year()
            )

    def validate(self):
        self._old_validate()
        valid_months = [
            self.employee.pessoa_fisica.data_nascimento.month,
        ]
        if self.payroll.periodo.mes not in valid_months:
            raise self.CalculationNotApplicable(
                "Apenas pode ser requerido no mês de nascimento!"
            )


@RunCodeManager.register("gfp-mpto-Advance13thsalary-14012020")
class AdvanceChristmasGratification14012020(AdvanceChristmasGratification1382018):

    def _query_event(self):
        year = self._year()
        q1 = Q(contracheque__folha__periodo__ano=year) & Q(
            contracheque__folha__periodo__mes__range=[1, 11]
        )
        q2 = Q(contracheque__folha__periodo__ano=year - 1) & Q(
            contracheque__folha__periodo__mes=12
        )
        query = self.employee.entries.filter(
            Q(evento__in=self.event.relationships, status="CT") & Q(q1 | q2)
        )
        if self.entry:
            query = query.exclude(pk=self.entry.pk)
        return query

    def validate(self):
        self._old_validate()
        dt_nasc = self.employee.pessoa_fisica.data_nascimento.month
        dt_nasc = dt_nasc - 1 if dt_nasc - 1 > 0 else 1
        valid_months = [
            dt_nasc,
        ]
        if self.payroll.periodo.mes not in valid_months:
            raise self.CalculationNotApplicable(
                "Apenas pode ser requerido no mês anterior ao de nascimento!"
            )


@RunCodeManager.register("gfp-mpto-Advance13thnetsalary")
class AdvanceChristmasGratificationNet(BaseCalculation):
    titulo = "Adiantamento de 13° Salário liquido percentual"

    PARAMS_ = ["info", "oIds", "pct"]
    EVALUATE_ON_REFERENCE_PAYROLL = True
    RECALCULATE_BASES = 2
    # FORCE_RECALCULATE_BASE = True

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.reference_payroll:
            raise self.CalculationNotApplicable(
                f"Folha de 13º não encontrada para o ano de {self.payroll.periodo.ano}!"
            )
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

    @property
    def reference_payroll(self):
        # Este calculo apenas deve ser calculado quando a folha de 13º base já existe
        _payroll = Payroll.objects.filter(
            periodo__ano=self.references[0], periodo__mes=13, complement=0
        ).first()
        return _payroll

    @property
    # @cached()
    def focuses_on(self):
        focuses_on = []
        if self.event:
            focuses_on = [
                e.numero for e in self.event.focuses_on_at(self.range_salary.first)
            ]
        return focuses_on

    def discount_paid_other_payroll(self):
        # TODO Verificar se é necessário utilizar o valor realmente pago no lugar
        # do correct_valor
        entries = self.employee.entries.filter(
            evento__in=self.event.relationships,
            status="CT",
            contracheque__pensioner=self.pensioner,
            contracheque__folha__periodo__ano=self.reference_payroll.periodo.ano,
        )
        if self.entry:
            entries = entries.exclude(pk=self.entry.pk)
        value = float(entries.aggregate(total=Sum("correct_valor")).get("total") or 0)
        # log.debug(value)
        return value


@RunCodeManager.register("gfp-mpto-DevolutionAdvance13thsalary")
class DevolutionAdvanceChristmasGratification(BaseCalculation):
    titulo = "Desconto devido adiantamento de 13° Salário"

    MULTI_CALCULATE = False
    JOIN_ON_MULTI = False
    FORCE_RECALCULATE_BASE = False
    RECALCULATE_BASES = 2
    ALL_PAYROLL = True

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
            Q(reference_year=self.payroll.periodo.ano)
            & Q(folha__periodo__ano=self.payroll.periodo.ano)
            & Q(folha__periodo__mes__range=[1, 11])
        )
        return self.employee.entries.filter(
            Q(evento__in=self.event.relationships, status="CT") & Q(q1)
        )

    def discount_paid_other_payroll(self):
        # log.debug('*********discount_paid_other_payroll********')
        if self.ALL_PAYROLL:
            entries = self.exclude_advances()
            if self.entry:
                entries = entries.exclude(pk=self.entry.pk).exclude(
                    paycheck_difference__entries__pk__in=[self.entry.pk]
                )
            return float(
                entries.aggregate(total=Sum("correct_valor")).get("total") or 0
            )
        return 0

    def quantity(self):
        return self.query_advances.count()

    def maximum_quantity(self):
        return 0

    def _get_value_from_entry(self, entry):
        return abs(float(entry.value))

    def _get_value_from_calc(self, calc):
        return calc.value()

    @property
    # @cached()
    def focuses_on(self):
        focuses_on = []
        if self.event:
            focuses_on = [
                e.numero for e in self.event.focuses_on_at(self.range_salary.first)
            ]
        return focuses_on

    def base_value_query(self):
        q_entries = Q(
            evento__numero__in=self.focuses_on,
            contracheque__servidor=self.employee,
            contracheque__pensioner=self.pensioner,
            contracheque__folha__periodo__ano=self.reference_payroll.periodo.ano,
        )
        query = Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

        return query

    def unicode_for_obj(self, obj):
        return "%02d/%04d (%s)" % (obj.reference_month, obj.reference_year, obj.evento)


@RunCodeManager.register("gfp-mpto-DevolutionAdvance13thsalary-ii")
class DevolutionAdvanceChristmasGratificationII(
    DevolutionAdvanceChristmasGratification
):

    @property
    @cached()
    def query_advances(self):
        q1 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano)
            & Q(folha__periodo__mes__range=[1, 11])
        )
        # q2 = Q(Q(folha__periodo__ano=self.payroll.periodo.ano - 1) & Q(folha__periodo__mes=12))

        return self.employee.entries.filter(
            Q(evento__numero__in=self.focuses_on) & Q(q1 | q2)
        )


@RunCodeManager.register("gfp-mpto-rescission-13thsalary")
class ChristmasGratificationRescission(ChristmasGratification):

    title = "13° proporcional"
    # EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {}

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
