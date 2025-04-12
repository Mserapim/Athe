# -.- coding: utf-8 -.-
# from rh.models import *
# from rh.afastamento.models import *
# from rh.afastamento.views import *
# from rh.views import *
# from rh.estagio.models import *
# from rh.estagio.views import *

import itertools

from django.contrib.auth.models import User
from django.db.models.fields import NOT_PROVIDED

from contrib.helpers import get_controller_class_for_model
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.models import Application, Controller

# from const import *

log = getLogger(__name__)

set_current_user(User.objects.get(username="gustavodettenborn"))


def mock_dynamic(**kargs):
    """
    Este método é responsável por descobrir o controller padrão do modelo, extrair a instância do Form e a partir
    dos campos do formulário aplicar valores baseando-se em seus tipos.
    Caso o campo possua valor padrão, este será o seu valor.
    Ele utiliza dois parâmetros padrão além dos campos do controller.
    @kargs['model'] - modelo que deverá ser buscado ou criado obrigatório;
    @kargs['apply_none'] - o parâmetro nomeado apply_none é opcional, caso ele seja informado a ForeignKey que o possuir será None.
    """
    model = kargs.get("model")
    controller = get_controller_class_for_model(model)
    instance_form = controller.Form()
    for field_name in instance_form.fields:
        field = model._meta.get_field(field_name)
        type_name = (type(field)).__name__
        value = None
        if type_name == "ManyToManyField":
            # print 'REMOVENDO->', 'ManyToManyField', field_name
            if field_name in kargs:
                kargs.pop(field_name)
        else:
            if field_name not in kargs and type_name != "ForeignKey":
                value = mock_django_field(field)
                kargs.update({field_name: value})
            elif type_name == "ForeignKey":
                # if not kargs.get(field_name, None) is None and not 'apply_none' in kargs:
                #     value = mock(**(kargs.get(field_name))) if not kargs.get(field_name, None) is None else None
                if (
                    "apply_none" not in kargs
                    and field.__dict__.get("required", True) is True
                ):
                    value = mock(
                        **(
                            (kargs.get(field_name))
                            if not kargs.get(field_name, None) is None
                            else {"model": field.remote_field.model}
                        )
                    )
                if field_name in kargs:
                    kargs.pop(field_name)
                kargs.update({field_name: value})
    kargs = remove_conf_pars(**kargs)
    instancia = None
    try:
        instancia = model.objects.get_or_create(**kargs)[0]
    except Exception:
        print(
            "ERRO EM mock_dynamic: erro ao criar/recuperar instância de %s"
            % model.__name__
        )
        # print 'model->', model
        # print 'kargs->', kargs
        # print err
    return instancia


def mock(**kargs):
    """
    Este método tenta pegar ou criar um objeto baseado nos parâmetros enviados.
    @kargs['model'] - modelo que deverá ser buscado ou criado obrigatório;
    @kargs['query'] - uma query, não obrigatória, para buscar um objeto específico (default=False);
    @kargs['mock_dynamic'] - uma query, não obrigatória, para buscar um objeto específico (default=True);
    @kargs['apply_none'] - o parâmetro nomeado apply_none é opcional, caso ele seja informado a ForeignKey que o possuir será None.
    @kargs['n,n1,....,nn,nn+1'] - todos os argumentos de busca padrão, quando @kargs['query'] não for informado, ou criação da instância.
    Exemplo de chamada:
        * mock(model='Model', servidor=mock(model='Model1', pk=value))
        * mock(model='Model', servidor={'model': 'Model1', 'pk': value})
        * mock(model='Model', 'query': False, 'mock_dynamic': True, 'apply_none': True, servidor={'model': 'Model1', 'pk': value})
    """
    instancia = None
    if kargs.get("model", False) is False:
        raise Exception("Parâmetro model não informado!")
    model = kargs.get("model")
    try:
        if "apply_none" not in kargs:
            if (
                not kargs.get("query", False) is False
                and model.objects.filter(kargs.get("query")).exists()
            ):
                instancia = model.objects.filter(kargs.get("query")).latest("pk")
            elif (
                len(remove_conf_pars(**kargs)) > 0
                and (
                    len(
                        [
                            resposta
                            for resposta in itertools.ifilter(
                                (lambda x: isinstance(x, dict)), kargs.itervalues()
                            )
                        ]
                    )
                    == 0
                )
                and model.objects.filter(**remove_conf_pars(**kargs)).exists()
            ):
                instancia = model.objects.filter(**remove_conf_pars(**kargs)).latest(
                    "pk"
                )
            elif model.objects.filter().exists():
                instancia = model.objects.latest("pk")
            else:
                instancia = mock_dynamic(**kargs)
    except Exception:
        print("ERRO EM mock: erro ao criar/recuperar instância de %s" % model.__name__)
    finally:
        return instancia


