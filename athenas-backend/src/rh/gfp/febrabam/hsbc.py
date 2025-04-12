# -*- coding: utf-8 -*-

import re
from datetime import datetime

from django.db.models import Q

from contrib.helpers import clear_to_ascii
from rh.gfp.febrabam import LoteFebraban, Protocol, Registro
from rh.gfp.models import DadoBancarioServidorFolha, FolhaEvento
from rh.models import Banco, Servidor, UnidadeAdministrativa
from rh.pensao.models import PensaoFolhaEvento

__name__ = "Banco HSBC"
__hid__ = "399"


class File(Protocol):
    """
    =======================================================================
      |  H.A. - Header de Arquivo * - Reg 0
      | -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
      |   | H.L. - Header de Lote 1 * - Reg 1
      | L |-----------------------------------------------
    A | O | R.D.L. - Registro de Detalhe do Lote 1 * - Reg 3A
    R | T |-----------------------------------------------
    Q | E | R.D.L. - Retistro de Detalhe do Lote 1 * - Reg 3B
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

    def __init__(self, conf):
        Protocol.__init__(self)
        #        self.nl         = '\r\n' #Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.banco = Banco.objects.get(numero=__hid__)
        self.uadm = UnidadeAdministrativa.objects.get(
            pk=84
        )  # FIXME: int(cfg.itens.get(key = "orgao").value))
        self.observer = conf.get("observer") if "observer" in conf else None
        self.lotes = []

        self.observer.set("pct", 0.0)

        config_layout = {
            "controle_banco": self.banco.numero,
            "controle_lote": 0,
            "controle_registro": 0,
            "empresa_inscricao_tipo": 2,  # 1 = CPF; 2 = CNPJ
            "empresa_inscricao_numero": "01786078000146",  # FIXME
            "empresa_convenio_contrato": self.banco.numero_convenio,
            "empresa_cc_agencia_cod": self.banco.agencia,
            "empresa_cc_conta_cod": self.banco.conta,
            "empresa_cc_conta_dv": self.banco.dv_conta[0],
            "empresa_cc_dv": self.banco.dv_conta[1],
            "empresa_nome": "%s" % self.uadm,
            "nome_banco": self.banco.nome,
        }

        # Adicionando Header de Arquivo REG 0------------------------------------------
        config_header_arquivo = config_layout
        config_header_arquivo.update(
            {
                "arquivo_cod_remessa": 1,
                "arquivo_sequencia": self.banco.get_sequencial(),
                "arquivo_data_geracao": datetime.now().strftime("%d%m%Y"),
                "arquivo_hora_geracao": datetime.now().strftime("%H%M%S"),
            }
        )
        self.observer.set("pctText", "Inserindo header de arquivo.")
        self.regs.append(  # Adicionando Registro de HEADER DE ARQUIVO Reg: 0
            Registro("240-hsbc-0-04.1", **config_header_arquivo)
        )
        # Adicionando Lotes REG 3------------------------------------------
        config_header_lote = config_layout
        config_header_lote.update(
            {
                "controle_lote": len(self.lotes) + 1,
                "controle_registro": 1,
                "servico_tipo": 30,
                "servico_forma_lancamento": 1,
                "layout": "020",
                "endereco_logradouro": "QD 202 NORTE, AV LO 4, CONJ 3",
                "endereco_numero": 0,
                "endereco_complemento": "LTS 5 e 6",
                "endereco_cidade": "PALMAS",
                "endereco_cep": 77006,
                "endereco_complemento_cep": 214,
                "endereco_estado": "TO",
                "comprovante_pgto": "N",
            }
        )

        soma = 0.0
        lote = LoteFebraban("240-hsbc-1C-04.1", "240-hsbc-5-04.1", **config_header_lote)
        query = FolhaEvento.objects.filter(folha=conf["folha"])
        qr_servidores = list(query.order_by("servidor").values("servidor").distinct())
        base_pct = len(qr_servidores)
        passo_pct = 0.0
        self.observer.set(
            "pctText", "Lote correntistas: %s registro(s)" % lote.getCountDetalhes()
        )
        self.observer.set("pct", passo_pct / base_pct)
        list_servidores_doc = []
        for info in qr_servidores:
            s = Servidor.objects.get(pk=info["servidor"])
            passo_pct += 1.0
            # Verifica se esse servidor tem pensionista por morte
            if s.pensao_pagador.filter(
                ~Q(pensaomorte=None) & Q(data_inicio__lte=conf["folha"].dt_pagamento)
            ) and not info.get("pensao"):
                qr_servidores += [
                    {"servidor": s.id, "pensao": p, "tipo": "PM"}
                    for p in s.pensao_pagador.filter(
                        ~Q(pensaomorte=None)
                        & Q(data_inicio__lte=conf["folha"].dt_pagamento)
                    )
                ]
            else:
                # Verifica se esse servidor tem alimentando
                if s.pensao_pagador.filter(
                    ~Q(pensaoalimenticia=None)
                    & Q(data_inicio__lte=conf["folha"].dt_pagamento)
                ) and not info.get("pensao"):
                    qr_servidores += [
                        {"servidor": s.id, "pensao": p, "tipo": "PA"}
                        for p in s.pensao_pagador.filter(
                            ~Q(pensaoalimenticia=None)
                            & Q(data_inicio__lte=conf["folha"].dt_pagamento)
                        )
                    ]
                dbs = (
                    DadoBancarioServidorFolha.objects.filter(
                        Q(tipo_folha=conf["folha"].tipo_folha)
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
                    .exclude(Q(data_vigencia__gt=conf["folha"].dt_pagamento))
                    .order_by("-data_vigencia")
                )
                if dbs.count() and dbs[0].dado_bancario_pessoa.banco == self.banco:
                    db = dbs[0].dado_bancario_pessoa
                    credito = 0.00
                    # TODO Alterar o primeiro query para a query que tras as FolhaEventos dos pensionistas
                    query_folhaeventos = (
                        PensaoFolhaEvento.objects.filter(
                            Q(folha=conf["folha"])
                            & Q(pensao__pensionista=info.get("pensao").pensionista)
                        )
                        if info.get("pensao")
                        else query.filter(servidor=s)
                    )
                    for e in query_folhaeventos:
                        evento = (
                            e.folha_evento.evento if info.get("pensao") else e.evento
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
                        self.observer.set("pct", (passo_pct / base_pct) * 0.5)
                        lote.addRegistro(
                            "240-hsbc-3A-04.1",
                            controle_banco=self.banco.numero,
                            servico_numero_registro=lote.getCountDetalhes() + 1,
                            favorecido_camara=18 if credito >= 3000 else 700,
                            favorecido_banco=db.banco.numero,
                            favorecido_cc_agencia_cod=re.sub(r"(\.|-)", "", db.agencia),
                            favorecido_cc_conta_cod=re.sub(
                                r"(\.|-)", "", db.conta_corrente_completa
                            )[0:-1],
                            favorecido_cc_conta_dv=re.sub(
                                r"(\.|-)", "", db.conta_corrente_completa
                            )[-1],
                            favorecido_nome="%s"
                            % clear_to_ascii(
                                info.get("pensao").pensionista.nome
                                if info.get("pensao")
                                else s.pessoa_fisica.nome
                            ),
                            credito_seu_numero="%s%04d%06d"
                            % (
                                datetime.now().strftime("%y%m%d"),
                                conf["folha"].tipo_folha.id,
                                (
                                    info.get("pensao").pensionista.id
                                    if info.get("pensao")
                                    else s.pessoa_fisica.id
                                ),
                            ),
                            credito_data_pgto=conf["folha"].dt_pagamento.strftime(
                                "%d%m%Y"
                            ),
                            credito_moeda_tipo="R$",
                            credito_valor_pgto=credito,
                            pagador_efetivo="PROCURADORIA GERAL DE JUSTICA",
                        )
                        soma += credito
                else:
                    # Caso em que esse servidor vai receber via DOC/TED por esse banco
                    if (
                        self.banco.principal
                        and dbs.count()
                        and dbs[0].dado_bancario_pessoa.banco.tem_convenio == 2
                    ):
                        info["dado_bancario"] = dbs[0].dado_bancario_pessoa
                        info["servidor"] = s
                        list_servidores_doc.append(info)
        lote.updateTrailer(
            controle_registro=5,
            totais_registros=lote.getCountDetalhes() + 2,
            totais_valor=soma,
        )
        self.regs = self.regs + lote.getRegistros()
        self.lotes.append(lote)

        # Adicionando Lote REG 3 - DOC/TED --------------------------------------
        if self.banco.principal:
            passo_pct = soma = 0.0
            base_pct = len(list_servidores_doc)
            config_header_lote.update(
                {
                    "controle_lote": len(self.lotes) + 1,
                    "servico_forma_lancamento": 3,
                }
            )
            lote2 = LoteFebraban(
                "240-hsbc-1C-04.1", "240-hsbc-5-04.1", **config_header_lote
            )
            for info in list_servidores_doc:
                s = info["servidor"]
                db = info["dado_bancario"]
                credito = 0.0
                for e in query.filter(servidor=s):
                    credito = (
                        (credito + float(e.valor))
                        if e.evento.tipo == "P"
                        else (credito - float(e.valor))
                    )
                if (credito) > 0:
                    passo_pct += 1.0
                    self.observer.set(
                        "pctText",
                        "Lote não correntistas: %s registros(s)."
                        % (lote2.getCountDetalhes() + 1),
                    )
                    self.observer.set("pct", (passo_pct / base_pct) * 0.5 + 0.5)
                    lote2.addRegistro(
                        "240-hsbc-3A-04.1",
                        controle_banco=self.banco.numero,
                        servico_numero_registro=lote.getCountDetalhes() + 1,
                        favorecido_camara=18 if credito >= 3000 else 700,
                        favorecido_banco=db.banco.numero,
                        favorecido_cc_agencia_cod=re.sub(r"(\.|-)", "", db.agencia),
                        favorecido_cc_conta_cod=re.sub(
                            r"(\.|-)", "", db.conta_corrente_completa
                        )[0:-1],
                        favorecido_cc_conta_dv=re.sub(
                            r"(\.|-)", "", db.conta_corrente_completa
                        )[-1],
                        favorecido_nome="%s"
                        % clear_to_ascii(
                            info.get("pensao").pensionista.nome
                            if info.get("pensao")
                            else s.pessoa_fisica.nome
                        ),
                        credito_seu_numero="%s%+11s"
                        % (
                            info.get("tipo") if info.get("pensao") else "MP",
                            (
                                info.get("pensao").pensionista.cpf
                                if info.get("pensao")
                                else s.matricula
                            ),
                        ),
                        credito_data_pgto=conf["folha"].dt_pagamento.strftime("%d%m%Y"),
                        credito_moeda_tipo="R$",
                        credito_valor_pgto=credito,
                        pagador_efetivo="PROCURADORIA GERAL DE JUSTICA",
                    )
                    lote2.addRegistro(
                        "240-hsbc-3B-08.4",
                        controle_banco=self.banco.numero,
                        controle_lote=len(self.lotes) + 1,
                        servico_numero_registro=lote2.getCountDetalhes() + 1,
                        comple_favorecido_tipo=1,
                        comple_favorecido_inscricao_numero=(
                            info.get("pensao").pensionista.cpf
                            if info.get("pensao")
                            else s.pessoa_fisica.cpf
                        ),
                    )
                    soma += credito
            lote2.updateTrailer(
                controle_registro=5,
                totais_registros=lote2.getCountDetalhes() + 2,
                totais_valor=soma,
            )
            self.regs = self.regs + lote2.getRegistros()
            self.lotes.append(lote2)
        # Adicionando Trailer de Arquivo REG 9 ----------------------------
        self.observer.set("pctText", "Inserindo trailer de arquivo.")
        self.regs.append(
            Registro(
                "240-hsbc-9-04.1",
                controle_banco=self.banco.numero,
                controle_lote=9999,
                controle_registro=9,
                totais_lotes=len(self.lotes),
                # Total de registros já inseridos no arquivo + o próprio trailer de arquivo
                totais_registros=len(self.regs) + 1,
            )
        )
        self.observer.set("pctText", "Gerando arquivo de crédito.")
        self.observer.set("pct", 1.0)
        # ----------------------------------------------------------------------
