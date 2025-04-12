# -*- coding: utf-8 -*-

import codecs
import os
from datetime import datetime

from django.conf import settings
from django.db.models import Q

from contrib.utils import DateUtils, getLogger, user_from_person
from rh.const import ESTADO_CIVIL_CHOICES, GRAU_INSTRUCAO_CHOICES
from rh.constants_functional_situations import (
    FUNCTIONAL_STATE_INDEX_STR_TO_INT,
    SITUACAO_FUNCIONAL,
)
from rh.gfp.models import (
    BankingEmployeeTypePayroll,
    EstruturaTabelaSalarial,
    Evento,
    FolhaEvento,
)
from rh.gfp.previdencia import Registro
from rh.gfp.previdencia.arquivo import (
    Afastamento,
    Cargo,
    Dependente,
    Orgao,
    Remuneracao,
    Servidor,
    Unidade,
)
from rh.gfp.previdencia.igeprev import (
    DadosAfastamento,
    DadosCargo,
    DadosOrgao,
    DadosServidor,
    DadosUnidade,
    Igeprev,
)
from rh.models import Cargo as CargoRh
from rh.models import PessoaFisica
from rh.models import UnidadeAdministrativa
from rh.pensao.models import PensaoFolhaEvento
from standard.models import Choice

log = getLogger(__name__)

ENCODING = "iso-8859-1"


unit_id_code = DadosUnidade.get_codigo(
    UnidadeAdministrativa.objects.filter(
        pessoa_juridica__cnpj="01786078000146",
        nome__icontains="PROCURADORIA GERAL DE JUSTI",
        codigo_igeprev=991,
    ).first()
)


class OrgaosSisprev(Orgao):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(OrgaosSisprev, self).__init__(**conf)

    def query(self):
        return UnidadeAdministrativa.objects.filter(
            Q(orgaogeral_ptr__lotacao=None) & ~Q(pessoa_juridica=None)
        ).exclude(poder=None)

    def add_registro(self, unidade_administrativa):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            endereco = None
            fone_fax = ""
            fone_institucional = ""
            fone_fax__resp = ""
            fone_trabalho_resp = ""
            responsavel = None
            if unidade_administrativa.pessoa_juridica.address.exists():
                endereco = unidade_administrativa.pessoa_juridica.address.latest("pk")
            if unidade_administrativa.responsavel:
                responsavel = unidade_administrativa.responsavel
                if unidade_administrativa.responsavel.phone.exists():
                    if unidade_administrativa.responsavel.phone.filter(
                        tipo_telefone=3
                    ).exists():
                        fone_fax__resp = (
                            unidade_administrativa.responsavel.phone.filter(
                                tipo_telefone=3
                            )
                            .latest("pk")
                            .numero
                        )
                    if unidade_administrativa.responsavel.phone.filter(
                        tipo_telefone=2
                    ).exists():
                        fone_trabalho_resp = (
                            unidade_administrativa.responsavel.phone.filter(
                                tipo_telefone=2
                            )
                            .latest("pk")
                            .numero
                        )

            if unidade_administrativa.pessoa_juridica.phone.exists():
                if unidade_administrativa.pessoa_juridica.phone.filter(
                    tipo_telefone=1
                ).exists():
                    fone_institucional = (
                        unidade_administrativa.pessoa_juridica.phone.filter(
                            tipo_telefone=5
                        ).last()
                    )
                if unidade_administrativa.pessoa_juridica.phone.filter(
                    tipo_telefone=3
                ).exists():
                    fone_fax = unidade_administrativa.pessoa_juridica.phone.filter(
                        tipo_telefone=4
                    ).last()
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=DadosOrgao.get_codigo(unidade_administrativa),
                    poder=DadosOrgao.get_poder(unidade_administrativa),
                    razao_social=DadosOrgao.get_razao(unidade_administrativa),
                    nome_fantasia=DadosOrgao.get_nome(unidade_administrativa),
                    cnpj=DadosOrgao.get_cnpj(unidade_administrativa),
                    logradouro=endereco.logradouro if endereco else "",
                    bairro=endereco.bairro if endereco else "",
                    cep=endereco.cep if endereco else "",
                    uf=(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio
                        else ""
                    ),
                    cidade=str(endereco.municipio) if endereco else "",
                    numero=endereco.numero if endereco else "",
                    complemento=endereco.complemento if endereco else "",
                    telefone=fone_institucional.numero if fone_institucional else "",
                    fax=fone_fax.numero if fone_fax else "",
                    email=unidade_administrativa.email,
                    site="",
                    resp_nome=responsavel.nome if responsavel else "",
                    resp_telefone=fone_trabalho_resp,
                    resp_fax=fone_fax__resp,
                    resp_email=responsavel.email_institucional if responsavel else "",
                    resp_cargo="",
                    codigo=DadosOrgao.get_codigo(unidade_administrativa),
                )
            )
        except Exception as err:
            log.exception(err)


class UnidadeSisprev(Unidade):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(UnidadeSisprev, self).__init__(**conf)

    def add_registro(self, lotacao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=DadosUnidade.get_codigo(lotacao),
                    nome=str(DadosUnidade.get_nome(lotacao)),
                    identificador_orgao=unit_id_code,
                    codigo=str(DadosUnidade.get_codigo(lotacao)),
                    sigla=str(DadosUnidade.get_sigla(lotacao)),
                )
            )
        except Exception as err:
            log.exception(err)


class LotacoesSisprev(UnidadeSisprev):

    _encoding = ENCODING

    def add_registro(self, lotacao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=DadosUnidade.get_codigo(lotacao),
                    nome=str(DadosUnidade.get_nome(lotacao)),
                    identificador_unidade=DadosUnidade.get_codigo(lotacao),
                )
            )
        except Exception as err:
            log.exception(err)


class CargosSisprev(Cargo):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(CargosSisprev, self).__init__(**conf)

    def query(self):
        return CargoRh.objects.filter(tipo_lei_cargo__in=("EF", "FC", "CM", "AC"))

    def add_registro(self, cargo):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            classificacao = "E"
            if cargo.tipo_lei_cargo == "FC":
                classificacao = "F"
            elif cargo.tipo_lei_cargo == "CM":
                classificacao = "C"
            acumulacao = ""
            cargo_quadro = DadosCargo.get_cargo_quadro(cargo)
            if cargo_quadro:
                if cargo_quadro.health:
                    acumulacao = 2
                elif cargo_quadro.teacher:
                    acumulacao = 3
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=DadosCargo.get_codigo(cargo),
                    nome=str(cargo_quadro),
                    codigo_cbo=cargo.current_config.cbo,
                    identificador_orgao=unit_id_code,
                    aposentadoria=(2 if cargo.indicativo == "M" else 5),
                    acumulacao="",
                    tipo_cargo=(2 if cargo_quadro and cargo_quadro.military else 1),
                    classificacao=classificacao,
                    carga_horaria=(cargo_quadro.carga_horaria if cargo_quadro else 40),
                )
            )
        except Exception as err:
            log.exception(err)


class FontePagadoraSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(FontePagadoraSisprev, self).__init__(**conf)

    def query(self):
        return UnidadeAdministrativa.objects.filter(
            pessoa_juridica__cnpj="01786078000146",
            nome__icontains="PROCURADORIA GERAL DE JUSTI",
            codigo_igeprev=991,
        )

    def add_registro(self, unidade_administrativa):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=DadosUnidade.get_codigo(unidade_administrativa),
                    nome=str(unidade_administrativa),
                    identificador_orgao=DadosUnidade.get_codigo(unidade_administrativa),
                )
            )
        except Exception as err:
            log.exception(err)


class TipoSituacaoFuncionalSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(TipoSituacaoFuncionalSisprev, self).__init__(**conf)

    def query(self):
        situations = {}
        for key in list(SITUACAO_FUNCIONAL.keys()):
            if not key == "NOT_FOUND":
                situations.update(
                    {
                        FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(
                            key
                        ): SITUACAO_FUNCIONAL.get(key)
                    }
                )
        return situations

    def add_registro(self, situacao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=situacao,
                    descricao=self.query()[situacao],
                )
            )
        except Exception as err:
            log.exception(err)


class EstadoCivilSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(EstadoCivilSisprev, self).__init__(**conf)

    def query(self):
        state = {}
        for key in ESTADO_CIVIL_CHOICES:
            state.update({key[0]: key[1]})
        return state

    def add_registro(self, situacao):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=situacao,
                    descricao=self.query()[situacao],
                )
            )
        except Exception as err:
            log.exception(err)


class EscolaridadeSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(EscolaridadeSisprev, self).__init__(**conf)

    def query(self):
        return GRAU_INSTRUCAO_CHOICES

    def add_registro(self, escolaridade):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=escolaridade,
                    descricao=GRAU_INSTRUCAO_CHOICES[escolaridade],
                )
            )
        except Exception as err:
            log.exception(err)


class TipoDependenciaSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(TipoDependenciaSisprev, self).__init__(**conf)

    def query(self):
        return [c for c in Choice.get_choices_for("rh", "TYPE_OF_DEPENDENCE")]

    def add_registro(self, dependencia):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=dependencia[0],
                    descricao=dependencia[1],
                )
            )
        except Exception as err:
            log.exception(err)


class QuadroMilitaresSisprev(CargosSisprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(QuadroMilitaresSisprev, self).__init__(**conf)

    def query(self):
        return (
            super(QuadroMilitaresSisprev, self).query().filter(quadros__military=True)
        )

    def add_registro(self, cargo):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=cargo.pk,
                    descricao=str(cargo),
                )
            )
        except Exception as err:
            log.exception(err)