def mock_django_field(field):
    """
    Este método retorna valor padrão do campo ou um valor baseado no seu tipo.
    """
    return (
        parser.get((type(field)).__name__)
        if field.default == NOT_PROVIDED
        else field.default
    )


def remove_conf_pars(**kargs):
    """
    Este método remove os parâmetros de configuração.
    """
    if "model" in kargs:
        kargs.pop("model")
    if "query" in kargs:
        kargs.pop("query")
    if "mock_dynamic" in kargs:
        kargs.pop("mock_dynamic")
    if "apply_none" in kargs:
        kargs.pop("apply_none")
    return kargs


class RHConfiguracaoTests(object):

    def __init__(self, **kargs):
        pass

    @classmethod
    def setUpModule(cls):
        set_current_user(User.objects.get(username="gustavodettenborn"))

    #        print '--------begin setUpModule-------------: %s' % self.__class__
    # print '--------begin setUpModule-------------:'
    # RHSetUp()
    #        print '--------end setUpModule-------------: %s' % self.__class__
    # print '--------end setUpModule-------------:'
    # print

    @classmethod
    def tearDownModule(cls):
        pass


#        print '--------begin tearDownModule-------------: %s' % self.__class__
#        print '--------end tearDownModule-------------: %s' % self.__class__
# print '--------begin tearDownModule-------------:'
# print '--------end tearDownModule-------------:'


class ModelControllerSetUp(object):

    controller = True
    model = True
    # objects = BASE_LICENCA_AFASTAMENTO
    controllers_installeds = []

    def __init__(self, **kargs):
        pass
        # self.controller = kargs.get('controller', True) if kargs.get('controller', True) else self.controller
        # self.model = kargs.get('model', True) if kargs.get('model', True) else self.model
        # self.objects = kargs.get('objects', None) if kargs.get('objects', None) else self.objects
        # if self.objects and (self.model or self.controller):
        #     self.install_apps()

    def install_controller(self, obj):
        try:
            if obj not in self.controllers_installeds and (
                Controller.objects.filter(controller__icontains=obj).count() == 0
            ):
                controller = Controller(
                    title=eval(obj).Form.Meta.model._meta.verbose_name,
                    controller=obj,
                    application=Application.objects.get(pk=103),
                )
                controller.save()
                self.controllers_installeds.append(obj)
        except Exception:
            pass

    def install_apps(self):
        for x in self.objects:
            for obj in x.iterkeys():
                if self.controller:
                    self.install_controller(obj)


