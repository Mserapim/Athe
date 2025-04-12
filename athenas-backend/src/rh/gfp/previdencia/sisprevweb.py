# -*- coding: utf-8 -*-

import codecs
from email.mime import message
import os
from datetime import datetime
from zipfile import ZipFile

from django.conf import settings
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from contrib.utils import DateUtils, getLogger, user_from_person
from corregedoria.prontuary.api import employee
from rh.afastamento.models import BaseLicencaAfastamento
from rh.constants_functional_situations import FUNCTIONAL_STATE_INDEX_STR_TO_INT
from rh.gfp.febrabam import Protocol
from rh.gfp.models import (
    ContraCheque,
    Folha,
    FolhaEvento,
    MovimentacaoProgressao,
    Periodo,
    SocialSecurityContributionsReport,
)
from rh.gfp.previdencia import Registro
from rh.gfp.previdencia.igeprev import (
    DadosCargo,
    DadosServidor,
    DadosUnidade,
    Igeprev,
    IgeprevGenerator,
    feedback,
)
from rh.gfp.previdencia.layout_sisprevweb import SISPREV
from rh.models import BenefitMovement, Dependencia, Dependente, Servidor as ServidorRh
from rh.models import UnidadeAdministrativa
from rh.socialsecurity.models import EmploymentBond

log = getLogger(__name__)

ENCODING = "utf-8"


ORGAN = UnidadeAdministrativa.objects.filter(
    pessoa_juridica__cnpj="01786078000146",
    nome__icontains="PROCURADORIA GERAL DE JUSTI",
    codigo_igeprev=991,
).first()


class Sisprev(Protocol):
    """
    Classe base para construção dos arquivos do IGEPREV.
    Considera-se que todas informações são extraídas em função do mês e ano de referência.
    """

    _file_name = ""
    _class_name = ""
    _encoding = "utf-8"

    def __init__(self, **conf):
        Protocol.__init__(self)
        self.conf(**conf)
        self.delete_file()
        self.write_feedback(message_progress="Gerando arquivo %s" % self._file_name)
        self.body()

    def conf(self, **conf):
        self.year = conf.get("year")
        self.month = conf.get("month")
        self.set_references(self.year, self.month)
        self.employee_data = DadosServidor(
            data_referencia=self.reference.last,
            data_referencia_inicio=self.reference.first,
            # importacao_completa=self._importacao_completa
        )
        # self.set_data_referencia(self._ano_referencia, self._mes_referencia)
        self.feedback = conf.get("feedback", feedback)

    def write_feedback(self, progress=1, message_progress="", info=False):
        self.feedback(
            "%(message_progress)s",
            progress,
            info=info,
            message_progress=message_progress[0:99],
        )

    @classmethod
    def cache_dir(cls):
        return settings.CACHE_PATH

    def query(self):
        return []

    def body(self):
        query = self.query()
        message_progress = "Inserindo %s." % self._class_name
        total = (
            query.count() if not isinstance(query, (list, dict, tuple)) else len(query)
        )
        count = 0
        self.write_feedback(progress=100, message_progress=message_progress, info=True)
        for info in query:
            count += 1.0
            progress = (100.0 * float(count)) / float(total)
            # self.write_feedback(progress=((), message_progress=message_progress)
            self.add_registry(info, progress)

    def add_registry(self, info, progress=0):
        pass

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def set_references(self, year, month):
        self.period = Periodo.objects.get(ano=year, mes=month)

    @property
    def reference(self):
        return self.period.range

    def delete_file(self):
        try:
            filename = os.path.join(self.cache_dir(), self._file_name)
            print("Apagando arquivo %s..." % filename)
            self.write_feedback(0, "Apagando arquivos existentes")
            log.info("Apagando arquivo %s..." % filename)
            os.unlink(filename)
        except Exception as err:
            log.exception(err)

    def save_file(self, mode="w", text=""):
        rst = False
        try:
            filename = os.path.join(self.cache_dir(), self._file_name)
            print("Criando arquivo %s..." % filename)
            log.info("Criando arquivo %s..." % filename)
            fd = codecs.open(filename, mode, self._encoding)
            if mode == "a":
                fd.write("\n")
        except Exception as err:
            log.exception(err)
        else:
            if not text:
                text = str(self)
            try:
                fd.write(text)
            except Exception as err:
                log.exception(err)
            fd.close()
            rst = True
        return rst

    def get_file_name(self):
        return "%s_MP_%s%s" % (self._file_name, self.year, self.month)

    def get_arc_file_name(self):
        return self._file_name


