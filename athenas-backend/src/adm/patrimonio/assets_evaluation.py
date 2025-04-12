# -*- coding: utf-8 -*-
import csv
import locale
import os
from datetime import date, datetime

import django
from django.db.models import Max, Q

from adm.patrimonio.models import (
    Avaliacao,
    AvaliacaoItem,
    Especie,
    GrupoEspecie,
    Patrimonio,
)
from contrib.middleware import set_current_user

os.environ.update(DJANGO_SETTINGS_MODULE="app.settings")
django.setup()


# Estado de Conservação (IPCA)
EC_IPCA_MAP = {
    1: 10.000000,  # Novo
    2: 8.000000,  # Bom
    3: 5.000000,  # Regular
    4: 2.000000,  # Inservivel
}

# Estado de Conservação (Descrição)
EC_DESCRIPTION_MAP = {1: "Novo", 2: "Bom", 3: "Regular", 4: "Inservivel"}


# Período de Utilização (Anos)
PU_MAP = {
    0: 0.000000,
    1: 1.000000,
    2: 2.000000,
    3: 3.000000,
    4: 4.000000,
    5: 5.000000,
    6: 6.000000,
    7: 7.000000,
    8: 8.000000,
    9: 9.000000,
}

# Período de Utilização (Description)
PU_DESCRIPTION_MAP = {
    0: "<= 1 ano",
    1: "1 ano",
    2: "2 anos",
    3: "3 anos",
    4: "4 anos",
    5: "5 anos",
    6: "6 anos",
    7: "7 anos",
    8: "8 anos",
    9: "9 anos",
}

# Período de Vida Útil Futura (Anos)
PVUF_MAP = {
    0: 4.000000,
    1: 4.000000,
    2: 4.000000,
    3: 4.000000,
    4: 4.000000,
    5: 5.000000,
    6: 6.000000,
    7: 7.000000,
    8: 8.000000,
    9: 9.000000,
}

# Período de Vida Útil Futura (Descrição)
PVUF_DESCRIPTION_MAP = {
    0: "<= 1 ano",
    1: "1 ano",
    2: "2 anos",
    3: "3 anos",
    4: "4 anos",
    5: "5 anos",
    6: "6 anos",
    7: "7 anos",
    8: "8 anos",
    9: "9 anos",
    10: ">= 10 anos",
}

# Novo período de Vida Útil Futura (Anos)
NPVUF_MAP = {
    3: {
        2: {
            "min": 2.0000000,
            "max": 2.0000000,
        },
        3: {
            "min": 1.0000000,
            "max": 1.0000000,
        },
    },
    4: {
        2: {
            "min": 2.0000000,
            "max": 2.0000000,
        },
        3: {
            "min": 1.0000000,
            "max": 1.0000000,
        },
    },
    5: {
        2: {
            "min": 3.0000000,
            "max": 3.0000000,
        },
        3: {
            "min": 1.0000000,
            "max": 2.0000000,
        },
    },
    10: {
        2: {
            "min": 6.0000000,
            "max": 8.0000000,
        },
        3: {
            "min": 1.0000000,
            "max": 5.0000000,
        },
    },
    20: {
        2: {
            "min": 11.0000000,
            "max": 15.0000000,
        },
        3: {
            "min": 1.0000000,
            "max": 10.0000000,
        },
    },
}

# Retornar o valor de mercado segundo a tabela FIPE
FIPE_VALUES = {
    5550: 30656.000000,
    10193: 24871.000000,
    9847: 24776.000000,
    12867: 24776.000000,  # Verificar valor
    10099: 24776.000000,
    809: 24776.000000,
    3744: 24776.000000,
    15564: 24776.000000,
    9862: 72689.000000,
    15514: 23917.000000,
    12934: 23917.000000,
    12935: 23917.000000,
    9718: 62458.000000,
    6974: 30656.000000,
    11515: 30656.000000,
    2091: 20080.000000,
    798: 20349.000000,
    3112: 20349.000000,
    5519: 20349.000000,
    15965: 20349.000000,
    # 10741: ?,
    # 12706: ?,
    # 16282: ?,
}

