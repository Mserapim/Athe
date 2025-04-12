from rh.pvf.const import (
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
    STS_EFFECTIVE,
    STS_STAND_BY,
)

NORMAL = 1
JUSTIFICADO = 2
FALTA = 3
FERIADOS_PONTO_FACULTATIVOS = 4
LICENCAS_AFASTAMENTOS = 5
DSR = 6
VIAGEM_A_SERVICO = 7
TELETRABALHO = 8

TIPO_DIA = {
    NORMAL: "Normal",
    JUSTIFICADO: "Justiticado",
    FALTA: "Falta",
    FERIADOS_PONTO_FACULTATIVOS: "Feriados e Ponto Facultativos",
    LICENCAS_AFASTAMENTOS: "Licenças e Afastamentos",
    DSR: "DSR",
}

DIAS_SEMANA = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]

ORIGEM_JUSTIFICATIVA_VDF = 1
ORIGEM_JUSTIFICATIVA_GESTOR_FALTAS = 2
ORIGEM_JUSTIFICATIVA_FERIADO_MUNICIPAL = 3
ORIGEM_JUSTIFICATIVA_FOLHA_PONTO = 4
ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO = 5

ANEXO_OBRIGATORIO = 1


TIPO_JUSTIFICATIVA_MAP = {
    1: 4,  # "ESQUECEU DE REGISTRAR" para "Esquecimento no registro ponto"
    2: 4,  # "ESQUECEU O CRACHÁ" para "Esquecimento no registro ponto"
    3: 24,  # "FERIADO MUNICIPAL." para "Feriado Municipal"
    4: 45,  # "LUTO OFICIAL" para "Afastamento(Licenças)"
    5: 26,  # "PARTICIPANDO DE CURSO" para "Participando de curso"
    6: 25,  # "JORNADA REDUZIDA - PERÍODO DE PROVAS" para "Jornada reduzida - período de provas"
    7: 46,  # "LICENÇA-PRÊMIO." para "Afastamentos (Usufrutos)"
    8: 46,  # "FOLGA CONCURSO ESTAGIÁRIO" para "Afastamentos (Usufrutos)"
    9: 46,  # "FOLGA PLANTÃO SERVIDOR" para "Afastamentos (Usufrutos)"
    10: 46,  # "RECESSO REMUNERADO" para "Afastamentos (Usufrutos)"
    11: 47,  # "RECESSO ANO NOVO." para "Feriados e Pontos Facultativos"
    12: 18,  # "A SERVIÇO DA SINDSEMP-MT" para "Outros"
    13: 45,  # "SISTEMA EM MANUTENÇÃO." para "Afastamento(Licenças)"
    14: 7,  # "HORÁRIO COMPENSADO" para "Compensado durante o mês"
    15: 45,  # "LICENÇA PARA TRATAR INTERESSE PARTICULAR" para "Afastamento(Licenças)"
    16: 9,  # "SUSPENSÃO DO EXPEDIENTE" para "Suspensão de expediente por Problemas no prédio/Detetização"
    17: 18,  # "SISTEMA EM MANUTENCAO" para "Outros"
    18: 45,  # "LICENÇA PARA QUALIFICAÇÃO PROFISSIONAL" para "Afastamento(Licenças)"
    19: 7,  # "HORÁRIO COMPENSADO." para "Compensado durante o mês"
    20: 45,  # "LICENÇA PATERNIDADE" para "Afastamento(Licenças)"
    21: 47,  # "FERIADO" para "Feriados e Pontos Facultativos"
    22: 4,  # "PONTO NÃO REGISTRADO" para "Esquecimento no registro ponto"
    23: 18,  # "A SERVIÇO FORA DA SEDE" para "Outros"
    24: 47,  # "PONTO FACULTATIVO" para "Feriados e Pontos Facultativos"
    25: 18,  # "DEMITIDO" para "Outros"
    26: 16,  # "DISPENSADO DO PONTO." para "Dispensa de ponto"
    27: 4,  # "SEM CRACHÁ" para "Esquecimento no registro ponto"
    28: 45,  # "LICENÇA LUTO" para "Afastamento(Licenças)"
    29: 47,  # "FERIADO MUNICIPAL" para "Feriados e Pontos Facultativos"
    30: 18,  # "SISTEMA EM MANUTENÇÃO" para Outros"
    31: 16,  # "DISPENSADO DO PONTO" para "Dispensa de ponto"
    32: 18,  # "ATIVIDADES NÃO INICIADAS" para "Outros"
    33: 45,  # "LICENÇA GESTACIONAL" para “Afastamento(Licenças)"
    34: 46,  # "FOLGA RECESSO FORENSE" para "Afastamentos (Usufrutos)"
    35: 46,  # "DISPENSA ELEITORAL." para "Afastamentos (Usufrutos)"
    36: 46,  # "FÉRIAS" para "Afastamentos (Usufrutos)"
    37: 46,  # "DISPENSA ELEITORAL" para "Afastamentos (Usufrutos)"
    38: 45,  # "LICENÇA PARA ATIVIDADE POLÍTICA" para “Afastamento(Licenças)"
    39: 46,  # "FÉRIAS." para "Afastamentos (Usufrutos)"
    40: 9,  # "SUSPENSÃO DO EXPEDIENTE." para "Suspensão de expediente por Problemas no prédio/Detetização"
    41: 45,  # "LICENÇA GALA" para “Afastamento(Licenças)"
    42: 47,  # "RECESSO NATALINO." para "Feriados e Pontos Facultativos"
    43: 47,  # "RECESSO ANO NOVO" para "Feriados e Pontos Facultativos"
    44: 4,  # "PONTO NÃO REGISTRADO." para "Esquecimento no registro ponto"
    45: 39,  # "A SERVIÇO DA JUSTIÇA ELEITORAL" para "A Serviço da Justiça Eleitoral"
    46: 45,  # "LICENÇA MÉDICA" para “Afastamento(Licenças)"
    47: 19,  # "DISPENSA POR DOAÇÃO DE SANGUE" para "Doação de Sangue"
    48: 18,  # "DIA SEM ESTÁGIO" para "Outros"
    49: 18,  # "LICENÇA SEM REMUNERAÇÃO - ESTAGIÁRIOS" para "Outros"
    50: 28,  # "ATIVIDADE DISCENTE OBRIGATÓRIA" para "Atividade discente obrigatória"
    51: 18,  # "VIAGEM A SERVIÇO" para "Outros"
    52: 45,  # "LICENÇA-PRÊMIO" para “Afastamento(Licenças)"
    53: 18,  # "ESQUECEU DE REGISTRAR." para "Outros"
    54: 45,  # "ATESTADO MÉDICO." para “Afastamento(Licenças)"
    55: 18,  # "VIAGEM À SERVIÇO" para "Outros"
    56: 18,  # "EM PROCESSO DE REMOÇÃO." para "Outros"
    57: 18,  # "ATIVO" para "Outros"
    58: 34,  # "TRIBUNAL DO JÚRI" para "Participação em audiência/júri"
    59: 45,  # "ATESTADO MÉDICO" para “Afastamento(Licenças)"
    60: 18,  # "EM PROCESSO DE REMOÇÃO" para "Outros"
    61: 46,  # "RECESSO REMUNERADO." para “Afastamento(Usufrutos)”
    62: 47,  # "RECESSO NATALINO" para "Feriados e Pontos Facultativos"
}


STATUS_RELATORIO_JUST_PONTO = [
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
    STS_EFFECTIVE,
    STS_STAND_BY,
]
