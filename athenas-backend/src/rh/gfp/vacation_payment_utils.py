from calendar import monthrange
import datetime
import decimal

from contrib.utils import getLogger
from dateutil import relativedelta
from django.db.models import Q

from contrib.daterange import NewDateRange
from rh.gfp.models import EstruturaTabelaSalarial, FolhaEvento
from standard.models import Item


log = getLogger(__name__)


def extract_base_salary_for_cms(employee, initial_period_date, final_period_date):
    """
    Função que retorna um dicionário com os períodos e salários atuais para
    cada provimento no periodo calculado para comissionados
    """
    salaries = {}
    range_ = NewDateRange(initial_period_date, final_period_date)
    for p in employee.get_posses_ativas(initial_period_date, final_period_date):
        if (
            p.quadro.cargo.tipo_lei_cargo
            in [
                "CM",
            ]
            and not p.servidor.tipo == "M"
        ):
            salaries_ = EstruturaTabelaSalarial.salarios(p.quadro.cargo)
            for salary in salaries_:
                idx = f'{p.quadro.cargo.tipo_lei_cargo}{salary[1].sigla_cache}:{p.data_exercicio if p.data_exercicio else ""}>{p.data_desligamento if p.data_desligamento else ""}'
                if idx not in salaries:
                    salaries[idx] = {}
                value = salary[1].valor
                gratification = salary[1].gratificacao
                period_intersect = range_.intersect(
                    NewDateRange(p.data_exercicio, p.data_desligamento)
                )
                pos_end_date = (
                    relativedelta.relativedelta(
                        period_intersect.end_date, period_intersect.start_date
                    ).months
                    if not relativedelta.relativedelta(
                        period_intersect.end_date, period_intersect.start_date
                    ).days
                    else relativedelta.relativedelta(
                        period_intersect.end_date, period_intersect.start_date
                    ).months
                    + 1
                )
                salaries[idx] = {
                    "range": period_intersect,
                    "first_date": period_intersect.start_date,
                    "end_date": period_intersect.end_date,
                    "months_in_period": pos_end_date,
                    "salary": salary[1],
                    "type": p.quadro.cargo.tipo_lei_cargo,
                    "value": value,
                    "gratification": gratification,
                    "total": gratification + value,
                }
    return salaries


def get_salary_atualized(employee):
    """
    Retorna a soma dos salários e gratificações atualizados para cada provimento do servidor.

    :param employee: objeto que representa um servidor.
    :type employee: object
    :return: soma dos salários e gratificações do servidor para os cargos atuais.
    :rtype: float
    """
    today = datetime.datetime.today().date()
    total = 0
    for p in employee.get_posses_ativas(today, today):
        if not employee.is_member:
            for prog in p.progressoes.exclude(
                Q(data_inicio_vigencia__gt=today)
                | (~Q(data_fim_vigencia=None) & Q(data_fim_vigencia__lt=today))
            ):
                salaries_ = EstruturaTabelaSalarial.salarios(
                    p.quadro.cargo, today, today, prog.referencia_nivel2d
                )
                for salary in salaries_:
                    value = salary[1].valor
                    gratification = salary[1].gratificacao
                    total = total + value + gratification
        else:
            salaries_ = EstruturaTabelaSalarial.salarios(p.quadro.cargo)
            for salary in salaries_:
                value = salary[1].valor_membro
                gratification = salary[1].gratificacao_membro
                total = total + value + gratification
    return total


def get_paychecks(
    employee, number_of_event, start_date_acquisition=None, end_date_acquisition=None
):
    """
    Retorna uma lista ordenada de folhas de pagamento correspondentes ao
    servidor e eventos especificados.

    :param employee: (Servidor) objeto que representa um servidor público.
    :param number_of_event: (int or list[int]) número do evento ou lista de
        números de eventos desejados.
    :param start_date_acquisition: (Date) data de início do período desejado.
    :param end_date_acquisition: (Date) data de fim do período desejado.
    :return: lista ordenada de folhas de pagamento correspondentes aos eventos e
        servidor especificados.
    :rtype: QuerySet
    """
    if isinstance(number_of_event, list):
        folha_eventos = FolhaEvento.objects.filter(
            servidor=employee,
            evento__numero__in=number_of_event,
            status__in=["CT", "CE", "BS"],
        ).order_by("-folha")
    else:
        folha_eventos = FolhaEvento.objects.filter(
            servidor=employee,
            evento__numero=number_of_event,
            status__in=["CT", "CE", "BS"],
        ).order_by("-folha")
    if start_date_acquisition and end_date_acquisition:
        folha_eventos = folha_eventos.filter(
            (
                Q(
                    folha__periodo__mes__gte=start_date_acquisition.month,
                    folha__periodo__ano=start_date_acquisition.year,
                )
                | Q(folha__periodo__ano__gt=start_date_acquisition.year)
            )
            & (
                Q(
                    folha__periodo__mes__lte=end_date_acquisition.month,
                    folha__periodo__ano=end_date_acquisition.year,
                )
                | Q(folha__periodo__ano__lt=end_date_acquisition.year)
            )
        )

    return folha_eventos