class PessoasSisprev(Servidor):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(PessoasSisprev, self).__init__(**conf)

    def query(self):
        return PessoaFisica.objects.filter(
            pk__in=super(PessoasSisprev, self).query().values("pessoa_fisica__pk")
        )

    def add_registro(self, pessoa_fisica):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            endereco = None
            fone_residencial = ""
            fone_celular = ""
            fone_trabalho = ""
            if pessoa_fisica.address.exists():
                endereco = pessoa_fisica.address.latest("pk")
            if pessoa_fisica.phone.exists():
                if pessoa_fisica.phone.filter(tipo_telefone=1).exists():
                    fone_residencial = (
                        pessoa_fisica.phone.filter(tipo_telefone=1).latest("pk").numero
                    )
                if pessoa_fisica.phone.filter(tipo_telefone=3).exists():
                    fone_celular = (
                        pessoa_fisica.phone.filter(tipo_telefone=3).latest("pk").numero
                    )
                if pessoa_fisica.phone.filter(tipo_telefone=2).exists():
                    fone_trabalho = (
                        pessoa_fisica.phone.filter(tipo_telefone=2).latest("pk").numero
                    )
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=pessoa_fisica.pk,
                    cpf=pessoa_fisica.cpf,
                    nome=str(pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        pessoa_fisica.data_nascimento
                    ),
                    sexo=pessoa_fisica.sexo,
                    cep=endereco.cep if endereco else "",
                    logradouro=endereco.logradouro if endereco else "",
                    complemento=endereco.complemento if endereco else "",
                    bairro=endereco.bairro if endereco else "",
                    numero=endereco.numero if endereco else "",
                    uf=(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio
                        else ""
                    ),
                    cidade=str(endereco.municipio) if endereco else "",
                    fone_residencial=fone_residencial,
                    fone_celular=fone_celular,
                    fone_trabalho=fone_trabalho,
                    email_1=pessoa_fisica.email_institucional,
                    email_2=(
                        user_from_person(pessoa_fisica).email
                        if user_from_person(pessoa_fisica)
                        else ""
                    ),
                    mae=pessoa_fisica.nome_mae,
                    pai=pessoa_fisica.nome_pai,
                    estado_civil=pessoa_fisica.estado_civil,
                    identificador_escolaridade=pessoa_fisica.grau_instrucao,
                    doenca_incapacitante="verificar com rh como preencher",
                    portador_molestia=(0 if hasattr(pessoa_fisica, "molestia") else 1),
                    nacionalidade=pessoa_fisica.nacionalidade,
                    naturalidade_uf=(
                        str(pessoa_fisica.municipio_naturalidade.estado.sigla)
                        if pessoa_fisica.municipio_naturalidade
                        else ""
                    ),
                    naturalidade_cidade=str(pessoa_fisica.municipio_naturalidade),
                    pis_pasep=pessoa_fisica.pis_pasep,
                    rg_numero=pessoa_fisica.rg,
                    rg_orgao=pessoa_fisica.rg_orgao,
                    rg_uf=pessoa_fisica.rg_uf.sigla,
                    rg_data_expedicao=DateUtils.date_to_str(
                        pessoa_fisica.rg_data_expedicao
                    ),
                    ctps_numero=(
                        pessoa_fisica.ctps.ctps_numero if pessoa_fisica.ctps else ""
                    ),
                    ctps_serie=(
                        pessoa_fisica.ctps.ctps_series if pessoa_fisica.ctps else ""
                    ),
                    ctps_uf=(
                        pessoa_fisica.ctps.estado_expedicao.sigla
                        if pessoa_fisica.ctps and pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    ctps_data_emissao=(
                        DateUtils.date_to_str(pessoa_fisica.ctps.data_expedicao)
                        if pessoa_fisica.ctps and pessoa_fisica.ctps.data_expedicao
                        else ""
                    ),
                    ctps_local_expedicao=(
                        pessoa_fisica.ctps.estado_expedicao.sigla
                        if pessoa_fisica.ctps and pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    titulo_eleitoral_numero=(
                        pessoa_fisica.voter.numero if pessoa_fisica.voter else ""
                    ),
                    titulo_eleitoral_zona=(
                        pessoa_fisica.voter.voter_zone.valor
                        if pessoa_fisica.voter and pessoa_fisica.voter.voter_zone
                        else ""
                    ),
                    titulo_eleitoral_secao=(
                        pessoa_fisica.voter.voter_section.valor
                        if pessoa_fisica.voter and pessoa_fisica.voter.voter_section
                        else ""
                    ),
                    titulo_eleitoral_uf=(
                        pessoa_fisica.voter.estado_expedicao.sigla
                        if pessoa_fisica.voter and pessoa_fisica.voter.estado_expedicao
                        else ""
                    ),
                    observacoes="",
                    certidao_nascimento="",
                    certidao_nascimento_livro="",
                    certidao_nascimento_folha="",
                    certidao_casamento="",
                    certidao_casamento_livro="",
                    certidao_casamento_folha="",
                    cnh_numero=pessoa_fisica.cnh.numero if pessoa_fisica.cnh else "",
                    cnh_data_emissao=(
                        DateUtils.date_to_str(pessoa_fisica.cnh.data_expedicao)
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.data_expedicao
                        else ""
                    ),
                    cnh_data_validade=(
                        DateUtils.date_to_str(pessoa_fisica.cnh.data_validade)
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.data_validade
                        else ""
                    ),
                    cnh_emissor=(
                        pessoa_fisica.cnh.estado_expedicao.sigla
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.estado_expedicao
                        else ""
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class SeguradosSisprev(Servidor):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(SeguradosSisprev, self).__init__(**conf)

    def add_registro(self, servidor):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            posse_atual = self.dados_servidor.get_posse_atual(servidor)
            identificador_categoria = 1
            if posse_atual.quadro.cargo.tipo_lei_cargo == "EF" or servidor.requested:
                identificador_categoria = 1
            elif posse_atual.quadro.cargo.tipo_lei_cargo in ("CM", "FC"):
                identificador_categoria = 4
            # identificador_situacao_funcional_anterior = ''

            sf_atual = ""
            if servidor.historico_situacao_funcional.filter(
                situacao=servidor.situacao_funcional_cache
            ).exists():
                sf_atual = servidor.historico_situacao_funcional.filter(
                    situacao=servidor.situacao_funcional_cache
                ).latest("data_inicio")
            sf_anterior = ""
            if (
                sf_atual
                and servidor.historico_situacao_funcional.filter(
                    data_inicio__lte=sf_atual.data_inicio
                ).exists()
            ):
                sf_anterior = servidor.historico_situacao_funcional.filter(
                    data_inicio__lte=sf_atual.data_inicio
                ).latest("data_inicio")
            workplace = None
            if servidor.get_workplace_only().exists():
                workplace = servidor.get_workplace_only().latest("pk").lotacao
            elif servidor.work_assignment.exists():
                workplace = servidor.work_assignment.latest("pk").lotacao
            else:
                workplace = servidor._raw_locations(option=1).latest("pk").lotacao

            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    # identificador=servidor.pessoa_fisica.cpf,
                    identificador=DadosServidor.get_registry_origin(servidor),
                    identificador_pessoa=servidor.pessoa_fisica.pk,
                    identificador_categoria=identificador_categoria,
                    matricula=DadosServidor.get_registry_origin(servidor),
                    identificador_cargo=DadosCargo.get_codigo(posse_atual.quadro.cargo),
                    identificador_orgao=unit_id_code,
                    identificador_unidade=DadosUnidade.get_codigo(workplace),
                    identificador_lotacao=DadosUnidade.get_codigo(workplace),
                    identificador_unidade_origem="",
                    identificador_lotacao_origem="",
                    data_admissao=DateUtils.date_to_str(posse_atual.data_posse),
                    identificador_fonte_pagadora=unit_id_code,
                    excluido_exonerado=str("S" if not servidor.ativo else "N"),
                    data_exclusao=(
                        DateUtils.date_to_str(posse_atual.data_desligamento)
                        if not servidor.ativo and posse_atual.data_desligamento
                        else ""
                    ),
                    motivo_exclusao=(
                        posse_atual.desligamento.get_tipo_desligamento_display()
                        if not servidor.ativo and posse_atual.data_desligamento
                        else ""
                    ),
                    identificador_situacao_funcional=FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(
                        servidor.situacao_funcional_cache
                    ),
                    data_situacao_funcional=(
                        DateUtils.date_to_str(sf_atual.data_inicio) if sf_atual else ""
                    ),
                    data_obito=(
                        DateUtils.date_to_str(servidor.pessoa_fisica.data_obito)
                        if servidor.pessoa_fisica.data_obito
                        else ""
                    ),
                    fundo_previdenciario=str(
                        "PF"
                        if servidor.data_exercicio
                        >= datetime(year=2012, month=6, day=1).date()
                        else "PP"
                    ),
                    graduacao_militar="",
                    data_inicio_militar="",
                    identificador_quadro_militar="",
                    identificador_situacao_funcional_anterior=str(
                        FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(sf_anterior)
                        if sf_anterior
                        else ""
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class SeguradosCedidosSisprev(Afastamento):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(SeguradosCedidosSisprev, self).__init__(**conf)

    def query(self):
        self._importacao_completa = True
        return (
            super(SeguradosCedidosSisprev, self)
            .query()
            .filter(~Q(afastamento__afastamentooutroorgao=None))
        )

    def add_registro(self, afastamento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=afastamento.servidor.pessoa_fisica.cpf,
                    identificador_cargo=DadosCargo.get_codigo(
                        self.dados_servidor.get_posse_atual(
                            afastamento.servidor
                        ).quadro.cargo
                    ),
                    identificador_orgao_origem=unit_id_code,
                    identificador_orgao_cedido=DadosUnidade.get_codigo(
                        afastamento.instancia_modelo.orgao
                    ),
                    data_inicio=DadosAfastamento.get_data_inicio(afastamento),
                    data_fim=DadosAfastamento.get_data_fim(afastamento),
                    onus="N" if afastamento.instancia_modelo.onus == 1 else "S",
                    observacao="",
                )
            )
        except Exception as err:
            log.exception(err)


class PessoasDependentesSisprev(Dependente):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(PessoasDependentesSisprev, self).__init__(**conf)

    def query(self):
        self._importacao_completa = True
        return PessoaFisica.objects.filter(
            pk__in=super(PessoasDependentesSisprev, self)
            .query()
            .values("dependente__pessoa_fisica")
        )

    def add_registro(self, pessoa_fisica):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            endereco = None
            fone_residencial = ""
            fone_celular = ""
            fone_trabalho = ""
            if pessoa_fisica.address.exists():
                endereco = pessoa_fisica.address.latest("pk")
            if pessoa_fisica.phone.exists():
                if pessoa_fisica.phone.filter(tipo_telefone=1).exists():
                    fone_residencial = (
                        pessoa_fisica.phone.filter(tipo_telefone=1).latest("pk").numero
                    )
                if pessoa_fisica.phone.filter(tipo_telefone=3).exists():
                    fone_celular = (
                        pessoa_fisica.phone.filter(tipo_telefone=3).latest("pk").numero
                    )
                if pessoa_fisica.phone.filter(tipo_telefone=2).exists():
                    fone_trabalho = (
                        pessoa_fisica.phone.filter(tipo_telefone=2).latest("pk").numero
                    )
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=pessoa_fisica.pk,
                    cpf=pessoa_fisica.cpf,
                    nome=str(pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        pessoa_fisica.data_nascimento
                    ),
                    sexo=pessoa_fisica.sexo,
                    cep=endereco.cep if endereco else "",
                    logradouro=endereco.logradouro if endereco else "",
                    complemento=endereco.complemento if endereco else "",
                    bairro=endereco.bairro if endereco else "",
                    numero=endereco.numero if endereco else "",
                    uf=(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio
                        else ""
                    ),
                    cidade=str(endereco.municipio) if endereco else "",
                    fone_residencial=fone_residencial,
                    fone_celular=fone_celular,
                    fone_trabalho=fone_trabalho,
                    email_1=pessoa_fisica.email_institucional,
                    email_2="",
                    nome_mae=pessoa_fisica.nome_mae,
                    nome_pai=pessoa_fisica.nome_pai,
                    estado_civil=pessoa_fisica.estado_civil,
                    identificador_escolaridade=pessoa_fisica.grau_instrucao,
                    portador_incapacitante="verificar com rh como preencher",
                    portador_molestia=(0 if hasattr(pessoa_fisica, "molestia") else 1),
                    nacionalidade=pessoa_fisica.nacionalidade,
                    naturalidade_uf=(
                        str(pessoa_fisica.municipio_naturalidade.estado.sigla)
                        if pessoa_fisica.municipio_naturalidade
                        else ""
                    ),
                    naturalidade_cidade=str(pessoa_fisica.municipio_naturalidade),
                    pis_pasep=pessoa_fisica.pis_pasep,
                    rg_numero=pessoa_fisica.rg,
                    rg_orgao=pessoa_fisica.rg_orgao,
                    rg_uf=pessoa_fisica.rg_uf.sigla if pessoa_fisica.rg_uf else "",
                    rg_data_expedicao=(
                        DateUtils.date_to_str(pessoa_fisica.rg_data_expedicao)
                        if pessoa_fisica.rg_data_expedicao
                        else ""
                    ),
                    ctps_numero=(
                        pessoa_fisica.ctps.ctps_numero if pessoa_fisica.ctps else ""
                    ),
                    ctps_serie=(
                        pessoa_fisica.ctps.ctps_serie if pessoa_fisica.ctps else ""
                    ),
                    ctps_uf=(
                        pessoa_fisica.ctps.estado_expedicao.sigla
                        if pessoa_fisica.ctps and pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    ctps_data_emissao=(
                        DateUtils.date_to_str(pessoa_fisica.ctps.data_expedicao)
                        if pessoa_fisica.ctps
                        else ""
                    ),
                    ctps_local_expedicao=(
                        pessoa_fisica.ctps.estado_expedicao.sigla
                        if pessoa_fisica.ctps and pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    titulo_eleitoral_numero=(
                        pessoa_fisica.voter.numero if pessoa_fisica.voter else ""
                    ),
                    titulo_eleitoral_zona=(
                        pessoa_fisica.voter.voter_zone.valor
                        if pessoa_fisica.voter and pessoa_fisica.voter.voter_zone
                        else ""
                    ),
                    titulo_eleitoral_secao=(
                        pessoa_fisica.voter.voter_section
                        if pessoa_fisica.voter and pessoa_fisica.voter.voter_section
                        else ""
                    ),
                    titulo_eleitoral_uf=(
                        pessoa_fisica.voter.estado_expedicao.sigla
                        if pessoa_fisica.voter and pessoa_fisica.voter.estado_expedicao
                        else ""
                    ),
                    observacoes="",
                    certidao_nascimento="",
                    certidao_nascimento_livro="",
                    certidao_nascimento_folha="",
                    certidao_casamento="",
                    certidao_casamento_livro="",
                    certidao_casamento_folha="",
                    cnh_numero=pessoa_fisica.cnh.numero if pessoa_fisica.cnh else "",
                    cnh_data_emissao=(
                        DateUtils.date_to_str(pessoa_fisica.cnh.data_expedicao)
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.data_expedicao
                        else ""
                    ),
                    cnh_data_validade=(
                        DateUtils.date_to_str(pessoa_fisica.cnh.data_validade)
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.data_validade
                        else ""
                    ),
                    cnh_emissor=(
                        pessoa_fisica.cnh.estado_expedicao.sigla
                        if pessoa_fisica.cnh and pessoa_fisica.cnh.estado_expedicao
                        else ""
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class DependentesSisprev(Dependente):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(DependentesSisprev, self).__init__(**conf)

    def query(self):
        self._importacao_completa = True
        return super(DependentesSisprev, self).query()

    def add_registro(self, dependencia):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            condicao_dependente = "N"
            if dependencia.estudante:
                condicao_dependente = "U"
            elif dependencia.dependente.capacidade == 1:
                condicao_dependente = "C"
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=dependencia.pk,
                    identificador_pessoa_dependente=dependencia.dependente.pessoa_fisica.pk,
                    identificador_pessoa_responsavel=dependencia.dependente.responsavel.pk,
                    identificador_tipo_dependencia=dependencia.tipo,
                    data_inicio=DateUtils.date_to_str(dependencia.data_inicio),
                    data_fim=(
                        DateUtils.date_to_str(dependencia.data_fim)
                        if dependencia.data_fim
                        else ""
                    ),
                    condicao_dependente=str(condicao_dependente),
                    codigo_doenca_invalidez="",
                    data_laudo_invalidez="",
                    irrf=("S" if dependencia.tipo == 1 else "N"),
                    motivo_inicio_dependencia=(
                        str(
                            dependencia.dependente.get_motivo_inicio_dependencia_display()
                        )
                        if dependencia.dependente.motivo_inicio_dependencia
                        else ""
                    ),
                    tipo_dependencia=dependencia.tipo,
                )
            )
        except Exception as err:
            log.exception(err)


class EventosRubricasSisprev(SeguradosSisprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(EventosRubricasSisprev, self).__init__(**conf)

    def query(self):
        return (
            Evento.objects.filter(
                Q(em_plano__pessoa_juridica__cnpj="25091307000176")
                | Q(
                    pk__in=Evento.objects.filter(
                        em_plano__pessoa_juridica__cnpj="25091307000176"
                    )
                    .distinct()
                    .values("configs__focuses_on__pk")
                )
            )
            .filter(
                Q(configs__start_validity__lte=self._data_referencia_inicio)
                & (
                    Q(configs__end_validity__isnull=True)
                    | Q(configs__end_validity__gte=self._data_referencia)
                )
            )
            .distinct()
        )

    def compoe_remuneracao_conbribuicao(self, evento):
        return (
            "S"
            if evento.aplica_em.all()
            .filter(
                event__genre_event__genre_number__in=["900", "901", "902", "905", "906"]
            )
            .exists()
            else "N"
        )

    def incide_irrf(self, evento):
        return (
            "S"
            if evento.aplica_em.all()
            .filter(focuses_on__genre_event__genre_number__in=["991", "992", "999"])
            .exists()
            else "N"
        )

    def compoe_remuneracao_cargo_efetivo(self, evento):
        return (
            "S"
            if evento.genre_event and evento.genre_event.config_transparency == 25
            else "N"
        )

    def add_registro(self, evento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            lei = ""
            if evento.publicacao:
                lei = "%%" % (evento.publicacao.numero, evento.publicacao.ano)
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=evento.numero,
                    nome=str(evento),
                    abreviatura=str(evento),
                    lei=lei,
                    compoe_remuneracao_contribuicao=self.compoe_remuneracao_conbribuicao(
                        evento
                    ),
                    compoe_remuneracao_cargo_efetivo=self.compoe_remuneracao_cargo_efetivo(
                        evento
                    ),
                    proporcionaliza="",
                    incide_irrf=self.incide_irrf(evento),
                    incide_margem_consignavel="S" if evento.aplica_consignavel else "N",
                    tipo_evento=("C" if evento.tipo == "P" else "D"),
                    tipo_calculo_evento="Automatico" if evento.automatico else "Manual",
                    formula="",
                )
            )
        except Exception as err:
            log.exception(err)


class BancosSisprev(PessoasSisprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(BancosSisprev, self).__init__(**conf)

    def query(self):
        return BankingEmployeeTypePayroll.objects.filter(
            type_of_payroll__principal=True,
            person__pk__in=super(BancosSisprev, self).query().values("pk"),
        )

    def add_registro(self, banking_employee_payroll):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador_pessoa=banking_employee_payroll.person.pk,
                    forma_pagamento=1,
                    banco=banking_employee_payroll.banking_person.banco.numero,
                    agencia=banking_employee_payroll.banking_person.banco.agencia,
                    dv_agencia=banking_employee_payroll.banking_person.banco.dv_agencia,
                    conta=banking_employee_payroll.banking_person.banco.conta,
                    dv_conta=banking_employee_payroll.banking_person.banco.dv_conta,
                    op="",
                    representante_legal="N",
                )
            )
        except Exception as err:
            log.exception(err)


class CargosOcupadosSisprev(SeguradosSisprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(CargosOcupadosSisprev, self).__init__(**conf)

    def add_registro(self, servidor):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            posse_atual = self.dados_servidor.get_posse_atual(servidor)
            classificacao = "E"
            if posse_atual.quadro.cargo.tipo_lei_cargo == "FC":
                classificacao = "F"
            elif posse_atual.quadro.cargo.tipo_lei_cargo in ("CM", "AC"):
                classificacao = "C"
            data_inicio = ""
            data_fim = ""
            if posse_atual:
                data_inicio = DateUtils.date_to_str(posse_atual.data_exercicio)
                data_fim = (
                    DateUtils.date_to_str(posse_atual.data_desligamento)
                    if posse_atual.data_desligamento
                    else ""
                )
            referencia = ""
            nivel = ""
            classe = ""
            padrao = ""
            progressao = servidor.movimentacaopessoal_set.filter(
                ~Q(movimentacaoprogressao=None)
            )
            if progressao.exists() and not servidor.member_type_by_possession:
                progressao = progressao.latest(
                    "movimentacaoprogressao__data_referencia_inicial"
                ).movimentacaoprogressao
                referencia = str(progressao.referencia_nivel2d)
                nivel = str(progressao.referencia_nivel2d.vertical)
                classe = str(progressao.referencia_nivel2d.horizontal)
                padrao = str(progressao.referencia_nivel2d.ordem)
            else:
                salaries = EstruturaTabelaSalarial.salarios(
                    posse_atual.quadro.cargo,
                    self._data_referencia_inicio,
                    self._data_referencia,
                )
                if len(salaries) > 0:
                    salary = salaries[0]
                    referencia = (
                        str(salary[1].referencia_nivel2d)
                        if salary[1].referencia_nivel2d
                        else ""
                    )
                    nivel = (
                        str(salary[1].referencia_nivel2d.vertical)
                        if salary[1].referencia_nivel2d.vertical
                        else ""
                    )
                    classe = (
                        str(salary[1].referencia_nivel2d.horizontal)
                        if salary[1].referencia_nivel2d.horizontal
                        else ""
                    )
                    padrao = (
                        str(salary[1].referencia_nivel2d.ordem)
                        if salary[1].referencia_nivel2d.ordem
                        else ""
                    )

            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    # identificador_segurado=servidor.pessoa_fisica.cpf,
                    identificador_segurado=DadosServidor.get_registry_origin(servidor),
                    identificador_cargo=DadosCargo.get_codigo(posse_atual.quadro.cargo),
                    # identificador_cargo=posse_atual.quadro.cargo.pk,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    cargo_atual=1,
                    referencia=referencia,
                    nivel=nivel,
                    classe=classe,
                    padrao=padrao,
                    classificacao_cargo=classificacao,
                )
            )
        except Exception as err:
            log.exception(err)


class FinanceiroSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(FinanceiroSisprev, self).__init__(**conf)

    def query(self):
        return (
            FolhaEvento.objects.filter(
                (
                    Q(evento__em_plano__pessoa_juridica__cnpj="25091307000176")
                    | Q(
                        evento__pk__in=Evento.objects.filter(
                            em_plano__pessoa_juridica__cnpj="25091307000176"
                        )
                        .distinct()
                        .values("configs__focuses_on__pk")
                    )
                )
                & Q(
                    folha__periodo__mes=(
                        13
                        if self.get_data_referencia_inicio().month == 12
                        else self.get_data_referencia_inicio().month
                    )
                )
                & Q(folha__periodo__ano=self.get_data_referencia_inicio().year)
            )
            .filter(
                Q(evento__configs__start_validity__lte=self._data_referencia_inicio)
                & (
                    Q(evento__configs__end_validity__isnull=True)
                    | Q(evento__configs__end_validity__gte=self._data_referencia)
                )
            )
            .distinct()
            .order_by("servidor", "folha__periodo__mes")
        )

    def add_registro(self, folha_evento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            # GFP_TIPO_CALCULO = {
            #     1: 'PERCENTUAL', # P
            #     3: 'QUANTIDADE', # D
            #     2: 'VALOR BASE', # V
            #     4: 'LIVRE',
            #     5: 'QUANTIDADE/PERCENTUAL', # P
            # }
            referencia = "V"
            valor_referencia = ""
            if folha_evento.evento.tipo_calculo in (3, 5):
                referencia = "D"
                valor_referencia = (
                    folha_evento.evento.quantidade or folha_evento.evento.porcentagem
                )
            elif folha_evento.evento.tipo_calculo == 1:
                referencia = "P"
                valor_referencia = folha_evento.evento.porcentagem
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    # identificador_segurado=folha_evento.servidor.pessoa_fisica.cpf,
                    identificador_segurado=DadosServidor.get_registry_origin(
                        folha_evento.servidor
                    ),
                    identificador_evento=folha_evento.evento.numero,
                    valor=float(folha_evento.valor),
                    remuneracao_total=(
                        "S" if folha_evento.evento.carater == 1 else "N"
                    ),
                    ano=folha_evento.reference_year,
                    mes=folha_evento.reference_month,
                    referencia=str(referencia),
                    valor_referencia=(
                        str(valor_referencia) if valor_referencia is not None else ""
                    ),
                    # numero_tipo_folha=unicode(folha_evento.folha.tipo_folha.numero),
                    # descricao_numero_tipo_folha=unicode(folha_evento.folha),
                    numero_tipo_folha=str(
                        Igeprev.get_sheet(
                            21
                            if folha_evento.evento.genre_event in ("901", "906")
                            else 1
                        )
                    ),
                    descricao_numero_tipo_folha=str(
                        Igeprev.get_description_sheet(
                            21
                            if folha_evento.evento.genre_event in ("901", "906")
                            else 1
                        )
                    ),
                )
            )
        except Exception as err:
            log.exception(err)


class PensoesAlimenticiasSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(PensoesAlimenticiasSisprev, self).__init__(**conf)

    def query(self):
        return PensaoFolhaEvento.objects.filter(
            ~Q(pensao__pensaoalimenticia=None)
            & Q(
                folha__periodo__mes=(
                    13
                    if self.get_data_referencia_inicio().month == 12
                    else self.get_data_referencia_inicio().month
                )
            )
            & Q(folha__periodo__ano=self.get_data_referencia_inicio().year)
        ).order_by("pensao__servidor", "folha__periodo__mes")

    def add_registro(self, pensao_folha_evento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            endereco = None
            fone_residencial = ""
            fone_celular = ""
            fone_trabalho = ""
            if pensao_folha_evento.pensao.pensionista.address.exists():
                endereco = pensao_folha_evento.pensao.pensionista.address.latest("pk")
            if pensao_folha_evento.pensao.pensionista.phone.exists():
                if pensao_folha_evento.pensao.pensionista.phone.filter(
                    tipo_telefone=1
                ).exists():
                    fone_residencial = (
                        pensao_folha_evento.pensao.pensionista.phone.filter(
                            tipo_telefone=1
                        )
                        .latest("pk")
                        .numero
                    )
                if pensao_folha_evento.pensao.pensionista.phone.filter(
                    tipo_telefone=3
                ).exists():
                    fone_celular = (
                        pensao_folha_evento.pensao.pensionista.phone.filter(
                            tipo_telefone=3
                        )
                        .latest("pk")
                        .numero
                    )
                if pensao_folha_evento.pensao.pensionista.phone.filter(
                    tipo_telefone=2
                ).exists():
                    fone_trabalho = (
                        pensao_folha_evento.pensao.pensionista.phone.filter(
                            tipo_telefone=2
                        )
                        .latest("pk")
                        .numero
                    )

            codigo_banco = ""
            numero_conta = ""
            digito_numero_conta = ""
            numero_agencia = ""
            digito_numero_agencia = ""
            if pensao_folha_evento.pensao.pensionista.bankings_employee_payroll.filter(
                banking_person__principal=True
            ).exists():
                banking = pensao_folha_evento.pensao.pensionista.bankings_employee_payroll.filter(
                    banking_person__principal=True
                ).first()
                codigo_banco = banking.banking_person.banco.numero
                numero_conta = banking.banking_person.banco.conta
                digito_numero_conta = banking.banking_person.banco.dv_conta
                numero_agencia = banking.banking_person.banco.agencia
                digito_numero_agencia = banking.banking_person.banco.dv_agencia

            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=pensao_folha_evento.pk,
                    nome=str(pensao_folha_evento.pensao.pensionista),
                    sexo=pensao_folha_evento.pensao.pensionista.sexo,
                    logradouro=endereco.logradouro if endereco else "",
                    bairro=endereco.bairro if endereco else "",
                    cep=endereco.cep if endereco else "",
                    email=pensao_folha_evento.pensao.pensionista.email_institucional,
                    fone_comercial=fone_trabalho,
                    fone_residencial=fone_residencial,
                    fone_celular=fone_celular,
                    data_nascimento=(
                        DateUtils.date_to_str(
                            pensao_folha_evento.pensao.pensionista.data_nascimento
                        )
                        if pensao_folha_evento.pensao.pensionista.data_nascimento
                        else ""
                    ),
                    cidade=str(endereco.municipio) if endereco else "",
                    uf=(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio
                        else ""
                    ),
                    nome_pai=pensao_folha_evento.pensao.pensionista.nome_pai,
                    nome_mae=pensao_folha_evento.pensao.pensionista.nome_mae,
                    identificador_estado_civil=pensao_folha_evento.pensao.pensionista.estado_civil,
                    identificador_escolaridade=pensao_folha_evento.pensao.pensionista.grau_instrucao,
                    cpf=pensao_folha_evento.pensao.pensionista.cpf,
                    rg_numero=pensao_folha_evento.pensao.pensionista.rg,
                    pis_pasep=pensao_folha_evento.pensao.pensionista.pis_pasep,
                    titulo_eleitoral=(
                        pensao_folha_evento.pensao.pensionista.voter.numero
                        if pensao_folha_evento.pensao.pensionista.voter
                        else ""
                    ),
                    titulo_eleitoral_zona=(
                        pensao_folha_evento.pensao.pensionista.voter.voter_zone.valor
                        if pensao_folha_evento.pensao.pensionista.voter
                        and pensao_folha_evento.pensao.pensionista.voter.voter_zone
                        else ""
                    ),
                    titulo_eleitoral_secao=(
                        pensao_folha_evento.pensao.pensionista.voter.voter_section
                        if pensao_folha_evento.pensao.pensionista.voter
                        and pensao_folha_evento.pensao.pensionista.voter
                        else ""
                    ),
                    naturalidade_cidade=str(
                        pensao_folha_evento.pensao.pensionista.municipio_naturalidade
                    ),
                    naturalidade_uf=(
                        str(
                            pensao_folha_evento.pensao.pensionista.municipio_naturalidade.estado.sigla
                        )
                        if pensao_folha_evento.pensao.pensionista.municipio_naturalidade
                        else ""
                    ),
                    ctps=(
                        pensao_folha_evento.pensao.pensionista.ctps.ctps_numero
                        if pensao_folha_evento.pensao.pensionista.ctps
                        else ""
                    ),
                    rg_orgao=pensao_folha_evento.pensao.pensionista.rg_orgao,
                    rg_uf=(
                        pensao_folha_evento.pensao.pensionista.rg_uf.sigla
                        if pensao_folha_evento.pensao.pensionista.rg_uf
                        else ""
                    ),
                    rg_data_expedicao=(
                        DateUtils.date_to_str(
                            pensao_folha_evento.pensao.pensionista.rg_data_expedicao
                        )
                        if pensao_folha_evento.pensao.pensionista.rg_data_expedicao
                        else ""
                    ),
                    ctps_serie=(
                        pensao_folha_evento.pensao.pensionista.ctps.ctps_serie
                        if pensao_folha_evento.pensao.pensionista.ctps
                        else ""
                    ),
                    ctps_uf=(
                        pensao_folha_evento.pensao.pensionista.ctps.estado_expedicao.sigla
                        if pensao_folha_evento.pensao.pensionista.ctps
                        and pensao_folha_evento.pensao.pensionista.ctps.estado_expedicao
                        else ""
                    ),
                    ctps_data_emissao=(
                        DateUtils.date_to_str(
                            pensao_folha_evento.pensao.pensionista.ctps.data_expedicao
                        )
                        if pensao_folha_evento.pensao.pensionista.ctps
                        else ""
                    ),
                    ctps_local_expedicao=(
                        pensao_folha_evento.pensao.pensionista.ctps.estado_expedicao.sigla
                        if pensao_folha_evento.pensao.pensionista.ctps
                        and pensao_folha_evento.pensao.pensionista.ctps.estado_expedicao
                        else ""
                    ),
                    numero_endereco=endereco.numero if endereco else "",
                    # identificador_segurado=pensao_folha_evento.pensao.servidor.pessoa_fisica.cpf,
                    identificador_segurado=DadosServidor.get_registry_origin(
                        pensao_folha_evento.pensao.servidor
                    ),
                    data_inicio=DateUtils.date_to_str(
                        pensao_folha_evento.pensao.data_inicio
                    ),
                    data_fim=(
                        DateUtils.date_to_str(pensao_folha_evento.pensao.data_fim)
                        if pensao_folha_evento.pensao.data_fim
                        else ""
                    ),
                    valor=pensao_folha_evento.pensao.valor,
                    formula_pensao="",
                    percentual="existe esta informacao??",
                    codigo_banco=codigo_banco,
                    numero_conta=numero_conta,
                    digito_numero_conta=digito_numero_conta,
                    numero_agencia=numero_agencia,
                    digito_numero_agencia=digito_numero_agencia,
                )
            )
        except Exception as err:
            log.exception(err)


