# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

from django.db.models import Q, signals

from contrib.utils import DateUtils, getLogger
from default.testting import AthenasTestCase
from rh.afastamento.models import (
    ACTIVE,
    FINISHED,
    AfastamentoCompeticao,
    AfastamentoCursoConcurso,
    AfastamentoDeslocamento,
    AfastamentoEleitoral,
    AfastamentoEstudar,
    AfastamentoMandatoEletivo,
    AfastamentoMissao,
    AfastamentoOutroOrgao,
    AfastamentoPrisao,
    AfastamentoServirJuri,
    AfastamentoTreinamento,
    AusenciaCasamento,
    AusenciaConclusao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
    AusenciaFalecimento,
    AusenciaNascimento,
    BaseLicencaAfastamento,
    FeriasAfastamento,
    FolgaEleitoral,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaDoencaPessoaFamilia,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    LicencaMaternidade,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
    Recesso,
    Viagem,
)
from rh.const import CANCELADO, ENCERRADO
from rh.models import (
    DeclaracaoAtividade,
    Lotacao,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReconducao,
    MovimentacaoRemocaoMembro,
    MovimentacaoTitularizacao,
    Servidor,
    ServidorLotacao,
)
from rh.signals import cache as cache_signals
from rh.signals import lotacao as lotacao_signals
from rh.tests_api import RHConfiguracaoTests

log = getLogger(__name__)


def setUpModule():
    RHConfiguracaoTests.setUpModule()


def tearDownModule():
    RHConfiguracaoTests.tearDownModule()


class SignalsTestCase(AthenasTestCase):

    avoid = False
    classe = None
    anotacao = None

    def test_desativa(self):
        query = MovimentacaoDesligamento.objects.filter()[0:1]
        for movimentacao in query:
            signals.post_save.send(sender=movimentacao.__class__, instance=movimentacao)

    def test_refactoring_atualiza_cache_ativo(self):
        movimentacao = DeclaracaoAtividade.objects.latest("pk")
        cache_signals.atualiza_cache_ativo(
            sender=movimentacao.__class__, instance=movimentacao
        )

        movimentacao = MovimentacaoPosse.objects.latest("pk")
        cache_signals.atualiza_cache_ativo(
            sender=movimentacao.__class__, instance=movimentacao
        )

        try:
            movimentacao = MovimentacaoReconducao.objects.latest("pk")
            cache_signals.atualiza_cache_ativo(
                sender=movimentacao.__class__, instance=movimentacao
            )
        except MovimentacaoReconducao.DoesNotExist:
            pass
        except Exception as e:
            raise e

    def test_refactoring_atualiza_cache_tipo(self):
        movimentacao = DeclaracaoAtividade.objects.latest("pk")
        cache_signals.atualiza_cache_tipo(
            sender=movimentacao.__class__, instance=movimentacao
        )

        movimentacao = MovimentacaoPosse.objects.latest("pk")
        cache_signals.atualiza_cache_tipo(
            sender=movimentacao.__class__, instance=movimentacao
        )

        try:
            movimentacao = MovimentacaoReconducao.objects.latest("pk")
            cache_signals.atualiza_cache_tipo(
                sender=movimentacao.__class__, instance=movimentacao
            )
        except MovimentacaoReconducao.DoesNotExist:
            pass
        except Exception as e:
            raise e

    def test_lotacao_mudanca_lotacao(self):
        movimentacao = MovimentacaoRemocaoMembro.objects.latest("pk")
        lotacao_signals.mudanca_lotacao(
            sender=movimentacao.__class__, instance=movimentacao
        )
        movimentacao = MovimentacaoPromocao.objects.latest("pk")
        lotacao_signals.mudanca_lotacao(
            sender=movimentacao.__class__, instance=movimentacao
        )
        movimentacao = MovimentacaoTitularizacao.objects.latest("pk")
        lotacao_signals.mudanca_lotacao(
            sender=movimentacao.__class__, instance=movimentacao
        )

    def test_lotacao_atualizar_ativo(self):
        movimentacao = ServidorLotacao.objects.latest("pk")
        lotacao_signals.atualizar_ativo(
            sender=movimentacao.__class__, instance=movimentacao
        )


