# -*- coding: utf-8 -*-

from datetime import datetime

from contrib.protofile import GroupRecords, Protocol, Record
from contrib.utils import getLogger
from contrib.helpers import clear_to_ascii
from rh.gfp.generators.pasep.layouts import FPSFPASEP
from rh.gfp.models import ContraCheque as Paycheck
from rh.models import PIS_PASEP, UnidadeAdministrativa, Banco
from standard.models import Configuration


__name__ = "Banco do Brasil - PASEP FPS228"
__hid__ = "001"

log = getLogger(__name__)


class RecordPasep(Record):
    _protocol = FPSFPASEP
    _separator = ""


class File(Protocol):
    """
    =======================================================================
           |  H.F. - Header of File * - Reg 1
           | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
           |   |-----------------------------------------------
       F   |   | R.D. - Detail Record * - Reg 2
       I   |   |-----------------------------------------------
       L   |   | R.D. - Detail Record * - Reg 2
       E   |   |-----------------------------------------------
           |   | .
           |   | .
           |   | .
           | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
           | T.F. - Trailer of File * - Reg 9
    =======================================================================
    """

    def __init__(self, payroll, task):
        super(File, self).__init__()
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.banco = Banco.objects.get(numero=__hid__)
        self.cfg = Configuration.objects.get(application="gfp")
        uadm = self.cfg.get("orgao")
        self.email = self.cfg.get("email_gfp")
        self.uadm = UnidadeAdministrativa.objects.get(pk=uadm)
        self.payroll = payroll
        self.observer = task
        self.regs = []

    def get_records(self):

        log.debug(self.observer)
        self.observer.set("pct", 0.0)

        config_header = {
            "data_geracao": datetime.now().strftime("%d%m%Y"),
            "cnpj_entidade": self.uadm.pessoa_juridica.cnpj,
            "numero_remessa": 1,
            "agencia_controle": 3615,
            "digito_agencia_controle": 3,
            "data_pagamento": self.payroll.dt_pagamento.strftime("%d%m%Y"),
            "numero_convenio": 4587,
            "agencia_lancamento": 3615,
            "digito_agencia_lancamento": 3,
            "conta_lancamento": 80695,
            "digito_conta_lancamento": 1,
            "email": self.cfg.get("email_gfp", ""),
        }

        # Adicionando Header de Arquivo REG 1------------------------------------------
        self.observer.set("pctText", "Inserindo header de arquivo.")

        group_records = GroupRecords(
            RecordPasep, "fps900-1", "fps900-9", **config_header
        )

        query = Paycheck.objects.filter(folha=self.payroll).order_by("servidor")

        base_pct = query.count()
        passo_pct = 0

        self.observer.set("total", base_pct)
        self.observer.set("pct", passo_pct)
        list_persons = []
        for paycheck in query:
            if paycheck.servidor.pessoa_fisica.pk not in list_persons:
                list_persons.append(paycheck.servidor.pessoa_fisica.pk)
                endereco = (
                    paycheck.servidor.pessoa_fisica.address.all()[0]
                    if paycheck.servidor.pessoa_fisica.address.exists()
                    else None
                )
                group_records.add(
                    "fps900-2",
                    type_registro=2,
                    pasep=paycheck.servidor.pessoa_fisica.documento.get(
                        tipo_documento=PIS_PASEP
                    ).numero,
                    nome=clear_to_ascii(paycheck.servidor.pessoa_fisica.nome),
                    matricula=paycheck.servidor.matricula,
                    endereco=clear_to_ascii(endereco.logradouro) if endereco else "",
                    numero=(
                        endereco.numero if endereco and endereco.numero.isdigit() else 0
                    ),
                    complemento=(
                        clear_to_ascii(endereco.complemento) if endereco else ""
                    ),
                    bairro=clear_to_ascii(endereco.bairro) if endereco else "",
                    municipio=(
                        clear_to_ascii(endereco.municipio.nome)
                        if endereco and endereco.municipio
                        else ""
                    ),
                    uf=(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio and endereco.municipio.estado
                        else ""
                    ),
                    cep=endereco.cep if endereco else 0,
                )
            else:
                self.observer.message(
                    "Servidor %s ignorado por já constar no arquivo!"
                    % paycheck.servidor,
                    2,
                )
            passo_pct += 1
            self.observer.set("pct", passo_pct)

        group_records.update_trailer(
            total=group_records.count(),
        )

        self.regs = self.regs + group_records.get_records()

        self.observer.set("pctText", "Gerando arquivo PASEP FPS900.")

        return self.regs
        # ----------------------------------------------------------------------