class ContribuicoesMensalSisprev(Remuneracao):

    _encoding = ENCODING

    def __init__(self, **conf):
        self._total_base_value = 0
        self._total_employer_contribution = 0
        self._total_contribution = 0
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(ContribuicoesMensalSisprev, self).__init__(**conf)

    def query(self):
        return super(ContribuicoesMensalSisprev, self).query()

    def adiciona_corpo(self):
        super(ContribuicoesMensalSisprev, self).adiciona_corpo()
        filename = os.path.join(settings.CACHE_PATH, "contribuicaomensaltotal.csv")
        fd = codecs.open(filename, "a", self._encoding)
        # fd.write('total valor base|total contribuicao|total patronal|mes|ano\n')
        fd.write(
            "\n%s|%s|%s|%s|%s"
            % (
                self._total_base_value,
                self._total_contribution,
                self._total_employer_contribution,
                self.get_data_referencia().month,
                self.get_data_referencia().year,
            )
        )

    def add_registro(self, servidor):

        try:
            fe = FolhaEvento.objects.filter(
                contracheque__servidor=servidor,
                folha__pk=self.folha,
                folha__periodo__mes=self.get_data_referencia().month,
                folha__periodo__ano=self.get_data_referencia().year,
            )

            event_to_filter = ["900", "902", "905"]
            for sheet_event in fe.filter(
                evento__genre_event__genre_number__in=event_to_filter
            ):
                base_value = sheet_event.valor_base or 0
                contribution = sheet_event.value or 0
                # if contribution < 0:
                #     contribution = contribution * -1
                employer_contribution = sheet_event.employer_contribution or 0
                # if employer_contribution < 0:
                #     employer_contribution = employer_contribution * -1

                self._total_base_value += base_value
                self._total_contribution += contribution * -1
                self._total_employer_contribution += employer_contribution * -1
                self.regs.append(
                    Registro(
                        len(self.regs) + 1,
                        self._class_name,
                        apply_blank=False,
                        separator="ß",
                        identificador_segurado=DadosServidor.get_registry_origin(
                            servidor
                        ),
                        ano_folha=sheet_event.folha.periodo.ano,
                        mes_folha=sheet_event.folha.periodo.mes,
                        ano_direito=sheet_event.reference_year,
                        mes_direito=sheet_event.reference_month,
                        remuneracao_contribuicao=base_value,
                        contribuicao_previdenciaria_segurada=contribution,
                        contribuicao_previdenciaria_fonte_pagadora=employer_contribution,
                        identificador_fonte_pagadora=unit_id_code,
                        numero_tipo_folha=str(Igeprev.get_sheet(1)),
                        descricao_numero_tipo_folha=str(
                            Igeprev.get_description_sheet(1)
                        ),
                    )
                )

            event_to_filter = ["901", "906"]
            for sheet_event in fe.filter(
                evento__genre_event__genre_number__in=event_to_filter
            ):
                base_value = sheet_event.valor_base or 0
                contribution = sheet_event.value or 0
                # if contribution < 0:
                #     contribution = contribution * -1
                employer_contribution = sheet_event.employer_contribution or 0
                # if employer_contribution < 0:
                #     employer_contribution = employer_contribution * -1

                self._total_base_value += base_value
                self._total_contribution += contribution * -1
                self._total_employer_contribution += employer_contribution * -1
                if base_value or contribution or employer_contribution:
                    self.regs.append(
                        Registro(
                            len(self.regs) + 1,
                            self._class_name,
                            apply_blank=False,
                            separator="ß",
                            identificador_segurado=DadosServidor.get_registry_origin(
                                servidor
                            ),
                            ano_folha=sheet_event.folha.periodo.ano,
                            mes_folha=sheet_event.folha.periodo.mes,
                            ano_direito=sheet_event.reference_year,
                            mes_direito=sheet_event.reference_month,
                            remuneracao_contribuicao=base_value,
                            contribuicao_previdenciaria_segurada=contribution,
                            contribuicao_previdenciaria_fonte_pagadora=employer_contribution,
                            identificador_fonte_pagadora=unit_id_code,
                            numero_tipo_folha=str(Igeprev.get_sheet(21)),
                            descricao_numero_tipo_folha=str(
                                Igeprev.get_description_sheet(21)
                            ),
                        )
                    )
        except Exception as err:
            log.exception(err)


