# -*- coding: utf-8 -*-

import codecs
import json
import unittest
from datetime import date, datetime
from string import Template

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import OneToOneRel

from contrib.decorator import profile
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, getLogger
from default.testting import AthenasTestCase
from engine.mq.models import Task
from rh.afastamento import models as afastamento_models
from rh.afastamento import tests as afastamento_tests
from rh.const import (
    ACTIVE,
    CANCELED,
    ESTADO_CIVIL_CHOICES,
    GRAU_INSTRUCAO_CHOICES,
    INTERRUPCAO,
    TIPO_LOGRADOURO_ENDERECO_CHOICES,
    TITULO_ELEITOR,
    TYPE_PHONE_EMERGENCY,
    WORK_ASSIGNMENT,
    WORKPLACE,
)
from rh.models import (
    CargaHoraria,
    Cargo,
    CargoQuadro,
    Carreira,
    Comarca,
    Curso,
    DadoBancario,
    DadoBancarioConsignatario,
    DadoBancarioPessoa,
    DeclaracaoAtividade,
    Dependente,
    DocsDadosEspecificos,
    Documento,
    DocumentSpecialized,
    Endereco,
    Estado,
    InativacaoCargoMembro,
    Localidade,
    Lotacao,
    MicroRegiao,
    MovimentacaoAposentadoria,
    MovimentacaoAproveitamento,
    MovimentacaoConcessao,
    MovimentacaoDesligamento,
    MovimentacaoEstabilizacao,
    MovimentacaoPessoal,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoRedistribuicao,
    MovimentacaoReintegracao,
    MovimentacaoRemocao,
    MovimentacaoRemocaoMembro,
    MovimentacaoRequisicao,
    MovimentacaoReversao,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    MovimentacaoTitularizacao,
    NecessidadeEspecial,
    OrgaoGeral,
    PeriodoRequisicao,
    Pessoa,
    PessoaFisica,
    PessoaJuridica,
    Publicacao,
    Quadro,
    Relationship,
    Servidor,
    ServidorLocalizacao,
    ServidorLotacao,
    ServidorVinculo,
    SituacaoFuncional,
    Telefone,
    UnidadeAdministrativa,
)
from rh.task.workplace import create_new_employeeworkplace

# from rh.tests_api import RHConfiguracaoTests
from rh.tests_api.utils import mock

log = getLogger(__name__)


def setUpModule():
    # RHConfiguracaoTests.setUpModule()
    pass


def tearDownModule():
    # RHConfiguracaoTests.tearDownModule()
    pass


def validate_publicacao(self):
    if self.publicacao is None:
        self.publicacao = mock(model=Publicacao, query=(~Q(data_vigencia=None)))
    return True


def validate_publicacao_posse(self):
    if self.movimentacao_posse.publicacao_movimentacao is None or (
        (
            self.movimentacao_posse.publicacao_movimentacao is not None
            and self.movimentacao_posse.publicacao_movimentacao.data_vigencia is None
        )
    ):
        self.movimentacao_posse.publicacao_movimentacao = mock(
            model=Publicacao, query=(~Q(data_vigencia=None))
        )
    return True


def validate_publicacao_movimentacao(self):
    if self.publicacao_movimentacao is None or (
        self.publicacao_movimentacao is not None
        and self.publicacao_movimentacao.data_vigencia is None
    ):
        self.publicacao_movimentacao = mock(
            model=Publicacao, query=(~Q(data_vigencia=None))
        )
    return True


def validate_desligamento_automatico_membro(self):
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


def validate_duplicate_workplace(self):
    return True


class MovimentacaoDesligamentoTestCase(unittest.TestCase):

    def test_save(self):
        if MovimentacaoDesligamento.objects.exists():
            MovimentacaoDesligamento.objects.latest("pk").save()


class MovimentacaoAposentadoriaTestCase(unittest.TestCase):

    classe = MovimentacaoAposentadoria

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoRemocaoMembroTestCase(unittest.TestCase):

    def test_save(self):
        # movimentacao = MovimentacaoRemocao.objects.filter(servidor__tipo='M').latest('pk')
        # movimentacao.save()
        query = MovimentacaoRemocao.objects.filter(servidor__tipo="M")
        try:
            for movimentacao in query:
                movimentacao.save()
                break
        except Exception as err:
            print(err)
            raise err


class PessoaTestCase(AthenasTestCase):

    avoid = False
    classe = Pessoa


class PessoaFisicaTestCase(AthenasTestCase):

    avoid = False
    classe = PessoaFisica

    def test_atualiza_cache_necessidade_especial(self):
        pessoa_fisica = PessoaFisica.objects.filter().latest("pk")
        if NecessidadeEspecial.objects.filter(~Q(pessoafisica=None)).exists():
            pessoa_fisica = (
                NecessidadeEspecial.objects.filter(~Q(pessoafisica=None))
                .latest("pk")
                .pessoafisica.latest("pk")
            )
        PessoaFisica.objects.filter(pk=pessoa_fisica.pk).update(
            necessidade_especial=False
        )
        pessoa_fisica.atualiza_cache_necessidade_especial()

    def test_set_data_obito(self):
        data_obito = datetime.now().date()
        pessoa = PessoaFisica.objects.filter(data_obito=None).latest("pk")
        pessoa.set_data_obito(data_obito=data_obito)
        assert PessoaFisica.objects.get(pk=pessoa.pk).data_obito == data_obito
        pessoa.set_data_obito(data_obito=None)
        assert PessoaFisica.objects.get(pk=pessoa.pk).data_obito is None


class PessoaJuridicaTestCase(AthenasTestCase):

    avoid = False
    classe = PessoaJuridica


class OrgaoGeralTestCase(AthenasTestCase):

    avoid = False
    classe = OrgaoGeral


class UnidadeAdministrativaTestCase(AthenasTestCase):

    avoid = False
    classe = UnidadeAdministrativa


class LotacaoTestCase(unittest.TestCase):

    avoid = False
    classe = Lotacao

    # @unittest.skip("skipping test_update_responsible")
    def test_update_responsible(self):
        posse = MovimentacaoPosse.objects.filter(
            ~Q(quadro__cargo__lotacao_responsavel__responsavel=None)
        ).latest("pk")
        lotacao_responsavel = posse.quadro.cargo.lotacao_responsavel.responsavel
        lotacao = posse.quadro.cargo.lotacao_responsavel
        Lotacao.objects.filter(pk=lotacao.pk).update(responsavel=None)
        lotacao.update_responsible(responsible_new=posse.servidor)
        assert Lotacao.objects.get(pk=lotacao.pk).responsavel == posse.servidor
        lotacao.update_responsible(responsible_new=lotacao_responsavel)

    # @unittest.skip("skipping test_atualiza_chefia_servidor")
    def test_atualiza_chefia_servidor(self):
        workplace = Lotacao.objects.get(pk=448)
        employees = workplace._employee_workplaces().filter(ativo=True)
        employee_old_responsible = workplace.responsavel
        employee_new_responsible = (
            employees.exclude(servidor=employee_old_responsible).latest("pk").servidor
        )
        employees_old_count = employees.count()
        workplace.responsavel = employee_new_responsible
        workplace.save()
        assert (
            workplace._employee_workplaces().filter(ativo=True).count()
            == employees_old_count
        )

        workplace = Lotacao.objects.get(pk=546)
        employees = workplace._employee_workplaces().filter(ativo=True)
        employee_old_responsible = workplace.responsavel
        employee_new_responsible = (
            employees.exclude(servidor=employee_old_responsible).latest("pk").servidor
        )
        employees_old_count = employees.count()
        workplace.responsavel = employee_new_responsible
        workplace.save()
        assert (
            workplace._employee_workplaces().filter(ativo=True).count()
            == employees_old_count
        )

        workplace = Lotacao.objects.get(pk=457)
        employees = workplace._employee_workplaces().filter(ativo=True)
        employee_old_responsible = workplace.responsavel
        employee_new_responsible = (
            employees.exclude(servidor=employee_old_responsible).latest("pk").servidor
        )
        employees_old_count = employees.count()
        workplace.responsavel = employee_new_responsible
        workplace.save()
        assert (
            workplace._employee_workplaces().filter(ativo=True).count()
            == employees_old_count
        )

    def test_save(self):
        # lotacao = Lotacao.objects.get(pk=546)  # rh
        # chagas = Servidor.objects.get(matricula=69507)
        # vicente = Servidor.objects.get(matricula=68907)
        # lotacao.responsavel = vicente if lotacao.responsavel == chagas else chagas
        # lotacao.save()

        # lotacao = Lotacao.objects.get(pk=457)  # corregedoria geral
        # alcir = Servidor.objects.get(matricula=3090)
        # joao_rodrigues = Servidor.objects.get(matricula=989)
        # lotacao.responsavel = joao_rodrigues if lotacao.responsavel == alcir else alcir
        # lotacao.save()
        pass

    def test_employees(self):
        # print('\n')
        # print(self.classe.objects.first().employees)
        assert self.classe.objects.first().employees

    def test_employee_workplaces_responsible(self):
        # print('\n')
        # print(self.classe.objects.first().employee_workplaces_responsible)
        assert self.classe.objects.first().employee_workplaces_responsible

        pass
        # print('\n')
        # print(self.classe.objects.first().owner)
        assert self.classe.objects.first().owner

    def test_employee_exercise(self):
        # print('\n')
        # print(self.classe.objects.first().employee_exercise)
        assert self.classe.objects.first().employee_exercise


class DadoBancarioTestCase(AthenasTestCase):

    avoid = False
    classe = DadoBancario


class EstadoTestCase(AthenasTestCase):

    avoid = False
    classe = Estado


class ComarcaTestCase(AthenasTestCase):

    avoid = False
    classe = Comarca


class MicroRegiaoTestCase(AthenasTestCase):

    avoid = False
    classe = MicroRegiao


class LocalidadeTestCase(AthenasTestCase):

    avoid = False
    classe = Localidade


class ServidorTestCase(AthenasTestCase):

    avoid = False
    classe = Servidor

    # @unittest.skip('skipping test_atualiza_cache_tipo')
    def test_atualiza_cache_tipo(self):
        """
        Este método deve testar atualiza_cache_tipo de Servidor.
        """

        servidor = DeclaracaoAtividade.objects.latest("pk").servidor
        Servidor.objects.filter(pk=servidor.pk).update(tipo="M")
        Servidor.objects.get(pk=servidor.pk).atualiza_cache_tipo()
        assert "E" == Servidor.objects.get(pk=servidor.pk).tipo

        servidor = (
            MovimentacaoPosse.objects.filter(servidor__tipo="M").latest("pk").servidor
        )
        Servidor.objects.filter(pk=servidor.pk).update(tipo="E")
        Servidor.objects.get(pk=servidor.pk).atualiza_cache_tipo()
        assert "M" == Servidor.objects.get(pk=servidor.pk).tipo

        servidor = (
            MovimentacaoPosse.objects.filter(servidor__tipo="S").latest("pk").servidor
        )
        Servidor.objects.filter(pk=servidor.pk).update(tipo="E")
        Servidor.objects.get(pk=servidor.pk).atualiza_cache_tipo()
        assert "S" == Servidor.objects.get(pk=servidor.pk).tipo

    # @unittest.skip('skipping test_atualiza_cache_ativo')
    # def test_atualiza_cache_ativo(self):
    #     """
    #         Este método deve testar test_atualiza_cache_ativo de Servidor.
    #     """
    #     servidor = Servidor.objects.filter(
    #         movimentacaopessoal__movimentacaodesligamento=None, ativo=True).latest('pk')
    #     Servidor.objects.filter(pk=servidor.pk).update(ativo=False)
    #     servidor.atualiza_cache_ativo()
    #     assert Servidor.objects.get(pk=servidor.pk).ativo is True

    #     servidor = MovimentacaoPosse.objects.filter(
    #         ~Q(desligamento__data_desligamento=None) & Q(servidor__ativo=False) & Q(servidor__tipo='S')
    #     ).latest('data_exercicio').servidor
    #     Servidor.objects.filter(pk=servidor.pk).update(ativo=True)
    #     servidor.atualiza_cache_ativo()
    #     assert Servidor.objects.get(pk=servidor.pk).ativo is False

    # @unittest.skip('skipping test_atualiza_cache_categoria')
    def test_atualiza_cache_categoria(self):
        servidor = Servidor.objects.filter().latest("pk")
        Servidor.objects.filter(pk=servidor.pk).update(categoria_cache="NOT_FOUND")
        servidor.atualiza_cache_categoria()
        assert Servidor.objects.get(pk=servidor.pk).categoria_cache != ""

    # @unittest.skip('skipping test_set_data_referencia_ferias')
    def test_set_data_referencia_ferias(self):
        posse = MovimentacaoPosse.objects.filter(servidor__tipo="S", ativo=True).latest(
            "pk"
        )
        servidor = posse.servidor
        Servidor.objects.filter(pk=servidor.pk).update(data_referencia_ferias=None)
        servidor.set_data_referencia_ferias(posse.data_exercicio)

    # @unittest.skip('skipping test_substitutos')
    def test_substitutos(self):
        # from rh.plugins.arquimedes import *
        servidor = Servidor.objects.filter(tipo="M", ativo=True).latest("pk")
        print(servidor)
        print(servidor.my_substitute())
        assert servidor.my_substitute() is not []

    def test_set_chief_immediate(self):
        servidor1 = MovimentacaoPosse.objects.filter(servidor__tipo="S", ativo=True)[
            0
        ].servidor
        servidor2 = MovimentacaoPosse.objects.filter(servidor__tipo="S", ativo=True)[
            1
        ].servidor
        chefe_imediato = servidor1.chefe_imediato
        servidor1.set_chief_immediate(chief_immediate=servidor2)
        assert Servidor.objects.get(pk=servidor1.pk).chefe_imediato == servidor2
        servidor1.set_chief_immediate(chief_immediate=chefe_imediato)
        assert Servidor.objects.get(pk=servidor1.pk).chefe_imediato == chefe_imediato

    # @unittest.skip('skipping test_update_designation_to_substitution')
    def test_update_designation_to_substitution(self):
        servidor = (
            MovimentacaoPosse.objects.filter(servidor__tipo="S", ativo=True)
            .latest("pk")
            .servidor
        )
        servidor._update_designation_to_substitution()

    def test_raw_locations(self):
        date = datetime.now().date()
        employee = Servidor.objects.get(matricula=69507)
        employee_workplace = ServidorLotacao.objects.filter(servidor=employee)

        assert employee_workplace.count() == employee._raw_locations().count()

        query = employee_workplace.filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim=None) | Q(data_vigencia_fim__gte=date))
        )

        assert query.count() == employee._raw_locations(date=date).count()

        assert query.filter().count() == employee._raw_locations(date=date).count()

        assert (
            query.filter(ativo=True).count()
            == employee._raw_locations(date=date, active=True).count()
        )

        # workplace

        assert (
            employee_workplace.filter(designacao=False).count()
            == employee._raw_locations(option=WORKPLACE).count()
        )

        query = employee_workplace.filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim=None) | Q(data_vigencia_fim__gte=date))
        )

        query = query.filter(designacao=False)

        assert (
            query.count()
            == employee._raw_locations(option=WORKPLACE, date=date).count()
        )

        assert (
            query.filter().count()
            == employee._raw_locations(option=WORKPLACE, date=date).count()
        )

        assert (
            query.filter(ativo=True).count()
            == employee._raw_locations(option=WORKPLACE, date=date, active=True).count()
        )

        # work_assignment

        assert (
            employee_workplace.filter(designacao=True).count()
            == employee._raw_locations(option=WORK_ASSIGNMENT).count()
        )

        query = employee_workplace.filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim=None) | Q(data_vigencia_fim__gte=date))
        )

        query = query.filter(designacao=True)

        assert (
            query.count()
            == employee._raw_locations(option=WORK_ASSIGNMENT, date=date).count()
        )

        assert (
            query.filter().count()
            == employee._raw_locations(option=WORK_ASSIGNMENT, date=date).count()
        )

        assert (
            query.filter(ativo=True).count()
            == employee._raw_locations(
                option=WORK_ASSIGNMENT, date=date, actve=True
            ).count()
        )


class ServidorVinculoTestCase(AthenasTestCase):

    avoid = False
    classe = ServidorVinculo


class DependenteTestCase(AthenasTestCase):

    avoid = False
    classe = Dependente


class DocsDadosEspecificosTestCase(AthenasTestCase):

    avoid = False
    classe = DocsDadosEspecificos


class DocumentoTestCase(AthenasTestCase):

    avoid = False
    classe = Documento


class TelefoneTestCase(AthenasTestCase):

    avoid = False
    classe = Telefone


class EnderecoTestCase(AthenasTestCase):

    avoid = False
    classe = Endereco


class DadoBancarioConsignatarioTestCase(AthenasTestCase):

    avoid = False
    classe = DadoBancarioConsignatario


class DadoBancarioPessoaTestCase(AthenasTestCase):

    avoid = False
    classe = DadoBancarioPessoa


class CursoTestCase(AthenasTestCase):

    avoid = False
    classe = Curso


class CarreiraTestCase(AthenasTestCase):

    avoid = False
    classe = Carreira


class CargoTestCase(AthenasTestCase):

    avoid = False
    classe = Cargo


class PublicacaoTestCase(AthenasTestCase):

    avoid = False
    classe = Publicacao


class QuadroTestCase(AthenasTestCase):

    avoid = False
    classe = Quadro

    def test_carga_horaria(self):
        quadro = Quadro.objects.latest("pk")
        assert quadro.carga_horaria

    def test_tipo_carga_horaria(self):
        quadro = Quadro.objects.latest("pk")
        assert quadro.tipo_carga_horaria


class CargoQuadroTestCase(AthenasTestCase):

    avoid = False
    classe = CargoQuadro

    def test_save(self):
        classe = self.classe.objects.latest("pk")
        classe.save()


class ServidorLocalizacaoTestCase(AthenasTestCase):

    avoid = False
    classe = ServidorLocalizacao


# def validate_publicacao(self):
#     return True


