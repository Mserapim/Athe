# -*- coding: utf-8 -*-

import unittest

from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.task.sicapap import sicap_generator
from rh.tests_api import RHConfiguracaoTests

log = getLogger(__name__)


def setUpModule():
    RHConfiguracaoTests.setUpModule()


def tearDownModule():
    RHConfiguracaoTests.tearDownModule()


class SicapTestCase(unittest.TestCase):

    def test_sicap_generator(self):
        try:
            print("test_sicap_generator")
            Task.start(
                sicap_generator,
                year=2018,
                months=[2],
                user=get_current_user().pk,
                success="""<p>Arquivo <span style="font-weight:bold">SICAP AP %(sicapap)s</span> foi gerado com sucesso.
                Para fazer o download clique no <a href="/athenas/RHSicapApWindowGenerator/file/?uuid=%(uuid)s">link</a>.
    </p>
    <p>Este arquivo está disponível para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
            )
            print("test_sicap_generator end")
        except Exception as err:
            print(err)
            log.exception(err)

    # @unittest.skip("skipping test_construtor: expensive MAY USE FOR SICAP TESTS")
    def test_construtor(self):
        # SicapBuilder(quarter=3, year=2016)
        pass


# N 405 1998
# N 406 1998
# N 1833 2010
# N 3989 2006
# N 4028 2012
# N 4924 2006
# N 6779 2012
# N 8018 1998
# N 11949 1997
# for fe in FolhaEvento.objects.filter(
#                 # Q(servidor__matricula__in=(94109, )) &
#                 # ~Q(evento__config_transparencia=None) &
#                 Q(folha__periodo__mes__gte=1) &
#                 Q(folha__periodo__mes__lte=4) &
#                 Q(folha__periodo__ano=2014)).order_by('servidor', 'folha__periodo__mes'):
#     if fe.evento.config_transparencia is None:
#         print fe.evento.config_transparencia, fe.valor, fe, fe.folha.periodo.mes, fe.folha.periodo.ano

# for e in Evento.objects.filter().order_by('titulo'):
#     if e.config_transparencia is None:
#         print e

# data_inicio = datetime(2014, 1, 1)
# data_fim = datetime(2014, 4, 30)

# print DateUtils.date_to_str(data_inicio)
# print DateUtils.date_to_str(data_fim)

# filtro_prorrogacao = (
#     Q(baselicencaafastamento__afastamento__afastamentooutroorgao__prorrogacao__data_inicio__gte=data_inicio) &
#     Q(baselicencaafastamento__afastamento__afastamentooutroorgao__prorrogacao__data_inicio__lte=data_fim))

# filtro_afastamentooutroorgao = (
#     ((Q(baselicencaafastamento__afastamento__afastamentooutroorgao__data_inicio__gte=data_inicio) &
#         Q(baselicencaafastamento__afastamento__afastamentooutroorgao__data_inicio__lte=data_fim)) |
#         filtro_prorrogacao
#     ) & ~Q(baselicencaafastamento__afastamento__afastamentooutroorgao__estado=CANCELADO))

# movs = MovimentacaoPessoal.objects.filter(filtro_afastamentooutroorgao)

# print movs.count()

# for m in movs:
#     prorrogacao = m.baselicencaafastamento.prorrogacao.filter(Q(data_inicio__gte=data_inicio) & Q(data_inicio__lte=data_fim))
#     if prorrogacao.exists():
#         data_inicio = prorrogacao.latest('data_inicio').data_inicio
#         data_fim = prorrogacao.latest('data_inicio').data_fim
#     else:
#         data_inicio = m.baselicencaafastamento.data_inicio
#         data_fim = m.baselicencaafastamento.data_fim
#     print DateUtils.date_to_str(data_inicio), DateUtils.date_to_str(data_fim), m.baselicencaafastamento

# SicapBuilder(quarter=3, year=2014)
# for cargo in Cargo.objects.filter(pk__in=[25, 301, 30, 33, 297, 89]):
#     try:
#         print '-----------------------------------'
#         print cargo
#         print cargo, cargo.quadro_set.filter()[0].movimentacaoposse_set.filter(ativo=True)
#         # salario = cargo.get_salarios(data_inicio=datetime(2014, 9, 1))
#         # print salario
#         for tabelas in TabelaSalarial.objects.filter(estrutura_salarial__cargos_estrutura__cargo=cargo):#.exclude(
#             #     models.Q(data_vigencia_inicio__gt=data_fim) |
#             #     (
#             #         ~models.Q(data_vigencia_fim=None) &
#             #         models.Q(data_vigencia_fim__lt=data_inicio)
#             #     )
#             # ).order_by('-data_vigencia_inicio')
#             print tabelas
#     except Exception as err:
#         print unicode(err)

# def test_construtor(self):
#     SicapBuilder(quarter=1, year=2014)

# def test_movimentacao(self):

#     print 'APOSENTADORIA'
#     for aposentadoria in rh_models.MovimentacaoAposentadoria.objects.filter(servidor__matricula=2990):
#         print aposentadoria.pk, aposentadoria
#     print 'DESLIGAMENTO'
#     for desligamento in rh_models.MovimentacaoDesligamento.objects.filter(servidor__matricula=2990):
#         print desligamento.pk, desligamento
#         if rh_models.MovimentacaoAposentadoria.objects.filter(pk=desligamento.pk).exists():
#             print 'aposentou'

# servidor = rh_models.Servidor.objects.filter()
