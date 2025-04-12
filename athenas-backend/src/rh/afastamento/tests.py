# -*- coding: utf-8 -*-

import codecs
import unittest
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, getLogger
from default.testting import AthenasTestCase
from mixer.backend.django import mixer
from rh.afastamento.models import (
    Afastamento,
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
    Ausencia,
    AusenciaCasamento,
    AusenciaConclusao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
    AusenciaFalecimento,
    AusenciaNascimento,
    BaseLicencaAfastamento,
    FeriasAfastamento,
    FolgaAniversario,
    FolgaCompensacao,
    Licenca,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaDoencaPessoaFamilia,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    LicencaMaternidade,
    LicencaSaude,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
    Recesso,
    Viagem,
)
from rh.const import (
    ACTIVE,
    ALTERACAO,
    CANCELADO,
    CANCELED,
    FINISHED,
    INTERRUPCAO,
    MOVED_AWAY,
    REVOGACAO,
    SCHEDULED,
    TIPO_BASE_LICENCA_AFASTAMENTO,
)
from rh.models import (
    AnotacaoAfastamento,
    AnotacaoAusencia,
    AnotacaoLicenca,
    Lotacao,
    MovimentacaoPosse,
    MovimentacaoSubstituicaoMembro,
    Publicacao,
    Servidor,
    ServidorLotacao,
)

# from rh.tests_api import RHConfiguracaoTests
from rh.tests_api.utils import mock

log = getLogger(__name__)


def setUpModule():
    # RHConfiguracaoTests.setUpModule()
    pass


def tearDownModule():
    # RHConfiguracaoTests.tearDownModule()
    pass


class GestorAfastamentoTestCase(AthenasTestCase):

    avoid = False
    classe = BaseLicencaAfastamento

    @classmethod
    def tearDownClass(cls):
        pass


def validate_publicacao(self):
    if self.publicacao is None:
        self.publicacao = mock(model=Publicacao, query=(~Q(data_vigencia=None)))
    return True


def validate_posse(self):
    if self.movimentacao_posse is None:
        self.movimentacao_posse = (
            self.servidor.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="EF"
            ).latest("data_exercicio")
            if self.servidor.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="EF"
            ).exists()
            else None
        )
    return True


def validate_lotacao_fora_organograma(self):
    return True