class EmployeeWorkplaceTestCase(AthenasTestCase):

    avoid = False
    classe = ServidorLotacao

    def setUp(self):
        self.lotacao_vigente = (
            ServidorLotacao.objects.filter(
                Q(designacao=False)
                & Q(
                    Q(data_vigencia_fim__gte=datetime.now().date())
                    | Q(data_vigencia_fim=None)
                )
            )
            .exclude(publicacao=None)
            .latest("pk")
        )
        # print 'lotacao_vigente'
        # print self.lotacao_vigente, self.lotacao_vigente.data_vigencia_fim
        self.lotacao_sem_vigencia = ServidorLotacao.objects.filter(
            designacao=False, data_vigencia_fim__lt=datetime.now().date()
        ).latest("pk")
        # print 'lotacao_sem_vigencia'
        # print self.lotacao_sem_vigencia, self.lotacao_sem_vigencia.data_vigencia_fim
        self.lotacao = ServidorLotacao.objects.filter(designacao=False).latest("pk")
        # print 'lotacao'
        # print self.lotacao, self.lotacao.data_vigencia_fim

        self.designacao_vigente = ServidorLotacao.objects.filter(
            Q(designacao=True)
            & Q(
                Q(data_vigencia_fim__gte=datetime.now().date())
                | Q(data_vigencia_fim=None)
            )
        ).latest("pk")
        # print 'designacao_vigente'
        # print self.designacao_vigente, self.designacao_vigente.data_vigencia_fim
        self.designacao_sem_vigencia = ServidorLotacao.objects.filter(
            designacao=True, data_vigencia_fim__lt=datetime.now().date()
        ).latest("pk")
        # print 'designacao_sem_vigencia'
        # print self.designacao_sem_vigencia, self.designacao_sem_vigencia.data_vigencia_fim
        self.designacao = ServidorLotacao.objects.filter(designacao=True).latest("pk")
        # print 'designacao'
        # print self.designacao, self.designacao.data_vigencia_fim

        self.validate_publicacao_orig = ServidorLotacao.validate_publicacao
        self.validate_posse_orig = ServidorLotacao.validate_posse
        self.validate_lotacao_fora_organograma_orig = (
            ServidorLotacao.validate_lotacao_fora_organograma
        )
        self.validate_duplicate_workplace_orig = (
            ServidorLotacao.validate_duplicate_workplace
        )
        ServidorLotacao.validate_publicacao = validate_publicacao
        ServidorLotacao.validate_posse = validate_posse
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma
        )
        ServidorLotacao.validate_duplicate_workplace = validate_duplicate_workplace

    def tearDown(self):
        ServidorLotacao.validate_publicacao = self.validate_publicacao_orig
        ServidorLotacao.validate_posse = self.validate_posse_orig
        ServidorLotacao.validate_lotacao_fora_organograma = (
            self.validate_lotacao_fora_organograma_orig
        )
        ServidorLotacao.validate_duplicate_workplace = (
            self.validate_duplicate_workplace_orig
        )

    @unittest.skip("skipping test_cmd_atualizar_ativo")
    def test_cmd_atualizar_ativo(self):
        servidor_lotacao = (
            self.classe.objects.filter(ativo=True, lotacao__organograma=True)
            .exclude(publicacao=None)
            .latest("pk")
        )
        ativo = servidor_lotacao.ativo
        self.classe.objects.filter(pk=servidor_lotacao.pk).update(ativo=(not ativo))
        ServidorLotacao.cmd_atualizar_ativo(
            servidor_lotacao=[
                servidor_lotacao.pk,
            ]
        )
        assert ativo == self.classe.objects.get(pk=servidor_lotacao.pk).ativo
        self.classe.objects.filter(pk=servidor_lotacao.pk).update(ativo=ativo)

    @unittest.skip("skipping test_cmd_update_estado_all")
    def test_cmd_atualizar_ativo_all(self):
        # date = datetime.now().date()
        # query = (Q(data_vigencia_fim__gt=date) | Q(data_vigencia_fim=None)) & Q(servidor__tipo='M')
        query = Q(
            servidor__tipo__in=[
                "M",
            ]
        )
        self.classe.cmd_atualizar_ativo(
            servidor_lotacao=self.classe.objects.filter(query).values("pk")
        )

    @unittest.skip("skipping test_create_work_assignment")
    def test_create_work_assignment(self):
        EmployeeWorkplaceTestCase.create_work_assignment(
            employee_type=["S", "M"], delete_workplace_transformed_work_assignment=True
        )

    @classmethod
    def create_work_assignment(
        cls,
        employee_type=[
            "S",
        ],
        delete_workplace_transformed_work_assignment=False,
    ):
        """
        Script:

        Criar exercício para todas lotações.
        """
        print("\nCriando Designações a partir de Lotações...")
        ServidorLotacao.validate_publicacao = validate_publicacao

        for employee_workplace in ServidorLotacao.objects.filter(
            servidor__tipo__in=employee_type,
            designacao=False,
            servidor__ativo=True,
            ativo=True,
        ).order_by("servidor"):
            fields_update = {}
            if not employee_workplace.movimentacao_posse:
                possession = employee_workplace.servidor.get_posses_ativas(
                    employee_workplace.data_vigencia_inicio
                )
                if possession.exists():
                    possession = possession.latest("pk")
                else:
                    possession = employee_workplace.servidor.posses.latest("pk")
                fields_update.update({"movimentacao_posse": possession})
            try:
                fields_update.update(
                    {
                        "designacao": True,
                        "responsible": employee_workplace.responsible,
                        "child_of": employee_workplace,
                    }
                )
                ServidorLotacao._create_by_copy(employee_workplace, fields_update)
            except Exception as err:
                log.info(
                    "%s -%s \nDesignação não criada!"
                    % (employee_workplace.servidor, employee_workplace)
                )
                # print('%s -%s \nDesignação não criada!' % (employee_workplace.servidor, employee_workplace))
                log.exception(err)
        print("Done.")

        if delete_workplace_transformed_work_assignment:
            print(
                "\nTentando apagar lotações que já foram transformadas em designações..."
            )
            employee_workplaces = ServidorLotacao.objects.filter(
                servidor__tipo__in=employee_type,
                designacao=False,
                servidor__ativo=True,
            ).exclude(lotacao__cargo_responsavel__tipo_lei_cargo="EF")
            for employee_workplace in employee_workplaces.order_by("servidor"):
                if employee_workplace.father_of.exists():
                    try:
                        print("Apagando: %s" % employee_workplace)
                        employee_workplace.delete()
                    except Exception as err:
                        print(err)
                else:
                    print("NÃO APAGOU")
                    print(
                        employee_workplace.servidor,
                        employee_workplace.servidor.is_ativo(),
                        employee_workplace,
                    )
            print("Done.")

    def test_validate_duplicate_workplace(self):
        employee_workplace = self.classe.objects.filter(
            ~Q(father_of=None) & Q(designacao=False) & Q(provisorio=False)
        ).latest("pk")
        new_kwargs = dict(
            [
                (fld.name, getattr(employee_workplace, fld.name))
                for fld in employee_workplace._meta.fields
                if fld.name != employee_workplace._meta.pk
            ]
        )
        new_kwargs.pop("id")
        if not new_kwargs.get("movimentacao_posse", None):
            possession = new_kwargs.get("servidor").get_posses_ativas(
                new_kwargs.get("data_vigencia_inicio")
            )
            if possession.exists():
                possession = possession.latest("pk")
            else:
                possession = new_kwargs.get("servidor").posses.latest("pk")
            new_kwargs.update({"movimentacao_posse": possession})
        if not new_kwargs.get("publicacao", None):
            new_kwargs.update({"publicacao": Publicacao.objects.latest("pk")})
        new = ServidorLotacao(**new_kwargs)
        self.assertRaises(
            self.classe.LotacaoDuplicada, new.validate_duplicate_workplace
        )

    def test_validate_duplicate_work_assignment(self):
        employee_work_assignment = self.classe.objects.filter(
            ~Q(father_of=None) & Q(designacao=True) & Q(provisorio=False)
        ).latest("pk")
        new_kwargs = dict(
            [
                (fld.name, getattr(employee_work_assignment, fld.name))
                for fld in employee_work_assignment._meta.fields
                if fld.name != employee_work_assignment._meta.pk
            ]
        )
        new_kwargs.pop("id")
        if not new_kwargs.get("movimentacao_posse", None):
            possession = new_kwargs.get("servidor").get_posses_ativas(
                new_kwargs.get("data_vigencia_inicio")
            )
            if possession.exists():
                possession = possession.latest("pk")
            else:
                possession = new_kwargs.get("servidor").posses.latest("pk")
            new_kwargs.update({"movimentacao_posse": possession})
        if not new_kwargs.get("publicacao", None):
            new_kwargs.update({"publicacao": Publicacao.objects.latest("pk")})
        new = ServidorLotacao(**new_kwargs)
        self.assertRaises(Exception, new.validate_duplicate_work_assignment)

    # @unittest.skip("skipping test_is_ativo")
    def test_is_active(self):
        assert True == self.lotacao_vigente.is_active()
        assert False == self.lotacao_sem_vigencia.is_active()
        assert True == self.designacao_vigente.is_active()
        assert False == self.designacao_sem_vigencia.is_active()

    # @unittest.skip("skipping test_validate_lotacao_fora_organograma")
    def test_validate_lotacao_fora_organograma(self):
        ServidorLotacao.validate_lotacao_fora_organograma = (
            self.validate_lotacao_fora_organograma_orig
        )
        lotacao_vigente = ServidorLotacao.objects.filter(
            designacao=False, lotacao__organograma=True
        ).latest("pk")
        lotacao = lotacao_vigente.lotacao
        Lotacao.objects.filter(pk=lotacao.pk).update(organograma=False)
        lotacao_vigente = ServidorLotacao.objects.get(pk=lotacao_vigente.pk)
        self.assertRaises(Exception, lotacao_vigente.validate_lotacao_fora_organograma)
        Lotacao.objects.filter(pk=lotacao.pk).update(organograma=True)

    # @unittest.skip("skipping test_validate_lotacao_nao_escolhida")
    def test_validate_lotacao_nao_escolhida(self):
        lotacao = self.lotacao_vigente.lotacao
        ServidorLotacao.objects.filter(pk=self.lotacao_vigente.pk).update(lotacao=None)
        self.lotacao_vigente = ServidorLotacao.objects.get(pk=self.lotacao_vigente.pk)
        self.assertRaises(
            Exception, self.lotacao_vigente.validate_lotacao_nao_escolhida
        )
        ServidorLotacao.objects.filter(pk=self.lotacao_vigente.pk).update(
            lotacao=lotacao
        )

    # @unittest.skip("skipping test_validate_publicacao")
    def test_validate_publicacao(self):
        ServidorLotacao.validate_publicacao = self.validate_publicacao_orig
        servidor_lotacao = ServidorLotacao.objects.filter(ativo=True).latest("pk")
        publicacao = servidor_lotacao.publicacao
        ServidorLotacao.objects.filter(pk=servidor_lotacao.pk).update(publicacao=None)
        servidor_lotacao = ServidorLotacao.objects.get(pk=servidor_lotacao.pk)
        self.assertRaises(Exception, servidor_lotacao.validate_publicacao)
        ServidorLotacao.objects.filter(pk=servidor_lotacao.pk).update(
            publicacao=publicacao
        )

    @unittest.skip("skipping test_validate")
    def test_validate(self):
        publicacao = self.lotacao_vigente.publicacao
        ServidorLotacao.objects.filter(pk=self.lotacao_vigente.pk).update(
            publicacao=None
        )
        self.lotacao_vigente = ServidorLotacao.objects.get(pk=self.lotacao_vigente.pk)
        self.assertRaises(Exception, self.lotacao_vigente.validate)
        ServidorLotacao.objects.filter(pk=self.lotacao_vigente.pk).update(
            publicacao=publicacao
        )

        data_vigencia = publicacao.data_vigencia
        Publicacao.objects.filter(pk=publicacao.pk).update(data_vigencia=None)
        self.lotacao_vigente = ServidorLotacao.objects.get(pk=self.lotacao_vigente.pk)
        self.assertRaises(Exception, self.lotacao_vigente.validate)
        Publicacao.objects.filter(pk=publicacao.pk).update(data_vigencia=data_vigencia)

        posse = self.lotacao_vigente.movimentacao_posse
        servidor = posse.servidor
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(
            servidor=Servidor.objects.get(matricula=94109)
        )
        self.lotacao_vigente = ServidorLotacao.objects.get(pk=self.lotacao_vigente.pk)
        self.assertRaises(Exception, self.lotacao_vigente.validate)
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(servidor=servidor)

    def test_anotacao(self):
        pass

    def test_get_texto(self):
        pass

    def test_delete(self):
        pass

    def test_finalizar_lotacao_ativa(self):
        pass

    def test_get_lotacao(self):
        pass

    # @unittest.skip("skipping test_update_chief_immediate_employee")
    def test_update_chief_immediate_employee(self):
        servidor_lotacao = None
        for servidor in Servidor.objects.filter():
            if servidor.workplace.exists():
                servidor_lotacao = servidor.workplace.latest("pk")
        if servidor_lotacao:
            Servidor.objects.filter(pk=servidor.pk).update(chefe_imediato=None)
            self.classe.objects.get(
                pk=servidor_lotacao.pk
            ).update_chief_immediate_employee()
            assert not Servidor.objects.get(pk=servidor.pk).chefe_imediato is None

    @unittest.skip("skipping test_lotacao_por_provimento")
    def test_lotacao_por_provimento(self):
        posse = None
        promocao = None
        remocao = None
        for mov in MovimentacaoPessoal.objects.filter(
            servidor__ativo=True, servidor__tipo="M"
        ):
            if posse is None:
                try:
                    posse = (
                        mov.movimentacaoposse
                        if (
                            MovimentacaoPromocao.objects.filter(
                                servidor=mov.servidor
                            ).count()
                            == 0
                            and MovimentacaoRemocaoMembro.objects.filter(
                                servidor=mov.servidor
                            ).count()
                            == 0
                        )
                        and mov.movimentacaoposse.quadro.cargo.lotacao_responsavel
                        else None
                    )
                except Exception:
                    pass
            if promocao is None:
                try:
                    promocao = (
                        mov.movimentacaoposse.movimentacaopromocao
                        if mov.movimentacaoposse.movimentacaopromocao.lotacao_destino
                        else None
                    )
                except Exception:
                    pass
            if remocao is None:
                try:
                    remocao = (
                        mov.movimentacaoposse.movimentacaoremocaomembro
                        if mov.movimentacaoposse.movimentacaoremocaomembro.lotacao_destino
                        else None
                    )
                except Exception:
                    pass
            if posse and promocao and remocao:
                break

            # if isinstance(provimento, MovimentacaoRemocaoMembro):
            #     lotacao = provimento.lotacao_destino
            # elif (isinstance(provimento, MovimentacaoPosse) or isinstance(provimento, MovimentacaoPromocao) or
            #         isinstance(provimento, MovimentacaoTitularizacao)):
            #     lotacao = provimento.quadro.cargo.lotacao_responsavel

        if posse:
            print("posse", posse, posse.quadro.cargo.lotacao_responsavel)
        if promocao:
            print(
                "promocao",
                promocao.servidor,
                promocao,
                promocao.quadro.cargo.lotacao_responsavel,
            )
        if remocao:
            # print 'remocao', remocao.servidor, remocao, remocao.lotacao_destino
            # print self.classe.get_lotacao(remocao.servidor, remocao.lotacao_destino, remocao.publicacao_movimentacao, remocao.data_exercicio)
            servidor_lotacao = self.classe.get_lotacao(
                remocao.servidor,
                remocao.lotacao_destino,
                remocao.publicacao_movimentacao,
                remocao.data_exercicio,
            )
            assert remocao.lotacao_destino == servidor_lotacao.lotacao


class PeriodoRequisicaoTestCase(AthenasTestCase):

    avoid = False
    classe = PeriodoRequisicao


class MovimentacaoPosseTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoPosse

    def setUp(self):
        self.validate_publicacao_orig = self.classe.validate_publicacao
        self.validate_publicacao_desligamento_orig = (
            MovimentacaoDesligamento.validate_publicacao
        )
        self.classe.validate_publicacao = validate_publicacao_movimentacao

        MovimentacaoDesligamento.validate_publicacao = validate_publicacao_movimentacao

        self.validate_publicacao_posse_orig = (
            MovimentacaoDesligamento.validate_publicacao_posse
        )
        MovimentacaoDesligamento.validate_publicacao_posse = validate_publicacao_posse

        self.validate_desligamento_automatico_membro_orig = (
            self.classe.validate_desligamento_automatico_membro
        )
        self.classe.validate_desligamento_automatico_membro = (
            validate_desligamento_automatico_membro
        )

    def tearDown(self):
        self.classe.validate_publicacao = self.validate_publicacao_orig
        MovimentacaoDesligamento.validate_publicacao = (
            self.validate_publicacao_desligamento_orig
        )
        MovimentacaoDesligamento.validate_publicacao_posse = (
            self.validate_publicacao_posse_orig
        )
        self.classe.validate_desligamento_automatico_membro = (
            self.validate_desligamento_automatico_membro_orig
        )

    # def test_atualiza_cache_ativo(self):
    #     err = None
    #     try:
    #         posse = MovimentacaoPosse.objects.filter(quadro__cargo__tipo_lei_cargo='EF').latest('pk')
    #         posse.save()
    #     except Exception as err:
    #         pass
    #     assert err is None
    #     err = None
    #     try:
    #         posse = MovimentacaoPosse.objects.filter(quadro__cargo__tipo_lei_cargo='CM').latest('pk')
    #         posse.save()
    #     except Exception as err:
    #         pass
    #     assert err is None
    #     err = None
    #     try:
    #         posse = MovimentacaoPosse.objects.filter(quadro__cargo__tipo_lei_cargo='FC').latest('pk')
    #         posse.save()
    #     except Exception as err:
    #         pass
    #     assert err is None

    def test_atualiza_cache_ativo(self):
        """
        Este método deve testar test_atualiza_cache_ativo de MovimentacaoPosse.
        """
        posses = MovimentacaoPosse.objects.filter(
            quadro__cargo__tipo_lei_cargo__in=("AC", "ES", "EL")
        ).values("pk")
        desligamento = (
            MovimentacaoDesligamento.objects.filter(
                data_desligamento__lt=datetime.now()
            )
            .exclude(movimentacao_posse__pk__in=posses)
            .latest("pk")
        )
        posse = desligamento.movimentacao_posse
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=True)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is True:
            raise Exception(
                "Não modificou o campo ativo corretamente! Deveria ser False."
            )

        log.debug("----------------------------------------")
        desligamento = MovimentacaoAposentadoria.objects.filter(
            data_desligamento__lt=datetime.now()
        ).latest("pk")
        posse = desligamento.movimentacao_posse
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=True)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is True:
            print("Não modificou o campo ativo corretamente! Deveria ser False.")
            assert False

        posse = MovimentacaoPosse.objects.filter(data_desligamento=None).latest("pk")
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=False)
        posse = MovimentacaoPosse.objects.get(pk=posse.pk)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is False:
            raise Exception(
                "Não modificou o campo ativo corretamente! Deveria ser True."
            )

        posse = MovimentacaoPosse.objects.filter(
            ~Q(data_desligamento=None) & Q(data_desligamento__lt=datetime.now())
        ).latest("pk")
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=True)
        posse = MovimentacaoPosse.objects.get(pk=posse.pk)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is True:
            raise Exception(
                "Não modificou o campo ativo corretamente! Deveria ser False."
            )

        MovimentacaoPosse.objects.filter(pk=posse.pk).update(
            ativo=True, data_desligamento=None
        )
        posse = MovimentacaoPosse.objects.get(pk=posse.pk)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is True:
            raise Exception(
                "Não modificou o campo ativo corretamente! Deveria ser False."
            )
        if MovimentacaoPosse.objects.get(pk=posse.pk).data_desligamento is None:
            raise Exception(
                "Não modificou o campo data_desligamento corretamente! Deveria possuir valor."
            )

        desligamento = (
            MovimentacaoPosse.objects.filter(
                servidor__tipo="S",
                quadro__cargo__tipo_lei_cargo="EF",
                data_desligamento__lt=datetime.now(),
            )
            .latest("data_desligamento")
            .desligamento
        )
        data_desligamento_atual = desligamento.data_desligamento
        desligamento.data_desligamento = (datetime.now() + relativedelta(days=1)).date()
        desligamento.save()
        desligamento = MovimentacaoDesligamento.objects.filter(
            pk=desligamento.pk
        ).latest("pk")
        posse = desligamento.movimentacao_posse
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=False)
        posse.set_data_desligamento()
        posse.atualiza_cache_ativo()
        if MovimentacaoPosse.objects.get(pk=posse.pk).ativo is False:
            raise Exception(
                "Não modificou o campo ativo corretamente! Deveria ser True."
            )
        desligamento.data_desligamento = data_desligamento_atual
        desligamento.save()

    #     #PRECISA DE MOCK PARA REALIZAR OS TESTES ABAIXO
    #     # desligamento = MovimentacaoPosse.objects.filter(
    #     #     servidor__tipo='S', quadro__cargo__tipo_lei_cargo='EF', data_desligamento__lt=datetime.now()
    #     # ).latest('data_desligamento').desligamento
    #     # signals.post_delete.send(sender=MovimentacaoDesligamento, instance=desligamento)
    #     # desligamento = MovimentacaoDesligamento.objects.filter(pk=desligamento.pk).latest('pk')
    #     # ativo = desligamento.movimentacao_posse.ativo
    #     # data_desligamento = desligamento.movimentacao_posse.data_desligamento
    #     # if ativo is False:
    #     #     raise Exception('Ativo %s. Ativo deveria ser True!' % ativo)
    #     # if not data_desligamento is None:
    #     #     raise Exception('Data de desligamento %s. Data de desligamento deveria ser None!' % data_desligamento)

    # @unittest.skip('skipping test_cmd_atualizar_cache_ativo')
    def test_cmd_atualizar_cache_ativo(self):
        # query = (Q(data_desligamento__lt=hoje) & Q(ativo=True))
        posse = MovimentacaoPosse.objects.filter(
            data_desligamento__lt=datetime.now()
        ).latest("data_desligamento")
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=True)
        MovimentacaoPosse.cmd_atualizar_cache_ativo(
            [
                posse.pk,
            ]
        )
        assert MovimentacaoPosse.objects.get(pk=posse.pk).ativo is False
        posse = MovimentacaoPosse.objects.filter(
            data_desligamento__lt=datetime.now()
        ).latest("data_desligamento")
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(ativo=True)
        MovimentacaoPosse.cmd_atualizar_cache_ativo([posse.pk])
        assert MovimentacaoPosse.objects.get(pk=posse.pk).ativo is False

    @unittest.skip("skipping test_cmd_atualizar_cache_ativo")
    def test_cmd_atualizar_cache_ativo(self):
        MovimentacaoPosse.cmd_atualizar_cache_ativo()

    # @unittest.skip('skipping test_set_data_desligamento')
    def test_set_data_desligamento(self):
        posse = MovimentacaoPosse.objects.filter(~Q(data_desligamento=None)).latest(
            "data_desligamento"
        )
        MovimentacaoPosse.objects.filter(pk=posse.pk).update(data_desligamento=None)
        posse.set_data_desligamento()
        assert not MovimentacaoPosse.objects.get(pk=posse.pk).data_desligamento is None

    def test_data_desligamento(self):
        possession = MovimentacaoPosse.objects.filter(
            ~Q(data_desligamento=None)
        ).latest("data_desligamento")
        assert possession._data_desligamento

    def test_desligamento_automatico_membro(self):
        employee = Servidor.objects.get(matricula=13293)
        possession = employee.posses.latest("data_desligamento")
        possession._data_desligamento


class MovimentacaoRequisicaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoRequisicao

    def test_salva(self):
        if self.classe.objects.filter(self.classe.filtro_periodo_vigente()).exists():
            self.classe.objects.filter(self.classe.filtro_periodo_vigente()).latest(
                "pk"
            ).save()

    def test_uma_requisicao_nenhum_desligamento(self):
        requisicao = self.classe.objects.filter(posse_origem__desligamento=None).latest(
            "pk"
        )
        self.classe.uma_requisicao_nenhum_desligamento(requisicao)


class MovimentacaoAproveitamentoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoAproveitamento

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoPromocaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoPromocao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoTitularizacaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoTitularizacao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoReadaptacaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoReadaptacao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoReconducaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoReconducao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoReintegracaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoReintegracao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoReversaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoReversao

    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()


class MovimentacaoConcessaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoConcessao


