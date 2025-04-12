from contrib.utils import getLogger
from rest_framework import serializers
from rh.const import TIPO_LOGRADOURO_ENDERECO_CHOICES
from rh.gfp.models import ExtraPaymentPeriod
from rh.models import (
    Dependente,
    Servidor,
    PessoaFisica,
    MovimentacaoPosse,
    BenefitMovement,
)
from rh.gfp.models import ContraCheque, FolhaEvento
import re
from rh.const import TIPO_POSSE
import datetime
from contrib.nil import nil_date

from django.db.models import Sum

log = getLogger(__name__)


data_limite = datetime.date(2023, 10, 31)


def get_vinculo_prev(servidor):

    lista_co1 = [
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
    ]
    lista_co2 = ["MAP", "SAP", "MAP2", "APO"]
    lista_co3 = ["BFP"]

    try:
        if servidor.mov_beneficiaries.exists() and servidor.ativo == False:
            return 8

        if servidor.type_by_possession in lista_co1:
            return 1
        elif servidor.type_by_possession in lista_co2:
            return 2
        elif servidor.type_by_possession in lista_co3:
            return 5
        else:
            return None
    except:
        return None


SITUACAO_FUNCIONAL = {}

TIPO_APOSENTADORIA = {
    4: 1,  # Aposentadoria por idade - Proventos proporcionais calculado sobre a média, reajuste manter valor real
    3: 1,  # Aposentadoria por idade - Proventos proporcionais calculado sobre integralidade, revisão pela paridade
    1: 2,  # Aposentadoria por idade e tempo de contribuição - Proventos com integralidade, revisão pela paridade
    2: 2,  # Aposentadoria por idade e tempo de contribuição - Proventos pela média, reajuste manter valor real
    662: 2,  # Aposentadoria voluntária com proventos integrais ao tempo de mandato - Leis próprias
    661: 2,  # Aposentadoria voluntária com proventos proporcionais ao tempo de mandato - Leis próprias
    6: 3,  # Aposentadoria compulsória - Proventos proporcionais calculado sobre a média, reajuste manter valor real
    5: 3,  # Aposentadoria compulsória - Proventos proporcionais calculado sobre a média, reajuste manter valor real
    12: 4,  # Aposentadoria da pessoa com deficiência
    439: 4,  # Aposentadoria da pessoa com deficiência
    16: 4,  # Aposentadoria da pessoa com deficiência - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    443: 4,  # Aposentadoria da pessoa com deficiência - Servidor vinculado a RPC - Proventos limitados ao teto do RGP
    18: 4,  # Aposentadoria por invalidez - Proventos com integralidade, revisão pela paridade
    19: 4,  # Aposentadoria por invalidez - Proventos pela média, reajuste manter valor real
    21: 4,  # Aposentadoria por invalidez - Proventos proporcionais calculado sobre a média, reajuste manter valor real
    20: 4,  # Aposentadoria por invalidez - Proventos proporcionais calculado sobre integralidade, revisão pela paridade
    22: 4,  # Aposentadoria por invalidez - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    447: 4,  # Aposentadoria por invalidez com paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    663: 4,  # Aposentadoria por invalidez permanente - Proventos integrais - Leis próprias
    664: 4,  # Aposentadoria por invalidez permanente - Proventos proporcionais ao tempo de mandato - Leis próprias
    448: 4,  # Aposentadoria por invalidez sem paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    7: 5,  # Aposentadoria de professor - Proventos com integralidade, revisão pela paridade
    8: 5,  # Aposentadoria de professor - Proventos pela média, reajuste manter valor real
    10: 6,  # Aposentadoria especial - Risco
    437: 6,  # Aposentadoria especial - Risco
    14: 6,  # Aposentadoria especial - Risco - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    441: 6,  # Aposentadoria especial - Risco - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    17: 6,  # Aposentadoria especial de policial - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    444: 6,  # Aposentadoria especial de policial - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    13: 6,  # Aposentadoria especial do policial civil
    440: 6,  # Aposentadoria especial do policial civil
    11: 7,  # Aposentadoria especial - Exposição a agentes nocivos
    438: 7,  # Aposentadoria especial - Exposição a agentes nocivos
    15: 7,  # Aposentadoria especial - Exposição a agentes nocivos - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    442: 7,  # Aposentadoria especial - Exposição a agentes nocivos - Servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    655: 9,  # Reserva remunerada compulsória integral
    658: 9,  # Reserva remunerada compulsória proporcional
    656: 9,  # Reserva remunerada integral
    657: 9,  # Reserva remunerada proporcional
    651: 10,  # Reforma
    653: 10,  # Reforma compulsória integral
    652: 10,  # Reforma compulsória proporcional
    450: 10,  # Reforma concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    654: 10,  # Reforma por incapacidade definitiva
    650: 10,  # Reforma por invalidez
    446: None,  # Aposentadoria com paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    454: None,  # Aposentadoria de parlamentar - Plano próprio
    9: None,  # Aposentadoria de servidor vinculado a RPC - Proventos limitados ao teto do RGPS
    455: None,  # Aposentadoria de servidor vinculado ao Poder Legislativo - Plano próprio
    445: None,  # Aposentadoria sem paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    458: None,  # Benefício especial proporcional - Servidor pertencente a RPPS que opta pelo RPC - Demais entes da Federação, de acordo com as disposições das leis específicas
    457: None,  # Benefício especial proporcional - Servidor pertencente a RPPS que opta pelo RPC da União
    659: None,  # Complementação de aposentadoria do RGPS
    660: None,  # Complementação de pensão por morte do RGPS
    459: None,  # Outros benefícios especiais com vínculo previdenciário
    453: None,  # Outros benefícios previdenciários concedidos antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    461: None,  # Outros benefícios sem vínculo previdenciário
    460: None,  # Pensão especial sem vínculo previdenciário
    456: None,  # Pensão por morte - Plano próprio
    23: None,  # Pensão por morte (art. 40, § 7º, da CF/1988)
    451: None,  # Pensão por morte com paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    25: None,  # Pensão por morte com paridade, decorrente do art. 3º da EC 47/2005
    24: None,  # Pensão por morte com paridade, decorrente do art. 6º-A da EC 41/2003
    665: None,  # Pensão por morte de parlamentar - Lei específica
    666: None,  # Pensão por morte de parlamentar - Planos anteriores à EC 20/1998
    26: None,  # Pensão por morte militar
    452: None,  # Pensão por morte sem paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
    449: None,  # Transferência para reserva concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
}

