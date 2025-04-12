# -*- coding: utf-8 -*-
import datetime

from rh.const import (
    # TYPE_TRAVEL,
    TYPE_AWARD_LICENSE,
    TYPE_HEALTH_PREVENT,
    TYPE_MATERNITY_LICENSE,
    # TYPE_WORK_GROUP,
    # TYPE_NEW_FUNCTION,
    # TYPE_ORDELY,
    # TYPE_COMPENSATION_LOW,
    # TYPE_FULL_BIRTHDAY,
    # TYPE_DEPARTURE_DISMISSAL_JUDGMENT,
    TYPE_VACATION,
    TYPE_RECESS,
    TYPE_HEALTH3DAYS,
    TYPE_HEALTH30DAYS,
    TYPE_HEALTH_MEDICAL_BOARD,
    TYPE_HEALTH_FAMILY_DESEASE,
    TYPE_LICENSE_ADOPTION,
    TYPE_LICENSE_SPOUSE,
    TYPE_LICENSE_MILITARY_SERVICE,
    TYPE_LICENSE_POLITICAL_ACTIVITIES,
    TYPE_LICENSE_TRAINING,
    TYPE_LICENSE_SPECIAL_INTEREST,
    TYPE_LICENSE_MANDATE_CLASSIST,
    TYPE_DEPARTURE_AVAILABILITY,
    # TYPE_DEPARTURE_OTHER_ORGAN,
    TYPE_DEPARTURE_MANDATE_ELECTIVE,
    TYPE_DEPARTURE_STUDY,
    TYPE_DEPARTURE_MISSION,
    TYPE_DEPARTURE_ELECTORAL,
    TYPE_DEPARTURE_SERVE_JURY,
    TYPE_DEPARTURE_TRAINING,
    TYPE_DEPARTURE_DISPLACEMENT,
    TYPE_DEPARTURE_COMPETITION,
    TYPE_DEPARTURE_COURSE_CONTEST,
    TYPE_DEPARTURE_PRISION,
    TYPE_DEPARTURE_SUSPENSION,
    TYPE_ABSENCE_BLOOD_DONATION,
    TYPE_ABSENCE_ELECTORAL,
    TYPE_ABSENCE_MARRIAGE,
    TYPE_ABSENCE_BIRTH,
    TYPE_ABSENCE_DEATH,
    TYPE_ABSENCE_CONCLUSION,
    TYPE_ELECTORAL_FLEX,
    TYPE_BANK_HOURS,
)

DATE_V12 = datetime.date(2024, 1, 1)

EVENT_KIND = {
    "EEMP": ("s1000",),
    "TI": (
        "s1005",
        "s1020",
        "s1070",
        "s1010",
    ),
    "CF": (
        "s2200",
        "s2300",
        "s2205",
        "s2206",
        "s2306",
        "s2230",
        "s2231",
        "s2299",
        "s2399",
        "s2298",
        "s2400",
        "s2405",
        "s2410",
        "s2416",
        "s2418",
        "s2420",
        "s3000",
    ),
    "FP": (
        "s1200",
        "s1202",
        "s1207",
        "s1210",
        "s1298",
        "s1299",
    ),
    "TOT": (
        # 's5001',
        # 's5002',
        # 's5011',
    ),
    "SST": (
        "s2210",
        "s2220",
        "s2240",
    ),
    "STPC": (),
    "REP": (
        # 's1298',
    ),
    "FEP": (
        # 's1299',
    ),
    "EBS": (
        # 's3000'
    ),
}

DELIVERY_STATUS_BATCH = {
    1: "Criando",
    2: "Aguardando envio",
    201: "Lote recebido com Sucesso",
    202: "Lote recebido com advertências",
    301: "Erro servidor eSocial",
    401: "Lote incorreto - Erro preenchimento",
    402: "Lote incorreto - Schema inválido",
    403: "Lote incorreto - Versão do schema não permitida",
    404: "Lote incorreto - Erro certificado",
    405: "Lote incorreto - Lote nulo ou vazio",
}


PROCESS_STATUS_BATCH = {
    101: "Lote aguardando processamento",
    201: "Lote processado com Sucesso",
    202: "Lote processado com advertências",
    301: "Erro servidor eSocial",
    401: "Lote incorreto - Erro preenchimento",
    402: "Lote incorreto - Schema inválido",
    403: "Lote incorreto - Versão do schema não permitida",
    404: "Lote incorreto - Erro certificado",
    405: "Lote incorreto - Lote nulo ou vazio",
    501: "Solicitação de consulta incorreta",
}

PROCESS_STATUS_EVENT = {
    # "label": "Aguardando empacotamento",
    1: "Evento criado",
    # "label": "Aguardando finalização de dependência",
    2: "Evento criado mas não pode ser enviado até que todas as dependências sejam satisfeitas",
    # "label": "Empacotado e aguardando envio",
    3: "Evento empacotado no lote de envio",
    # "label": "Enviado e aguardando processamento",
    4: "Evento enviado e aguardando ser processado pela base do eSocial",
    5: "Dependência não satisfeita",
    201: "Sucesso",  # "label": "Sucesso",
    202: "Sucesso com advertência",  # "label": "Sucesso com advertência",
    210: "Sucesso informado localmente",  # "label": "Sucesso informado localmente",
    301: "Erro Servidor",  # "label": "Erro Servidor",
    401: "Erro no conteúdo do evento",  # "label": "Erro no conteúdo do evento",
    402: "Schema inválido",  # "label": "Schema inválido",
    403: "Leiaute inválido",  # "label": "Leiaute inválido",
    # "label": "Erro do certificado digital",
    404: "Erro do certificado digital da assinatura do evento",
    405: "Erro na assinatura evento",  # "label": "Erro na assinatura evento",
    # "label": "Evento não pertence ao grupo",
    406: "Evento não pertence ao grupo especificado no lote de eventos",
    # "label": "Regra de precedência de eventos não seguida",
    407: """A regra de precedência na transmissão de eventos não foi seguida. Eventos desse tipo não 407 devem ser enviados para
        processamento em paralelo. Ver seção 5.6.1 do Manual de Orientação do Desenvolvedor""",
    # "label": "Erro na integração com o sistema CNPJ / CPF",
    408: "Erro na integração com o sistema CNPJ / CPF",
    # "label": "Erro na integração - Procuração Eletrônica RFB",
    409: "Erro na integração com o sistema Procuração Eletrônica RFB",
    # "label": "Erro na integração - Procuração Eletrônica Caixa",
    410: "Erro na integração com o sistema Procuração Eletrônica Caixa",
    # "label": "Assinante inválido",
    411: """Assinante não possui perfil de procuração eletrônica para enviar este tipo de evento ou assinante não consta como representante
        legal da empresa""",
}