# Intervalo que compreende os patrimônios a serem avaliados
START = datetime(1989, 1, 1)
END = datetime(2012, 12, 31, 23, 59, 59)

# Espécies sem ItemAvaliacao
SPECIES_NO_EVALUATION_ITEM = []

# Espécies com mais de um ItemAvaliacao
SPECIES_MORE_THAN_ONE_EVALUATION_ITEM = []

# Espécie com vida útil divergente da portaria conjunta SECAD/SEFAZ/CGE
NOT_FOUND_VUIB_SPECIES = []

# 1 - Bens permanentes inservíveis em processo de baixa
UNSERVICEABLES_IN_WRITE_OFF_PROCESS = [
    "0423",
    "0565",
    "0567",
    "0571",
    "0697",
    "0806",
    1287,
    1404,
    1666,
    1771,
    1776,
    1778,
    2743,
    2757,
    2773,
    2784,
    3039,
    3106,
    3136,
    3150,
    3287,
    3497,
    3558,
    3593,
    3645,
    3893,
    3962,
    4144,
    4896,
    4947,
    5135,
    5138,
    5209,
    5230,
    7548,
    7551,
    7690,
    7743,
    7799,
    7880,
    7883,
    7886,
    7940,
    7950,
    7964,
    7978,
    8043,
    8137,
    8385,
    8430,
    8590,
    8611,
    8623,
    8628,
    8691,
    8704,
    8742,
    8759,
    8829,
    8942,
    9023,
    9035,
    9058,
    9059,
    9060,
    9076,
    9096,
    9097,
    9149,
    9172,
    9211,
    9225,
    9241,
    9245,
    9252,
    9262,
    9286,
    9306,
    9309,
    9359,
    9362,
    9379,
    9385,
    9393,
    9409,
    9413,
    9433,
    9510,
    9547,
    9670,
    9678,
    9689,
    9700,
    9785,
    9786,
    9788,
    9861,
    9995,
    10014,
    10021,
    10022,
    10024,
    10025,
    10027,
    10034,
    10084,
    10146,
    10244,
    10264,
    10284,
    10316,
    10318,
    10322,
    10325,
    10330,
    10339,
    10342,
    10360,
    10726,
    10745,
    10753,
    10778,
    10782,
    10788,
    10790,
    10791,
    10799,
    10801,
    10803,
    10804,
    10814,
    10816,
    10828,
    10829,
    10833,
    10838,
    10853,
    10862,
    10869,
    10870,
    10873,
    10875,
    10876,
    10880,
    10882,
    10889,
    10904,
    10905,
    10908,
    10916,
    10923,
    10924,
    10927,
    10935,
    10936,
    10940,
    10943,
    10946,
    10952,
    10955,
    10957,
    10974,
    10995,
    11018,
    11025,
    11031,
    11038,
    11039,
    11040,
    11045,
    11055,
    11057,
    11058,
    11072,
    11083,
    11084,
    11088,
    11108,
    11129,
    11136,
    11138,
    11178,
    11179,
    11182,
    11192,
    11198,
    11202,
    11203,
    11204,
    11205,
    11209,
    11221,
    11222,
    11223,
    11227,
    11270,
    11271,
    11274,
    11290,
    11292,
    11293,
    11296,
    11308,
    11313,
    11314,
    11320,
    11325,
    11331,
    11333,
    11394,
    11409,
    11413,
    11414,
    11418,
    11434,
    11435,
    11440,
    11442,
    11453,
    11458,
    11459,
    11460,
    11462,
    11468,
    11469,
    11524,
    11526,
    11528,
    11531,
    11532,
    11545,
    11550,
    11565,
    11572,
    11576,
    11582,
    11586,
    11599,
    11602,
    11605,
    11611,
    11614,
    11622,
    11630,
    11641,
    11647,
    11672,
    11697,
    11703,
    11729,
    11750,
    11756,
    11757,
    11759,
    11767,
    11774,
    11789,
    11827,
    11844,
    11864,
    11877,
    11889,
    11890,
    11897,
    11971,
    11986,
    11993,
    11996,
    12000,
    12007,
    12011,
    12019,
    12648,
    12729,
    12742,
    12747,
    12752,
    12760,
    12766,
    12774,
    12775,
    12787,
    12788,
    12791,
    12794,
    13002,
    13003,
    13005,
    13008,
    13009,
    13011,
    13013,
    13027,
    13031,
    13034,
    13045,
    13048,
    13051,
    13056,
    13057,
    13060,
    13062,
    13093,
    13094,
    13151,
    13180,
    13198,
    13200,
    13208,
    13213,
    13224,
    13229,
    13231,
    13232,
    13260,
    13261,
    13293,
    13317,
    13375,
    13418,
    13550,
    13551,
    13726,
    13949,
    13969,
    13972,
    13994,
    14012,
    14050,
    14070,
    14143,
    14144,
    14145,
    14147,
    14154,
    14165,
    14173,
    14217,
    14230,
    14249,
    14259,
    14265,
    14272,
    14281,
    14285,
    14494,
    14500,
    14515,
    14533,
    14617,
    14724,
    14744,
    14768,
    14770,
    14771,
    14773,
    14789,
    14795,
    14798,
    14801,
    14803,
    14804,
    14805,
    14808,
    14812,
    14813,
    14814,
    14817,
    14822,
    14828,
    14834,
    14839,
    14867,
    14869,
    14875,
    15252,
    15889,
    15901,
    15912,
    15917,
    16000,
    16081,
    16265,
    16281,
    16472,
    16478,
    16493,
    16499,
    16677,
    16717,
    16728,
    16797,
    16801,
    16973,
    17062,
    17064,
    17297,
    17986,
    18160,
    18503,
    18504,
    18509,
    18530,
    20359,
    20360,
    20361,
    20362,
]