class MovimentacaoRemocaoTestCase(unittest.TestCase):

    @unittest.skip("skipping test_")
    def test_remocao(self):
        # MOTIVO_REMOCAO = (
        #     (1, 'OFÍCIO'),
        #     (2, 'REQUERIMENTO'),
        #     (3, 'PERMUTA'),
        #     #(4, 'OUTROS')
        # )

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

        servidor = None

        # REMOÇÃO PADRÃO
        for posse in (
            MovimentacaoPosse.objects.filter(
                Q(servidor__tipo="S")
                & Q(quadro__cargo__tipo_lei_cargo="EF")
                & Q(ativo=True)
            )
            .exclude(servidor__servidor_lotacao=None)
            .exclude(servidor__servidor_lotacao__movimentacao_posse=None)
            .exclude(servidor__servidor_lotacao__publicacao=None)
            .exclude(
                servidor__pk__in=MovimentacaoRemocao.objects.filter().values("servidor")
            )
        ):
            lotacao_destino = None
            # print posse.servidor, 'locations', posse.servidor.work_assignment
            if len(posse.servidor.work_assignment) > 0:
                for lotacao in Lotacao.objects.filter(organograma=True):
                    if posse.servidor.work_assignment.latest("pk").lotacao != lotacao:
                        lotacao_destino = lotacao
                        break
                remocao = MovimentacaoRemocao(
                    publicacao_movimentacao=mock(
                        model=Publicacao, query=(~Q(data_vigencia=None))
                    ),
                    servidor=posse.servidor,
                    remocao=1,
                    lotacao_destino=lotacao_destino,
                    data_vigencia=datetime.now().date(),
                )
                remocao.save()
                break

        print("servidor", servidor)

        # # #REMOÇÃO PERMUTA
        # exclude = [servidor.pk, ]
        # servidor = MovimentacaoPosse.objects.filter(
        #     Q(servidor__tipo='S') &
        #     Q(quadro__cargo__tipo_lei_cargo='EF') &
        #     Q(ativo=True)
        # ).exclude(
        #     servidor__servidor_lotacao=None
        # ).exclude(
        #     servidor__servidor_lotacao__movimentacao_posse=None
        # ).exclude(
        #     servidor__servidor_lotacao__publicacao=None
        # ).exclude(
        #     servidor__pk__in=exclude).exclude(servidor__pk__in=MovimentacaoRemocao.objects.filter().values('servidor')).latest('pk').servidor
        # exclude.append(servidor.pk)
        # servidor_permutado = MovimentacaoPosse.objects.filter(
        #     Q(servidor__tipo='S') &
        #     Q(quadro__cargo__tipo_lei_cargo='EF') &
        #     Q(ativo=True)
        # ).exclude(
        #     servidor__servidor_lotacao=None
        # ).exclude(
        #     servidor__servidor_lotacao__movimentacao_posse=None
        # ).exclude(
        #     servidor__servidor_lotacao__publicacao=None
        # ).exclude(
        #     servidor__pk__in=exclude).exclude(servidor__pk__in=MovimentacaoRemocao.objects.filter().values('servidor')).latest('pk').servidor

        # lotacao_destino = None
        # for lotacao in Lotacao.objects.filter(organograma=True):
        #     if servidor.get_lotacao().latest('pk').lotacao != lotacao:
        #         lotacao_destino = lotacao
        #         break
        # remocao = MovimentacaoRemocao(
        #     publicacao_movimentacao=mock(model=Publicacao, query=(~Q(data_vigencia=None))),
        #     servidor=servidor,
        #     remocao=3,
        #     servidor_permuta=servidor_permutado,
        #     data_vigencia=datetime.now().date())
        # remocao.save()

        ServidorLotacao.validate_publicacao = validate_publicacao_orig
        ServidorLotacao.validate_posse = validate_posse_orig
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma_orig
        )

    def test_update_last_designation(self):
        remocao = MovimentacaoRemocao.objects.filter().latest("pk")
        if remocao:
            sl = ServidorLotacao.objects.filter(
                servidor=remocao.servidor, designacao=False
            ).latest("data_vigencia")
            if sl:
                data_vigencia_fim = sl.data_vigencia_fim
                assert remocao._update_last_designation() is True

                ServidorLotacao.objects.filter(pk=sl.pk).update(
                    data_vigencia_fim=data_vigencia_fim
                )

    def test_save(self):
        if MovimentacaoRemocao.objects.filter(remocao=1, servidor__tipo="S").exists():
            MovimentacaoRemocao.objects.filter(remocao=1, servidor__tipo="S").latest(
                "pk"
            ).save()
        if MovimentacaoRemocao.objects.filter(remocao=2, servidor__tipo="S").exists():
            MovimentacaoRemocao.objects.filter(remocao=2, servidor__tipo="S").latest(
                "pk"
            ).save()
        if MovimentacaoRemocao.objects.filter(remocao=3, servidor__tipo="S").exists():
            MovimentacaoRemocao.objects.filter(remocao=3, servidor__tipo="S").latest(
                "pk"
            ).save()

    def test_remocao(self):
        # MOTIVO_REMOCAO = (
        #     (1, 'OFÍCIO'),
        #     (2, 'REQUERIMENTO'),
        #     (3, 'PERMUTA'),
        #     #(4, 'OUTROS')
        # )
        # REMOÇÃO PADRÃO
        for possession in MovimentacaoPosse.objects.filter(
            quadro__cargo__tipo_lei_cargo="EF", ativo=True, servidor__tipo="S"
        ):
            if possession.servidor.workplace.exists():
                employee = possession.servidor
                break
        print(employee)
        lotacao_destino = None
        for lotacao in Lotacao.objects.filter(organograma=True):
            if employee.workplace.latest("pk").lotacao != lotacao:
                lotacao_destino = lotacao
                break
        remocao = MovimentacaoRemocao(
            servidor=employee,
            publicacao_movimentacao=Publicacao.objects.latest("pk"),
            remocao=1,
            lotacao_destino=lotacao_destino,
            data_vigencia=datetime.now().date(),
        )
        remocao.save()

        employee_exclude = [
            employee.pk,
        ]
        # REMOÇÃO PERMUTA
        for possession in MovimentacaoPosse.objects.filter(
            quadro__cargo__tipo_lei_cargo="EF", ativo=True, servidor__tipo="S"
        ).exclude(servidor__pk__in=employee_exclude):
            if possession.servidor.workplace.exists():
                employee = possession.servidor
                break
        print(employee)
        print(employee.workplace.latest("pk").lotacao)
        employee_exclude.append(employee.pk)

        for possession in MovimentacaoPosse.objects.filter(
            quadro__cargo__tipo_lei_cargo="EF", ativo=True, servidor__tipo="S"
        ).exclude(servidor__pk__in=employee_exclude):
            if possession.servidor.workplace.exists():
                servidor_permutado = possession.servidor
                break
        print(servidor_permutado)
        print(servidor_permutado.workplace.latest("pk").lotacao)
        remocao = MovimentacaoRemocao(
            servidor=employee,
            publicacao_movimentacao=Publicacao.objects.latest("pk"),
            remocao=3,
            servidor_permuta=servidor_permutado,
            data_vigencia=datetime.now().date(),
            lotacao_destino=servidor_permutado.workplace.latest("pk").lotacao,
        )
        remocao.save()


class MovimentacaoRedistribuicaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoRedistribuicao

    def test_save(self):
        if self.classe.objects.exists():
            self.classe.objects.filter().latest("pk").save()


class MovimentacaoEstabilizacaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoEstabilizacao

    def test_save(self):
        if self.classe.objects.exists():
            try:
                self.classe.objects.filter().latest("pk").save()
            except self.classe.AlreadyExists as err:
                print(err)
            except Exception as err:
                raise err


class DeclaracaoAtividadeTestCase(AthenasTestCase):

    avoid = False
    classe = DeclaracaoAtividade


def show_situation_employee(employee):
    date = datetime.now().date()
    query = SituacaoFuncional.objects.filter(servidor=employee).filter(
        Q(data_inicio__lte=date) & (Q(data_fim__gte=date) | Q(data_fim=None))
    )
    if not query.exists():
        query = SituacaoFuncional.objects.filter(servidor=employee)
    for st in query.order_by("-data_inicio"):
        print(st.__unicode_full__())


def show_situation_employee_all():
    for employee in Servidor.objects.filter(ativo=True):
        print("%s: %s" % (employee, employee.situacao_funcional_cache))


class SituacaoFuncionalTestCase(AthenasTestCase):

    avoid = False
    classe = SituacaoFuncional

    @unittest.skip("test_salva")
    def test_salva(self):
        if self.classe.objects.filter().exists():
            self.classe.objects.latest("pk").save()

    @unittest.skip("test_geral")
    def test_geral(self):
        # self.verifica_situacao_funcional_cache_ativo_com_afastamento()
        # self.verifica_situacao_afastado_sem_afastamento()
        # self.verifica_situacao_cancelada()
        # self.verifica_servidor_desligado_situacao_ativo()
        pass

        # self.mostra_situacao_funcional(matriculas=[4690, ])
        # self.mostra_ferias_afastamento_a_partir_amanha()
        # self.mostra_ferias_afastamento_fruindo()

        # self.verifica_situacao_funcional_incorreta()

        # SituacaoFuncionalManager.atualiza_situacao_funcional_servidor()

    @unittest.skip("test_geral")
    def test_functional_status_effective(self):
        SituacaoFuncional.functional_status_effective()

    @unittest.skip("test_create_possession_state")
    def test_create_possession_state(self):
        self.create_possession_state_raw()

    @classmethod
    def create_possession_state_raw(cls):
        SituacaoFuncional.objects.filter(situacao__in=["ATIVO"]).delete()
        SituacaoFuncional.objects.filter(situacao__icontains="INATIVO").delete()
        Servidor.objects.filter().update(situacao_funcional_cache="NOT_FOUND")

        SituacaoFuncionalTestCase.create_situations_possessions_and_fired()

        SituacaoFuncional.update_functional_status_effective(
            registry=[m.servidor.matricula for m in MovimentacaoPosse.objects.filter()]
        )

    @unittest.skip("test_create_situations_possessions_and_fired")
    def test_create_situations_possessions_and_fired(self):
        self.create_situations_possessions_and_fired()

    @classmethod
    def create_situations_possessions_and_fired(cls):
        validate_publicacao_posse_old = (
            MovimentacaoDesligamento.validate_publicacao_posse
        )
        validate_publicacao_old = MovimentacaoDesligamento.validate_publicacao

        validate_publicacao_old = MovimentacaoPosse.validate_publicacao
        gera_progressao_old = MovimentacaoPosse.gera_progressao

        MovimentacaoDesligamento.validate_publicacao_posse = lambda x: True
        MovimentacaoDesligamento.validate_publicacao = lambda x: True
        MovimentacaoPosse.validate_publicacao = lambda x: True
        MovimentacaoPosse.gera_progressao = lambda x: True

        possessions = MovimentacaoPosse.objects.filter()
        total = possessions.count()
        count = 1
        for possession in possessions.order_by("data_exercicio", "data_desligamento"):
            instance = possession.instancia_modelo
            print(instance)
            try:
                instance.save()
            except Exception as err:
                print(err)
            try:
                if hasattr(instance, "desligamento"):
                    fired = instance.desligamento
                    if hasattr(fired, "movimentacaoaposentadoria"):
                        fired = fired.movimentacaoaposentadoria
                    fired.save()
            except Exception as err:
                print(err)
            print("count: %s - total: %s" % (count, total))
            count += 1
        fireds = MovimentacaoDesligamento.objects.filter()
        total += fireds.count()
        for fired in fireds.order_by("data_desligamento"):
            print(fired)
            try:
                fired.save()
            except Exception as err:
                print(err)
            print("count: %s - total: %s" % (count, total))
            count += 1

        departures = afastamento_models.BaseLicencaAfastamento.objects.filter()
        total += departures.count()
        for departure in departures.order_by("data_fim"):
            departure = departure.instancia_modelo
            print(departure)
            try:
                departure.save()
            except Exception as err:
                print(err)
            print("count: %s - total: %s" % (count, total))
            count += 1

        MovimentacaoPosse.gera_progressao = gera_progressao_old
        MovimentacaoPosse.validate_publicacao = validate_publicacao_old
        MovimentacaoDesligamento.validate_publicacao_posse = (
            validate_publicacao_posse_old
        )
        MovimentacaoDesligamento.validate_publicacao = validate_publicacao_old

    @unittest.skip("test_update_functional_status_effective")
    def test_update_functional_status_effective(self):
        # self.classe.update_functional_status_effective()
        self.classe.update_functional_status_effective(
            registry=[m.servidor.matricula for m in MovimentacaoPosse.objects.filter()]
        )
        # self.classe.update_functional_status_effective(registry=[s.matricula for s in Servidor.objects.filter()])
        # self.classe.update_functional_status_effective(registry=[68707])

    @unittest.skip("test_show")
    def test_show(self):
        from rh.constants_functional_situations import FUNCTIONAL_STATE_INDEX_STR_TO_INT

        active = True
        employees = Servidor.objects.filter(
            # matricula=32701,
            # matricula=52104,
            ativo=active
        )
        print(employees.count())
        for employee in employees:
            print("")
            print(
                (
                    "----%s%s afastamento: %s"
                    % (employee, "-" * 30, employee.afastamento_ativo())
                )[0:100]
            )
            for sf in SituacaoFuncional.objects.filter(servidor=employee).order_by(
                "data_inicio"
            ):
                # print(('----%s%s' % (unicode(sf), '-' * 60))[0:80])
                # applicable_conditions = SITUATION_APPLICABLE(FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(sf.situacao))
                # validity = SituacaoFuncional.validate_validity(sf, applicable_conditions)
                validity = SituacaoFuncional.validate_validity(sf)
                if validity:
                    print(
                        sf,
                        DateUtils.date_to_str(sf.data_inicio),
                        DateUtils.date_to_str(sf.data_fim) if sf.data_fim else "----",
                        sf.situacao,
                        FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(sf.situacao),
                        "validity:",
                        validity,
                    )
            print("---------------------------------------------------")

    @unittest.skip("verifica_situacao_funcional_cache_ativo_com_afastamento")
    def verifica_situacao_funcional_cache_ativo_com_afastamento(self):
        """
        Este método verifica e mostra os servidores que possuem situacação funcional ACTIVE, porém possuem
        afastamento ativo naquele momemnto.
        """
        print("verifica_situacao_funcional_cache_ativo_com_afastamento")
        for servidor in Servidor.objects.filter():
            if (
                servidor.situacao_funcional_cache == "ATIVO"
                and servidor.afastamento_ativo()
            ):
                afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
                    servidor=servidor, estado=ACTIVE
                )
                for afastamento in afastamentos:
                    print(
                        afastamento.pk,
                        afastamento,
                        "de",
                        DateUtils.date_to_str(afastamento.data_inicio),
                        "->(PREVISTA: %s) ->"
                        % (
                            DateUtils.date_to_str(afastamento.data_prevista)
                            if afastamento.data_prevista
                            else "-----------"
                        ),
                        (
                            DateUtils.date_to_str(afastamento.data_fim)
                            if afastamento.data_fim
                            else "-----------"
                        ),
                    )
                    afastamento.instancia_modelo.save()
                    print("---------------------")
                break

    @unittest.skip("verifica_situacao_afastado_sem_afastamento")
    def verifica_situacao_afastado_sem_afastamento(self):
        print("verifica_situacao_afastado_sem_afastamento")
        for servidor in Servidor.objects.filter():
            if (
                servidor.situacao_funcional_cache != "ATIVO"
                and servidor.afastamento_ativo() is False
            ):
                for (
                    afastamento
                ) in afastamento_models.BaseLicencaAfastamento.objects.filter(
                    servidor=servidor, estado=ACTIVE
                ):
                    if (
                        afastamento.servidor.situacao_funcional_cache
                        == afastamento.situacao_funcional
                        and afastamento.servidor.afastamento_ativo()
                    ):
                        print(
                            afastamento.servidor,
                            afastamento.servidor.situacao_funcional_cache,
                        )
                        print(
                            afastamento.pk,
                            afastamento,
                            "de",
                            DateUtils.date_to_str(afastamento.data_inicio),
                            "->(PREVISTA: %s) ->"
                            % (
                                DateUtils.date_to_str(afastamento.data_prevista)
                                if afastamento.data_prevista
                                else "-----------"
                            ),
                            (
                                DateUtils.date_to_str(afastamento.data_fim)
                                if afastamento.data_fim
                                else "-----------"
                            ),
                        )
                        print("---------------------")
                break

    @unittest.skip("verifica_situacao_cancelada")
    def verifica_situacao_cancelada(self):
        print("verifica_situacao_cancelada")
        data_fim = datetime.now() - relativedelta(days=1)
        afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
            data_fim__lte=data_fim
        ).order_by("servidor")
        for afastamento in afastamentos:
            situacao_funcional = SituacaoFuncional.objects.filter(
                situacao=afastamento.situacao_funcional,
                servidor=afastamento.servidor,
                data_inicio=afastamento.data_inicio,
                data_fim=afastamento.data_fim,
            )
            if (
                afastamento.servidor.situacao_funcional_cache != "ATIVO"
                and afastamento.estado == CANCELED
                and situacao_funcional.exists()
            ):
                # print afastamento.servidor, afastamento.servidor.situacao_funcional_cache
                situacao_funcional = situacao_funcional[0]
                print(
                    "SERVIDOR SITUAÇÃO FUNCIONAL",
                    afastamento.servidor.situacao_funcional_cache,
                )
                print(
                    situacao_funcional,
                    "de",
                    DateUtils.date_to_str(situacao_funcional.data_inicio),
                    " -> ",
                    (
                        DateUtils.date_to_str(situacao_funcional.data_fim)
                        if situacao_funcional.data_fim
                        else "-----------"
                    ),
                )
                print(
                    afastamento.pk,
                    afastamento,
                    "de",
                    DateUtils.date_to_str(afastamento.data_inicio),
                    "->(PREVISTA: %s) ->"
                    % (
                        DateUtils.date_to_str(afastamento.data_prevista)
                        if afastamento.data_prevista
                        else "-----------"
                    ),
                    (
                        DateUtils.date_to_str(afastamento.data_fim)
                        if afastamento.data_fim
                        else "-----------"
                    ),
                    afastamento.get_estado_display(),
                )
                print("---------------------")
            break

    @unittest.skip("verifica_servidor_desligado_situacao_ativo")
    def verifica_servidor_desligado_situacao_ativo(self):
        print("verifica_servidor_desligado_situacao_ativo")
        servidores = (
            Servidor.objects.filter(ativo=False)
            .exclude(situacao_funcional_cache__icontains="INATIVO_")
            .order_by("pessoa_fisica")
        )
        for servidor in servidores:
            if servidor.situacao_funcional_cache != "NOT_FOUND":
                print(servidor)
                print("%s%s" % (servidor.situacao_funcional_cache, "-" * 20))[
                    0:20
                ], "ATIVO", servidor.is_ativo(), "AFASTAMENTOS", servidor.afastamento_ativo()
                # if servidor.afastamento_ativo():
                #   print BaseLicencaAfastamento.objects.filter(servidor=servidor, estado=ATIVO)
                if servidor.is_ativo() is False and servidor.posses.exists():
                    print(servidor.posses.latest("data_desligamento"))
                    servidor.posses.latest("data_desligamento").desligamento.save()
                else:
                    print("Não possui desligamento!")
                    Servidor.objects.filter(pk=servidor.pk).update(
                        situacao_funcional_cache="NOT_FOUND"
                    )
                self.mostra_situacao_funcional([servidor.matricula])
                print("-----------------------------------------------")
            break
            # if servidor.situacao_funcional_cache:
            #     # print afastamento.servidor, afastamento.servidor.situacao_funcional_cache
            #     situacao_funcional= situacao_funcional[0]
            #     print situacao_funcional, 'de', DateUtils.date_to_str(situacao_funcional.data_inicio), ' -> ', DateUtils.date_to_str(situacao_funcional.data_fim) if situacao_funcional.data_fim else '-----------'
            #     print afastamento.get_estado_display()
            #     print afastamento.pk, afastamento, 'de', DateUtils.date_to_str(afastamento.data_inicio), '->(PREVISTA: %s) ->' % (DateUtils.date_to_str(afastamento.data_prevista) if afastamento.data_prevista else '-----------'), DateUtils.date_to_str(afastamento.data_fim) if afastamento.data_fim else '-----------'
            #     print '---------------------'

    @unittest.skip("mostra_situacao_funcional")
    def mostra_situacao_funcional(self, matriculas=[]):
        print("MOSTRA SITUAÇÃO FUNCIONAL")
        situacoes = SituacaoFuncional.objects.filter(servidor__matricula__in=matriculas)
        for sf in situacoes.order_by("data_inicio"):
            print(
                sf.servidor,
                "pk=",
                sf.pk,
                "|%s|" % sf.content_type,
                sf,
                "de",
                DateUtils.date_to_str(sf.data_inicio),
                "->",
                DateUtils.date_to_str(sf.data_fim) if sf.data_fim else "-----------",
            )
        print("total", situacoes.count())

    @unittest.skip("mostra_ferias_afastamento_a_partir_amanha")
    def mostra_ferias_afastamento_a_partir_amanha(self):
        print("mostra_ferias_afastamento_a_partir_amanha")
        afastamentos = (
            afastamento_models.FeriasAfastamento.objects.filter(
                data_inicio__gt=(datetime.now() + relativedelta(days=1)),
                data_inicio__lt=(datetime.now() + relativedelta(days=30)),
                servidor__tipo="S",
            )
            .exclude(estado=CANCELED)
            .order_by("servidor")[0:10]
        )
        for afastamento in afastamentos:
            print(
                afastamento.pk,
                afastamento,
                "de",
                DateUtils.date_to_str(afastamento.data_inicio),
                "->(PREVISTA: %s) ->"
                % (
                    DateUtils.date_to_str(afastamento.data_prevista)
                    if afastamento.data_prevista
                    else "-----------"
                ),
                (
                    DateUtils.date_to_str(afastamento.data_fim)
                    if afastamento.data_fim
                    else "-----------"
                ),
            )
            print("---------------------")

    @unittest.skip("mostra_ferias_afastamento_fruindo")
    def mostra_ferias_afastamento_fruindo(self):
        data_inicio = datetime.now() - relativedelta(days=30)
        data_fim = datetime.now()
        print(
            "mostra_ferias_afastamento_fruindo a partir de %s a %s"
            % (DateUtils.date_to_str(data_inicio), DateUtils.date_to_str(data_fim))
        )
        afastamentos = (
            afastamento_models.FeriasAfastamento.objects.filter(
                data_inicio__gt=data_inicio,
                data_inicio__lt=data_fim,
                servidor__tipo="S",
            )
            .exclude(estado=CANCELED)
            .order_by("servidor")[0:10]
        )
        for afastamento in afastamentos:
            print(
                afastamento.pk,
                afastamento,
                "de",
                DateUtils.date_to_str(afastamento.data_inicio),
                "->(PREVISTA: %s) ->"
                % (
                    DateUtils.date_to_str(afastamento.data_prevista)
                    if afastamento.data_prevista
                    else "-----------"
                ),
                (
                    DateUtils.date_to_str(afastamento.data_fim)
                    if afastamento.data_fim
                    else "-----------"
                ),
            )
            print("---------------------")

    @unittest.skip("verifica_situacao_funcional_incorreta")
    def verifica_situacao_funcional_incorreta(self):
        servidores = Servidor.objects.filter()
        print("total de servidores", servidores.count())
        situacao_ativo_com_afastamento = []
        situacao_afastado_sem_afastamento = []
        for servidor in servidores:
            afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
                servidor=servidor
            )
            afastamentos_ativos = afastamentos.filter(estado=ACTIVE)
            if (
                servidor.situacao_funcional_cache == "ATIVO"
                and afastamentos_ativos.count()
            ):
                situacao_ativo_com_afastamento.append(
                    (servidor, servidor.situacao_funcional_cache, afastamentos_ativos)
                )
            elif (
                (servidor.situacao_funcional_cache.find("ATIVO_") != -1)
                and (servidor.situacao_funcional_cache.find("INATIVO_") == -1)
                and not afastamentos_ativos.exists()
                and servidor.situacao_funcional_cache != "ATIVO"
            ):
                situacao_afastado_sem_afastamento.append(
                    (servidor, servidor.situacao_funcional_cache, afastamentos_ativos)
                )
        print("SERVIDORES ATIVOS COM AFASTAMENTOS")
        for item in situacao_ativo_com_afastamento:
            print(item)
        print("SERVIDORES MOVED_AWAYS SEM AFASTAMENTOS")
        for item in situacao_afastado_sem_afastamento:
            print(item)
            if item[0].is_ativo():
                posse = item[0].posses_ativas.latest("data_exercicio")
                print(posse)
                if item[0].posses_ativas.count() > 1:
                    try:
                        posse = (
                            item[0]
                            .posses_ativas.filter(Q(quadro__cargo__tipo_lei_cargo="EF"))
                            .latest("data_exercicio")
                        )
                    except Exception:
                        posse = (
                            item[0]
                            .posses_ativas.filter(
                                Q(quadro__cargo__tipo_lei_cargo__in=("CM", "AC"))
                            )
                            .latest("data_exercicio")
                        )
                try:
                    posse.save()
                except Exception:
                    pass
            print("-------------------------------------")

    @unittest.skip("verifica_situacao_funcional_incorreta")
    def test__update_functional_status_possession_fired(self):
        fired = MovimentacaoDesligamento.objects.latest("pk")
        SituacaoFuncional._update_functional_status_possession_fired(
            fired.movimentacao_posse,
            fired.movimentacao_posse.data_exercicio,
            created=False,
        )
        SituacaoFuncional._update_functional_status_possession_fired(
            fired.movimentacao_posse,
            fired.movimentacao_posse.data_exercicio,
            created=True,
        )

    @profile("situacaoFuncionaltestcase.prof")
    def test(self):
        from string import Template

        def test_departured(cache):
            return (
                cache.startswith("ATIVO_LIC")
                or cache.startswith("ATIVO_AFA")
                or cache.startswith("ATIVO_AUS")
                or cache.startswith("ATIVO_FERIAS")
                or cache.startswith("ATIVO_RECESSO")
                or cache.startswith("ATIVO_FOLGA")
                or cache.startswith("ATIVO_USU")
                or cache.startswith("ATIVO_PLANTAO")
                or cache.startswith("ATIVO_DISPONIBILIDADE")
                or cache.startswith("ATIVO_ATUACAO_GRUPO_TRAB")
                or cache.startswith("ATIVO_DESEMPENHO_FUNCAO")
            )

        # SituacaoFuncional._manager_situations()

        # print(employee)
        # print('situacao_funcional_cache', situacao_funcional_cache)
        # print('new', new)
        # text = '%s|%s|%s|%s|%s|%s\n' % (employee.tipo, employee.matricula, employee.pessoa_fisica, employee.ativo, situacao_funcional_cache, new)
        # cls.write_file(text, 'situacaofuncional.csv', mode='a')
        # print('-----------------------------')

        if True:
            # SituacaoFuncional.write_file('', 'sit.csv')
            count = 0
            # for employee in Servidor.objects.filter(tipo__in=['S', 'M']):
            for employee in Servidor.objects.filter():
                fired = False
                if (
                    employee.tipo not in ["T", "V", "E"]
                    and not employee.posses_ativas.exists()
                ) or (
                    employee.tipo in ["T", "V", "E"]
                    and not employee.get_declarationactivity().exists()
                ):
                    fired = True
                departured = False
                departures = employee.departures()
                if departures.exists():
                    departured = True
                sit_fired = 1
                if fired:
                    if not employee.situacao_funcional_cache.startswith("INATIVO"):
                        sit_fired = 2
                sit_departured = 1
                if departured:
                    if not test_departured(employee.situacao_funcional_cache):
                        sit_departured = 2
                template = Template(
                    """$employee: $status -> $kind\n SITUACAO: $situation\n DESLIGADO: $fired\n AFASTADO: $departured\n-------------------------"""
                )
                buff = template.substitute(
                    employee=employee,
                    status=employee.ativo,
                    kind=employee.get_tipo_display(),
                    situation=employee.situacao_funcional_cache,
                    fired=fired,
                    departured=departured,
                )
                # changed = False
                if sit_fired == 2 and not employee.situacao_funcional_cache.startswith(
                    "NOT_FOUND"
                ):
                    # print(employee.tipo not in ['T', 'V', 'E'] and not employee.posses_ativas.exists())
                    # print(employee.tipo in ['T', 'V', 'E'] and not employee.get_declarationactivity().exists())
                    # print(employee.posses_ativas)
                    # print(employee.get_declarationactivity())
                    # changed = True
                    count += 1
                    print("sit_fired: %s" % sit_fired)
                    to_persist = None
                    if employee.posses.exists():
                        # print(employee.posses_ativas)
                        # print(employee.posses.latest('data_exercicio'))
                        possession = employee.posses.latest("data_desligamento")
                        if hasattr(possession, "desligamento"):
                            to_persist = possession.desligamento
                    elif employee.get_declarationactivity().exists():
                        to_persist = employee.get_declarationactivity().last()
                    # show_situation_employee(employee)
                    # #RODAR SAVE SÓ PARA RESOLVER OS PENDENTES
                    try:
                        if to_persist:
                            to_persist.save()
                    except Exception as err:
                        print(err)
                    SituacaoFuncional._manager_situations(employee)
                    print(buff)
                if sit_departured == 2:
                    # changed = True
                    count += 1
                    print("sit_departured: %s" % sit_departured)
                    print(departures.last().instancia_modelo)
                    # RODAR SAVE SÓ PARA RESOLVER OS PENDENTES
                    try:
                        departures.last().instancia_modelo.save()
                    except Exception as err:
                        print(err)
                    # show_situation_employee(employee)
                    SituacaoFuncional._manager_situations(employee)
                    print(buff)
                # if not changed:
                #     changed = True
                #     count += 1
                #     SituacaoFuncional._manager_situations(employee)
                # print(buff)

                # if changed:
                #     print('##############################################################')
            print(count)
        # show_situation_employee_all()


class MovimentacaoSubstituicaoTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoSubstituicao

    def setUp(self):
        try:
            data_inicio = datetime.now()
            data_fim = data_inicio + relativedelta(days=16)
            self.posse = MovimentacaoPosse.objects.filter(
                quadro__cargo__substituivel=True, ativo=True
            ).latest("data_exercicio")
            servidor_substituido = self.posse.servidor
            afastamento = afastamento_models.FeriasAfastamento(
                servidor=servidor_substituido,
                data_inicio=data_inicio,
                data_prevista=data_fim,
                data_fim=data_fim,
            )
            self.substituicao = self.classe(
                afastamento=afastamento,
                servidor=Servidor.objects.filter(ativo=True).latest("pk"),
                servidor_substituido=servidor_substituido,
                data_inicio=data_inicio,
                data_fim=data_fim,
                publicacao_movimentacao=mock(
                    model=Publicacao, query=(~Q(data_vigencia=None))
                ),
            )
        except Exception as err:
            print(err)
            mensagem = "setUp de MovimentacaoSubstituicaoTestCase falhou!"
            log.info(mensagem)
            raise Exception(mensagem)

    def test_validate_replaceable(self):
        Cargo.objects.filter(pk=self.posse.quadro.cargo.pk).update(substituivel=False)
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            self.substituicao.validate_replaceable,
        )
        Cargo.objects.filter(pk=self.posse.quadro.cargo.pk).update(substituivel=True)

        data_exercicio_original = self.posse.data_exercicio
        MovimentacaoPosse.objects.filter(pk=self.posse.pk).update(
            data_exercicio=(self.substituicao.data_inicio + relativedelta(days=30))
        )
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            self.substituicao.validate_replaceable,
        )
        MovimentacaoPosse.objects.filter(pk=self.posse.pk).update(
            data_exercicio=data_exercicio_original
        )

        desligamento = MovimentacaoDesligamento(
            movimentacao_posse=self.posse,
            tipo_desligamento=4,
            publicacao_movimentacao=mock(
                model=Publicacao, query=(~Q(data_vigencia=None))
            ),
            data_desligamento=(
                self.substituicao.data_fim - relativedelta(days=1)
            ).date(),
        )
        desligamento.save()

        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            self.substituicao.validate_replaceable,
        )

        desligamento.delete()

    def test_atualizar_responsavel(self):
        pass

    def test_validate_intervalo_pertence_afastamento(self):
        pass
        # TODO: MODIFICAR PARA UTILIZAR AS INFORMAÇÕES DO SETUP
        # instancia = self.classe.objects.filter(afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_vigente())
        # if instancia.exists():
        #     instancia = instancia.latest('pk')
        #     instancia_novo = self.classe(
        #         servidor=instancia.afastamento.servidor,
        #         afastamento=instancia.afastamento,
        #         servidor_substituido=instancia.afastamento.servidor,
        #         publicacao_movimentacao=instancia.publicacao_movimentacao,
        #         data_inicio=instancia.data_inicio - relativedelta(days=3),
        #         posse=instancia.posse
        #     )
        #     self.assertRaises(self.classe.MovimentacaoSubstituicaoExceptionBase, instancia_novo.validate_intervalo_pertence_afastamento)

    # @unittest.skip("skipping test_validate_publicacao")
    def test_validate_publicacao(self):
        instancia = self.classe.objects.filter(
            ~Q(publicacao_movimentacao__data_vigencia=None)
        ).latest("pk")
        publicacao = instancia.publicacao_movimentacao
        data_vigencia = publicacao.data_vigencia
        Publicacao.objects.filter(pk=publicacao.pk).update(data_vigencia=None)
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            self.classe.objects.get(pk=instancia.pk).validate_publicacao,
        )
        Publicacao.objects.filter(pk=publicacao.pk).update(data_vigencia=data_vigencia)

    @unittest.skip("skipping test_validate_data_fim_publicacao_fim")
    def test_validate_data_fim_publicacao_fim(self):
        """
        DEPRECATED
        """
        hoje = datetime.now()
        instancia = self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_iniciado()
        )[0]
        instancia.data_fim = hoje
        instancia.publicacao_fim = None
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            instancia.validate_data_fim_publicacao_fim,
        )

    # @unittest.skip("skipping test_validate_substituicao_iniciada")
    def test_validate_substituicao_iniciada(self):
        hoje = datetime.now().date()
        instancia = self.classe.objects.filter(
            Q(data_inicio__lte=hoje) & Q(data_fim__gte=hoje)
        ).latest("pk")
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            instancia.validate_substituicao_iniciada,
        )

    # @unittest.skip("skipping test_validate_substituicao_finalizada")
    def test_validate_substituicao_finalizada(self):
        hoje = datetime.now().date()
        instancia = self.classe.objects.filter(data_fim__lt=hoje).latest("pk")
        self.assertRaises(
            self.classe.FinalizedErr, instancia.validate_substituicao_finalizada
        )

    def test_update_from_departure(self):
        print("test_update_from_departure")
        substituicao = (
            self.classe.objects.filter().exclude(afastamento=None).latest("pk")
        )
        # data_fim = substituicao.data_fim
        # self.classe.objects.filter(pk=substituicao).update(
        #     data_fim=substituicao.afastamento.data_fim + relativedelta(days=1))
        MovimentacaoSubstituicao.update_from_departure(substituicao.afastamento)

    def test_save(self):
        for movimentacao in self.classe.objects.filter():
            try:
                movimentacao.validate_cargo_arquimedes_ativo()
                movimentacao.save()
                break
            except Exception:
                pass


def write_table_employee_workplace(buf="", rewrite=False):
    if rewrite:
        if not buf:
            buf = "{"
            template = Template(
                """
        "$registry": {
            $employee_workplaces
        }"""
            )
            template_employee_workplaces = Template(
                """"$pk": {
                "pk": "$pk",
                "unicode": "$unicode",
                "workplace_pk": "$workplace_pk",
                "workplace_unicode": "$workplace_unicode",
                "date_start": "$date_start",
                "date_end": "$date_end"
            }"""
            )
            for employee in Servidor.objects.filter(
                ativo=True,
                tipo__in=["S", "M"],
            ).order_by("matricula"):
                if len(buf) > 1:
                    buf += ","
                buf_template_employee_workplaces = ""
                for employee_workplace in ServidorLotacao.objects.filter(
                    servidor=employee,
                    # ativo=True
                ):
                    if len(buf_template_employee_workplaces) > 1:
                        buf_template_employee_workplaces += ","
                    buf_template_employee_workplaces += template_employee_workplaces.substitute(
                        pk=employee_workplace.pk,
                        unicode=employee_workplace,
                        workplace_pk=employee_workplace.lotacao.pk,
                        workplace_unicode=employee_workplace.lotacao,
                        # date_start=DateUtils.date_to_str(employee_workplace.data_vigencia_inicio),
                        # date_end=DateUtils.date_to_str(employee_workplace.data_vigencia_fim) if employee_workplace.data_vigencia_fim else '',
                        date_start=employee_workplace.data_vigencia_inicio,
                        date_end=employee_workplace.data_vigencia_fim,
                    )
                buf += template.substitute(
                    registry=employee.matricula,
                    employee_workplaces=buf_template_employee_workplaces,
                )
            buf += "\n}"
        table_employee_workplace = (
            "%s/table_employee_workplace.json" % settings.CACHE_PATH
        )
        with open(table_employee_workplace, "w") as out:
            out.write(buf)


def read_table_employee_workplace():
    table_employee_workplace = "%s/table_employee_workplace.json" % settings.CACHE_PATH
    with open(table_employee_workplace, "r") as out:
        return json.load(out)


def diff_table_employee_workplace(buf=""):
    buf_created = ""
    buf_deleted = ""
    table_employee_workplace = read_table_employee_workplace()
    for employee in Servidor.objects.filter(ativo=True, tipo__in=["S", "M"]).order_by(
        "pessoa_fisica__nome"
    ):
        employee_workplaces = ServidorLotacao.objects.filter(servidor=employee)
        try:
            pks = []
            # print(employee_workplaces.values('lotacao'))
            for empl in list(table_employee_workplace[employee.matricula].values()):
                pks.append(empl.get("pk"))
                # print(empl.get('workplace_pk'))
                # print(empl.get('workplace_unicode'))
                if (
                    not employee_workplaces.filter(pk=int(empl.get("pk"))).exists()
                    and not employee_workplaces.filter(
                        lotacao__pk=int(empl.get("workplace_pk"))
                    ).exists()
                ):
                    buf_deleted += "\n%s | %s" % (employee, empl.get("unicode"))
            empl_diff = employee_workplaces.filter().exclude(pk__in=pks)
            for empl in empl_diff:
                buf_created += "\n%s | %s" % (empl.servidor, empl)
        except Exception as err:
            print("errr")
            print(err)

    if buf_created or buf_deleted:
        if buf_created:
            print("\nLotações e Exercícios criados:")
            print(buf_created)
        if buf_deleted:
            print("\nLotações e Exercícios apagados:")
            print(buf_deleted)


ServidorLotacao.validate_employee_departure = lambda x: True


class MovimentacaoSubstituicaoMembroTestCase(AthenasTestCase):

    avoid = False
    classe = MovimentacaoSubstituicaoMembro

    @unittest.skip("skipping test_save")
    def test_save(self):
        for movimentacao in self.classe.objects.filter():
            try:
                movimentacao.validate_cargo_arquimedes_ativo()
                movimentacao.save()
                break
            except Exception:
                pass

    @unittest.skip("skipping test_change_workplace_to_work_assignment")
    def test_change_workplace_to_work_assignment(self):
        from judicial.management.commands.load_infra_conf import Manager

        write_table_employee_workplace(rewrite=True)

        manager = Manager(verbose=True)

        manager.load_initial_replacements_from_file_gen()
        manager._loaddata(fixtures=manager.fixtures)
        manager._loaddata(fixtures=manager.fixtures_dev)
        manager._loaddata_rh()

        # manager.load_workplace_responsible_from_file_gen()

        manager.set_workplace_configurations()

        EmployeeWorkplaceTestCase.create_work_assignment(
            employee_type=["M", "S"], delete_workplace_transformed_work_assignment=False
        )

        #############################################
        print(
            """
Atualizando lotações de cargos efetivos:
- atribuindo responsabilidade;
- atribuindo data de fim quando houver desligamento do cargo que é dono do local;
- excluindo lotações e designações duplicadas do cargo que é dono do local;
- criando lotações do cargo que é dono do local;
..."""
        )
        possessions = MovimentacaoPosse.objects.filter(
            ativo=True, servidor__tipo="M", quadro__cargo__tipo_lei_cargo="EF"
        )
        for possession in possessions.order_by("servidor", "data_exercicio"):
            # print('-------------------------------------------------------------')
            # print(possession)
            employee_workplaces = ServidorLotacao.objects.filter(
                servidor=possession.servidor,
                designacao=False,
                lotacao__cargo_responsavel=possession.quadro.cargo,
            )
            # CASO EXISTA LOTAÇÃO PARA O CARGO
            if employee_workplaces.exists():
                # print('# CASO EXISTA LOTAÇÃO PARA O CARGO')
                employee_workplace = employee_workplaces.latest("data_vigencia_inicio")
                # TRANSFORMA O EXERCÍCIO E A LOTAÇÃO EM TITULAR/AFASTÁVEL
                # print('# TRANSFORMA O EXERCÍCIO E A LOTAÇÃO EM TITULAR/AFASTÁVEL')
                ServidorLotacao.objects.filter(pk=employee_workplace.pk).update(
                    responsible=True
                )
                ServidorLotacao.objects.filter(
                    child_of__pk=employee_workplace.pk
                ).update(responsible=True)
                if not ServidorLotacao.objects.filter(
                    child_of__pk=employee_workplace.pk
                ).exists():
                    try:
                        created = ServidorLotacao.objects.get(
                            pk=employee_workplace.pk
                        ).create_work_assignment()
                    except Exception as err:
                        print(
                            "-------------------------------------------------------------"
                        )
                        print(possession)
                        print(err)
                try:
                    # print('# FINALIZA A LOTAÇÃO CASO A POSSSE NÃO TENHA MAIS EFEITO')
                    # FINALIZA A LOTAÇÃO CASO A POSSSE NÃO TENHA MAIS EFEITO
                    employee_workplace = ServidorLotacao.objects.get(
                        pk=employee_workplace.pk
                    )
                    employee_workplace.must_validate_document = False
                    # if possession.data_desligamento:
                    #     employee_workplace.data_vigencia_fim = (possession.data_desligamento - relativedelta(days=1))
                    employee_workplace.data_vigencia_fim = (
                        (possession.data_desligamento - relativedelta(days=1))
                        if possession.data_desligamento
                        else None
                    )
                    employee_workplace.from_substitution = False
                    employee_workplace.save(propagate_resp=False)
                except Exception as err:
                    print(
                        "-------------------------------------------------------------"
                    )
                    print(possession)
                    print(err)
                # print('# EXCLUI LOTAÇÕES DUPLICADAS PARA O LOCAL EM QUESTÃO')
                # EXCLUI LOTAÇÕES DUPLICADAS PARA O LOCAL EM QUESTÃO
                # ServidorLotacao.objects.filter(
                #     servidor=possession.servidor,
                #     designacao=False,
                #     lotacao__cargo_responsavel=possession.quadro.cargo
                # ).exclude(pk=employee_workplace.pk).delete()
            else:
                # print('# CRIANDO LOTAÇÃO PARA UM CARGO EF QUE É RESPONSÁVEL POR UM LOCAL, BASEANDO-SE EM EXERCÍCIO EXISTENTE')
                # CRIANDO LOTAÇÃO PARA UM CARGO EF QUE É RESPONSÁVEL POR UM LOCAL, BASEANDO-SE EM EXERCÍCIO EXISTENTE
                employee_workplaces = ServidorLotacao.objects.filter(
                    servidor=possession.servidor,
                    designacao=True,
                    lotacao__cargo_responsavel=possession.quadro.cargo,
                )
                if employee_workplaces.exists():
                    employee_workplace = employee_workplaces.latest(
                        "data_vigencia_inicio"
                    )
                    fields_update = {
                        "designacao": False,
                        "responsible": True,
                        "child_of": None,
                    }
                    try:
                        created = employee_workplace._create_by_copy(
                            employee_workplace, fields_update
                        )
                        ServidorLotacao.objects.filter(pk=employee_workplace.pk).update(
                            child_of=created, responsible=True
                        )
                    except Exception as err:
                        print(
                            "-------------------------------------------------------------"
                        )
                        print(possession)
                        print(err)
                # print('# CRIANDO LOTAÇÃO PARA UMA POSSE DE CARGO EFETIVO QUE NÃO POSSUI LOTAÇÃO')
                # CRIANDO LOTAÇÃO PARA UMA POSSE DE CARGO EFETIVO QUE NÃO POSSUI LOTAÇÃO
                # print('# CRIANDO EXERCÍCIO PARA UMA POSSE DE CARGO EFETIVO QUE NÃO POSSUI LOTAÇÃO')
                # CRIANDO EXERCÍCIO PARA UMA POSSE DE CARGO EFETIVO QUE NÃO POSSUI LOTAÇÃO
                employee_workplaces = ServidorLotacao.objects.filter(
                    servidor=possession.servidor,
                    lotacao__cargo_responsavel=possession.quadro.cargo,
                )
                if (
                    not employee_workplaces.exists()
                    and possession.quadro.cargo.lotacao_responsavel
                ):
                    try:
                        workplace = ServidorLotacao._create(
                            must_validate_document=False,
                            responsible=True,
                            servidor=possession.servidor,
                            lotacao=possession.quadro.cargo.lotacao_responsavel,
                            publicacao=possession.publicacao_movimentacao,
                            data_vigencia_inicio=possession.data_exercicio,
                            data_vigencia_fim=possession.data_desligamento,
                            anotar=True,
                            propagate_resp=False,
                        )
                        if workplace:
                            ServidorLotacao.objects.filter(pk=workplace.pk).update(
                                responsible=True
                            )
                            workplace.create_work_assignment()
                            ServidorLotacao.objects.filter(
                                child_of__pk=workplace.pk
                            ).update(responsible=True)
                        else:
                            print(
                                "-------------------------------------------------------------"
                            )
                            print("Não criou lotação e exercício para:")
                            print(possession)
                    except Exception as err:
                        print(
                            "-------------------------------------------------------------"
                        )
                        print(possession)
                        print(err)
                elif employee_workplaces.exists():
                    for employee_workplace in employee_workplaces:
                        ServidorLotacao.objects.filter(pk=employee_workplace.pk).update(
                            responsible=True
                        )
                        ServidorLotacao.objects.filter(
                            child_of__pk=employee_workplace.pk
                        ).update(responsible=True)
            if (
                not possession.servidor.departures().exists()
                and possession.quadro.cargo.lotacao_responsavel
                and possession.quadro.cargo.lotacao_responsavel != possession.servidor
            ):
                workplace = Lotacao.objects.get(
                    pk=possession.quadro.cargo.lotacao_responsavel.pk
                )
                workplace.responsavel = possession.servidor
                workplace.save()
            # print('------------------------------------------------------------------------')
        print("Done.")

        # print('''\nCriando designações baseadas nas lotações existentes...''')
        # # CRIANDO EXERCÍCIOS BASEANDO-SE NAS LOTAÇÕES QUE NÃO SÃO DE CARGO EFETIVO
        # # APAGANDO ESTAS LOTAÇÕES QUE DEVERIAM SER EXERCÍCIO
        # for possession in possessions.order_by('servidor'):
        #     employee_workplaces = ServidorLotacao.objects.filter(
        #         servidor=possession.servidor,
        #         designacao=False,
        #         ativo=True
        #     ).exclude(
        #         lotacao__cargo_responsavel__pk__in=possession.servidor.posses.filter(quadro__cargo__tipo_lei_cargo='EF').values('quadro__cargo')
        #     )
        #     for employee_workplace in employee_workplaces:
        #         created = None
        #         try:
        #             created = employee_workplace.create_work_assignment()
        #         except Exception as err:
        #             print(unicode(err))
        #         try:
        #             if created:
        #                 ServidorLotacao.objects.filter(pk=employee_workplace.pk).delete()
        #             else:
        #                 print('Como não criou exercício não foi possível apargar:')
        #                 print(unicode(created))
        #         except Exception as err:
        #             print(unicode(err))
        # print('''Done.''')
        # ###########################################

        # manager.load_responsible_from_substitution_member(verbose=False, departure_active=True)

        # manager.load_responsible_from_inativation_member(verbose=False, departure_active=True)

        manager.set_work_assignment_to_substitution(verbose=True, departure_active=True)

        substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
            ~Q(designation_substituted__father_of=None)
        )
        # substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
        #     Q(afastamento__estado=ACTIVE) &
        #     ~Q(designation_substituted=None)
        # )
        print(
            "\nSubstituições com lotações pai de designações: %s"
            % substitutions.count()
        )
        for substitution in substitutions:
            if (
                substitution.designation_substituted
                and substitution.designation_substituted.father_of.exists()
            ):
                print(
                    substitution.servidor_substituido,
                    substitution.designation_substituted.father_of.latest(
                        "data_vigencia_inicio"
                    ),
                )
                MovimentacaoSubstituicaoMembro.objects.filter(pk=substitution).update(
                    designation_substituted=substitution.designation_substituted.father_of.latest(
                        "data_vigencia_inicio"
                    )
                )
                sub = MovimentacaoSubstituicaoMembro.objects.get(pk=substitution)
                try:
                    sub.save()
                except Exception as err:
                    print(err)
        print(
            "Substituições sem designações: %s"
            % MovimentacaoSubstituicaoMembro.objects.filter(
                afastamento__estado=ACTIVE, designation_substituted=None
            ).count()
        )

        inactivations = InativacaoCargoMembro.objects.filter(
            ~Q(designation__father_of=None)
        )
        print(
            "Inativações de com lotações pai de designações: %s" % inactivations.count()
        )
        for inactivation in inactivations:
            if inactivation.designation and inactivation.designation.father_of.exists():
                print(
                    inactivation.afastamento.servidor,
                    inactivation.designation.father_of.latest("data_vigencia_inicio"),
                )
                InativacaoCargoMembro.objects.filter(pk=inactivation.pk).update(
                    designation=inactivation.designation.father_of.latest(
                        "data_vigencia_inicio"
                    )
                )
                ina = InativacaoCargoMembro.objects.get(pk=inactivation.pk)
                try:
                    ina.save()
                except Exception as err:
                    print(err)
        print(
            "Inativações sem designações: %s"
            % InativacaoCargoMembro.objects.filter(
                afastamento__estado=ACTIVE, designation=None
            ).count()
        )

        manager.call_update_substitution_member(
            verbose=True,
            only_active_substitution=False,
            departure_situation=[
                ACTIVE,
            ],
        )

        # manager.call_update_situation_employee_workplace()

        diff_table_employee_workplace()

        print("\nExercícios pendentes...")
        substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
            afastamento__estado=ACTIVE
        )
        for substitution in substitutions.order_by(
            "servidor_substituido", "data_inicio"
        ):
            if not substitution.designation_substituted:
                print(
                    "%s\nExercício do substituido não existe.\nServidor Substituído: %s.\nServidor Substituto: %s\n--------------------------------------"
                    % (
                        substitution,
                        substitution.servidor_substituido,
                        substitution.servidor,
                    )
                )
            if (
                substitution.substituicao_finalizada() or substitution.is_active()
            ) and not substitution.designation_substitute:
                print(
                    "%s\nExercício do substituto não existe.\nServidor Substituído: %s.\nServidor Substituto: %s\n--------------------------------------"
                    % (
                        substitution,
                        substitution.servidor_substituido,
                        substitution.servidor,
                    )
                )
            if (
                substitution.substituicao_finalizada()
                and substitution.designation_substitute
                and not substitution.designation_substitute.is_finished()
            ):
                print(
                    "%s\nExercício do substituto não existe.\nServidor Substituído: %s.\nServidor Substituto: %s\n--------------------------------------"
                    % (
                        substitution,
                        substitution.servidor_substituido,
                        substitution.servidor,
                    )
                )

        print("\nTitular...")
        workplaces = Lotacao.objects.filter(responsible_substituted=None).exclude(
            executionorgan=None
        )
        print("LOCAL|RESPONSAVEL|TITULAR")
        for workplace in workplaces.order_by("nome"):
            if workplace.responsavel != workplace.owner.first():
                owner = workplace.owner.first()
                print(
                    "%s | %s | %s"
                    % (workplace, workplace.responsavel, owner if owner else "----")
                )

    @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        for instancia in self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_vigente()
        ):
            instancia_novo = self.classe(
                afastamento=instancia.afastamento,
                designation_substituted=instancia.designation_substituted,
                servidor_substituido=instancia.afastamento.servidor,
                publicacao_movimentacao=instancia.publicacao_movimentacao,
                data_inicio=instancia.data_inicio + relativedelta(days=1),
                posse=instancia.posse,
            )
            self.assertRaises(
                self.classe.MovimentacaoSubstituicaoExceptionBase,
                instancia_novo.validate_periodo,
            )

    @unittest.skip("skipping test_validate_employee_not_member")
    def test_validate_employee_not_member(self):
        afastamento = afastamento_tests.BaseLicencaAfastamento.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_vigente(),
            servidor__tipo="S",
        ).first()
        instancia_novo = self.classe(
            afastamento=afastamento,
            servidor_substituido=afastamento.servidor,
            publicacao_movimentacao=afastamento.publicacao_movimentacao,
            data_inicio=afastamento.data_inicio,
            posse=Servidor.objects.get(
                pk=afastamento.servidor.pk
            ).posses_ativas.filter()[0],
        )
        self.assertRaises(
            self.classe.MovimentacaoSubstituicaoExceptionBase,
            instancia_novo.validate_employee_not_member,
        )

    @unittest.skip("skipping test_validate_designacao")
    def test_validate_designacao(self):
        for sub in self.classe.objects.filter().order_by("servidor"):
            designacao = ServidorLotacao.objects.filter(
                lotacao__cargo_responsavel__cargo_arquimedes=sub.cargo_arquimedes
            )
            if designacao.exists():
                print(sub.cargo_arquimedes, sub.servidor, designacao.first())
                self.classe.objects.filter(pk=sub.pk).update(
                    designacao=designacao.first()
                )
                # pass
            else:
                # print sub.servidor
                pass

    @unittest.skip("skipping test_validate_substitutos")
    def test_validate_substitutos(self):
        for servidor in Servidor.objects.filter(tipo="M").exclude(ativo=False):
            print(servidor, servidor.my_replacement())

    def test_sub(self):
        for sub in MovimentacaoSubstituicaoMembro.objects.filter(pk__in=[47988]):
            try:
                sub.save()
            except Exception as err:
                print(err)


