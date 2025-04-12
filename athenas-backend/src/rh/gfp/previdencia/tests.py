# -*- coding: utf-8 -*-

import codecs
import unittest

from django.conf import settings

from contrib.middleware import get_current_user
from contrib.utils import getLogger
from default.testting import AthenasTestCase
from engine.mq.models import Task
from rh.gfp.previdencia.task.igeprev import generator
from rh.tests_api import ModelControllerSetUp

log = getLogger(__name__)


class PrevidenciaSetUp(ModelControllerSetUp):
    pass


def setUpModule():
    PrevidenciaSetUp()


def tearDownModule():
    pass


class IgeprevTestCase(AthenasTestCase):

    avoid = False
    classe = None
    anotacao = None

    @classmethod
    def tearDownClass(cls):
        pass

    # @unittest.skip('skipping test_generator')
    def test_generator(self):
        sheets = [
            934,
            # 864,
            # 860,
            # 855,
            # #COMPLEMENTAR
            # 854,
            # 851,
            # 848,
            # #COMPLEMENTAR
            # 847,
            # 844,
            # #COMPLEMENTAR
            # 840,
            # 842,
            # #COMPLEMENTAR
            # 839,
            # 838,
            # 832,
            # 831,
            # 826,
        ]
        for sheet in sheets:
            task = Task.start(
                generator,
                sheet=sheet,
                user=get_current_user().pk,
                success="""
                <p>Arquivo <span style="font-weight:bold">IGEPREV %(igeprev)s</span> foi gerado com sucesso.
                Para fazer o download clique no
                    <a href="/athenas/GFPSocialSecurityWindowFileGenerator/file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>Este arquivo está disponível para download até dia
                    <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
            )
            while Task.objects.get(uuid=task.uuid).state in (
                "initializing",
                "progress",
            ):
                pass


class SisprevTestCase(unittest.TestCase):

    directory_12017 = "%s/mpeto-igeprev-normal-1-2017" % settings.CACHE_PATH
    directory_112016 = "%s/mpeto-igeprev-normal-11-2016" % settings.CACHE_PATH
    file_job_position = "CARGOS_MP.txt"
    file_busy_job_position = "CARGOS_OCUPADOS_MP.txt"

    @classmethod
    def find_code(cls, lines, code):
        res = False
        for line in lines:
            if line.split("\xdf")[0] == code:
                res = True
        return res

    @unittest.skip("")
    def test_busy_job_position_in_job_position(self):
        """CARGOS
        PROC01ß01o PROCURADOR DE JUSTICA-PGJ-TOßß991ß2ßß1ßEß40ß
        0 - identificador=DadosCargo.get_codigo(cargo),
        1 - nome=unicode(cargo_quadro),
        2 - codigo_cbo=cargo.cbo,
        3 - identificador_orgao=DadosUnidade.get_codigo(
            UnidadeAdministrativa.objects.filter(
                pessoa_juridica__cnpj='01786078000146',
                nome__icontains='PROCURADORIA GERAL DE JUSTI', codigo_igeprev=991).first()),
        4 - aposentadoria=(2 if cargo.indicativo == 'M' else 5),
        5 - acumulacao='',
        6 - tipo_cargo=(2 if cargo_quadro and cargo_quadro.military else 1),
        7 - classificacao=classificacao,
        8 - carga_horaria=(cargo_quadro.carga_horaria if cargo_quadro else 40),
        """
        readed_job_position = codecs.open(
            "%s/%s" % (self.directory_12017, self.file_job_position), "r"
        )
        lines_job_position = readed_job_position.readlines()
        # for line in lines_job_position:
        #     print line.split('\xdf')

        readed_busy_job_position = codecs.open(
            "%s/%s" % (self.directory_12017, self.file_busy_job_position), "r"
        )
        lines_busy_job_position = readed_busy_job_position.readlines()
        for line in lines_busy_job_position:
            if not self.find_code(lines_job_position, line.split("\xdf")[1]):
                print(line.split("\xdf"))

    @unittest.skip("")
    def test_job_position_code(self):
        from rh.models import Cargo

        # readed = codecs.open('%s/job_position.csv' % (settings.BASE_DIR), 'r')
        lines_job_position = [
            "36 | ASSISTENTE ADMINISTRATIVO-PMP-TO |XXXADM|",
            "121 | ASSISTENTE ADMINISTRATIVO-PMP-TO |XXXADM|XXXADM1",
            "82 | PROMOTOR DE JUSTIÇA 2A ENTRÂNCIA-PGJ-TO | PROM2E |",
            "162 | PROMOTOR DE JUSTIÇA DE ALVORADA-PGJ-TO | PROM2E | PRMALV",
            "163 | PROMOTOR DE JUSTIÇA DE ANANÁS-PGJ-TO | PROM2E | PRMANA",
            "164 | PROMOTOR DE JUSTIÇA DE ARAGUAÇU-PGJ-TO | PROM2E | PRMAGU",
            "165 | PROMOTOR DE JUSTIÇA DE ARAPOEMA-PGJ-TO | PROM2E | PRMAPA",
            "166 | PROMOTOR DE JUSTIÇA DE AUGUSTINÓPOLIS-PGJ-TO | PROM2E | PRMAUS",
            "167 | PROMOTOR DE JUSTIÇA DE COLMÉIA-PGJ-TO | PROM2E | PRMCOL",
            "168 | PROMOTOR DE JUSTIÇA DE CRISTALÂNDIA-PGJ-TO | PROM2E | PRM01CRT",
            "169 | PROMOTOR DE JUSTIÇA DE FILADÉLFIA-PGJ-TO | PROM2E | PRMFIL",
            "170 | PROMOTOR DE JUSTIÇA DE FORMOSO DO ARAGUAIA-PGJ-TO | PROM2E | PRMFMO",
            "171 | PROMOTOR DE JUSTIÇA DE ITAGUATINS-PGJ-TO | PROM2E | PRMITA",
            "172 | PROMOTOR DE JUSTIÇA DE MIRANORTE-PGJ-TO | PROM2E | PRMMIR",
            "173 | PROMOTOR DE JUSTIÇA DE NATIVIDADE-PGJ-TO | PROM2E | PRMNAT",
            "174 | PROMOTOR DE JUSTIÇA DE PALMEIRÓPOLIS-PGJ-TO | PROM2E | PRMPAL",
            "175 | PROMOTOR DE JUSTIÇA DE PARANÃ-PGJ-TO | PROM2E | PRMPRN",
            "176 | PROMOTOR DE JUSTIÇA DE PEIXE-PGJ-TO | PROM2E | PRMPEX",
            "177 | PROMOTOR DE JUSTIÇA DE XAMBIOÁ-PGJ-TO | PROM2E | PRMXAM",
            "81 | PROMOTOR DE JUSTIÇA 1A ENTRÂNCIA-PGJ-TO | PROM1E |",
            "148 | PROMOTOR DE JUSTIÇA DE ALMAS-PGJ-TO | PROM1E | PRMALM",
            "149 | PROMOTOR DE JUSTIÇA DE ARAGUACEMA-PGJ-TO | PROM1E | PRMAGM",
            "150 | PROMOTOR DE JUSTIÇA DE AURORA DO TOCANTINS-PGJ-TO | PROM1E | PRMAUR",
            "151 | PROMOTOR DE JUSTIÇA DE AXIXÁ DO TOCANTINS-PGJ-TO | PROM1E | PRMAXX",
            "152 | PROMOTOR DE JUSTIÇA DE FIGUEIRÓPOLIS-PGJ-TO | PROM1E | PRMFIG",
            "153 | PROMOTOR DE JUSTIÇA DE GOIATINS-PGJ-TO | PROM1E | PRMGOI",
            "154 | PROMOTOR DE JUSTIÇA DE ITACAJÁ-PGJ-TO | PROM1E | PRMITA",
            "155 | PROMOTOR DE JUSTIÇA DE MONTE DO CARMO-PGJ-TO | PROM1E | PRMMON",
            "156 | PROMOTOR DE JUSTIÇA DE NAZARÉ-PGJ-TO | PROM1E | PRMNAZ",
            "157 | PROMOTOR DE JUSTIÇA DE NOVO ACORDO-PGJ-TO | PROM1E | PRMNAC",
            "158 | PROMOTOR DE JUSTIÇA DE PIUM-PGJ-TO | PROM1E | PRMPIU",
            "159 | PROMOTOR DE JUSTIÇA DE PONTE ALTA DO TOCANTINS-PGJ-TO | PROM1E | PRMPNT",
            "160 | PROMOTOR DE JUSTIÇA DE TOCANTÍNIA-PGJ-TO | PROM1E | PRMTNI",
            "161 | PROMOTOR DE JUSTIÇA DE WANDERLÂNDIA-PGJ-TO | PROM1E | PRMWAN",
            "315 | CIRURGIAO DENTISTA-SESAU-TO | XXXCDE |",
            "147 | CIRURGIAO DENTISTA-PMP-TO | XXXCDE | XXXCDE1",
            "239 | 1° PROMOTOR DE JUSTIÇA DE ARAGUATINS-PGJ-TO | PROM3E | PRM01AGS",
            "283 | 2° PROMOTOR DE JUSTIÇA DE ARAGUATINS-PGJ-TO | PROM3E | PRM02AGS",
            "262 | 30°  PROMOTOR DE JUSTIÇA DA CAPITAL-PGJ-TO | PROM3E | PRM29CAP",
            "83 | PROMOTOR DE JUSTIÇA 3A ENTRÂNCIA-PGJ-TO | PROM3E |",
            "75 | PROCURADOR DE JUSTIÇA-PGJ-TO | PROC |",
            "263 | PROCURADOR GERAL DE JUSTIÇA DO ESTADO DO TOCANTINS-PGJ-TO | PROC | PROCGERAL",
            "264 | SUBPROCURADOR GERAL DE JUSTIÇA-PGJ-TO | PROC | PROCGERALSUB",
        ]
        for line in lines_job_position:
            buff = line.replace("\n", "")
            buff = line.split("|")
            print(buff)
            if len(buff) > 3:
                buff[0] = buff[0].replace(" ", "")
                buff[3] = buff[3].replace(" ", "")
                print(buff[0])
                if Cargo.objects.filter(codigo=buff[3]).exists():
                    print("ENCONTRADO", buff[3])
                    print("-----------------------------")
                else:
                    Cargo.objects.filter(pk=buff[0]).update(codigo=buff[3])

    def test(self):
        from rh.models import Servidor
        from rh.gfp.models import Folha, FolhaEvento

        print("")
        registry = [
            136816,
            17697,
            3190,
            5090,
            16097,
            1189,
            989,
            389,
            8091,
            15794,
            6791,
            4191,
        ]

        _total_base_value = 0
        _total_contribution = 0
        _total_employer_contribution = 0

        for employee in Servidor.objects.filter(matricula__in=registry):
            print(employee.matricula)
            # sheet = Folha.objects.get(pk=893)  # 032018
            sheet = Folha.objects.get(pk=880)  # 122017
            if employee.matricula == 136816:
                sheet = Folha.objects.get(pk=870)  # 122017
            fe = FolhaEvento.objects.filter(
                contracheque__servidor=employee,
                folha__pk=sheet.pk,
                folha__periodo__mes=sheet.periodo.mes,
                folha__periodo__ano=sheet.periodo.ano,
            )

            base_value = 0
            contribution = 0
            employer_contribution = 0

            event_to_filter = ["900", "902", "905"]
            for sheet_event in fe.filter(
                evento__genre_event__genre_number__in=event_to_filter
            ):
                base_value = sheet_event.valor_base or 0
                contribution = sheet_event.value or 0
                employer_contribution = sheet_event.employer_contribution or 0

                _total_base_value += base_value
                _total_contribution += contribution * -1
                _total_employer_contribution += employer_contribution * -1

            print("base_value", base_value)
            print("contribution", contribution)
            print("employer_contribution", employer_contribution)
            print("---------------------------------------------")

        # print('_total_base_value', _total_base_value)
        # print('_total_contribution', _total_contribution)
        # print('_total_employer_contribution', _total_employer_contribution)