class BaseLicencaAfastamentoTestCase(AthenasTestCase):

    avoid = False
    classe = BaseLicencaAfastamento

    def setUp(self):
        # print '--------------setUp------------'
        self.afastamento_vigente = None
        self.afastamento_vigente_criado = False
        try:
            self.afastamento_vigente = self.classe.objects.filter(
                self.filtro_vigente()
            ).latest("pk")
        except Exception:
            try:
                self.afastamento_vigente = mock(
                    model=self.classe,
                    data_inicio=datetime.now().date(),
                    data_prevista=datetime.now().date(),
                    estado=2,
                )
                self.afastamento_vigente_criado = True
            except Exception:
                print("Não foi possível gerar objeto: %s" % self.classe)

        self.afastamento_iniciado = None
        self.afastamento_iniciado_criado = False
        try:
            self.afastamento_iniciado = (
                self.classe.objects.filter(self.filtro_iniciado())
                .exclude(estado=CANCELED)
                .exclude(alteracao=CANCELED)
                .latest("pk")
            )
        except Exception:
            try:
                self.afastamento_iniciado = mock(
                    model=self.classe,
                    data_inicio=datetime.now().date(),
                    data_prevista=datetime.now().date(),
                    estado=2,
                )
                self.afastamento_iniciado_criado = True
            except Exception:
                print("Não foi possível gerar objeto: %s" % self.classe)

        # print 'self.afastamento_iniciado'
        # print self.afastamento_iniciado_criado
        # print self.show_afastamento(self.afastamento_iniciado)

        self.afastamento_encerrado = None
        self.afastamento_encerrado_criado = False
        try:
            self.afastamento_encerrado = self.classe.objects.filter(
                self.filtro_finalizado()
            ).latest("pk")
        except Exception:
            try:
                self.afastamento_encerrado = mock(
                    model=self.classe,
                    data_inicio=datetime.now().date() - relativedelta(days=3),
                    data_prevista=datetime.now().date() - relativedelta(days=1),
                    estado=3,
                )
                self.afastamento_encerrado_criado = True
            except Exception:
                print("Não foi possível gerar objeto: %s" % self.classe)

        self.afastamento = None
        self.afastamento_criado = False
        try:
            self.afastamento = (
                BaseLicencaAfastamento.objects.filter()
                .exclude(data_fim=None)
                .latest("data_fim")
                .instancia_modelo
            )
        except Exception:
            try:
                self.afastamento = mock(
                    model=self.classe,
                    data_inicio=datetime.now().date() - relativedelta(days=3),
                    data_prevista=datetime.now().date() - relativedelta(days=1),
                )
                self.afastamento_criado = True
            except Exception:
                print("Não foi possível gerar objeto: %s" % self.classe)

    def tearDown(self):
        # print '-----tearDown------'
        try:
            if (
                self.afastamento_vigente_criado is True
                and self.afastamento_vigente is not None
            ):
                self.afastamento_vigente.delete()
            if (
                self.afastamento_iniciado_criado is True
                and self.afastamento_iniciado is not None
            ):
                self.afastamento_iniciado.delete()
            if (
                self.afastamento_encerrado_criado is True
                and self.afastamento_encerrado is not None
            ):
                self.afastamento_encerrado.delete()
            if self.afastamento_criado is True and self.afastamento is not None:
                self.afastamento.delete()
        except Exception:
            # print(err)
            pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def filtro_vigente(self, hoje=None):
        hoje = datetime.now().date() if not hoje else hoje
        return Q(data_inicio__gte=hoje) & Q(Q(data_fim__gte=hoje) | Q(data_fim=None))

    @classmethod
    def filtro_iniciado(self, hoje=None):
        hoje = datetime.now().date() if not hoje else hoje
        return Q(data_inicio__lte=hoje) & (Q(data_fim__gte=hoje) | Q(data_fim=None))

    @classmethod
    def filtro_finalizado(self, hoje=None):
        hoje = datetime.now().date() if not hoje else hoje
        return Q(data_fim__lt=hoje)

    @unittest.skip("skipping 1 test_validate_data_prevista")
    def test_validate_data_prevista(self):
        if self.afastamento_vigente is not None:
            self.afastamento_vigente.alteracao = REVOGACAO
            self.afastamento_vigente.data_fim = self.afastamento_vigente.data_prevista
            if self.afastamento_vigente.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_vigente.validate_data_prevista,
                )

            self.afastamento_vigente.alteracao = None
            self.afastamento_vigente.data_fim = (
                self.afastamento_vigente.data_prevista + relativedelta(days=1)
            )
            if self.afastamento_vigente.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_vigente.validate_data_prevista,
                )

            if self.afastamento_vigente.data_prevista is None:
                self.afastamento_vigente.data_prevista = datetime.now().date()
                self.afastamento_vigente.save()
                self.setUp()
            self.afastamento_vigente.data_prevista = (
                self.afastamento_vigente.data_prevista + relativedelta(days=1)
            )
            if self.afastamento_vigente.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_vigente.validate_data_prevista,
                )

        if self.afastamento_encerrado is not None:
            self.afastamento_encerrado.alteracao = ALTERACAO
            self.afastamento_encerrado.data_prevista = (
                self.afastamento_encerrado.data_fim
            )
            if self.afastamento_encerrado.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_encerrado.validate_data_prevista,
                )

            # VALIDAR: DATA DE FIM DIFERENTE DA PREVISTA COM DATA FIM SENDO MAIOR
            self.afastamento_encerrado.alteracao = None
            self.afastamento_encerrado.data_fim = (
                self.afastamento_encerrado.data_prevista + relativedelta(days=3)
            )
            if self.afastamento_encerrado.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_encerrado.validate_data_prevista,
                )

            if self.afastamento_encerrado.data_prevista is None:
                self.afastamento_encerrado.data_prevista = datetime.now().date()
                self.afastamento_encerrado.save()
                self.setUp()
            self.afastamento_encerrado.data_prevista = (
                self.afastamento_encerrado.data_prevista + relativedelta(days=1)
            )
            if self.afastamento_encerrado.nao_validar_data_prevista() is False:
                self.assertRaises(
                    self.classe.BaseLicencaAfastamentoExceptionBase,
                    self.afastamento_encerrado.validate_data_prevista,
                )

    @unittest.skip("skipping 1 test_validate_periodo")
    def test_validate_periodo(self):
        if self.afastamento is not None and not hasattr(
            self.afastamento, "feriasafastamento"
        ):
            afastamento_novo = self.classe(
                servidor=self.afastamento.servidor,
                data_inicio=self.afastamento.data_inicio,
            )
            self.assertRaises(
                self.classe.ExceptionBasePeriodo, afastamento_novo.validate_periodo
            )

            afastamento_novo.data_fim = self.afastamento.data_inicio + relativedelta(
                days=3
            )
            self.assertRaises(
                self.classe.ExceptionBasePeriodo, afastamento_novo.validate_periodo
            )

            data_inicio = self.afastamento.data_fim + relativedelta(days=1)
            data_fim = self.afastamento.data_fim + relativedelta(days=3)
            # TENHO QUE GARANTIR QUE NÃO HAJA PERÍODO CONFLITANDO, POIS QUERO TESTAR A VALIDAÇÃO DO INTERVALO!
            # HORA, SE QUER TESTAR A VALIDAÇÃO DE INTERVALO NÃO É AQUI, CONTUDO, ESTA VALIDAÇÃO LEVA EM CONSIDERAÇÃO ALGUMAS
            # INFORMAÇÕES POR ISSO DEVE SER TESTADA ASSIM MESMO!
            afastamento_novo.data_inicio = data_inicio
            afastamento_novo.data_fim = data_fim

            self.assertIs(afastamento_novo.validate_periodo(), True)

    def test_validate_save_servidor(self):
        pass

    def test_validate_delete_servidor(self):
        pass

    def test_validate_save_ativo(self):
        pass

    def test_validate_delete_membro(self):
        pass

    def test_validate_delete_ativo(self):
        pass

    def test_validate_data_inicio_maior_data_fim(self):
        pass

    def test_validate_delete(self):
        pass

    @unittest.skip("skipping 1 test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        afastamento = self.classe.objects.filter(self.filtro_iniciado())
        if afastamento.exists():
            afastamento = afastamento.latest("pk")
            # print 'test_validate_afastamento_iniciado', self.classe
            # print afastamento
            self.assertRaises(
                self.classe.ErroAfastamentoIniciado,
                afastamento.validate_afastamento_iniciado,
            )

        afastamento = self.classe.objects.filter(self.filtro_finalizado())
        if afastamento.exists():
            afastamento = afastamento.latest("pk")
            self.assertIs(afastamento.validate_afastamento_iniciado(), True)

    @unittest.skip("skipping 1 test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        afastamento = self.classe.objects.filter(self.filtro_finalizado())
        if afastamento.exists():
            afastamento = afastamento.latest("pk")
            self.assertRaises(
                self.classe.BaseLicencaAfastamentoExceptionBase,
                afastamento.validate_afastamento_finalizado,
            )

        afastamento = self.classe.objects.filter(self.filtro_iniciado())
        if afastamento.exists():
            afastamento = afastamento.latest("pk")
            self.assertIs(afastamento.validate_afastamento_finalizado(), True)

    @unittest.skip("skipping 1 test_alteracao_ferias")
    def test_alteracao_ferias(self):
        valor_resposta = True
        if (
            self.classe.objects.filter(self.filtro_iniciado())
            .exclude(data_fim=None)
            .exists()
        ):
            afastamento = (
                self.classe.objects.filter(self.filtro_iniciado())
                .exclude(data_fim=None)
                .latest("pk")
            )
            valor_resposta = BaseLicencaAfastamento.validate_alteracao_ferias(
                afastamento
            )
            assert (
                afastamento.alteracao_ferias(afastamento=afastamento) is valor_resposta
            )

    @unittest.skip("skipping 1 test_validate_save_membro")
    def test_validate_save_membro(self):

        if self.classe == FeriasAfastamento:

            # MEMBRO
            afastamento = None
            try:
                afastamento = self.classe.objects.filter(
                    Q(servidor__tipo="M") & self.filtro_iniciado()
                ).latest("data_inicio")
            except Exception:
                pass
            if afastamento:
                assert afastamento.condicao_validate_save_ativo() is True
                # agendado_arquimedes_old = afastamento.agendado_arquimedes
                # BaseLicencaAfastamento.objects.filter(pk=afastamento.pk)
                # afastamento.agendado_arquimedes is False
                # self.assertRaises(self.classe.BaseLicencaAfastamentoExceptionBase, afastamento.validate_save_ativo)
                # TODO: PARA REALIZAR O TESTE ABAIXO É NECESSÁRIO GARANTIR QUE O AFASTAMENTO ESTÁ NO ARQUIMEDES
                # agendado = afastamento.solicita_agendamento_arquimedes()
                # assert self.classe.objects.get(pk=afastamento.pk).agendado_arquimedes == agendado

            # SERVIDOR
            afastamento = None
            try:
                afastamento = self.classe.objects.filter(
                    Q(servidor__tipo="S") & self.filtro_iniciado()
                ).latest("data_inicio")
            except Exception:
                pass
            if afastamento:
                assert afastamento.condicao_validate_save_ativo() is False

    @unittest.skip("skipping 1 test_atualizar_estado")
    def test_atualizar_estado(self):
        # SCHEDULED
        # ACTIVE
        # FINISHED
        # CANCELED

        afa = self.classe.objects.filter(estado=CANCELED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=SCHEDULED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=CANCELED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=ACTIVE)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=CANCELED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=FINISHED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=SCHEDULED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=CANCELED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=SCHEDULED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=ACTIVE)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=SCHEDULED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=FINISHED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=ACTIVE)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=CANCELED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=ACTIVE)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=SCHEDULED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=ACTIVE)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=FINISHED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=FINISHED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=CANCELED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=FINISHED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=SCHEDULED)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

        afa = self.classe.objects.filter(estado=FINISHED)
        if afa.exists():
            afa = afa.latest("pk")
            # print afa.__class__, afa, DateUtils.date_to_str(afa.data_inicio), DateUtils.date_to_str(afa.data_fim), ' - ESTADO:', afa.get_estado_display(), ' - ALTERACAO:', afa.get_alteracao_display()
            estado_atual = afa.estado
            BaseLicencaAfastamento.objects.filter(pk=afa.pk).update(estado=ACTIVE)
            BaseLicencaAfastamento.atualizar_estado(afa)
            afa = self.classe.objects.get(pk=afa.pk)
            assert afa.estado == estado_atual

    # def test_validate_prazo_maximo(self):
    #     if self.afastamento_vigente:
    #         self.afastamento_vigente = instancia.data_inicio + relativedelta(years=5)
    #         self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)

    @unittest.skip("skipping 1 test_verifica_sobreposicao_periodo")
    def test_verifica_sobreposicao_periodo(self):
        if (
            self.afastamento_iniciado
            and self.afastamento_iniciado.data_inicio > datetime.now().date()
        ):
            self.assertRaises(
                self.classe.BaseLicencaAfastamentoExceptionBase,
                self.afastamento_iniciado.verifica_sobreposicao_periodo,
                self.afastamento_iniciado.servidor,
                self.afastamento_iniciado.data_inicio,
                self.afastamento_iniciado.data_fim,
            )

    def test_set_data_fim_por_prorrogacao(self):
        pass

    @unittest.skip("skipping 1 test_anotacao_alteracao")
    def test_anotacao_alteracao(self):
        # afa = self.classe.objects.filter(alteracao=REVOGACAO).exclude(estado=CANCELED).exclude(alteracao=CANCELED)
        afa = self.classe.objects.filter(pk=17260)
        if afa.exists():
            afa = afa.latest("pk")
            print(
                afa,
                DateUtils.date_to_str(afa.data_inicio),
                DateUtils.date_to_str(afa.data_fim),
                " - ESTADO:",
                afa.get_estado_display(),
                " - ALTERACAO:",
                afa.get_alteracao_display(),
            )
            print(afa.anotacao_geral.texto)
            afa.save()

    def test_anotacao(self):
        afa = self.classe.objects.filter()
        if afa.exists():
            afa = afa.latest("pk")
            afa.anotacao()

    @unittest.skip("skipping test_save")
    def test_save(self):
        if self.classe == BaseLicencaAfastamento:
            afas = self.classe.objects.filter()
            did = []
            for afa in afas:
                try:
                    inst = afa.instancia_modelo
                    if inst.__class__ not in did:
                        inst.save()
                        did.append(inst.__class__)
                    if len(did) == len(TIPO_BASE_LICENCA_AFASTAMENTO) - 1:
                        break
                except Exception as err:
                    print(err)

    # tester rh.afastamento.tests -t BaseLicencaAfastamentoTestCase

    # @unittest.skip("skipping test_update_designation_to_substitution")
    def test_update_designation_to_substitution(self):
        validate_publicacao_orig = ServidorLotacao.validate_publicacao
        validate_posse_orig = ServidorLotacao.validate_posse
        validate_lotacao_fora_organograma_orig = (
            ServidorLotacao.validate_lotacao_fora_organograma
        )
        ServidorLotacao.validate_publicacao = validate_publicacao
        ServidorLotacao.validate_posse = validate_posse
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma
        )

        for servidor in Servidor.objects.filter(tipo__in="M", ativo=True):
            if servidor.afastamento_ativo() is False:
                pks = servidor.work_assignment.values("pk")
                ServidorLotacao.objects.filter(pk__in=pks).update(situation=MOVED_AWAY)
                servidor._update_designation_to_substitution()
                assert (
                    ServidorLotacao.objects.filter(pk__in=pks)
                    .exclude(situation__in=(ACTIVE, FINISHED))
                    .exists()
                    is False
                )
                break

        self.afastamento_iniciado = (
            self.classe.objects.filter(self.filtro_iniciado())
            .exclude(servidor__tipo="S")
            .exclude(estado=CANCELED)
        )
        if self.classe == BaseLicencaAfastamento:
            self.afastamento_iniciado = self.afastamento_iniciado.exclude(
                self.classe._query_not_member_departure()
            )
        self.afastamento_iniciado = self.afastamento_iniciado.first()

        if self.afastamento_iniciado:

            self.afastamento_iniciado = self.afastamento_iniciado.instancia_modelo
            self.classe = type(self.afastamento_iniciado)

            pks = self.afastamento_iniciado.servidor.work_assignment.values("pk")
            ServidorLotacao.objects.filter(pk__in=pks).update(situation=ACTIVE)
            self.afastamento_iniciado.servidor._update_designation_to_substitution()
            assert (
                ServidorLotacao.objects.filter(pk__in=pks)
                .exclude(situation=MOVED_AWAY)
                .exists()
                is False
            )

            pks = self.afastamento_iniciado.servidor.work_assignment.values("pk")
            ServidorLotacao.objects.filter(pk__in=pks).update(situation=ACTIVE)
            self.afastamento_iniciado.servidor._update_designation_to_substitution()
            assert (
                ServidorLotacao.objects.filter(pk__in=pks)
                .exclude(situation=MOVED_AWAY)
                .exists()
                is False
            )

            # TESTING DEPARTURE SITUATION CANCELED CHANGING TO ACITVE, FINISHED
            pks = self.afastamento_iniciado.servidor.work_assignment.values("pk")
            alteracao = self.afastamento_iniciado.alteracao
            estado = self.afastamento_iniciado.estado
            self.classe.objects.filter(pk=self.afastamento_iniciado.pk).update(
                estado=CANCELED, alteracao=CANCELED
            )
            self.classe.objects.get(pk=self.afastamento_iniciado.pk).save()
            # self.afastamento_iniciado = self.classe.objects.get(pk=self.afastamento_iniciado.pk)
            self.afastamento_iniciado.servidor._update_designation_to_substitution()
            assert (
                ServidorLotacao.objects.filter(pk__in=pks)
                .exclude(situation=MOVED_AWAY)
                .exists()
                is True
            )

            self.classe.objects.filter(pk=self.afastamento_iniciado.pk).update(
                estado=estado, alteracao=alteracao
            )
            self.classe.objects.get(pk=self.afastamento_iniciado.pk).save()

            self.afastamento_iniciado = self.classe.objects.get(
                pk=self.afastamento_iniciado.pk
            )
            pks = servidor.work_assignment.values("pk")
            self.afastamento_iniciado.servidor._update_designation_to_substitution()
            assert (
                ServidorLotacao.objects.filter(pk__in=pks)
                .exclude(situation=MOVED_AWAY)
                .exists()
                is True
            )

            # #ENDING DEPARTURES AND CHANGING DESIGNATIONS TO ACTIVE, FINISHED
            pks = self.afastamento_iniciado.servidor.work_assignment.values("pk")
            alteracao = self.afastamento_iniciado.alteracao
            estado = self.afastamento_iniciado.estado
            data_fim = self.afastamento_iniciado.data_fim
            self.classe.objects.filter(pk=self.afastamento_iniciado.pk).update(
                data_fim=datetime.now().date() - relativedelta(days=1),
                alteracao=ALTERACAO,
            )
            self.classe.objects.get(pk=self.afastamento_iniciado.pk).save()
            self.afastamento_iniciado.servidor._update_designation_to_substitution()
            assert (
                ServidorLotacao.objects.filter(pk__in=pks)
                .exclude(situation=MOVED_AWAY)
                .exists()
                is True
            )
            self.classe.objects.filter(pk=self.afastamento_iniciado.pk).update(
                data_fim=data_fim, estado=estado, alteracao=alteracao
            )
            self.classe.objects.get(pk=self.afastamento_iniciado.pk).save()
            self.afastamento_iniciado.servidor._update_designation_to_substitution()

        ServidorLotacao.validate_publicacao = validate_publicacao_orig
        ServidorLotacao.validate_posse = validate_posse_orig
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma_orig
        )

    @classmethod
    def show_afastamento(cls, afastamento):
        message = """
            PK:          %s - AFASTAMENTO: %s
            ESTADO:      %s - ALTERACAO:   %s
            MATRICULA:   %s
            INICIO:      %s - FIM:         %s - PREVISTA:    %s""" % (
            afastamento.pk,
            afastamento,
            afastamento.get_estado_display(),
            afastamento.get_alteracao_display(),
            afastamento.servidor.matricula,
            DateUtils.date_to_str(afastamento.data_inicio),
            DateUtils.date_to_str(afastamento.data_fim),
            DateUtils.date_to_str(afastamento.data_prevista),
        )
        log.debug(message)
        print(message)

    @classmethod
    def show_designacao(cls, designacao):
        message = """
            PK: %s - DESIGNACAO: %s - ESTADO: %s
            SERVIDOR: %s
            INICIO: %s - FIM: %s
        """ % (
            designacao.pk,
            designacao,
            designacao.get_situation_display(),
            designacao.servidor,
            (
                DateUtils.date_to_str(designacao.data_vigencia_inicio)
                if designacao.data_vigencia_inicio
                else "----"
            ),
            (
                DateUtils.date_to_str(designacao.data_vigencia_fim)
                if designacao.data_vigencia_fim
                else "----"
            ),
        )
        log.debug(message)
        print(message)