class AfastamentoTestCase(SignalsTestCase):

    @unittest.skip("skipping test")
    def test_atualizar_estado(self):
        for afastamento in FeriasAfastamento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in Viagem.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in Recesso.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in FolgaEleitoral.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaSaude3Dias.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaSaude30Dias.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaSaudeJuntaMedica.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaDoencaPessoaFamilia.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaMaternidade.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaAdocao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaAfastamentoConjuge.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaServicoMilitar.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaAtividadePolitica.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaCapacitacao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaInteresseParticular.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in LicencaMandatoClassista.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoOutroOrgao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoMandatoEletivo.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoEstudar.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoMissao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoEleitoral.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoServirJuri.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoTreinamento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoDeslocamento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoCompeticao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoCursoConcurso.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AfastamentoPrisao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaDoacaoSangue.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaEleitor.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaCasamento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaNascimento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaFalecimento.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
        for afastamento in AusenciaConclusao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)

    @unittest.skip("skipping test")
    def test_anotacao_post_save(self):
        for afastamento in LicencaSaudeJuntaMedica.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
            for prorrogacao in afastamento.prorrogacao.filter().exclude(
                estado__in=(ENCERRADO, CANCELADO)
            ):
                self.assertEqual(prorrogacao.save(), None)
        for afastamento in LicencaDoencaPessoaFamilia.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
            for prorrogacao in afastamento.prorrogacao.filter().exclude(
                estado__in=(ENCERRADO, CANCELADO)
            ):
                self.assertEqual(prorrogacao.save(), None)
        for afastamento in LicencaMaternidade.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
            for prorrogacao in afastamento.prorrogacao.filter().exclude(
                estado__in=(ENCERRADO, CANCELADO)
            ):
                self.assertEqual(prorrogacao.save(), None)
        for afastamento in LicencaAdocao.objects.filter().exclude(
            estado__in=(ENCERRADO, CANCELADO)
        ):
            self.assertEqual(afastamento.save(), None)
            for prorrogacao in afastamento.prorrogacao.filter().exclude(
                estado__in=(ENCERRADO, CANCELADO)
            ):
                self.assertEqual(prorrogacao.save(), None)


class EmployeeFireChangeVacationTestCase(unittest.TestCase):

    def change_vacation_by_fire(self):
        from rh.ferias.models import (
            PeriodoAquisitivoServidorUsufruto,
            PASU_HOMOLOGADO,
            PASU_FRUINDO,
            PASU_FRUIDO,
            PAS_INDENIZADA,
        )

        # employee = Servidor.objects.get(matricula=95909)
        # fired = MovimentacaoDesligamento.objects.filter(servidor=employee)
        # print fired.last()
        # print fired.last().save()
        # print
        for fired in MovimentacaoDesligamento.objects.filter(
            Q(data_desligamento__gte=datetime(2017, 6, 1))
        ).order_by(
            "-data_desligamento"
        ):  # [0:80]:
            employee = fired.servidor
            possessions = MovimentacaoPosse.objects.filter(
                Q(servidor=employee)
                & (
                    Q(data_desligamento__gt=fired.data_desligamento)
                    | Q(data_desligamento=None)
                )
            ).exclude(pk=fired.movimentacao_posse.pk)
            if not possessions.exists():
                pasus = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    periodo_aquisitivo_servidor__servidor=fired.servidor,
                    data_inicio__gte=fired.data_desligamento,
                    estado__in=(PASU_HOMOLOGADO, PASU_FRUINDO, PASU_FRUIDO),
                )
                print(possessions.exists(), fired)
                for pasu in pasus:
                    print("Dias pagos: %s" % pasu.pas.paid_days, pasu)
                    if pasu.pas.estado == PAS_INDENIZADA:
                        print("PAS INDENIZADA")
                print("--------------------------------")
                fired.save()
            """
                DUAS PERGUNTAS:
                    - ALTERAR PARA ÉPOCA OPORTUNA MESMO O PAS ESTEJA INDENIZADO

                    heloisa casado - 07/07/2017
            """
