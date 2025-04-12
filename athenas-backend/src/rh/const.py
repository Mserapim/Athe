# -*- coding: utf-8 -*-

DIAS_SEMANA = (
    (1, "DOMINGO"),
    (2, "SEGUNDA"),
    (3, "TERÇA"),
    (4, "QUARTA"),
    (5, "QUINTA"),
    (6, "SEXTA"),
    (7, "SÁBADO"),
)

TURNO = (
    (1, "MATUTINO"),
    (2, "VESPERTINO"),
    (3, "NOTURNO"),
    (4, "DIA INTEIRO"),
)

ENTRADA_SAIDA = (
    (1, "ENTRADA"),
    (2, "SAÍDA"),
)

OPCAO_DESLIGAMENTO = (
    (1, "A PEDIDO"),
    (2, "OFÍCIO"),
)

# TODO: MODIFICAR PARA DICIONÁRIO, VERIFICAR DEMAIS IMPLEMENTAÇÕES
TIPO_DOCUMENTO_CHOICES = {
    1: "ATO",
    2: "DECRETO",
    3: "PORTARIA",
    4: "OFÍCIO",
    5: "DESPACHO",
    6: "TERMO",
    7: "MEMORANDO",
    8: "REQUERIMENTO",
    9: "CONCESSÃO",
    10: "ACORDO COOPERAÇÃO TÉCNICA",
    11: "LEI",  # 1:'LEI',
    # 4:'PORTARIA',# modificar para 3 em publicacao
    # 7:'DESPACHO',# modificar para 5 em publicacao
    # 10:'CONCESSÃO',# modificar para 9 em publicacao
    # 11:'ATO',# modificar para 1 em publicacao
    12: "APOSTILA",
    # 13:'OFÍCIO',# modificar para 4 em publicacao
    # 14:'MEMORANDO',# modificar para 7 em publicacao
    14: "DECRETO LEGISLATIVO",  # 3:'DECRETO LEGISLATIVO',
    15: "RESOLUÇÃO",  # 5:'RESOLUÇÃO',
    16: "CIRCULAR",  # 6:'CIRCULAR',
    17: "PROCESSO",  # 8:'PROCESSO',
    # 9:'REQUERIMENTO',#modificar para 8 em publicacao
    95: "DECLARAÇÃO DE ENTRADA EM ATIVIDADE",
    98: "TERMO POSSE",
    97: "TERMO EXERCÍCIO",
    96: "TERMO LOTAÇÃO",
    99: "OUTROS",
    100: "DOCUMENTO DIGITAL",
}

TIPO_LOGRADOURO_ENDERECO_CHOICES = (
    (8, "RUA"),  # EXISTE ESOCIAL: R
    (9, "QUADRA"),  # EXISTE ESOCIAL: Q
    (1, "AVENIDA"),  # EXISTE ESOCIAL: AV
    (2, "PRAÇA"),  # EXISTE ESOCIAL: PC
    (3, "VIELA"),  # EXISTE ESOCIAL: VLA
    (4, "PONTO"),  # NÃO EXISTE ESOCIAL
    (5, "VIADUTO"),  # EXISTE ESOCIAL: VD
    (6, "ALAMEDA"),  # EXISTE ESOCIAL: AL
    (7, "OUTROS"),  # NÃO EXISTE ESOCIAL
)

MOTIVO_SUBSTITUICAO_CHOICES = ((1, "FÉRIAS"),)

TIPO_COMUNICACAO = (
    (3, "FÉRIAS"),
    (1, "RECESSO"),
    (2, "LICENÇA"),
    (4, "AUSÊNCIA DA COMARCA"),
)

TIPO_EVENTO = (
    (3, "OUTROS"),
    (2, "SEMINÁRIO"),
    (1, "CURSO DE CAPACITAÇÃO PROFISSIONAL"),
)

TIPO_PARTICIPACAO_EVENTO = (
    (1, "CONVIDADO"),
    (2, "CONVOCADO"),
    (3, "PARTICIPANTE"),
)

SITUACAO_SERVIDOR = (
    (39, "ACORDO DE COOPERAÇÃO TÉCNICA - COM ÔNUS"),
    (40, "ACORDO DE COOPERAÇÃO TÉCNICA - SEM ÔNUS"),
    (1, "AFASTADO PARA ASSOCIAÇÃO DOS MEMBROS"),
    (2, "AFASTADO PARA CARGO ELETIVO"),
    (3, "AFASTADO PARA CONCORRER A ELEIÇÃO"),
    (4, "AFASTADO PARA CURSO"),
    (5, "AFASTADO PARA O SINDICATO DA CATEGORIA"),
    (6, "APOSENTADORIA"),
    (7, "APOSENTADORIA - COMPULSÓRIA INTEGRAL"),
    (8, "APOSENTADORIA - COMPULSÓRIA PROPORCIONAL"),
    (9, "APOSENTADORIA - INTEGRAL P/ TEMPO DE SERVIÇO"),
    (10, "APOSENTADORIA - INVALIDEZ INTEGRAL"),
    (11, "APOSENTADORIA - INVALIDEZ PROPORCIONAL"),
    (12, "APOSENTADORIA - PROPORCIONAL"),
    (13, "CEDIDO A OUTRO ÓRGÃO - COM ÔNUS"),
    (14, "CEDIDO A OUTRO ÓRGÃO - COM ÔNUS - ESTÁGIO PROBATÓRIO"),
    (15, "CEDIDO A OUTRO ÓRGÃO - SEM ÔNUS"),
    (16, "CEDIDO A OUTRO ÓRGÃO - SEM ÔNUS - ESTÁGIO PROBATÓRIO"),
    (17, "DEMISSÃO"),
    (18, "EM EXERCÍCIO"),
    (19, "EM EXERCÍCIO - ESTÁGIO PROBATÓRIO"),
    (20, "EXONERAÇÃO - A PEDIDO"),
    (21, "EXONERAÇÃO - DE OFÍCIO"),
    (22, "FALECIDO"),
    (23, "FÉRIAS REMUNERADAS"),
    (24, "INATIVO"),
    (25, "LICENÇA - ELEITORAL"),
    (26, "LICENÇA - GALA"),
    (27, "LICENÇA - LUTO"),
    (28, "LICENÇA - RECLUSÃO"),
    (29, "LICENÇA - SERVIÇO MILITAR"),
    (30, "LICENÇA MATERNIDADE"),
    (31, "LICENÇA MÉDICA"),
    (32, "LICENÇA PARA ACOMP. FAMILIAR"),
    (33, "LICENÇA PATERNIDADE"),
    (34, "LICENÇA PRÊMIO"),
    (35, "LICENÇA SEM VENCIMENTO"),
    (42, "LICENÇA SEM VENCIMENTO - ESTÁGIO PROBATÓRIO"),
    (36, "REQUISITADO - COM ÔNUS"),
    (37, "REQUISITADO - SEM ÔNUS"),
    (38, "RETORNO AO ÓRGÃO DE ORIGEM"),
    (99, "OUTROS"),
)

TIPO_ANOTACAO_FERIAS = {
    "HOMOLOGACAO": "Homologação",
    "MARCACAO": "Marcação",
    "ALTERACAO": "Alteração",
    "SUSPENSAO": "Suspensão",
    "INTERRUPCAO": "Interrupção",
}

TIPO_PUBLICACAO = (
    (1, "LEI"),
    (2, "PORTARIA"),
    (3, "ATO"),
)

PERIODO_FERIAS_CHOICES = (("1", "PRIMEIRO"), ("2", "SEGUNDO"))

SEXO_CHOICES = (
    ("M", "MASCULINO"),
    ("F", "FEMININO"),
    ("N", "NÃO INFORMADO"),
)