PROCESS_STATUS_EVENT_SENT_ERROR = (
    301,  # "Erro Servidor",  # "label": "Erro Servidor",
    401,  # "Erro no conteúdo do evento",  # "label": "Erro no conteúdo do evento",
    402,  # "Schema inválido",  # "label": "Schema inválido",
    403,  # "Leiaute inválido",  # "label": "Leiaute inválido",
    404,  # "Erro do certificado digital da assinatura do evento", # "label": "Erro do certificado digital",
    405,  # "Erro na assinatura evento",  # "label": "Erro na assinatura evento",
    406,  # "Evento não pertence ao grupo especificado no lote de eventos", # "label": "Evento não pertence ao grupo",
    407,  # "A regra de precedência na transmissão de eventos não foi seguida. Eventos desse tipo não 407 devem ser enviados para
    # processamento em paralelo. Ver seção 5.6.1 do Manual de Orientação do Desenvolvedor", # "label": "Regra de precedência de eventos
    # não seguida",
    408,  # "Erro na integração com o sistema CNPJ / CPF", # "label": "Erro na integração com o sistema CNPJ / CPF",
    409,  # "Erro na integração com o sistema Procuração Eletrônica RFB", # "label": "Erro na integração - Procuração Eletrônica RFB",
    410,  # "Erro na integração com o sistema Procuração Eletrônica Caixa", # "label": "Erro na integração - Procuração Eletrônica Caixa",
    411,  # "Assinante não possui perfil de procuração eletrônica para enviar este tipo de evento ou assinante não consta como
    # representante legal da empresa", # "label": "Assinante inválido",
)

PROCESS_STATUS_EVENT_NOT_SENT = (
    1,  # "Evento criado",  # "label": "Aguardando empacotamento",
    2,  # "Evento criado mas não pode ser enviado até que todas as dependências sejam satisfeitas", # "label": "Aguardando finalização
    # de dependência",
    3,  # "Evento empacotado no lote de envio" # "label": "Empacotado e aguardando envio",
)

PROCESS_STATUS_EVENT_VALIDS_SENT = (
    201,  # "Sucesso",  # "label": "Sucesso",
    202,  # "Sucesso com advertência",  # "label": "Sucesso com advertência",
    210,  # "Sucesso informado localmente",
)

PROCESS_STATUS_EVENT_SENT = {
    # "label": "Enviado e aguardando processamento",
    4: "Evento enviado e aguardando ser processado pela base do eSocial",
    201: "Sucesso",  # "label": "Sucesso",
    202: "Sucesso com advertência",  # "label": "Sucesso com advertência",
    210: "Sucesso informado localmente",
    301: "Erro Servidor",  # "label": "Erro Servidor",
    # "label": "Evento não pertence ao grupo",
    406: "Evento não pertence ao grupo especificado no lote de eventos",
    # "label": "Regra de precedência de eventos não seguida",
    407: """A regra de precedência na transmissão de eventos não foi seguida. Eventos desse tipo não 407 devem ser enviados para
        processamento em paralelo. Ver seção 5.6.1 do Manual de Orientação do Desenvolvedor""",
    # "label": "Erro na integração com o sistema CNPJ / CPF",
    408: "Erro na integração com o sistema CNPJ / CPF",
    # "label": "Erro na integração - Procuração Eletrônica RFB",
    409: "Erro na integração com o sistema Procuração Eletrônica RFB",
    # "label": "Erro na integração - Procuração Eletrônica Caixa",
    410: "Erro na integração com o sistema Procuração Eletrônica Caixa",
    # "label": "Assinante inválido",
    411: """Assinante não possui perfil de procuração eletrônica para enviar este tipo de evento ou assinante não consta como
     representante legal da empresa""",
}

CAN_DELETE_EVENT_STATUS = (1, 2, 3, 5)
CAN_SET_DELETED_EVENT_STATUS = (401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411)
VALID_EVENT_STATUS = (1, 2, 3, 4, 201, 202, 210)

EMPLOYER_APP = 1
GOVERNMENT_APP = 2

EMISSION_PROCESS_TYPE = {
    EMPLOYER_APP: "Aplicativo do empregador",
    GOVERNMENT_APP: "Aplicativo governamental",
}

FILE_ORIGIN_ORIGINAL = 1
FILE_ORIGIN_RECTIFIED = 2

FILE_ORIGIN_TYPE = {
    FILE_ORIGIN_ORIGINAL: "ORIGINAL",
    FILE_ORIGIN_RECTIFIED: "RETIFICADO",
}

SIM = "Sim"
NAO = "Não"

NOT_VALID = 1
VALID = 2