class ReplacementsMemberTestCase(unittest.TestCase):

    classe = MovimentacaoSubstituicaoMembro

    def setUp(self):
        self.servidor = []
        for servidor in Servidor.objects.filter(tipo="M", ativo=True).order_by(
            "pessoa_fisica__nome"
        ):
            if (
                servidor.my_substitute_employee().exists()
                and servidor.afastamento_ativo()
            ):
                self.servidor.append(servidor.matricula)
                # print '\n', servidor, servidor.my_replacement_substitute().count(), servidor.get_afastamentos()

        self.validate_publicacao_movimentacao_orig = (
            MovimentacaoSubstituicaoMembro.validate_publicacao
        )

        self.validate_publicacao_orig = ServidorLotacao.validate_publicacao
        self.validate_posse_orig = ServidorLotacao.validate_posse
        self.validate_lotacao_fora_organograma_orig = (
            ServidorLotacao.validate_lotacao_fora_organograma
        )
        self.validate_duplicate_workplace_orig = (
            ServidorLotacao.validate_duplicate_workplace
        )
        ServidorLotacao.validate_publicacao = validate_publicacao
        ServidorLotacao.validate_posse = validate_posse
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma
        )
        ServidorLotacao.validate_duplicate_workplace = validate_duplicate_workplace

        MovimentacaoSubstituicaoMembro.validate_publicacao = (
            validate_publicacao_movimentacao
        )

    def tearDown(self):
        ServidorLotacao.validate_publicacao = self.validate_publicacao_orig
        ServidorLotacao.validate_posse = self.validate_posse_orig
        ServidorLotacao.validate_lotacao_fora_organograma = (
            self.validate_lotacao_fora_organograma_orig
        )
        ServidorLotacao.validate_duplicate_workplace = (
            self.validate_duplicate_workplace_orig
        )

        MovimentacaoSubstituicaoMembro.validate_publicacao = (
            self.validate_publicacao_movimentacao_orig
        )

    @unittest.skip("skipping test_substitutes")
    def test_substitutes(self):
        for servidor in Servidor.objects.filter(
            # matricula=77407,
            tipo="M",
            ativo=True,
        ):
            if (
                servidor.my_replacement_substitute().exists()
                and servidor.afastamento_ativo()
            ):
                print(
                    servidor,
                    servidor.my_replacement_substitute().count(),
                    servidor.get_afastamentos(),
                )

    @unittest.skip("skipping test_cmd_replacement_manager")
    def test_cmd_replacement_manager(self):
        MovimentacaoSubstituicaoMembro.cmd_replacement_manager()

    @unittest.skip("skipping test_replacement_manager")
    def test_replacement_manager(self):
        hoje = datetime.now().date()

        afastamentos = (
            afastamento_models.BaseLicencaAfastamento.objects.filter(
                data_inicio__lte=hoje,
                data_fim__gte=hoje,
                # servidor__matricula__in=self.servidor
                # servidor__matricula__in=[17697, ]
            )
            .exclude(substituicao=None)
            .values("pk")
            .distinct()
        )
        print(afastamentos.count())
        for afastamento in afastamentos:
            print(afastamento)
            moved_away = afastamento_models.BaseLicencaAfastamento.objects.get(
                pk=afastamento.get("pk")
            ).instancia_modelo
            # , DateUtils.date_to_str(moved_away.data_inicio), DateUtils.date_to_str(moved_away.data_fim) if moved_away.data_fim else '----'
            print("\n", moved_away)
            # print('_-> _raw_locations before call replacement_manager')
            # moved_away.servidor._raw_locations()

            substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
                afastamento__pk=afastamento.get("pk")
            )
            for substitution in substitutions.order_by("data_inicio"):
                situation = "ATIVA"
                if substitution.substituicao_finalizada():
                    situation = "FINALIZADA"
                elif substitution.data_inicio > hoje:
                    situation = "AGENDADA"

                # if not substitution.substituicao_finalizada():
                print(
                    "==========>______REPLACEMENT: %s %s - %s"
                    % (situation, substitution, substitution.servidor)
                )
                try:
                    substitution.save()
                except Exception as err:
                    print(err)
            # print('_-> _raw_locations after call replacement_manager')
            # moved_away.servidor._raw_locations()
            # moved_away.servidor.work_assignment
            print("--------------------------------------------------------")

    @unittest.skip("skipping test_replacement_starting")
    def test_replacement_starting(self):
        hoje = datetime.now().date()
        # hoje = datetime(2014, 11, 17).date()
        # replacements = MovimentacaoSubstituicaoMembro.objects.filter(
        #     data_inicio__lte=hoje,
        #     data_fim__gte=hoje
        #     # data_inicio__gte=hoje
        # ).exclude(designation_substituted=None)

        # afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
        #     data_inicio__lte=hoje, data_fim__gte=hoje).exclude(
        #         substituicao=None).exclude(servidor__tipo='S').values('pk').distinct()

        afastamentos = (
            afastamento_models.BaseLicencaAfastamento.objects.filter(
                data_inicio__lte=hoje,
                data_fim__gte=hoje,
                # servidor__matricula__in=self.servidor
                servidor__matricula__in=[
                    99310,
                ],
            )
            .exclude(substituicao=None)
            .values("pk")
            .distinct()
        )
        for afastamento in afastamentos[0:1]:
            moved_away = afastamento_models.BaseLicencaAfastamento.objects.get(
                pk=afastamento.get("pk")
            ).instancia_modelo
            # , DateUtils.date_to_str(moved_away.data_inicio), DateUtils.date_to_str(moved_away.data_fim) if moved_away.data_fim else '----'
            print("\n", moved_away)
            print("_-> _raw_locations before call replacement_manager")
            moved_away.servidor._raw_locations()

            substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
                afastamento__pk=afastamento.get("pk")
            )
            for substitution in substitutions.order_by("-data_inicio"):
                # situation = 'ATIVA'
                # if substitution.substituicao_finalizada():
                #     situation = 'FINALIZADA'
                # elif substitution.data_inicio > hoje:
                #     situation = 'AGENDADA'

                # if not substitution.substituicao_finalizada():
                #   print('______REPLACEMENT: %s %s' % (situation, substitution))

                MovimentacaoSubstituicaoMembro.replacement_manager(
                    replacement=[
                        substitution,
                    ]
                )
            print("_-> _raw_locations after call replacement_manager")
            moved_away.servidor._raw_locations()
            # moved_away.servidor.work_assignment
            print("--------------------------------------------------------")
        # for substituicao in replacements.order_by('data_inicio')[0:2]:
        #     MovimentacaoSubstituicaoMembro.replacement_manager(replacement=[substituicao, ])
        #     print '--------------------------------------------------------'
        # for substituicao in replacements.order_by('data_inicio')[0:2]:
        #     MovimentacaoSubstituicaoMembro.replacement_manager(replacement=[substituicao, ])
        #     print '--------------------------------------------------------'

        # from engine.notification.models import Notification
        # from django.contrib.contenttypes.models import ContentType
        # for n in Notification.objects.filter(
        #     target_id=Servidor.objects.get(pessoa_fisica__nome__icontains='vicente oli').pk,
        #         target_ct=ContentType.objects.get(name='servidor')).order_by('-created_at')[0:10]:
        #     print n.created_at, n.formatMsg()

        # for n in Notification.objects.filter().order_by('-created_at')[0:20]:
        #     print n.created_at, n.formatMsg()

        # hoje = datetime.now().date()
        # for substituicao in MovimentacaoSubstituicaoMembro.objects.filter(
        #         # data_inicio=hoje):
        #         # data_inicio__gte=hoje
        #         ).order_by('data_inicio').exclude(designation_substituted=None):
        #     print 'SUBSTITUICAO:', substituicao.servidor_substituido, substituicao
        #     print substituicao.designation_substituted
        #     self.create_designcao_from_substituicao(substituicao)
        #     print '--------------------------------------------------------'

        # substituicoes = MovimentacaoSubstituicaoMembro.objects.filter(
        #     ).order_by('data_inicio').exclude(designation_substituted=None)
        # print 'TOTAL COM DESIGNACAO SUBSTITUIDO:', substituicoes.count()
        # print 'TOTAL COM DESIGNACAO SUBSTITUIDO E DESIGNACAO DE SUBSTITUTO:', substituicoes.exclude(designacao=None).count()

    @unittest.skip("skipping test_replacement_starting")
    def test_replacement_starting(self):
        b = afastamento_tests.BaseLicencaAfastamento.objects.filter(pk=24618)[0]
        b = b.instancia_modelo
        b.alteracao = INTERRUPCAO
        b.data_fim = datetime(2016, 3, 24).date()
        b.save()

        # hoje = datetime.now().date()
        # moved_aways = afastamento_models.BaseLicencaAfastamento.objects.filter(pk__in=[
        #     24618,
        #     # 23607
        # ])
        # for moved_away in moved_aways:
        #     moved_away = moved_away.instancia_modelo
        #     print '\n', moved_away#, DateUtils.date_to_str(moved_away.data_inicio), DateUtils.date_to_str(moved_away.data_fim) if moved_away.data_fim else '----'

        #     substitutions = MovimentacaoSubstituicaoMembro.objects.filter(afastamento=moved_away)
        #     for substitution in substitutions.order_by('data_inicio'):
        #         situation = 'ATIVA'
        #         if substitution.substituicao_finalizada():
        #             situation = 'FINALIZADA'
        #         elif substitution.data_inicio > hoje:
        #             situation = 'AGENDADA'

        #         # if not substitution.substituicao_finalizada():
        #         print('______REPLACEMENT: %s %s' % (situation, substitution))
        #         print(substitution.designation_substituted.pk, substitution.designation_substituted, substitution.designation_substituted.membersubstitution_substituted.exists())
        #         # substitution.save()
        #         print('--------------------------------------------------------')

        #         # MovimentacaoSubstituicaoMembro.replacement_manager(replacement=[substitution, ])
        #     # print('--------------work_assignment')
        #     # for wa in moved_away.servidor.work_assignment:
        #     #     print(wa)
        #     moved_away.save()

    def create_designcao_from_substituicao(self, substituicao):
        servidor_lotacao = ServidorLotacao._create(
            designacao=True,
            servidor=substituicao.servidor,
            lotacao=substituicao.designation_substituted.lotacao,
            publicacao=(
                substituicao.publicacao_movimentacao
                if substituicao.publicacao_movimentacao
                else mock(model=Publicacao, query=(~Q(data_vigencia=None)))
            ),
            data_vigencia_inicio=substituicao.data_inicio,
            data_vigencia_fim=substituicao.data_fim,
            movimentacao_posse=(
                substituicao.servidor.posses_ativas.filter(
                    quadro__cargo__tipo_lei_cargo="EF"
                ).latest("data_exercicio")
                if substituicao.servidor.posses_ativas.filter(
                    quadro__cargo__tipo_lei_cargo="EF"
                ).exists()
                else None
            ),
        )

        if servidor_lotacao:
            if substituicao.data_fim != servidor_lotacao.data_vigencia_fim:
                print("DATAS DIFERENTES!!!!")
                servidor_lotacao.data_vigencia_fim = substituicao.data_fim
                servidor_lotacao.from_substitution = False
                servidor_lotacao.save()
                ServidorLotacao.objects.filter(pk=servidor_lotacao.pk).update(
                    from_substitution=True
                )

            self.update_substituicao_designacao_substituto(
                substituicao, servidor_lotacao
            )
            # TODO: analisar onde INSERIR uma transação para todo o bloco de implementações

    def update_substituicao_designacao_substituto(self, substituicao, servidor_lotacao):
        """
        This method update MovimentacaoSubstituicaoMembro.designacao placing the new ServidorLotacao
            of the servidor replacement.
        """
        try:
            sub = MovimentacaoSubstituicaoMembro.objects.get(pk=substituicao.pk)
            sub.designacao = servidor_lotacao
            sub.save()
        except Exception as err:
            print(err)

    @unittest.skip("skipping test_change_data_fim_substituicao")
    def test_change_data_fim_substituicao(self):
        hoje = datetime.now().date()
        substituicoes = (
            MovimentacaoSubstituicaoMembro.objects.filter(
                # pk=21511
                data_inicio__gte=hoje
            )
            .order_by("data_inicio")
            .exclude(designation_substituted=None)
            .exclude(designacao=None)
        )
        for substituicao in substituicoes[0:1]:
            print(
                "SUBSTITUICAO:",
                substituicao.pk,
                substituicao.servidor_substituido,
                substituicao,
            )
            data_fim = substituicao.afastamento.data_fim - relativedelta(days=1)
            print("FIM", substituicao.data_fim, "NOVO FIM", data_fim)
            substituicao.data_fim = data_fim
            substituicao.save()
            # TODO: GATILHO após save chamando
            self.create_designcao_from_substituicao(substituicao)
            # self.replacement_ending(substituicoes)


class InativacaoCargoMembroTestCase(AthenasTestCase):

    avoid = False
    classe = InativacaoCargoMembro

    def test_save(self):
        if self.classe.objects.exists():
            self.classe.objects.latest("pk").save()

    # @unittest.skip("skipping test_validate_intervalo_pertence_afastamento")
    def test_validate_intervalo_pertence_afastamento(self):
        instancia = self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_vigente()
        )
        if instancia.exists():
            instancia = instancia.latest("pk")
            instancia_novo = self.classe(
                afastamento=instancia.afastamento,
                cargo_arquimedes=instancia.cargo_arquimedes,
                publicacao_inativacao=instancia.publicacao_inativacao,
                data_inicio=instancia.data_inicio - relativedelta(days=3),
            )
            self.assertRaises(
                self.classe.InativacaoExceptionBase,
                instancia_novo.validate_intervalo_pertence_afastamento,
            )

    # @unittest.skip("skipping test_validate_publicacao")
    def test_validate_publicacao(self):
        instancia = self.classe.objects.filter()
        if instancia.exists():
            instancia = instancia.latest("pk")
            instancia.publicacao_inativacao = None
            self.assertRaises(
                self.classe.InativacaoExceptionBase, instancia.validate_publicacao
            )
            instancia = self.classe.objects.filter()[0]
            instancia.publicacao_inativacao.data_vigencia = None
            self.assertRaises(
                self.classe.InativacaoExceptionBase, instancia.validate_publicacao
            )

    # @unittest.skip("skipping test_validate_periodo")
    def test_validate_periodo(self):
        instancia = self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_vigente()
        )
        if instancia.exists():
            instancia = instancia.latest("pk")
            instancia_novo = self.classe(
                afastamento=instancia.afastamento,
                cargo_arquimedes=instancia.cargo_arquimedes,
                data_inicio=instancia.data_inicio,
                publicacao_inativacao=instancia.publicacao_inativacao,
            )
            self.assertRaises(
                self.classe.InativacaoExceptionBase, instancia_novo.validate_periodo
            )

    # @unittest.skip("skipping test_validate_inativacao_iniciada")
    def test_validate_inativacao_iniciada(self):
        instancia = self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_iniciado()
        )
        if instancia.exists():
            instancia = instancia.latest("pk")
            self.assertRaises(
                self.classe.InativacaoExceptionBase,
                instancia.validate_inativacao_iniciada,
            )

    # @unittest.skip("skipping test_validate_inativacao_finalizada")
    def test_validate_inativacao_finalizada(self):
        instancia = self.classe.objects.filter(
            afastamento_tests.BaseLicencaAfastamentoTestCase.filtro_finalizado()
        )
        if instancia.exists():
            instancia = instancia.latest("pk")
            self.assertRaises(
                self.classe.InativacaoExceptionBase,
                instancia.validate_inativacao_finalizada,
            )

    # @unittest.skip("skipping test_validate_employee_not_member")
    def test_validate_cargo(self):
        for sub in self.classe.objects.filter():
            posse = MovimentacaoPosse.objects.filter(
                quadro__cargo__cargo_arquimedes=sub.cargo_arquimedes
            ).latest("data_exercicio")
            print(sub.cargo_arquimedes, posse, sub.posse)
            self.classe.objects.filter(pk=sub.pk).update(posse=posse)


