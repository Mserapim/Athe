# -*- coding: utf-8 -*-

from django.db.models import Q, Sum

from contrib.utils import DateUtils, getLogger
from rh.afastamento import models as afastamento_models
from rh.gfp import models as gfp_models
from rh.gfp.previdencia import Registro
from rh.gfp.previdencia.igeprev import (
    DadosAfastamento,
    DadosCargo,
    DadosCargoCarreira,
    DadosCarreira,
    DadosDependente,
    DadosGrupoSalarial,
    DadosOrgao,
    DadosProgressao,
    DadosRemuneracao,
    DadosServidor,
    DadosUnidade,
    Igeprev,
)
from rh.models import Cargo as CargoRh
from rh.models import Carreira as CarreiraRh
from rh.models import Dependencia
from rh.models import Dependente as DependenteRh
from rh.models import Lotacao, MovimentacaoPosse, MovimentacaoRequisicao
from rh.models import Servidor as ServidorRh
from rh.models import UnidadeAdministrativa
from rh.sicap.utils import SicapServidor

log = getLogger()

__name__ = "Arquivos IGEPREV"
__hid__ = ""


class Orgao(Igeprev):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Orgao, self).__init__(**conf)

    def query(self):
        return UnidadeAdministrativa.objects.filter(
            Q(orgaogeral_ptr__lotacao=None) & ~Q(pessoa_juridica=None)
        ).exclude(poder=None)

    def add_registro(self, unidade_administrativa):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    poder=DadosOrgao.get_poder(unidade_administrativa),
                    nome=DadosOrgao.get_nome(unidade_administrativa),
                    codigo=DadosOrgao.get_codigo(unidade_administrativa),
                    sigla=DadosOrgao.get_sigla(unidade_administrativa),
                    cnpj=DadosOrgao.get_cnpj(unidade_administrativa),
                )
            )
        except Exception as err:
            log.exception(err)


class Cargo(Igeprev):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Cargo, self).__init__(**conf)

    def query(self):
        return CargoRh.objects.filter(tipo_lei_cargo__in=("EF", "AC"))

    def add_registro(self, cargo):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            salario = Grupo.query_tpl(
                [
                    cargo.pk,
                ]
            ).distinct()
            nome_grupo_salarial = "%s" % cargo.codigo
            if salario.exists():
                nome_grupo_salarial = DadosGrupoSalarial.get_nome(salario[0])
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    poder=DadosCargo.get_poder(cargo),
                    orgao=DadosCargo.get_orgao(cargo),
                    codigo=DadosCargo.get_codigo(cargo),
                    descricao=DadosCargo.get_descricao(cargo),
                    data_inicio_cargo=DadosCargo.get_data_inicio_cargo(cargo),
                    data_fim_cargo=DadosCargo.get_data_fim(cargo),
                    nome_grupo_salarial=nome_grupo_salarial,
                    cargo_acumulado=4 if cargo.indicativo == "M" else 1,
                    contagem_especial=1,
                    tecnico_especifico=0,
                    dedicacao_exclusiva=0,
                    aposentadoria_especial=0,
                )
            )
        except Exception as err:
            log.exception(err)


class Grupo(Cargo):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Grupo, self).__init__(**conf)

    @classmethod
    def query_tpl(cls, cargo):
        """
        Este método retorna um queryset ReferenciaSalario.
        Recebe uma lista de pks de cargos.
        """
        return (
            gfp_models.ReferenciaSalario.objects.filter(
                referencia_nivel2d__cargos_estrutura__cargo__pk__in=cargo
            )
            .exclude(
                Q(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="AC")
            )
            .order_by(
                "tabela_salarial__estrutura_salarial", "referencia_nivel2d__ordem"
            )
            .distinct()
        )

    @classmethod
    def query_requisicao(
        cls, cargo=None, data_referencia=None, data_referencia_inicio=None
    ):
        requisicoes = MovimentacaoRequisicao.objects.filter(
            Q(posse_origem__quadro__cargo__tipo_lei_cargo="AC")
            & (
                Q(data_inicio__lte=data_referencia)
                & (Q(data_fim__gte=data_referencia_inicio) | Q(data_fim=None))
            )
        )
        return (
            requisicoes.filter(posse_origem__quadro__cargo=cargo)
            if cargo
            else requisicoes
        )

    def query(self):
        return self.query_tpl(super(Grupo, self).query().values("pk")).distinct()

    def adiciona_corpo(self):
        super(Grupo, self).adiciona_corpo()
        self.adiciona_corpo_encargo_financeiro()

    def add_registro(self, salario):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    poder=DadosGrupoSalarial.get_poder(salario),
                    nome=DadosGrupoSalarial.get_nome(salario),
                    descricao=DadosGrupoSalarial.get_descricao(salario),
                    classe=DadosGrupoSalarial.get_classe(salario),
                    referencia=DadosGrupoSalarial.get_referencia(salario),
                    data_inicio=DadosGrupoSalarial.get_data_inicio(salario),
                    data_fim=DadosGrupoSalarial.get_data_fim(salario),
                    salario=DadosGrupoSalarial.get_salario(salario),
                )
            )
        except Exception as err:
            log.exception(err)

    def adiciona_corpo_encargo_financeiro(self):
        """
        Adiciona cargos de requições com encargos financeiros.
        """
        try:
            for requisicao in self.query_requisicao(
                data_referencia=self.get_data_referencia(),
                data_referencia_inicio=self.get_data_referencia_inicio,
            ):
                encargo_financeiro = requisicao.encargos_financeiros.filter(
                    Q(data_inicio__lte=self.get_data_referencia())
                    & (
                        Q(data_fim__gte=self.get_data_referencia_inicio())
                        | Q(data_fim=None)
                    )
                )
                if encargo_financeiro.exists():
                    encargo_financeiro = encargo_financeiro.latest("data_inicio")
                    try:
                        self.regs.append(
                            Registro(
                                len(self.regs) + 1,
                                self._class_name,
                                poder=requisicao.posse_origem.quadro.cargo.poder,
                                nome="%s"
                                % (requisicao.posse_origem.quadro.cargo.codigo),
                                descricao="%s"
                                % (requisicao.posse_origem.quadro.cargo.codigo),
                                classe="req",
                                referencia="%s" % requisicao.pk,
                                data_inicio=(
                                    DateUtils.date_to_str(
                                        encargo_financeiro.data_inicio
                                    )
                                    if encargo_financeiro.data_inicio
                                    else None
                                ),
                                data_fim=(
                                    DateUtils.date_to_str(encargo_financeiro.data_fim)
                                    if encargo_financeiro.data_fim
                                    else None
                                ),
                                salario=encargo_financeiro.remuneracao,
                            )
                        )
                    except Exception as err:
                        log.exception(err)
        except Exception as err:
            log.exception(err)