STATUS_VALIDATION = {NOT_VALID: "Not Valid", VALID: "Valid"}

INCLUSION = 1
MODIFICATION = 2
EXCLUSION = 3
RECTIFICATION = 4

ACTION = {
    INCLUSION: "inclusao",
    MODIFICATION: "alteracao",
    EXCLUSION: "exclusao",
}

ACTION_RECTIFICATION = {
    INCLUSION: "inclusao",
    RECTIFICATION: "retificacao",
    EXCLUSION: "exclusao",
}

EXCLUSION_TYPE_DEFAULT = 1
EXCLUSION_TYPE_S3000 = 2
EXCLUSION_TYPE_NOT = 3

MONTHLY = 1
ANYTIME = 2
ONCE = 3

PERIODICITY = {
    MONTHLY: "Mensalmente",
    ANYTIME: "Qualquer momento",
    ONCE: "Uma vez(cadastro inicial)",
}

PERIODICITY_KEY_UNICODE = {
    "MONTHLY": MONTHLY,
    "ANYTIME": ANYTIME,
    "ONCE": ONCE,
}


MANDATORY = 1
NOT_MANDATORY = 2
MANDATORY_IF_EXIST = 3
NOT_APPLICABLE = 4

OBLIGATION = {
    MANDATORY: "OBRIGATÓRIO",
    NOT_MANDATORY: "NÃO OBRIGATÓRIO",
    MANDATORY_IF_EXIST: "OBRIGATÓRIO SE EXISTIR INFORMAÇÕES",
    NOT_APPLICABLE: "NÃO APLICÁVEL",
}

ORIGINAL = 1
RECTIFIED = 2

INDICATIVE_TYPE_INFORMATION = {ORIGINAL: "ORIGINAL", RECTIFIED: "RETIFICADO"}

YEARLY = 2

INDICATIVE_ASCERTAINMENT_PERIOD = {MONTHLY: "MENSAL", YEARLY: "ANUAL(13 SALÁRIO)"}

OCCURRENCE_MANDATORY = 1
OCCURRENCE_NOT_MANDATORY = 2

OCCURRENCE_CHOICE = {
    "1": OCCURRENCE_MANDATORY,
    "0": OCCURRENCE_NOT_MANDATORY,
}

RACE_ESOCIAL = {
    1: "Branca",
    2: "Negra",
    3: "Parda (parda ou declarada como mulata, cabocla, cafuza, mameluca ou mestiça de negro com pessoa de outra cor ou raça)",
    4: "Amarela (de origem japonesa, chinesa, coreana etc)",
    5: "Indígena",
    6: "Não informado",
}

RACE_MAP = {
    1: 3,  # ATHENAS: ESOCIAL
    2: 4,
    3: 2,
    4: 5,
    5: 6,
    6: 1,
}

MARITAL_STATUS_ESOCIAL = {
    1: "Solteiro",
    2: "Casado",
    3: "Divorciado",
    4: "Separado",
    5: "Viúvo",
}

MARITAL_STATUS_MAP = {
    1: 1,
    2: 2,
    3: 5,
    4: 4,
    5: 3,
    6: 2,  # "UNIAO ESTAVEL",
}

DEGREE_EDUCATION_ESOCIAL = {
    1: "Analfabeto, inclusive o que, embora tenha recebido instrução, não se alfabetizou",
    2: "Até o 5o ano incompleto do Ensino Fundamental (antiga 4a série) ou que se tenha alfabetizado sem ter frequentado escola regular",
    3: "5o ano completo do Ensino Fundamental",
    4: "Do 6o ao 9o ano do Ensino Fundamental incompleto (antiga 5a a 8a série)",
    5: "Ensino Fundamental Completo",
    6: "Ensino Médio incompleto",
    7: "Ensino Médio completo",
    8: "Educação Superior incompleta",
    9: "Educação Superior completa",
    10: "Pós-Graduação completa",
    11: "Mestrado completo",
    12: "Doutorado completo",
}

DEGREE_EDUCATION_MAP = {
    1: "01",  # "ANALFABETO",
    2: "02",  # "ALFABETIZADO SEM CURSOS REGULARES",
    # 3: '',  # "SERA EXCLUIDO 4",
    4: "05",  # "FUNDAMENTAL COMPLETO",
    5: "06",  # "MÉDIO INCOMPLETO",
    6: "07",  # "MEDIO COMPLETO OU EQUIVALENTE LEGAL",
    7: "08",  # "SUPERIOR INCOMPLETO",
    8: "09",  # "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL",
    9: "10",  # "ESPECIALIZAÇÃO/PÓS",
    10: "11",  # "MESTRADO",
    11: "12",  # "DOUTORADO",
    # 12: ,  # "SERA EXCLUIDO",
    # 13: ,  # "SERA EXCLUIDO 1",
    # 14: ,  # "SERA EXCLUIDO 2",
    15: "02",  # "ATÉ O 5o ANO INCOMPLETO DO ENSINO FUNDAMENTAL",
    16: "03",  # "5o ANO COMPLETO DO ENSINO FUNDAMENTAL",
    17: "04",  # "DO 6o AO 9o ANO DO ENSINO FUNDAMENTAL INCOMPLETO",
}