class DepartureManageNewTestCase(unittest.TestCase):
    """
    -testes a serem escritos:
        -criar afastamento e substituições para um membro
            - verificar se o exercício do afastado finalizou corretamente;
            - verificar se o exercício do substituto iniciou corretamente;
            - verificar se o exercício do afastado iniciou corretamente;
            - verificar se o exercício do substituto finalizou corretamente;
        -criar afastamento para atuação em grupo de trabalho/desempenho de função
            - verificar se exercício em "designações de exercício" permaneceu ativa, e as demais finalizadas;
            - criar outro afastamento concomitante:
                - verificar se ele finaliza as designações adicionadas "em exercicio" do afastamento para grupo de trabalho;
                - adicionar exercício para grupo de trabalho ao novo afastamento "em exercicio" e verificar se permanece ativo;
                - verificar se exercício criado para desempenho é afastado corretamente;
        - verificar se os responsáveis estão corretos a cada dança de cadeiras;
    """

    def get_employee_not_departured(
        self,
        start_date=None,
        end_date=None,
        exclude=[],
        owner=False,
        not_substitution=False,
    ):
        employee = None
        for possession in MovimentacaoPosse.objects.filter(
            Q(servidor__tipo="M")
            & Q(quadro__cargo__tipo_lei_cargo="EF")
            & Q(ativo=True)
            & ~Q(quadro__cargo__lotacao_responsavel=None)
        ).exclude(servidor__pk__in=exclude):
            # print possession.servidor, possession.servidor.departures(start_date=start_date, end_date=end_date).exists(), possession.servidor.substitutions_per_date(start_date=start_date, end_date=end_date).exists(), possession.servidor.owner_locations_can_substitute.exists()
            if not possession.servidor.departures(
                start_date=start_date, end_date=end_date
            ).exists():
                employee = possession.servidor
                if (
                    not_substitution
                    and employee.substitutions_per_date(
                        start_date=start_date, end_date=end_date
                    ).exists()
                ):
                    employee = None
            if owner and employee:
                if not employee.owner_locations_can_substitute.exists():
                    employee = None
            if employee:
                break
        return employee

    def test_create_departure_and_substitution(self):
        start_date = datetime.now() - relativedelta(days=3)
        end_work_assignment = start_date - relativedelta(days=1)
        interruption_date = start_date + relativedelta(days=1)
        new_begin_date = (interruption_date + relativedelta(days=1)).date()
        interruption_date = interruption_date.date()
        end_date = (start_date + relativedelta(days=30)).date()
        start_date = start_date.date()
        employee = self.get_employee_not_departured(
            start_date=start_date, end_date=end_date, owner=True, not_substitution=True
        )
        # print('\n---------------------------------------')
        print(
            "\nEmployee departure: %s owner_locations: %s"
            % (employee, employee.owner_locations_can_substitute.exists())
        )
        departure = mixer.blend(
            "afastamento.LicencaSaude30Dias",
            servidor=employee,
            data_inicio=start_date,
            prazo_solicitado=30,
            prazo_concedido=30,
        )
        # print departure
        # print employee.work_assignment
        # print not employee.work_assignment.exclude(pk__in=employee.owner_locations_can_substitute.values('pk')).exists()
        owner_locations_not_active = not employee.work_assignment.exclude(
            pk__in=employee.owner_locations_can_substitute.values("pk")
        ).exists()
        # print employee.owner_locations_can_substitute.exists()
        owner_location = employee.owner_locations_can_substitute.first()

        substitute = self.get_employee_not_departured(
            start_date=start_date, end_date=end_date, exclude=[employee.pk]
        )
        print("Substitute %s" % substitute)
        try:
            mixer.blend(
                "rh.MovimentacaoSubstituicaoMembro",
                afastamento=departure,
                servidor=substitute,
                designation_substituted=owner_location,
                posse=employee.posses_ativas.first(),
                cargo_arquimedes=0,
                servidor_substituido=departure.servidor,
                data_inicio=departure.data_inicio,
                data_prevista_fim=departure.data_fim,
            )
            # print substitution
        except Exception as err:
            print(err)

        substitute_new_work_assigment_active = substitute.work_assignment.filter(
            lotacao=owner_location.lotacao
        ).exists()
        substitute_new_work_assigment_to_delete = substitute.work_assignment.filter(
            lotacao=owner_location.lotacao
        ).exists() and substitute.work_assignment.filter(
            lotacao=owner_location.lotacao
        ).latest(
            "data_vigencia_inicio"
        )

        departure.alteracao = INTERRUPCAO
        departure.data_fim = interruption_date
        departure.save()

        owner_locations_active = not employee.work_assignment.exclude(
            pk__in=employee.owner_locations_can_substitute.values("pk")
        ).exists()
        owner_locations_active_to_delete = (
            employee.get_work_assignment()
            .filter(data_vigencia_inicio=new_begin_date)
            .first()
        )
        # print('owner_locations_active_to_delete')
        # print(owner_locations_active_to_delete)
        substitute_new_work_assigment_not_active = (
            not substitute.work_assignment.filter(
                lotacao=owner_location.lotacao
            ).exists()
        )

        if owner_locations_active_to_delete:
            MovimentacaoSubstituicaoMembro.objects.filter(
                designation_substituted=owner_locations_active_to_delete
            ).update(designation_substituted=None)
            if ServidorLotacao.objects.filter(
                pk=owner_locations_active_to_delete.pk
            ).exists():
                ServidorLotacao.objects.filter(
                    pk=owner_locations_active_to_delete.pk
                ).delete()

        for sub in departure.substituicao.filter():
            if sub.movimentacaosubstituicaomembro.designation_substitute:
                sub.movimentacaosubstituicaomembro.designation_substitute.delete()
        departure.substituicao.filter().delete()
        departure.alteracao = CANCELED
        departure.save()

        if substitute_new_work_assigment_to_delete:
            MovimentacaoSubstituicaoMembro.objects.filter(
                designation_substitute=substitute_new_work_assigment_to_delete
            ).update(designation_substitute=None)
            if ServidorLotacao.objects.filter(
                pk=substitute_new_work_assigment_to_delete.pk
            ).exists():
                ServidorLotacao.objects.filter(
                    pk=substitute_new_work_assigment_to_delete.pk
                ).delete()

        # print employee.get_work_assignment().filter(data_vigencia_fim=end_work_assignment).count()
        employee.get_work_assignment().filter(
            data_vigencia_fim=end_work_assignment
        ).update(data_vigencia_fim=None, changed_by_departure=None)
        # print employee.get_work_assignment().count()
        ServidorLotacao.cmd_atualizar_ativo(
            servidor_lotacao=employee.get_work_assignment().values("pk")
        )

        print(owner_locations_not_active)
        print(substitute_new_work_assigment_active)
        print(owner_locations_active)
        print(substitute_new_work_assigment_not_active)
        assert (
            owner_locations_not_active
            and substitute_new_work_assigment_active
            and owner_locations_active
            and substitute_new_work_assigment_not_active
        )

    # @unittest.skip("skipping test_create_departure_for_group_work")
    def test_create_departure_for_group_work(self):
        log.debug(
            "=====================> test_create_departure_for_group_work <====================="
        )
        print(
            "=====================> test_create_departure_for_group_work <====================="
        )
        start_date = datetime.now() - relativedelta(days=3)
        start_date_health = start_date + relativedelta(days=3)
        start_date_health = start_date_health.date()
        end_date = start_date + relativedelta(days=90)
        end_date = end_date.date()
        # end_work_assignment = start_date - relativedelta(days=1)
        interruption_date = start_date + relativedelta(days=1)
        # new_begin_date = (interruption_date + relativedelta(days=1)).date()
        interruption_date = interruption_date.date()
        end_date = (start_date + relativedelta(days=30)).date()
        start_date = start_date.date()
        employee = self.get_employee_not_departured(
            start_date=start_date, end_date=end_date, owner=True, not_substitution=True
        )
        print("\n---------------------------------------")
        print(
            "Employee departure: %s owner_locations: %s"
            % (employee, employee.owner_locations_can_substitute.exists())
        )
        # work_assignment = employee.work_assignment
        # print(work_assignment)
        work_assignment_pgj = mixer.blend(
            "rh.ServidorLotacao",
            servidor=employee,
            movimentacao_posse=employee.posses_ativas.latest("data_exercicio"),
            lotacao=Lotacao.objects.get(pk=454),
            data_vigencia_inicio=start_date,
            data_vigencia_fim=end_date,
            designacao=True,
        )
        print(work_assignment_pgj)

        departure = mixer.blend(
            "afastamento.AtuacaoGrupoTrabalho",
            servidor=employee,
            data_inicio=start_date,
            data_prevista=end_date,
            data_fim=end_date,
        )
        print(
            "%s => %s à %s"
            % (
                departure,
                DateUtils.date_to_str(departure.data_inicio),
                (
                    DateUtils.date_to_str(departure.data_fim)
                    if departure.data_fim
                    else "----"
                ),
            )
        )
        print("employee.work_assignment", employee.work_assignment)
        # owner_location = employee.owner_locations_can_substitute.first()

        work_assignment_not_active = not employee.work_assignment.exists()
        work_assignment_pgj_not_active = not employee.work_assignment.filter(
            pk=work_assignment_pgj.pk
        ).exists()

        departure.designation_exercise.add(work_assignment_pgj)
        print("employee.work_assignment", employee.work_assignment)

        work_assignment_pgj_active = employee.work_assignment.filter(
            pk=work_assignment_pgj.pk
        ).exists()

        departure_health = mixer.blend(
            "afastamento.LicencaSaude30Dias",
            servidor=employee,
            data_inicio=start_date_health,
            prazo_solicitado=30,
            prazo_concedido=30,
        )
        print(
            "%s => %s à %s"
            % (
                departure_health,
                DateUtils.date_to_str(departure_health.data_inicio),
                (
                    DateUtils.date_to_str(departure_health.data_fim)
                    if departure_health.data_fim
                    else "----"
                ),
            )
        )
        print("employee.work_assignment", employee.work_assignment)
        work_assignment_not_active_after_health = not employee.work_assignment.exists()

        departure_health.designation_exercise.add(work_assignment_pgj)

        work_assignment_active_after_health = employee.work_assignment.exists()

        departure_health.designation_exercise.remove(work_assignment_pgj)

        for sub in departure_health.substituicao.filter():
            if sub.movimentacaosubstituicaomembro.designation_substitute:
                sub.movimentacaosubstituicaomembro.designation_substitute.delete()

        departure_health.substituicao.filter().delete()
        departure_health.alteracao = CANCELED
        departure_health.save()

        for sub in departure.substituicao.filter():
            if sub.movimentacaosubstituicaomembro.designation_substitute:
                sub.movimentacaosubstituicaomembro.designation_substitute.delete()

        departure.substituicao.filter().delete()
        departure.alteracao = CANCELED
        departure.save()

        departure.designation_exercise.remove(work_assignment_pgj)

        work_assignment_pgj.delete()

        print(work_assignment_not_active)
        print(work_assignment_pgj_not_active)
        print(work_assignment_pgj_active)
        print(work_assignment_not_active_after_health)
        print(work_assignment_active_after_health)
        assert (
            work_assignment_not_active
            and work_assignment_pgj_not_active
            and work_assignment_pgj_active
            and work_assignment_not_active_after_health
            and work_assignment_active_after_health
        )

    def verifie_if_member_is_correct_place(self):
        pass


class AfastamentoTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = Afastamento
    anotacao = AnotacaoAfastamento


#     @unittest.skip("skipping test_validate_periodo")
#     def test_validate_periodo(self):
#         pass

#     @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
#     def test_validate_data_fim_publicacao_fim(self):
#         pass

#     @unittest.skip("skipping test_validate_afastamento_iniciado")
#     def test_validate_afastamento_iniciado(self):
#         pass

#     @unittest.skip("skipping test_validate_afastamento_finalizado")
#     def test_validate_afastamento_finalizado(self):
#         pass

# #    @unittest.skip("skipping test_validate_campos_alterados")
#     def test_validate_campos_alterados(self):
# #        afastamento = self.classe.objects.filter(self.filtro_iniciado())[0]
# #        afastamento.data_fim = None
# #        afastamento.publicacao_fim = None
# #        self.assertIs(afastamento.validate_data_fim_publicacao_fim(), True)
#         super(AfastamentoTestCase, self).test_validate_campos_alterados()

#     @unittest.skip("skipping test_criados")
#     def test_criados(self):
#         self.assertGreater(self.classe.objects.count(), 0)

#     def test_validate_publicacao(self):
#         afastamento = Afastamento.objects.filter()[0]
#         afastamento.publicacao_movimentacao = None
#         self.assertRaises(Afastamento.ErroPublicacaoNaoEncontrada, afastamento.validate_publicacao)