# 2 - Bens que deixaram de ser permanente conforme o MTO 2018
# (passaram a ser bens de consumo)
UNSERVICEABLES_CHANGED_TO_CONSUMPTION_ASSETS = [
    96,
    97,
    277,
    278,
    279,
    2470,
    3365,
    3366,
    3367,
    3368,
    9068,
    9069,
]

# 3 - Bens permanentes com espécie divergente conforme MTO 2018
# (mudança apenas na Espécie, continuam sendo do Grupo dos Bens Permanente)
NOW_ONLY_PERMANENT_SPECIES = [1028, 4213, 4946, 8771, 8772, 8937, 8982, 9498, 11655]

# 4 - Veículos não encontrados (Inservíveis)
NOT_FOUND_CAR_VEHICLES = [1538, 1539, 1540, 1541, 1542, 1543, 2395]

# Espécies de veículos
CAR_VEHICLE_SPECIES = Especie.objects.filter(codigo__in=[201, 203, 1327])

# Grupo 35 - Equipamentos de Processamento de Dados
DATA_PROCESSING_EQUIPMENT = GrupoEspecie.objects.get(codigo=35).especies.all()

# Grupo 42 - Equipamenbto de Mobiliário Geral
GENERAL_FURNITURE = GrupoEspecie.objects.get(codigo=42).especies.filter(
    codigo__in=[17, 35, 351, 534, 1290, 1376, 1377, 1378, 1380, 1381]
)

# Patrimônios a serem avaliados (exceto inservíveis)
query = (
    Patrimonio.objects.select_related("item_entrada", "item_entrada__especie")
    .prefetch_related("avaliacoes", "item_entrada__especie__itens_avaliacao")
    .filter(data_tombo__range=[START, END], data_baixa=None)
    .exclude(
        Q(
            plaqueta__in=UNSERVICEABLES_IN_WRITE_OFF_PROCESS,
            item_entrada__nota__conta__tipo=1,
        )
        | Q(plaqueta__in=UNSERVICEABLES_CHANGED_TO_CONSUMPTION_ASSETS)
        | Q(plaqueta__in=NOW_ONLY_PERMANENT_SPECIES, item_entrada__nota__conta__tipo=1)
        | Q(plaqueta__in=NOT_FOUND_CAR_VEHICLES, item_entrada__nota__conta__tipo=1)
    )
)


