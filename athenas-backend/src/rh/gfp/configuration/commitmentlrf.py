# -*- coding: utf-8 -*-
import operator
from functools import reduce

from django.db.models.expressions import Func
from django.db.models import F, Value, TextField, Sum, Q, CharField
from django.db.models.functions import Cast, Concat
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
from standard.models import Choice
from rh.gfp.models import FolhaEvento, Folha
from rh.gfp.configuration.models import ConfigReport
from django.db import connection
from decimal import Decimal
from functools import reduce
from contrib.utils import getLogger
import base64

log = getLogger(__name__)

TYPE_FORMULA = {"PATTERN": 1, "REGISTRATION": 2, "SQL": 3}
GFP_TYPE_EVENT_VALUE = {1: "P", 2: "D", 3: "I"}
GFP_TYPE_EVENT = {"PROVENTO": "P", "DESCONTO": "D", "INFORMATIVO": "I"}
TRANSFER_TYPE = {
    "FINANCIAL": 1,
    "ACCOUNTING": 2,
    "FINANCIAL_TOTALIZER": 3,
    "FINANCIAL_ACCOUNTING": 4,
    "NOT_DISPLAY": 4,
}
GFP_TYPE_REPORT = {"EMPENHOS": 1, "LRF": 2}
GFP_SECTION = {
    "APOSENTADOS": 10,
    "MILITARES": 20,
    "PENSIONISTAS": 30,
    "SERVIDORES_ATIVOS": 40,
    "SENTENCAS_JUDICIAIS": 50,
    "DESPESAS_DE_EXERCICIOS_ANTERIORES": 60,
    "INDENIZACOES_RESTITUICOES_TRABALHISTAS": 65,
    "OUTROS_BENEFICIOS_ASSISTENCIAIS": 70,
    "AUXILIO_ALIMENTACAO": 80,
    "INDENIZACOES_RESTITUICOES": 90,
    "OBRIGACOES_PATRONAIS": 100,
    "RESUMO": 110,
    "FOLHA_PAGAMENTO": 500,
    "ADIANTAMENTO_13_SALARIO": 510,
    "ADICIONAL_FERIAS": 520,
    "OUTROS_VENCIMENTOS": 530,
    "OUTRAS_DESPESAS_VARIAVEIS": 540,
    "REPASSES_FOLHA_MES": 900,
}