TIPO_RELACAO = {
    1: 1,  # Conjuge , a companheira, o companheiro
    2: 1,  # Conjuge , a companheira, o companheiro
    3: 2,  # Filho não emancipado, menor de 21 anos ou outra idade legislação RPPS
    4: 3,  # Filho invalido ou com deficiencia
    5: 4,  # Pais
    6: 5,  # Irmão não emancipado, menor de 21 anos ou invalido ou com deficiencia
    7: 5,  # Irmão não emancipado, menor de 21 anos ou invalido ou com deficiencia
    8: 6,  # Outros
    9: 6,  # Outros
    10: 6,  # Outros
    11: 6,  # Outros
    12: 6,  # Outros
    13: 6,  # Outros
    14: 6,  # Outros
    15: 6,  # Outros
    16: 6,  # Outros
    17: 6,  # Outros
    18: 6,  # Outros
}

TIPO_REPRESENTACAO = {
    999: 1,  # PAI
    999: 2,  # MÂE
    999: 3,  # TUTOR
    999: 4,  # CURADOR
    999: 5,  # RESPONSAVEL POR GUARDA
    999: 6,  # GUARDA DE MENOR DE 18 ANOS
}

LISTA_NASCIONALIDADE = {
    1: 10,
    88: 29,
    197: 45,
}

LISTA_PAIS = {
    1: 32,
    88: 70,
    197: 45,
}

LISTA_RACA = {
    4: 1,  # Indígena
    6: 2,  # Branca
    3: 4,  # Preta
    2: 6,  # Amarela
    1: 8,  # Parda
    5: 9,  # Não Informado
}

LISTA_RG_ORGAO = {
    "SSP": 1,
    "RFBR": 2,
    "MF": 3,
    "MARINHA": 4,
    "EXERCITO": 5,
    "AERONAUTICA": 6,
    "CRP": 7,
    "CRTR": 8,
    "COREN": 9,
    "CORECON": 10,
    "CRMV": 11,
    "CRFa": 12,
    "CRN": 13,
    "CAU": 14,
    "CRF": 15,
    "CONFEA": 16,
    "CRO": 17,
    "CRESS": 18,
    "CRQ": 19,
    "CRM": 20,
    "COFEN": 21,
    "CREFITO": 22,
    "BM": 23,
    "OAB": 24,
    "SESPAP": 25,
    "SDS": 26,
    "SJ": 27,
    "MINIS. MARINHA": 28,
    "SPTC": 29,
    "SIC": 30,
    "IIFP": 31,
    "CRC": 32,
    "DETRAN - DIC": 33,
    "DETRAN DIC": 33,
    "DETRAN": 33,
    "DDIC": 33,
    "FUNAI": 34,
    "POLICIA MILITAR": 35,
    "DGPC": 36,
    "SSDS": 37,
    "MINIS. EXERCITO": 38,
    "PJC": 39,
    "POLICIA JUD. CIVIL": 40,
    "CBM": 41,
    "SEC EST CASA CIVIL": 42,
    "CRA": 43,
    "CREA": 44,
    "SEJUSP": 45,
    "SEJ": 45,
    "SEJSP MT": 45,
    "SEJMT": 45,
    "SEJSP": 45,
    "PM": 46,
    "BOMBEIRO MILITAR": 47,
    "DEP. POLICIA FEDERAL": 48,
    "DPF": 48,
    "MINISTERIO DA DEFESA": 49,
    "POLICIA TEC CIENTIF": 50,
    "PC": 51,
    "CGPI/DPF": 52,
    "SESDC": 53,
    "SESP": 54,
    "MINIS. AERONAUTICA": 55,
    "SEDPM": 56,
    "SESDEC": 57,
    "CRBM": 60,
    "CONFEF": 58,
    "CRFA": 69,
    "CEE": 63,
    "CRBio": 61,
    "CRB": 62,
    "None": 1,
    "NONE": 1,
    "SEDAL": 1,
    "B": 1,
    "ABC": 1,
    "11238449": 1,
    "MT": 1,
    "00001": 1,
    "00009": 1,
    "00011": 1,
    "00018": 1,
    "MPF - MT": 1,
}

TIPO_LOGRADOURO = {
    1: 17,
    2: 109,
    3: 179,
    4: 179,
    5: 179,
    6: 168,
    7: 179,
    8: 128,
    9: 125,
    100: 179,
}

