# -*- coding: utf-8 -*-

from datetime import datetime

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.helpers import clear_to_ascii
from contrib.protofile import GroupRecords, Protocol, Record
from contrib.utils import getLogger
from engine.models import NullTaskSession
from rh.constants_functional_situations import FUNCTIONAL_STATE_INDEX_STR_TO_INT
from rh.gfp.models import Evento as Event
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.models import MarginPaycheck, MarginConsignable
from rh.models import Lotacao, Servidor, UnidadeAdministrativa
from standard.models import Choice, Configuration

from .layouts import NEOCONSIG

# import re

__name__ = "NeoConsig"
__hid__ = "001"

log = getLogger(__name__)


class RecordNeoconsig(Record):
    _protocol = NEOCONSIG
    _separator = ""


class BaseNeoConsigFile(Protocol):
    """
    =======================================================================
           |  H.F. - Header of File * - Reg 1
           |   |-----------------------------------------------
       F   |   | R.D. - Detail Record * - Reg 2
       I   |   |-----------------------------------------------
       L   |   | R.D. - Detail Record * - Reg 2
       E   |   |-----------------------------------------------
           |   | .
           |   | .
           |   | .
    =======================================================================
    """

    def __init__(self, period, task=NullTaskSession()):
        super(BaseNeoConsigFile, self).__init__()
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.cfg = Configuration.objects.get(application="gfp")
        self.period = period
        self.range = NewDateRange.from_month(self.period.ano, self.period.mes)
        self.observer = task
        self.regs = []


class EmployeesFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CADSERVIDOR",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('SERVIDORES %s' % self.period)

        query = Servidor.objects.exclude(
            type_by_possession__in=["TCR", "VOL", "JCA", "XXX"]
        )

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        organ = UnidadeAdministrativa.objects.filter(main=True, ativo=True).first()

        for employee in query:
            seq += 1
            cat = 0
            try:
                choice = Choice.objects.get(
                    app_label="rh",
                    name="CLASSIF_EMPLOYEE_BY_POSSESSION",
                    cvalue=employee.type_by_possession,
                )
                cat = choice.value
            except Choice.DoesNotExists:
                cat = 0

            workplace = employee.get_workplace(self.range.last).first()
            departures = employee.get_afastamentos(self.range.last)
            departure = departures[0].my_origin if departures else None

            group_records.add(
                "employees",
                sequencial=seq,
                codigo_secretaria=organ.pk if organ else 1,
                matricula=employee.matricula,
                identificador=0,
                cpf=employee.pessoa_fisica.cpf,
                data_nascimento=(
                    employee.pessoa_fisica.data_nascimento.strftime("%d%m%Y")
                    if employee.pessoa_fisica.data_nascimento
                    else 0
                ),
                nome=clear_to_ascii(employee.pessoa_fisica.nome.upper()),
                codigo_situacao=FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(
                    employee.situacao_funcional_cache, 0
                ),
                codigo_categoria=cat,
                codigo_lotacao=workplace.lotacao.pk if workplace else 0,
                admissao=(
                    employee.data_exercicio.strftime("%d%m%Y")
                    if employee.data_exercicio
                    else 0
                ),
                afastamento=(
                    departure.data_inicio.strftime("%d%m%Y") if departure else 0
                ),
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de servidores.")

        return self.regs
        # ----------------------------------------------------------------------


class OrgansFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CADSECRETARIA",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('SECRETARIAS %s' % self.period)

        query = UnidadeAdministrativa.objects.filter(main=True, ativo=True)

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for organ in query:

            seq += 1

            group_records.add(
                "organs",
                sequencial=seq,
                codigo_secretaria=organ.pk,
                sigla=clear_to_ascii((organ.sigla or "").upper()),
                nome=clear_to_ascii(organ.nome.upper()),
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de secretarias.")

        return self.regs
        # ----------------------------------------------------------------------


class WorkLocationsFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "LOTACAO",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('LOTACOES %s' % self.period)

        query = Lotacao.objects.filter(organograma=True, ativo=True)

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for worklocation in query:

            seq += 1

            group_records.add(
                "worklocations",
                sequencial=seq,
                codigo_lotacao=worklocation.pk,
                nome=clear_to_ascii(worklocation.nome.upper())[0:50],
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de lotações.")

        return self.regs
        # ----------------------------------------------------------------------


class EventsFile(BaseNeoConsigFile):
    # margens
    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "VANTAGEMDESCONTO",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('RUBRICAS %s' % self.period)

        query = MarginConsignable.objects.filter(active=True)

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for event in query:

            seq += 1
            # AJUSTAR
            group_records.add(
                "events",
                sequencial=seq,
                rubrica=seq,
                nome=clear_to_ascii(event.title.upper())[0:50],
                tipo="D",
                participa_do_calculo="N",
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de lotações.")

        return self.regs
        # ----------------------------------------------------------------------


class ClassificationsFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CADCATEGORIA",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('CADCATEGORIA %s' % self.period)

        choices = Choice.get_dict_choices_for("rh", "CLASSIF_EMPLOYEE_BY_POSSESSION")

        base_pct = len(choices)
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for idx in choices:
            choice = choices[idx]

            seq += 1

            group_records.add(
                "classifications",
                sequencial=seq,
                codigo_categoria=idx,
                nome=clear_to_ascii(choice.upper())[0:50],
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de lotações.")

        return self.regs
        # ----------------------------------------------------------------------


class SituationsFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CADSITFUNCIONAL",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('CADSITFUNCIONAL %s' % self.period)

        choices = FUNCTIONAL_STATE_INDEX_STR_TO_INT

        base_pct = len(choices)
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for value in choices:
            idx = choices[value]

            seq += 1

            group_records.add(
                "situations",
                sequencial=seq,
                codigo_situacao=idx,
                nome=clear_to_ascii(value.upper())[0:50],
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de situações.")

        return self.regs
        # ----------------------------------------------------------------------


class FinancialFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "FINANCEIRO",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('FINANCEIRO %s' % self.period)

        query = Servidor.objects.filter(ativo=True).exclude(
            type_by_possession__in=["TCR", "VOL", "EXT", "JCA", "XXX"]
        )

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0
        margins = []
        employee_id = None
        for employee in query:
            if employee.id != employee_id:
                margins = []
                employee_id = employee.id
            for mp in MarginPaycheck.objects.filter(
                paycheck__folha__periodo=self.period, paycheck__servidor=employee
            ).order_by("-total_value"):
                if mp.margin.id not in margins:
                    margins.append(mp.margin.pk)
                    # log.debug(('SERVIDORES %s %s' % (mp.margin, employee))

                    seq += 1
                    group_records.add(
                        "finacial",
                        sequencial=seq,
                        competencia="%02d%04d" % (self.period.mes, self.period.ano),
                        cpf=employee.pessoa_fisica.cpf,
                        matricula=employee.matricula,
                        identificador=0,
                        tipo_lancamento="V",
                        codigo=2 if mp.margin.identification == "M005CC" else 1,
                        valor_margem=int(mp.total_value * 100),
                    )
                    if not mp.total_value:
                        log.info(employee, mp, mp.total_value)
                    passo_pct += 1
                    self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de situações.")

        return self.regs
        # ----------------------------------------------------------------------


class HistoryFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CARGAEMPRESTIMO",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        choices = Entry.objects.filter(
            Q(folha__periodo=self.period)
            & Q(evento__consignment_manager=True, evento__active=True)
        )

        base_pct = len(choices)
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0
        # log.debug(('CARGAEMPRESTIMO %s' % self.period)

        for entry in choices:
            # idx = choices[entry]
            seq += 1
            tipo_operacao = 1
            if entry.evento.margins_consigneds.filter(
                identification__in=[
                    "M005CC",
                ]
            ).exists():
                tipo_operacao = 2
            elif entry.evento.margins_consigneds.filter(
                identification__in=["M030GERAL", "M100PAE"]
            ).exists():
                if entry.evento.carater == 7:
                    tipo_operacao = 1
                else:
                    tipo_operacao = 3
            else:
                tipo_operacao = 3
            log.info(entry)
            group_records.add(
                "history",
                sequencial=seq,
                rubrica=entry.evento.numero,
                matricula=entry.contracheque.servidor.matricula,
                identificador="000",
                cpf=entry.contracheque.servidor.pessoa_fisica.cpf,
                valor_da_parcela=int(abs(entry.valor * 100)),
                total_de_parcelas=entry.prazo,
                parcela_atual=entry.parcela,
                status_da_operacao=1,
                tipo_operacao=tipo_operacao,
                data_parcela_atual=entry.folha.dt_pagamento.strftime("%d%m%Y"),
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de situações.")

        return self.regs
        # ----------------------------------------------------------------------


class PaidOffFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "RETORNOQUITADAS",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        choices = Entry.objects.filter(
            Q(folha__periodo=self.period)
            & Q(evento__consignment_manager=True, evento__active=True)
        )

        base_pct = len(choices)
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0
        # log.debug(('RETORNOQUITADAS %s' % self.period)

        for entry in choices:
            # idx = choices[entry]
            seq += 1
            log.info(entry)
            group_records.add(
                "paidoff",
                sequencial=seq,
                competencia=f"{self.period.mes:02d}{self.period.ano:04d}",
                cpf=entry.contracheque.servidor.pessoa_fisica.cpf,
                matricula=entry.contracheque.servidor.matricula,
                identificador="000",
                rubrica=entry.evento.numero,
                valor_parcela=int(abs(entry.valor * 100)),
                numero_da_parcela=int(entry.parcela),
                total_de_parcelas=int(entry.prazo),
                id_da_operacao=int(entry.info) if entry.info.isdigit() else 0,
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de consignações quitadas.")

        return self.regs
        # ----------------------------------------------------------------------


class ConsigneeFile(BaseNeoConsigFile):

    def get_records(self):

        # log.debug((self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d%m%Y")

        config_header = {
            "data_de_geracao": today,
            "nome_do_arquivo": "CADCONSIGNATARIA",
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordNeoconsig, "header", None, **config_header)

        # log.debug(('CADCONSIGNATARIA %s' % self.period)

        choices = Event.objects.filter(consignment_manager=True, active=True)

        base_pct = len(choices)
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        seq = 0

        for value in choices:
            # idx = choices[value]

            seq += 1

            group_records.add(
                "consignee",
                sequencial=seq,
                codigo_consignataria=0,
                nome="",
                cnpj=0,
                razao_social="",
                nome_fantasia=clear_to_ascii(value.titulo.upper())[0:50],
                rubrica=value.numero,
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo de situações.")

        return self.regs
        # ----------------------------------------------------------------------