class ContribuicoesHomologacaoSisprev(ContribuicoesMensalSisprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        super(ContribuicoesHomologacaoSisprev, self).__init__(**conf)

    def query(self):
        return super(ContribuicoesHomologacaoSisprev, self).query().filter(ativo=True)

    def add_registro(self, servidor):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            """
            pensar em buscar as informações de remuneração de acordo com a FOLHA.
            """
            bruto, liquido, valor_base, contribuicao, patronal, valor_irrf = (
                self.dados_remuneracao.calculo(
                    servidor, self.folha, event_to_filter=["90500", "90000"]
                )
            )
            # log.debug(
            #     '\nSERVIDOR: %s \n remuneração contribuicao: %s \n remuneração bruta: %s \n valor liquido: (
            #        %s - %s - %s) = %s' % (
            #     servidor.matricula,
            #     valor_base,
            #     valor_base,
            #     valor_base, contribuicao, valor_irrf,
            #     (valor_base - contribuicao - valor_irrf)
            # ))
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    matricula=DadosServidor.get_registry_origin(servidor),
                    cpf=servidor.pessoa_fisica.cpf,
                    sexo=servidor.pessoa_fisica.sexo,
                    categoria="EFETIVO",
                    data_nascimento=DateUtils.date_to_str(
                        servidor.pessoa_fisica.data_nascimento
                    ),
                    remuneracao_contribuicao=valor_base,
                    # remuneracao_bruta=valor_base,
                    # remuneracao_liquida=valor_base - contribuicao - valor_irrf,
                    remuneracao_bruta="",
                    remuneracao_liquida="",
                    mes=self.get_data_referencia().month,
                    ano=self.get_data_referencia().year,
                    orgao=str(
                        UnidadeAdministrativa.objects.filter(
                            pessoa_juridica__cnpj="01786078000146",
                            nome__icontains="PROCURADORIA GERAL DE JUSTI",
                            codigo_igeprev=991,
                        ).first()
                    ),
                    poder=4,
                )
            )
        except Exception as err:
            log.exception(err)