#     def test_validate_data_vigencia(self):
#         afastamento = Afastamento.objects.filter()[0]
#         afastamento.publicacao_movimentacao = Publicacao.objects.get(pk=2975)
#         afastamento.publicacao_movimentacao.data_vigencia = None
#         self.assertRaises(Afastamento.ErroVigenciaNaoEncontrada, afastamento.validate_data_vigencia)


class LicencaTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = Licenca
    anotacao = AnotacaoLicenca

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        pass

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        pass


class AusenciaTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = Ausencia
    anotacao = AnotacaoAusencia

    @unittest.skip("skipping test_validate_prazo_maximo")
    def test_validate_prazo_maximo(self):
        self.afastamento_vigente
        self.assertRaises(
            self.classe.ErroPrazoMaximo, self.afastamento_vigente.validate_prazo_maximo
        )

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        pass

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        pass

    @unittest.skip("skipping test_validate_campos_alterados")
    def test_validate_campos_alterados(self):
        pass


class FeriasTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = FeriasAfastamento

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_data_prevista_sem_alteracao_datas_diferentes(self):
        pass

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        pass

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        pass

    @unittest.skip("skipping test_validate_campos_alterados")
    def test_validate_campos_alterados(self):
        pass

    @unittest.skip("skipping test_criados")
    def test_criados(self):
        self.assertGreater(self.classe.objects.count(), 0)


class ViagemTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = Viagem

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        pass

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        pass

    @unittest.skip("skipping test_validate_campos_alterados")
    def test_validate_campos_alterados(self):
        pass

    @unittest.skip("skipping test_criados")
    def test_criados(self):
        self.assertGreater(self.classe.objects.count(), 0)


class RecessoTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = Recesso

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        pass

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_iniciado")
    def test_validate_afastamento_iniciado(self):
        pass

    @unittest.skip("skipping test_validate_afastamento_finalizado")
    def test_validate_afastamento_finalizado(self):
        pass

    @unittest.skip("skipping test_validate_campos_alterados")
    def test_validate_campos_alterados(self):
        pass

    @unittest.skip("skipping test_criados")
    def test_criados(self):
        self.assertGreater(self.classe.objects.count(), 0)


class AfastamentoOutroOrgaoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoOutroOrgao

    @unittest.skip("skipping test_save ONLY FOR TO WORK")
    def test_save(self):
        log.debug("-------------->>>>>>>>>>>>>>>>>>>>>TEST_SAVE")
        afastamento = self.classe.objects.get(pk=7077)
        afastamento.texto = "GUSTAVO"
        afastamento.save()
        # print self.classe.objects.get(pk=7077).anotacao_geral.texto

        log.debug(
            "-----------------------------------------------------------------------------"
        )

        afastamento = self.classe.objects.get(pk=11912)
        afastamento.texto = "GUSTAVO"
        afastamento.save()
        # print self.classe.objects.get(pk=11912).anotacao_geral.texto
        # self.classe.objects.get(pk=4160).save()
        # self.classe.objects.get(pk=78807).save()


class AfastamentoMandatoEletivoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoMandatoEletivo


class AfastamentoEstudarTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoEstudar


class AfastamentoMissaoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoMissao


class AfastamentoEleitoralTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoEleitoral


class AfastamentoServirJuriTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoServirJuri


class AfastamentoTreinamentoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoTreinamento


class AfastamentoDeslocamentoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoDeslocamento

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=11)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AfastamentoCompeticaoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoCompeticao


class AfastamentoCursoConcursoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoCursoConcurso


class AfastamentoPrisaoTestCase(AfastamentoTestCase):

    avoid = False
    classe = AfastamentoPrisao


class LicencaSaudeTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaSaude

    def test_validate_data_prevista(self):
        super(LicencaSaudeTestCase, self).test_validate_data_prevista()

        # self.afastamento_encerrado.data_fim = (self.afastamento_encerrado.data_fim + relativedelta(days=1))
        # self.afastamento_encerrado.prazo_concedido = self.afastamento_encerrado.prazo_concedido + 1
        # assert True == self.afastamento_encerrado.validate_data_prevista()


class LicencaSaude3DiasTestCase(LicencaSaudeTestCase):

    avoid = False
    classe = LicencaSaude3Dias


#     def test_validate_prazo_maximo(self):
#         instancia = self.classe.objects.filter()[0]
#         instancia.data_fim = instancia.data_inicio + relativedelta(days=4)
#         self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)

#     def test_validate_campos_alterados(self):
#         hoje = datetime.now().date()
#         afastamento = mock(
#             'LicencaSaude3Dias',
#             servidor=mock(model=Servidor, matricula=94008),
#             data_inicio=hoje,
#             data_fim=(hoje + relativedelta(days=2)),
#             prazo_solicitado=3,
#             prazo_concedido=3,
#             deferida=True
#         )
# #        print '_____________CAMPOS QUE PODEM SER ALTERADOS______________'
# #        for campo in afastamento.exclude:
# #            if not campo in afastamento.usuario_nao_informa:
# #                print campo
# #        print '_________________________________________________________'
#         afastamento.anota = (not afastamento.anota)
#         afastamento.texto = 'teste'
#         afastamento.data_prevista = hoje
#         afastamento.data_fim = hoje
#         self.assertIs(afastamento.validate_campos_alterados(), True)
#         super(LicencaTestCase, self).test_validate_campos_alterados()


class LicencaSaude30DiasTestCase(LicencaSaudeTestCase):

    avoid = False
    classe = LicencaSaude30Dias

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=31)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)

    # def test_validate_campos_alterados(self):
    #     hoje = datetime.now().date()
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.anota = (not instancia.anota)
    #     instancia.texto = 'teste'
    #     instancia.data_prevista = hoje
    #     instancia.data_fim = hoje
    #     self.assertIs(instancia.validate_campos_alterados(), True)
    #     super(LicencaTestCase, self).test_validate_campos_alterados()


class BaseLicencaSaudeJuntaMedicaTestCase(LicencaSaudeTestCase):

    avoid = False
    classe = LicencaSaudeJuntaMedica

    # def test_validate_prazo_minimo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=instancia.prazo_minimo - 2)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMinimo, instancia.validate_prazo_minimo)
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.prazo_solicitado = instancia.prazo_minimo - 1
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMinimo, instancia.validate_prazo_minimo)


class LicencaSaudeJuntaMedicaTestCase(BaseLicencaSaudeJuntaMedicaTestCase):

    avoid = False
    classe = LicencaSaudeJuntaMedica


class LicencaDoencaPessoaFamiliaTestCase(LicencaSaudeJuntaMedicaTestCase):

    avoid = False
    classe = LicencaDoencaPessoaFamilia