TYPE_STREET_ESOCIAL = {
    "A": "Área",
    "AC": "Acesso",
    "ACA": "Acampamento",
    "ACL": "Acesso Local",
    "AD": "Adro",
    "AE": "Área Especial",
    "AER": "Aeroporto",
    "AL": "Alameda",
    "AMD": "Avenida Marginal Direita",
    "AME": "Avenida Marginal Esquerda",
    "AN": "Anel Viário",
    "ANT": "Antiga Estrada",
    "ART": "Artéria",
    "AT": "Alto",
    "ATL": "Atalho",
    "A V": "Área Verde",
    "AV": "Avenida",
    "AVC": "Avenida Contorno",
    "AVM": "Avenida Marginal",
    "AVV": "Avenida Velha",
    "BAL": "Balneário",
    "BC": "Beco",
    "BCO": "Buraco",
    "BEL": "Belvedere",
    "BL": "Bloco",
    "BLO": "Balão",
    "BLS": "Blocos",
    "BLV": "Bulevar",
    "BSQ": "Bosque",
    "BVD": "Boulevard",
    "BX": "Baixa",
    "C": "Cais",
    "CAL": "Calçada",
    "CAM": "Caminho",
    "CAN": "Canal",
    "CH": "Chácara",
    "CHA": "Chapadão",
    "CIC": "Ciclovia",
    "CIR": "Circular",
    "CJ": "Conjunto",
    "CJM": "Conjunto Mutirão",
    "CMP": "Complexo Viário",
    "COL": "Colônia",
    "COM": "Comunidade",
    "CON": "Condomínio",
    "COR": "Corredor",
    "CPO": "Campo",
    "CRG": "Córrego",
    "CTN": "Contorno",
    "DSC": "Descida",
    "DSV": "Desvio",
    "DT": "Distrito",
    "EB": "Entre Bloco",
    "EIM": "Estrada Intermunicipal",
    "ENS": "Enseada",
    "ENT": "Entrada Particular",
    "EQ": "Entre Quadra",
    "ESC": "Escada",
    "ESD": "Escadaria",
    "ESE": "Estrada Estadual",
    "ESI": "Estrada Vicinal",
    "ESL": "Estrada de Ligação",
    "ESM": "Estrada Municipal",
    "ESP": "Esplanada",
    "ESS": "Estrada de Servidão",
    "EST": "Estrada",
    "ESV": "Estrada Velha",
    "ETA": "Estrada Antiga",
    "ETC": "Estação",
    "ETD": "Estádio",
    "ETN": "Estância",
    "ETP": "Estrada Particular",
    "ETT": "Estacionamento",
    "EVA": "Evangélica",
    "EVD": "Elevada",
    "EX": "Eixo Industrial",
    "FAV": "Favela",
    "FAZ": "Fazenda",
    "FER": "Ferrovia",
    "FNT": "Fonte",
    "FRA": "Feira",
    "FTE": "Forte",
    "GAL": "Galeria",
    "GJA": "Granja",
    "HAB": "Núcleo Habitacional",
    "IA": "Ilha",
    "IND": "Indeterminado",
    "IOA": "Ilhota",
    "JD": "Jardim",
    "JDE": "Jardinete",
    "LD": "Ladeira",
    "LGA": "Lagoa",
    "LGO": "Lago",
    "LOT": "Loteamento",
    "LRG": "Largo",
    "LT": "Lote",
    "MER": "Mercado",
    "MNA": "Marina",
    "MOD": "Modulo",
    "MRG": "Projeção",
    "MRO": "Morro",
    "MTE": "Monte",
    "NUC": "Núcleo",
    "NUR": "Núcleo Rural",
    "O": "Outros",
    "OUT": "Outeiro",
    "PAR": "Paralela",
    "PAS": "Passeio",
    "PAT": "Pátio",
    "PC": "Praça",
    "PCE": "Praça de Esportes",
    "PDA": "Parada",
    "PDO": "Paradouro",
    "PNT": "Ponta",
    "PR": "Praia",
    "PRL": "Prolongamento",
    "PRM": "Parque Municipal",
    "PRQ": "Parque",
    "PRR": "Parque Residencial",
    "PSA": "Passarela",
    "PSG": "Passagem",
    "PSP": "Passagem de Pedestre",
    "PSS": "Passagem Subterrânea",
    "PTE": "Ponte",
    "PTO": "Porto",
    "Q": "Quadra",
    "QTA": "Quinta",
    "QTS": "Quintas",
    "R": "Rua",
    "R I": "Rua Integração",
    "R L": "Rua de Ligação",
    "R P": "Rua Particular",
    "R V": "Rua Velha",
    "RAM": "Ramal",
    "RCR": "Recreio",
    "REC": "Recanto",
    "RER": "Retiro",
    "RES": "Residencial",
    "RET": "Reta",
    "RLA": "Ruela",
    "RMP": "Rampa",
    "ROA": "Rodo Anel",
    "ROD": "Rodovia",
    "ROT": "Rotula",
    "RPE": "Rua de Pedestre",
    "RPR": "Margem",
    "RTN": "Retorno",
    "RTT": "Rotatória",
    "SEG": "Segunda Avenida",
    "SIT": "Sitio",
    "SRV": "Servidão",
    "ST": "Setor",
    "SUB": "Subida",
    "TCH": "Trincheira",
    "TER": "Terminal",
    "TR": "Trecho",
    "TRV": "Trevo",
    "TUN": "Túnel",
    "TV": "Travessa",
    "TVP": "Travessa Particular",
    "TVV": "Travessa Velha",
    "UNI": "Unidade",
    "V": "Via",
    "V C": "Via Coletora",
    "V L": "Via Local",
    "VAC": "Via de Acesso",
    "VAL": "Vala",
    "VCO": "Via Costeira",
    "VD": "Viaduto",
    "V-E": "Via Expressa",
    "VER": "Vereda",
    "VEV": "Via Elevado",
    "VL": "Vila",
    "VLA": "Viela",
    "VLE": "Vale",
    "VLT": "Via Litorânea",
    "VPE": "Via de Pedestre",
    "VRT": "Variante",
    "ZIG": "Zigue-Zague",
}