class ContribuicoesHistoricoSisprev(Igeprev):

    _encoding = ENCODING

    def __init__(self, **conf):
        conf.update({"_set_header": False})
        if "class_name" not in conf:
            conf["class_name"] = self.__class__.__name__
        conf.update({"_save_on_demand": True})
        super(ContribuicoesHistoricoSisprev, self).__init__(**conf)

    def query(self):
        return (
            FolhaEvento.objects.filter(
                Q(folha__pk__lte=self.folha)
                & (
                    Q(evento__em_plano__pessoa_juridica__cnpj="25091307000176")
                    | Q(
                        evento__pk__in=Evento.objects.filter(
                            em_plano__pessoa_juridica__cnpj="25091307000176"
                        )
                        .distinct()
                        .values("configs__focuses_one__pk")
                    )
                )
            )
            .filter(
                Q(configs__start_validity__lte=self._data_referencia_inicio)
                & (
                    Q(configs__end_validity__isnull=True)
                    | Q(configs__end_validity__gte=self._data_referencia)
                )
            )
            .distinct()
            .values("pk")
        )

    def add_registro(self, folha_evento):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        try:
            folha_evento = FolhaEvento.objects.get(pk=folha_evento.get("pk"))
            self.write_feedback(
                message_progress="%s - %s"
                % (folha_evento.servidor.matricula, str(folha_evento))
            )
            base_value = folha_evento.valor_base or 0
            contribution = folha_evento.value or 0
            employer_contribution = folha_evento.employer_contribution or 0
            # if contribution < 0:
            #     contribution = contribution * -1
            # if folha_evento.folha.pk != self.folha:
            text = Registro(
                len(self.regs) + 1,
                self._class_name,
                apply_blank=False,
                separator="ß",
                # identificador_segurado=folha_evento.servidor.pessoa_fisica.cpf,
                identificador_segurado=DadosServidor.get_registry_origin(
                    folha_evento.servidor
                ),
                ano=folha_evento.folha.periodo.ano,
                mes=folha_evento.folha.periodo.mes,
                remuneracao_contribuicao=base_value,
                contribuicao_previdenciaria_segurado=contribution,
                contribuicao_previdenciaria_fonte_pagadora=employer_contribution,
                identificador_fonte_pagadora=unit_id_code,
                # numero_tipo_folha=unicode(folha_evento.folha.tipo_folha.numero),
                # descricao_numero_tipo_folha=unicode(folha_evento.folha.tipo_folha.titulo)
                numero_tipo_folha=str(
                    Igeprev.get_sheet(
                        21 if folha_evento.evento.genre_event in ("901", "906") else 1
                    )
                ),
                descricao_numero_tipo_folha=str(
                    Igeprev.get_description_sheet(
                        21 if folha_evento.evento.genre_event in ("901", "906") else 1
                    )
                ),
            )
            self.save_file(mode="a", text=str(text))
        except Exception as err:
            log.exception(err)