class LicencaMaternidadeTestCase(LicencaSaudeJuntaMedicaTestCase):

    avoid = False
    classe = LicencaMaternidade

    @unittest.skip("skipping validate_prazo_minimo LicencaMaternidadeTestCase")
    def test_validate_prazo_minimo(self):
        pass

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=instancia.prazo_maximo + 1)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)
    #     instancia.natimorto = True
    #     instancia.prazo_maximo = 30
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)

    # def test_validate_campos_alterados(self):
    #     hoje = datetime.now().date()
    #     afastamento = self.classe.objects.filter()[0]
    #     afastamento.anota = (not afastamento.anota)
    #     afastamento.texto = 'teste'
    #     afastamento.data_prevista = hoje
    #     afastamento.data_fim = hoje
    #     self.assertIs(afastamento.validate_campos_alterados(), True)
    #     super(LicencaMaternidadeTestCase, self).test_validate_campos_alterados()


class LicencaAdocaoTestCase(LicencaSaudeJuntaMedicaTestCase):

    avoid = False
    classe = LicencaAdocao


#     @unittest.skip("skipping validate_prazo_minimo LicencaAdocaoTestCase")
#     def test_validate_prazo_minimo(self):
#         pass

#     def test_validate_campos_alterados(self):
#         hoje = datetime.now().date()
#         instancia = self.classe.objects.filter()[0]
# #        print '_____________CAMPOS QUE PODEM SER ALTERADOS______________'
# #        for campo in instancia.exclude:
# #            if not campo in instancia.usuario_nao_informa:
# #                print campo
# #        print '_________________________________________________________'
#         instancia.anota = (not instancia.anota)
#         instancia.texto = 'teste'
#         instancia.data_prevista = hoje
#         instancia.data_fim = hoje
#         self.assertIs(instancia.validate_campos_alterados(), True)
#         super(LicencaAdocaoTestCase, self).test_validate_campos_alterados()


class LicencaAfastamentoConjugeTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaAfastamentoConjuge


#     def test_validate_campos_alterados(self):
#         hoje = datetime.now().date()
#         instancia = self.classe.objects.filter()[0]
# #        instancia = mock(model=self.classe,
# #            servidor = mock(model=Servidor, matricula = 96209),
# #            publicacao_movimentacao = mock(model=Publicacao, pk = 2975),
# #            publicacao_fim = mock(model=Publicacao, pk = 2975),
# #            data_inicio = hoje,
# #            data_fim = hoje + relativedelta(days=2)
# #        )
# #        print '_____________CAMPOS QUE PODEM SER ALTERADOS______________'
# #        for campo in instancia.exclude:
# #            if not campo in instancia.usuario_nao_informa:
# #                print campo
# #        print '_________________________________________________________'
#         instancia.anota = (not instancia.anota)
#         instancia.texto = 'teste'
#         instancia.data_prevista = hoje
#         instancia.data_fim = hoje
#         self.assertIs(instancia.validate_campos_alterados(), True)
#         super(LicencaAfastamentoConjugeTestCase, self).test_validate_campos_alterados()


class LicencaServicoMilitarTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaServicoMilitar


#     def test_validate_campos_alterados(self):
#         hoje = datetime.now().date()
#         instancia = self.classe.objects.filter()[0]
# #        instancia = mock(model=self.classe,
# #            servidor = mock(model=Servidor, matricula = 79507),
# #            publicacao_movimentacao = mock(model=Publicacao, pk = 2975),
# #            publicacao_fim = mock(model=Publicacao, pk = 2975),
# #            data_inicio = hoje,
# #            data_fim = hoje + relativedelta(days=2)
# #        )
# #        print '_____________CAMPOS QUE PODEM SER ALTERADOS______________'
# #        for campo in instancia.exclude:
# #            if not campo in instancia.usuario_nao_informa:
# #                print campo
# #        print '_________________________________________________________'
#         instancia.anota = (not instancia.anota)
#         instancia.texto = 'teste'
#         instancia.data_prevista = hoje
#         instancia.data_fim = hoje
#         self.assertIs(instancia.validate_campos_alterados(), True)
#         super(LicencaServicoMilitarTestCase, self).test_validate_campos_alterados()


class LicencaAtividadePoliticaTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaAtividadePolitica


class LicencaCapacitacaoTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaCapacitacao


#     def test_validate_campos_alterados(self):
#         hoje = datetime.now().date()
#         instancia = self.classe.objects.filter()[0]
# #        instancia = mock(model=self.classe,
# #            servidor = mock(model=Servidor, matricula = 69507),
# #            publicacao_movimentacao = mock(model=Publicacao, pk = 2975),
# #            publicacao_fim = mock(model=Publicacao, pk = 2975),
# #            data_inicio = hoje,
# #            data_fim = hoje + relativedelta(days=2),
# #            curso = mock('Curso', pk = 5),
# #            instituicao = mock('UnidadeAdministrativa', pk = 382),
# #        )
# #        print '_____________CAMPOS QUE PODEM SER ALTERADOS______________'
# #        for campo in instancia.exclude:
# #            if not campo in instancia.usuario_nao_informa:
# #                print campo
# #        print '_________________________________________________________'
#         instancia.anota = (not instancia.anota)
#         instancia.texto = 'teste'
#         instancia.data_prevista = hoje
#         instancia.data_fim = hoje
#         self.assertIs(instancia.validate_campos_alterados(), True)
#         super(LicencaCapacitacaoTestCase, self).test_validate_campos_alterados()


class LicencaInteresseParticularTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaInteresseParticular

    # def test_validate_erro_data_fim(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = None
    #     self.assertRaises(BaseLicencaAfastamento.ErroDataFimNone, instancia.validate_erro_data_fim)

    # @unittest.skip("skipping test_validate_prazo_maximo LicencaInteresseParticular")
    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class LicencaMandatoClassistaTestCase(LicencaTestCase):

    avoid = False
    classe = LicencaMandatoClassista


class AusenciaDoacaoSangueTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaDoacaoSangue

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=2)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AusenciaEleitorTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaEleitor

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=3)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AusenciaCasamentoTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaCasamento

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=10)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AusenciaNascimentoTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaNascimento

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=10)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AusenciaFalecimentoTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaFalecimento

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=10)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class AusenciaConclusaoTestCase(AusenciaTestCase):

    avoid = False
    classe = AusenciaConclusao

    # def test_validate_prazo_maximo(self):
    #     instancia = self.classe.objects.filter()[0]
    #     instancia.data_fim = instancia.data_inicio + relativedelta(days=12)
    #     self.assertRaises(BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo)


class FolgaAniversarioTestCase(AusenciaTestCase):

    avoid = False
    classe = FolgaAniversario

    def test_validate_periodo_maximo_marcacao(self):
        self.setUp()
        servidor = {"model": "Servidor", "pk": 179}
        instancia = mock(
            model=self.classe,
            servidor=servidor,
            anotacao_aquisicao={
                "model": "AnotacaoFolgaAniversario",
                "servidor": servidor,
            },
            data_inicio=datetime.now().date(),
            data_prevista=datetime.now().date(),
        )
        print(instancia)
        instancia.data_fim = instancia.data_inicio + relativedelta(days=2)
        self.assertRaises(
            BaseLicencaAfastamento.ErroPrazoMaximo, instancia.validate_prazo_maximo
        )

        instancia.data_inicio = instancia.data_referencia + relativedelta(
            years=1, days=1
        )
        instancia.data_fim = instancia.data_referencia + relativedelta(years=1, days=1)
        self.assertRaises(
            BaseLicencaAfastamento.ErroPrazoMaximo,
            instancia.validate_periodo_maximo_marcacao,
        )


class FolgaCompensacaoTestCase(BaseLicencaAfastamentoTestCase):

    avoid = False
    classe = FolgaCompensacao


class CreateWorkAssignmentTestCase(unittest.TestCase):

    def test_employees(self):
        ServidorLotacao._work_assignment_return_from_departured(
            BaseLicencaAfastamento.objects.get(pk=33211).instancia_modelo
        )
        ServidorLotacao._work_assignment_return_from_departured(
            BaseLicencaAfastamento.objects.get(pk=35573).instancia_modelo
        )
        BaseLicencaAfastamento.objects.get(pk=35573).instancia_modelo.save()

        for base in BaseLicencaAfastamento.objects.filter(
            Q(servidor__tipo="M")
            & Q(data_fim__gte=datetime(2016, 8, 1))
            & Q(data_fim__lte=datetime(2016, 9, 2))
        ).order_by("servidor"):
            work_count_before = base.servidor.work_assignment.filter(owner=True).count()
            work_before = base.servidor.work_assignment.filter(owner=True)
            try:
                ServidorLotacao._work_assignment_return_from_departured(
                    base.instancia_modelo
                )
            except Exception as err:
                print(err)
            work_count_after = base.servidor.work_assignment.filter(owner=True).count()
            work_after = base.servidor.work_assignment.filter(owner=True)

            if work_count_before != work_count_after:
                print("------------------------------------")
                print(
                    base.instancia_modelo,
                    DateUtils.date_to_str(base.data_inicio),
                    DateUtils.date_to_str(base.data_fim),
                )
                print("work_count_before %s" % work_count_before)
                print("work_before %s" % work_before)
                print("work_count_after %s" % work_count_after)
                print("work_after %s" % work_after)