TYPE_STREET_MAP = {
    1: "AV",
    2: "PC",
    3: "VLA",
    5: "VD",
    8: "R",
    9: "Q",
}

FIRE_TYPE_ESOCIAL = {
    "01": "Rescisão com justa causa, por iniciativa do empregador",
    "02": "Rescisão sem justa causa, por iniciativa do empregador",
    "03": "Rescisão antecipada do contrato a termo por iniciativa do empregador",
    "04": "Rescisão antecipada do contrato a termo por iniciativa do empregado",
    "05": "Rescisão por culpa recíproca",
    "06": "Rescisão por término do contrato a termo",
    "07": "Rescisão do contrato de trabalho por iniciativa do empregado",
    "08": "Rescisão do contrato de trabalho por interesse do(a) empregado(a), nas hipóteses previstas nos arts. 394 e 483, § 1º da CLT",
    "09": "Rescisão  por  opção  do  empregado  em  virtude  de  falecimento  do  empregador  individual  ou empregador doméstico",
    "10": "Rescisão por falecimento do empregado",
    "11": "Transferência  de  empregado  para  empresa  do  mesmo  grupo  empresarial  que  tenha  assumido  os encargos trabalhistas, \
        sem que tenha havido rescisão do contrato de trabalho",
    "12": "Transferência  de  empregado  da  empresa  consorciada  para  o  consórcio  que  tenha  assumido  os encargos trabalhistas, e \
        vice-versa, sem que tenha havido rescisão do contrato de trabalho",
    "13": "Transferência de empregado de empresa ou consórcio, para outra empresa ou consórcio que tenha assumido os encargos trabalhistas \
        por motivo de sucessão (fusão, cisão ou incorporação), sem que tenha havido rescisão do contrato de trabalho",
    "14": "Rescisão  do  contrato  de  trabalho  por  encerramento  da  empresa,  de  seus  estabelecimentos  ou supressão  de  parte  de  \
        suas  atividades  ou  falecimento  do  empregador  individual  ou  empregador doméstico sem continuação da atividade",
    "15": "Demissão de Aprendizes por Desempenho Insuficiente ou Inadaptação",
    "16": "Declaração  de  nulidade  do  contrato  de  trabalho  por  infringência  ao  inciso  II  do  art.  37  da Constituição Federal, \
        quando mantido o direito ao salário",
    "17": "Rescisão Indireta do Contrato de Trabalho",
    "18": "Aposentadoria Compulsória (somente para categorias de trabalhadores 301 a 309)",
    "19": "Aposentadoria por idade (somente para categorias de trabalhadores 301 a 309)",
    "20": "Aposentadoria por idade e tempo de contribuição (somente categorias 301 a 309)",
    "21": "Reforma Militar (somente para categorias de trabalhadores 301 a 309)",
    "22": "Reserva Militar (somente para categorias de trabalhadores 301 a 309)",
    "23": "Exoneração (somente para categorias de trabalhadores 301 a 309)",
    "24": "Demissão (somente para categorias de trabalhadores 301 a 309)",
    "25": "Vacância para assumir outro cargo efetivo (somente para categorias de trabalhadores 301 a 309)",
    "26": "Rescisão   do   contrato   de   trabalho   por   paralisação   temporária   ou   definitiva   da   empresa, estabelecimento  ou  \
        parte  das  atividades  motivada  por  atos  de  autoridade  municipal,  estadual  ou federal",
    "27": "Rescisão por motivo de força maior",
    "28": "Término da Cessão/Requisição",
    "29": "Redistribuição",
    "30": "Mudança de Regime Trabalhista",
    "31": "Reversão de Reintegração",
    "32": "Extravio de Militar",
    "33": "Rescisão por acordo entre as partes (art. 484-A da CLT)",
    "34": "Transferência de titularidade do empregado doméstico para outro representante da mesma unidade familiar",
    "35": "Extinção do contrato de trabalho intermitente",
    "36": "Mudança de CPF",
}

FIRE_TYPE_MAP = {
    1: "23",  # 'EXONERAÇÃO EFETIVO',
    2: "23",  # 'EXONERAÇÃO COMISSIONADO',
    3: "23",  # 'EXONERAÇÃO ESTABILIZADO - SERA EXCLUIDO',
    4: "00",  # 'APOSENTADORIA POR INVALIDEZ',
    5: "00",  # 'APOSENTADORIA VOLUNTÁRIA - SERA EXCLUIDO',
    6: "25",  # 'POSSE EM OUTRO CARGO',
    7: "10",  # 'FALECIMENTO',
    8: "00",  # 'RESCISÃO - SERA EXCLUIDO',
    9: "24",  # 'DEMISSÃO',
    10: "00",  # 'RESERVA REFORMA - SERA EXCLUIDO',
    11: "00",  # 'DISPONIBILIDADE - SERA EXCLUIDO',
    12: "00",  # 'PROMOÇÃO/REMOÇÃO',
    13: "28",  # 'FIM REQUISIÇÃO/ACORDO COOPERAÇÃO',
    14: "18",  # 'APOSENTADORIA COMPULSÓRIA',
    15: "00",  # 'APOSENTADORIA ESPECIAL - SERA EXCLUIDO',
    16: "20",  # 'APOSENTADORIA POR TEMPO DE CONTRIBUIÇÃO',
    17: "19",  # 'APOSENTADORIA POR IDADE',
    18: "29",  # 'REDISTRIBUIÇÃO',
    19: "31",  # 'REVERSÃO DE REINTEGRAÇÃO',
    20: "00",  # 'FIM DE MANDATO'
}

