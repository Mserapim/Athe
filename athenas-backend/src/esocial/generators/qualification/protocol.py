# -*- coding: utf-8 -*-


from contrib.protofile import Protocol, Record, GroupRecords
from contrib.protofile import my_cmp
from esocial.generators.qualification.layouts import ESOCIALQUALIF
from esocial.models import RegistrationQualification

# from datetime import datetime
from contrib.utils import getLogger
from engine.models import NullTaskSession
from contrib.helpers import clear_to_ascii

import functools


log = getLogger(__name__)


class RecordQualif(Record):
    _protocol = ESOCIALQUALIF
    _separator = ";"

    def __str__(self):
        linha = ""

        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                pass
            else:
                if Record.is_empty(self.info[k]) and self.is_required(k):
                    l = self.__class__.get_required_value(
                        label=self._protocol[self.layout][k]["label"],
                        required=self._protocol[self.layout][k].get("required", 0),
                    )
                else:
                    l = self.prepare(k)
                try:
                    if linha:
                        linha += (
                            self._separator + l
                            if not type(l) is str
                            else self._separator + str(l)
                        )
                    else:
                        linha += l if not type(l) is str else str(l)
                except Exception as e:
                    log.exception(e)
        return linha + self._separator_on_end_line


class QualificationFile(Protocol):
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

    def __init__(self, task=NullTaskSession(), all_persons=True):
        super(QualificationFile, self).__init__()
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.observer = task
        self.regs = []
        self.all_persons = all_persons

    def __str__(self):
        return self.__extract_regs__()

    def __extract_regs__(self):
        return self.nl.join(["%s" % (r) for r in self.get_records()])

    def get_records(self):

        log.debug(self.observer)
        self.observer.set("pct", 0.0)

        # ref = "%02d%04d" % (self.period.mes, self.period.ano)
        # today = datetime.today().strftime("%d%m%Y")

        config_header = {}

        # Adicionando Header de Arquivo REG 1------------------------------------------
        # self.observer.set('pctText', 'Inserindo header de arquivo.')

        group_records = GroupRecords(RecordQualif, None, None, **config_header)
        # log.debug('BASE SALARY FOR %s' % self.period)

        log.info("Avaliando servidores obrigados a serem qualificados")
        # default_nis = '12030567126'  # Usar para qualificações que não necessitam de NIS. Ex.: ESTAGIARIO
        # dt_now = datetime.now().date()

        query_persons = RegistrationQualification.objects.exclude(status=2).order_by(
            "nome"
        )
        if not self.all_persons:
            query_persons = query_persons.exclude(qualified=True)

        base_pct = query_persons.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)

        for rq in query_persons:
            # valid_trainee = np.is_trainee() and np.tipo == 'E' and np.ativo
            # if valid_trainee or np.paychecks.filter(folha__periodo__ano=dt_now.year, folha__periodo__mes=dt_now.month).exists():
            pf = rq.natural_person
            cpf = rq.cpf.replace(".", "").replace("-", "")
            dn = rq.dn.strftime("%d%m%Y") if rq.dn else ""
            # nis = pf.documento.filter(tipo_documento__in=[5, 6]).first().numero if pf.documento.filter(tipo_documento__in=[5, 6]) else ''
            nis = rq.nis.replace(".", "").replace("-", "")

            if rq.type_of_person in [3, 4, 5, 6] and not nis:
                nis = RegistrationQualification.default_nis

            group_records.add(
                "persons",
                cpf=cpf,
                nome=clear_to_ascii(pf.nome),
                nis=nis,
                dn=dn,
            )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

            # print '%s;%s;%s;%s' % (cpf, nis, pf.nome, pf.data_nascimento.strftime('%d%m%Y'))

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo para qualificação eSocial.")

        return self.regs