class FindDepartureConcatenatedTestCase(unittest.TestCase):

    def test(self):
        # print(BaseLicencaAfastamento.objects.get(pk=36173).servidor)
        # print(BaseLicencaAfastamento.objects.get(pk=36173).servidor.owner_locations_can_substitute)
        # print(BaseLicencaAfastamento.objects.get(pk=36173).servidor.work_assignment_effective_exercise)
        # from rh.gfp.models import Folha
        # print(Servidor.objects.get(matricula=16597).work_assignment_effective_exercise)
        # BaseLicencaAfastamento.objects.get(pk=36173).instancia_modelo.save()
        # BaseLicencaAfastamento.objects.get(pk=31296).instancia_modelo.save()

        BaseLicencaAfastamento.objects.get(pk=36173).servidor  # employee
        departure_concatenated = BaseLicencaAfastamento.objects.get(
            pk=36173
        ).find_departure_concatenated()
        for departure in departure_concatenated:
            print(
                departure,
                DateUtils.date_to_str(departure.data_inicio),
                DateUtils.date_to_str(departure.data_fim),
            )
            # departure.instancia_modelo.save()
        # departures = [departure.pk for departure in departure_concatenated]
        # departures = employee.departures().exclude(~Q(desempenhofuncao=None) | ~Q(atuacaogrupotrabalho=None))
        # if departures.exists():
        #     departures = [dep.pk for dep in departures.latest('data_inicio').find_departure_concatenated()]
        # work_assignment = employee.get_work_assignment().filter(changed_by_departure__pk__in=departures)
        # print(work_assignment)

        # folha = Folha.objects.get(pk=831)
        # for fe in folha.lancamentos.filter(evento__numero='06900'):
        #     workplace = fe.servidor.workplace_by_date(datetime(2016, 10, 1))
        #     #if not (fe.info == unicode(workplace.localidade.comarca)) or fe.servidor.matricula in (11292, 108810):
        #     effective = ' | effective exercise => '
        #     ef_array = []
        #     for ef in fe.servidor.work_assignment_effective_exercise:
        #         effective += '|%s' % unicode(ef.lotacao.localidade.comarca)
        #         ef_array.append(unicode(ef.lotacao.localidade.comarca))
        #     if fe.info not in ef_array:
        #         print fe.servidor, ' | ', fe.info, ' | ', workplace.localidade.comarca, effective


class FeriasAfastamentoAnnotataionTestCase(unittest.TestCase):

    def test_annotation(self):
        # print(FeriasAfastamento.objects.get(pk=34997).anotacao_geral)
        # FeriasAfastamento.objects.get(pk=34997).save()
        for fa in (
            FeriasAfastamento.objects.filter(estado=CANCELED)
            .exclude(anotacao_geral=None)
            .order_by("data_inicio")
        ):
            print(
                fa,
                DateUtils.date_to_str(fa.data_inicio),
                fa.anotacao_classe,
                fa.anotacao_geral,
            )
            try:
                fa.save()
            except Exception as err:
                print(err)


class FeriasAfastamentoTestCase(unittest.TestCase):

    def test(self):
        for fa in FeriasAfastamento.objects.filter(pk__in=[38723]).order_by(
            "data_inicio"
        ):
            print(fa, DateUtils.date_to_str(fa.data_inicio))
            try:
                fa.save()
            except Exception as err:
                print(err)


class DepartureEndedTestCase(unittest.TestCase):

    def test(self):
        for departure in (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor__tipo="M") & Q(data_fim__gte=datetime(2016, 10, 1)),
                # Q(servidor__matricula=100610)
            )
            .exclude(estado__in=[SCHEDULED, CANCELED])
            .order_by("servidor")
        ):
            print(departure)
            print(departure.servidor.workplace_only_active)
            print(departure.servidor.work_assignment)
            try:
                departure.instancia_modelo.save()
            except Exception as err:
                print(err)
            print("-------------------------")


class DepartureTestCase(unittest.TestCase):

    # @unittest.skip('skipping test_departured')
    def test_departured(self):
        print()
        # registry = []
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Rafael Pinto Alamy').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Luiz Antonio Francisco Pinto').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Daniel Jose de Oliveira Almeida').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Adriano Zizza Romero').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Airton Amilcar Machado Momo').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Cynthia Assis de Paula').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Elizon de Sousa Medrado').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Bartira Silva Quinteiro').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Caleb de Melo Filho').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Isabelle Rocha Valenca Figueiredo').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Paulo Alexandre Rodrigues de Siqueira').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Tarso Rizo Oliveira Ribeiro').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Argemiro Ferreira dos Santos Neto').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Araina').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Francisco Jose Pinheiro Brandes Junior').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Rui Gomes Pereira da Silva Neto').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Guilherme Cintra Deleuse').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Milton Quintana').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Juliana da Hora Almeida').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Luma Gomides de Souza').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Rogerio Rodrigo Ferreira Mota').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Gustavo Schult Junior').last().matricula)
        # registry.append(Servidor.objects.filter(pessoa_fisica__nome__icontains='Pedro Jainer Passos Clarindo da Silva').last().matricula)
        # query = BaseLicencaAfastamento.objects.filter(servidor__matricula__in=registry).exclude(estado__in=[FINISHED, CANCELED])
        # for base in query.exclude(data_inicio__gte=datetime(2018, 5, 31).date()).order_by('servidor__pessoa_fisica__nome'):
        #     instance = base.instancia_modelo
        #     print instance, '===>', DateUtils.date_to_str(instance.data_inicio), 'à', DateUtils.date_to_str(instance.data_fim)

        query = (
            BaseLicencaAfastamento.objects.filter(servidor__tipo="M")
            .exclude(
                ~Q(licenca__licencamandatoclassista=None)
                # ~Q(desempenhofuncao=None) |
                # ~Q(atuacaogrupotrabalho=None)
            )
            .exclude(estado__in=[FINISHED, CANCELED, SCHEDULED])
        )
        for base in query.order_by("estado"):
            instance = base.instancia_modelo
            work_locations_effective_exercise = (
                instance.servidor.work_locations_effective_exercise
            )
            # print work_locations_effective_exercise.count(), work_locations_effective_exercise
            if not work_locations_effective_exercise.exists():
                print(instance)
                print(
                    instance.data_inicio, instance.data_inicio - relativedelta(days=1)
                )
                wa = instance.servidor.get_work_assignment(
                    date=instance.data_inicio - relativedelta(days=1)
                )
                print(wa.count())
                if not wa.exists():
                    wa = instance.servidor._raw_locations(option=2)
                    print(wa.count())
                if wa.exists():
                    wa = wa.last()
                    print(wa)
                    ServidorLotacao.objects.filter(pk=wa.pk).update(
                        changed_by_departure=instance
                    )
                    ServidorLotacao.objects.get(pk=wa.pk).save()
                    if instance.servidor.work_locations_effective_exercise.exists():
                        print("GRAVOU")
                    # instance.save()
                print("----------------------------------------------------")

    @unittest.skip("skipping test_annotation")
    def test_annotation(self):
        query = (
            BaseLicencaAfastamento.objects.filter(anotacao_geral=None)
            .exclude(estado__in=[SCHEDULED, CANCELED])
            .exclude(tipo__in=[5])
        )
        print("count", query.count())
        for base in query:
            instance = base.instancia_modelo
            print(instance)
            BaseLicencaAfastamento.objects.filter(pk=base.pk).update(
                anotacao_geral=instance.anotacao()
            )
            print("----------------------------------------------------")

    @unittest.skip("skipping test")
    def test(self):
        # for departure in BaseLicencaAfastamento.objects.filter(pk__in=[42698, 37208, 38611]):
        for departure in (
            BaseLicencaAfastamento.objects.filter(servidor__tipo="M")
            .exclude(
                estado__in=[
                    SCHEDULED,
                ]
            )
            .order_by("data_inicio")
        ):
            departure = departure.instancia_modelo
            count = ServidorLotacao.objects.filter(servidor=departure.servidor).count()
            try:
                departure.save()
            except Exception as err:
                print(err)
            count2 = ServidorLotacao.objects.filter(servidor=departure.servidor).count()
            if count != count2:
                print(departure.__str_restful__(), count, count2)
                print("-------------------------")

    # @classmethod
    # def search_for_duplicate(cls, sl):
    #     return sl.servidor._raw_locations(
    #         date=sl.data_vigencia_inicio,
    #         option=WORK_ASSIGNMENT
    #     ).exclude(pk=sl.pk).filter(lotacao=sl.lotacao)

    # def finish_duplicate_exercise(self):
    #     pks = []
    #     count = count_wrong = 0
    #     work_assignment = ServidorLotacao.search_for_duplicate(self)
    #     for wa in work_assignment:
    #         log.debug('%s - %s' % (self.pk, self))
    #         log.debug('%s - %s' % (wa.pk, wa))
    #         if self.data_vigencia_inicio >= wa.data_vigencia_inicio:
    #             wa.data_vigencia_fim = self.data_vigencia_inicio - relativedelta(days=1)
    #             try:
    #                 wa.save()
    #                 count += 1
    #             except Exception as err:
    #                 pks.append([self.pk, wa.pk])
    #                 count_wrong += 1
    #                 log.debug(unicode(err))
    #         log.debug('----------------------------------------')
    #     log.debug('count %s' % count)
    #     log.debug('count wrong %s' % count_wrong)
    #     log.debug(pks)