DEPARTURE_TYPE_ESOCIAL = {
    "01": "Acidente/Doença do trabalho",
    "03": "Acidente/Doença não relacionada ao trabalho",
    "05": "Afastamento/licença   prevista   em   regime   próprio   (estatuto),   sem remuneração",
    "06": "Aposentadoria por invalidez",
    "07": "Acompanhamento  -  Licença  para  acompanhamento  de  membro  da família enfermo",
    "08": "Afastamento do empregado para participar de atividade do Conselho Curador  do  FGTS  -  art.  65,  §6º,  Dec.  99.684/90  \
        (Regulamento  do FGTS)",
    "10": "Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração",
    "11": "Cárcere",
    "12": "Cargo Eletivo - Candidato a cargo eletivo - Lei 7.664/1988. art. 25°, parágrafo único - Celetistas em geral",
    "13": "Cargo  Eletivo  -  Candidato  a  cargo  eletivo   -  Lei   Complementar 64/1990. art. 1°, inciso II, alínea “l” - Servidor \
        público, estatutário ou não, dos órgãos ou entidades da Administração Direta ou Indireta da União,   dos   Estados,   do   \
        Distrito   Federal,   dos   Municípios   e   dos Territórios, inclusive das fundações mantidas pelo Poder Público",
    # '14': 'Cessão / Requisição',
    "15": "Gozo  de  férias ou recesso  - Afastamento  temporário para o  gozo  de férias ou recesso",
    "16": "Licença     remunerada     -     Lei,     liberalidade     da     empresa     ou Acordo/Convenção Coletiva de Trabalho",
    # '17': 'Licença  Maternidade  -  120  dias  e  suas  prorrogações/antecipações, inclusive para o cônjuge sobrevivente|01/01/2014',
    # '17': 'Licença Maternidade - 120 dias, inclusive para o cônjuge sobrevivente',
    "17": "Licença Maternidade",
    "18": "Licença Maternidade - 121 dias a 180 dias, Lei 11.770/2008 (Empresa Cidadã), inclusive para o cônjuge sobrevivente",
    "19": "Licença Maternidade - Afastamento temporário por motivo de aborto não criminoso",
    "20": "Licença Maternidade - Afastamento temporário por motivo de licença-maternidade  decorrente  de  adoção  ou  guarda  judicial  \
        de  criança, inclusive para o cônjuge sobrevivente",
    "21": "Licença não remunerada ou Sem Vencimento",
    "22": "Mandato  Eleitoral  -  Afastamento  temporário  para  o  exercício  de mandato eleitoral",
    # '23': 'Mandato  Eleitoral  -  Afastamento  temporário  para  o  exercício  de mandato eleitoral, com remuneração',
    "24": "Mandato   Sindical mandato sindical|-   Afastamento|temporário|para|exercício|de",
    "25": "Mulher vítima de violência - Lei 11.340/2006 - art. 9º   §2o, II - Lei Maria da Penha",
    "26": "Participação  de  empregado  no  Conselho  Nacional  de  Previdência Social-CNPS (art. 3º, Lei 8.213/1991)",
    "27": "Qualificação - Afastamento por suspensão do contrato de acordo com o art 476-A da CLT",
    "28": "Representante   Sindical   -   Afastamento   pelo   tempo   que   se   fizer necessário,   quando,   na   qualidade   de \
        representante   de   entidade sindical,   estiver   participando   de   reunião   oficial   de   organismointernacional do \
        qual o Brasil seja membro",
    "29": "Serviço Militar - Afastamento temporário para prestar serviço militar obrigatório",
    # '30': 'Suspensão disciplinar - CLT, art. 474',
    "31": "Servidor Público em Disponibilidade",
    # '33': 'Licença Maternidade - de 180 dias, Lei 13.301/2016',
    "34": "Inatividade  do  trabalhador  avulso  (portuário  ou  não  portuário)  por período superior a 90 dias",
    "35": "Licença   Maternidade   -   Antecipação   e/ou   prorrogação   mediante atestado médico",
    "36": "Afastamento temporário de exercente de mandato eletivo para cargo em comissão",
}