class Carreira(Igeprev):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Carreira, self).__init__(**conf)

    def query(self):
        return CarreiraRh.objects.filter()

    def add_registro(self, carreira):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    codigo=DadosCarreira.get_codigo(carreira),
                    descricao=DadosCarreira.get_descricao(carreira),
                )
            )
        except Exception as err:
            log.exception(err)


class CargoCarreira(Cargo):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(CargoCarreira, self).__init__(**conf)

    def query(self):
        return CargoRh.objects.filter(tipo_lei_cargo__in=("EF",)).exclude(
            carreira__codigo__in=("DISP",)
        )

    def add_registro(self, cargo):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            if cargo.carreira:
                self.regs.append(
                    Registro(
                        len(self.regs) + 1,
                        self._class_name,
                        poder=DadosCargoCarreira.get_poder(cargo),
                        carreira=DadosCargoCarreira.get_carreira(cargo),
                        orgao=DadosCargoCarreira.get_orgao(cargo),
                        cargo=DadosCargoCarreira.get_cargo(cargo),
                    )
                )
        except Exception as err:
            log.exception(err)


class Servidor(Igeprev):

    dados_servidor = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Servidor, self).__init__(**conf)

    def conf(self, **conf):
        super(Servidor, self).conf(**conf)
        self.dados_servidor = DadosServidor(
            data_referencia=self.get_data_referencia(),
            data_referencia_inicio=self.get_data_referencia_inicio(),
            importacao_completa=self._importacao_completa,
        )

    def query(self, in_genre_event=[]):
        if self._importacao_completa:
            servidores = ServidorRh.objects.filter(
                tipo__in=("S", "M"),
                social_securities__organ__cnpj="25091307000176",
            ).distinct()
        else:
            servidores = ServidorRh.objects.filter(
                tipo__in=("S", "M"),
                social_securities__organ__cnpj="25091307000176",
                entries__folha__pk=self.folha,
                entries__folha__periodo__mes=(
                    self.get_data_referencia().month
                    if self._mes_referencia != 13
                    else 13
                ),
                entries__folha__periodo__ano=self.get_data_referencia().year,
            ).distinct()
        return servidores

    def add_registro(self, servidor):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            # if servidor.membro:
            ddd, telefone = self.dados_servidor.get_telefone(servidor.pessoa_fisica)
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    orgao_atual=self.dados_servidor.get_orgao_atual(servidor),
                    orgao_origem=self.dados_servidor.get_orgao_origem(servidor),
                    lotacao=self.dados_servidor.get_lotacao(servidor),
                    matricula=DadosServidor.get_matricula(servidor),
                    nome=DadosServidor.get_nome(servidor.pessoa_fisica),
                    cpf=DadosServidor.get_cpf(servidor.pessoa_fisica),
                    identidade=DadosServidor.get_identidade(servidor.pessoa_fisica),
                    uf_identidade=DadosServidor.get_uf_identidade(
                        servidor.pessoa_fisica
                    ),
                    data_identidade=DadosServidor.get_data_identidade(
                        servidor.pessoa_fisica
                    ),
                    numero_titulo_eleitor=DadosServidor.get_numero_titulo_eleitor(
                        servidor.pessoa_fisica
                    ),
                    zona_titulo_eleitor=DadosServidor.get_zona_titulo_eleitor(
                        servidor.pessoa_fisica
                    ),
                    secao_titulo_eleitor=DadosServidor.get_secao_titulo_eleitor(
                        servidor.pessoa_fisica
                    ),
                    uf_titulo_eleitor=DadosServidor.get_uf_titulo_eleitor(
                        servidor.pessoa_fisica
                    ),
                    municipio_naturalidade=DadosServidor.get_municipio_naturalidade(
                        servidor.pessoa_fisica
                    ),
                    uf_naturalidade=DadosServidor.get_uf_naturalidade(
                        servidor.pessoa_fisica
                    ),
                    data_nascimento=DadosServidor.get_data_nascimento(
                        servidor.pessoa_fisica
                    ),
                    sexo=DadosServidor.get_sexo(servidor.pessoa_fisica),
                    estado_civil=DadosServidor.get_estado_civil(servidor.pessoa_fisica),
                    bairro=self.dados_servidor.get_bairro(
                        objeto=servidor.pessoa_fisica, label="bairro", linha="20"
                    ),
                    municipio=self.dados_servidor.get_municipio(
                        objeto=servidor.pessoa_fisica, label="municipio", linha="21"
                    ),
                    uf=self.dados_servidor.get_uf(
                        objeto=servidor.pessoa_fisica, label="uf", linha="22"
                    ),
                    pais=self.dados_servidor.get_uf(
                        objeto=servidor.pessoa_fisica, label="pais", linha="23"
                    ),
                    cep=self.dados_servidor.get_cep(
                        objeto=servidor.pessoa_fisica, label="cep", linha="24"
                    ),
                    tipo_logradouro=self.dados_servidor.get_tipo_logradouro(
                        objeto=servidor.pessoa_fisica,
                        label="tipo_logradouro",
                        linha="25",
                    ),
                    logradouro=self.dados_servidor.get_logradouro(
                        objeto=servidor.pessoa_fisica, label="logradouro", linha="26"
                    ),
                    quadra=self.dados_servidor.get_quadra(
                        objeto=servidor.pessoa_fisica, label="quadra", linha="27"
                    ),
                    lote=self.dados_servidor.get_lote(
                        objeto=servidor.pessoa_fisica, label="lote", linha="28"
                    ),
                    numero=self.dados_servidor.get_numero(
                        objeto=servidor.pessoa_fisica, label="numero", linha="29"
                    ),
                    complemento=self.dados_servidor.get_complemento(
                        objeto=servidor.pessoa_fisica, label="complemento", linha="30"
                    ),
                    pis_pasep=DadosServidor.get_pis_pasep(servidor.pessoa_fisica),
                    grau_instrucao=DadosServidor.get_grau_instrucao(
                        servidor.pessoa_fisica
                    ),
                    email=DadosServidor.get_email(servidor.pessoa_fisica),
                    data_obito=DadosServidor.get_data_obito(servidor.pessoa_fisica),
                    ddd=ddd,
                    telefone=telefone,
                    nome_mae=DadosServidor.get_nome_mae(servidor.pessoa_fisica),
                    nome_pai=DadosServidor.get_nome_pai(servidor.pessoa_fisica),
                    vinculo_ente=self.dados_servidor.get_vinculo_ente(servidor),
                    situacao_previdenciaria=self.dados_servidor.get_situacao_previdenciaria(
                        servidor
                    ),
                    situacao_funcional=self.dados_servidor.get_situacao_funcional(
                        servidor
                    ),
                    cargo_atual=self.dados_servidor.get_cargo_atual(servidor),
                    data_posse=self.dados_servidor.get_data_posse(servidor),
                    data_exoneracao=self.dados_servidor.get_data_exoneracao(servidor),
                    data_inicio_funcao=self.dados_servidor.get_data_inicio_funcao(
                        servidor
                    ),
                    data_ingresso_servico_publico=DadosServidor.get_data_ingresso_servico_publico(
                        servidor
                    ),
                    data_ingresso_carreira=self.dados_servidor.get_data_ingresso_carreira(
                        servidor
                    ),
                    folha=Igeprev.get_folha(),
                    classe_salarial_atual=self.dados_servidor.get_classe_salarial_atual(
                        servidor
                    ),
                    referencia_salarial_atual=self.dados_servidor.get_referencia_salarial_atual(
                        servidor
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class ServidorRequisitado(Servidor):

    dados_servidor = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(ServidorRequisitado, self).__init__(**conf)

    @classmethod
    def requisitados(cls, folha, data_referencia, mes_referencia):
        servidores = ServidorRh.objects.filter(
            pk__in=ServidorRh.objects.filter(
                tipo__in=("S", "M"),
                entries__evento__em_plano__pessoa_juridica__cnpj="25091307000176",
                entries__folha__pk=folha,
                entries__folha__periodo__mes=(
                    data_referencia.month if mes_referencia != 13 else 13
                ),
                entries__folha__periodo__ano=data_referencia.year,
            ).values("pk"),
            categoria_cache__in=("REQ", "RCM", "RFC"),
        ).distinct()
        return servidores

    def query(self):
        return self.requisitados(
            self.folha, self.get_data_referencia(), self._mes_referencia
        )


class Remuneracao(Servidor):

    _competencia = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Remuneracao, self).__init__(**conf)

    def conf(self, **conf):
        super(Remuneracao, self).conf(**conf)
        self.dados_remuneracao = DadosRemuneracao(
            data_referencia=self.get_data_referencia(),
            data_referencia_inicio=self.get_data_referencia_inicio(),
            importacao_completa=self._importacao_completa,
        )
        self.dados_remuneracao._mes_referencia = self._mes_referencia
        self._competencia = "%s%s" % (
            self.get_data_referencia().year,
            (
                self.get_data_referencia().month
                if len(str(self.get_data_referencia().month)) > 1
                else ("0%s" % self.get_data_referencia().month)
            ),
        )

    def add_registro(self, servidor):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            """
            pensar em buscar as informações de remuneração de acordo com a FOLHA.
            """
            bruto, liquido, valor_base, contribuicao, patronal = (
                self.dados_remuneracao.calculo(servidor, self.folha)
            )
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    tipo_participante=DadosRemuneracao.get_tipo_participante(servidor),
                    # orgao_atual=self.dados_servidor.get_orgao_atual(servidor),
                    orgao_atual=DadosCargo.get_orgao(
                        self.dados_servidor.get_posse_atual(servidor).quadro.cargo
                    ),
                    matricula=DadosServidor.get_matricula(servidor),
                    cpf=DadosServidor.get_cpf(servidor.pessoa_fisica),
                    cargo=self.dados_servidor.get_cargo_atual(servidor),
                    data_posse=self.dados_servidor.get_data_posse(servidor),
                    tipo_remuneracao=self.dados_remuneracao.get_tipo_remuneracao(
                        servidor
                    ),
                    salario_bruto=bruto,
                    salario_liquido=liquido,
                    contribuicao_patronal=patronal,
                    contribuicao_segurado=contribuicao,
                    salario_contribuicao=valor_base,
                    competencia=self._competencia,
                    folha=Igeprev.get_folha(),
                    cpf_dependente="",
                    data_nascimento_dependente="",
                    sexo_dependente="",
                )
            )
        except Exception as err:
            log.exception(err)