class FunctionalTestCase(unittest.TestCase):

    def test(self):
        # FeriasAfastamento.objects.get(pk=53009).save()
        # DesempenhoFuncao.objects.get(pk=39188).save()
        # DesempenhoFuncao.objects.get(pk=23591).save()
        # DesempenhoFuncao.objects.get(pk=47474).save()
        # for base in BaseLicencaAfastamento.objects.filter(servidor__matricula=989):
        #     base.instancia_modelo.save()
        # for base in ServidorLotacao.objects.filter(servidor__matricula=989):
        #     base.save()

        for base in (
            BaseLicencaAfastamento.objects.filter(
                servidor__tipo="M", data_fim__gte=datetime(2018, 12, 1).date()
            )
            .filter(
                Q(desempenhofuncao__isnull=False)
                | Q(atuacaogrupotrabalho__isnull=False)
            )
            .order_by("servidor", "data_fim")
        ):
            print(base.servidor, base.__str_restful__())
            try:
                base.instancia_modelo.save()
            except Exception as err:
                print(err)


class ManagerDeparturesScript(unittest.TestCase):

    def test(self):
        from rh.gfp.models import Folha

        year = 2018
        sheet = Folha.objects.filter(tipo_folha__principal=True).latest("pk")
        date_start = datetime(year, 12, 20).date()
        date_end = datetime(year + 1, 1, 6).date()
        self.criar_recesso_natalino(
            year=year, sheet=sheet, date_start=date_start, date_end=date_end
        )

    def employees_exclude_from_document(self):
        employee = []
        with codecs.open("employee_departure.txt", "r") as file_employee:
            for line in file_employee.readlines():
                employee.append(line.replace(",", ""))
        return employee

    def criar_recesso_natalino(
        self, year=None, sheet=None, date_start=None, date_end=None
    ):
        from rh.gfp.models import ContraCheque
        from dateutil.relativedelta import relativedelta

        departures_to_check = BaseLicencaAfastamento.objects.filter(
            servidor__tipo="S"
        ).exclude(
            Q(estado=CANCELADO) | Q(data_fim__lte=(date_start - relativedelta(days=1)))
        )
        dr_recess = NewDateRange(date_start, date_end)
        # count = 0
        employee_registry_candidate = []
        employee_registry_removed = []
        print("Servidores afastados que não terão Recesso criado:")
        for dep in departures_to_check.order_by("servidor", "-data_inicio"):
            days_conflict = dr_recess.intersect(
                NewDateRange(dep.data_inicio, dep.data_fim)
            ).days
            if (
                days_conflict > 0
                and int(dep.servidor.matricula) in employee_registry_candidate
            ):
                print("%s|%s|%s|%s") % (
                    DateUtils.date_to_str(dep.data_inicio),
                    DateUtils.date_to_str(dep.data_fim) if dep.data_fim else "----",
                    dep,
                    "CONFLITO(%d)" % days_conflict,
                )
                employee_registry_removed.append(int(dep.servidor.matricula))
            elif (
                days_conflict == 0
                and not int(dep.servidor.matricula) in employee_registry_candidate
            ):
                employee_registry_candidate.append(int(dep.servidor.matricula))

        print(
            "\nServidores trabalhando pelo ato: ",
            len(self.employees_exclude_from_document()),
        )
        for se in Servidor.objects.filter(
            matricula__in=self.employees_exclude_from_document()
        ).order_by("pessoa_fisica__nome"):
            print(se)

        employees = Servidor.objects.filter(
            matricula__in=ContraCheque.objects.filter(servidor__tipo="S", folha=sheet)
            .distinct()
            .values("servidor__matricula")
        )
        count_inactive = employees.filter(ativo=False).count()

        employees = employees.exclude(ativo=False)

        count_active = employees.filter(ativo=True).count()
        total_sheet = employees.count()

        employees = employees.exclude(
            matricula__in=self.employees_exclude_from_document()
        )
        total_exclude_document = employees.count()

        employees = employees.exclude(matricula__in=employee_registry_removed)
        total_exclude_removed = employees.count()

        created, err = self.run_create(employees, date_start, date_end, year)
        departures = Recesso.objects.filter(ano=year)
        buff = ""
        for line in err:
            buff += line + "\n"
        print(
            """
Folha: %s
Total de servidores da Folha: %d
Total de servidores da Folha - Ativos: %d
Total de servidores da Folha - Inativos: %d
Total de servidores do ato: %d
Total de servidores sem os do ato: %d
Total de servidores sem, os do ato e os que já possuem afastamentos: %d
Total criado: %d
Total não criado: %d
%s
Total de afastamentos para %d: %d
        """
            % (
                sheet,
                total_sheet,
                count_active,
                count_inactive,
                len(self.employees_exclude_from_document()),
                total_exclude_document,
                total_exclude_removed,
                created,
                len(err),
                buff,
                year,
                departures.count(),
            )
        )

    def run_create(self, employees, date_start, date_end, year):
        err = []
        created = 0
        for employee in employees.filter(ativo=True):
            result = self._create(employee, date_start, date_end, year)
            if result:
                err.append(result)
            else:
                created += 1
                # print employee
        # print 'férias', FeriasAfastamento.objects.filter(data_inicio=data_fim).exclude(estado=CANCELADO).count()
        return created, err

    def _create(self, employee, date_start, date_end, year):
        # print 'CRIANDO RECESSO PARA O SERVIDOR.....', servidor
        err = None
        try:
            # recesso = Recesso(
            Recesso.objects.get_or_create(
                servidor=employee,
                data_inicio=date_start,
                data_prevista=date_end,
                data_fim=date_end,
                ano=year,
            )
            # recesso.save()
        except Exception as err:
            print(err)
        return err


class ExericesTestCase(unittest.TestCase):

    def test(self):
        from rh.models import User

        count = 0
        modified_by_athenas = 0
        user_athenas = User.objects.get(username="athenas")
        for departure in (
            BaseLicencaAfastamento.objects.filter(
                created_at__gte=datetime(2020, 1, 1).date(), servidor__tipo="M"
            )
            .exclude(estado__in=[CANCELED, SCHEDULED])
            .order_by("-data_inicio")
        ):
            employee_workplaces = departure.servidor.work_assignment_from_departure(
                departure
            )
            employee_workplaces = employee_workplaces.exclude(
                pk__in=departure.designation_exercise.filter(ativo=False).values("pk")
            )
            for work_assignment in employee_workplaces:
                date_end = departure.data_inicio - relativedelta(days=1)
                if (
                    work_assignment.data_vigencia_fim
                    and work_assignment.data_vigencia_fim != date_end
                ):
                    count += 1
                    print(departure.__str_restful__())
                    print(
                        work_assignment.servidor,
                        work_assignment,
                        DateUtils.date_to_str(date_end),
                    )
                    if work_assignment.modified_by == user_athenas:
                        modified_by_athenas += 1
                        ServidorLotacao.objects.filter(pk=work_assignment.pk).update(
                            data_vigencia_fim=date_end
                        )
                        work_assignment.refresh_from_db()
                        work_assignment.anotacao()
                    print("----------------------------------------------")
            # apenas em test pra ver se retorna com implementação antiga
            # ServidorLotacao._finalize_work_assignment_from_departure(departure.my_origin)
        print("count %s | modified_by_athenas %s" % (count, modified_by_athenas))