TYPE_PHONE_HOME = 1  # "RESIDENCIAL"
TYPE_PHONE_BUSINESS = 2  # "COMERCIAL"
TYPE_PHONE_MOBILE = 3  # "CELULAR"
TYPE_PHONE_FAX = 4  # "FAX"
TYPE_PHONE_INSTITUTIONAL = 5  # "INSTITUCIONAL"
TYPE_PHONE_EMERGENCY = 6  # "CONTATO EMERGÊNCIA"

TIPO_TELEFONE_CHOICES = (
    (TYPE_PHONE_HOME, "RESIDENCIAL"),
    (TYPE_PHONE_BUSINESS, "COMERCIAL"),
    (TYPE_PHONE_MOBILE, "CELULAR"),
    (TYPE_PHONE_FAX, "FAX"),
    (TYPE_PHONE_INSTITUTIONAL, "INSTITUCIONAL"),
    (TYPE_PHONE_EMERGENCY, "CONTATO EMERGÊNCIA"),
)

SOLTEIRO = 1
CASADO = 2
VIUVO = 3
SEPARADO_JUDICIALMENTE = 4
DIVORCIADO = 5
UNIAO_ESTAVEL = 6

ESTADO_CIVIL_CHOICES = (
    (SOLTEIRO, "SOLTEIRO"),
    (CASADO, "CASADO"),
    (VIUVO, "VIUVO"),
    (SEPARADO_JUDICIALMENTE, "SEPARADO JUDICIALMENTE"),
    (DIVORCIADO, "DIVORCIADO"),
    (UNIAO_ESTAVEL, "UNIAO ESTAVEL"),
    # Estado civil do trabalhador, conforme opções abaixo:
    # 1 - Solteiro; - 1
    # 2 - Casado; - 2
    # 3 - Divorciado; - 5
    # 4 - Separado; - 4
    # 5 - Viúvo. - 3
    # Valores Válidos: 1, 2, 3, 4, 5.
)

GRAU_INSTRUCAO_CHOICES = {
    1: "ANALFABETO",
    2: "ALFABETIZADO SEM CURSOS REGULARES",
    3: "FUNDAMENTAL INCOMPLETO",
    4: "FUNDAMENTAL COMPLETO",
    5: "MÉDIO INCOMPLETO",
    6: "MÉDIO COMPLETO",
    13: "TÉCNICO",
    7: "SUPERIOR INCOMPLETO",
    8: "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL",
    9: "ESPECIALIZAÇÃO/PÓS-GRADUAÇÃO",
    10: "MESTRADO",
    11: "DOUTORADO",
    12: "PÓS-DOUTORADO",
    14: "INFORMADO",
    # Grau de instrução do trabalhador, conforme opções abaixo:
    #     01 - Analfabeto, inclusive o que, embora tenha recebido instrução, não se alfabetizou; - 1
    #     02 - Até o 5o ano incompleto do Ensino Fundamental (antiga 4a série) ou que se tenha alfabetizado sem ter frequentado
    #          escola regular;
    #     03 - 5o ano completo do Ensino Fundamental;
    #     04 - Do 6o ao 9o ano do Ensino Fundamental incompleto (antiga 5a a 8a série); - 3
    #     05 - Ensino Fundamental Completo; - 4
    #     06 - Ensino Médio incompleto; - 5
    #     07 - Ensino Médio completo; - 6
    #     08 - Educação Superior incompleta; - 7
    #     09 - Educação Superior completa; - 8
    #     10 - Pós-Graduação completa; - 9
    #     11 - Mestrado completo; - 10
    #     12 - Doutorado completo. - 11
}

GRAU_PARENTESCO_CHOICES = {
    1: "CÔNJUGE",
    2: "COMPANHEIRO",
    3: "FILHO(A)",
    4: "PAI/MÃE/AVÓS/BISAVÓS",
    5: "IRMÃO",
    6: "ENTEADO",
    7: "MENOR TUTELADO",
    8: "EX-CÔNJUGE",
    9: "NETOS",
    10: "OUTROS",
}

GRAU_PARENTESCO_DOENCA_CHOICES = {
    1: "Cônjuge/Companheiro(a)",
    2: "Pai/Mãe",
    3: "Madrasta/Padrasto",
    4: "Filho(a)",
    5: "Enteado(a)",
    6: "Dependente",
}

# TODO PEGAR INFORMAÇÕES DO CORREIO
TIPO_ENDERECO_CHOICES = (
    (1, "Residencial"),
    (2, "Comercial"),
    (3, "Institucional"),
    (4, "Profissional"),
    (5, "Via pública"),
    (6, "Não informado"),
)

ESFERA_GOVERNAMENTAL_CHOICES = (
    (1, "FEDERAL"),
    (2, "ESTADUAL"),
    (3, "MUNICIPAL"),
)

PODER_CHOICES = (
    (1, "EXECUTIVO"),
    (2, "LEGISLATIVO"),
    (3, "JUDICIÁRIO"),
    (4, "MINISTÉRIO PÚBLICO"),
    (5, "DESCONHECIDO"),
    (6, "TRIBUNAL DE CONTAS"),
)

CARGA_HORARIA_SEMANAL = (
    (20, "20"),
    (25, "25"),
    (30, "30"),
    (40, "40"),
)

CARGA_HORARIA_EVENTO = (
    (4, "04 HORAS"),
    (8, "08 HORAS"),
    (12, "12 HORAS"),
    (16, "16 HORAS"),
    (20, "20 HORAS"),
    (24, "24 HORAS"),
    (28, "28 HORAS"),
    (32, "32 HORAS"),
    (36, "36 HORAS"),
    (40, "40 HORAS"),
    (450, "450 HORAS"),
)

SIM_NAO = (
    (1, "SIM"),
    (2, "NÃO"),
)

INDICATIVO = (
    ("I", "INDEFINIDO"),
    ("E", "ESTAGIÁRIO"),
    ("M", "MEMBRO DO MINISTÉRIO PÚBLICO"),
    ("P", "MILITAR"),
    ("S", "SERVIDOR"),
    ("T", "TERCEIRIZADO"),
    ("V", "VOLUNTÁRIO"),
    ("A", "JOVEM CIDADÃO - APRENDIZ"),
    ("X", "EXTERNO SEM VÍNCULO"),
    ("O", "APOSENTADO"),
    ("R", "RESIDENTE"),
)

SANGUE = (
    (4, "A"),
    (1, "B"),
    (2, "AB"),
    (3, "O"),
)

FATOR_RH = (
    (2, "+"),
    (1, "-"),
)

RACA_COR_CHOICES = (
    (6, "BRANCA"),
    (1, "PARDA"),
    (2, "AMARELA"),
    (3, "PRETA"),
    (4, "INDÍGENA"),
    (5, "NÃO INFORMADO"),
    # Raça e cor do trabalhador, conforme opções abaixo:
    # 1 - Branca; - 6
    # 2 - Preta; - 3
    # 3 - Parda (parda ou declarada como mulata, cabocla, cafuza, mameluca ou mestiça de negro com pessoa de outra cor ou raça); - 1
    # 4 - Amarela (de origem japonesa, chinesa, coreana etc); - 2
    # 5 - Indígena; - 4
    # 6 - Não informado. - 5
    # Valores Válidos: 1, 2, 3, 4, 5, 6.
)