DEPARTURE_TYPE_MAP = {
    # NÃO CONSTA '01',  # 'Acidente/Doença do trabalho',
    # TYPE_HEALTH3DAYS: '03', # NÃO VAI COMO 3 POIS EXISTE REGRA QUE NÃO ENVIA COMO 3  # 'Acidente/Doença não relacionada ao trabalho',
    TYPE_HEALTH3DAYS: "10",  # 'Acidente/Doença não relacionada ao trabalho',
    # TYPE_HEALTH3DAYS SÓ VAI PARA REGIME GERAL
    TYPE_HEALTH_MEDICAL_BOARD: "10",  # 'Acidente/Doença não relacionada ao trabalho',
    TYPE_HEALTH30DAYS: "10",  # 'Acidente/Doença não relacionada ao trabalho',
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   sem remuneração',
    TYPE_DEPARTURE_COURSE_CONTEST: "05",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   sem remuneração',
    TYPE_DEPARTURE_SUSPENSION: "05",
    # NÃO CONSTA : '06',  # 'Aposentadoria por invalidez',
    # 'Acompanhamento  -  Licença  para  acompanhamento  de  membro  da família enfermo',
    TYPE_HEALTH_FAMILY_DESEASE: "07",
    # NÃO CONSTA '08',  # 'Afastamento do empregado para participar de atividade do Conselho Curador  do  FGTS  -  art.  65,  §6º,
    # Dec.  99.684/90  (Regulamento  do FGTS)',
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_LICENSE_TRAINING: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_STUDY: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_MISSION: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_BLOOD_DONATION: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_ELECTORAL: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_MARRIAGE: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_BIRTH: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_DEATH: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ABSENCE_CONCLUSION: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_TRAINING: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_SERVE_JURY: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_ELECTORAL: "10",
    # TYPE_DEPARTURE_COURSE_CONTEST: '10',  # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_DISPLACEMENT: "10",
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_DEPARTURE_COMPETITION: "10",
    TYPE_BANK_HOURS: "10",
    TYPE_HEALTH_PREVENT: "10",
    TYPE_AWARD_LICENSE: "10",
    # TYPE_DEPARTURE_SUSPENSION: '10',  # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    # 'Afastamento/licença   prevista   em   regime   próprio   (estatuto),   com remuneração',
    TYPE_ELECTORAL_FLEX: "10",
    TYPE_DEPARTURE_PRISION: "11",  # 'Cárcere',
    # NÃO CONSTA '12',  # 'Cargo Eletivo - Candidato a cargo eletivo - Lei 7.664/1988. art. 25°, parágrafo único - Celetistas em geral',
    TYPE_LICENSE_POLITICAL_ACTIVITIES: "13",  # 'Cargo  Eletivo  -  Candidato  a  cargo  eletivo   -  Lei   Complementar 64/1990. art. 1°,
    # inciso II, alínea “l” - Servidor público, estatutário ou não, dos órgãos ou entidades da Administração Direta ou Indireta da União,
    # dos   Estados,   do   Distrito   Federal,   dos   Municípios   e   dos Territórios,
    # inclusive das fundações mantidas pelo Poder Público',
    # TYPE_DEPARTURE_OTHER_ORGAN: '14',  # 'Cessão / Requisição',
    # 'Gozo  de  férias ou recesso  - Afastamento  temporário para o  gozo  de férias ou recesso',
    TYPE_VACATION: "15",
    # 'Gozo  de  férias ou recesso  - Afastamento  temporário para o  gozo  de férias ou recesso',
    TYPE_RECESS: "15",
    # NÃO CONSTA '16',  # 'Licença remunerada - Lei, liberalidade da empresa ou Acordo/Convenção Coletiva de Trabalho',
    # NÃO CONSTA '17',  # 'Licença Maternidade - 120 dias, inclusive para o cônjuge sobrevivente',
    # 'Licença Maternidade - 121 dias a 180 dias, Lei 11.770/2008 (Empresa Cidadã), inclusive para o cônjuge sobrevivente',
    TYPE_MATERNITY_LICENSE: "17",
    # TYPE_MATERNITY_LICENSE: '19',  # 'Licença Maternidade - Afastamento temporário por motivo de aborto não criminoso',
    TYPE_LICENSE_ADOPTION: "20",  # 'Licença Maternidade - Afastamento temporário por motivo de licença-maternidade
    # decorrente  de  adoção  ou  guarda  judicial  de  criança, inclusive para o cônjuge sobrevivente',
    TYPE_LICENSE_SPOUSE: "05",  # 'Licença não remunerada ou Sem Vencimento',
    # 'Licença não remunerada ou Sem Vencimento',
    TYPE_LICENSE_SPECIAL_INTEREST: "05",
    # 'Mandato  Eleitoral  -  Afastamento  temporário  para  o  exercício  de mandato eleitoral, sem remuneração',
    TYPE_DEPARTURE_MANDATE_ELECTIVE: "22",
    # 'Mandato   Sindical mandato sindical|-   Afastamento|temporário|para|exercício|de',
    TYPE_LICENSE_MANDATE_CLASSIST: "24",
    # NÃO CONSTA '25',  # 'Mulher vítima de violência - Lei 11.340/2006 - art. 9º   §2o, II - Lei Maria da Penha',
    # NÃO CONSTA '26',  # 'Participação  de  empregado  no  Conselho  Nacional  de  Previdência Social-CNPS (art. 3º, Lei 8.213/1991)',
    # NÃO CONSTA '27',  # 'Qualificação - Afastamento por suspensão do contrato de acordo com o art 476-A da CLT',
    # NÃO CONSTA '28',  # 'Representante   Sindical   -   Afastamento   pelo   tempo   que   se   fizer necessário,
    # quando,   na   qualidade   de   representante   de   entidade sindical,   estiver   participando   de   reunião   oficial   de
    # organismointernacional do qual o Brasil seja membro',
    # 'Serviço Militar - Afastamento temporário para prestar serviço militar obrigatório',
    TYPE_LICENSE_MILITARY_SERVICE: "29",
    # NÃO CONSTA '30',  # 'Suspensão disciplinar - CLT, art. 474',
    TYPE_DEPARTURE_AVAILABILITY: "31",  # 'Servidor Público em Disponibilidade',
    # 0: '35',  # 'Licença   Maternidade   -   Antecipação   e/ou   prorrogação   mediante atestado médico',
}


DEPENDENT_TYPE_ESOCIAL = {
    "01": "Cônjuge",
    "02": "Companheiro(a)  com  o(a)  qual  tenha  filho  ou  viva  há  mais  de  5  (cinco)  anos  ou  possua Declaração de União Estável",
    "03": "Filho(a) ou enteado(a)",
    "04": "Filho(a) ou enteado(a), universitário(a) ou cursando escola técnica de 2º grau",
    "06": "Irmão(ã), neto(a) ou bisneto(a) sem arrimo dos pais, do(a) qual detenha a guarda judicial",
    # ITEM 07 não está sendo utilizado no arquivo de eventos, porém consta no arquivo de tabelas em tipo de dependente
    # '07': 'Irmão(ã), neto(a) ou bisneto(a) sem arrimo dos pais, universitário(a) ou cursando escola técnica de 2° grau,
    # do(a) qual detenha a guarda judicial',
    "09": "Pais, avós e bisavós",
    "10": "Menor pobre do qual detenha a guarda judicial",
    "11": "A pessoa absolutamente incapaz, da qual seja tutor ou curador",
    "12": "Ex-cônjuge",
    "99": "Agregado/Outros",
}