LISTA_SITUACAO_FUNCIONAL = {
    "NOT_FOUND": None,  #'Não encontrado',
    "ATIVO": 1,  #'Em atividade',
    "ATIVO_LIC_SAUDE": 2,  # 'Licenciado - Tratamento de Saúde',
    "ATIVO_LIC_DOENCA": 2,  # 'Licenciado - Doença em Pessoa da Família',
    "ATIVO_LIC_MATERNIDADE": 2,  # 'Licenciado - Maternidade',
    "ATIVO_LIC_ADOCAO": 2,  # 'Licenciado - Tutoria ou Adoção',
    "ATIVO_LIC_AFAST_CONJUGE": 2,  # 'Licenciado - Afastamento do Conjuge/Companheiro',
    "ATIVO_LIC_MILITAR": 2,  # 'Licenciado - Serviço Militar',
    "ATIVO_LIC_POLITICA": 2,  # 'Licenciado - Atividade Política',
    "ATIVO_LIC_CAPACITACAO": 2,  # 'Licenciado - Capacitação ou Especialização (3 meses por quinquênio)',
    "ATIVO_LIC_INTERESSE": 3,  #'Licenciado - Tratar de Interesse Particular',
    "ATIVO_LIC_CLASSISTA": 3,  #'Licenciado - Desempenho de Mandato Classista',
    "ATIVO_LIC_PREMIO": 2,  #'Licença Prêmio',
    "ATIVO_AFA_DISPONIBILIDADE": 8,  #'Afastado - Em disponibilidade',
    "ATIVO_AFA_OUT_ORG_ONUS_MP": 4,  #'Afastado - Servir a outro Órgão com ônus para o MP',
    "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP": 5,  #'Afastado - Servir a outro Órgão sem ônus para o MP',
    "ATIVO_AFA_SUSPENSAO": 11,  #'Afastado - Suspensão',
    "ATIVO_AFA_COMPJUIZO": 11,  #'Afastado - Comparecer a juízo',
    "ATIVO_AFA_ELETIVO": 9,  #'Afastado - Exercício de Mandato Eletivo',
    "ATIVO_AFA_ESTUDAR": 11,  #'Afastado - Estudar no País/Exterior',
    "ATIVO_AFA_PARC_ESTUDAR": 11,  #'Afastado Parcial - Estudar no País/Exterior',
    "ATIVO_AFA_MISSAO": 11,  #'Afastado - Missão Oficial no Exterior',
    "ATIVO_AFA_ELEITORAL": 11,  #'Afastado - Convocação da Justiça Eleitoral',
    "ATIVO_AFA_JURI": 11,  #'Afastado - Servir no Tribunal do Juri',
    "ATIVO_AFA_TREINAMENTO": 11,  #'Afastado - Treinamento (Palestras/Congressos/Seminários/Outros)',
    "ATIVO_AFA_DESLOCAMENTO": 11,  #'Afastado - Deslocamento até a nova sede',
    "ATIVO_AFA_COMPETICAO": 11,  #'Afastado - Competição desportiva ou representação cultural',
    "ATIVO_AFA_CURSO_CONCURSO": 11,  #'Afastado - Curso de formação de etapa de concurso público',
    "ATIVO_AFA_PRISAO": 11,  #'Afastado - Prisão',
    "ATIVO_AFA_SINDICANCIA_ADM": 11,  #'Afastado - Sindicância Administrativa',
    "ATIVO_AUS_SANGUE": 11,  #'Ausente - Doação de sangue',
    "ATIVO_AUS_ELEITOR": 11,  #'Ausente - Alistamento como eleitor',
    "ATIVO_AUS_CASAMENTO": 11,  #'Ausente - Casamento',
    "ATIVO_AUS_NASCIMENTO": 11,  #'Ausente - Nascimento/adoção de filho',
    "ATIVO_AUS_FALECIMENTO": 11,  #'Ausente - Falecimento',
    "ATIVO_AUS_CONCLUSAO": 11,  #'Ausente - Finalização de trabalho de conclusão de curso',
    "ATIVO_FERIAS": 11,  #'Fruindo Férias',
    "ATIVO_VIAGEM": 11,  #'Viagem a Serviço',
    "ATIVO_RECESSO": 11,  #'Fruindo Recesso',
    "ATIVO_FOLGA_ANIVERSARIO": 11,  #'Fruindo Folga Aniversário',
    "ATIVO_FOLGA_ELEITORAL": 11,  #'Fruindo Folga Eleitoral',
    "ATIVO_FOLGA_COMPENSACAO": 11,  #'Fruindo Folga Compensação',
    "ATIVO_USU_BANCO_DE_HORAS": 11,  #'Fruindo Folga Banco de Horas',
    "ATIVO_USU_PREVENCAOSAUDE": 11,  #'Fruindo Folga Prevenção Saúde',
    "ATIVO_ATUACAO_GRUPO_TRAB": 11,  #'Atuação em Grupo de Trabalho',
    "ATIVO_DESEMPENHO_FUNCAO": 11,  #'Desempenho de Função',
    "ATIVO_PLANTAO": 11,  #'Fruindo Plantão de Feriado',
    "ATIVO_DISPONIBILIDADE": 8,  #'Em disponibilidade(com onus para origem ou para requisitante?)',
    "INATIVO_APO_INVALIDEZ": 11,  #'Aposentado - Por invalidez',
    "INATIVO_APO_COMPULSORIO": 11,  #'Aposentado - Compulsório',
    "INATIVO_APO_VOLUNTARIO": 11,  #'Aposentado - Voluntário',
    "INATIVO_APO_ESPECIAL": 11,  #'Aposentado - Especial',
    "INATIVO_APO_TEMPO_CONTRIBUICAO": 11,  #'Aposentado - Por tempo de contribuição',
    "INATIVO_APO_IDADE": 11,  #'Aposentado - Por idade',
    "INATIVO_FALECIDO": 11,  #'Falecido',
    "INATIVO_EXONERADO_PEDIDO": 11,  #'Exonerado - A pedido',
    "INATIVO_EXONERADO_OFICIO": 11,  #'Exonerado - De ofício',
    "INATIVO_DEMITIDO": 11,  #'Demitido',
    "INATIVO_DEVOLVIDO": 11,  #'Devolvido ao Órgão de Origem',
    "INATIVO_OUTRO_CARGO": 11,  #'Posse em outro cargo inacumulável',
    "INATIVO_TSVE": 11,  #'Fim de TSVE',
    "ATIVO_AFA_CANDIDATURA": 11,  #'Afastado - Candidatura',
}


class DependenciaPrevidenciarioVoSerializer(serializers.ModelSerializer):

    coCondicao = serializers.SerializerMethodField()
    coTipoDependencia = serializers.SerializerMethodField()
    pessoaPrevidenciario = serializers.SerializerMethodField()

    class Meta:
        model = Dependente
        fields = ["coCondicao", "coTipoDependencia", "pessoaPrevidenciario"]

    def get_coCondicao(self, obj):
        return obj.capacidade

    def get_coTipoDependencia(self, obj):
        DEPENDENCIA_MAP = {
            1: 1,  # Cônjuge, a companheira, o companheiro
            2: 1,  # Cônjuge, a companheira, o companheiro
            3: 2,  # Filho não emancipado, menor de 21 anos ou outra idade legislação RPPS
            4: 3,  # Filho inválido ou com deficiência
            5: 4,  # Pais
            6: 5,  # Irmão não emancipado, menor de 21 anos ou inválido ou com deficiência
            7: 5,  # Irmão não emancipado, menor de 21 anos ou inválido ou com deficiência
            8: 6,  # Outros
            9: 6,  # Outros
            10: 6,  # Outros
            11: 6,  # Outros
            12: 6,  # Outros
            13: 6,  # Outros
            14: 6,  # Outros
            15: 6,  # Outros
            16: 6,  # Outros
            17: 2,  # Filho não emancipado, menor de 21 anos ou outra idade legislação RPPS
            18: 6,  # Outros
        }
        return DEPENDENCIA_MAP.get(obj.grau_parentesco, None)

    def get_pessoaPrevidenciario(self, obj):
        return PessoaPrevidenciarioSerializer(obj.pessoa_fisica).data


class PessoaPrevidenciarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = PessoaFisica
        fields = []
        """
        fields = [
            'bairro', 'celular', 'cep', 'cnhCategoria', 'cnhDtValid', 'cnhNum', 'cnhUf', 'coEstCivil', 'coSexo',
            'codIbgeCidade', 'complemento', 'cpf', 'dtNasc', 'email', 'idprofNum', 'idprofTipo', 'idprofUf', 'logradouro',
            'nacionalidade', 'nascCidadeIbge', 'nascPais', 'nascUf', 'nome', 'nomeMae', 'nomeSocial', 'numLogradouro','pisPasep', 'raca',
            'rgDtExp', 'rgNum', 'rgOrgaoExp', 'rgTipo', 'rgUf', 'telefone', 'tipoLogradouro', 'uf', 'vinculoPrevidenciario'
        ]
        """

    def get_fields(self):

        obj = self.instance

        fields = super().get_fields()

        lista_fields = [
            "bairro",
            "celular",
            "cep",
            "cnhCategoria",
            "cnhDtValid",
            "cnhNum",
            "cnhUf",
            "coEstCivil",
            "coSexo",
            "codIbgeCidade",
            "complemento",
            "cpf",
            "dtNasc",
            "email",
            "idprofNum",
            "idprofTipo",
            "idprofUf",
            "logradouro",
            "nacionalidade",
            "nascCidadeIbge",
            "nascPais",
            "nascUf",
            "nome",
            "nomeMae",
            "nomeSocial",
            "numLogradouro",
            "pisPasep",
            "raca",
            "rgDtExp",
            "rgNum",
            "rgOrgaoExp",
            "rgTipo",
            "rgUf",
            "telefone",
            "tipoLogradouro",
            "uf",
        ]

        # if obj.dependentes_pessoa.all().exists():
        #     lista_fields = ['coSexo', 'cpf', 'dtNasc', 'nome']
        #
        # elif obj.servidor_set.exists():
        #     co_vinculo = get_vinculo_prev(servidor=obj.servidor_set.first())
        #
        #     if co_vinculo == 1:
        #         lista_fields = [
        #             'bairro', 'celular', 'cep', 'cnhCategoria', 'cnhDtValid', 'cnhNum', 'cnhUf', 'coEstCivil', 'coSexo',
        #             'codIbgeCidade', 'complemento', 'cpf', 'dtNasc', 'email', 'idprofNum', 'idprofTipo', 'idprofUf', 'logradouro',
        #             'nacionalidade', 'nascCidadeIbge', 'nascPais', 'nascUf', 'nome', 'nomeMae', 'nomeSocial', 'numLogradouro',
        #             'pisPasep', 'raca', 'rgDtExp', 'rgNum', 'rgOrgaoExp', 'rgTipo', 'rgUf', 'telefone', 'tipoLogradouro', 'uf',
        #         ]
        #     elif co_vinculo == 2:
        #         lista_fields = [
        #             'bairro', 'celular', 'cep', 'cnhCategoria', 'cnhDtValid', 'cnhNum', 'cnhUf', 'coEstCivil', 'coSexo',
        #             'codIbgeCidade', 'complemento', 'cpf', 'dtNasc', 'email', 'idprofNum', 'idprofTipo', 'idprofUf', 'logradouro',
        #             'nacionalidade', 'nascCidadeIbge', 'nascPais', 'nascUf', 'nome', 'nomeMae', 'nomeSocial', 'numLogradouro',
        #             'pisPasep', 'raca', 'rgDtExp', 'rgNum', 'rgOrgaoExp', 'rgTipo', 'rgUf', 'telefone', 'tipoLogradouro', 'uf',
        #         ]
        #     elif co_vinculo == 5:
        #         lista_fields = [
        #             'bairro', 'celular', 'cep', 'cnhCategoria', 'cnhDtValid', 'cnhNum', 'cnhUf', 'coEstCivil', 'coSexo',
        #             'codIbgeCidade', 'complemento', 'cpf', 'dtNasc', 'email', 'idprofNum', 'idprofTipo', 'idprofUf', 'logradouro',
        #             'nacionalidade', 'nascCidadeIbge', 'nascPais', 'nascUf', 'nome', 'nomeMae', 'nomeSocial', 'numLogradouro',
        #             'pisPasep', 'raca', 'rgDtExp', 'rgNum', 'rgOrgaoExp', 'rgTipo', 'rgUf', 'telefone', 'tipoLogradouro', 'uf',
        #         ]

        for field in lista_fields:
            fields[field] = serializers.SerializerMethodField()

        return fields

    def get_idprofNum(self, obj):
        return None

    def get_idprofTipo(self, obj):
        return None

    def get_idprofUf(self, obj):
        return None

    def get_bairro(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.bairro is not None:
            return endereco.bairro if not endereco.bairro == "" else "Sem Bairro"
        return "Sem Bairro"

    def get_numLogradouro(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.numero is not None:
            return endereco.numero.split(",")[0]
        return None

    def get_cep(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.cep is not None:
            cep = endereco.cep
            cep = "".join(filter(str.isdigit, cep))

            if len(cep) == 8:
                cep_formatado = f"{cep[:5]}-{cep[5:]}"
                return cep_formatado
            elif len(cep) < 8:
                cep = cep.zfill(8)
                cep_formatado = f"{cep[:5]}-{cep[5:]}"
                return cep_formatado
        return None

    def get_codIbgeCidade(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.outsider:
            return 9999999

        if endereco and endereco.municipio:
            return str(endereco.municipio.ibge)
        return ""

    def get_complemento(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.complemento is not None:
            cleaned_text = re.sub("<[^<]+?>", " ", endereco.complemento).strip()
            return cleaned_text[:50] if not cleaned_text == "" else None
        return None

    def get_logradouro(self, obj):
        endereco = obj.address.last()
        if endereco:
            return endereco.logradouro
        return None

    def get_tipoLogradouro(self, obj):
        endereco = obj.address.last()
        if endereco and endereco.tipo_logradouro:
            return TIPO_LOGRADOURO.get(endereco.tipo_logradouro, None)
        return None

    def get_uf(self, obj):
        endereco = obj.address.last()
        # if endereco and endereco.outsider and endereco.country.id == 197 :
        #    return 'PT'

        if endereco and endereco.municipio and endereco.municipio.estado:
            return endereco.municipio.estado.sigla
        return (
            obj.municipio_naturalidade.estado.sigla
            if obj.municipio_naturalidade
            else None
        )

    def get_celular(self, obj):

        telefones = obj.phone.all()

        telefone = telefones.filter(tipo_telefone=3).first()  # Celular
        if telefone:
            return str(telefone.numero).strip()
        telefone = telefones.filter(tipo_telefone=1).first()  # Telefone fixo
        if telefone:
            return str(telefone.numero).strip()
        telefone = telefones.all().first()  # Telefone fixo
        if telefone:
            return str(telefone.numero).strip()
        return "6536110600"

    def cnh_libera_dados(self, cnh):
        if (
            cnh
            and cnh.cnh_category
            and cnh.data_validade
            and cnh.numero
            and cnh.estado_expedicao
        ):
            return True
        return False

    def get_cnhCategoria(self, obj):
        cnh = obj.cnh
        return cnh.cnh_category.valor if self.cnh_libera_dados(cnh) else None

    def get_cnhDtValid(self, obj):
        cnh = obj.cnh
        return (
            cnh.data_validade.strftime("%d/%m/%Y")
            if self.cnh_libera_dados(cnh)
            else None
        )

    def get_cnhNum(self, obj):
        cnh = obj.cnh
        return cnh.numero if self.cnh_libera_dados(cnh) else None

    def get_cnhUf(self, obj):
        cnh = obj.cnh
        return cnh.estado_expedicao.sigla if self.cnh_libera_dados(cnh) else None

    def get_coEstCivil(self, obj):
        estado_civil_map = {
            1: 1,  # SOLTEIRO
            2: 2,  # CASADO
            3: 3,  # VIUVO
            4: 4,  # SEPARADO JUDICIALMENTE
            5: 5,  # DIVORCIADO
            6: 6,  # UNIAO ESTAVEL
        }
        return estado_civil_map.get(obj.estado_civil, 9)  # OUTROS

    def get_coSexo(self, obj):
        sexo_map = {
            "M": 2,
            "F": 1,
        }
        return sexo_map.get(obj.sexo, None)

    def get_cpf(self, obj):
        return obj.cpf

    def get_dtNasc(self, obj):
        return obj.data_nascimento.strftime("%d/%m/%Y") if obj.data_nascimento else None

    def get_email(self, obj):
        email_institucional = obj.email_institucional
        email_pessoal = obj.email_pessoal

        if email_institucional:
            return email_institucional.split()[0]
        elif email_pessoal:
            return email_pessoal.split()[0]
        return "None"

    def get_nacionalidade(self, obj):
        nacionalidade = obj.nationality
        if nacionalidade:
            return LISTA_NASCIONALIDADE.get(nacionalidade.pk, None)
        return None

    def get_nascCidadeIbge(self, obj):
        return (
            obj.municipio_naturalidade.nome[:20] if obj.municipio_naturalidade else None
        )

    def get_nascPais(self, obj):
        if obj.nationality_birth:
            return LISTA_PAIS.get(obj.nationality_birth.pk, None)
        return None

    def get_nascUf(self, obj):
        return (
            obj.municipio_naturalidade.estado.sigla
            if obj.municipio_naturalidade
            else None
        )

    def get_nome(self, obj):
        return obj.nome

    def get_nomeMae(self, obj):
        if obj.nome_mae is not None and not obj.nome_mae == "":
            return obj.nome_mae
        return obj.nome

    def get_nomeSocial(self, obj):
        return obj.social_name

    def get_pisPasep(self, obj):
        if obj.pis_pasep:
            return obj.pis_pasep.numero
        return None

    def get_raca(self, obj):
        return LISTA_RACA.get(obj.raca_cor, 5)

    def libera_dados_rg(self, obj):

        if obj.servidor_set.first() and get_vinculo_prev(obj.servidor_set.first()) != 5:
            return True
        if obj.rg_orgao is None:
            # return  False
            obj.rg_orgao = "ssp"

        rg_orgao = obj.rg_orgao.upper()
        orgao = None

        for chave, valor in LISTA_RG_ORGAO.items():
            if chave in rg_orgao:
                orgao = valor
                break

        if obj.rg_data_expedicao and obj.rg and obj.rg_uf.sigla and orgao:
            return True

        return False

    def get_rgDtExp(self, obj):
        return (
            obj.rg_data_expedicao.strftime("%d/%m/%Y")
            if self.libera_dados_rg(obj)
            else None
        )

    def get_rgNum(self, obj):
        return obj.rg if self.libera_dados_rg(obj) else None

    def get_rgOrgaoExp(self, obj):
        rg_orgao = obj.rg_orgao
        orgao = None

        if rg_orgao is None:
            return 1

        for chave, valor in LISTA_RG_ORGAO.items():
            if chave in rg_orgao or chave in rg_orgao.upper():
                orgao = valor
                break

        return orgao if self.libera_dados_rg(obj) and orgao else None

    def get_rgUf(self, obj):
        return obj.rg_uf.sigla if self.libera_dados_rg(obj) else None

    def get_rgTipo(self, obj):
        return 1 if self.libera_dados_rg(obj) else None

    def get_telefone(self, obj):
        telefones = obj.phone.all()
        telefone = telefones.filter(tipo_telefone=1).first()  # Telefone fixo
        if telefone:
            return str(telefone.numero).strip()
        telefone = telefones.filter(tipo_telefone=3).first()  # Celular
        if telefone:
            return str(telefone.numero).strip()
        return "6536110600"

    def get_vinculoPrevidenciario(self, obj):
        return {}


class PensaoPrevidenciarioSerializer(serializers.ModelSerializer):
    coDuracao = serializers.SerializerMethodField()
    coTipoRelacao = serializers.SerializerMethodField()
    dtObitoInstituidor = serializers.SerializerMethodField()
    pessoaPrevidenciario = serializers.SerializerMethodField()
    vinculoPrevidenciario = serializers.SerializerMethodField()

    class Meta:
        model = BenefitMovement
        fields = [
            "coDuracao",
            "coTipoRelacao",
            "dtObitoInstituidor",
            "pessoaPrevidenciario",
            "vinculoPrevidenciario",
        ]

    def get_coDuracao(self, obj):
        return obj.type_pension_death or 0

    def get_coTipoInstituidor(self, obj):
        return None  # inteiro

    def get_coTipoRelacao(self, obj):
        dep = Dependente.objects.filter(pessoa_fisica__pk=obj.servidor.pessoa_fisica.id)
        if dep.exists():
            return TIPO_RELACAO.get(dep.first().grau_parentesco, None)

        return None  # inteiro

    def get_dtInicioPensao(self, obj):
        return None

    def get_dtObitoInstituidor(self, obj):
        return (
            obj.founder_employee.pessoa_fisica.data_obito.strftime("%d/%m/%Y")
            if not obj.founder_employee.pessoa_fisica.data_obito is None
            else None
        )

    def get_idPensaoPrev(self, obj):
        return None  # inteiro

    def get_pessoaPrevidenciario(self, obj):

        return PessoaPrevidenciarioSerializer(obj.servidor.pessoa_fisica).data
        # return {}

    def get_nuTempoDuracao(self, obj):
        return None  # inteiro

    def get_vinculoPrevidenciario(self, obj):
        return VinculoPrevidenciarioSerializer(obj.servidor).data

    def get_vlBeneficioPensao(self, obj):
        return None  # float

    def get_vlPctQuota(self, obj):
        return None  # float

    def get_vlTotalPensao(self, obj):
        return None  # float


class RepresentanteLegalPrevidenciarioSerializer(serializers.ModelSerializer):
    tipoRepresentacao = serializers.SerializerMethodField()
    pessoaPrevidenciario = serializers.SerializerMethodField()

    class Meta:
        model = PessoaFisica
        fields = ["tipoRepresentacao", "pessoaPrevidenciario"]

    def get_tipoRepresentacao(self, obj):

        mov = BenefitMovement.objects.filter(
            servidor=obj.dependente, legal_representative=obj, ativo=True
        )
        if mov.exists():
            return mov.first().type_legal_representative

        return None

    def get_pessoaPrevidenciario(self, obj):
        return PessoaPrevidenciarioSerializer(obj).data


class VinculoPrevidenciarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Servidor
        fields = []

    def get_fields(self):
        obj = self.instance

        fields = super().get_fields()

        lista_fields = []

        co_vinculo = get_vinculo_prev(obj)

        if co_vinculo == 1:
            lista_fields = [
                "categoria",
                "coPoder",
                "coSituacaoFuncional",
                "coTipoCargo",
                "coTipoFundo",
                "coTipoPopulacao",
                "coTipoVinculo",
                "coVinculoPrev",
                "dataAtualizaoDados",
                "dtIngCarreira",
                "dtIngEnte",
                "emailContatoEmergencia",
                "flagCensoExterno",
                "inPrevComp",
                "jornada",
                "matricula",
                "nivel",
                "noCargo",
                "noCarreira",
                "noOrgao",
                "nomeContatoEmergencia",
                "nuVinculo",
                "parentesco",
                "telefoneContatoEmergencia",
                "vlRemuneracao",
            ]
        elif co_vinculo == 2:
            lista_fields = [
                "categoria",
                "coPoder",
                "coTipoAposentadoria",
                "coTipoCargo",
                "coTipoFundo",
                "coTipoVinculo",
                "coVinculoPrev",
                "dataAtualizaoDados",
                "dtIngEnte",
                "dtInicioAposentadoria",
                "emailContatoEmergencia",
                "flagCensoExterno",
                "jornada",
                "matricula",
                "nivel",
                "noOrgao",
                "nomeContatoEmergencia",
                "nuVinculo",
                "parentesco",
                "telefoneContatoEmergencia",
                "vlAposentadoria",
                "dtIngCarreira",
                "representanteLegal",
            ]
        elif co_vinculo == 5:
            lista_fields = [
                "coPoder",
                "coTipoFundo",
                "coVinculoPrev",
                "dataAtualizaoDados",
                "emailContatoEmergencia",
                "flagCensoExterno",
                "matricula",
                "noOrgao",
                "nomeContatoEmergencia",
                "nuVinculo",
                "parentesco",
                "telefoneContatoEmergencia",
                "representanteLegal",
            ]
        elif co_vinculo == 8:
            lista_fields = [
                "coPoder",
                "coTipoFundo",
                "coVinculoPrev",
                "dataAtualizaoDados",
                "flagCensoExterno",
                "matricula",
                "noOrgao",
                "nuVinculo",
            ]

        for field in lista_fields:
            fields[field] = serializers.SerializerMethodField()

        return fields

    def get_categoria(self, obj):
        return obj.get_type_by_possession_display()[:20]

    def get_cnpjOrgao(self, obj):
        return None

    def get_cnpjPoder(self, obj):
        return None

    def get_coCompMassa(self, obj):
        return None  # inteiro

    def get_coCondicao(self, obj):
        return None  # inteiro

    def get_coCriterioElegibilidade(self, obj):
        return None  # inteiro

    def get_coPoder(self, obj):
        return 4

    def get_coSituacao(self, obj):
        return None  # inteiro

    def get_coSituacaoFuncional(self, obj):
        if obj.situacao_funcional_cache:
            return LISTA_SITUACAO_FUNCIONAL.get(obj.situacao_funcional_cache)
        return None  # inteiro

    def get_coTipoAposentadoria(self, obj):
        mov = BenefitMovement.objects.filter(servidor=obj)
        if mov.exists():
            if mov.last().benefit_role:
                return TIPO_APOSENTADORIA[mov.last().benefit_role.pk]

        return None  # inteiro

    def get_coTipoCargo(self, obj):
        co_cargo = None
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj, ativo=True).last()
        if mov_posse and mov_posse.quadro.cargo:
            cargo = mov_posse.quadro.cargo
            if cargo.indicativo == "S":
                co_cargo = 7
            elif cargo.indicativo == "M":
                co_cargo = 1

        return co_cargo

    def get_coTipoFundo(self, obj):
        return 2

    def get_coTipoPoder(self, obj):
        return None  # inteiro

    def get_coTipoPopulacao(self, obj):
        if obj.ativo:
            return 1
        return None  # inteiro

    def get_coTipoVinculo(self, obj):
        if obj.type_by_possession == "ECM":
            return 2
        if obj.type_by_possession in TIPO_POSSE["aposentados"]:
            return None
        return 1

    def get_coVinculoPrev(self, obj):
        return get_vinculo_prev(obj)

    def get_codgIbge(self, obj):
        return None  # inteiro

    def get_cpf(self, obj):
        return None

    def get_dataAtualizaoDados(self, obj):
        data_corte = datetime.date(2022, 4, 30)
        return data_corte.strftime("%d/%m/%Y")
        """p_posse = obj.posses.first()

        if p_posse and p_posse.data_posse <= data_corte:
            return data_corte.strftime('%d/%m/%Y')
        
        elif obj.pessoa_fisica.history.exists():
            return obj.pessoa_fisica.history.last().when.strftime('%d/%m/%Y')
        else:
            if obj.pessoa_fisica.modified_at >= obj.modified_at:
                return obj.pessoa_fisica.modified_at.strftime('%d/%m/%Y')
            else:
                return obj.modified_at.strftime('%d/%m/%Y')

        return None"""

    def get_dataRecebido(self, obj):
        return None

    def get_dtIngCargo(self, obj):
        return None

    def get_dtIngCarreira(self, obj):
        if obj.type_by_possession in TIPO_POSSE["aposentados"]:
            return None
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj).first()
        if mov_posse and mov_posse.data_posse:
            return mov_posse.data_posse.strftime("%d/%m/%Y")
        return None

    def get_dtIngEnte(self, obj):
        if obj.type_by_possession in TIPO_POSSE["aposentados"]:
            return None
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj).first()
        if mov_posse and mov_posse.data_posse:
            return mov_posse.data_posse.strftime("%d/%m/%Y")
        return None

    def get_dtIngServPub(self, obj):
        return None

    def get_dtInicioAbono(self, obj):
        return None

    def get_dtInicioAposentadoria(self, obj):
        if obj.type_by_possession in TIPO_POSSE["aposentados"]:
            mov_posse = MovimentacaoPosse.objects.filter(servidor=obj).last()
            if mov_posse and mov_posse.data_posse:
                return f"{mov_posse.data_posse.strftime('%d/%m/%Y')}"
        return None

    def get_dtProvAposentadoria(self, obj):
        return None

    def get_dtSituacao(self, obj):
        return None

    def get_emailContatoEmergencia(self, obj):
        return None

    def get_flagCensoExterno(self, obj):
        """data_corte = datetime.date(2022, 4, 30)

        p_posse = obj.posses.first()

        if p_posse and p_posse.data_posse <= data_corte:
            return 1
        return 2"""
        return 1

    def get_idenVinculo(self, obj):
        return None  # int

    def get_inAbonoPermanencia(self, obj):
        return None  # int

    def get_inParidServ(self, obj):
        return None  # int

    def get_inPrevComp(self, obj):
        return None  # int

    def get_jornada(self, obj):
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj, ativo=True).last()
        if mov_posse and mov_posse.quadro.cargo:
            cargo = mov_posse.quadro.cargo
            return f"{cargo.configs.last().workload}"
        return None

    def get_matricula(self, obj):
        return f"{obj.matricula}"

    def get_nivel(self, obj):

        reference_ef = None

        possessions = obj.posses_ativas
        possession_ef = possessions.filter(
            quadro__cargo__tipo_lei_cargo__in=("EF", "AC")
        )
        if possession_ef.exists():
            reference_ef = (
                ContraCheque._get_referencia_from_posse(
                    possessions.get(quadro__cargo__tipo_lei_cargo="EF")
                )
                if obj.is_efetivo
                else None
            )

        if reference_ef:
            return reference_ef.sigla_cache
        return ""

    def get_noCargo(self, obj):
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj, ativo=True).last()
        if mov_posse and mov_posse.quadro.cargo:
            return f"{mov_posse.quadro.cargo}"
        return None

    def get_noCarreira(self, obj):
        return ""

    def get_noOrgao(self, obj):
        mov_posse = MovimentacaoPosse.objects.filter(servidor=obj, ativo=True).last()
        if mov_posse and mov_posse.quadro.cargo:
            cargo = mov_posse.quadro.cargo
            return f"{cargo.unidade_administrativa}"
        return None

    def get_nomeContatoEmergencia(self, obj):
        return None

    def get_nomeEnte(self, obj):
        return None

    def get_nuAno(self, obj):
        return None

    def get_nuDependentes(self, obj):
        return None  # inteiro

    def get_nuMes(self, obj):
        return None  # inteiro

    def get_nuTempoRgps(self, obj):
        return None  # inteiro

    def get_nuTempoRppsEs(self, obj):
        return None  # inteiro

    def get_nuTempoRppsFed(self, obj):
        return None  # inteiro

    def get_nuTempoRppsMun(self, obj):
        return None  # inteiro

    def get_nuVinculo(self, obj):
        return 1  # envio padrão 1

    def get_parentesco(self, obj):
        return None

    def get_telefoneContatoEmergencia(self, obj):
        return None

    def get_uf(self, obj):
        return None

    def get_vlAposentadoria(self, obj):
        if obj.type_by_possession in TIPO_POSSE["aposentados"]:
            pagamento = ExtraPaymentPeriod.objects.filter(
                employee=obj, end_validity__isnull=True
            ).first()

            if pagamento:
                return float(pagamento.value)
        return None  # numnbr 0.0

    def get_vlBaseCalculo(self, obj):
        return None  # numnbr 0.0

    def get_vlCompensPrevid(self, obj):
        return None  # numnbr 0.0

    def get_vlContribuicao(self, obj):
        return None  # numnbr 0.0

    def get_vlRemuneracao(self, obj):

        if obj.type_by_possession == "ECM":
            subsidios = ["00100", "00600"]
        else:
            subsidios = [
                "00100",
            ]

        data = datetime.date(2023, 10, 31)
        folha_evento_soma = FolhaEvento.objects.filter(
            folha__dt_pagamento__month=10,
            folha__dt_pagamento__year=2023,
            servidor=obj,
            evento__numero__in=subsidios,
        ).aggregate(soma=Sum("valor"))

        if folha_evento_soma["soma"] is None:
            log.info(obj)
            log.info(folha_evento_soma)

        return (
            float(folha_evento_soma["soma"])
            if folha_evento_soma and folha_evento_soma["soma"]
            else None
        )

        # cc = obj.paychecks.filter(folha__dt_fechamento__lte=data)

        # log.info(cc.first().total_bruto)
        # log.info(cc.first().total_liquido)

        # return float(cc.first().total_bruto) if cc.exists() else None

    def get_vlTetoEspecifico(self, obj):
        return None  # numnbr 0.0

    def get_representanteLegal(self, obj):

        mov = BenefitMovement.objects.filter(servidor=obj, ativo=True)

        if mov.exists():
            representante = mov.first().legal_representative
            if representante:
                representante.dependente = obj
                return RepresentanteLegalPrevidenciarioSerializer(representante).data

        return None


