# -*- coding: utf-8 -*-

from datetime import datetime

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.helpers import clear_to_ascii
from contrib.protofile import GroupRecords, Protocol, Record
from contrib.utils import getLogger
from engine.models import NullTaskSession
from rh.gfp.models import ContraCheque as PayCheck
from rh.gfp.models import Folha as Payroll
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.models import MarginPaycheck
from rh.models import Quadro, Servidor, UnidadeAdministrativa
from standard.models import Configuration

from .layouts import CONSIGFACIL

# import re

__name__ = "ConsigFacil"
__hid__ = "001"

log = getLogger(__name__)


class RecordConsigFacil(Record):
    _protocol = CONSIGFACIL
    _separator = ";"


class BaseConfigFacilFile(Protocol):
    def __init__(self, period, task=NullTaskSession()):
        super(BaseConfigFacilFile, self).__init__()
        # self.nl = '\r\n'  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.cfg = Configuration.objects.get(application="gfp")
        self.period = period
        self.range = NewDateRange.from_month(self.period.ano, self.period.mes)
        self.observer = task
        self.regs = []


class EmployeesFile(BaseConfigFacilFile):

    def get_records(self):

        # log.debug((self.observer)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)

        group_records = GroupRecords(RecordConsigFacil, None, None)

        payroll = Payroll.objects.filter(
            periodo=self.period, tipo_folha__titulo="NORMAL"
        ).last()
        employees_by_paycheck = list(
            PayCheck.objects.filter(folha=payroll)
            .order_by("servidor__id")
            .distinct("servidor__id")
            .values_list("servidor__id", flat=True)
        )

        query = Servidor.objects.exclude(
            type_by_possession__in=["TCR", "VOL", "JCA", "XXX", "SAP", "BFP", "COE"]
        ).filter(pk__in=employees_by_paycheck)
        organ = UnidadeAdministrativa.objects.filter(main=True, ativo=True).first()

        base_pct = query.count()
        passo_pct = 0
        inc_progress = 50.0 / base_pct
        seq = 0

        for employee in query:
            seq += 1
            margin = MarginPaycheck.objects.filter(
                paycheck__folha__periodo=self.period, paycheck__servidor=employee
            ).order_by("-total_value")
            margin_general = margin.filter(margin__identification="M030GERAL").first()
            margin_card = margin.filter(margin__identification="M005CC").first()
            celular = employee.pessoa_fisica.phone.filter(main=True).first()
            if not celular:
                celular = employee.pessoa_fisica.phone.all().first()
            job_position = employee.job_position()
            group_records.add(
                "employees",
                folha=payroll.id,
                matricula=employee.matricula,
                cpf=employee.pessoa_fisica.cpf,
                nome=clear_to_ascii(employee.pessoa_fisica.nome.upper()),
                codigo_regime=employee.type_by_possession,
                regime=employee.get_type_by_possession_display(),
                cargo_estavel=1 if employee.is_efetivo else 0,
                data_admissao=(
                    employee.data_exercicio.strftime("%d%m%Y")
                    if employee.data_exercicio
                    else 0
                ),
                codigo_orgao=organ.id,
                descricao_orgao=organ.nome,
                codigo_cargo=(
                    job_position.cargo.codigo
                    if isinstance(job_position, Quadro)
                    else ""
                ),
                descricao_cargo=(
                    job_position.cargo.nome
                    if isinstance(job_position, Quadro)
                    else job_position
                ),
                email="",
                celular=celular.numero if celular else 0,
                margem_geral=margin_general.total_value if margin_general else 0,
                margem_cartao=margin_card.total_value if margin_card else 0,
                data_nascimento=(
                    employee.pessoa_fisica.data_nascimento.strftime("%d%m%Y")
                    if employee.pessoa_fisica.data_nascimento
                    else 0
                ),
            )
            passo_pct += 1
            self.observer.increment_progress(inc_progress)

        self.regs = self.regs + group_records.get_records()

        self.observer.info(msg="Gerado arquivo de servidores.", type_of=1)

        return self.regs


class EntriesFile(BaseConfigFacilFile):

    def get_records(self):

        today = datetime.today().strftime("%d%m%Y")

        # Adicionando Header de Arquivo REG 1------------------------------------------

        group_records = GroupRecords(RecordConsigFacil, None, None)

        choices = Entry.objects.filter(
            Q(folha__periodo=self.period)
            & Q(evento__consignment_manager=True, evento__active=True)
        )

        base_pct = choices.count()
        passo_pct = 0

        inc_progress = 50.0 / base_pct

        seq = 0

        for entry in choices:
            seq += 1
            group_records.add(
                "payroll",
                folha=entry.folha.id,
                matricula=entry.contracheque.servidor.matricula,
                codigo_verba=entry.evento.numero,
                descricao_verba=entry.evento.titulo,
                tipo="V" if entry.evento.tipo == "P" else "D",
                valor=abs(entry.value),
                parcelas_restantes=(entry.prazo - entry.parcela),
                parcela_inicial=1,
                parcela_atual=entry.parcela,
                prazo_total=entry.prazo,
            )

            passo_pct += 1
            self.observer.increment_progress(inc_progress)

        self.regs = self.regs + group_records.get_records()

        self.observer.info(msg="Gerado arquivo de situações.", type_of=1)

        return self.regs