class ServidorLevantamento(Remuneracao):

    dados_servidor = None

    @classmethod
    def _query(cls, folha):
        return gfp_models.FolhaEvento.objects.filter(
            contracheque__folha=folha, evento__numero__in=["90000", "90500"]
        )  # .filter(contracheque__servidor__matricula__in=[22999, 32201, 3190, 77207, 130515])

    def query(self):
        return self._query(self.folha)

    def add_registro(self, folhaevento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        servidor = folhaevento.contracheque.servidor
        remunera = str(folhaevento.valor_base)
        remunera = remunera.replace(".", "")
        remuner = 0
        try:
            remuner = str(DadosRemuneracao.remuner(servidor, self.folha))
            remuner = remuner.replace(".", "")
        except Exception:
            pass

        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    matricula=DadosServidor.get_matricula(servidor),
                    patroc="25091307000176",
                    tipo_orgao="",
                    descr_orgao="PROCURADORIA GERAL DE JUSTIÇA - PGJ-TO",
                    cargo=str(
                        self.dados_servidor.get_posse_atual(servidor).quadro.cargo
                    ),
                    data_nascimento=DadosServidor.get_data_nascimento(
                        servidor.pessoa_fisica
                    ),
                    sexo=DadosServidor.get_sexo(servidor.pessoa_fisica),
                    estado_civil=str(
                        DadosServidor.get_estado_civil(servidor.pessoa_fisica)
                    ),
                    data_admissao=self.dados_servidor.get_data_inicio_funcao(servidor),
                    remunera=remunera,
                    data_carreira=self.dados_servidor.get_data_ingresso_carreira(
                        servidor
                    ),
                    data_cargo=self.dados_servidor.get_data_posse(servidor),
                    remuner=remuner,
                    tipo_ativ="1",
                    categoria="1",
                    tempo_ant=DadosRemuneracao.tempo_anterior_rgps(servidor),
                    grupo_orgao=4,
                    fundo=DadosRemuneracao.fundo(folhaevento),
                )
            )
        except Exception as err:
            log.exception(err)

    @classmethod
    def estado_civil(cls, estado_civil):
        parser = {
            1: "0",  # solteiro
            2: "1",  # casado e união estável
            6: "1",  # casado e união estável
            3: "2",  # viúvo
            4: "3",  # desquitado/divorciado/separado
            5: "3",  # desquitado/divorciado/separado
        }
        return parser.get(estado_civil)