class CensoPrevidenciarioSerializer(serializers.ModelSerializer):

    # dependenciaPrevidenciaria = serializers.SerializerMethodField()
    # pensaoPrevidenciario = serializers.SerializerMethodField()
    # pessoaPrevidenciario = serializers.SerializerMethodField()
    # vinculoPrevidenciario = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        # fields = ['dependenciaPrevidenciaria', 'pensaoPrevidenciario', 'pessoaPrevidenciario', 'vinculoPrevidenciario']
        fields = []

    def get_fields(self):
        obj = self.instance
        fields = super().get_fields()

        lista_fields = [
            "dependenciaPrevidenciaria",
            "pensaoPrevidenciario",
            "pessoaPrevidenciario",
            "vinculoPrevidenciario",
        ]

        co_vinculo = get_vinculo_prev(obj)

        if co_vinculo == 1:
            lista_fields = [
                "dependenciaPrevidenciaria",
                "pessoaPrevidenciario",
                "vinculoPrevidenciario",
            ]
        elif co_vinculo == 2:
            lista_fields = [
                "dependenciaPrevidenciaria",
                "pessoaPrevidenciario",
                "vinculoPrevidenciario",
            ]
        elif co_vinculo == 5:
            lista_fields = []
        elif co_vinculo == 8:
            lista_fields = [
                "pensaoPrevidenciario",
                "pessoaPrevidenciario",
                "vinculoPrevidenciario",
            ]

        for field in lista_fields:
            fields[field] = serializers.SerializerMethodField()

        return fields

    def get_dependenciaPrevidenciaria(self, obj):
        lista_maticula_dependentes_erro = [
            554,
            472,
            1132,
            245,
            1337,
            1124,
            740,
            1182,
            1364,
            572,
            466,
            834,
            415,
            929,
            626,
            1191,
            6804,
            354,
            7199,
            241,
            1209,
            1151,
            9,
            1232,
            1179,
            465,
            11,
            571,
            1145,
            250,
            288,
            1327,
            1303,
            450,
            1234,
            591,
            6640,
            1355,
            509,
            772,
            1245,
            869,
            6591,
            1019,
            538,
            6570,
            1140,
            7115,
            1347,
            695,
            594,
            1242,
            1268,
            207,
            6582,
            152,
            658,
            471,
            1026,
            7045,
            1383,
            6918,
            1149,
            159,
            1117,
            516,
            7161,
            738,
            6820,
            702,
            7146,
            213,
            836,
            628,
            601,
            716,
            343,
            1244,
            1310,
            661,
            1339,
            6800,
            1134,
            1236,
            567,
            327,
            259,
            181,
            219,
            1318,
            1278,
            160,
            1153,
            434,
            279,
            1228,
            540,
            1221,
            251,
            1201,
            857,
            741,
            330,
            6011,
            7004,
            1207,
            1247,
            1229,
            7207,
            1192,
            881,
            770,
            1185,
            634,
            389,
            560,
            7056,
            320,
            6005,
            226,
            133,
            6659,
            1128,
            664,
            7200,
            1186,
            324,
            345,
            891,
            6802,
            636,
            349,
            590,
            6015,
            6708,
            786,
            221,
        ]

        # lista_maticula_dependentes_erro = []

        if obj.matricula in lista_maticula_dependentes_erro:
            return []
        return [
            DependenciaPrevidenciarioVoSerializer(dependente).data
            for dependente in obj.dependentes.all().exclude(
                pessoa_fisica__cpf__icontains="#dep"
            )
        ]
        # return []

    def get_pensaoPrevidenciario(self, obj):
        if get_vinculo_prev(obj) == 8:
            mov = BenefitMovement.objects.filter(founder_employee=obj, ativo=True)
            return [PensaoPrevidenciarioSerializer(pensao).data for pensao in mov]
        return []

    def get_pessoaPrevidenciario(self, obj):
        return PessoaPrevidenciarioSerializer(obj.pessoa_fisica).data

    def get_vinculoPrevidenciario(self, obj):
        return VinculoPrevidenciarioSerializer(obj).data