class CargaHorariaTestCase(AthenasTestCase):

    avoid = False
    classe = CargaHoraria

    def test_save(self):
        if self.classe.objects.exists():
            self.classe.objects.filter().latest("pk").save()

    def test_cmd_update_workload(self):
        carga_horaria = CargaHoraria.objects.filter().latest("pk").pk
        CargaHoraria.cmd_update_workload([carga_horaria])

    def test_criar_carga_horaria(self):
        posse = (
            MovimentacaoPosse.objects.filter()
            .exclude(data_exercicio=None)
            .latest("data_exercicio")
        )
        carga_horaria = CargaHoraria.criar_carga_horaria(
            servidor=posse.servidor,
            publicacao=None,
            data_inicio=posse.data_exercicio,
            data_fim=None,
            quantidade=posse.quadro.carga_horaria,
            tipo=posse.quadro.tipo_carga_horaria,
        )
        if (
            carga_horaria is None
            and CargaHoraria.objects.filter(
                servidor=posse.servidor,
                data_inicio=posse.data_exercicio,
                quantidade=posse.quadro.carga_horaria,
                tipo=posse.quadro.tipo_carga_horaria,
            ).exists()
        ):
            carga_horaria = CargaHoraria.objects.filter(
                servidor=posse.servidor,
                data_inicio=posse.data_exercicio,
                quantidade=posse.quadro.carga_horaria,
                tipo=posse.quadro.tipo_carga_horaria,
            ).latest("pk")
            assert carga_horaria.servidor == posse.servidor
            assert carga_horaria.data_inicio == posse.data_exercicio
            assert carga_horaria.quantidade == posse.quadro.carga_horaria
            assert carga_horaria.tipo == posse.quadro.tipo_carga_horaria

    def test_create_workload_by_possession(self):
        posse = MovimentacaoPosse.objects.filter(servidor__matricula=91108).latest(
            "data_exercicio"
        )
        CargaHoraria.create_workload_by_possession(posse.servidor)

        posse = MovimentacaoPosse.objects.filter(servidor__matricula=94109).latest(
            "data_exercicio"
        )
        CargaHoraria.create_workload_by_possession(posse.servidor)

    def test_verifica_carga_horaria_mesma_quantidade(self):
        posse = MovimentacaoPosse.objects.filter(servidor__matricula=91108).latest(
            "data_exercicio"
        )
        cargas = CargaHoraria.objects.filter(servidor=posse.servidor)
        if cargas.exists() is False:
            assert (
                CargaHoraria.verifica_carga_horaria_mesma_quantidade(
                    servidor=posse.servidor, quantidade=posse.quadro.carga_horaria
                )
                is False
            )
        if cargas.exists() is True:
            assert (
                CargaHoraria.verifica_carga_horaria_mesma_quantidade(
                    servidor=posse.servidor, quantidade=cargas.latest("pk").quantidade
                )
                is True
            )

    def test_carga_horaria_anterior(self):
        from decimal import Decimal

        carga_horaria, created = CargaHoraria.objects.get_or_create(
            servidor__matricula=91108, quantidade=Decimal(30)
        )
        assert not carga_horaria.carga_horaria_anterior() is None

    def test_apagar_carga_horaria(self):
        carga_horaria = CargaHoraria.objects.filter(faltas=None).latest("pk")
        pk = carga_horaria.pk
        self.classe.apagar_carga_horaria(
            carga_horaria.servidor, carga_horaria.data_inicio
        )
        assert self.classe.objects.filter(pk=pk).exists() is False

    @unittest.skip("skipping test_atualiza_carga_horaria")
    def test_atualiza_carga_horaria(self):
        # DEPRECATED
        pass
        # posse = MovimentacaoPosse.objects.filter(~Q(data_desligamento=None)).latest('data_exercicio')
        # carga_horaria = self.classe.objects.filter(servidor=posse.servidor).latest('pk')
        # self.classe.objects.filter(pk=carga_horaria.pk).update(data_fim=None)
        # self.classe.atualiza_carga_horaria(posse)
        # print self.classe.objects.filter(pk=carga_horaria.pk)
        # print self.classe.objects.filter(pk=carga_horaria.pk).latest('pk').data_fim
        # assert not self.classe.objects.filter(pk=carga_horaria.pk).latest('pk').data_fim is None

    def test_atualiza_data_fim_carga_horaria_anterior(self):
        pass
        # for servidor in CargaHoraria.objects.filter().latest('pk')

        # carga_horaria_anterior = carga_horaria.carga_horaria_anterior()

        # if not carga_horaria_anterior is None:
        #     if criar is True:
        #         carga_horaria_anterior.data_fim = (self.data_inicio - relativedelta(days=1))
        #     else:
        #         carga_horaria_anterior.data_fim = None if self.servidor.ativo else carga_horaria_anterior.data_fim

        # carga_horaria.atualiza_data_fim_carga_horaria_anterior()
        # if CargaHoraria.objects.get(pk=carga_horaria_anterior.pk).data_fim is None:
        #     raise Exception('Data de fim incorreta!')
        carga_horaria = None
        carga_horaria_anterior = None
        for servidor in Servidor.objects.filter(ativo=True):
            carga_horaria = CargaHoraria.objects.filter().latest("pk")
            carga_horaria_anterior = carga_horaria.carga_horaria_anterior()
            if carga_horaria_anterior is not None:
                break
        if carga_horaria and carga_horaria_anterior:
            CargaHoraria.objects.filter(pk=carga_horaria_anterior.pk).update(
                data_fim=None
            )
            carga_horaria.atualiza_data_fim_carga_horaria_anterior(
                criar=(False if carga_horaria.data_fim is not None else True)
            )
            assert (
                not CargaHoraria.objects.filter(pk=carga_horaria_anterior.pk)
                .latest("pk")
                .data_fim
                is None
            )

            carga_horaria = CargaHoraria.objects.filter().latest("pk")
            carga_horaria_anterior = carga_horaria.carga_horaria_anterior()
            carga_horaria.atualiza_data_fim_carga_horaria_anterior(criar=False)
            assert (
                CargaHoraria.objects.filter(pk=carga_horaria_anterior.pk)
                .latest("pk")
                .data_fim
                is None
            )

            carga_horaria.atualiza_data_fim_carga_horaria_anterior(
                criar=(False if carga_horaria.data_fim is not None else True)
            )


class MigrationEmployeeWorkplace(unittest.TestCase):

    def test(self):
        print(
            "\nQuantidade de Lotações que terão Lotações de Servidores migradas: %s"
            % Lotacao.objects.exclude(old=None).count()
        )
        publication = Publicacao.objects.get(pk=19817)
        print(
            "\nPublicação %s vigente a partir do dia %s"
            % (publication, DateUtils.date_to_str(publication.data_vigencia))
        )
        print("\n")
        for workplace in Lotacao.objects.exclude(old=None):
            print(
                "%s> %s"
                % (("%s %s" % (workplace.old, "=" * 100))[0:100], "%s" % workplace)
            )
        print("\nIniciando o processo...")
        count_old = count_new = 0
        for workplace in Lotacao.objects.exclude(old=None):
            print(
                "-----------------------------------------------------------------------------"
            )
            print(
                "%s> %s"
                % (("%s %s" % (workplace.old, "=" * 100))[0:100], "%s" % workplace)
            )
            Task.start(
                create_new_employeeworkplace,
                new=workplace.pk,
                old=workplace.old.pk,
                old_reference=workplace.old.pk if workplace.old else None,
                publication=publication.pk,
                user=get_current_user().pk,
            )
            olds = ServidorLotacao.objects.filter(lotacao=workplace.old, ativo=True)
            news = ServidorLotacao.objects.filter(lotacao=workplace)
            print("\n Total de lotações de servidores antigas: %s" % olds.count())
            for old in olds:
                print(
                    "%s - %s à %s - %s"
                    % (
                        old,
                        DateUtils.date_to_str(old.data_vigencia_inicio),
                        (
                            DateUtils.date_to_str(old.data_vigencia_fim)
                            if old.data_vigencia_fim
                            else "----"
                        ),
                        old.servidor,
                    )
                )
                count_old += 1
            print("\n Total de lotações de servidores novas: %s" % news.count())
            for new in news:
                print(
                    "%s - %s à %s - %s"
                    % (
                        new,
                        DateUtils.date_to_str(new.data_vigencia_inicio),
                        (
                            DateUtils.date_to_str(new.data_vigencia_fim)
                            if new.data_vigencia_fim
                            else "----"
                        ),
                        new.servidor,
                    )
                )
                count_new += 1

        employee_workplaces = ServidorLotacao.objects.filter(publicacao=publication)
        print(
            "\n Novas lotações para a publicação %s: %s"
            % (publication, employee_workplaces.count())
        )
        for employee_workplace in employee_workplaces.order_by("lotacao__nome"):
            print(
                "%s - %s à %s - %s"
                % (
                    employee_workplace,
                    DateUtils.date_to_str(employee_workplace.data_vigencia_inicio),
                    (
                        DateUtils.date_to_str(employee_workplace.data_vigencia_fim)
                        if employee_workplace.data_vigencia_fim
                        else "----"
                    ),
                    employee_workplace.servidor,
                )
            )

        print("\nOld: %s\nNew:%s \n%s" % (count_old, count_new, count_old - count_new))


class EmployeeWorkplaceReportTestCase(unittest.TestCase):

    @unittest.skip("skipping test_new_17062016")
    def test_new_17062016(self):
        print("\n")
        print("SERVDIOR|LOTACAO|INICIO|FIM|PROVISORIO|INICIO|FIM|EXERCICIO|INICIO|FIM|")
        for employee in Servidor.objects.filter(
            pk__in=ServidorLotacao.objects.filter(
                data_vigencia_inicio=datetime(2016, 6, 17)
            ).values("servidor"),
            tipo="S",
            # ativo=True
        ):
            # print sl.pk, '|', sl, '|', sl.servidor, '|', sl.data_vigencia_inicio, '|', sl.data_vigencia_fim
            # print employee
            employee_workplaces = ServidorLotacao.objects.filter(
                data_vigencia_inicio=datetime(2016, 6, 17), servidor=employee
            )
            # print employee_workplaces.count()
            employee_workplace_provisional = None
            employee_workplace = (
                employee_workplaces.filter(designacao=False).first()
                if employee_workplaces.filter(designacao=False).exists()
                else None
            )
            employee_workassignment = (
                employee_workplaces.filter(designacao=True).first()
                if employee_workplaces.filter(designacao=True).exists()
                else None
            )

            if not employee_workplace:
                employee_workplace = ServidorLotacao.objects.filter(
                    Q(servidor=employee)
                    & Q(designacao=False)
                    & (
                        Q(data_vigencia_fim__gte=datetime(2016, 6, 17))
                        | Q(data_vigencia_fim=None)
                    )
                )
                if employee_workplace.exists():
                    employee_workplace = employee_workplace.latest(
                        "data_vigencia_inicio"
                    )

            if not employee_workassignment:
                employee_workassignment = ServidorLotacao.objects.filter(
                    Q(servidor=employee)
                    & Q(designacao=True)
                    & (
                        Q(data_vigencia_fim__gte=datetime(2016, 6, 17))
                        | Q(data_vigencia_fim=None)
                    )
                )
                if employee_workassignment.count() > 1:
                    print("EEEEEEEEEEEIIIIIIIIIIIIIIIIIIIIIII mais de um exercício!!!!")
                if employee_workassignment.exists():
                    employee_workassignment = employee_workassignment.latest(
                        "data_vigencia_inicio"
                    )

            if employee_workplace and employee_workplace.provisorio:
                employee_workplace_provisional = employee_workplace
                employee_workplace = ServidorLotacao.objects.filter(
                    servidor=employee, designacao=False, provisorio=False
                )
                if employee_workplace.exists():
                    employee_workplace = employee_workplace.latest(
                        "data_vigencia_inicio"
                    )

            if not employee_workplace_provisional:
                employee_workplace_provisional = ServidorLotacao.objects.filter(
                    Q(servidor=employee)
                    & Q(designacao=False)
                    & Q(provisorio=True)
                    & (
                        Q(data_vigencia_fim__gte=datetime(2016, 6, 17))
                        | Q(data_vigencia_fim=None)
                    )
                )
                if employee_workplace_provisional.exists():
                    employee_workplace_provisional = (
                        employee_workplace_provisional.latest("data_vigencia_inicio")
                    )

            print(
                "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|"
                % (
                    employee,
                    employee_workplace.lotacao if employee_workplace else "",
                    (
                        DateUtils.date_to_str(employee_workplace.data_vigencia_inicio)
                        if employee_workplace
                        else ""
                    ),
                    (
                        DateUtils.date_to_str(employee_workplace.data_vigencia_fim)
                        if employee_workplace and employee_workplace.data_vigencia_fim
                        else ""
                    ),
                    (
                        employee_workplace_provisional.lotacao
                        if employee_workplace_provisional
                        else ""
                    ),
                    (
                        DateUtils.date_to_str(
                            employee_workplace_provisional.data_vigencia_inicio
                        )
                        if employee_workplace_provisional
                        else ""
                    ),
                    (
                        DateUtils.date_to_str(
                            employee_workplace_provisional.data_vigencia_fim
                        )
                        if employee_workplace_provisional
                        and employee_workplace_provisional.data_vigencia_fim
                        else ""
                    ),
                    employee_workassignment.lotacao if employee_workassignment else "",
                    (
                        DateUtils.date_to_str(
                            employee_workassignment.data_vigencia_inicio
                        )
                        if employee_workassignment
                        else ""
                    ),
                    (
                        DateUtils.date_to_str(employee_workassignment.data_vigencia_fim)
                        if employee_workassignment
                        and employee_workassignment.data_vigencia_fim
                        else ""
                    ),
                )
            )

    def test(self):
        print("\n")
        ServidorLotacao.validate_posse = lambda x: True
        employee_workplaces = ServidorLotacao.objects.filter(
            # data_vigencia_inicio=datetime(2016, 6, 17),
            ativo=True,
            servidor__tipo="S",
            designacao=False,
        )
        # print employee_workplaces.count()
        # print('SERVDIOR|LOTACAO|INICIO|FIM|PROVISORIO|INICIO|FIM|EXERCICIO|INICIO|FIM|')
        # for employee_workplace in employee_workplaces:
        #     # if employee_workplace:
        #     #     print employee_workplace.anotacao_geral_lotacao.texto
        #     try:
        #         employee_workplace.save()
        #     except Exception as err:
        #         print employee_workplace.pk, '|', employee_workplace, '|', employee_workplace.servidor, '|', DateUtils.date_to_str(employee_workplace.data_vigencia_inicio), '|', DateUtils.date_to_str(employee_workplace.data_vigencia_fim) if employee_workplace.data_vigencia_fim else '------------------'
        #         print(err)
        print(employee_workplaces.count())
        buff = "MATRICULA|SERVDIOR|LOTACAO|RESPONSAVEL|CHEFE_IMEDIATO|NOVO_CHEFE_IMEDIATO|INICIO|FIM|PROVISORIO|INICIO|FIM|EXERCICIO|INICIO|FIM|"
        for employee_workplace in employee_workplaces.order_by("lotacao", "servidor"):
            new_boss_immediate = employee_workplace.servidor._get_chefe_imediato()
            workplace_responsible = employee_workplace.lotacao.responsavel
            employee_chief_immediate = employee_workplace.servidor.chefe_imediato
            buff += ("\n%s|%s|%s|%s|%s|%s|%s|%s|") % (
                employee_workplace.servidor.matricula,
                employee_workplace.servidor.pessoa_fisica,
                employee_workplace.lotacao,
                workplace_responsible if workplace_responsible else "",
                employee_chief_immediate if employee_chief_immediate else "",
                new_boss_immediate if new_boss_immediate else "",
                DateUtils.date_to_str(employee_workplace.data_vigencia_inicio),
                (
                    DateUtils.date_to_str(employee_workplace.data_vigencia_fim)
                    if employee_workplace.data_vigencia_fim
                    else ""
                ),
            )
        print(buff)
        print(settings.CACHE_PATH)
        with open("%s/workplace.csv" % (settings.CACHE_PATH), "w") as out:
            out.write(buff)
            # if employee_workplace:
            #     print employee_workplace.anotacao_geral_lotacao.texto
            # try:
            #     employee_workplace.save()
            # except Exception as err:
            #     print employee_workplace.pk, '|', employee_workplace, '|', employee_workplace.servidor, '|', DateUtils.date_to_str(employee_workplace.data_vigencia_inicio), '|', DateUtils.date_to_str(employee_workplace.data_vigencia_fim) if employee_workplace.data_vigencia_fim else '------------------'
            #     print(err)


class MigrationTestCase(unittest.TestCase):

    def test_employees(self):
        pass


class MemberWorkLocationsTestCase(unittest.TestCase):

    def test_members(self):
        print("")
        registry = [
            3190,  # DESEMPENHO DE FUNÇÃO
            11092,
            52104,
            13293,
            53504,
            17697,
            108810,
            124714,
            126814,
            51204,  # FÉRIAS
            130615,  # FÉRIAS
        ]
        for employee in Servidor.objects.filter(ativo=True):
            if employee.departures().exists():
                registry.append(employee.matricula)
        for employee in Servidor.objects.filter(
            tipo="M", ativo=True, matricula__in=registry
        ):
            # if not MovimentacaoPosse.objects.filter(quadro__cargo__nome__icontains='substituto', servidor=s, ativo=True).exists():
            print(employee, "==========", "AFASTADO PARA:", employee.departures())
            print("->work_assignment", employee.work_assignment)
            print(
                "->work_assignment_effective_exercise",
                employee.work_assignment_effective_exercise,
            )
            print(
                "->work_assignment responsible",
                employee.work_assignment.filter(responsible=True),
            )
            print(
                "->work_assignment owner", employee.work_assignment.filter(owner=True)
            )
            print("->work_locations", employee.work_locations)
            print(
                "->owner_locations",
                employee.owner_locations.first()
                or (
                    "SUBSTITUTO"
                    if MovimentacaoPosse.objects.filter(
                        quadro__cargo__nome__icontains="substituto",
                        servidor=employee,
                        ativo=True,
                    ).exists()
                    else None
                ),
            )
            print(
                "->owner_locations_can_substitute",
                employee.owner_locations_can_substitute.first(),
            )
            print("->workplace", employee.workplace.first())
            print(
                "->workplace_by_date %s" % DateUtils.date_to_str(datetime.now().date()),
                employee.workplace_by_date(),
            )
            print(
                "->workplace_by_date %s"
                % DateUtils.date_to_str(datetime(2015, 9, 1).date()),
                employee.workplace_by_date(date=datetime(2015, 9, 1).date()),
            )
            print(
                "->workplace_by_date %s"
                % DateUtils.date_to_str(datetime(2014, 9, 1).date()),
                employee.workplace_by_date(date=datetime(2014, 9, 1).date()),
            )
            print(
                "->workplace_by_date %s"
                % DateUtils.date_to_str(datetime(2013, 9, 1).date()),
                employee.workplace_by_date(date=datetime(2013, 9, 1).date()),
            )
            print(
                "->workplace_by_date %s"
                % DateUtils.date_to_str(datetime(2012, 9, 1).date()),
                employee.workplace_by_date(date=datetime(2012, 9, 1).date()),
            )
            print(
                "->workplace_by_date %s"
                % DateUtils.date_to_str(datetime(2011, 9, 1).date()),
                employee.workplace_by_date(date=datetime(2011, 9, 1).date()),
            )
            print("->workplace_current", employee.workplace_current)
            print("------------------------------------")

    def test(self):
        pass
        # ServidorLotacao.cmd_atualizar_ativo()
        # afastamento_models.BaseLicencaAfastamento.objects.get(pk=35336).instancia_modelo.save()
        # employee = Servidor.objects.get(matricula=14593)
        # print(employee)
        # print(employee.workplace_by_date(date=datetime(2016, 9, 20)))

        # afastamento_models.BaseLicencaAfastamento.objects.get(pk=36207).instancia_modelo.save()

        # for empl in ServidorLotacao.objects.filter():
        #     if (empl.membersubstitution_substituted.exists() or empl.membersubstitution_substitute.exists() or empl.changed_by_departure):
        #         empl.set_from_substitution()

        # for base in BaseLicencaAfastamento.objects.filter(
        #     Q(servidor__tipo='M') &
        #     Q(data_fim__gte=datetime(2016, 8, 1)) &
        #     Q(data_fim__lte=datetime(2016, 9, 2))
        # ).order_by('servidor'):
        #     work_count_before = base.servidor.work_assignment.filter(owner=True).count()
        #     work_before = base.servidor.work_assignment.filter(owner=True)
        #     try:
        #         ServidorLotacao._work_assignment_return_from_departured(base.instancia_modelo)
        #     except Exception as err:
        #         print(unicode(err))
        #     work_count_after = base.servidor.work_assignment.filter(owner=True).count()
        #     work_after = base.servidor.work_assignment.filter(owner=True)

        #     if work_count_before != work_count_after:
        #         print '------------------------------------'
        #         print base.instancia_modelo, DateUtils.date_to_str(base.data_inicio), DateUtils.date_to_str(base.data_fim)
        #         print('work_count_before %s' % work_count_before)
        #         print('work_before %s' % work_before)
        #         print('work_count_after %s' % work_count_after)
        #         print('work_after %s' % work_after)