DEPENDENT_TYPE_MAP = {
    1: "01",  # "CÔNJUGE",
    2: "02",  # "COMPANHEIRO(A)",
    3: "03",  # "FILHO(A) NÃO EMANCIPADO MENOR DE 21 ANOS",
    4: "11",  # "FILHO(A) ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR",
    5: "09",  # "PAI(MÃE) COM DEPENDÊNCIA ECONÔMICA",
    6: "06",  # "IRMÃO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA E GUARDA JUDICIAL",
    7: "11",  # "IRMAO(A) ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR",
    8: "03",  # "ENTEADO NÃO EMANCIPADO MENOR DE 21",
    9: "11",  # "ENTEADO ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR",
    10: "10",  # "MENOR TUTELADO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA OU GUARDA JUDICIAL",
    11: "11",  # "MENOR ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR",
    12: "09",  # "AVÓS COM DEPENDENCIA ECONOMICA",
    13: "09",  # "BISAVÓS COM DEPENDENCIA ECONOMICA",
    # "NETO(A) NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA E GUARDA JUDICIAL",
    14: "06",
    # "BISNETO(A) NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA E GUARDA JUDICIAL",
    15: "06",
    16: "12",  # " EX-CÔNJUGE",
    # "FILHO(A) OU ENTEADO(A) UNIVERSITÁRIO(A) OU CURSANDO ESCOLA TÉCNICA DE 2ºGRAU, ATÉ 24 ANOS",
    17: "04",
    18: "99",  # "AGREGADO/OUTROS",
    None: "99",
}

EQUAL_VALIDITY = 1
DIFF_VALIDITY = 2
DIFF_VALIDITY_END = 3

MAP_VALIDITY_RESULT = {
    EQUAL_VALIDITY: "EQUAL_VALIDITY",
    DIFF_VALIDITY: "DIFF_VALIDITY",
    DIFF_VALIDITY_END: "DIFF_VALIDITY_END",
}

NO_RESTRICTION = 0  # Sem restrições
SAME_EVENT = 1
EQUAL_VALIDITY_DIFF_CONTENT = 2  # Igual validade e conteudo diferente
DIFF_VALIDITY_DIFF_CONTENT = 3  # Diferente validade e conteudo diferente
DIFF_VALIDITY_SAME_CONTENT = 4  # Diferente validade e conteudo diferente
DIFF_VALIDITY_END_SAME_CONTENT = 5  # Diferente validade e conteudo diferente
DOESNT_EXIST_REFERENCE = 7
NOTHING_TODO = 9
EXCLUDE_EVENT = 10

MAP_VALIDATE_RESULT = {
    NO_RESTRICTION: "NO_RESTRICTION",
    SAME_EVENT: "SAME_EVENT",
    NOTHING_TODO: "NOTHING_TODO",
    EQUAL_VALIDITY_DIFF_CONTENT: "EQUAL_VALIDITY_DIFF_CONTENT",
    DIFF_VALIDITY_DIFF_CONTENT: "DIFF_VALIDITY_DIFF_CONTENT",
    DIFF_VALIDITY_SAME_CONTENT: "DIFF_VALIDITY_SAME_CONTENT",
    DIFF_VALIDITY_END_SAME_CONTENT: "DIFF_VALIDITY_END_SAME_CONTENT",
    DOESNT_EXIST_REFERENCE: "DOESNT_EXIST_REFERENCE",
    EXCLUDE_EVENT: "EXCLUDE_EVENT",
}

# 1 Sem diferença
# 2 Diferenças realacionadas à aplicação da Data Base
# 3 Diferenças realacionadas à aplicação de progressões retroativas
# 4 Diferenças realacionadas diversas

MAP_REASON_DIFFERENCE_IADC = {
    2: "A",  # Acordo Coletivo de Trabalho
    # 1: 'B',  # Diferenças realacionadas diversas "IN RFB nº 2.107/22"
    3: "B",  # Legislação federal, estadual, municipal ou distrital
    4: "B",  # Diferenças realacionadas diversas "IN RFB nº 2.107/22"
    # 1: 'C',  # Convenção Coletiva de Trabalho
    # 1: 'D',  # Sentença normativa - Dissídio
    # 1: 'E',  # Conversão de licença saúde em acidente de trabalho
    # 1: 'F',  # Outras verbas de natureza salarial ou não salarial devidas após o desligamento
    # 1: 'G',  # Antecipação de diferenças de acordo, convenção ou dissídio coletivo
    # 1: 'H',  # Recolhimento mensal de FGTS anterior ao início de obrigatoriedade dos eventos periódicos
}

MAP_TPPGTO_TO_DEMONSTRATIVE = {
    1: "s1200",
    4: "s1202",
    5: "s1207",
}

CATEGORIA_EVENTO_CADASTRO = {
    "EFE": ["EFE", "EFC", "ECM"],
    "CMS": ["CMS"],
    "MBR": ["MBR", "MEL", "MEC", "MCM", "MBR2", "MEL2", "MEC2", "MCM2"],
    "REQ": ["REQ", "RCM", "TCR", "VOL", "CTR", "EXT", "RFC", "REX", "COE"],
    "BFP": ["BFP", "APO", "MAP", "SAP", "MAP2"],
    "EST": ["EST", "RES", "JCA"],
}


EVENTOS_CADASTRO = [
    "s2200",
    "s2300",
    "s2205",
    "s2206",
    "s2306",
    "s2400",
    "s2405",
    "s2410",
    "s2416",
    "s2418",
    "s2420",
    "s2230",
    "s2231",
    "s2299",
    "s2399",
    "s2298",
]