class RegistroSisprev(Registro):
    """
    Classe para implementar os registros(linhas) dos arquivos bancários.
    """

    _protocolo = SISPREV
    _separador = "ß"


class PessoasSegurados(Sisprev):
    _class_name = "PessoasSegurados"
    _file_name = "PESSOAS_SEGURADOS_FOLHA_MENSAL"

    def query(self):
        return (
            ServidorRh.objects.filter(
                # tipo__in=('S', 'M'),
                social_securities__organ__cnpj="25091307000176"
            )
            .on_period_and_main_payroll(
                self.reference.first.month, self.reference.first.year
            )
            .exclude(
                type_by_possession__in=BenefitMovement.ALLOWED_TYPE_BY_POSSESSION
                + ("REX",)
            )
        )

    def get_phone_by_type(self, phone_type, person):
        return person.phone.filter(tipo_telefone__in=phone_type).last()

    def add_registry(self, employee, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        posse_atual = self.employee_data.get_posse_atual(employee)
        identificador_categoria = "EFETIVO"
        if employee.requested:
            identificador_categoria = "REQUISITADO"
        if employee.type_by_possession in [
            "ECM",
            "EFC",
            "RCM",
            "RFC",
        ]:
            identificador_categoria += "/COMISSAO"
        # identificador_situacao_funcional_anterior = ''

        sf_atual = ""
        if employee.historico_situacao_funcional.filter(
            situacao=employee.situacao_funcional_cache
        ).exists():
            sf_atual = (
                employee.historico_situacao_funcional.filter(
                    situacao=employee.situacao_funcional_cache
                )
                .order_by("data_inicio")
                .last()
            )
        sf_anterior = ""
        if (
            sf_atual
            and employee.historico_situacao_funcional.filter(
                data_inicio__lte=sf_atual.data_inicio
            ).exists()
        ):
            sf_anterior = (
                employee.historico_situacao_funcional.filter(
                    data_inicio__lte=sf_atual.data_inicio
                )
                .order_by("data_inicio")
                .last()
            )
        workplace = None
        if employee.get_workplace_only().exists():
            workplace = employee.get_workplace_only().last().lotacao
        elif employee.work_assignment.exists():
            workplace = employee.work_assignment.last().lotacao
        else:
            workplace = (
                employee._raw_locations(option=1).last().lotacao
                if employee._raw_locations(option=1).exists()
                else None
            )

        endereco = employee.pessoa_fisica.address.last()
        print(employee)
        print(workplace)
        try:
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador=employee.pessoa_fisica.cpf,
                    cpf=employee.pessoa_fisica.cpf,
                    nome=str(employee.pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        employee.pessoa_fisica.data_nascimento
                    ),
                    sexo=employee.pessoa_fisica.sexo,
                    mae=employee.pessoa_fisica.nome_mae,
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
                    fone_residencial=self.get_phone_by_type(
                        [1], employee.pessoa_fisica
                    ),
                    fone_celular=self.get_phone_by_type([3], employee.pessoa_fisica),
                    fone_trabalho=self.get_phone_by_type(
                        [2, 5], employee.pessoa_fisica
                    ),
                    email_1=employee.pessoa_fisica.email_institucional,
                    email_2=(
                        user_from_person(employee.pessoa_fisica).email
                        if user_from_person(employee.pessoa_fisica)
                        else ""
                    ),
                    pai=employee.pessoa_fisica.nome_pai,
                    estado_civil=employee.pessoa_fisica.estado_civil,
                    escolaridade=employee.pessoa_fisica.grau_instrucao,
                    doenca_incapacitante="N",
                    data_inicio_doenca_incapacitante="dd/mm/aaaa",
                    data_fim_doenca_incapacitante="dd/mm/aaaa",
                    portador_molestia=(
                        "S" if hasattr(employee.pessoa_fisica, "molestia") else "N"
                    ),
                    data_inicio_portador_molestia="dd/mm/aaaa",
                    data_fim_portador_molestia="dd/mm/aaaa",
                    nacionalidade=employee.pessoa_fisica.nacionalidade,
                    naturalidade_uf=(
                        str(employee.pessoa_fisica.municipio_naturalidade.estado.sigla)
                        if employee.pessoa_fisica.municipio_naturalidade
                        else ""
                    ),
                    naturalidade_cidade=str(
                        employee.pessoa_fisica.municipio_naturalidade
                    ),
                    pis_pasep=employee.pessoa_fisica.pis_pasep,
                    rg_numero=employee.pessoa_fisica.rg,
                    rg_orgao=employee.pessoa_fisica.rg_orgao,
                    rg_uf=employee.pessoa_fisica.rg_uf.sigla,
                    rg_data_expedicao=DateUtils.date_to_str(
                        employee.pessoa_fisica.rg_data_expedicao
                    ),
                    ctps_numero=(
                        employee.pessoa_fisica.ctps.ctps_numero
                        if employee.pessoa_fisica.ctps
                        else ""
                    ),
                    ctps_serie=(
                        employee.pessoa_fisica.ctps.ctps_series
                        if employee.pessoa_fisica.ctps
                        else ""
                    ),
                    ctps_uf=(
                        employee.pessoa_fisica.ctps.estado_expedicao.sigla
                        if employee.pessoa_fisica.ctps
                        and employee.pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    ctps_data_emissao=(
                        DateUtils.date_to_str(
                            employee.pessoa_fisica.ctps.data_expedicao
                        )
                        if employee.pessoa_fisica.ctps
                        and employee.pessoa_fisica.ctps.data_expedicao
                        else ""
                    ),
                    ctps_local_expedicao=(
                        employee.pessoa_fisica.ctps.estado_expedicao.sigla
                        if employee.pessoa_fisica.ctps
                        and employee.pessoa_fisica.ctps.estado_expedicao
                        else ""
                    ),
                    titulo_eleitoral_numero=(
                        employee.pessoa_fisica.voter.numero
                        if employee.pessoa_fisica.voter
                        else ""
                    ),
                    titulo_eleitoral_zona=(
                        employee.pessoa_fisica.voter.voter_zone.valor
                        if employee.pessoa_fisica.voter
                        and employee.pessoa_fisica.voter.voter_zone
                        else ""
                    ),
                    titulo_eleitoral_secao=(
                        employee.pessoa_fisica.voter.voter_section.valor
                        if employee.pessoa_fisica.voter
                        and employee.pessoa_fisica.voter.voter_section
                        else ""
                    ),
                    titulo_eleitoral_uf=(
                        employee.pessoa_fisica.voter.estado_expedicao.sigla
                        if employee.pessoa_fisica.voter
                        and employee.pessoa_fisica.voter.estado_expedicao
                        else ""
                    ),
                    identificador_segurado=employee.pessoa_fisica.cpf,
                    matricula=self.employee_data.get_registry_origin(employee),
                    categoria=identificador_categoria,
                    orgao=ORGAN.nome,
                    unidade=workplace.nome if workplace else "",
                    lotacao=workplace.nome if workplace else "",
                    identificador_cargo=DadosCargo.get_codigo(posse_atual.quadro.cargo),
                    nome_cargo=DadosCargo.get_descricao(posse_atual.quadro.cargo),
                    data_admissao=DateUtils.date_to_str(posse_atual.data_posse),
                    identificador_fonte_pagadora=ORGAN.codigo_igeprev,
                    nome_fonte_pagadora=ORGAN.nome,
                    tipo_situacao_funcional=FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(
                        employee.situacao_funcional_cache
                    ),
                    data_situacao_funcional=(
                        DateUtils.date_to_str(sf_atual.data_inicio) if sf_atual else ""
                    ),
                    excluido_exonerado=str("S" if not employee.ativo else "N"),
                    data_exclusao=(
                        DateUtils.date_to_str(posse_atual.data_desligamento)
                        if not employee.ativo and posse_atual.data_desligamento
                        else ""
                    ),
                    motivo_exclusao=(
                        posse_atual.desligamento.get_tipo_desligamento_display()
                        if not employee.ativo and posse_atual.data_desligamento
                        else ""
                    ),
                    fundo_previdenciario=str(
                        "PF"
                        if employee.data_exercicio
                        >= datetime(year=2012, month=6, day=1).date()
                        else "PP"
                    ),
                    abono_permanencia="S" if employee.stay_allowance else "N",
                    data_abono_permanencia=(
                        DateUtils.date_to_str(employee.stay_allowance)
                        if employee.stay_allowance
                        else ""
                    ),
                )
            )
            message = "Registro %s inserido com sucesso" % employee
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (employee, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class ExoneradosAfastados(PessoasSegurados):

    _class_name = "ExoneradosAfastados"
    _file_name = "PESSOAS_SEGURADOS_EXONERADOS_AFASTADOS"

    def query(self):
        period_departures = (
            BaseLicencaAfastamento.objects.currents_in(range=self.period.previous.range)
            .unpaid()
            .values("servidor")
        )
        return ServidorRh.objects.filter(
            social_securities__organ__cnpj="25091307000176", pk__in=period_departures
        )


class ContribuicoesMensal(PessoasSegurados):

    _file_name = "CONTRIBUICOES_MENSAL"
    _class_name = "ContribuicoesMensal"

    def query(self):
        employees = super().query().values_list("pk", flat=True)
        return ContraCheque.objects.filter(
            servidor__pk__in=employees,
            folha__periodo=self.period,
            lancamentos__evento__tags__label="rpps",
        )

    def add_registry(self, paycheck, progress):
        info = False
        try:
            values = paycheck.lancamentos.filter(evento__tags__label="rpps").aggregate(
                base=Sum("correct_base_value"),
                contribution=Sum("correct_value"),
                employer_contribution=Sum("correct_employer_contribution"),
            )
            base, contribution, employer_contribution = (
                values["base"],
                values["contribution"],
                values["employer_contribution"],
            )
            print(base, contribution, employer_contribution)
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador_segurado=paycheck.servidor.pessoa_fisica.cpf,
                    ano=paycheck.folha.periodo.ano,
                    mes=paycheck.folha.periodo.mes,
                    base_contribuicao=str(abs(base)),
                    contribuicao_segurado=str(abs(contribution)),
                    contribuicao_patronal=str(abs(employer_contribution)),
                    contribuicao_patronal_especial=0.00,
                    identificador_fonte_pagadora=ORGAN.codigo_igeprev,
                    nome_fonte_pagadora=ORGAN.nome,
                    numero_tipo_folha=paycheck.folha.tipo_folha.numero,
                    descricao_numero_tipo_folha=paycheck.folha.tipo_folha.titulo,
                )
            )
            message = "Registro %s inserido com sucesso" % paycheck
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (paycheck, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class GuiaRecolhimento(PessoasSegurados):

    _file_name = "GRPC_MENSAL"
    _class_name = "GuiaRecolhimento"

    def query(self):
        groups = SocialSecurityContributionsReport.objects.filter(
            payroll__periodo=self.period
        )
        print(groups.count())
        groups_list = []
        for group in groups.values_list("payroll", flat=True).distinct():
            for f in range(1, 3):
                summary = groups.filter(mass_segregation_plan=f).aggregate(
                    employee_base_calculation=Coalesce(
                        Sum("employee_base_calculation"), 0.00
                    ),
                    employee_contribution=Coalesce(Sum("employee_contribution"), 0.00),
                    employer_contribution=Coalesce(Sum("employer_contribution"), 0.00),
                    employee_quantity=Coalesce(Sum("employee_quantity"), 0.00),
                )
                groups_list.append(
                    {
                        "payroll": group,
                        "mass_segregation_plan": f,
                        "employee_base_calculation": summary[
                            "employee_base_calculation"
                        ],
                        "employee_contribution": summary["employee_contribution"],
                        "employer_contribution": summary["employer_contribution"],
                        "employee_quantity": summary["employee_quantity"],
                    }
                )

        return groups_list

    def add_registry(self, group, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        try:
            (
                sheet_type,
                sheet_description,
                sheet_year,
                sheet_month,
            ) = Folha.objects.filter(pk=group["payroll"]).values_list(
                "tipo_folha__numero",
                "tipo_folha__titulo",
                "periodo__ano",
                "periodo__mes",
            )[
                0
            ]
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador_fonte_pagadora=ORGAN.codigo_igeprev,
                    nome_fonte_pagadora=ORGAN.nome,
                    descricao_grupo="descricao",
                    fundo_previdenciario=(
                        "FUNDO PREVIDENCIARIO"
                        if group["mass_segregation_plan"] == 1
                        else "FUNDO FINANCEIRO"
                    ),
                    numero_tipo_folha=sheet_type,
                    descricao_numero_tipo_folha=sheet_description,
                    ano=sheet_year,
                    mes=sheet_month,
                    base_contribuicao=str(group["employee_base_calculation"]),
                    contribuicao_segurado=str(group["employee_contribution"]),
                    contribuicao_patronal=str(group["employer_contribution"]),
                    contribuicao_patronal_especial=0.00,
                    total_servidores=group["employee_quantity"],
                )
            )
            message = "Registro %s inserido com sucesso" % group
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (group, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class Dependentes(PessoasSegurados):

    _file_name = "DEPENDENTE"
    _class_name = "Dependentes"

    def query(self):
        employees_dependents = super().query().values_list("dependentes")
        dependencies_active = (
            Dependencia.objects.filter(dependente__pk__in=employees_dependents)
            .active_in(self.reference.first, self.reference.last)
            .values_list("dependente")
        )
        return Dependente.objects.filter(pk__in=dependencies_active).exclude(
            Q(pessoa_fisica__cpf__isnull=True) | Q(pessoa_fisica__cpf="")
        )

    def add_registry(self, dependent, progress):
        info = False
        try:
            endereco = dependent.pessoa_fisica.address.last()
            dependent_condition = "N"
            if dependent.capacidade == 2:
                if dependent.incapacity:
                    dependent_condition = "I"
                else:
                    dependent_condition = "C"

            dependencies = dependent.dependencias.active_in(range=self.reference)
            try:
                dependency = dependencies.get(tipo=1)  # irrf
            except:
                dependency = dependencies.last()
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador_responsavel=dependent.responsavel.cpf,
                    cpf_responsavel=dependent.responsavel.cpf,
                    nome_responsavel=str(dependent.responsavel),
                    data_nascimento_responsavel=DateUtils.date_to_str(
                        dependent.responsavel.data_nascimento
                    ),
                    identificador_dependente=dependent.pessoa_fisica.cpf,
                    cpf_dependente=dependent.pessoa_fisica.cpf,
                    nome_dependente=str(dependent.pessoa_fisica),
                    data_nascimento_dependente=DateUtils.date_to_str(
                        dependent.pessoa_fisica.data_nascimento
                    ),
                    sexo=dependent.pessoa_fisica.sexo,
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
                    fone_residencial=self.get_phone_by_type(
                        [1], dependent.pessoa_fisica
                    ),
                    fone_celular=self.get_phone_by_type([3], dependent.pessoa_fisica),
                    fone_trabalho=self.get_phone_by_type([5], dependent.pessoa_fisica),
                    email_1=dependent.pessoa_fisica.email_institucional,
                    mae=dependent.pessoa_fisica.nome_mae,
                    pai=dependent.pessoa_fisica.nome_pai,
                    estado_civil=dependent.pessoa_fisica.estado_civil,
                    escolaridade=dependent.pessoa_fisica.grau_instrucao,
                    doenca_incapacitante="N",  # verificar com rh como preencher
                    portador_molestia=(
                        "N" if hasattr(dependent.pessoa_fisica, "molestia") else "S"
                    ),
                    nacionalidade=dependent.pessoa_fisica.nacionalidade,
                    naturalidade_uf=(
                        str(dependent.pessoa_fisica.municipio_naturalidade.estado.sigla)
                        if dependent.pessoa_fisica.municipio_naturalidade
                        else ""
                    ),
                    naturalidade_cidade=str(
                        dependent.pessoa_fisica.municipio_naturalidade
                    ),
                    pis_pasep=dependent.pessoa_fisica.pis_pasep,
                    rg_numero=dependent.pessoa_fisica.rg,
                    rg_orgao=dependent.pessoa_fisica.rg_orgao,
                    rg_uf=(
                        dependent.pessoa_fisica.rg_uf.sigla
                        if dependent.pessoa_fisica.rg_uf
                        else ""
                    ),
                    rg_data_expedicao=(
                        DateUtils.date_to_str(dependent.pessoa_fisica.rg_data_expedicao)
                        if dependent.pessoa_fisica.rg_data_expedicao
                        else ""
                    ),
                    tipo_dependencia=dependency.tipo,
                    data_inicio_dependencia=DateUtils.date_to_str(
                        dependency.data_inicio
                    ),
                    data_fim_dependencia=(
                        DateUtils.date_to_str(dependency.data_fim)
                        if dependency.data_fim
                        else ""
                    ),
                    condicao_dependente=dependent_condition,
                    codigo_doenca_invalidez="",
                    data_laudo_invalidez="",
                    irrf=("S" if dependency.tipo == 1 else "N"),
                )
            )
            message = "Registro %s inserido com sucesso" % dependent
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (dependent, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class FolhaAtivos(PessoasSegurados):

    _file_name = "FOLHA_MENSAL_ATIVOS"
    _class_name = "FolhaAtivos"

    def query(self):
        employees = super().query().values_list("pk", flat=True)
        return FolhaEvento.objects.filter(
            folha__periodo=self.period, servidor__pk__in=employees
        )

    def is_focused_on(self, config, tag):
        return "S" if config.focuses_on.filter(tags__label=tag).exists() else "N"

    def add_registry(self, entry, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        try:
            employee = entry.servidor
            bank_info = employee.pessoa_fisica.bankings_employee_payroll.filter(
                type_of_payroll=entry.folha.tipo_folha
            ).last()
            config_event = entry.evento.configs.validity_in(
                self.reference.first, self.reference.last
            ).last()
            map_calc_type = {1: "P", 5: "P", 2: "V", 3: "D", 4: "V"}
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador=employee.pessoa_fisica.cpf,
                    matricula=employee.matricula,
                    cpf=employee.pessoa_fisica.cpf,
                    nome=str(employee.pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        employee.pessoa_fisica.data_nascimento
                    ),
                    categoria=1 if employee.ativo else 0,
                    data_inicio_vencimento=self.reference.first,
                    data_fim_vencimento=self.reference.last,
                    banco=bank_info.banking_person.banco.numero,
                    agencia=bank_info.banking_person.banco.agencia,
                    dv_agencia=bank_info.banking_person.banco.dv_agencia,
                    conta=bank_info.banking_person.banco.conta,
                    dv_conta=bank_info.banking_person.banco.dv_conta,
                    pagamento_bloqueado="N",
                    valor_beneficio_vencimento=0.00,
                    codigo_evento=entry.evento.numero,
                    descricao_evento=entry.evento.titulo,
                    valor_evento=entry.value,
                    tipo_evento=entry.evento.tipo,
                    compoe_base_contribuicao=self.is_focused_on(config_event, "rpps"),
                    incide_irrf=self.is_focused_on(config_event, "irrf"),
                    parcela_atual=entry.parcela,
                    total_parcelas=entry.prazo,
                    data_inicio_consignacao="",
                    data_fim_consignacao="",
                    ano=entry.folha.periodo.ano,
                    mes=entry.folha.periodo.mes,
                    referencia=map_calc_type.get(entry.evento.tipo_calculo),
                    valor_referencia=entry.valor_base,
                    numero_tipo_folha=str(entry.folha.tipo_folha.numero),
                    descricao_tipo_folha=str(entry.folha.tipo_folha.titulo),
                )
            )
            message = "Registro %s inserido com sucesso" % entry
        except Exception as err:
            message = "Erro em (evento/matricula) %s/%s : %s" % (
                entry.evento.numero,
                entry.servidor.matricula,
                err,
            )
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class EvolucaoCarreira(PessoasSegurados):
    _file_name = "EVOLUCAO_CARREIRA"
    _class_name = "EvolucaoCarreira"

    def query(self):
        employees = super().query().values_list("pk", flat=True)
        return MovimentacaoProgressao.objects.filter(servidor__pk__in=employees)

    def add_registry(self, progression, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        try:
            workplace = progression.servidor.get_workplace().last().lotacao
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    separator="ß",
                    identificador=progression.servidor.pessoa_fisica.cpf,
                    matricula=progression.servidor.matricula,
                    cpf=progression.servidor.pessoa_fisica.cpf,
                    nome=str(progression.servidor.pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        progression.servidor.pessoa_fisica.data_nascimento
                    ),
                    orgao=ORGAN.nome,
                    unidade=workplace.pai.nome,
                    lotacao=workplace.nome,
                    identificador_cargo=progression.movimentacao_posse.quadro.cargo.codigo,
                    nome_cargo=progression.movimentacao_posse.quadro.cargo.nome,
                    data_inicio=DateUtils.date_to_str(progression.data_inicio_vigencia),
                    data_fim=DateUtils.date_to_str(progression.data_fim_vigencia),
                    referencia=progression.referencia_nivel2d.sigla_cache,
                    nivel="",
                    classe=progression.referencia_nivel2d.vertical,
                    padrao=progression.referencia_nivel2d.horizontal,
                    motivo_fim="",
                )
            )
            message = "Registro %s inserido com sucesso" % progression
        except Exception as err:
            message = "Algo deu errado no registro %s de %s : %s" % (
                progression,
                progression.servidor.matricula,
                err,
            )
            # info = True ### comentei porque esse arquivo é histórico e tem muitos faltando dados
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class TempoAnteriorRPPS(PessoasSegurados):
    _file_name = "TEMPO_ANTERIOR_RPPS"
    _class_name = "TempoAnteriorRPPS"

    def query(self):
        employees = super().query().values_list("pessoa_fisica", flat=True)
        return EmploymentBond.objects.filter(
            retirement_prevision__natural_person__pk__in=employees, pension_system=2
        ).exclude(with_pgj=True)

    def add_registry(self, bond, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        employee = bond.retirement_prevision.natural_person.servidor_set.last()
        try:
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador=employee.pessoa_fisica.cpf,
                    matricula=employee.matricula,
                    cpf=employee.pessoa_fisica.cpf,
                    nome=str(employee.pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        employee.pessoa_fisica.data_nascimento
                    ),
                    data_inicio=DateUtils.date_to_str(bond.begin_date),
                    data_fim=DateUtils.date_to_str(bond.end_date),
                    protocolo="",
                    ano=bond.end_date.year,
                    nome_empresa=bond.employer,
                    cargo="",
                    orgao=bond.employer,
                )
            )
            message = "Registro %s inserido com sucesso" % bond
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (bond, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class TempoAnteriorRGPS(PessoasSegurados):
    _file_name = "TEMPO_ANTERIOR_RGPS"
    _class_name = "TempoAnteriorRGPS"

    def query(self):
        employees = super().query().values_list("pessoa_fisica", flat=True)
        return EmploymentBond.objects.filter(
            retirement_prevision__natural_person__pk__in=employees, pension_system=1
        ).exclude(with_pgj=True)

    def add_registry(self, bond, progress):
        """
        Este método adiciona os Registros de acordo com o layout do arquivo.
        """
        info = False
        employee = bond.retirement_prevision.natural_person.servidor_set.last()
        try:
            self.regs.append(
                RegistroSisprev(
                    len(self.regs) + 1,
                    self._class_name,
                    apply_blank=False,
                    identificador=employee.pessoa_fisica.cpf,
                    matricula=employee.matricula,
                    cpf=employee.pessoa_fisica.cpf,
                    nome=str(employee.pessoa_fisica),
                    data_nascimento=DateUtils.date_to_str(
                        employee.pessoa_fisica.data_nascimento
                    ),
                    data_inicio=DateUtils.date_to_str(bond.begin_date),
                    data_fim=DateUtils.date_to_str(bond.end_date),
                    aposentadoria_especial="N",
                    tipo_tempo=1 if bond.public_employee else 2,
                    protocolo="",
                    ano=bond.end_date.year,
                    nome_empresa=bond.employer,
                    cargo="",
                    orgao=bond.employer,
                )
            )
            message = "Registro %s inserido com sucesso" % bond
        except Exception as err:
            message = "Algo deu errado no registro %s : %s" % (bond, err)
            info = True
            log.exception(err)
        self.write_feedback(progress, info=info, message_progress=message)


class SisprevWebGenerator(object):

    BUILDERS = {
        "pessoas_segurados_folha_mensal": PessoasSegurados,
        "pessoas_segurados_exonerados_afastados": ExoneradosAfastados,
        "contribuicoes_mensal": ContribuicoesMensal,
        "grcp_mensal": GuiaRecolhimento,
        "dependentes": Dependentes,
        "folha_mensal_ativos": FolhaAtivos,
        "evolucao_carreira": EvolucaoCarreira,
        "tempo_anterior_rgps": TempoAnteriorRGPS,
        "tempo_anterior_rpps": TempoAnteriorRPPS,
    }

    def __init__(self, **kwargs):
        self.year = kwargs.get("year", None)
        self.month = kwargs.get("month", None)
        self.feedback = kwargs.get("feedback", feedback)

    def write_feedback(self, progress=1, message_progress="", info=False):
        self.feedback(
            "%(message_progress)s",
            progress,
            info=info,
            message_progress=message_progress[0:99],
        )

    @classmethod
    def cache_dir(cls):
        return settings.CACHE_PATH

    def get_zip_file(self):
        return os.path.join(self.cache_dir(), self.get_zip_name())

    def get_zip_name(self):
        return "mpeto-igeprev-%s-%s.zip" % (self.year, self.month)

    def compact(self, to_zip_files):
        try:
            total = len(to_zip_files)
            count = 0
            self.write_feedback(message_progress="Iniciando compressão de arquivos.")
            zipfile = ZipFile(self.get_zip_file(), "w")
            for f in to_zip_files:
                try:
                    source = "%s/%s" % (self.cache_dir(), f[0])
                    zipfile.write(source, "%s.txt" % f[1])
                except Exception as err:
                    log.exception(err)
                    print(err)
                count += 1
                self.write_feedback(
                    progress=((100.0 * float(count)) / float(total)),
                    message_progress="Comprimindo...",
                    info=True,
                )
            zipfile.close()
        except Exception as err:
            log.exception(err)
            print(err)

    def gerador(self, importacao_completa=False, tfiles=BUILDERS):

        to_zip = []

        if os.path.exists(self.get_zip_file()):
            os.unlink(self.get_zip_file())

        self.write_feedback(
            message_progress="Iniciando processo de geração de arquivos"
        )

        count = 0
        total = len(tfiles) if len(tfiles) > 0 else 1
        for mfile in tfiles:
            Builder = tfiles.get(mfile, None)
            count += 1

            self.write_feedback(
                progress=((100.0 * float(count)) / float(total)),
                message_progress="Gerando arquivos: %d de %d" % (count, total),
            )
            if Builder:
                builder = Builder(
                    feedback=self.feedback,
                    year=self.year,
                    month=self.month,
                )

                builder.save_file()

                to_zip.append(
                    [
                        builder.get_arc_file_name(),
                        builder.get_file_name(),
                    ]
                )
            else:
                log.warn("O gerador para o arquivo %s é desconhecido." % mfile)
        self.compact(to_zip)
        self.write_feedback(
            progress=100, message_progress="Geração de arquivos concluída."
        )