class ServidorAuditoriaTce(ServidorLevantamento):

    @classmethod
    def _query(cls, folha):
        query = ServidorLevantamento._query(folha)
        return query.exclude(
            servidor__pk__in=MovimentacaoPosse.objects.filter(
                quadro__cargo__tipo_lei_cargo="AC"
            ).values("servidor")
        )

    def add_registro(self, folhaevento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        servidor = folhaevento.contracheque.servidor
        remunera = str(folhaevento.valor_base)
        remunera = remunera.replace(".", "")
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    matricula=DadosServidor.get_matricula(servidor),
                    sexo=DadosServidor.get_sexo(servidor.pessoa_fisica),
                    estado_civil=str(
                        DadosServidor.get_estado_civil(servidor.pessoa_fisica)
                    ),
                    data_nascimento=DadosServidor.get_data_nascimento(
                        servidor.pessoa_fisica
                    ).replace("/", ""),
                    carreira=str(
                        self.dados_servidor.get_posse_atual(
                            servidor
                        ).quadro.cargo.carreira
                    ),
                    cargo=str(
                        self.dados_servidor.get_posse_atual(servidor).quadro.cargo
                    ),
                    data_ingresso=self.dados_servidor.get_data_posse(servidor).replace(
                        "/", ""
                    ),
                    data_cargo=self.dados_servidor.get_data_inicio_funcao(
                        servidor
                    ).replace("/", ""),
                    data_carreira=self.dados_servidor.get_data_inicio_funcao(
                        servidor
                    ).replace("/", ""),
                    tempo_ant=0,
                    tempo_outro_rpps=0,
                    remunera=remunera,
                    data_nascimento_conjuge=ServidorAuditoriaTce.date_born_spouse(
                        servidor, self.get_data_referencia_inicio()
                    ).replace("/", ""),
                    qtd_dependentes=ServidorAuditoriaTce.dependent_count(
                        servidor, self.get_data_referencia_inicio()
                    ),
                )
            )
        except Exception as err:
            log.exception(err)

    @classmethod
    def estado_civil(cls, estado_civil):
        parser = {
            3: "5",
            6: "2",
            7: "6",
        }
        return parser.get(estado_civil)

    @classmethod
    def dependency(cls, employee, date_start):
        return Dependencia.objects.filter(
            data_inicio__lte=date_start, tipo=5, dependente__servidor=employee
        )

    @classmethod
    def dependent_count(cls, employee, date_start):
        return cls.dependency(employee, date_start).values("dependente").count()

    @classmethod
    def date_born_spouse(cls, employee, date_start):
        date_born = ""
        dependency = cls.dependency(employee, date_start).filter(
            dependente__grau_parentesco=1
        )
        if dependency.exists():
            dependent = dependency.latest("data_inicio").dependente
            date_born = (
                DateUtils.date_to_str(dependent.pessoa_fisica.data_nascimento)
                if dependent.pessoa_fisica.data_nascimento
                else ""
            )
        return date_born