class UpdateSubstitutionTestCase(unittest.TestCase):

    @unittest.skip("skipping")
    def test(self):
        substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
            Q(data_inicio__gte=datetime(2016, 8, 22))
            | Q(data_fim__gte=datetime(2016, 9, 1))
            | Q(data_fim=None)
        )
        print(substitutions.count())
        for substitution in substitutions:
            if not substitution.designation_substituted:
                print("---------------------------")
                print(substitution.servidor_substituido)
                print(substitution.afastamento.pk, substitution.afastamento)
                print(
                    "Designação de servidor substituído não encontrado %s"
                    % substitution.servidor_substituido
                )
                try:
                    substitution.afastamento.instancia_modelo.save()
                except Exception as err:
                    print(err)
                try:
                    substitution.save()
                except Exception as err:
                    print(err)
            if (
                substitution.substituicao_finalizada() or substitution.is_active()
            ) and not substitution.designation_substitute:
                print("---------------------------")
                print(substitution.servidor_substituido)
                print(substitution.afastamento.pk, substitution.afastamento)
                print(
                    "Designação de servidor substituto não encontrado %s"
                    % substitution.servidor
                )
                try:
                    substitution.afastamento.instancia_modelo.save()
                except Exception as err:
                    print(err)
                try:
                    substitution.save()
                except Exception as err:
                    print(err)
            if (
                substitution.substituicao_finalizada()
                and substitution.designation_substitute
                and not substitution.designation_substitute.is_finished()
            ):
                print("---------------------------")
                print(substitution.servidor_substituido)
                print(substitution.afastamento.pk, substitution.afastamento)
                print(
                    "Designação de servidor substituto não finalizada %s"
                    % substitution.designation_substitute
                )
                try:
                    substitution.afastamento.instancia_modelo.save()
                except Exception as err:
                    print(err)
                try:
                    substitution.save()
                except Exception as err:
                    print(err)

    # def test(self):
    #     substitutions = MovimentacaoSubstituicaoMembro.objects.filter(
    #         Q(data_fim__gte=datetime.now().date())
    #     )
    #     print(substitutions.count())
    #     for substitution in substitutions:
    #         try:
    #             substitution.save()
    #         except Exception as err:
    #             print(err)


class EmployeeWorkplaceByDateTestCase(unittest.TestCase):

    @unittest.skip("skipping")
    def test(self):
        employees = Servidor.objects.filter(ativo=True, tipo="S")
        print(employees.count())
        for employee in employees:
            if employee.workplace_by_date():
                print(employee, employee.workplace_by_date())

    def test_members(self):
        from django.db import connection

        print("")
        registry = [
            3190,  # DESEMPENHO DE FUNÇÃO
            11092,
            52104,
            13293,
            53504,
            17697,
            108810,
            124714,
            126814,
            51204,  # FÉRIAS
            130615,  # FÉRIAS
            130415,  # FÉRIAS
        ]
        for employee in Servidor.objects.filter(
            tipo="M", ativo=True, matricula__in=registry
        ):
            # if not MovimentacaoPosse.objects.filter(quadro__cargo__nome__icontains='substituto', servidor=s, ativo=True).exists():
            print(employee, "==========", "AFASTADO PARA:", employee.departures())
            # print '->work_assignment', employee.work_assignment
            # print '->work_assignment_effective_exercise', employee.work_assignment_effective_exercise
            # print '->work_assignment responsible', employee.work_assignment.filter(responsible=True)
            # print '->work_assignment owner', employee.work_assignment.filter(owner=True)
            # print '->work_locations', employee.work_locations
            # print '->owner_locations', employee.owner_locations.first() or ('SUBSTITUTO' if MovimentacaoPosse.objects.filter(quadro__cargo__nome__icontains='substituto', servidor=employee, ativo=True).exists() else None)
            # print '->owner_locations_can_substitute', employee.owner_locations_can_substitute.first()
            # print '->workplace', employee.workplace.first()
            print(
                "->workplace_by_date %s" % DateUtils.date_to_str(datetime.now().date()),
                employee.workplace_by_date(),
            )
            print(connection.queries[len(connection.queries) - 2])
            print(connection.queries[len(connection.queries) - 3])
            print(connection.queries[len(connection.queries) - 4])
            # print '->workplace_by_date %s' % DateUtils.date_to_str(datetime(2015, 9, 1).date()), employee.workplace_by_date(date=datetime(2015, 9, 1).date())
            # print '->workplace_by_date %s' % DateUtils.date_to_str(datetime(2014, 9, 1).date()), employee.workplace_by_date(date=datetime(2014, 9, 1).date())
            # print '->workplace_by_date %s' % DateUtils.date_to_str(datetime(2013, 9, 1).date()), employee.workplace_by_date(date=datetime(2013, 9, 1).date())
            # print '->workplace_by_date %s' % DateUtils.date_to_str(datetime(2012, 9, 1).date()), employee.workplace_by_date(date=datetime(2012, 9, 1).date())
            # print '->workplace_by_date %s' % DateUtils.date_to_str(datetime(2011, 9, 1).date()), employee.workplace_by_date(date=datetime(2011, 9, 1).date())
            # print '->workplace_current', employee.workplace_current
            print("------------------------------------")


class GenerateDifferenceMigrationEsocialTestCase(unittest.TestCase):

    def test(self):
        import io

        persons = PessoaFisica.objects.filter(servidor__ativo=True)
        print("")
        print("Grau instrução")
        buf = "TIPO|MATRICULA|SERVIDOR|CARGO|GRAU INSTRUÇÃO|INFORMAÇÃO\n"
        for person in persons.filter(grau_instrucao__in=[3, 12, 13, 14]):
            employee = person.servidor_set.last()
            job_position = (
                employee.posses_ativas.last().quadro
                if employee.posses_ativas.last()
                else ""
            )
            buf += "%s|%s|%s|%s|%s|%s\n" % (
                employee.get_tipo_display(),
                employee.matricula,
                employee.pessoa_fisica,
                job_position,
                GRAU_INSTRUCAO_CHOICES.get(person.grau_instrucao),
                person.get_grau_instrucao_display(),
            )
        print(buf)
        file_to = "%s/grau_instrucao_pendencia_esocial.csv" % settings.CACHE_PATH
        with io.open(file_to, "w") as out:
            out.write(buf)

        buf = "TIPO|MATRICULA|SERVIDOR|CARGO|ESTADO CIVIL|INFORMAÇÃO\n"
        print("Estado civil")
        for person in persons.filter(estado_civil__in=[7]):
            employee = person.servidor_set.last()
            job_position = (
                employee.posses_ativas.last().quadro
                if employee.posses_ativas.last()
                else ""
            )
            buf += "%s|%s|%s|%s|%s|%s\n" % (
                employee.get_tipo_display(),
                employee.matricula,
                employee.pessoa_fisica,
                job_position,
                dict(ESTADO_CIVIL_CHOICES).get(person.estado_civil),
                person.get_estado_civil_display(),
            )
        print(buf)
        file_to = "%s/estado_civil_pendencia_esocial.csv" % settings.CACHE_PATH
        with io.open(file_to, "w") as out:
            out.write(buf)

        buf = "TIPO|MATRICULA|SERVIDOR|CARGO|TIPO LOGRADOURO|INFORMAÇÃO\n"
        print("Endereco")
        for address in Endereco.objects.filter(
            person__pessoafisica__servidor__ativo=True, tipo_logradouro__in=[4, 7]
        ):
            employee = address.person.pessoafisica.servidor_set.last()
            job_position = (
                employee.posses_ativas.last().quadro
                if employee.posses_ativas.last()
                else ""
            )
            buf += "%s|%s|%s|%s|%s|%s\n" % (
                employee.get_tipo_display(),
                employee.matricula,
                employee.pessoa_fisica,
                job_position,
                dict(TIPO_LOGRADOURO_ENDERECO_CHOICES).get(address.tipo_logradouro),
                address.get_tipo_logradouro_display(),
            )
        print(buf)
        file_to = (
            "%s/endereco_tipo_logradouro_pendencia_esocial.csv" % settings.CACHE_PATH
        )
        with io.open(file_to, "w") as out:
            out.write(buf)

        buf = ""
        print("Movimentacao Desligamento - Remover as opções do cadastro")
        print("Novas Validações")
        for person in persons.filter():
            errors = []
            employee = person.servidor_set.last()
            job_position = (
                employee.posses_ativas.last().quadro
                if employee.posses_ativas.last()
                else ""
            )
            try:
                person.validate_mandatory_sex()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_race()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_degree_education()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_date_born()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_municipality_naturalness()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_cpf()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_nis_pisep()
            except Exception as err:
                errors.append(err)
            for doc in person.documento.filter():
                try:
                    doc.validate_mandatory_nis()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_ctps()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_ric()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_rne()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_professional_council()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_cnh()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_voter()
                except Exception as err:
                    errors.append(err)
            if errors:
                buf_person = "%s|%s|%s|%s" % (
                    employee.get_tipo_display(),
                    employee.matricula,
                    employee.pessoa_fisica,
                    job_position,
                )
                for err in errors:
                    buf_person += "|%s" % err
                print(buf_person)
                buf_person += "\n"
                buf += buf_person
        file_to = (
            "%s/novas_validacoes_pendencias_esocial_COM_CNH.csv" % settings.CACHE_PATH
        )
        with io.open(file_to, "w") as out:
            out.write(buf)

        buf = ""
        print("CNH Pendentes...")
        for person in persons.filter():
            errors = []
            employee = person.servidor_set.last()
            if not employee.posses_ativas.filter(
                quadro__cargo__codigo__in=["OFD", "OFJ", "MOP", "MOT"]
            ).exists():
                job_position = (
                    employee.posses_ativas.last().quadro
                    if employee.posses_ativas.last()
                    else ""
                )
                for doc in person.documento.filter():
                    try:
                        doc.validate_mandatory_cnh()
                    except Exception as err:
                        doc.delete()
                        errors.append(err)
                if errors:
                    buf_person = "%s|%s|%s|%s" % (
                        employee.get_tipo_display(),
                        employee.matricula,
                        employee.pessoa_fisica,
                        job_position,
                    )
                    for err in errors:
                        buf_person += "|%s" % err
                    print(buf_person)
                    buf_person += "\n"
                    buf += buf_person
        file_to = "%s/cnh_removido.csv" % settings.CACHE_PATH
        with io.open(file_to, "w") as out:
            out.write(buf)

        buf = ""
        print("Novas Validações")
        for person in persons.filter():
            errors = []
            employee = person.servidor_set.last()
            job_position = (
                employee.posses_ativas.last().quadro
                if employee.posses_ativas.last()
                else ""
            )
            try:
                person.validate_mandatory_sex()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_race()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_degree_education()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_date_born()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_municipality_naturalness()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_cpf()
            except Exception as err:
                errors.append(err)
            try:
                person.validate_mandatory_nis_pisep()
            except Exception as err:
                errors.append(err)
            for doc in person.documento.filter():
                try:
                    doc.validate_mandatory_nis()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_ctps()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_ric()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_rne()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_professional_council()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_cnh()
                except Exception as err:
                    errors.append(err)
                try:
                    doc.validate_mandatory_voter()
                except Exception as err:
                    errors.append(err)
            if errors:
                buf_person = "%s|%s|%s|%s" % (
                    employee.get_tipo_display(),
                    employee.matricula,
                    employee.pessoa_fisica,
                    job_position,
                )
                for err in errors:
                    buf_person += "|%s" % err
                print(buf_person)
                buf_person += "\n"
                buf += buf_person
        file_to = (
            "%s/novas_validacoes_pendencias_esocial_CNH_REMOVIDA.csv"
            % settings.CACHE_PATH
        )
        with io.open(file_to, "w") as out:
            out.write(buf)


class DocumentSpecializedTestCase(unittest.TestCase):

    def test(self):
        d = DocumentSpecialized.objects.filter(tipo_documento=TITULO_ELEITOR).last()
        d.clean_fields()
        d.clean()


class MigrationEmployeeWorkAssignmentTestCase(unittest.TestCase):

    def run_migration(self, workplace, workplace_exclude, employees):
        print("----------------------------------------------------")
        date_start = datetime.now().date()
        created = []
        for workpl in Lotacao.objects.filter(ativo=True, pai=workplace).exclude(
            pk__in=workplace_exclude
        ):
            print("Criando exercício para Lotação: %s - %s" % (workpl, workpl.pk))
            for employee in employees:
                work_assignment = employee.work_assignment.last()
                # print(employee, work_assignment)
                fields_update = {
                    "lotacao": workpl,
                    "publicacao": None,
                    "data_vigencia": None,
                    "data_vigencia_inicio": date_start,
                    "data_vigencia_fim": None,
                    "full_exercise": False,
                    "designacao": True,
                    "changed_by_departure": None,
                    "created_by_departure": None,
                    "owner": False,
                    "commission": False,
                }

                # print fields_update
                try:
                    created.append(
                        ServidorLotacao._create_by_copy(work_assignment, fields_update)
                    )
                except Exception as err:
                    print(err)

        for creat in created:
            print(creat.pk, creat, creat.servidor, creat)

    def test(self):
        workplace_araguaina = Lotacao.objects.get(pk=142)
        workplaces_araguaina_exclude = [538, 266, 368]
        employee_araguaina = [
            139916,
            # 106510,
            83308,
            66707,
            # 114812,
            121913,
            114912,
            # 116212,
            89708,
            71607,
            80707,
            69107,
        ]
        print(len(employee_araguaina))
        employees = Servidor.objects.filter(matricula__in=employee_araguaina)
        print(employees.count())
        self.run_migration(workplace_araguaina, workplaces_araguaina_exclude, employees)

        workplace_gurupi = Lotacao.objects.get(pk=596)
        workplaces_gurupi_exclude = []
        employee_gurupi = [
            30201,
            133216,
            127414,
            124314,
            122913,
            138116,
        ]
        print(len(employee_gurupi))
        employees = Servidor.objects.filter(matricula__in=employee_gurupi)
        print(employees.count())
        self.run_migration(workplace_gurupi, workplaces_gurupi_exclude, employees)


def check_work_assignment(employee):
    if employee.tipo == "M":
        workplace_only_active = employee.workplace_only_active.filter(owner=True)
        if not workplace_only_active.exists():
            workplace_only_active = employee.workplace_only_active
    else:
        workplace_only_active = employee.workplace_only_active
    workplace_only = None
    work_assignment = None
    print("Lotações: %s" % workplace_only_active.count())
    if workplace_only_active.exists():
        workplace_only = workplace_only_active.last()
        work_assignments = employee.work_assignment_effective_exercise.filter(
            lotacao=workplace_only.lotacao
        )
        print("Exercícios da lotação: %s" % work_assignments.count())
        if work_assignments.exists():
            work_assignment = work_assignments.last()
    # for workplace_only in workplace_only_active:
    #     print('Exercícios da lotação: %s' % workplace_only_active.count())
    #     work_assignments = employee.work_assignment_effective_exercise.filter(lotacao=workplace_only.lotacao)
    #     for work_assignment in work_assignments:
    #         print(work_assignment)
    return workplace_only, work_assignment


class WorkplaceMainTestCase(unittest.TestCase):

    def test(self):
        # print('================> NÃO POSSUI EFETIVO EXERCÍCIO <================')
        # for employee in Servidor.objects.filter(ativo=True, tipo__in=['S', 'M']):
        #     if not employee.work_assignment_effective_exercise.exists():
        #         print employee.get_tipo_display(), '|', employee
        #         print 'get_workplace_only:', employee.get_workplace_only(date)
        #         print 'workplace_by_date:', employee.workplace_by_date()
        #         print '======================================'

        self.set_main()
        self.show_main()

    def set_main(self):
        date = datetime.now().date()
        print("================> NÃO POSSUI EFETIVO EXERCÍCIO <================")
        # count = 0
        done = []
        for employee in Servidor.objects.filter(
            ativo=True,
            tipo__in=[
                "S",
                # 'M'
            ],
        ):
            # if not employee.work_assignment_effective_exercise.exists():
            print(employee.get_tipo_display(), "|", employee)
            print("get_workplace_only:", employee.get_workplace_only(date))
            print("workplace_by_date:", employee.workplace_by_date())
            print(
                "work_locations_effective_exercise:",
                employee.work_locations_effective_exercise,
            )
            workplace_only, work_assignment = check_work_assignment(employee)
            if work_assignment and not work_assignment.main:
                work_assignment.action_set_main(True)
                for wa in work_assignment.work_assignment_child:
                    wa.action_set_main(True)
                done.append({employee, work_assignment})
            print("======================================")
        print(len(done))

    def show_main(self):
        diff = []
        buf = "matricula|servidor|lotacao original|lotacao novo\n"
        for employee in Servidor.objects.filter(
            ativo=True,
            tipo__in=[
                "S",
                # 'M'
            ],
        ):
            print(employee)
            # print 'get_workplace_only:', employee.get_workplace_only().filter(main=True)
            # print 'work_assignment_effective_exercise:', employee.work_assignment_effective_exercise.filter(main=True)
            print(
                "workplace_by_date original:", employee.workplace_by_date_refactored()
            )
            print("workplace_by_date:", employee.workplace_by_date())
            print("======================================")
            buf += "%s|%s|%s|%s\n" % (
                employee.matricula,
                employee,
                employee.workplace_by_date_refactored(),
                employee.workplace_by_date(),
            )
            if employee.workplace_by_date_refactored() != employee.workplace_by_date():
                diff.append(
                    {
                        employee.matricula: {
                            employee.workplace_by_date_refactored(),
                            employee.workplace_by_date(),
                        }
                    }
                )

        table_employee_workplace = "%s/employee_workplace.csv" % settings.CACHE_PATH
        with codecs.open(table_employee_workplace, "wa", "utf-8") as out:
            out.write(buf)

        print(len(diff))
        for df in diff:
            print(
                Servidor.objects.get(matricula=list(df.keys()[0])),
                df.get(list(df.keys())[0]),
            )


class PossessionTestCase(unittest.TestCase):

    def test(self):
        for possession in MovimentacaoPosse.objects.filter(ativo=True).order_by(
            "servidor", "data_exercicio"
        ):
            try:
                possession.anota = False
                possession.save()
            except Exception as err:
                print(possession, "====", DateUtils.date_to_str(possession.data_posse))
                print("""               ERRO EM                 %s""" % possession)
                print(err)


class RelationshipTestCase(unittest.TestCase):

    def setUp(self):
        relationship = Relationship(
            giver=Servidor.objects.get(matricula=989),
            receiver=Servidor.objects.get(matricula=119213),
            workplace=Lotacao.objects.get(pk=457),
            date_start=datetime.now().date(),
        )
        relationship.save()

        relationship = Relationship(
            giver=Servidor.objects.get(matricula=22999),
            receiver=Servidor.objects.get(matricula=46403),
            workplace=Lotacao.objects.get(pk=44145),
            date_start=datetime.now().date(),
        )
        relationship.save()

    def tearDown(self):
        # Relationship.objects.filter().delete()
        pass

    def test(self):
        for relationship in Relationship.objects.filter()[0:5]:
            print("RELATIONSHIP")
            print(relationship)
            giver = relationship.giver
            receiver = relationship.receiver
            print("GIVER")
            print(giver)
            print(giver.giver)
            print("RECEIVER")
            print(receiver)
            print(receiver.receiver)


class OwnerOfJobPositionTestCase(unittest.TestCase):

    def test(self):
        for employee in Servidor.objects.filter(
            tipo="M",
            ativo=True,
        ):
            if (
                not employee.member_substitute
                and afastamento_models.BaseLicencaAfastamento.objects.filter(
                    servidor=employee, estado=ACTIVE
                )
                .filter(
                    Q(desempenhofuncao__isnull=False) | Q(desempenhofuncao__isnull=True)
                )
                .exists()
            ):
                exists = False
                work_locations_effective_exercise = (
                    employee.work_locations_effective_exercise
                )
                for work_assignment in (
                    employee.work_assignment_effective_exercise.filter(owner=True)
                    .filter(lotacao__in=work_locations_effective_exercise.values("pk"))
                    .values("lotacao", "lotacao__nome")
                ):
                    possessions = MovimentacaoPosse.objects.filter(
                        servidor=employee,
                        quadro__cargo__tipo_lei_cargo="EF",
                        quadro__cargo__lotacao_responsavel__pk=work_assignment.get(
                            "lotacao"
                        ),
                        ativo=True,
                    )
                    exists = possessions.exists()
                    if exists:
                        break
                if not exists:
                    # print(employee)
                    # print(afastamento_models.BaseLicencaAfastamento.objects.filter(servidor=employee, estado=ACTIVE).filter(Q(desempenhofuncao__isnull=False) | Q(desempenhofuncao__isnull=True)))
                    # print('-----------------')

                    print(
                        "MEMBRO: %s"
                        % afastamento_models.BaseLicencaAfastamento.objects.filter(
                            servidor=employee, estado=ACTIVE
                        )
                        .filter(
                            Q(desempenhofuncao__isnull=False)
                            | Q(desempenhofuncao__isnull=True)
                        )
                        .last()
                    )
                    possessions = employee.posses_ativas
                    if possessions.exists():
                        print("PROVIMENTOS:")
                    for possession in possessions:
                        print(possession.quadro.cargo)
                    if employee.work_assignment.exists():
                        print("EXERCICIOS:")
                    for w in employee.work_assignment:
                        print(w)
                    print("-----------------")


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    import sys

    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


class QueryTestCase(unittest.TestCase):

    def test(self):
        revision = "000000"
        message = """Para realizar a migração de 0055 a 0056 é necessário colocar o código na revisão %s.
        Confirme[y] caso tenha certeza que a revisão é %s""" % (
            revision,
            revision,
        )
        print(query_yes_no(message, default="no"))


class EmployeeWorkassignmentInvalidtCase(unittest.TestCase):

    def test(self):
        employee_workassignment = ServidorLotacao.objects.filter(
            servidor__tipo="M", designacao=True
        )
        for empl in employee_workassignment.order_by("-data_vigencia_inicio"):
            if empl.data_vigencia_inicio == empl.data_vigencia_fim:
                departures = empl.servidor.departures(
                    start_date=empl.data_vigencia_inicio
                )
                if departures.exists():
                    departure = departures.last()
                    print(
                        empl.pk,
                        " - CREATED:",
                        (
                            empl.created_by_departure.pk
                            if empl.created_by_departure
                            else "NOT FOUND"
                        ),
                        " - CHANGED:",
                        (
                            empl.changed_by_departure.pk
                            if empl.changed_by_departure
                            else "NOT FOUND"
                        ),
                        " - DEPARTURE:",
                        departure.pk if departure else "NOT FOUND",
                    )


