# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import Configuration, AcquisitionPeriod
from rh.models import Servidor, BenefitMovement

from rh.apiv2.serializers.censoprevidenciario import CensoPrevidenciarioSerializer

from rh.const import TIPO_POSSE

from itertools import chain

import requests
import json

log = getLogger(__name__)


class Command(BaseCommand):

    help = """

    """

    data_limite = date(2023, 10, 31)

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.enviar_dados()

    def enviar_dados(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando O envio dos dados para o MTPREV >>>>>>>>>>>>>"
        )
        try:
            token_hom = "0ebeb5aafdd584ca5285fda4fe27832e"
            url_hom = f"http://homolog.servicos.seplag.mt.gov.br/apicensointegracao/stageVinculo/{token_hom}"

            token_prod = "bcd2487a459ee8c23754f93ca9e79547a6fdab582d9281cb07ce0553"
            url_prod = f"https://servicos.seplag.mt.gov.br/apicensointegracao/stageVinculo/{token_prod}"

            headers = {"accept": "*/*", "Content-Type": "application/json"}

            lista_erro = []
            lista_erro_matriculas = []

            lista_sucesso = []

            instituidores = self.get_instituidores_pensionistas()

            servidores = self.get_servidores_ativos()

            aposentados = self.get_servidores_aposentados()

            lista_geral = list(chain(servidores, aposentados, instituidores))

            for servidor in servidores:

                print(servidor)

                data = CensoPrevidenciarioSerializer(servidor).data

                data_json = json.dumps(data)

                # print(data_json)

                response = requests.post(url_prod, data=data_json, headers=headers)

                print(response.status_code)
                print(response.json())

                if (
                    response.status_code == 201
                ):  # and isinstance(response.json(), list) :
                    lista_sucesso.append(
                        {"servidor": servidor.matricula, "protocolo": response.json()}
                    )
                else:
                    lista_erro.append(
                        {"servidor": servidor.matricula, "erro": response.json()}
                    )
                    lista_erro_matriculas.append(servidor.matricula)

            print("lista de erros ----")
            print(lista_erro)
            print("lista de matriculas ----")
            print(lista_erro_matriculas)
            print("*")
            print("*")
            print("*")
            print("*")
            print("*")
            print("*")
            print("lista sucesso")
            print(lista_sucesso)
            print("*")
            print("*")
            print("numero envios")
            print(f"Total - {len(lista_geral)}")
            print(f"Ativos - {len(servidores)}")
            print(f"Aposentados - {len(aposentados)}")
            print(
                f"Instituidores - {len(instituidores)}  - beneficiarios -{BenefitMovement.objects.filter(founder_employee__in=instituidores).count()}"
            )

        except Exception as err:
            log.info(err)
            print(err)
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando O envio dos dados para o MTPREV  >>>>>>>>>>>>>"
        )

    def get_servidores_ativos(self):
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
        ]

        return Servidor.objects.filter(
            Q(ativo=True),
            Q(created_at__lte=self.data_limite),
            # Q(matricula=6564),
            # Q(type_by_possession__in=['ECM',])
            Q(type_by_possession__in=TIPO_POSSE["membros"])
            | Q(type_by_possession__in=TIPO_POSSE["servidores"]),
        )

    def get_servidores_aposentados(self):

        ignora_tipo_beneficio = [
            446,  # Aposentadoria com paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
            454,  # Aposentadoria de parlamentar - Plano próprio
            9,  # Aposentadoria de servidor vinculado a RPC - Proventos limitados ao teto do RGPS
            455,  # Aposentadoria de servidor vinculado ao Poder Legislativo - Plano próprio
            445,  # Aposentadoria sem paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
            458,  # Benefício especial proporcional - Servidor pertencente a RPPS que opta pelo RPC - Demais entes da Federação, de acordo com as disposições das leis específicas
            457,  # Benefício especial proporcional - Servidor pertencente a RPPS que opta pelo RPC da União
            659,  # Complementação de aposentadoria do RGPS
            660,  # Complementação de pensão por morte do RGPS
            459,  # Outros benefícios especiais com vínculo previdenciário
            453,  # Outros benefícios previdenciários concedidos antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
            461,  # Outros benefícios sem vínculo previdenciário
            460,  # Pensão especial sem vínculo previdenciário
            456,  # Pensão por morte - Plano próprio
            23,  # Pensão por morte (art. 40, § 7º, da CF/1988)
            451,  # Pensão por morte com paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
            25,  # Pensão por morte com paridade, decorrente do art. 3º da EC 47/2005
            24,  # Pensão por morte com paridade, decorrente do art. 6º-A da EC 41/2003
            665,  # Pensão por morte de parlamentar - Lei específica
            666,  # Pensão por morte de parlamentar - Planos anteriores à EC 20/1998
            26,  # Pensão por morte militar
            452,  # Pensão por morte sem paridade concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
            449,  # Transferência para reserva concedida antes da obrigatoriedade de envio dos eventos não periódicos para entes públicos no eSocial
        ]

        return Servidor.objects.filter(
            ativo=True,
            created_at__lte=self.data_limite,
            type_by_possession__in=TIPO_POSSE["aposentados"],  # , matricula=4043
        ).exclude(
            movimentacaopessoal__movimentacaoposse__benefitmovement__benefit_role__pk__in=ignora_tipo_beneficio
        )

    def get_instituidores_pensionistas(self):
        return Servidor.objects.filter(
            created_at__lte=self.data_limite,
            mov_beneficiaries__isnull=False,
            mov_beneficiaries__servidor__type_by_possession__in=TIPO_POSSE[
                "pensionistas"
            ],  # , matricula__in=[1022]
        ).distinct()