class ServidorTce(Remuneracao):

    def query(self):
        return gfp_models.ContraCheque.objects.filter(
            servidor__tipo__in=("S", "M"),
            folha__pk=self.folha,
            folha__periodo__mes=(
                self.get_data_referencia().month if self._mes_referencia != 13 else 13
            ),
            folha__periodo__ano=self.get_data_referencia().year,
        ).distinct()

    def add_registro(self, paycheck):
        try:
            servidor = paycheck.servidor
            possession = self.get_possession(servidor)
            date_fired = date_retirement = ""
            if possession and possession.data_desligamento:
                date_fired = DateUtils.date_to_str(possession.data_desligamento)
                if hasattr(possession.desligamento, "movimentacaoaposentadoria"):
                    date_retirement = date_fired
            month = str(self._mes_referencia)
            month = "0%s" % month if len(month) == 1 else month
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    # TODO: GERAR COM O SEPARADOR #
                    separator="#",
                    orgao="PROCURADORIA GERAL DE JUSTIÇA - PGJ-TO",
                    esfera="1",
                    municipio=self.get_workplace(servidor),
                    uf="TO",
                    nome=DadosServidor.get_nome(servidor.pessoa_fisica),
                    cpf=DadosServidor.get_cpf(servidor.pessoa_fisica),
                    matricula=DadosServidor.get_matricula(servidor),
                    regime=ServidorTce.legal_regime(possession.quadro),
                    cargo=str(possession.quadro.cargo),
                    cargo_natureza=ServidorTce.job_position_nature(possession.quadro),
                    data_exercicio=DateUtils.date_to_str(possession.data_exercicio),
                    data_aposentadoria=date_retirement,
                    data_exclusao=date_fired,
                    jornada=ServidorTce.working_hours(possession),
                    categoria_situacao=ServidorTce.job_position_category(servidor),
                    nome_pensionista="",
                    cpf_pensionista="",
                    folha_mes_ano="%s%s" % (month, self.get_data_referencia().year),
                    valor_bruto=ServidorTce.gross(servidor),
                    valor_teto=ServidorTce.value_for_ceiling(servidor, self.folha),
                    valor_abate_teto=ServidorTce.slaughter_value_ceiling(
                        servidor, self.folha
                    ),
                )
            )
        except Exception as err:
            log.exception(err)

    def get_possession(self, servidor):
        possessions = self.dados_servidor.get_posses(servidor)
        possession = None
        if servidor.membro:
            possession = possessions.latest("data_exercicio")
        else:
            possession = (
                possessions.exclude(Q(quadro__cargo__tipo_lei_cargo__in=("CM"))).latest(
                    "data_exercicio"
                )
                if possessions.exists()
                else None
            )
        if not possession:
            cache = servidor.posses.exclude(
                Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))
            )
            if cache.exists():
                possession = cache.latest("data_exercicio") if cache.exists() else None
            else:
                cache = servidor.posses
                possession = cache.latest("data_exercicio") if cache.exists() else None
        return possession

    def get_workplace(self, employee):
        workplace = "PROCURADORIA GERAL DE JUSTIÇA - PGJ-TO"
        employee_workplace = employee._raw_locations(option=1).exclude(
            data_vigencia_inicio__gt=self._data_referencia
        )
        if employee_workplace.exists():
            workplace = employee_workplace.latest("data_vigencia_inicio").lotacao
        elif employee._raw_locations().exists():
            workplace = employee._raw_locations().latest("data_vigencia_inicio").lotacao
        return str(workplace)

    @classmethod
    def job_position_nature(cls, job_position_table):
        value = 1
        if job_position_table.cargo_quadro and job_position_table.cargo_quadro.teacher:
            value = 3
        elif job_position_table.cargo_quadro and job_position_table.cargo_quadro.health:
            value = 2
        return str(value)

    @classmethod
    def legal_regime(cls, job_position_table):
        value = 1
        if job_position_table.cargo_quadro and job_position_table.cargo_quadro.military:
            value = 2
        return str(value)

    @classmethod
    def working_hours(cls, possession):
        return str(possession.quadro.carga_horaria)

    @classmethod
    def job_position_category(cls, employee):
        category = {
            1: 1,  # u'Carreira em exercício no próprio órgão',
            2: 2,  # u'Exclusivamente comissionado',
            5: 3,  # u'Cedido',
            6: 4,  # u'Inativo(aposentado)',
            7: 5,  # u'Instituidor de pensão por morte',
            8: 6,  # u'Requisitado',
            3: 7,  # u'Temporário',
            4: 8,  # u'Outras situações',
            9: 1,  # u'Outras situações',
            10: 8,  # u'Outras situações',
        }
        # type_13_link_payment = {
        #     1: u'Efetivo',
        #     2: u'Comissionado',
        #     3: u'Contratado',
        #     4: u'Disposição',
        #     5: u'Cedido',
        #     6: u'Aposentado',
        #     7: u'Pensionista',
        #     8: u'Requisitado',
        #     9: u'Eletivo',
        #     10: u'Estagiário',
        # }
        return str(category.get(SicapServidor.type_link_payment(employee)))

    @classmethod
    def gross(cls, employee):
        gross = (
            employee.paychecks.get(
                folha=gfp_models.Folha.objects.get(pk=774)
            ).total_bruto
            or "0,00"
        )
        gross = str(gross).replace(".", ",")
        gross = gross.replace("+", "")
        gross = gross.replace("-", "")
        return gross

    @classmethod
    def value_for_ceiling(cls, employee, sheet):
        event = [
            "001",
            "002",
            "004",
            "005",
            "006",
            "007",
            "011",
            "014",
            "020",
            "090",
            "091",
            "710",
        ]
        value = (
            employee.paychecks.get(folha=gfp_models.Folha.objects.get(pk=sheet))
            .lancamentos.filter(evento__genre_event__genre_number__in=event)
            .aggregate(total=Sum("value"))
            .get("total")
            or "0,00"
        )
        value = str(value).replace(".", ",")
        value = value.replace("+", "")
        value = value.replace("-", "")
        return value

    @classmethod
    def slaughter_value_ceiling(cls, employee, sheet):
        event = ["49900"]
        value = (
            employee.paychecks.get(folha=gfp_models.Folha.objects.get(pk=sheet))
            .lancamentos.filter(evento__numero__in=event)
            .aggregate(total=Sum("value"))
            .get("total")
            or "0,00"
        )
        value = str(value).replace(".", ",")
        value = value.replace("+", "")
        value = value.replace("-", "")
        return value