def is_data_processing_equipment(ai):
    """
    Verifica se o patrimônio em questão é ou não
    equipamento de processamento de dados
    """

    return ai.patrimonio.item_entrada.especie in DATA_PROCESSING_EQUIPMENT


def is_general_furniture(ai):
    """
    Verifica se o patrimônio em questão é ou não mobiliário geral
    """

    return ai.patrimonio.item_entrada.especie in GENERAL_FURNITURE


def is_car_vehicle(ai):
    """
    Verifica se o patrimônio em questão é ou não um veículo automóvel
    """

    return ai.patrimonio.item_entrada.especie in CAR_VEHICLE_SPECIES


def get_vuib(patrimonio):
    """
    Retorna o tempo de vida útil de fábrica
    """

    # Vida Útil Futura (Assumindo como Novo)
    factory_life_span = None
    evaluation_items = patrimonio.item_entrada.especie.itens_avaliacao
    if evaluation_items.count() == 1:
        factory_life_span = evaluation_items.get().vida_util
    elif evaluation_items.count() > 1:
        SPECIES_MORE_THAN_ONE_EVALUATION_ITEM.append(patrimonio)
        factory_life_span = evaluation_items.aggregate(max=Max("vida_util")).get("max")
    else:
        SPECIES_NO_EVALUATION_ITEM.append(patrimonio)
        factory_life_span = 0

    return factory_life_span


def get_period_of_use(avaliacao_item):
    """
    Período de Utilização (Anos)
    """

    interval = datetime.today() - avaliacao_item.patrimonio.data_tombo
    concept = int(interval.days / 365.250000)

    return concept


def calc_fa(EC, PVUF, PU):
    """
    Cálculo do Fator de Avaliação
    """

    # FA ou FR = ((EC x 4) + (PVUF x 6) + [PU x (-3)]) / 100
    return float((EC * 4.000000) + (PVUF * 6.000000) + (PU * -3.000000)) / 100.000000


def run_evaluation(ai):
    """
    Rodar avaliação
    """

    def get_npvuf_concept(patrimonio):
        """
        Retorna o novo período de vida útil Futura mínima ou máxima,
        de acordo com critérios estabelecidos por data e grupo/espécie
        """

        concept = None
        if patrimonio.data_tombo < datetime(2005, 1, 1):
            # Menor PVUF
            concept = "min"
        else:
            # Via de regra, leva maior PVUF
            concept = "max"

            if is_data_processing_equipment(ai):
                if patrimonio.data_tombo < datetime(2010, 7, 1):
                    concept = "min"
                else:
                    concept = "max"
            elif is_general_furniture(ai):
                concept = "min"

        return concept

    # Sub-fatores da avaliação
    EC = EC_IPCA_MAP.get(ai.conservacao)
    PU = PU_MAP.get(get_period_of_use(ai), 10.000000)

    # Vida Útil Inicial do Bem
    VUIB = NPVUF_MAP.get(get_vuib(ai.patrimonio))

    if VUIB:
        concept = get_npvuf_concept(ai.patrimonio)
        NPVUF = VUIB.get(ai.conservacao).get(concept)
        ai.vida_util = NPVUF
    else:
        NOT_FOUND_VUIB_SPECIES.append(ai.patrimonio.item_entrada.especie.pk)

    PVUF = PVUF_MAP.get(NPVUF, 10.000000)

    # Valor de Aquisição
    entrance_item = ai.patrimonio.item_entrada
    acquisition_value = float(entrance_item.valor_unitario)

    # Novo valor do bem patrimonial
    if is_car_vehicle(ai):
        ai.valor_avaliado = FIPE_VALUES.get(ai.patrimonio.pk)
    else:
        # Fator de avaliação
        FA = calc_fa(EC, PVUF, PU)
        ai.valor_avaliado = acquisition_value * FA

    # % residual do valor de aquisição
    residual = entrance_item.especie.itens_avaliacao.get().residual
    ai.residual = acquisition_value * float(residual) / 100.000000

    # Variação
    ai.depreciacao = acquisition_value - ai.valor_avaliado

    return ai