class ProgressionTestCase(unittest.TestCase):

    def test(self):
        # from rh.apd.models import *
        # count = 0
        # for per in PeriodicEvaluationPerformance.objects.filter().order_by('employee__servidor__pessoa_fisica__nome'):
        #     data_prevista = per.start_date + relativedelta(
        #             months=per.configuration.interval_periodic_evaluation,
        #             days=(per.days_suspended - 1)
        #         )
        #     if per.end_date != data_prevista:
        #         count += 1
        #         print ":".join([unicode(d) for d in [per.pk, per.get_status_display(), DateUtils.date_to_str(per.start_date), DateUtils.date_to_str(per.end_date), DateUtils.date_to_str(data_prevista), per.emplo
        # yee.servidor]])
        #         if per.status == '1':
        #             print per
        #             #PeriodicEvaluationPerformance.objects.filter(pk=per.pk).update(end_date=data_prevista)
        #         print('--------------------------')
        # print count
        from rh.gfp.models import MovimentacaoProgressao

        for mp in MovimentacaoProgressao.objects.filter().exclude(dias_suspenso=0)[
            0:10
        ]:
            print(mp.servidor, mp.dias_suspenso)
            # for per in PeriodicEvaluationPerformance.objects.filter():
            #     print per


class ReplacementTestCase(unittest.TestCase):

    # def test(self):
    #     print('employee.where_replacement_substitute()')
    #     # print employee.where_replacement_substitute()
    #     # for replacement in employee.where_replacement_substitute():
    #     #     print(replacement)

    @unittest.skip("skipping test_where_substitute_employee_workplace")
    def test_where_substitute_employee_workplace(self):
        employee = Servidor.objects.get(matricula=13293)
        print("employee.where_substitute_employee_workplace()")
        # print employee.where_substitute_employee_workplace()
        for employee_workplace in employee.where_substitute_employee_workplace():
            print(employee_workplace, employee_workplace.servidor)

    @unittest.skip("skipping test_where_substitute_employee")
    def test_where_substitute_employee(self):
        employee = Servidor.objects.get(matricula=13293)
        print("employee.where_substitute_employee()")
        # print employee.where_substitute_employee()
        for replacement in employee.where_substitute_employee():
            print(replacement)

    @unittest.skip("skipping test_where_substitute_workplace")
    def test_where_substitute_workplace(self):
        employee = Servidor.objects.get(matricula=13293)
        print("employee.where_substitute_workplace()")
        # print employee.where_substitute_workplace()
        for replacement in employee.where_substitute_workplace()[0]:
            print("MEMBRO: %s - CARGO: %s" % (employee, replacement.get("cargo_nome")))
            subs = replacement.get("substitutos")
            if len(subs) > 0:
                print("SUBSTITUTOS:")
                for sub in subs:
                    print(sub.get("cargo_subs_nome"))
                    print(sub.get("servidor_nome"))
                    print("----------+++++++---------")
            else:
                print("SUBSTITUTOS: NÃO EXISTE")
            print("------------------------------")

    @unittest.skip("skipping test_where_substitute")
    def test_where_substitute(self):
        employee = Servidor.objects.get(matricula=13293)
        print("employee.where_substitute()")
        # print employee.where_substitute()
        for replacement in employee.where_substitute():
            print(replacement)

    # @unittest.skip("skipping test_where_substitute")
    def test(self):
        print("")
        # employee_substituted = 1538
        employee_substituted = 1525
        # employee_substituted = 1659
        substituted = Servidor.objects.get(pk=employee_substituted)
        identify = []
        print("substituted", substituted)
        print("my_replacement")
        for rpl in substituted.my_replacement():
            print(
                rpl,
                rpl.substitute.owner,
                rpl.substitute._employee_workplaces(active=True)
                .filter(servidor__tipo="M")
                .values("servidor__pessoa_fisica__nome"),
            )
            print(
                rpl.substitute.servidores_lotacao.filter(
                    ativo=True, servidor__tipo="M"
                ).count()
            )
        print("my_replacement_substitute")
        for rpl in substituted.my_replacement_substitute():
            print(
                rpl,
                rpl.substitute.owner,
                rpl.substitute._employee_workplaces(active=True)
                .filter(servidor__tipo="M")
                .values("servidor__pessoa_fisica__nome"),
            )
            print(
                rpl.substitute.servidores_lotacao.filter(
                    ativo=True, servidor__tipo="M"
                ).count()
            )
        print("my_replacement_employee_workplace")
        for employee_workplace in substituted.my_replacement_employee_workplace():
            print(employee_workplace, employee_workplace.servidor)
        print("my_substitute_employee")
        for employee in substituted.my_substitute_employee():
            print(employee)
        print("==============================================")
        for employee in substituted.my_substitute_employee():
            print("----------------------------")
            print(employee)
            ide = {"registry": employee.matricula, "order": 0}
            my_replacement_employee_workplace = (
                substituted.my_replacement_employee_workplace()
            )
            print(my_replacement_employee_workplace.count())
            for employee_workplace in my_replacement_employee_workplace:
                print(employee_workplace)
            print(my_replacement_employee_workplace.filter(servidor=employee).count())
            for employee_workplace in my_replacement_employee_workplace.filter(
                servidor=employee
            ):
                rpl = substituted.my_replacement_substitute(
                    workplace=employee_workplace.lotacao,
                    employee=employee_workplace.servidor,
                )
                if rpl.exists():
                    rpl = rpl.earliest("order")
                    ide.update({"order": rpl.order})
            identify.append(ide)
        print("identify")
        print(identify)


class FunctionalStatusTestCase(unittest.TestCase):

    def test(self):
        for employee in Servidor.objects.filter(ativo=True, tipo__in=["S", "M"]).filter(
            # matricula=94109
        ):
            if employee.departures().exists():
                print(employee, employee.departures())
                SituacaoFuncional._manager_situations(employee=employee)
                print("------------")


class MergePersonTestCase(unittest.TestCase):

    @unittest.skip("skipping test_diff_relateds")
    def test_diff_relateds(self):
        instance = PessoaFisica.objects.get(pk=503)
        instance_new = PessoaFisica.objects.get(pk=376)
        diff = []
        for fld in instance._meta.get_fields():
            diff_field = {"name": fld.name, "label": "", "config": {}, "values": []}
            if fld.is_relation:
                if not hasattr(instance, fld.name) or fld.name in [
                    "created_by",
                    "modified_by",
                    "pessoa_ptr",
                ]:
                    # print(fld, fld.name)
                    pass
                elif fld.many_to_many:
                    diff_field.get("config").update(
                        {"label": fld.related_model._meta.verbose_name}
                    )
                    queryset = getattr(instance, fld.name).filter()
                    print(queryset.count())
                    if queryset.count():
                        if hasattr(fld, "field"):
                            diff_field.get("config").update(
                                {
                                    "manytomany_reverse": True,
                                    "model": fld.related_model,
                                    "model_class_refer": fld.field.related_model,
                                    "query": Q(
                                        **{
                                            "{}".format(
                                                fld.remote_field.name
                                            ): "{}".format(instance.pk)
                                        }
                                    ),
                                    "remote_field_name": fld.remote_field.name,
                                }
                            )
                        else:
                            diff_field.get("config").update(
                                {
                                    "manytomany": True,
                                    "model": fld.model,
                                    "model_class_refer": fld.related_model,
                                    "query": Q(**{"pk": "{}".format(instance.pk)}),
                                    "remote_field_name": fld.name,
                                    "queryset": queryset,
                                }
                            )

                    values = []
                    for q in queryset:
                        values.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance}
                        )

                    queryset = getattr(instance_new, fld.name).filter()
                    for q in queryset:
                        values.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance_new}
                        )

                    diff_field.update({"values": values})

            if len(diff_field.get("values")):
                diff.append(diff_field)
                print(diff_field)
                print("========================")
            # break
        print(len(diff))

    def test_check_not_merge(self):
        # 34879, 35066
        instance = PessoaFisica.objects.get(pk=34879)
        instance_new = PessoaFisica.objects.get(pk=35066)
        to_update = []
        field_to_choose = [
            "phone",
            "address",
            "dadosbancarios",
            "documento",
            "necessidades_especiais",
            "social_program",
            "serious_diseases",
            "municipio_naturalidade",
            "rg_uf",
            "foto",
        ]
        fields = [
            f for f in instance._meta.get_fields() if f.name not in field_to_choose
        ]
        for fld in fields:
            if fld.is_relation:
                fld_name = fld.name
                if not hasattr(instance, fld_name):
                    fld_name = "%s_set" % fld_name
                if not hasattr(instance, fld_name) or fld_name in [
                    "created_by",
                    "modified_by",
                    "pessoa_ptr",
                ]:
                    pass
                elif fld.many_to_many:
                    queryset = getattr(instance, fld_name).filter()
                    if queryset.count():
                        print(fld_name, getattr(instance, fld_name).count())
                        print(fld_name, getattr(instance_new, fld_name).count())
                        if hasattr(fld, "field"):
                            to_update.append(
                                {
                                    "manytomany_reverse": True,
                                    "model": fld.related_model,
                                    "model_class_refer": fld.field.related_model,
                                    "query": Q(
                                        **{
                                            "{}".format(
                                                fld.remote_field.name
                                            ): "{}".format(instance.pk)
                                        }
                                    ),
                                    "remote_field_name": fld.remote_field.name,
                                    "pk_add": instance_new.pk,
                                    "pk_rm": instance.pk,
                                    "fld": fld,
                                }
                            )
                        else:
                            to_update.append(
                                {
                                    "manytomany": True,
                                    "model": fld.model,
                                    "model_class_refer": fld.related_model,
                                    "query": Q(**{"pk": "{}".format(instance.pk)}),
                                    "remote_field_name": fld_name,
                                    "pk_add": instance_new.pk,
                                    "pk_rm": instance.pk,
                                    "queryset": queryset,
                                    "fld": fld,
                                }
                            )
                elif (
                    getattr(instance, fld_name, None)
                    and fld.get_internal_type() in ["ForeignKey", "OneToOneField"]
                    and isinstance(fld, (ForeignKey, OneToOneRel))
                ):
                    to_update.append(
                        {
                            "foreignkey": True,
                            "model": fld.model,
                            "model_class_refer": fld.related_model,
                            "query": Q(**{"pk": "{}".format(instance_new.pk)}),
                            "query_rm": Q(**{"pk": "{}".format(instance.pk)}),
                            "remote_field_name": fld_name,
                            "pk_add": instance_new.pk,
                            "pk_rm": instance.pk,
                            "fld": fld,
                        }
                    )
                    print(fld_name, getattr(instance, fld_name, None))
                    print(fld_name, getattr(instance_new, fld_name, None))
                elif (
                    not isinstance(fld, (ForeignKey, OneToOneRel))
                    and getattr(instance, fld_name).count()
                ):
                    print(fld_name, getattr(instance, fld_name).count())
                    print(fld_name, getattr(instance_new, fld_name).count())
                    to_update.append(
                        {
                            "model": fld.related_model,
                            "query": Q(
                                **{
                                    "{}".format(fld.remote_field.name): "{}".format(
                                        instance.pk
                                    )
                                }
                            ),
                            "remote_field_name": fld.remote_field.name,
                            "pk_add": instance_new.pk,
                            "pk_rm": instance.pk,
                            "fld": fld,
                        }
                    )
        print(len(to_update))

    @unittest.skip("skipping test_imp")
    def test_imp(self):
        # 34879, 35066
        instance = PessoaFisica.objects.get(pk=402)
        instance_new = PessoaFisica.objects.get(pk=375)
        to_update = []
        # field_to_choose = ['phone', 'address', 'dadosbancarios', 'documento', 'necessidades_especiais',
        #                    'social_program', 'serious_diseases']
        for fld in instance._meta.get_fields():
            if fld.is_relation:
                fld_name = fld.name
                if not hasattr(instance, fld_name):
                    fld_name = "%s_set" % fld_name
                if not hasattr(instance, fld_name) or fld_name in [
                    "created_by",
                    "modified_by",
                    "pessoa_ptr",
                ]:
                    # print(fld.name)
                    # print('-----------------------')
                    pass
                elif fld.many_to_many:
                    queryset = getattr(instance, fld_name).filter()
                    if queryset.count():
                        if hasattr(fld, "field"):
                            to_update.append(
                                {
                                    "manytomany_reverse": True,
                                    "model": fld.related_model,
                                    "model_class_refer": fld.field.related_model,
                                    "query": Q(
                                        **{
                                            "{}".format(
                                                fld.remote_field.name
                                            ): "{}".format(instance.pk)
                                        }
                                    ),
                                    "remote_field_name": fld.remote_field.name,
                                    "pk_add": instance_new.pk,
                                    "pk_rm": instance.pk,
                                    "fld": fld,
                                }
                            )
                            # print('1')
                        else:
                            to_update.append(
                                {
                                    "manytomany": True,
                                    "model": fld.model,
                                    "model_class_refer": fld.related_model,
                                    "query": Q(**{"pk": "{}".format(instance.pk)}),
                                    "remote_field_name": fld_name,
                                    "pk_add": instance_new.pk,
                                    "pk_rm": instance.pk,
                                    "queryset": queryset,
                                    "fld": fld,
                                }
                            )
                            # print('2')
                    # else:
                    #     print('else')
                    #     print(fld, getattr(instance, fld_name).count())
                elif (
                    getattr(instance, fld_name, None)
                    and fld.get_internal_type() in ["ForeignKey", "OneToOneField"]
                    and isinstance(fld, (ForeignKey, OneToOneRel))
                ):
                    to_update.append(
                        {
                            "foreignkey": True,
                            "model": fld.model,
                            "model_class_refer": fld.related_model,
                            "query": Q(**{"pk": "{}".format(instance_new.pk)}),
                            "query_rm": Q(**{"pk": "{}".format(instance.pk)}),
                            "remote_field_name": fld_name,
                            "pk_add": instance_new.pk,
                            "pk_rm": instance.pk,
                            "fld": fld,
                        }
                    )
                    # print('3')
                elif (
                    not isinstance(fld, (ForeignKey, OneToOneRel))
                    and getattr(instance, fld_name).count()
                ):
                    to_update.append(
                        {
                            "model": fld.related_model,
                            "query": Q(
                                **{
                                    "{}".format(fld.remote_field.name): "{}".format(
                                        instance.pk
                                    )
                                }
                            ),
                            "remote_field_name": fld.remote_field.name,
                            "pk_add": instance_new.pk,
                            "pk_rm": instance.pk,
                            "fld": fld,
                        }
                    )
                    # print('4')
                # else:
                #     print('else')
                #     print(fld, getattr(instance, fld_name).count())
                # print('-----------------------')

        for _update in to_update:
            manytomany_reverse = _update.get("manytomany_reverse")

            foreignkey = _update.get("foreignkey")
            manytomany = _update.get("manytomany")
            model = _update.get("model")
            query = _update.get("query")
            queryset = _update.get("queryset")
            remote_field_name = _update.get("remote_field_name")
            pk_add = _update.get("pk_add")
            pk_rm = _update.get("pk_rm")
            model_class_refer = _update.get("model_class_refer", PessoaFisica)
            try:
                if manytomany_reverse:
                    try:
                        for many in model.objects.filter(query):
                            att = getattr(many, remote_field_name)
                            att.add(model_class_refer.objects.get(pk=pk_add))
                            att.remove(model_class_refer.objects.get(pk=pk_rm))
                            # print(att.filter().count())
                    except Exception as err:
                        print("============>err 1 - 0")
                        print(err)
                        print(_update)
                        # print(_dict_update)
                        print("----------------------")
                elif manytomany:
                    try:
                        # print('manytomany')
                        # for many in model.objects.filter(query):
                        add = model.objects.get(pk=pk_add)
                        rm = model.objects.get(pk=pk_rm)
                        att_add = getattr(add, remote_field_name)
                        att_rm = getattr(rm, remote_field_name)
                        # print(att)
                        # print(queryset.count())
                        for inst in queryset:
                            # print(inst)
                            att_add.add(inst)
                            att_rm.remove(inst)
                        # print(att_add.filter().count())
                        # print(att_rm.filter().count())
                    except Exception as err:
                        print("============>err 1 - 1")
                        print(err)
                        print(_update)
                        # print(_dict_update)
                        print("----------------------")
                elif foreignkey:
                    try:
                        p_rm = model.objects.get(_update.get("query_rm"))
                        # _dict_update = {remote_field_name: model_class_refer.objects.get(pk=getattr(p_rm, remote_field_name))}
                        _dict_update = {
                            remote_field_name: getattr(p_rm, remote_field_name).pk
                        }
                        model.objects.filter(query).update(**_dict_update)
                    except Exception as err:
                        print("============>err 1")
                        print(err)
                        print(_update)
                        print(model)
                        print(query)
                        print(_dict_update)
                        print("----------------------")
                else:
                    try:
                        # q1 = model.objects.filter(query).count()
                        _dict_update = {remote_field_name: pk_add}
                        print(
                            model.objects.filter(query).filter(**_dict_update).count()
                        )
                        model.objects.filter(query).update(**_dict_update)
                        # q2 = model.objects.filter(**_dict_update).count()
                    except Exception as err:
                        print("============>err 2")
                        print(err)
                        print(_update)
                        print(_dict_update)
                        print("----------------------")
            except Exception as err:
                print("============>err 3")
                print(model)
                print(err)
                print("----------------------")

    @unittest.skip("test_m2m")
    def test_m2m(self):
        # found = []
        for naturalperson in PessoaFisica.objects.filter(pk=14705):
            pass

        all_field_names_from = self.mm_fields(naturalperson)

        for fld in all_field_names_from:
            print(fld.name)

    @unittest.skip("skipping test")
    def test(self):
        found = []
        for naturalperson in PessoaFisica.objects.filter():
            duplicated = (
                PessoaFisica.objects.filter(nome=naturalperson.nome)
                .exclude(nome__in=found)
                .exclude(pk=naturalperson.pk)
            )
            if duplicated.count() > 1:
                found.append(naturalperson.nome)
                break
        print(naturalperson.pk, naturalperson, duplicated.count())
        duplicated = duplicated.first()
        print(duplicated.pk, duplicated)

        # all_field_names_from = set(self.fields_names(naturalperson) + self.mm_fields_names(naturalperson))
        all_field_names_from = set(self.fields_names(naturalperson))
        # all_field_names_to = set(self.fields_names(duplicated))

        for fld_name in all_field_names_from:
            fld_from = getattr(naturalperson, fld_name, None)
            fld_to = getattr(duplicated, fld_name, None)
            if fld_from != fld_to:
                print(fld_name)
                print("diff", fld_from, fld_to)

    def fields_names(self, instance):
        fields = []
        for fld in instance._meta.get_fields():
            if not fld.is_relation and fld.name not in (
                "id",
                "created_at",
                "modified_at",
                "data_cadastro",
            ):
                fields.append(fld.name)
            # print(fld)
        # print('-----------end-----------------')
        return fields

    def mm_fields_names(self, instance):
        return [fld[0].attname for fld in instance._meta.get_m2m_with_model()]

    def mm_fields(self, instance):
        return [
            fld[0].attname for fld in instance._meta.get_fields() if fld.is_relation
        ]


class WorkAssignmentTestCase(unittest.TestCase):

    @unittest.skip("skipping test_activate_work_assignment_from_departure")
    def test_activate_work_assignment_from_departure(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        departure = BaseLicencaAfastamento.objects.get(pk=67344).my_origin
        ServidorLotacao._activate_work_assignment_from_departure(departure)

    def test_return_work_assignment_from_departured(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        departure = BaseLicencaAfastamento.objects.get(pk=67344).my_origin
        ServidorLotacao._return_work_assignment_from_departured(departure)


class NaturalPersonHistoryTest(unittest.TestCase):

    def setUp(self):
        self._natural_person = (
            Servidor.objects.filter(
                ativo=True,
                pessoa_fisica__phone__isnull=False,
                pessoa_fisica__phone__tipo_telefone=TYPE_PHONE_EMERGENCY,
                pessoa_fisica__address__isnull=False,
            )
            .last()
            .pessoa_fisica
        )
        print(self._natural_person.pk, self._natural_person)

    def tearDown(self):
        pass

    @unittest.skip("skipping test_write_history")
    def test_write_history(self):
        """address"""
        from rh.models import NaturalPersonHistory

        address = Endereco.objects.filter(
            person__pessoafisica__servidor__matricula=94109
        ).last()
        print(address.pk)
        address.numero = 1
        NaturalPersonHistory.write_history(address)

        """phone"""
        phone = address.person.phone.filter(main=True).last()
        print(phone, phone.main)
        phone.numero = 6381232647
        NaturalPersonHistory.write_history(phone)

        """natural_person"""
        natural_person = address.person.pessoafisica
        natural_person.nome = "Gustavo"
        print(natural_person.pk, natural_person)
        NaturalPersonHistory.write_history(natural_person)

    def test_create_natural_person_history(self):
        """address"""
        from rh.models import NaturalPersonHistory
        from rh.scripts.create_employee_history import (
            create_natural_person_history,
            _fill_from_instance,
            _values_from_instance,
            _fill_from_instance_original,
            _values_from_instance_original,
        )

        NaturalPersonHistory._fill_from_instance = _fill_from_instance
        NaturalPersonHistory._values_from_instance = _values_from_instance

        create_natural_person_history(self._natural_person, setup=False)

        NaturalPersonHistory._fill_from_instance = _fill_from_instance_original
        NaturalPersonHistory._values_from_instance = _values_from_instance_original

        employee_history = NaturalPersonHistory.objects.filter(
            natural_person=self._natural_person
        ).last()
        assert employee_history.when == date.today()

    def test_write_history_address(self):
        """address"""
        from rh.models import NaturalPersonHistory
        from rh.scripts.create_employee_history import _create_address

        _create_address(self._natural_person)
        employee_history = NaturalPersonHistory.objects.filter(
            natural_person=self._natural_person
        ).last()
        assert (
            employee_history.address_type_street is not None
            and employee_history.address_type_address is not None
            and employee_history.address_city is not None
            and employee_history.address_public_place is not None
            and employee_history.address_district is not None
            and employee_history.address_zip_code is not None
            and employee_history.address_number is not None
            and employee_history.address_outsider is not None
        )

    def test_write_history_phone(self):
        """phone"""
        from rh.models import NaturalPersonHistory
        from rh.scripts.create_employee_history import _create_phone

        _create_phone(self._natural_person)
        employee_history = NaturalPersonHistory.objects.filter(
            natural_person=self._natural_person
        ).last()
        assert (
            employee_history.phone_main is not None
            and employee_history.phone_type is not None
            and employee_history.phone_public is not None
            and employee_history.phone_description is not None
            and employee_history.phone_contact_emergency is not None
            and employee_history.contact_emergency_name is not None
        )