def calc_from_period(employee, payroll, event, params):
    """
    Realiza o cálculo de folha a partir de um evento e folha específicos.
    """
    classcode = event.calculation_at(payroll.date_range.first)
    cls = classcode.cls

    calc = cls(employee, payroll, event, params=params)
    return calc


def gratifications_to_check(key):
    """
    Retorna números de gratificações que devem entrar no
    cálculo de pagamento de abonos e gratificação de férias
    """
    try:
        item = Item.objects.get(key=key)

        return item.value.split(",")
    except Exception as error:
        msg = f"Não há configurações das Gratificações em Painel de Controle > Configurações > Item de configuração > {key}."
        raise Exception(msg) from error


def calculate_average_value_of_months(values, diff_months):
    """
    Calcula a média de salário, pelo número de meses passado como parâmetro;

    :param values: (dict) Dicionário contendo os valores para cálculo.
    :param diff_months: (int) O número de meses de diferença entre as datas de início e término.

    :return: O valor médio calculado.
    :rtype: decimal.Decimal
    """
    try:
        total = decimal.Decimal(0)
        for value in values.values():
            if (
                value["first_date"].day == 1
                and value["end_date"].month
                != (value["end_date"] + relativedelta.relativedelta(days=1)).month
                and value["months_in_period"] == 12
            ):
                return decimal.Decimal(value["total"])

            qnt_days_range_init = monthrange(
                value["first_date"].year, value["first_date"].month
            )[1]
            qnt_days_range_end = monthrange(
                value["end_date"].year, value["end_date"].month
            )[1]

            if len(values.values()) > 1 and value["first_date"].day != 1:
                if value["first_date"].month != value["end_date"].month:
                    for range_value in values.values():
                        if (
                            range_value["range"].last.month
                            == value["range"].first.month
                        ):
                            day_conference = monthrange(
                                range_value["range"].last.year,
                                range_value["range"].last.month,
                            )[1]
                            date_conference = datetime.datetime(
                                range_value["range"].last.year,
                                range_value["range"].last.month,
                                1,
                            ).date()
                            date_range_conference = NewDateRange(
                                date_conference, range_value["range"].last
                            )
                            qnt_days_range_init = monthrange(
                                value["range"].first.year, value["range"].first.month
                            )[1]
                            end_date = datetime.datetime(
                                value["range"].first.year,
                                value["range"].first.month,
                                qnt_days_range_init,
                            ).date()
                            date_range_ref = NewDateRange(
                                value["range"].first, end_date
                            )

                            if (
                                date_range_ref.days + date_range_conference.days
                                == day_conference
                            ) or (
                                date_range_ref.days + date_range_conference.days
                                > day_conference / 2
                            ):
                                if (
                                    value["range"].last.year
                                    == value["range"].first.year + 1
                                ):
                                    base_month = value["months_in_period"]
                                else:
                                    base_month = (
                                        value["range"].last.month
                                        - value["range"].first.month
                                        + 1
                                    )
                            else:
                                base_month = (
                                    value["range"].last.month
                                    - value["range"].first.month
                                )
                                break
                        else:
                            if (
                                value["range"].last.year
                                == value["range"].first.year + 1
                            ):
                                if value["range"].last.day > value["range"].first.day:
                                    base_month = value["months_in_period"] - 1
                                    break
                                else:
                                    base_month = value["months_in_period"]
                                    break
                            else:
                                base_month = value["months_in_period"]
                                break
                else:
                    if value["range"].last.year == value["range"].first.year + 1:
                        base_month = 12
                    # regra para quando tiver mais de um no mesmo mês
                    else:
                        base_month = (
                            value["range"].last.month - value["range"].first.month
                        )
            elif (
                len(values.values()) > 1
                and value["range"].last.day < qnt_days_range_end
            ):
                if (
                    value["range"].last.year == value["range"].first.year + 1
                    and value["range"].days > 350
                ):
                    base_month = 12
                else:
                    base_month = value["range"].last.month - value["range"].first.month
            elif value["range"].first.day != 1 and value["range"].first.day > round(
                qnt_days_range_init / 2
            ):
                if value["range"].last.year == value["range"].first.year + 1:
                    base_month = 12
                else:
                    base_month = (
                        value["range"].last.month - value["range"].first.month + 1
                    )
            else:
                if value["range"].last.year == value["range"].first.year + 1:
                    base_month = value["months_in_period"]
                else:
                    base_month = (
                        value["range"].last.month - value["range"].first.month + 1
                    )
            if base_month < 0:
                base_month = base_month * -1
            total += decimal.Decimal(
                value["total"] * round(decimal.Decimal(base_month), 8)
            )
        return total / diff_months
    except Exception as e:
        log.error(e)
