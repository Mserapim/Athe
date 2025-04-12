# -*- coding: utf-8 -*-

import re
from datetime import datetime

from contrib import protofile
from contrib.utils import getLogger
from contrib.helpers import clear_to_ascii
from rh.gfp.febrabam.layouts import SICREDI40
from rh.gfp.models import ContraCheque
from rh.models import UnidadeAdministrativa
from standard.models import Configuration, RunCodeManager
from django.utils.html import strip_tags
import re
from standard.models import RunCodeManager, Configuration

__hid__ = "226"

log = getLogger(__name__)


class FebrabanRecord(protofile.Record):

    _protocol = SICREDI40
    _separator = ""


@RunCodeManager.register("febraban-sicredi-40")
class File(protofile.Protocol):
    """
    =======================================================================
         A |  H.A. - Header de Arquivo * - Reg 0
         R | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
         Q |  R.D.L. - Registro de Detalhe d
         U |
         I |
         V |
         O |
     =======================================================================
    """

    typeof = "GENBANK"
    title = "BANCO COOPERATIVO SICREDI S.A. - BANSICREDI"
    description = "Gerador SICREDI!"

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def __extract_regs__(self):
        return self.nl.join([str(r) for r in self.get_records()]) + self.nl

    def __init__(self, payroll, convenant, task, log=None):
        super(File, self).__init__()
        self.log = log if log else getLogger(__name__)
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.cfg_pensioner = Configuration.get_or_create("gfp")
        PENSIONSER_IN_FILE_BANK = (
            True
            if int(self.cfg_pensioner.get("sicredi_pensioner_file_bank", 0)) == "1"
            else False
        )
        self.convenant = convenant
        self.bank = self.convenant.bank
        self.payroll = payroll
        self.cfg = Configuration.objects.get(application="gfp")
        try:
            self.uadm = UnidadeAdministrativa.objects.get(pk=int(self.cfg.get("orgao")))
            self.uadm_address = self.uadm.address.first()
        except Exception as e:
            raise e
        self.observer = task
        self.lots = []

        self.log.debug(self.observer)
        self.observer.set("pct", 0.0)

        config_layout = {
            "ano_geracao": self.payroll.dt_pagamento.strftime("%y"),
            "mes_geracao": self.payroll.dt_pagamento.strftime("%m"),
            "dia_geracao": self.payroll.dt_pagamento.strftime("%d"),
        }
        query = ContraCheque.objects.filter(
            folha=self.payroll, dado_bancario_pessoa__banco__pk=self.bank.pk
        ).order_by("servidor__matricula", "pensioner")
        query = (
            query.filter(pensioner__isnull=True)
            if not PENSIONSER_IN_FILE_BANK
            else query
        )

        sum_cc = 0
        for cc in query:
            sum_cc = sum_cc + cc.total_liquido

        # Adicionando Header de Arquivo REG 0------------------------------------------
        config_header_file = config_layout
        config_header_file.update({"total_linhas": len(query), "valor_total": sum_cc})

        self.observer.set("pctText", "Inserindo header de arquivo.")
        self.regs.append(  # Adicionando FebrabanRecord de HEADER DE ARQUIVO Reg: 0
            FebrabanRecord("40-sicredi-head", **config_header_file)
        )
        # Adicionando detalhe linha 3------------------------------------------
        config_detalhe_linha = config_layout
        base_count = query.count()
        count = 0

        self.observer.set("total", base_count)
        self.observer.set("pct", count)

        for cc in query:

            count += 1

            db = cc.dado_bancario_pessoa
            if cc.total_liquido <= 0:
                # NOTIFY THIS
                continue
            if not db:
                # NOTIFY THIS
                continue
            if db.banco == self.bank and db.tipo_conta == 1:
                config_detalhe_linha.update(
                    {
                        "favorecido_cc_conta": db.conta_corrente_completa[0:-1],
                        "favorecido_cc_conta_dv": db.conta_corrente_completa[-1],
                        "matricula": str(cc.servidor.matricula)[-4:],
                        "numero_linha": len(self.regs),
                        "valor": cc.total_liquido,
                    }
                )

                self.regs.append(  # Adicionando FebrabanRecord de HEADER DE ARQUIVO Reg: 0
                    FebrabanRecord("40-sicredi-detalhe", **config_detalhe_linha)
                )

                self.observer.set("pctText", "Créditos: %s registro(s)" % (count))
                self.observer.set("pct", count)

        self.observer.set("pctText", "Gerando arquivo de crédito.")