TIPO_DESLIGAMENTO = {
    1: "EXONERAÇÃO EFETIVO",
    2: "EXONERAÇÃO COMISSIONADO",
    3: "EXONERAÇÃO ESTABILIZADO - SERA EXCLUIDO",
    4: "APOSENTADORIA POR INVALIDEZ",
    5: "APOSENTADORIA VOLUNTÁRIA - SERA EXCLUIDO",
    14: "APOSENTADORIA COMPULSÓRIA",
    15: "APOSENTADORIA ESPECIAL - SERA EXCLUIDO",
    16: "APOSENTADORIA POR TEMPO DE CONTRIBUIÇÃO",
    17: "APOSENTADORIA POR IDADE",
    6: "POSSE EM OUTRO CARGO",
    7: "FALECIMENTO",
    8: "RESCISÃO - SERA EXCLUIDO",
    9: "DEMISSÃO",
    10: "RESERVA REFORMA - SERA EXCLUIDO",
    11: "DISPONIBILIDADE - SERA EXCLUIDO",
    12: "PROMOÇÃO/REMOÇÃO",
    13: "FIM REQUISIÇÃO/ACORDO COOPERAÇÃO",
    18: "REDISTRIBUIÇÃO",
    19: "REVERSÃO DE REINTEGRAÇÃO",
    20: "FIM DE MANDATO",
    21: "FIM TSVE",
    22: "FIM DE CONTRATO",
    23: "REVISÃO DE BENEFÍCIO",
    24: "TÉRMINO BENEFÍCIO",
    # 01  Rescisão com justa causa, por iniciativa do empregador
    # 02  Rescisão sem justa causa, por iniciativa do empregador
    # 03  Rescisão antecipada do contrato a termo por iniciativa do empregador
    # 04  Rescisão antecipada do contrato a termo por iniciativa do empregado
    # 05  Rescisão por culpa recíproca
    # 06  Rescisão por término do contrato a termo
    # 07  Rescisão do contrato de trabalho por iniciativa do empregado
    # 08  Rescisão do contrato de trabalho por interesse do(a) empregado(a), nas  hipóteses previstas nos arts. 394 e 483, § 1º da CLT
    # 09  Rescisão  por  falecimento  do  empregador  individual  ou  empregador  doméstico  por  opção  do empregado
    # 10  Rescisão por falecimento do empregado
    # 11  Transferência de empregado para empresa do mesmo grupo empresarial que tenha assumido os encargos trabalhistas, sem que tenha
    #     havido rescisão do contrato de trabalho
    # 12  Transferência  de  empregado  da  empresa  consorciada  para  o  consórcio  que  tenha  assumido  os encargos trabalhistas, e
    #     vice-versa, sem que tenha havido rescisão do contrato de trabalho
    # 13  Transferência  de  empregado  de  empresa  ou  consórcio,  para  outra  empresa  ou  consórcio  que tenha assumido os encargos
    #     trabalhistas por motivo de sucessão (fusão, cisão ou incorporação), sem que tenha havido rescisão do contrato de trabalho
    # 14  Rescisão  do  contrato  de  trabalho  por  encerramento  da  empresa,  de  seus  estabelecimentos  ou supressão de parte de suas
    #     atividades ou falecimento do empregador individual ou empregador doméstico sem continuação da atividade
    # 15  Demissão de Aprendizes por Desempenho Insuficiente ou Inadaptação
    # 16  Declaração  de  nulidade  do  contrato  de  trabalho  por  infringência  ao  inciso  II  do  art.  37  da Constituição Federal,
    #     quando mantido o direito ao salário
    # 17  Rescisão Indireta do Contrato de Trabalho
    # 18  Aposentadoria Compulsória (somente para categorias de trabalhadores 301 a 309)
    # 19  Aposentadoria por idade (somente para categorias de trabalhadores 301 a 309)
    # 20  Aposentadoria por idade e tempo de contribuição (somente categorias 301 a 309)
    # 21  Reforma Militar (somente para categorias de trabalhadores 301 a 309)
    # 22  Reserva Militar (somente para categorias de trabalhadores 301 a 309)
    # 23  Exoneração (somente para categorias de trabalhadores 301 a 309)
    # 24  Demissão (somente para categorias de trabalhadores 301 a 309)
    # 25  Vacância para assumir outro cargo efetivo (somente para categorias de trabalhadores 301 a 309)
    # 26  Rescisão   do   contrato   de   trabalho   por   paralisação   temporária   ou   definitiva   da   empresa, estabelecimento ou
    #     parte das atividades motivada por atos de autoridade municipal, estadual ou federal
    # 27  Rescisão por motivo de força maior
    # 28  Término da Cessão/Requisição
    # 29  Redistribuição
    # 30  Mudança de Regime Trabalhista
    # 31  Reversão de Reintegração
    # 32  Extravio de Militar
}

TIPO_APOSENTADORIA = {
    1: "COMPULSÓRIA",
    2: "ESPECIAL",
    3: "IMPLEMENTO DE IDADE",
    4: "INVALIDEZ",
    5: "TEMPO DE CONTRIBUIÇÃO",
    6: "VOLUNTÁRIA",
}

RULES = {
    1: "Art. 3º, da EC nº 47/05",
    2: "Art. 40º, § 1º, III, b, da Constituição Federal",
    3: "Art. 10º, § 1º, I, da  EC nº 103/19",
    4: "Art. 4º da EC nº 103/19",
    5: "Regra Geral: Fundamento Art. 40, § 1°, III, a, da CF.",
    6: "Art. 8, I e III, a e b, da EC nº 20/98 (vigente até 31/12/2003)",
    7: "Art. 8º, § 1º, I, a e b, da EC nº 20/98 (Vigente até 31.12.03)",
    8: "Art. 2º, I a III, a e b, da EC nº 41/03",
    9: "Art. 6º, da EC nº 41/03",
    10: "Art. 20 da  EC nº 103/19",
}

ORIGEM = 1
REQUISITANTE = 2
ORIGEM_REQUISITANTE = 3

TIPO_ONUS = (
    (ORIGEM, "ORIGEM"),
    (REQUISITANTE, "REQUISITANTE"),
    (ORIGEM_REQUISITANTE, "Cedente e Cessionário"),
)

ONUS_PAYMENT_EMPLOYER = 1
ONUS_PAYMENT_REQUESTER = 1
ONUS_PAYMENT_BOTH = 1

ONUS_PAYMENT = {
    ONUS_PAYMENT_EMPLOYER: "Apenas do Empregador",
    ONUS_PAYMENT_REQUESTER: "Apenas do Sindicato",
    ONUS_PAYMENT_BOTH: "Parte do Empregador, sendo a diferença e/ou complementação salarial paga pelo Sindicato",
}

TIPO_NIVEL_ESCOLARIDADE = (
    (1, "FUNDAMENTAL"),
    (2, "MÉDIO"),
    (3, "SUPERIOR"),
    (4, "ELEMENTAR"),
    (5, "POS GRADUAÇÃO"),
)

TIPO_CARGA_HORARIA = (
    (1, "SEMANAL"),
    (2, "MENSAL"),
)

TIPO_LEI_CARGO = (
    ("EF", "EFETIVO"),
    ("CM", "COMISSÃO"),
    ("FC", "FUNÇÃO DE CONFIANÇA"),
    ("AC", "ACORDO DE COOPERAÇÃO TÉCNICA"),
    ("ES", "ESTAGIÁRIO"),
    ("EL", "ELETIVO"),
    ("TE", "TERCEIRIZADO"),
    ("VL", "VOLUNTÁRIO"),
    ("JC", "JOVEM CIDADÃO - APRENDIZ"),
    ("EX", "EXTERNO - SEM VÍNCULO"),
    ("AP", "APOSENTADO"),
    ("RS", "RESIDENTE"),
)

MOTIVO_SUBSTITUICAO = (
    (1, "FÉRIAS"),
    (2, "LICENÇA"),
    (3, "RECESSO NATALINO"),
    (4, "PLANTÃO"),
    (5, "VIAGEM A TRABALHO"),
    (6, "DESEMPENHO DE FUNÇÃO"),
    (7, "DISPOSIÇÃO DE OUTRO ÓRGÃO"),
    (8, "REPRESENTAÇÃO DE CLASSE"),
    (9, "ATUAÇÃO DE GRUPO DE TRABALHO"),
    (10, "TRÂNSITO/PROMOÇÃO/REMOÇÃO"),
    (12, "SUSPENSÃO"),
)

