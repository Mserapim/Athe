# -*- coding: utf-8 -*-

import re
from datetime import datetime

from django.db.models import Q

from contrib.helpers import clear_to_ascii
from contrib.utils import getLogger
from rh.gfp.febrabam import LoteFebraban, Protocol
from rh.gfp.febrabam.layouts import BRADESCO500
from rh.gfp.models import DadoBancarioServidorFolha, FolhaEvento
from rh.models import Banco, Servidor, UnidadeAdministrativa
from rh.pensao.models import PensaoFolhaEvento

log = getLogger()

__name__ = "Banco Bradesco 500"
__hid__ = "237"


class File(Protocol):
    """
    =======================================================================
      |  H.A. - Header de Arquivo * - Reg 0
      | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
      |   |
      | L |
    A | O | R.D.L. - Registro de Detalhe do Lote 1 * - Reg 3A
    R | T |
    Q | E |
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

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def comp_registro(self, reg_a, reg_b, key="favorecido_cc_banco"):
        if reg_a.get(key) > reg_b.get(key):
            return 1
        elif reg_a.get(key) < reg_b.get(key):
            return -1
        else:
            return 0

    def __init__(self, conf):
        Protocol.__init__(self)
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.banco = Banco.objects.get(numero=__hid__)
        self.uadm = UnidadeAdministrativa.objects.get(
            pk=84
        )  # FIXME: int(cfg.itens.get(key = "orgao").value))
        self.observer = conf.get("observer") if "observer" in conf else None
        self.lotes = []
        self.remessa = 1
        self.folha = conf.get("folha")
        self.observer.set("pct", 0.0)

        header_arquivo = {
            "cod_convenio": self.banco.numero_convenio,
            "empresa_inscricao_numero": "01786078000146",
            "empresa_nome": "%s" % self.uadm,
            "numero_remessa": self.banco.get_sequencial(),
            "arquivo_data_geracao": datetime.now().strftime("%Y%m%d"),
            "arquivo_hora_geracao": datetime.now().strftime("%H%M%S"),
            "servico_numero_registro": 1,
        }

        # Adicionando Lotes REG 3------------------------------------------
        soma = 0.0
        lote = LoteFebraban(
            BRADESCO500["500-bradesco-pag-for-0"],
            BRADESCO500["500-bradesco-pag-for-9"],
            **header_arquivo
        )
        query = FolhaEvento.objects.filter(folha=self.folha)
        qr_servidores = list(query.order_by("servidor").values("servidor").distinct())
        base_pct = len(qr_servidores)
        passo_pct = 0.0
        self.observer.set(
            "pctText", "Lote correntistas: %s registro(s)" % lote.getCountDetalhes()
        )
        self.observer.set("pct", passo_pct / base_pct)
        for info in qr_servidores:
            s = Servidor.objects.get(pk=info["servidor"])
            passo_pct += 1.0
            # Verifica se esse servidor tem pensionista por morte
            if s.pensao_pagador.filter(
                ~Q(pensaomorte=None) & Q(data_inicio__lte=self.folha.dt_pagamento)
            ) and not info.get("pensao"):
                qr_servidores += [
                    {"servidor": s.id, "pensao": p, "tipo": "PM"}
                    for p in s.pensao_pagador.filter(
                        ~Q(pensaomorte=None)
                        & Q(data_inicio__lte=self.folha.dt_pagamento)
                    )
                ]
                log.debug(qr_servidores[-1])
                log.debug(qr_servidores[-1]["pensao"])
                log.debug(
                    qr_servidores[-1]["pensao"].pensionista
                    if qr_servidores[-1]["pensao"]
                    else "Sem Pensao"
                )
            else:
                # Verifica se esse servidor tem alimentando
                if s.pensao_pagador.filter(
                    ~Q(pensaoalimenticia=None)
                    & Q(data_inicio__lte=self.folha.dt_pagamento)
                ) and not info.get("pensao"):
                    qr_servidores += [
                        {"servidor": s.id, "pensao": p, "tipo": "PA"}
                        for p in s.pensao_pagador.filter(
                            ~Q(pensaoalimenticia=None)
                            & Q(data_inicio__lte=self.folha.dt_pagamento)
                        )
                    ]
                    log.debug(qr_servidores[-1])
                dbs = (
                    DadoBancarioServidorFolha.objects.filter(
                        Q(tipo_folha=self.folha.tipo_folha)
                        &
                        # TODO Alterar o 1° s.pessoa_fisica.pessoa_ptr para info.get('pensao').pensionista)
                        Q(
                            dado_bancario_pessoa__pessoa=(
                                info.get("pensao").pensionista
                                if info.get("pensao")
                                else s.pessoa_fisica.pessoa_ptr
                            )
                        )
                    )
                    .exclude(Q(data_vigencia__gt=self.folha.dt_pagamento))
                    .order_by("-data_vigencia")
                )
                if dbs.exists():
                    db = dbs[0].dado_bancario_pessoa
                    if db.banco == self.banco or (
                        self.banco.principal and db.banco.tem_convenio == 2
                    ):
                        credito = 0.00
                        # TODO Alterar o primeiro query para a query que tras as FolhaEventos dos pensionistas
                        query_folhaeventos = (
                            PensaoFolhaEvento.objects.filter(
                                Q(folha=self.folha)
                                & Q(pensao__pensionista=info.get("pensao").pensionista)
                            )
                            if info.get("pensao")
                            else query.filter(servidor=s)
                        )
                        for e in query_folhaeventos:
                            evento = (
                                e.folha_evento.evento
                                if info.get("pensao")
                                else e.evento
                            )
                            credito = (
                                (credito + float(e.valor))
                                if evento.tipo == "P"
                                else (credito - float(e.valor))
                            )
                        if (credito) > 0.001:
                            self.observer.set(
                                "pctText",
                                "Lote correntistas: %s registro(s)"
                                % (lote.getCountDetalhes() + 1),
                            )
                            self.observer.set("pct", (passo_pct / base_pct))
                            favorecido_inscricao_numero = info_complementares = ""
                            modalidade_pgto = 1
                            cpf = (
                                info.get("pensao").pensionista.cpf
                                if info.get("pensao")
                                else s.pessoa_fisica.cpf
                            )
                            favorecido_inscricao_numero = cpf[0:9] + "0000" + cpf[9:11]
                            if db.banco != self.banco:
                                info_complementares = (
                                    "C00000006"
                                    + ("%s" % db.tipo_conta).rjust(2, "0")
                                    + "".rjust(45, " ")
                                )
                                modalidade_pgto = 3 if credito < 3000.00 else 8
                            enderecos = (
                                s.pessoa_fisica.address.order_by("pk")
                                if not info.get("pensao")
                                else info.get("pensao").pensionista.address.order_by(
                                    "pk"
                                )
                            )
                            endereco = enderecos[0] if enderecos.exists() else ""
                            registro_transacao = {
                                "favorecido_inscricao_tipo": 1,
                                "favorecido_inscricao_numero": favorecido_inscricao_numero,
                                "favorecido_nome": "%s"
                                % clear_to_ascii(
                                    info.get("pensao").pensionista.nome
                                    if info.get("pensao")
                                    else s.pessoa_fisica.nome
                                ),
                                "favorecido_endereco": "%s"
                                % clear_to_ascii("%s" % endereco),
                                "favorecido_endereco_cep": (
                                    "%s" % endereco.cep[0:5] if endereco else 0
                                ),
                                "favorecido_endereco_complemento_cep": (
                                    "%s" % endereco.cep[5:8] if endereco else 0
                                ),
                                "favorecido_cc_banco": db.banco.numero,
                                "favorecido_cc_agencia_cod": re.sub(
                                    r"(\.|-)", "", db.agencia
                                )[0:-1],
                                "favorecido_cc_agencia_dv": re.sub(
                                    r"(\.|-)", "", db.agencia
                                )[-1],
                                "favorecido_cc_conta_cod": re.sub(
                                    r"(\.|-)", "", db.conta_corrente_completa
                                )[0:-1],
                                "favorecido_cc_conta_dv": re.sub(
                                    r"(\.|-)", "", db.conta_corrente_completa
                                )[-1],
                                "favorecido_num_pagamento": "%s%s"
                                % (
                                    ("%s" % self.folha.id).rjust(8, "0"),
                                    (
                                        "%s"
                                        % (
                                            info.get("pensao").pensionista.id
                                            if info.get("pensao")
                                            else s.pessoa_fisica.id
                                        )
                                    ).rjust(8, "0"),
                                ),
                                "credito_data_vencimento": self.folha.dt_pagamento.strftime(
                                    "%Y%m%d"
                                ),
                                "credito_data_emissao": datetime.now().strftime(
                                    "%Y%m%d"
                                ),
                                "credito_valor_doc": credito,
                                "credito_data_pgto": self.folha.dt_pagamento.strftime(
                                    "%Y%m%d"
                                ),
                                "modalidade_pgto": modalidade_pgto,
                                "info_complementares": info_complementares,
                                "info_empresa": "%s%+11s%+7s"
                                % (
                                    info.get("tipo") if info.get("pensao") else "MP",
                                    (
                                        info.get("pensao").pensionista.cpf
                                        if info.get("pensao")
                                        else s.matricula
                                    ),
                                    conf["folha"].id,
                                ),
                                "cod_lancamento": 469,
                                "favorecido_tipo_conta": db.tipo_conta,
                                "servico_numero_registro": lote.getCountDetalhes() + 2,
                            }
                            lote.addRegistro(
                                BRADESCO500["500-bradesco-pag-for-1"],
                                **registro_transacao
                            )
                            soma += credito
                else:
                    pass  # Notificar que o servidor não possui dado bancário

        # Adicionando Trailer de Arquivo REG 9 ----------------------------
        self.observer.set("pctText", "Inserindo trailer de arquivo.")
        lote.updateTrailer(
            controle_registro=9,
            total_registros=lote.getCountDetalhes() + 2,
            total_valor=soma,
            servico_numero_registro=lote.getCountDetalhes() + 2,
        )
        self.regs = self.regs + lote.getRegistros()
        self.lotes.append(lote)
        self.observer.set("pctText", "Gerando arquivo de crédito.")
        self.observer.set("pct", 1.0)
        # ----------------------------------------------------------------------