class RemuneracaoRequisitado(Remuneracao):

    def query(self):
        return ServidorRequisitado.requisitados(
            self.folha, self.get_data_referencia(), self._mes_referencia
        )


class Progressao(Servidor):

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Progressao, self).__init__(**conf)

    def query(self):
        if self._importacao_completa:
            return gfp_models.MovimentacaoProgressao.objects.filter()
        else:
            return gfp_models.MovimentacaoProgressao.objects.filter(
                Q(
                    data_vigencia__month=self._mes_referencia,
                    data_vigencia__year=self._ano_referencia,
                )
            ).exclude(Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo="AC"))

    def add_registro(self, progressao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            salario = Grupo.query_tpl(
                [
                    progressao.movimentacao_posse.quadro.cargo.pk,
                ]
            ).filter(referencia_nivel2d=progressao.referencia_nivel2d)
            if salario.count():
                self.regs.append(
                    Registro(
                        len(self.regs) + 1,
                        self._class_name,
                        matricula=DadosServidor.get_matricula(progressao.servidor),
                        cpf=DadosServidor.get_cpf(progressao.servidor.pessoa_fisica),
                        orgao_atual=self.dados_servidor.get_orgao_atual(
                            progressao.servidor
                        ),
                        cargo=DadosProgressao.get_cargo(progressao),
                        data_posse=DadosProgressao.get_data_posse(progressao),
                        data_inicio_vigencia=DadosProgressao.get_data_inicio_vigencia(
                            progressao
                        ),
                        data_fim_vigencia=DadosProgressao.get_data_fim_vigencia(
                            progressao
                        ),
                        grupo_salarial=DadosGrupoSalarial.get_nome(salario[0]),
                        classe=DadosGrupoSalarial.get_classe(salario[0]),
                        referencia=DadosGrupoSalarial.get_referencia(salario[0]),
                        salario=DadosGrupoSalarial.get_salario(salario[0]),
                    )
                )
        except Exception as err:
            log.exception(err)


class Afastamento(Servidor):

    dados_afastamento = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Afastamento, self).__init__(**conf)

    def conf(self, **conf):
        super(Afastamento, self).conf(**conf)
        self.dados_afastamento = DadosAfastamento(
            data_referencia=self.get_data_referencia(),
            data_referencia_inicio=self.get_data_referencia_inicio(),
            importacao_completa=self._importacao_completa,
        )

    def query(self):
        if self._importacao_completa:
            afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
                ~Q(afastamento__afastamentooutroorgao=None)
                | ~Q(licenca__licencainteresseparticular=None)
                | ~Q(licenca__licencaafastamentoconjuge=None)
                | ~Q(licenca__licencamandatoclassista=None)
                | ~Q(licenca__licencaatividadepolitica=None)
            )
        else:
            afastamentos = afastamento_models.BaseLicencaAfastamento.objects.filter(
                Q(
                    ~Q(afastamento__afastamentooutroorgao=None)
                    | ~Q(licenca__licencainteresseparticular=None)
                    | ~Q(licenca__licencaafastamentoconjuge=None)
                    | ~Q(licenca__licencamandatoclassista=None)
                    | ~Q(licenca__licencaatividadepolitica=None)
                )
                & Q(
                    data_inicio__month=self._mes_referencia,
                    data_inicio__year=self._ano_referencia,
                )
            )
        return afastamentos.exclude(estado=afastamento_models.CANCELED)

    def add_registro(self, afastamento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    matricula=DadosServidor.get_matricula(afastamento.servidor),
                    cpf=DadosServidor.get_cpf(afastamento.servidor.pessoa_fisica),
                    nome=DadosServidor.get_nome(afastamento.servidor.pessoa_fisica),
                    orgao_origem=self.dados_servidor.get_orgao_origem(
                        afastamento.servidor
                    ),
                    cargo_origem=self.dados_servidor.get_cargo_origem(
                        afastamento.servidor
                    ),
                    data_posse=self.dados_servidor.get_data_posse_origem(
                        afastamento.servidor
                    ),
                    orgao_destino=self.dados_afastamento.get_orgao_destino(
                        objeto=afastamento, label="orgao_destino", linha="8"
                    ),
                    cargo_destino=DadosAfastamento.get_cargo_destino(afastamento),
                    data_inicio_afastamento=DadosAfastamento.get_data_inicio(
                        afastamento
                    ),
                    data_fim_afastamento=DadosAfastamento.get_data_fim(afastamento),
                    codigo_afastamento=DadosAfastamento.get_codigo(afastamento),
                    ato=self.dados_afastamento.get_ato(
                        objeto=afastamento, label="ato", linha="13"
                    ),
                    data_publicacao_do=DadosAfastamento.get_data_publicacao_do(
                        afastamento
                    ),
                    numero_publicacao_do=DadosAfastamento.get_numero_publicacao_do(
                        afastamento
                    ),
                    data_revogacao=DadosAfastamento.get_data_revogacao(afastamento),
                    data_retorno=DadosAfastamento.get_data_retorno(afastamento),
                    data_publicacao_do_revogacao=DadosAfastamento.get_data_publicacao_do_revogacao(
                        afastamento
                    ),
                    numero_publicacao_do_revogacao=DadosAfastamento.get_numero_publicacao_do_revogacao(
                        afastamento
                    ),
                    opcao_contribuicao=self.dados_afastamento.get_opcao_contribuicao(
                        objeto=afastamento, label="opcao_contribuicao", linha="20"
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class Dependente(Igeprev):

    dados_dependente = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Dependente, self).__init__(**conf)

    def conf(self, **conf):
        super(Dependente, self).conf(**conf)
        self.dados_dependente = DadosDependente(
            data_referencia=self.get_data_referencia(),
            data_referencia_inicio=self.get_data_referencia_inicio(),
            importacao_completa=self._importacao_completa,
        )

    def query(self):
        if self._importacao_completa:
            return Dependencia.objects.filter(
                Q(tipo=5) & Q(dependente__servidor__ativo=True)
            )
        else:
            return Dependencia.objects.filter(
                Q(tipo=5)
                & Q(dependente__servidor__ativo=True)
                & Q(
                    dependente__data_alteracao__month=self._mes_referencia,
                    dependente__data_alteracao__year=self._ano_referencia,
                )
            )

    def add_registro(self, dependencia):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    nome_mae_servidor=DadosServidor.get_nome_mae(
                        dependencia.dependente.servidor.pessoa_fisica
                    ),
                    cpf_servidor=DadosServidor.get_cpf(
                        dependencia.dependente.servidor.pessoa_fisica
                    ),
                    nome_dependente=DadosDependente.get_nome(
                        dependencia.dependente.pessoa_fisica
                    ),
                    data_nascimento_dependente=DadosDependente.get_data_nascimento(
                        dependencia.dependente.pessoa_fisica
                    ),
                    tipo_capacidade_dependente=DadosDependente.get_tipo_capacidade(
                        dependencia.dependente
                    ),
                    sexo_dependente=DadosDependente.get_sexo(
                        dependencia.dependente.pessoa_fisica
                    ),
                    cpf_dependente=(
                        DadosDependente.get_cpf(dependencia.dependente.pessoa_fisica)
                        if not DadosDependente.get_cpf(
                            dependencia.dependente.pessoa_fisica
                        )
                        == ""
                        else DadosServidor.get_cpf(
                            dependencia.dependente.servidor.pessoa_fisica
                        )
                    ),
                    identidade=DadosDependente.get_identidade(
                        dependencia.dependente.pessoa_fisica
                    ),
                    identidade_uf=DadosDependente.get_uf_identidade(
                        dependencia.dependente.pessoa_fisica
                    ),
                    data_emissao_identidade=DadosDependente.get_data_identidade(
                        dependencia.dependente.pessoa_fisica
                    ),
                    email_dependente=DadosDependente.get_email(
                        dependencia.dependente.pessoa_fisica
                    ),
                    estado_civil=DadosDependente.get_estado_civil(
                        dependencia.dependente.pessoa_fisica
                    ),
                    grau_instrucao=DadosDependente.get_grau_instrucao(
                        dependencia.dependente.pessoa_fisica
                    ),
                    grau_parentesco=DadosDependente.get_grau_parentesco(
                        dependencia.dependente
                    ),
                    data_inicio_dependente=DadosDependente.get_data_inicio_dependente(
                        dependencia.dependente
                    ),
                    motivo_inicio_dependente=DadosDependente.get_motivo_inicio_dependente(
                        dependencia.dependente
                    ),
                    data_termino_dependencia=DadosDependente.get_data_termino_dependencia(
                        dependencia.dependente
                    ),
                    motivo_fim_dependencia=DadosDependente.get_motivo_fim_dependencia(
                        dependencia.dependente
                    ),
                    tipo_dependencia=DadosDependente.get_tipo_dependencia(
                        dependencia.dependente
                    ),
                    nome_mae_dependente=DadosDependente.get_nome_pai(
                        dependencia.dependente.pessoa_fisica
                    ),
                    nome_pai_dependente=DadosDependente.get_nome_mae(
                        dependencia.dependente.pessoa_fisica
                    ),
                    banco=self.dados_dependente.get_banco(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="banco",
                        linha="23",
                    ),
                    agencia=self.dados_dependente.get_agencia(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="agencia",
                        linha="24",
                    ),
                    dv_agencia=self.dados_dependente.get_dv_agencia(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="dv_agencia",
                        linha="25",
                    ),
                    conta=self.dados_dependente.get_conta(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="conta",
                        linha="26",
                    ),
                    dv_conta=self.dados_dependente.get_dv_conta(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="dv_conta",
                        linha="27",
                    ),
                    bairro=self.dados_dependente.get_bairro(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="bairro",
                        linha="28",
                    ),
                    municipio=self.dados_dependente.get_municipio(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="municipio",
                        linha="29",
                    ),
                    uf=self.dados_dependente.get_uf(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="uf",
                        linha="30",
                    ),
                    cep=self.dados_dependente.get_cep(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="cep",
                        linha="31",
                    ),
                    tipo_logradouro=self.dados_dependente.get_tipo_logradouro(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="tipo_logradouro",
                        linha="32",
                    ),
                    logradouro=self.dados_dependente.get_logradouro(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="logradouro",
                        linha="33",
                    ),
                    quadra=self.dados_dependente.get_quadra(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="quadra",
                        linha="34",
                    ),
                    lote=self.dados_dependente.get_lote(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="lote",
                        linha="35",
                    ),
                    numero=self.dados_dependente.get_numero(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="numero",
                        linha="36",
                    ),
                    complemento=self.dados_dependente.get_complemento(
                        objeto=dependencia.dependente.pessoa_fisica,
                        label="complemento",
                        linha="37",
                    ),
                    data_nascimento_servidor=DadosServidor.get_data_nascimento(
                        dependencia.dependente.servidor.pessoa_fisica
                    ),
                    sexo_servidor=DadosServidor.get_sexo(
                        dependencia.dependente.servidor.pessoa_fisica
                    ),
                    folha=Igeprev.get_folha(),
                    data_prevista_termino_dependencia=DadosDependente.get_data_prevista_termino_dependencia(
                        dependencia.dependente
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class DependenteLevantamento(Dependente):

    dados_dependente = None

    def query(self):
        return Dependencia.objects.filter(
            data_inicio__lte=self.get_data_referencia(),
            tipo=5,
            dependente__servidor__pk__in=ServidorLevantamento._query(self.folha).values(
                "servidor"
            ),
        )

    def add_registro(self, dependencia):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            matricula_dep = DadosDependente.get_cpf(
                dependencia.dependente.pessoa_fisica
            )
            if not matricula_dep:
                matricula_dep = DadosServidor.get_cpf(
                    dependencia.dependente.servidor.pessoa_fisica
                )
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    matricula=DadosServidor.get_matricula(
                        dependencia.dependente.servidor
                    ),
                    matricula_dep=str(matricula_dep),
                    ordem=dependencia.pk,
                    data_nascimento=DadosDependente.get_data_nascimento(
                        dependencia.dependente.pessoa_fisica
                    ),
                    sexo=DadosDependente.get_sexo(dependencia.dependente.pessoa_fisica),
                    grau=DependenteLevantamento.get_grau_parentesco(dependencia),
                    classe=DependenteLevantamento.get_classe(dependencia),
                    cond_dep=DependenteLevantamento.get_condicao_fisica(dependencia),
                    espec_grau=DependenteLevantamento.get_especificao_grau(dependencia),
                )
            )
        except Exception as err:
            log.exception(err)

    @classmethod
    def get_classe(cls, dependencia):
        if dependencia.dependente.servidor.ativo:
            return "1"
        return "2"

    @classmethod
    def get_condicao_fisica(cls, dependencia):
        return str(dependencia.dependente.capacidade)

    @classmethod
    def get_grau_parentesco(cls, dependencia):
        parser = {
            1: 1,
            2: 1,
            3: 3,
            4: 2,
            5: 4,
        }
        return str(parser.get(dependencia.dependente.grau_parentesco, 5))

    @classmethod
    def get_especificao_grau(cls, dependencia):
        if DependenteLevantamento.get_grau_parentesco(dependencia) == 5:
            return (dependencia.dependente.get_grau_parentesco_display())[0:15]
        return ""


