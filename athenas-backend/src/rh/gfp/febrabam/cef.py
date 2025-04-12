# -*- coding: utf-8 -*-

import re
from datetime import datetime

from django.db.models import Q

from contrib.helpers import clear_to_ascii
from rh.gfp.febrabam import Protocol, Registro
from rh.gfp.models import DadoBancarioServidorFolha, FolhaEvento
from rh.models import Banco, Servidor, UnidadeAdministrativa
from rh.pensao.models import PensaoFolhaEvento

__name__ = "Caixa Econômica Federal"
__hid__ = "104"



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
        self.nl = '\r\n'  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.banco = Banco.objects.get(numero=__hid__)
        self.uadm = UnidadeAdministrativa.objects.get(pk=84)  # FIXME: int(cfg.itens.get(key = "orgao").value))
        self.observer = conf.get('observer') if 'observer' in conf else None
        self.lotes = []

        self.observer.set('pct', 0.0)
        config_layout = {
            'cod_convenio': self.banco.numero_convenio,
            'empresa_nome': "%s" % self.uadm,
            'banco_cod': self.banco.numero,
            'banco_nome': self.banco.nome,
            'data_movimento': datetime.now().strftime("%Y%m%d"),
            'numero_sequencial_arquivo': self.banco.get_sequencial(),
        }

        # Adicionando Header de Arquivo REG 0------------------------------------------
        config_header_arquivo = config_layout

        self.observer.set('pctText', 'Inserindo header de arquivo.')
        self.regs.append(  # Adicionando Registro de HEADER DE ARQUIVO Reg: 0
            Registro('150-cef-A-04.0', **config_header_arquivo)
        )
        # Adicionando Registros E ------------------------------------------

        soma = 0.0
        query = FolhaEvento.objects.filter(folha=conf["folha"])
        qr_servidores = list(query.order_by('servidor').values('servidor').distinct())
        base_pct = len(qr_servidores)
        passo_pct = 0.0
        list_servidores_doc = []
        for info in qr_servidores:
            s = Servidor.objects.get(pk=info['servidor'])
            passo_pct += 1.0
            # Verifica se esse servidor tem pensionista por morte
            if s.pensao_pagador.filter(
                    ~Q(pensaomorte=None) &
                    Q(data_inicio__lte=conf["folha"].dt_pagamento)) and not info.get('pensao'):
                qr_servidores += [{'servidor': s.id, 'pensao': p, 'tipo': 'PM'}
                                  for p in s.pensao_pagador.filter(~Q(pensaomorte=None) &
                                                                   Q(data_inicio__lte=conf["folha"].dt_pagamento))]
            else:
                # Verifica se esse servidor tem alimentando
                if s.pensao_pagador.filter(~
                                           Q(pensaoalimenticia=None) &
                                           Q(data_inicio__lte=conf["folha"].dt_pagamento)) and not info.get('pensao'):
                    qr_servidores += [{'servidor': s.id, 'pensao': p, 'tipo': 'PA'} for p in s.pensao_pagador.filter(
                        ~Q(pensaoalimenticia=None) & Q(data_inicio__lte=conf["folha"].dt_pagamento))]
                dbs = DadoBancarioServidorFolha.objects.filter(
                    Q(tipo_folha=conf["folha"].tipo_folha) &
                    # TODO Alterar o 1° s.pessoa_fisica.pessoa_ptr para info.get('pensao').pensionista)
                    Q(dado_bancario_pessoa__pessoa=(info.get('pensao').pensionista if info.get(
                        'pensao') else s.pessoa_fisica.pessoa_ptr))
                ).exclude(Q(data_vigencia__gt=conf["folha"].dt_pagamento)).order_by('-data_vigencia')
                if dbs.count() and dbs[0].dado_bancario_pessoa.banco == self.banco:
                    db = dbs[0].dado_bancario_pessoa
                    credito = 0.00
                    # TODO Alterar o primeiro query para a query que tras as FolhaEventos dos pensionistas
                    query_folhaeventos = PensaoFolhaEvento.objects.filter(
                        Q(folha=conf["folha"]) &
                        Q(pensao__pensionista=info.get('pensao').pensionista)) if info.get(
                        'pensao') else query.filter(servidor=s)
                    for e in query_folhaeventos:
                        evento = e.evento
                        credito = (credito + float(e.valor)) if evento.tipo == 'P' else (credito - float(e.valor))
                    if(credito) > 0.001:
                        self.observer.set('pctText', 'Lote correntistas: %s registro(s)' % (len(self.regs) + 1))
                        self.observer.set('pct', (passo_pct / base_pct) * 0.5)
                        self.regs.append(
                            Registro('150-cef-E-04.0',
                                     id_cliente_empresa="%s%s" % (
                                         info.get('tipo') if info.get('pensao') else '', s.matricula),
                                     agencia_cod=re.sub(r'(\.|-)', '', db.agencia),
                                     id_cliente_banco=re.sub(r'(\.|-)', '', db.conta_corrente_completa).rjust(12, '0'),
                                     data_vencimento=conf["folha"].dt_pagamento.strftime("%Y%m%d"),
                                     valor=credito,
                                     informacao="%s%s%+11s%+7s" % (
                                        clear_to_ascii((
                                            info.get('pensao').pensionista.nome if info.get('pensao') else s.pessoa_fisica.nome
                                        )[0:40].ljust(40),
                                        info.get('tipo') if info.get('pensao') else 'MP',
                                        info.get('pensao').pensionista.cpf if info.get('pensao') else s.matricula,
                                        conf["folha"].id
                                     ),
                                     numero_agendamento_cliente=len(self.regs) + 1,
                                     numero_sequencial_registro=len(self.regs) + 1,
                                     cod_movimento=2
                                     )
                        )
                        soma += credito
                else:
                    # Caso em que esse servidor vai receber via DOC/TED por esse banco
                    if self.banco.principal and dbs.count() and dbs[0].dado_bancario_pessoa.banco.tem_convenio == 2:
                        list_servidores_doc.append({'servidor': s, 'dado_bancario': dbs[0].dado_bancario_pessoa})
        # Adicionando Trailer de Arquivo REG 9 ----------------------------
        self.observer.set('pctText', 'Inserindo trailer de arquivo.')
        self.regs.append(  # Adicionando Registro de TRAILER DE ARQUIVO Reg: 9
            Registro('150-cef-Z-04.0',
                     total_valor=soma,
                     total_registros=len(self.regs) + 1,
                     numero_sequencial_registro=len(self.regs),
                     )
        )
        self.observer.set('pctText', 'Gerando arquivo de crédito.')
        self.observer.set('pct', 1.0)
        # ----------------------------------------------------------------------
