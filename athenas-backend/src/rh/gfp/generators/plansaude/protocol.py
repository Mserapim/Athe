# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings

from contrib.protofile import GroupRecords, Protocol, Record
from contrib.utils import getLogger
from engine.models import NullTaskSession
from rh.afastamento.models import LicencaInteresseParticular
from rh.const import ATIVO
from rh.gfp.generators.plansaude.layouts import FPSPLAN
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.models import LoadedEntryHistory
from rh.models import Servidor
from standard.models import Configuration

# import re

__name__ = "PlanSaúde"
__hid__ = "001"

log = getLogger(__name__)


class RecordPlan(Record):
    _protocol = FPSPLAN
    _separator = ";"


class BasePlanSaudeFile(Protocol):
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
        super(BasePlanSaudeFile, self).__init__()
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.cfg = Configuration.objects.get(application="gfp")
        self.period = period
        self.observer = task
        self.regs = []


class ConsignablesFile(BasePlanSaudeFile):

    def get_records(self):

        log.debug(self.observer)
        self.observer.set("pct", 0.0)

        ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d/%m/%Y")

        config_header = {
            "organ": settings.PLANSAUDE_ORGAN_NAME,
            "file_name": "RETORNO_CONSIGNAÇÕES",
            "reference": ref,
            "date": today,
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordPlan, "header", None, **config_header)

        log.debug("BASE SALARY FOR %s" % self.period)

        rubricas = {
            "7820": ["ME", "F"],  # Mensalidade Normal
            "7821": ["ME", "F"],  # Mensalidade Normal 4%
            "7822": ["ME", "F"],  # Mensalidade Normal 6%
            "7880": [
                "PA",
                None,
            ],  # Parcelamento. Verificar direto no folha_evento quantas parcelas foram solicitadas
            "7860": ["ME", 1],  # Mensalidade em atraso
            "7861": ["ME", 1],  # Mensalidade em atraso
            "7862": ["ME", 1],  # Mensalidade - diferença
            "7870": ["ME", 1],  # Mensalidade - diferença
            "7830": ["TX", 1],
            "7840": ["DI", "F"],
            "7850": ["CP", 1],
            "51000": ["ME", "F"],  # Mensalidade Normal
            "51001": ["DM", 1],  # Mensalidade - diferença
            "51006": ["DM", 1],  # Mensalidade - diferença
            "51400": [
                "PA",
                None,
            ],  # Parcelamento. Verificar direto no folha_evento quantas parcelas foram solicitadas
            "51300": ["TX", 1],
            "51100": ["DI", "F"],
            "51101": ["DD", "F"],
            "51106": ["DD", "F"],
            "51200": ["CP", 1],
        }

        query = Entry.objects.filter(
            contracheque__folha__periodo=self.period,
            evento__numero__in=list(rubricas.keys()),
        ).order_by("contracheque__servidor", "evento__numero", "pk")

        refused_query = (
            LoadedEntryHistory.objects.exclude(status=1)
            .filter(payroll__periodo=self.period, typeof="PLANSAUDE")
            .order_by("status")
        )

        base_pct = query.count() + refused_query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        for fe in query:

            conf_rubrica = rubricas.get(fe.evento.numero)

            group_records.add(
                "consignables",
                organ=settings.PLANSAUDE_ORGAN_COD,
                registration=fe.contracheque.servidor.matricula,
                cpf=fe.contracheque.servidor.pessoa_fisica.cpf,
                month=fe.reference_month,
                year=fe.reference_year,
                value=("%.2f" % fe.valor).replace(".", ","),
                type_of=conf_rubrica[0],
                percent=(
                    ("%d" % fe.pct)
                    if conf_rubrica[1] == "F" and conf_rubrica[0] == "ME" and fe.pct
                    else ""
                ),
                installments=conf_rubrica[1] if conf_rubrica[1] == "F" else fe.prazo,
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        for leh in refused_query:
            # conf_rubrica = rubricas.get(fe.evento.numero)
            # log.debug(u'LINE[%s]: %s' % (leh.typeof, leh.line_text))
            resgistration_number = leh.identification[0:15].strip()
            try:
                employee = Servidor.objects.get(matricula=resgistration_number)
            except Exception:
                employee = None

            group_records.add(
                "consignables",
                organ=settings.PLANSAUDE_ORGAN_COD,
                registration=resgistration_number,
                cpf=(
                    employee.pessoa_fisica.cpf
                    if employee and employee.pessoa_fisica
                    else ""
                ),
                month=leh.payroll.periodo.mes,
                year=leh.payroll.periodo.ano,
                value="0,00",
                type_of=leh.identification[-2:].strip(),
                refused_flag=1,
                refused_reason=14 if leh.status == 3 else 15,
                percent="",
                installments="F",
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo PLANSAÚDE RETORNO_CONSIGNAÇÕES.")

        return self.regs
        # ----------------------------------------------------------------------


class BasesFile(BasePlanSaudeFile):

    def get_records(self):

        log.debug(self.observer)
        self.observer.set("pct", 0.0)

        ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d/%m/%Y")

        config_header = {
            "organ": settings.PLANSAUDE_ORGAN_NAME,
            "file_name": "BASE_SALARIAL",
            "reference": ref,
            "date": today,
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordPlan, "header", None, **config_header)

        events = ["7820", "7821", "7822", "51000"]  # Rubricas de mensalidade

        # folha = models.Folha.objects.get(id=self.request.GET.get("folha"))
        events_payroll = Entry.objects.filter(
            contracheque__folha__periodo=self.period, evento__numero__in=events
        ).order_by("servidor")

        log.debug("BASE SALARY EVENTS: %s" % events_payroll.count())

        base_pct = events_payroll.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        for fe in events_payroll:
            group_records.add(
                "bases",
                organ=settings.PLANSAUDE_ORGAN_COD,
                registration=fe.servidor.matricula,  # Matrícula
                cpf=fe.servidor.pessoa_fisica.cpf,  # CPF
                month=self.period.mes,  # Mês de referencia da folha
                year=self.period.ano,  # Ano de referencia da folha
                base_value=("%.2f" % fe.valor_base).replace(".", ","),
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo PLANSAÚDE: BASES SALARIAIS")

        return self.regs
        # ----------------------------------------------------------------------


class DeparturesFile(BasePlanSaudeFile):

    def get_records(self):

        log.debug(self.observer)
        self.observer.set("pct", 0.0)

        ref = "%02d%04d" % (self.period.mes, self.period.ano)
        today = datetime.today().strftime("%d/%m/%Y")

        config_header = {
            "organ": settings.PLANSAUDE_ORGAN_NAME,
            "file_name": "AFASTAMENTOS",
            "reference": ref,
            "date": today,
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(RecordPlan, "header", None, **config_header)

        active_lips = LicencaInteresseParticular.objects.filter(estado=ATIVO).order_by(
            "servidor"
        )

        base_pct = active_lips.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        for lip in active_lips:
            group_records.add(
                "departures",
                organ=settings.PLANSAUDE_ORGAN_COD,
                registration=lip.servidor.matricula,  # Matrícula
                cpf=lip.servidor.pessoa_fisica.cpf,  # CPF
                departure_reason=2,
            )

            passo_pct += 1
            self.observer.set("pct", passo_pct)

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo PLANSAÚDE: AFASTAMENTOS")

        return self.regs
        # ----------------------------------------------------------------------