TIPO_AFASTAMENTO_CHOICES = (
    (1, "A DISPOSIÇÃO COM ÔNUS PARA O REQUISITANTE"),
    (2, "A DISPOSIÇÃO COM ÔNUS PARA A ORIGEM"),
    (3, "LICENÇA PARA TRATAR DE INTERESSES PARTICULARES"),
    (4, "LICENÇA PARA ACOMPANHAMENTO DE CÔNJUGE"),
    (5, "AFASTAMENTO PARA EXERCÍCIO DE MANDADO ELETIVO"),
    (6, "REPRESENTAÇÃO SINDICAL"),
)

MOTIVO_VACANCIA = (
    (1, "EXONERAÇÃO"),
    (2, "DEMISSÃO"),
    (3, "READAPTAÇÃO"),
    (4, "APOSENTADORIA"),
    (5, "POSSE EM OUTRO CARGO INACUMULÁVEL"),
    (6, "FALECIMENTO"),
)

MOTIVO_REMOCAO = (
    (1, "OFÍCIO"),
    (2, "REQUERIMENTO"),
    (3, "PERMUTA"),
    # (4, 'OUTROS')
)

MOTIVO_REDISTRIBUICAO = (
    (1, "OFÍCIO"),
    (2, "DISPONIBILIDADE"),
    (3, "DISPONIBILIDADE PROVISÓRIA"),
)