def prepare_assets():
    """Preparar ativos
    Cria o item de Reavaliação
    """

    set_current_user("athenas")

    # Cria ou recupera a Avaliação
    evaluation, created = Avaliacao.objects.get_or_create(
        ano=2018,
        de=START,
        ate=END,
        mes=12,
        tipo=3,
    )

    # Certifica de que todos os itens a serem avaliados sejam apagados
    evaluation.itens.all().delete()

    print("Iniciando criação da carga de Avaliação de Itens ...\n")

    # Cria uma lista vazia de AvaliacaoItem
    ais = []
    for p in query:
        ai = AvaliacaoItem(
            avaliacao=evaluation,
            patrimonio=p,
            valor_atual=p.valor_base,
            # quantidade_dias=(datetime.today() - p.data_tombo).days,
            conservacao=p.conservacao,
        )
        ais.append(run_evaluation(ai))

    # Criação em lote da carga
    AvaliacaoItem.objects.bulk_create(ais)

    print("Encerrada a carga de Avaliação de Itens!\n")


def unlink_species_from_a_evaluation_item():
    """
    Desvincula/Remove de espécie, ItemAvaliacao constante mais de uma vez
    """

    for p in query:
        evaluation_items = p.item_entrada.especie.itens_avaliacao
        if evaluation_items.count() > 1:
            print(p.pk)
            for i in evaluation_items.exclude(
                grupo__titulo="OUTROS MATERIAIS PERMANENTES"
            ):
                p.item_entrada.especie.itens_avaliacao.remove(i)


def generate_evaluation_csv():
    """
    Gera o arquivo CSV após a geração da avaliação com os valores: (Plaqueta, Valor Aquisição, EC, PVUF, PU, Valor Avaliado)
    """

    print("Iniciando a geração do arquivo csv...\n")
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

    try:
        evaluations = AvaliacaoItem.objects.filter(avaliacao=Avaliacao.objects.first())
    except AvaliacaoItem.DoesNotExit:
        print("Não foi possível encontrar os itens avaliados...\n")
    except Exception as e:
        print(e)
    else:
        evaluations_rows = []
        evaluations_header = [
            "Plaqueta",
            "Valor Aquisição",
            "EC",
            "PVUF",
            "PU",
            "Valor Avaliado",
        ]
        for evaluation in evaluations:
            unitary_value = str(
                locale.currency(
                    evaluation.patrimonio.item_entrada.valor_unitario,
                    grouping=True,
                    symbol=None,
                )
            )
            ec = EC_DESCRIPTION_MAP.get(evaluation.conservacao)
            pvuf = PVUF_DESCRIPTION_MAP.get(evaluation.vida_util)
            pu = PU_DESCRIPTION_MAP.get(get_period_of_use(evaluation), ">= 10 anos")
            assessed_value = str(
                locale.currency(evaluation.valor_avaliado, grouping=True, symbol=None)
            )
            row = (
                evaluation.patrimonio.plaqueta,
                unitary_value,
                ec,
                pvuf,
                pu,
                assessed_value,
            )
            evaluations_rows.append(row)

        file_path = os.path.dirname(os.path.abspath("__file__"))
        date_format = date.today().strftime("%d_%m_%Y")
        file_csv = "evaluation_report_{}.csv".format(date_format)
        with open(file_csv, "wb") as csvfile:
            f_csv = csv.writer(csvfile, delimiter=";")
            f_csv.writerow(evaluations_header)
            f_csv.writerows(evaluations_rows)

    print("O arquivo csv foi gerado em: {}/{}".format(file_path, file_csv))


def main():
    """
    Função principal
    """
    prepare_assets()
    generate_evaluation_csv()


if __name__ == "__main__":
    main()