class RHSetUp(ModelControllerSetUp):

    def __init__(self, **kargs):
        # try:
        #     hoje = datetime.now().date()

        #     mock('Publicacao',
        #         pk = 2975,
        #         data_vigencia = hoje,
        #         numero = '111111111',
        #         veiculo_publicacao = 7,
        #         numero_publicacao = '111111111',
        #         tipo = 8,
        #         data_expedicao = hoje
        #     )

        #     mock('AfastamentoCompeticao',
        #         servidor = mock('Servidor', matricula = 68907),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #     )

        #     afastamento = mock('AfastamentoOutroOrgao',
        #         servidor = mock('Servidor', matricula = 108610),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         data_inicio = (hoje + relativedelta(days=1)),
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 108610).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         quadro_destino = mock('Quadro', pk=341),
        #         onus = 2,
        #         contribuicao = 2,
        #         orgao = mock('OrgaoGeral', pk = 382)
        #     )

        #     mock('MovimentacaoSubstituicaoMembro',
        #         servidor = mock('Servidor', matricula = 108610),
        #         cargo_arquimedes = 1303,
        #         afastamento = afastamento,
        #         data_inicio = afastamento.data_inicio,
        #         data_prevista = afastamento.data_prevista,
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 108610).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #     )

        #     afastamento = mock('AfastamentoOutroOrgao',
        #         servidor = mock('Servidor', matricula = 3090),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=10),
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 3090).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         quadro_destino = mock('Quadro', pk = 341),
        #         onus = 2,
        #         contribuicao = 2,
        #         orgao = mock('OrgaoGeral', pk = 382)
        #     )

        #     mock('MovimentacaoSubstituicaoMembro',
        #         servidor = mock('Servidor', matricula = 13293),
        #         cargo_arquimedes = 1040,
        #         afastamento = afastamento,
        #         data_inicio = afastamento.data_inicio,
        #         data_prevista = afastamento.data_prevista - relativedelta(days=5),
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 3090).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #     )

        #     mock('MovimentacaoSubstituicaoMembro',
        #         servidor = mock('Servidor', matricula = 13293),
        #         cargo_arquimedes = 1040,
        #         afastamento = afastamento,
        #         data_inicio = (afastamento.data_inicio + relativedelta(days=6)),
        #         data_prevista = afastamento.data_prevista,
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 3090).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #     )

        #     afastamento = mock('AfastamentoTreinamento',
        #         servidor = mock('Servidor', matricula = 108710),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = (hoje - relativedelta(days=10)),
        #         data_prevista = (hoje - relativedelta(days=2)),
        #     )

        #     inativacao = mock('InativacaoCargoMembro',
        #         cargo_arquimedes = 1140,
        #         afastamento = afastamento,
        #         data_inicio = afastamento.data_inicio,
        #         data_prevista = afastamento.data_prevista - relativedelta(days=5),
        #         publicacao_inativacao = mock('Publicacao', pk = 2975),
        #         publicacao_ativacao = mock('Publicacao', pk = 2975),
        #     )

        #     substituicao = mock('MovimentacaoSubstituicaoMembro',
        #         servidor = mock('Servidor', matricula = 13293),
        #         cargo_arquimedes = 1140,
        #         afastamento = afastamento,
        #         data_inicio = inativacao.data_prevista + relativedelta(days=1),
        #         data_prevista = inativacao.data_prevista + relativedelta(days=1),
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 108710).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #     )

        #     mock('InativacaoCargoMembro',
        #         cargo_arquimedes = 1140,
        #         afastamento = afastamento,
        #         data_inicio = substituicao.data_prevista + relativedelta(days=1),
        #         data_prevista = afastamento.data_prevista,
        #         publicacao_inativacao = mock('Publicacao', pk = 2975),
        #         publicacao_ativacao = mock('Publicacao', pk = 2975),
        #     )

        #     mock('AfastamentoTreinamento',
        #         servidor = mock('Servidor', matricula = 65507),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     afastamento = mock('AfastamentoDeslocamento',
        #         servidor = mock('Servidor', matricula = 13293),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('InativacaoCargoMembro',
        #         cargo_arquimedes = 1254,
        #         afastamento = afastamento,
        #         data_inicio = afastamento.data_inicio,
        #         data_prevista = afastamento.data_prevista,
        #         publicacao_inativacao = mock('Publicacao', pk = 2975),
        #         publicacao_ativacao = mock('Publicacao', pk = 2975),
        #     )

        #     mock('AfastamentoDeslocamento',
        #         servidor = mock('Servidor', matricula = 99810),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('AfastamentoMandatoEletivo',
        #         servidor = mock('Servidor', matricula = 96309),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #     )

        #     mock('AfastamentoEstudar',
        #         servidor = mock('Servidor', matricula = 116112),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #         instituicao = mock('UnidadeAdministrativa', pk = 382),
        #         curso = mock('Curso', pk = 5),
        #         localidade = mock('Localidade', pk = 12178)
        #     )

        #     mock('AfastamentoMissao',
        #         servidor = mock('Servidor', matricula = 98410),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #         orgao = mock('OrgaoGeral', pk = 382)
        #     )

        #     mock('AfastamentoEleitoral',
        #         servidor = mock('Servidor', matricula = 6491),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje
        #     )

        #     mock('AfastamentoServirJuri',
        #         servidor = mock('Servidor', matricula = 69607),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje
        #     )

        #     mock('AfastamentoTreinamento',
        #         servidor = mock('Servidor', matricula = 108110),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje
        #     )

        #     mock('AfastamentoTreinamento',
        #         servidor = mock('Servidor', matricula = 92508),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje
        #     )

        #     mock('AfastamentoCursoConcurso',
        #         servidor = mock('Servidor', matricula = 99610),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #         orgao = mock('OrgaoGeral', pk = 382)
        #     )

        #     mock('AfastamentoPrisao',
        #         servidor = mock('Servidor', matricula = 46403),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje
        #     )

        #     afastamento = mock('LicencaSaude3Dias',
        #         servidor = mock('Servidor', matricula = 94008),
        #         data_inicio = hoje,
        #         data_prevista = (hoje + relativedelta(days=2)),
        #         prazo_solicitado = 3,
        #         prazo_concedido = 3,
        #         deferida = True
        #     )

        #     afastamento = mock('LicencaDoencaPessoaFamilia',
        #         servidor = mock('Servidor', matricula = 96109),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #         atestado_medico = None,
        #         prazo_solicitado = 4,
        #         prazo_concedido = 4,
        #         deferida = True,
        #         data_envio = (hoje - relativedelta(days=1)),
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         acompanhado = mock('PessoaFisica', pk = 4560),
        #         grau_parentesco = 3
        #     )

        #     afastamento = mock('LicencaMaternidade',
        #         servidor = mock('Servidor', matricula = 106410),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_parto = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #         atestado_medico = None,
        #         prazo_solicitado = 4,
        #         prazo_concedido = 4,
        #         deferida = True,
        #         data_envio = (hoje - relativedelta(days=1)),
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         crianca = mock('PessoaFisica', nome = 'recem nascido')
        #     )

        #     afastamento = mock('LicencaAdocao',
        #         servidor = mock('Servidor', matricula = 110111),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #         atestado_medico = None,
        #         prazo_solicitado = 4,
        #         prazo_concedido = 4,
        #         deferida = True,
        #         data_envio = (hoje - relativedelta(days=1)),
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         crianca = mock('PessoaFisica', nome = 'filho adotado')
        #     )

        #     afastamento = mock('LicencaAfastamentoConjuge',
        #         servidor = mock('Servidor', matricula = 96209),
        #         conjuge = mock('PessoaFisica', pk = 2250),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #         orgao = mock('OrgaoGeral', pk = 382),
        #         orgao_destino = mock('OrgaoGeral', pk = 382)
        #     )

        #     afastamento = mock('LicencaServicoMilitar',
        #         servidor = mock('Servidor', matricula = 79507),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_inicio_servico = hoje - relativedelta(days=365),
        #         data_fim_servico = hoje,
        #         data_prevista = hoje + relativedelta(days=2)
        #     )

        #     afastamento = mock('LicencaCapacitacao',
        #         servidor = mock('Servidor', matricula = 69507),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje + relativedelta(days=2),
        #         curso = mock('Curso', pk = 5),
        #         instituicao = mock('UnidadeAdministrativa', pk = 382),
        #     )

        #     mock('LicencaSaude3Dias',
        #         servidor = mock('Servidor', matricula = 22999),
        #         data_inicio = (hoje + relativedelta(days=1)),
        #         data_prevista = (hoje + relativedelta(days=1)),
        #         prazo_solicitado = 3,
        #         prazo_concedido = 3,
        #         deferida = True
        #     )

        #     mock('LicencaSaude3Dias',
        #         servidor = mock('Servidor', matricula = 5990),
        #         data_inicio = (hoje + relativedelta(days=1)),
        #         data_prevista = (hoje + relativedelta(days=1)),
        #         prazo_solicitado = 3,
        #         prazo_concedido = 3,
        #         deferida = True
        #     )

        #     mock('LicencaSaude30Dias',
        #         servidor = mock('Servidor', matricula = 32201),
        #         data_inicio = (hoje + relativedelta(days=1)),
        #         data_prevista = (hoje + relativedelta(days=1)),
        #         prazo_solicitado = 30,
        #         prazo_concedido = 30,
        #         deferida = True
        #     )

        #     mock('LicencaSaudeJuntaMedica',
        #         servidor = mock('Servidor', matricula = 52404),
        #         data_inicio = (hoje - relativedelta(days=5)),
        #         atestado_medico = None,
        #         prazo_solicitado = 4,
        #         prazo_concedido = 4,
        #         deferida = True,
        #         data_envio = (hoje - relativedelta(days=1)),
        #         data_prevista = (hoje - relativedelta(days=1)),
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #     )

        #     mock('LicencaDoencaPessoaFamilia',
        #         servidor = mock('Servidor', matricula = 99510),
        #         data_inicio = (hoje - relativedelta(days=6)),
        #         data_prevista = (hoje - relativedelta(days=1)),
        #         atestado_medico = None,
        #         prazo_solicitado = 6,
        #         prazo_concedido = 6,
        #         deferida = True,
        #         data_envio = hoje,
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         grau_parentesco =3,
        #         acompanhado = mock('PessoaFisica', pk = 4532)
        #     )

        #     mock('LicencaMaternidade',
        #         servidor = mock('Servidor', matricula = 2990),
        #         data_inicio = (hoje - relativedelta(days=181)),
        #         data_parto = hoje,
        #         atestado_medico = None,
        #         prazo_solicitado = 10,
        #         prazo_concedido = 10,
        #         deferida = True,
        #         data_envio = (hoje - relativedelta(days=200)),
        #         data_prevista = hoje,
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         crianca = mock('PessoaFisica', pk = 4532)
        #     )

        #     afastamento = mock('LicencaAdocao',
        #         servidor = mock('Servidor', matricula = 5690),
        #         data_inicio = hoje,
        #         atestado_medico = None,
        #         prazo_solicitado = 10,
        #         prazo_concedido = 10,
        #         deferida = True,
        #         data_envio = hoje,
        #         data_prevista = hoje,
        #         documento_solicitacao = None,
        #         atestado_junta_medica = None,
        #         parecer = "parecer",
        #         crianca = mock('PessoaFisica', pk = 4532)
        #     )

        #     mock('MovimentacaoSubstituicaoMembro',
        #         servidor = mock('Servidor', matricula = 13293),
        #         cargo_arquimedes = 1189,
        #         afastamento = afastamento,
        #         data_inicio = afastamento.data_inicio,
        #         data_prevista = afastamento.data_prevista,
        #         posse = mock('MovimentacaoPosse', pk = Servidor.objects.get(matricula = 5690).posses_ativas.filter(quadro__cargo__tipo_lei_cargo='EF').get().pk),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #     )

        #     mock('LicencaAfastamentoConjuge',
        #         servidor = mock('Servidor', matricula = 7091),
        #         conjuge = mock('PessoaFisica', pk = 2250),
        #         data_inicio = hoje,
        #         orgao = mock('OrgaoGeral', pk = 382),
        #         orgao_destino = mock('OrgaoGeral', pk = 382)
        #     )

        #     mock('LicencaAtividadePolitica',
        #         servidor = mock('Servidor', matricula = 86208),
        #         data_inicio = hoje,
        #     )

        #     mock('LicencaCapacitacao',
        #         servidor = mock('Servidor', matricula = 100810),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         instituicao = mock('UnidadeAdministrativa', pk = 382),
        #         curso = mock('Curso', pk = 5)
        #     )

        #     mock('LicencaInteresseParticular',
        #         servidor = mock('Servidor', matricula = 80507),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         publicacao_fim = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('LicencaMandatoClassista',
        #         servidor = mock('Servidor', matricula = 106810),
        #         publicacao_movimentacao = mock('Publicacao', pk = 2975),
        #         data_inicio = hoje,
        #         entidade = mock('OrgaoGeral', pk = 382),
        #     )

        #     mock('AusenciaDoacaoSangue',
        #         servidor = mock('Servidor', matricula = 68407),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('AusenciaEleitor',
        #         servidor = mock('Servidor', matricula = 14693),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     print 'ausencia casamento----------------------------------'

        #     mock('AusenciaCasamento',
        #         servidor = mock('Servidor', matricula = 84208),
        #         conjuge = mock('PessoaFisica', pk = 2250),
        #         data_inicio = hoje,
        #         data_casamento = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('AusenciaNascimento',
        #         servidor = mock('Servidor', matricula = 94109),
        #         crianca = mock('PessoaFisica', pk = 2250),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('AusenciaFalecimento',
        #         servidor = mock('Servidor', matricula = 82707),
        #         pessoa = mock('PessoaFisica', pk = 212),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )

        #     mock('AusenciaConclusao',
        #         servidor = mock('Servidor', matricula = 30201),
        #         curso = mock('Curso', pk = 5),
        #         data_inicio = hoje,
        #         data_prevista = hoje,
        #     )
        # except Exception, e: print e
        super(RHSetUp, self).__init__(**kargs)
