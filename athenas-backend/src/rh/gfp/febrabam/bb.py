# -*- coding: utf-8 -*-

import re
from datetime import datetime

from contrib import protofile
from contrib.utils import getLogger
from contrib.helpers import clear_to_ascii
from rh.gfp.febrabam.layouts import FEBRABAN
from rh.gfp.models import ContraCheque
from rh.models import UnidadeAdministrativa
from standard.models import Configuration, RunCodeManager
from standard.models import RunCodeManager, Configuration

# __name__ = u"Banco do Brasil CNAB240"
__hid__ = "001"

log = getLogger(__name__)


class FebrabanRecord(protofile.Record):

    _protocol = FEBRABAN
    _separator = ""


@RunCodeManager.register("febraban-bb-240")
class File(protofile.Protocol):
    """Protofile.

    =======================================================================
          |  H.A. - Header de Arquivo * - Reg 0
          | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
          |   | H.L. - Header de Lote 1 * - Reg 1
          | L |-----------------------------------------------
        A | O | R.D.L. - Registro de Detalhe do Lote 1 * - Reg 3A
        R | T |-----------------------------------------------
        Q | E | R.D.L. - Registro de Detalhe do Lote 1 * - Reg 3B
        U | 1 |-----------------------------------------------
        I |   | T.L. - Trailer do Lote 1 * - Reg 5
        V |   |___________________________________________________
        O |   |
          | L |
          | O |
          | T |  LOTES OPCIONAIS, CASO TENHAM.
          | E |
          | 2 |
          |   |
          | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
          | T.A. - Trailer de Arquivo * - Reg 9
    =======================================================================
    """

    typeof = "GENBANK"
    title = "Banco do Brasil CNAB240"
    description = "Gerador febrabam do BB para arquivos de 240 posições!"

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def __extract_regs__(self):
        return self.nl.join([str(r) for r in self.get_records()]) + self.nl

    def __init__(self, payroll, convenant, task, log=None, *args):
        super(File, self).__init__()
        self.cfg_pensioner = Configuration.get_or_create("gfp")
        PENSIONSER_IN_FILE_BANK = (
            True
            if int(self.cfg_pensioner.get("bb_pensioner_file_bank", 0)) == "1"
            else False
        )
        self.log = log if log else getLogger(__name__)
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        employees = args[0] if args[0] else None
        self.employees = employees
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
        # self.observer.set('pct', 0.0)

        config_layout = {
            "controle_banco": self.bank.numero,
            "controle_lote": 0,
            "controle_registro": 0,
            "layout": "040",
            "empresa_inscricao_tipo": 2,  # 1 = CPF; 2 = CNPJ
            "empresa_inscricao_numero": (
                self.uadm.pessoa_juridica.cnpj if self.uadm_address else ""
            ),
            "empresa_convenio_contrato": self.convenant.convenant,
            "empresa_cc_agencia_cod": self.convenant.agency_cod,
            "empresa_cc_agencia_dv": self.convenant.agency_cod_dv,
            "empresa_cc_conta_cod": self.convenant.account_cod,
            "empresa_cc_conta_dv": self.convenant.account_cod_dv,
            "empresa_nome": "%s" % self.uadm,
            "nome_banco": self.bank.nome,
        }

        # Adicionando Header de Arquivo REG 0------------------------------------------
        config_header_file = config_layout
        config_header_file.update(
            {
                "arquivo_cod_remessa": 1,
                "arquivo_sequencia": self.convenant.counter,
                "arquivo_data_geracao": datetime.now().strftime("%d%m%Y"),
                "arquivo_hora_geracao": datetime.now().strftime("%H%M%S"),
                # Novos campos na versão do BB, porém todo o restante do layout está igual ao da FEBRABAN
                "filler3": "           CSP00000",
            }
        )
        self.observer.info(msg="Inserindo header de arquivo.", type_of=1)
        self.regs.append(  # Adicionando FebrabanRecord de HEADER DE ARQUIVO Reg: 0
            FebrabanRecord("240-geral-0-08.4", **config_header_file)
        )
        # Adicionando Lotes REG 3------------------------------------------
        config_header_lote = config_layout
        config_header_lote.update(
            {
                "controle_lote": 1,
                "controle_registro": 1,
                "servico_tipo": 30,
                "servico_forma_lancamento": 1,
                "layout": "043",
                "endereco_logradouro": (
                    self.uadm_address.logradouro if self.uadm_address else ""
                ),
                "endereco_numero": (
                    self.uadm_address.numero if self.uadm_address else ""
                ),
                "endereco_complemento": (
                    self.uadm_address.complemento if self.uadm_address else ""
                ),
                "endereco_cidade": (
                    self.uadm_address.municipio.nome if self.uadm_address else ""
                ),
                "endereco_cep": self.uadm_address.cep[0:5] if self.uadm_address else "",
                "endereco_complemento_cep": (
                    self.uadm_address.cep[-2:] if self.uadm_address else ""
                ),
                "endereco_estado": (
                    self.uadm_address.municipio.estado.sigla
                    if self.uadm_address
                    else ""
                ),
            }
        )

        lot_cc = protofile.GroupRecords(
            FebrabanRecord,
            "240-geral-1C-04.3",
            "240-geral-5-04.1",
            **config_header_lote
        )
        self.lots.append(lot_cc)

        config_header_lote.update(
            {
                "controle_lote": 2,
                "servico_forma_lancamento": 5,
                "servico_tipo": 98,
            }
        )
        lot_cp = protofile.GroupRecords(
            FebrabanRecord,
            "240-geral-1C-04.3",
            "240-geral-5-04.1",
            **config_header_lote
        )
        self.lots.append(lot_cp)

        config_header_lote.update(
            {
                "controle_lote": 3,
                "servico_forma_lancamento": 3,
                "servico_tipo": 98,
            }
        )
        lot_ted = protofile.GroupRecords(
            FebrabanRecord,
            "240-geral-1C-04.3",
            "240-geral-5-04.1",
            **config_header_lote
        )
        self.lots.append(lot_ted)

        sum_cc = sum_cp = sum_ted = 0

        if self.employees:
            query = (
                ContraCheque.objects.filter(
                    folha=self.payroll, servidor__id__in=self.employees
                )
                .exclude(employee_pays_pension=2, pensioner__isnull=True)
                .order_by("dado_bancario_pessoa__pessoa", "pensioner")
            )
        else:
            query = (
                ContraCheque.objects.filter(folha=self.payroll)
                .exclude(employee_pays_pension=2, pensioner__isnull=True)
                .order_by("dado_bancario_pessoa__pessoa", "pensioner")
            )
        query = (
            query.filter(pensioner__isnull=True)
            if not PENSIONSER_IN_FILE_BANK
            else query
        )

        pct = 100.0 / query.count()
        count = 0
        # self.observer.set('total', base_count)
        # self.observer.set('pct', count)

        for cc in query:

            count += 1

            db = cc.dado_bancario_pessoa
            if cc.total_liquido <= 0:
                # NOTIFY THIS
                continue
            if not db:
                # NOTIFY THIS
                continue
            if db.banco == self.bank and db.tipo_conta == 2:  # conta poupança
                current_lot = lot_cp
                sum_cp += cc.total_liquido
            elif db.banco != self.bank:
                # TED/DOC para clientes de outro banco      desconsidera bancos do excluded do convenio
                if (
                    self.convenant.type_convenant == 2
                    and db.banco not in self.convenant.excluded_bank.all()
                ):
                    current_lot = lot_ted
                    sum_ted += cc.total_liquido
                else:
                    continue  # Desconsidera clientes de outros bancos
            else:
                current_lot = lot_cc
                sum_cc += cc.total_liquido

            current_lot.add(
                "240-geral-3A-08.4",
                controle_lote=current_lot.header.get("controle_lote"),
                servico_numero_registro=current_lot.count() + 1,
                favorecido_camara=00,  # 18 if (positivo - negativo)>= 3000 else 700,
                favorecido_banco=db.banco.numero,
                favorecido_cc_agencia_cod=re.sub(r"(\.|-)", "", db.agencia)[0:-1],
                favorecido_cc_agencia_dv=re.sub(r"(\.|-)", "", db.agencia)[-1].upper(),
                favorecido_cc_conta_cod=re.sub(
                    r"(\.|-)", "", db.conta_corrente_completa
                )[0:-1],
                favorecido_cc_conta_dv=re.sub(
                    r"(\.|-)", "", db.conta_corrente_completa
                )[-1].upper(),
                favorecido_nome="%s"
                % re.sub(r"\W+", " ", clear_to_ascii(db.pessoa.nome)),
                # favorecido_nome="%s" % clear_to_ascii('teste'),
                credito_seu_numero="%020d" % cc.id,
                credito_data_pgto=self.payroll.dt_pagamento.strftime("%d%m%Y"),
                credito_valor_pgto=cc.total_liquido,
            )
            current_lot.add(
                "240-geral-3B-08.4",
                controle_lote=current_lot.header.get("controle_lote"),
                servico_numero_registro=current_lot.count() + 1,
                comple_favorecido_inscricao_numero=db.pessoa.pessoafisica.cpf,
                comple_cod_doc_favorecido="%015d" % cc.id,
            )

            self.observer.increment_progress(pct)
            # self.observer.set('pct', count)

        if lot_cc.count() > 0:
            lot_cc.update_trailer(
                controle_registro=5,
                totais_registros=lot_cc.count() + 2,
                totais_valor=sum_cc,
            )
            self.regs = self.regs + lot_cc.get_records()
        else:
            self.lots.remove(lot_cc)

        if lot_cp.count() > 0:
            lot_cp.update_trailer(
                controle_registro=5,
                totais_registros=lot_cp.count() + 2,
                totais_valor=sum_cp,
            )
            self.regs = self.regs + lot_cp.get_records()
        else:
            self.lots.remove(lot_cp)

        if lot_ted.count() > 0:
            lot_ted.update_trailer(
                controle_registro=5,
                totais_registros=lot_ted.count() + 2,
                totais_valor=sum_ted,
            )
            self.regs = self.regs + lot_ted.get_records()
        else:
            self.lots.remove(lot_ted)

        # self.observer.set('pctText', 'Inserindo trailer de arquivo.')
        self.regs.append(
            FebrabanRecord(
                "240-geral-9-08.4",
                controle_banco=self.bank.numero,
                controle_lote=9999,
                controle_registro=9,
                totais_lotes=len(self.lots),
                # Total de registros já inseridos no arquivo + o próprio trailer de arquivo
                totais_registros=len(self.regs) + 1,
            )
        )
        # self.observer.set('pctText', 'Gerando arquivo de crédito.')