class DependenteRequisitado(Dependente):

    def query(self):
        servidores = ServidorRequisitado.requisitados(
            self.folha, self.get_data_referencia(), self._mes_referencia
        )
        if self._importacao_completa:
            return DependenteRh.objects.filter(
                Q(tipo=5)
                & Q(dependente__grau_parentesco__in=(1, 3))
                & Q(dependente__servidor__ativo=True)
            )
        else:
            return Dependencia.objects.filter(
                Q(tipo=5)
                & Q(dependente__grau_parentesco__in=(1, 3))
                & Q(dependente__servidor__ativo=True)
                & Q(
                    dependente__data_alteracao__month=self._mes_referencia,
                    dependente__data_alteracao__year=self._ano_referencia,
                )
                & Q(dependente__servidor__pk__in=servidores)
            )


class Unidade(Igeprev):

    dados_unidade = None

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(Unidade, self).__init__(**conf)

    def conf(self, **conf):
        super(Unidade, self).conf(**conf)
        self.dados_unidade = DadosUnidade(
            data_referencia=self.get_data_referencia(),
            data_referencia_inicio=self.get_data_referencia_inicio(),
            importacao_completa=self._importacao_completa,
        )

    def query(self):
        return Lotacao.objects.filter()

    def add_registro(self, lotacao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            ddd, telefone = self.dados_unidade.get_telefone(lotacao)
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    poder=DadosUnidade.get_poder(lotacao),
                    orgao=self.get_orgao(),
                    nome=DadosUnidade.get_nome(lotacao),
                    codigo=DadosUnidade.get_codigo(lotacao),
                    sigla=DadosUnidade.get_sigla(lotacao),
                    bairro=self.dados_unidade.get_bairro(
                        objeto=lotacao, label="bairro", linha="6"
                    ),
                    municipio=self.dados_unidade.get_municipio(
                        objeto=lotacao, label="municipio", linha="7"
                    ),
                    uf=self.dados_unidade.get_uf(objeto=lotacao, label="uf", linha="8"),
                    cep=self.dados_unidade.get_cep(
                        objeto=lotacao, label="cep", linha="9"
                    ),
                    tipo_logradouro=self.dados_unidade.get_tipo_logradouro(
                        objeto=lotacao, label="tipo_logradouro", linha="10"
                    ),
                    logradouro=self.dados_unidade.get_logradouro(
                        objeto=lotacao, label="logradouro", linha="11"
                    ),
                    quadra=self.dados_unidade.get_quadra(
                        objeto=lotacao, label="quadra", linha="12"
                    ),
                    lote=self.dados_unidade.get_lote(
                        objeto=lotacao, label="lote", linha="13"
                    ),
                    numero=self.dados_unidade.get_numero(
                        objeto=lotacao, label="numero", linha="14"
                    ),
                    complemento=self.dados_unidade.get_complemento(
                        objeto=lotacao, label="complemento", linha="15"
                    ),
                    ddd=ddd,
                    telefone=telefone,
                )
            )
        except Exception as err:
            log.exception(err)