VEICULO_PUBLICACAO = (
    (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
    (30, "DIARIO OFICIAL DA UNIAO"),
    (28, "DIARIO JUSTICA"),
    (29, "DIARIO JUSTICA ELEITORAL"),
    (1, "DOE ACRE"),
    (2, "DOE AMAPA"),
    (3, "DOE AMAZONAS"),
    (13, "DOE BAHIA"),
    (8, "DOE CEARA"),
    (26, "DOE DISTRITO FEDERAL"),
    (18, "DOE ESPIRITO SANTO"),
    (25, "DOE GOIAS"),
    (6, "DOE PARA"),
    (21, "DOE PARANA"),
    (11, "DOE PARAIBA"),
    (10, "DOE PERNAMBUCO"),
    (15, "DOE PIAUI"),
    (27, "DOE MATO GROSSO"),
    (24, "DOE MATO GROSSO DO SUL"),
    (14, "DOE MARANHAO"),
    (16, "DOE MINAS GERAIS"),
    (19, "DOE RIO DE JANEIRO"),
    (9, "DOE RIO GRANDE DO NORTE"),
    (23, "DOE RIO GRANDE DO SUL"),
    (4, "DOE RORAIMA"),
    (5, "DOE RONDONIA"),
    (22, "DOE SANTA CATARINA"),
    (17, "DOE SAO PAULO"),
    (12, "DOE SERGIPE"),
    (7, "DOE TOCANTINS"),
    (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
    (33, "PLACAR"),
)

MESES = (
    ("01", "JANEIRO"),
    ("02", "FEVEREIRO"),
    ("03", "MARÇO"),
    ("04", "ABRIL"),
    ("05", "MAIO"),
    ("06", "JUNHO"),
    ("07", "JULHO"),
    ("08", "AGOSTO"),
    ("09", "SETEMBRO"),
    ("10", "OUTUBRO"),
    ("11", "NOVEMBRO"),
    ("12", "DEZEMBRO"),
)

QUADRIMESTRE_CHOICES = (
    (1, "1º QUADRIMESTRE"),
    (2, "2º QUADRIMESTRE"),
    (3, "3º QUADRIMESTRE"),
)

TIPO_ATO_SICAP = {
    1: "LEI",
    2: "DECRETO",
    3: "DECRETO LEGISLATIVO",
    4: "PORTARIA",
    5: "RESOLUÇÃO",
    6: "CIRCULAR",
    7: "DESPACHO",
    8: "PROCESSO",
    9: "SEM ATO",
    10: "ATO",
    99: "OUTROS",
}


document_to_sicap = {
    1: 10,  # 'ATO',
    2: 2,  # 'DECRETO',
    3: 4,  # 'PORTARIA',
    5: 7,  # 'DESPACHO',
    11: 1,  # 'LEI',#1:'LEI',
    14: 3,  # 'DECRETO LEGISLATIVO',#3:'DECRETO LEGISLATIVO',
    15: 5,  # 'RESOLUÇÃO',#5:'RESOLUÇÃO',
    16: 6,  # 'CIRCULAR',#6:'CIRCULAR',
    17: 8,  # 'PROCESSO',#8:'PROCESSO',
    99: 99,  # 'OUTROS',
}

TITULO_ELEITOR = 1
CNH = 2
CTPS = 3
PIS_PASEP = 6
NIS = 5
IPSEP = 7
INSS = 8
RESERVISTA = 9
PROFESSIONAL_COUNCIL = CONSELHO_PROFISSIONAL = 10
RIC = 11
RNE = 12
CPF = 13
RG = 14
PASSPORT = 15
STABLE_BONDING = 54

DOCUMENTO_CHOICES = {
    TITULO_ELEITOR: "TÍTULO DE ELEITOR",
    CNH: "CNH",
    CTPS: "CTPS",
    PIS_PASEP: "PIS/PASEP",
    NIS: "NIS",
    IPSEP: "IPSEP",
    INSS: "INSS",
    RESERVISTA: "RESERVISTA",
    CONSELHO_PROFISSIONAL: "CONSELHO PROFISSIONAL",
    RIC: "RIC",
    RNE: "RNE",
    CPF: "CPF",
    RG: "RG",
    PASSPORT: "PASSAPORTE",
    STABLE_BONDING: "UNIAO ESTAVEL",
}

TITULO_ELEITOR_ZONA = 1
TITULO_ELEITOR_SECAO = 2
TITULO_ELEITOR_UF = 3
TITULO_ELEITOR_MUNICIPIO = 7
CNH_CATEGORIA = 4
CNH_FIRST_DATE = 12
RESERVISTA_CLASSE = 5
CTPS_SERIE = 6
CTPS_UF = 8
RIC_ISSUER = 9
RNE_ISSUER = 10
PROFESSIONAL_COUNCIL_ISSUER = 11
RG_ISSUER = 13

ESPECIFICIDADE_DOCUMENTO_CHOICES = {
    TITULO_ELEITOR_ZONA: "TÍTULO DE ELEITOR.ZONA",
    TITULO_ELEITOR_SECAO: "TÍTULO DE ELEITOR.SEÇÃO",
    TITULO_ELEITOR_UF: "TÍTULO DE ELEITOR.UF",
    TITULO_ELEITOR_MUNICIPIO: "TÍTULO DE ELEITOR.MUNICIPIO",
    CNH_CATEGORIA: "CNH.CATEGORIA",
    RESERVISTA_CLASSE: "RESERVISTA.CLASSE",
    CTPS_SERIE: "CTPS.SERIE",
    CTPS_UF: "CTPS.UF",
    RIC_ISSUER: "RIC.EMISSOR",
    RNE_ISSUER: "RNE.EMISSOR",
    PROFESSIONAL_COUNCIL_ISSUER: "CONSELHO PROFISSIONAL.EMISSOR",
    CNH_FIRST_DATE: "CNH.DATA PRIMEIRA HABILITAÇÃO",
    RG_ISSUER: "RG.ÓRGÃO DE EXPEDIÇÃO",
}

BIRTH_CERTIFICATE = 50
WEDDING_CERTIFICATE = 51
ADDRESS_CERTIFICATE = 52
CHILD_CUSTODY_TERM = 53

DIGITAL_DOCUMENT_TYPE = DOCUMENTO_CHOICES
DIGITAL_DOCUMENT_TYPE.update(
    {
        BIRTH_CERTIFICATE: "CERTIDÃO DE NASCIMENTO",
        WEDDING_CERTIFICATE: "CERTIDÃO DE CASAMENTO",
        ADDRESS_CERTIFICATE: "COMPROVANTE DE ENDEREÇO",
        CHILD_CUSTODY_TERM: "TERMO DE CUSTÓDIA DE MENOR",
        STABLE_BONDING: "TERMO DE UNIÃO ESTÁVEL",
    }
)

CNH_CATEGORY_A = 1
CNH_CATEGORY_B = 2
CNH_CATEGORY_C = 3
CNH_CATEGORY_D = 4
CNH_CATEGORY_E = 5
CNH_CATEGORY_AB = 6
CNH_CATEGORY_AC = 7
CNH_CATEGORY_AD = 8
CNH_CATEGORY_AE = 9

CNH_CATEGORY_TYPE = {
    CNH_CATEGORY_A: "A",
    CNH_CATEGORY_B: "B",
    CNH_CATEGORY_C: "C",
    CNH_CATEGORY_D: "D",
    CNH_CATEGORY_E: "E",
    CNH_CATEGORY_AB: "AB",
    CNH_CATEGORY_AC: "AC",
    CNH_CATEGORY_AD: "AD",
    CNH_CATEGORY_AE: "AE",
}

MOTIVO_INICIO_DEPENDENCIA = {
    0: "OUTROS",
    1: "NASCIMENTO",
    2: "ADOÇÃO",
    3: "FILHO PÓSTUMO",
    4: "TUTELA DO MENOR",
    5: "DECISÃO JUDICIAL",
    6: "INVALIDEZ",
    7: "CASAMENTO",
    8: "UNIÃO ESTÁVEL",
    9: "DEPENDÊNCIA ECONÔMICA",
}

MOTIVO_FIM_DEPENDENCIA = {
    0: "OUTROS",
    1: "MAIORIDADE",
    2: "EMANCIPAÇÃO",
    3: "DECISÃO JUDICIAL",
    4: "ÓBITO",
    5: "SEPARAÇÃO JUDICIAL",
    6: "INDEPENDÊNCIA ECONÔMICA",
    7: "CESSAÇÃO DE INVALIDEZ",
}

TIPO_DEPENDENTE = {
    1: "CÔNJUGE",
    2: "COMPANHEIRO(A)",
    3: "FILHO(A) NÃO EMANCIPADO MENOR DE 21 ANOS",
    4: "FILHO INVÁLIDO(A)",
    5: "PAI(MÃE) COM DEPENDÊNCIA ECONÔMICA",
    6: "IRMÃO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA",
    7: "IRMÃO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA",
    8: "ENTEADO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA",
    9: "ENTEADO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA",
    10: "MENOR TUTELADO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA",
    11: "MENOR TUTELADO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA",
    12: "OUTROS",
    # 01  Cônjuge - 1
    # 02  Companheiro(a)  com  o(a)  qual  tenha  filho  ou  viva  há  mais  de  5  (cinco)  anos  ou  possua Declaração de
    #     União Estável - 2
    # 03  Filho(a) ou enteado(a) - ?
    # 04  Irmão(ã), neto(a) ou bisneto(a) sem arrimo dos pais, do(a) qual detenha a guarda judicial
    # 05  Pais, avós e bisavós - ?
    # 06  Menor pobre do qual detenha a guarda judicial - ?
    # 07  A pessoa absolutamente incapaz, da qual seja tutor ou curador - ?
    # 08  Filho(a)  ou  enteado(a)  universitário(a)  ou  cursando  escola  técnica  de  2º  grau,  até  24  (vinte  e quatro) anos - ?
    # 15  Ex-cônjuge - ?
    # 99  Agregado/Outros - ?
}

IMPOSTO_RENDA = 1
SALARIO_FAMILIA = 3
PLANSAUDE = 2
AUXILIO_CRECHE = 4
PREVIDENCIA = 5
AUXILIO_ESPECIAL = 6

TIPO_DEPENDENCIA = {
    IMPOSTO_RENDA: "Imposto de Renda",
    SALARIO_FAMILIA: "Salário Família",
    PLANSAUDE: "PlanSaúde",
    AUXILIO_CRECHE: "Auxílio Creche",
    PREVIDENCIA: "Previdência",
    AUXILIO_ESPECIAL: "Auxílio Especial",
}

CAPACIDADE = {
    1: "VÁLIDO",
    2: "INVÁLIDO",
}

TIPO_MOVIMENTACAO_CARREIRA = {
    "NOMEACAO": "Nomeação",
    "APROVEITAMENTO": "Aproveitamento",
    "READAPTACAO": "Readaptação",
    "RECONDUCAO": "Recondução",
    "REINTEGRACAO": "Reintegração",
    "REVERSAO": "Reversão",
    "TITULARIZACAO": "Titularização",
    "PROGRESSAO": "Progressão",
    "ENQUADRAMENTO": "Enquadramento",
    "REMOCAO": "Remoção",
    "PROMOCAO": "Promoção",
    "REQUISICAO": "Requisição",
    "POSSE_ESTAGIARIO": "Posse Estagiário",
    "POSSE_RESIDENTE": "Posse Residente",
    "POSSE_COLABORADOR": "Posse Colaborador",
    "BENEFICIO": "Benefício Previdenciário",
}

CRITERIO_PROVIMENTO = {
    1: "ANTIGUIDADE",
    2: "MERECIMENTO",
    3: "PERMUTA",
}

CONFIG_BANDS_TRANSPARENCIA = {
    1: "Remuneração Base Bruta",
    2: "Adicional de Férias",
    3: "IRRF",
    4: "Previdência Social",
    5: "Aux. Alimentação",
    6: "Aux. Creche",
    7: "Aux. Transporte",
}

CATEGORIA_SERVIDOR = {
    "VOLUNTARIO": "Voluntário",
    "TERCEIRIZADO": "Terceirizado",
    "ESTAGIARIO": "Estagiário",
    "JOVEM_CIDADAO": "Jovem Cidadão - Aprendiz",
    "SERVIDOR_QUADRO": "Servidor - Quadro",
    "SERVIDOR_EXTRAQUADRO": "Servidor - Extraquadro",
    "SERVIDOR_EXTRA_REQUISITADO": "Servidor - Extraquadro requisitado",
    "SERVIDOR_EXTRA_REQUISITADO_ONUS": "Servidor - Extraquadro requisitado com ônus",
    "SERVIDOR_EXTRA_REQUISITADO_AC_ONUS": "Servidor - Extraquadro - Acordo Cooperação Técnica com ônus",
    "SERVIDOR_EXTRA_REQUISITADO_AC": "Servidor - Extraquadro - Acordo Cooperação Técnica sem ônus",
    "MEMBRO": "Membro",
    "MEMBRO_SUBS": "Membro - Promotor de Justiça Substituto",
    "MEMBRO_1ENT": "Membro - Promotor de Justiça 1ª Entrância",
    "MEMBRO_2ENT": "Membro - Promotor de Justiça 2ª Entrância",
    "MEMBRO_3ENT": "Membro - Promotor de Justiça 3ª Entrância",
    "MEMBRO_PROCURADOR": "Membro - Procurador de Justiça",
}

TYPE_VACATION = 5  #: 'FeriasAfastamento'
TYPE_TRAVEL = 6  # 'Viagem'
TYPE_RECESS = 7  #: 'Recesso'
TYPE_HEALTH3DAYS = 9  #: 'LicencaSaude3Dias'
TYPE_HEALTH_MEDICAL_BOARD = 10  #: 'LicencaSaudeJuntaMedica'
TYPE_HEALTH_FAMILY_DESEASE = 11  #: 'LicencaDoencaPessoaFamilia'
TYPE_MATERNITY_LICENSE = 12
TYPE_LICENSE_ADOPTION = 13  #: 'LicencaAdocao'
TYPE_LICENSE_SPOUSE = 14  #: 'LicencaAfastamentoConjuge'
TYPE_LICENSE_MILITARY_SERVICE = 15  #: 'LicencaServicoMilitar'
TYPE_LICENSE_POLITICAL_ACTIVITIES = 16  #: 'LicencaAtividadePolitica'
TYPE_LICENSE_TRAINING = 17  #: 'LicencaCapacitacao'
TYPE_LICENSE_SPECIAL_INTEREST = 18  #: 'LicencaInteresseParticular'
TYPE_LICENSE_MANDATE_CLASSIST = 19  #: 'LicencaMandatoClassista'
TYPE_DEPARTURE_OTHER_ORGAN = 20  #: 'AfastamentoOutroOrgao'
TYPE_DEPARTURE_MANDATE_ELECTIVE = 21  #: 'AfastamentoMandatoEletivo'
TYPE_DEPARTURE_STUDY = 22  #: 'AfastamentoEstudar'
TYPE_DEPARTURE_MISSION = 23  #: 'AfastamentoMissao'
TYPE_DEPARTURE_ELECTORAL = 24  #: 'AfastamentoEleitoral'
TYPE_DEPARTURE_SERVE_JURY = 25  #: 'AfastamentoServirJuri'
TYPE_DEPARTURE_TRAINING = 26  #: 'AfastamentoTreinamento'
TYPE_DEPARTURE_DISPLACEMENT = 27  #: 'AfastamentoDeslocamento'
TYPE_DEPARTURE_COMPETITION = 28  #: 'AfastamentoCompeticao'
TYPE_DEPARTURE_COURSE_CONTEST = 29  #: 'AfastamentoCursoConcurso'
TYPE_DEPARTURE_PRISION = 30  #: 'AfastamentoPrisao'
TYPE_ABSENCE_BLOOD_DONATION = 31  #: 'AusenciaDoacaoSangue'
TYPE_ABSENCE_ELECTORAL = 32  #: 'AusenciaEleitor'
TYPE_ABSENCE_MARRIAGE = 33  #: 'AusenciaCasamento'
TYPE_ABSENCE_BIRTH = 34  #: 'AusenciaNascimento'
TYPE_ABSENCE_DEATH = 35  #: 'AusenciaFalecimento'
TYPE_ABSENCE_CONCLUSION = 36  #: 'AusenciaConclusao'
TYPE_HEALTH30DAYS = 37  #: 'LicencaSaude30Dias'
TYPE_ELECTORAL_FLEX = 38  #: 'FolgaEleitoral'
TYPE_WORK_GROUP = 39  #: 'AtuacaoGrupoTrabalho'
TYPE_NEW_FUNCTION = 40  #: 'DesempenhoFuncao'
TYPE_ORDELY = 41  #: 'Plantao'
TYPE_COMPENSATION_LOW = 42  #: 'FolgaCompensacao'
TYPE_FULL_BIRTHDAY = 43  #: 'FolgaAniversario'
TYPE_DEPARTURE_SUSPENSION = 44  #: 'AfastamentoSuspensao'
TYPE_DEPARTURE_DISMISSAL_JUDGMENT = 45  #: 'AfastamentoComparecimentoJuizo'
TYPE_DEPARTURE_AVAILABILITY = 46  #: 'AfastamentoDisponibilidade'
TYPE_BANK_HOURS = 47  #: 'BancoDeHoras'
TYPE_HEALTH_PREVENT = 48
TYPE_AWARD_LICENSE = 59
TYPE_DEPARTURE_CANDIDATURE = 60  #: 'AfastamentoCandidatura'
TYPE_DEPARTURE_PARCIAL_STUDY = 61  #: 'AfastamentoParcialEstudar'
TYPE_DEPARTURE_ADM_INQUIRY = 62  #: 'AfastamentoSindicanciaAdm'
TYPE_HEALTHHOURS = 63  #: 'LicencaSaudeHoras'
TYPE_DOENCA_PESSOA_FAMILIA_JUNTA_MEDICA = 64

TIPO_BASE_LICENCA_AFASTAMENTO = {
    1: "BaseLicencaAfastamento",
    2: "Afastamento",
    3: "Licenca",
    4: "Ausencia",
    8: "LicencaSaude",
    TYPE_VACATION: "FeriasAfastamento",
    TYPE_TRAVEL: "Viagem",
    TYPE_RECESS: "Recesso",
    TYPE_HEALTH3DAYS: "LicencaSaude3Dias",
    TYPE_HEALTH30DAYS: "LicencaSaude30Dias",
    TYPE_HEALTH_MEDICAL_BOARD: "LicencaSaudeJuntaMedica",
    TYPE_HEALTH_FAMILY_DESEASE: "LicencaDoencaPessoaFamilia",
    TYPE_MATERNITY_LICENSE: "LicencaMaternidade",
    TYPE_LICENSE_ADOPTION: "LicencaAdocao",
    TYPE_LICENSE_SPOUSE: "LicencaAfastamentoConjuge",
    TYPE_LICENSE_MILITARY_SERVICE: "LicencaServicoMilitar",
    TYPE_LICENSE_POLITICAL_ACTIVITIES: "LicencaAtividadePolitica",
    TYPE_LICENSE_TRAINING: "LicencaCapacitacao",
    TYPE_LICENSE_SPECIAL_INTEREST: "LicencaInteresseParticular",
    TYPE_LICENSE_MANDATE_CLASSIST: "LicencaMandatoClassista",
    TYPE_DEPARTURE_AVAILABILITY: "AfastamentoDisponibilidade",
    TYPE_DEPARTURE_OTHER_ORGAN: "AfastamentoOutroOrgao",
    TYPE_DEPARTURE_MANDATE_ELECTIVE: "AfastamentoMandatoEletivo",
    TYPE_DEPARTURE_STUDY: "AfastamentoEstudar",
    TYPE_DEPARTURE_MISSION: "AfastamentoMissao",
    TYPE_DEPARTURE_ELECTORAL: "AfastamentoEleitoral",
    TYPE_DEPARTURE_SERVE_JURY: "AfastamentoServirJuri",
    TYPE_DEPARTURE_TRAINING: "AfastamentoTreinamento",
    TYPE_DEPARTURE_DISPLACEMENT: "AfastamentoDeslocamento",
    TYPE_DEPARTURE_COMPETITION: "AfastamentoCompeticao",
    TYPE_DEPARTURE_COURSE_CONTEST: "AfastamentoCursoConcurso",
    TYPE_DEPARTURE_PRISION: "AfastamentoPrisao",
    TYPE_DEPARTURE_SUSPENSION: "AfastamentoSuspensao",
    TYPE_DEPARTURE_DISMISSAL_JUDGMENT: "AfastamentoComparecimentoJuizo",
    TYPE_DEPARTURE_CANDIDATURE: "AfastamentoCandidatura",
    TYPE_DEPARTURE_ADM_INQUIRY: "AfastamentoSindicanciaAdm",
    TYPE_ABSENCE_BLOOD_DONATION: "AusenciaDoacaoSangue",
    TYPE_ABSENCE_ELECTORAL: "AusenciaEleitor",
    TYPE_ABSENCE_MARRIAGE: "AusenciaCasamento",
    TYPE_ABSENCE_BIRTH: "AusenciaNascimento",
    TYPE_ABSENCE_DEATH: "AusenciaFalecimento",
    TYPE_ABSENCE_CONCLUSION: "AusenciaConclusao",
    TYPE_ELECTORAL_FLEX: "FolgaEleitoral",
    TYPE_WORK_GROUP: "AtuacaoGrupoTrabalho",
    TYPE_NEW_FUNCTION: "DesempenhoFuncao",
    TYPE_ORDELY: "Plantao",
    TYPE_COMPENSATION_LOW: "FolgaCompensacao",
    TYPE_FULL_BIRTHDAY: "FolgaAniversario",
    TYPE_BANK_HOURS: "BancoDeHoras",
    TYPE_HEALTH_PREVENT: "HealthPrevent",
    TYPE_AWARD_LICENSE: "AwardLicense",
    TYPE_HEALTHHOURS: "LicencaSaudeHoras",
}

AGENDADO = 1
ATIVO = 2
ENCERRADO = 3
CANCELADO = 4


SCHEDULED = AGENDADO
ACTIVE = ATIVO
FINISHED = ENCERRADO
CANCELED = CANCELADO

ESTADO_BASE_LICENCA_AFASTAMENTO = {
    SCHEDULED: "AGENDADO",
    ACTIVE: "ATIVO",
    FINISHED: "ENCERRADO",
    CANCELED: "CANCELADO",
}

REVOGACAO = 1
ALTERACAO = 2
SUSPENSION = SUSPENSAO = 3
INTERRUPTION = INTERRUPCAO = 5

ALTERACAO_BASE_LICENCA_AFASTAMENTO = {
    REVOGACAO: "Revogação",
    ALTERACAO: "Alteração a pedido",
    SUSPENSAO: "Suspensão",
    INTERRUPCAO: "Interrupção",
    CANCELED: "Cancelado",
}

CARGO_ELETIVO_CHOICES = {
    1: "Prefeito/Vice",
    2: "Vereador",
    3: "Deputado Estadual",
    4: "Deputado Federal",
    5: "Governador/Vice",
    6: "Senador/Presidente República/Vice",
}

MANDATO_CLASSISTA_TIPO_ENTIDADE_CHOICES = {
    1: "Confederação",
    2: "Federação",
    3: "Associação Classe Nacional",
    4: "Associação Classe Estadual",
    5: "Sindicato e Entidade Fiscalizadora da Profissão",
}

TURNO_ELEITORAL = {1: "1º", 2: "2º", 3: "1º e 2º"}

STATUS_ESTAGIO = {
    1: "Em Andamento",
    2: "Aguardando Homologação",
    3: "Julgamento Comissão",
    4: "Homologado",
}

NAO_INFORMADA = 1
DEFERIDA = 2
INDEFERIDA = 3

TIPO_APROVACAO = {
    NAO_INFORMADA: "Não informada",
    DEFERIDA: "Deferida",
    INDEFERIDA: "Indeferida",
}

# ATIVO = 2
# ENCERRADO = 3
AFASTADO = 5
MOVED_AWAY = AFASTADO

SERVIDOR_LOTACAO_ESTADO = {
    ACTIVE: "ATIVO",
    MOVED_AWAY: "AFASTADO",
    FINISHED: "ENCERRADO",
}

REGIME_PREVIDENCIARIO = {1: "RGPS", 2: "RPPS", 3: "MILITAR"}

MASS_SEGREGATION_PLAN = {
    1: 1,  # Fundo em capitalização
    2: 2,  # Fundo em repartição
    3: 3,  # Mantido pelo tesouro
    4: 0,  # 'Sem segregação de massa'
}

WORKPLACE = 1
WORK_ASSIGNMENT = 2

WORKPLACE_CHOICE = {WORKPLACE: "Lotação", WORK_ASSIGNMENT: "Designação de Exercício"}

LICENSE_SEND_TO_SICAP = {
    9: "LicencaSaude3Dias",
    37: "LicencaSaude30Dias",
    10: "LicencaSaudeJuntaMedica",
    11: "LicencaDoencaPessoaFamilia",
    12: "LicencaMaternidade",
    13: "LicencaAdocao",
    14: "LicencaAfastamentoConjuge",
    15: "LicencaServicoMilitar",
    16: "LicencaAtividadePolitica",
    17: "LicencaCapacitacao",
    18: "LicencaInteresseParticular",
    19: "LicencaMandatoClassista",
}

FISICA = 1
VISUAL = 2
AUDITIVA = 3
MENTAL = 4
INTELECTUAL = 5

TIPO_DEFICIENCIA = {
    FISICA: "Deficiência Física",
    VISUAL: "Deficiência Visual",
    AUDITIVA: "Deficiência Auditiva",
    MENTAL: "Deficiência Mental",
    INTELECTUAL: "Deficiência Intelectual",
}

INDICATIVO_ADMISSAO = {
    1: "Normal",
    2: "Decorrente de ação fiscal",
    3: "Decorrente de decisão judicial",
}

ACIDENTE_TRANSITO_ATROPELAMENTO = 1
ACIDENTE_TRANSITO_COLISAO = 2
ACIDENTE_TRANSITO_OUTROS = 3

ACIDENTE_TRANSITO = {
    ACIDENTE_TRANSITO_ATROPELAMENTO: "Atropelamento",
    ACIDENTE_TRANSITO_COLISAO: "Colisão",
    ACIDENTE_TRANSITO_OUTROS: "Outros",
}

CUMULATIVE_NOT = 1
CUMULATIVE_PROFESSIONAL_HEALTH = 2
CUMULATIVE_PROFESSOR = 3
CUMULATIVE_TECHNICIAN = 4

CUMULATIVE = {
    CUMULATIVE_NOT: "NÃO ACUMULÁVEL",
    CUMULATIVE_PROFESSIONAL_HEALTH: "PROFISSIONAL DE SAÚDE",
    CUMULATIVE_PROFESSOR: "PROFESSOR",
    CUMULATIVE_TECHNICIAN: "TÉCNICO/CIENTÍFICO",
}


TYPE_INTERVAL_FIXED = 1
TYPE_INTERVAL_VARIABLE = 2

TYPE_INTERVAL = {TYPE_INTERVAL_FIXED: "FIXO", TYPE_INTERVAL_VARIABLE: "VARIÁVEL"}

TYPE_RACE_CHOICE = {
    1: "PARDA",
    2: "AMARELA",
    3: "PRETA",
    4: "INDÍGENA",
    5: "NÃO INFORMADO",
    6: "BRANCA",
}

PHYSICAL = 1
VISUAL = 2
AUDITIVE = 3
MENTAL = 4
INTELLECTUAL = 5

DEFICIENCY_TYPE = {
    PHYSICAL: "Física",
    VISUAL: "Visual",
    AUDITIVE: "Auditiva",
    MENTAL: "Mental",
    INTELLECTUAL: "Intelectual",
}

DEPENDENCY_INCOME_TAX = 1  # "Imposto de Renda",
DEPENDENCY_HEALTH_PLAN = 2  # "PlanSaúde",
DEPENDENCY_SALARY_FAMILY = 3  # "Salário Família",
DEPENDENCY_AID_CRECHE = 4  # "Auxílio Creche",
DEPENDENCY_PENSION = 5  # "Previdência",
DEPENDENCY_AID_SPECIAL = 6  # "Auxílio Especial",

DEPENDENCE_TYPE = {
    DEPENDENCY_INCOME_TAX: "Imposto de Renda",
    DEPENDENCY_HEALTH_PLAN: "PlanSaúde",
    DEPENDENCY_SALARY_FAMILY: "Salário Família",
    DEPENDENCY_AID_CRECHE: "Auxílio Creche",
    DEPENDENCY_PENSION: "Previdência",
    DEPENDENCY_AID_SPECIAL: "Auxílio Especial",
}

NOT_PROCESSED = 1
PROCESSED = 2
NOT_VALIDITY = 3

DIGITAL_DOCUMENT_STATE = {
    NOT_PROCESSED: "NÃO PROCESSADO",
    PROCESSED: "PROCESSADO",
    NOT_VALIDITY: "NÃO VALIDADO",
}

TRAINEE_NATURE_MANDATORY = 1
TRAINEE_NATURE_MANDATORY_NOT = 2

TRAINEE_NATURE = {
    TRAINEE_NATURE_MANDATORY: "OBRIGATÓRIO",
    TRAINEE_NATURE_MANDATORY_NOT: "NÃO OBRIGATÓRIO",
}

TRAINEE_LEVEL_FUNDAMENTAL = 1
TRAINEE_LEVEL_MEDIUM = 2
TRAINEE_LEVEL_FORMATION = 3
TRAINEE_LEVEL_HIGHER = 4
TRAINEE_LEVEL_SPECIAL = 8
TRAINEE_LEVEL_SOCIAL = 9

TRAINEE_LEVEL = {
    TRAINEE_LEVEL_FUNDAMENTAL: "Fundamental",
    TRAINEE_LEVEL_MEDIUM: "Médio",
    TRAINEE_LEVEL_FORMATION: "Formação Profissional",
    TRAINEE_LEVEL_HIGHER: "Superior",
    TRAINEE_LEVEL_SPECIAL: "Especial",
    TRAINEE_LEVEL_SOCIAL: "Mãe social",
}

TRAINEE_NATURE_MANDATORY = 1
TRAINEE_NATURE_MANDATORY_NOT = 2

TRAINEE_NATURE = {
    TRAINEE_NATURE_MANDATORY: "OBRIGATÓRIO",
    TRAINEE_NATURE_MANDATORY_NOT: "NÃO OBRIGATÓRIO",
}

TRAINEE_LEVEL_FUNDAMENTAL = 1
TRAINEE_LEVEL_MEDIUM = 2
TRAINEE_LEVEL_FORMATION = 3
TRAINEE_LEVEL_HIGHER = 4
TRAINEE_LEVEL_SPECIAL = 8
TRAINEE_LEVEL_SOCIAL = 9

TRAINEE_LEVEL = {
    TRAINEE_LEVEL_FUNDAMENTAL: "Fundamental",
    TRAINEE_LEVEL_MEDIUM: "Médio",
    TRAINEE_LEVEL_FORMATION: "Formação Profissional",
    TRAINEE_LEVEL_HIGHER: "Superior",
    TRAINEE_LEVEL_SPECIAL: "Especial",
    TRAINEE_LEVEL_SOCIAL: "Mãe social",
}


TYPE_RETIREMENT_COMPULSORY = 1
TYPE_RETIREMENT_SPECIAL = 2
TYPE_RETIREMENT_AGE_IMPLEMENT = 3
TYPE_RETIREMENT_INVALIDITY = 4
TYPE_RETIREMENT_CONTRIBUTION_TIME = 5
TYPE_RETIREMENT_VOLUNTEER = 6

TYPE_RETIREMENT = {
    TYPE_RETIREMENT_COMPULSORY: "Compulsória",
    TYPE_RETIREMENT_SPECIAL: "Especial",
    TYPE_RETIREMENT_AGE_IMPLEMENT: "Implemento de idade",
    TYPE_RETIREMENT_INVALIDITY: "Invalidez",
    TYPE_RETIREMENT_CONTRIBUTION_TIME: "Tempo de contribuição",
    TYPE_RETIREMENT_VOLUNTEER: "Voluntária",
}


CLASS_ORGAN_CRM = 1
CLASS_ORGAN_CRO = 2
CLASS_ORGAN_RMS = 3
CLASS_ORGAN_OTHER = 99
CLASS_ORGAN = {
    CLASS_ORGAN_CRM: "Conselho Regional de Medicina (CRM)",
    CLASS_ORGAN_CRO: "Conselho Regional de Odontologia (CRO)",
    CLASS_ORGAN_RMS: "Registro do Ministério da Saúde (RMS",
    CLASS_ORGAN_OTHER: "Outros",
}

RESIDENCE_TIME_INDETERMINATE = 1
RESIDENCE_TIME_DETERMINED = 2
NOT_IMMIGRANT = 10
IMMIGRANTE_RESIDENCE_TIME = {
    RESIDENCE_TIME_INDETERMINATE: "PRAZO INDETERMINADO",
    RESIDENCE_TIME_DETERMINED: "PRAZO DETERMINADO",
    NOT_IMMIGRANT: "NÃO É IMIGRANTE",
}

ENTRY_CONDITION_REFUGEEE = 1
ENTRY_CONDITION_ASYLUM_SEEKER = 2
ENTRY_CONDITION_FAMILY_REUNION = 3
ENTRY_CONDITION_AGREEMENT_MERCOSUR = 4
ENTRY_CONDITION_DEPENDENT_DIPLOMATIC = 5
ENTRY_CONDITION_FRIENDSHIP_PORTUGAL = 6
ENTRY_CONDITION_OTHER = 7
IMMIGRANTE_ENTRY_CONDITION = {
    ENTRY_CONDITION_REFUGEEE: "Refugiado",
    ENTRY_CONDITION_ASYLUM_SEEKER: "Solicitante de refúgio",
    ENTRY_CONDITION_FAMILY_REUNION: "Permanência no Brasil em razão de reunião familiar",
    ENTRY_CONDITION_AGREEMENT_MERCOSUR: "Beneficiado pelo acordo entre países do Mercosul",
    ENTRY_CONDITION_DEPENDENT_DIPLOMATIC: "Dependente de agente diplomático e/ou consular de países que mantêm acordo de reciprocidade para o exercício de atividade remunerada no Brasil",
    ENTRY_CONDITION_FRIENDSHIP_PORTUGAL: "Beneficiado pelo Tratado de Amizade, Cooperação e Consulta entre a República Federativa do Brasil e a República Portuguesa",
    ENTRY_CONDITION_OTHER: "Outra condição",
    NOT_IMMIGRANT: "NÃO É IMIGRANTE",
}

HEALTH_LICENSE_CLS_NORMAL = 1
HEALTH_LICENSE_CLS_ANTICIPATION = 2
HEALTH_LICENSE_CLS_EXTENSION = 3

HEALTH_LICENSE_CLASSIFICATION = {
    HEALTH_LICENSE_CLS_NORMAL: "NORMAL",
    HEALTH_LICENSE_CLS_ANTICIPATION: "ANTECIPAÇÃO",
    HEALTH_LICENSE_CLS_EXTENSION: "PRORROGAÇÃO",
}

TYPE_BY_POSSESSION_BENEFICIARY = ("BFP", "MAP", "SAP")


MAP_FORESIGHT = {1: 1, 2: 2, 3: 2}  # RGPS  # RPPS

TIPO_FOLHA_ID = {
    "EST": 49,
    "RES": 63,
}

TIPO_POSSE = {
    "membros": ["MBR", "MBR2", "MEL", "MCM", "MEC", "MEL2", "MCM2", "MEC2"],
    "servidores": ["EFE", "ECM"],
    "aposentados": ["MAP", "SAP", "MAP2", "APO"],
    "pensionistas": ["BFP"],
    "todos": [
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
        "MAP",
        "SAP",
        "MAP2",
        "APO",
        "BFP",
    ],
}


TIPO_DEPENDENTE_IR = 1
TIPO_DEPENDENTE_AUX_CRECHE = 4

TEMPO_COD_EMAIL = 5


STATUS_TELETRABALHO_REGULAR = 1
STATUS_TELETRABALHO_DESBLOQUEADO = 2
STATUS_TELETRABALHO_BLOQUEADO = 3
STATUS_TELETRABALHO_REVOGADO = 4
STATUS_TELETRABALHO_IGNORADO = 5
STATUS_TELETRABALHO_CONCLUIDO = 6
STATUS_TELETRABALHO_PENDENTE = 7


ACOES_TELETRABALHO = (
    ("BLOQUEAR", "Bloquear"),
    ("DESBLOQUEAR", "Desbloquear"),
    ("REVOGAR", "Revogar"),
    ("IGNORAR", "Ignorar"),
    ("CONCLUIR", "Concluir"),
    ("REGULARIZAR", "Regularizar"),
    ("PENDENTE", "Pendente"),
    ("ZERAR", "Zerar saldo devedor"),
)