class CommitmentLRF(object):

    def __init__(self):
        self.aposentados_possession = ["MAP", "SAP", "BFP"]
        self.servidores_possession = [
            "MEL",
            "MBR",
            "EFE",
            "ECM",
            "EFC",
            "CMS",
            "RCM",
            "EXT",
            " REQ",
        ]

    def sum_employer_obligation(self, section, employer_obligation, value):
        """Este método realiza a soma dos valores das obrigaçãoes patronais
        Args:
            section (int): Seção
            employer_obligation (decimal): Obrigações patronais
            value: (decimal) : Valor

        Returns:
            Decimal: Valor da obrigaçãoes Patronais
        """

        if (
            section
            == Choice.objects.get(
                name="GFP_SECTION", value=GFP_SECTION["OBRIGACOES_PATRONAIS"]
            ).value
        ):
            return employer_obligation + value
        else:
            return employer_obligation

    def sum_event(self, config, result, section, nature, subelement, creditor, value):
        """Este método realiza a soma dos valores dos eventos da folha
        Args:
            config (object): Configuração
            result (dict): dict com os resultado dos eventos
            section (int) : Seção
            nature (str): Natueza do evento
            subelement (str): Subelemento
            creditor (str): cod. do credor
            value (decimal): valor
            option (str): opcao
            config_ids(list): config_ids
            subelementos(list): subelementos
        Returns:
            Dict: dict com os resultado dos eventos
        """
        if result.get(section):
            if result[section].get(config.type_event):
                result[section][config.type_event].append(
                    {
                        "type": config.type_event,
                        "nature": nature,
                        "subelem": subelement,
                        "text": config.text,
                        "creditor": creditor,
                        "value": value,
                    }
                )
            else:
                result[section].update(
                    {
                        config.type_event: [
                            {
                                "type": config.type_event,
                                "nature": nature,
                                "subelem": subelement,
                                "text": config.text,
                                "creditor": creditor,
                                "value": value,
                            }
                        ],
                    }
                )

            result[section]["amount"][config.type_event] = (
                result[section]["amount"][config.type_event] + value
            )
            result[section]["count"][config.type_event] = (
                result[section]["count"][config.type_event] + 1
            )
            desconto = (
                result[section]["amount"][GFP_TYPE_EVENT["PROVENTO"]]
                - result[section]["amount"][GFP_TYPE_EVENT["DESCONTO"]]
            )
            result[section]["amount"]["liquid"] = desconto if desconto > 0 else 0

            return result
        else:
            result.update(
                {
                    section: {
                        config.type_event: [
                            {
                                "type": config.type_event,
                                "nature": nature,
                                "subelem": subelement,
                                "text": config.text,
                                "creditor": creditor,
                                "value": value,
                            }
                        ],
                    },
                }
            )
            result[section].update(
                {
                    "amount": {
                        GFP_TYPE_EVENT["PROVENTO"]: 0,
                        GFP_TYPE_EVENT["DESCONTO"]: 0,
                        "liquid": 0,
                    }
                }
            )
            result[section].update(
                {
                    "count": {
                        GFP_TYPE_EVENT["PROVENTO"]: 0,
                        GFP_TYPE_EVENT["DESCONTO"]: 0,
                    }
                }
            )
            result[section]["amount"][config.type_event] = (
                result[section]["amount"][config.type_event] + value
            )
            result[section]["count"][config.type_event] = (
                result[section]["count"][config.type_event] + 1
            )
            result[section]["amount"]["liquid"] = (
                result[section]["amount"][GFP_TYPE_EVENT["PROVENTO"]]
                - result[section]["amount"][GFP_TYPE_EVENT["DESCONTO"]]
            )
            result[section].update(
                {
                    "category": Choice.objects.get(
                        name="GFP_SECTION", value=section
                    ).description
                }
            )
            return result

    def create_empty_table(self, result):
        """Este método criar objects(vazio) para igualar a quantidade de linhas da tabela
        Args:
            result (dict): dict com os resultado dos eventos
        Returns:
            Dict: dict com os resultado dos eventos
        """
        for event in result:
            count_icome = result[event]["count"][GFP_TYPE_EVENT["PROVENTO"]]
            count_discount = result[event]["count"][GFP_TYPE_EVENT["DESCONTO"]]
            change_event = (
                GFP_TYPE_EVENT["DESCONTO"]
                if count_icome > count_discount
                else GFP_TYPE_EVENT["PROVENTO"]
            )
            bigger = count_icome if count_icome > count_discount else count_discount
            smaller = count_icome if count_icome < count_discount else count_discount
            diff = bigger - smaller

            for value in range(diff):
                if result[event].get(change_event):
                    result[event][change_event].append({"value": None})
                else:
                    result[event].update({change_event: [{"value": None}]})

        return result

    def sum_totais(self, config, list_funds_total, value):
        """Este método calcula a soma dos totais de cada evento
        Args:
            config (object): Configuração
            list_funds_total(dict): Dicionário com os valores das somas
            value (decimal): valor
        Returns:
            Dict: Dicionário com os valores das somas
        """
        if config.type_event == GFP_TYPE_EVENT["DESCONTO"]:
            if list_funds_total.get("total_discounts"):
                list_funds_total["total_discounts"] = (
                    list_funds_total["total_discounts"] + value
                )
            else:
                list_funds_total.update({"total_discounts": value})
        else:
            if list_funds_total.get("total_earnings_employer"):
                list_funds_total["total_earnings_employer"] = (
                    list_funds_total["total_earnings_employer"] + value
                )
            else:
                list_funds_total.update({"total_earnings_employer": value})

        return list_funds_total

    def get_value_event(
        self,
        config,
        list_type_possession,
        sheet,
        option=None,
        status=None,
        elementos=None,
    ):
        """Este método calcula o valor total de cada configuração
        Returns:
            Decimal: valor do final da configuração(evento)
        """

        if config.type_formula == TYPE_FORMULA["PATTERN"]:
            if config.formula:
                return Decimal(config.formula)
            else:
                return 0
        elif config.type_formula == TYPE_FORMULA["REGISTRATION"]:
            params = {
                "evento__in": config.include_funds.all(),
                "servidor__in": config.include_registration.all(),
                "servidor__lotacoes__in": config.include_workplaces.all(),
                "servidor__servidor_lotacao__movimentacao_posse__quadro__cargo__in": config.include_job_positions.all(),
                "folha__pk": sheet.pk,
            }

            if status:
                params.update({"status": status})

            diference = []
            if option in ["1", "2"]:
                logic = list(
                    set(list_type_possession).intersection(
                        set(self.servidores_possession)
                    )
                )
                diference = logic
            elif option == "99":
                logic = list(
                    set(list_type_possession).intersection(
                        set(self.aposentados_possession)
                    )
                )
                diference = logic
            value = (
                FolhaEvento.objects.filter(
                    Q(**self.params_query_set(params, list_type_possession, config))
                )
                .filter(self.filter_option_mass_segregation(option))
                .exclude(evento__in=list(config.exclude_funds.all()))
                .exclude(servidor__in=config.exclude_registration.all())
                .exclude(servidor__lotacoes__in=config.exclude_workplaces.all())
                .exclude(evento__tipo="I")
                .exclude(
                    servidor__servidor_lotacao__movimentacao_posse__quadro__cargo__in=config.exclude_job_positions.all()
                )
                .exclude(servidor__type_by_possession__in=diference)
                .distinct()
                .aggregate(total_value=Sum("correct_valor"))
            )

            return value["total_value"] if value["total_value"] else 0
        else:
            if config.formula:
                try:
                    with connection.cursor() as cursor:
                        repls = (
                            ("%FOLHA%", str(sheet.pk)),
                            ("%MASS_SEGREGATION%", self.set_option_value(option)),
                            ("DELETE", ""),
                            ("UPDATE", ""),
                            ("DROP", ""),
                        )
                        sql = reduce(
                            lambda a, kv: a.replace(*kv), repls, config.formula
                        )
                        cursor.execute(sql)
                        value = cursor.fetchone()[0]
                except Exception as err:
                    raise Exception("Instrução sql inválida")

                if value:
                    return self.check_possession(value, option, config, elementos)
                else:
                    return 0
            else:
                return 0

    def set_option_value(self, option):
        """retorna o valor da tag conforme a segregação de massa"""
        if int(option) in [1, 2]:
            return str(f"IN ({option})")
        else:
            return str(f"NOT IN ({9999})")

    def filter_option_mass_segregation(self, option):
        """Este método criar um filtro de acordo com a segregação de massa
        Returns:
            Q: Object
        """
        option = int(option)
        filter_options = Q()
        if option > 0:
            if option in [1, 2]:
                filter_options &= Q(
                    **{"servidor__socialsecurities__mass_segregation_plan": option}
                )

        return filter_options

    def params_query_set(self, params, list_type_possession, config):
        args = {}
        if list_type_possession:
            if list_type_possession[0]:
                args.update({"servidor__type_by_possession__in": list_type_possession})
        if not config.include_funds.all():
            args.update({"evento__tipo": config.type_event})

        for param in params:
            if params[param]:
                args.update({param: params[param]})

        return args

    def sum_payroll_transfer(self, payroll_transfer, config, value):
        """Este método calcula o valores dos repasses da folha
        Returns:
            Dict: Dicionário com os valores das somas
        """
        if config.creditor:
            if payroll_transfer.get(str(config.creditor) + config.text):
                payroll_transfer[str(config.creditor) + config.text].update(
                    {
                        "creditor": config.creditor,
                        "description": config.text,
                        "value": payroll_transfer[str(config.creditor) + config.text][
                            "value"
                        ]
                        + value,
                    }
                )
            else:
                payroll_transfer.update(
                    {
                        str(config.creditor)
                        + config.text: {
                            "creditor": config.creditor,
                            "description": config.text,
                            "value": value,
                        }
                    }
                )
            payroll_transfer["value_total"] = payroll_transfer["value_total"] + value

        return payroll_transfer

    def set_value(self, config, value):
        """
        Setar o valor para 0 caso a config seja totalizador
        Returns:
            int: valor
        """
        if not config.subelement and config.type_event == GFP_TYPE_EVENT["PROVENTO"]:
            return 0

        return value

    def nature_totalizer(self, result, section, nature, type_event, value):
        if type_event == GFP_TYPE_EVENT["PROVENTO"]:
            for line in result[section][type_event]:
                if not line["subelem"]:
                    if line["nature"] == nature:
                        line["value"] = line["value"] + value
        return result

    def calc_commitment_report(self, period, type_sheet, option, subtitle):
        """Este método realizar o cálculo do relatório de empenhos
        :Returns
            Dict: Dicionário com os valores do relatório de empenhos
        """
        result = {}
        payroll_transfer = {"value_total": 0}
        employer_obligation = 0
        list_funds_total = {"total_earnings_employer": 0, "total_discounts": 0}
        aposentados_possession = ["MAP", "SAP", "BFP"]
        servidores_possession = [
            "MEL",
            "MBR",
            "EFE",
            "ECM",
            "EFC",
            "CMS",
            "RCM",
            "EXT",
            " REQ",
        ]

        split_into_array = Func(
            F("type_by_possession"),
            Value(","),
            function="regexp_split_to_array",
            output=ArrayField(TextField()),
        )

        section_element = Cast(
            Concat(F("section"), Value("-"), F("nature"), Value("-"), F("subelement")),
            output_field=CharField(),
        )

        sheet = Folha.objects.get(pk=type_sheet)
        configs = (
            ConfigReport.objects.prefetch_related(
                "include_funds",
                "exclude_funds",
                "include_registration",
                "exclude_registration",
                "include_workplaces",
                "exclude_workplaces",
                "include_job_positions",
                "exclude_job_positions",
            )
            .annotate(
                splited_possession=split_into_array, section_element=section_element
            )
            .filter(type_report=GFP_TYPE_REPORT["EMPENHOS"])
        )

        if option in ["1", "2"]:
            elementos = configs.filter(
                self.icontains_with_in("splited_possession", servidores_possession),
            ).values_list("section_element", flat=True)
        elif option == "99":
            elementos = configs.filter(
                self.icontains_with_in("splited_possession", aposentados_possession)
            ).values_list("section_element", flat=True)
        else:
            elementos = []
        for config in configs:
            section = config.section
            config.type_event = GFP_TYPE_EVENT_VALUE[config.type_event]
            creditor = config.creditor if config.creditor != None else ""
            subelement = config.subelement if config.subelement != None else ""
            nature = config.nature if config.nature != None else ""
            list_type_possession = config.type_by_possession.split(",")
            status = "CT"

            value = self.get_value_event(
                config, list_type_possession, sheet, option, status, elementos
            )
            value = self.set_value(config, value)
            employer_obligation = self.sum_employer_obligation(
                config.section, employer_obligation, value
            )
            self.sum_event(config, result, section, nature, subelement, creditor, value)
            self.nature_totalizer(result, section, nature, config.type_event, value)
            self.sum_payroll_transfer(payroll_transfer, config, value)
            self.sum_totais(config, list_funds_total, value)

        self.create_empty_table(result)
        list_funds_total.update(
            {
                "liquid": list_funds_total["total_earnings_employer"]
                - list_funds_total["total_discounts"],
                "total_earnings": list_funds_total["total_earnings_employer"]
                - employer_obligation,
            }
        )

        with open("static/images/logo-report-mpmt.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        context_data = {
            "values": [result[item] for item in result],
            "value_transfer_total": payroll_transfer.pop("value_total"),
            "values_transfer": [
                payroll_transfer[transfer] for transfer in payroll_transfer
            ],
            "value_total": list_funds_total,
            "period": period,
            "number_sheet": period.split("/")[0],
            "hour": datetime.now().strftime("%H:%M"),
            "date": datetime.now().strftime("%d/%m/%Y"),
            "logo_mpmt": encoded_string.decode("utf-8"),
            "subtitle": subtitle,
            "payroll": str(sheet).title(),
        }

        return context_data

    def sum_lrf(self, config, result, section, value):
        """Este método realiza a soma dos valores dos eventos da folha LRF
        Args:
            config (object): Configuração
            result (dict): dict com os resultado dos eventos
            section (int) : Seção
            value (decimal): valor

        Returns:
            Dict: dict com os resultado dos eventos
        """
        if result.get(section):

            result[section].append(
                {
                    "totalizer": config.text,
                    "value": value,
                }
            )

            return result
        else:
            result.update(
                {
                    section: [
                        {
                            "totalizer": Choice.objects.get(
                                name="GFP_SECTION", value=section
                            ).description,
                            "value": None,
                        }
                    ],
                }
            )
            result[section].append(
                {
                    "totalizer": config.text,
                    "value": value,
                }
            )

            return result

    def calc_lrf_report(self, period, type_sheet, option, subtitle):
        """Este método realizar o cálculo do relatório de LRF
        :Returns
            Dict: Dicionário com os valores do relatório de LRF
        """
        result = {}
        sheet = Folha.objects.get(pk=type_sheet)
        configs = ConfigReport.objects.prefetch_related(
            "include_funds",
            "exclude_funds",
            "include_registration",
            "exclude_registration",
            "include_workplaces",
            "exclude_workplaces",
            "include_job_positions",
            "exclude_job_positions",
        ).filter(type_report=GFP_TYPE_REPORT["LRF"])
        for config in configs:
            list_type_possession = config.type_by_possession.split(",")
            config.type_event = GFP_TYPE_EVENT_VALUE[config.type_event]
            value = self.get_value_event(config, list_type_possession, sheet)
            result = self.sum_lrf(config, result, config.section, value)

        with open("static/images/logo-report-mpmt.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        context_data = {
            "values": [result[item] for item in result],
            "period": period,
            "number_sheet": period.split("/")[0],
            "hour": datetime.now().strftime("%H:%M"),
            "date": datetime.now().strftime("%d/%m/%Y"),
            "logo_mpmt": encoded_string.decode("utf-8"),
            "payroll": str(sheet).title(),
        }

        return context_data

    @staticmethod
    def icontains_with_in(lookup, values):
        """
        Function that makes an icontains over a list of values

        Common cases: Make a filter to a ArrayField

        :param str lookup: Field to look at
        :param values: Values to iterate over
        """

        return reduce(
            operator.or_, [Q(**{f"{lookup}__icontains": value}) for value in values]
        )

    def check_possession(self, value, option=None, config=None, elementos=None):
        if not option:
            return value
        if option in ["1", "2"] and config.section_element in elementos:
            return 0
        elif option == "99" and config.section_element in elementos:
            return 0
        return value
