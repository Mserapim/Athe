# -.- coding: utf-8 -.-
from edocs.protocolo.models import Movimentacao
from edocs.protocolo.const import MIDIA_ORIGEM
from contrib.utils import getLogger
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery

log = getLogger()


class Query(object):

    def __init__(self, **kwargs):
        super(Query, self).__init__()


# EDOCBoxQuery(servidor=Servidor.objects.get(matricula='84008'), lotacoes=[554], lotacoes_protocolo_geral=[None], valor=None).escreve_tabela([])


class EDOCBoxQuery(Query):

    def __init__(self, servidor, lotacoes, lotacoes_protocolo_geral=[], valor=None):
        # super(self.__class__, self).__init__(**kwargs)
        self.servidor = servidor
        self.lotacoes = lotacoes
        self.lotacoes_protocolo_geral = lotacoes_protocolo_geral
        self.valor = valor

    @classmethod
    def get_role_exclude(cls):
        return ~Q(protocolo__processo=None) | ~Q(with_workflow=False)

    def get_caixa_entrada(self):
        # return Movimentacao.objects.filter(self.get_regra_caixa_entrada())
        return Movimentacao.objects.filter(
            self.get_regra_caixa_entrada()
        ).select_related(
            "protocolo",
            "lotacao_origem",
            "lotacao_destino",
            "lotacao_criacao",
            "servidor_origem",
            "servidor_destino",
            "destinatario",
        )

    def get_caixa_entrada_departamento(self):
        # return Movimentacao.objects.filter(self.get_qdepartamento_entrada())
        return Movimentacao.objects.filter(
            self.get_qdepartamento_entrada()
        ).select_related(
            "protocolo",
            "lotacao_origem",
            "lotacao_destino",
            "lotacao_criacao",
            "servidor_origem",
            "servidor_destino",
            "destinatario",
        )

    def get_caixa_saida(self):
        # return Movimentacao.objects.filter(self.get_regra_caixa_saida())
        return Movimentacao.objects.filter(self.get_regra_caixa_saida()).select_related(
            "protocolo",
            "lotacao_origem",
            "lotacao_destino",
            "lotacao_criacao",
            "servidor_origem",
            "servidor_destino",
            "destinatario",
        )

    def get_caixa_saida_refactoring_original(self):
        return Movimentacao.objects.filter(
            self.get_regra_caixa_saida_refactoring_original()
        ).select_related(
            "protocolo",
            "lotacao_origem",
            "lotacao_destino",
            "lotacao_criacao",
            "servidor_origem",
            "servidor_destino",
            "destinatario",
        )

    def get_qpessoal_entrada(self):
        qservidor_destino = Q(servidor_destino=self.servidor)
        qdestinatario = Q(destinatario=self.servidor.pessoa_fisica)
        qpessoal = qdestinatario | qservidor_destino
        return qpessoal

    def get_qdepartamento_entrada(self):
        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso
        qservidor_destino_none = Q(servidor_destino=None)
        qdestino_none = Q(lotacao_destino=None)
        qdestinatario_none = Q(destinatario=None)
        qlotacao_origem = Q(lotacao_origem__in=self.lotacoes)
        qdestino_destinatario_none_e_lotacao_origem = Q(
            qdestino_none
            & qdestinatario_none
            & qlotacao_origem
            & qservidor_destino_none
        )
        #        qdestino_destinatario_none_e_lotacao_origem = Q(qdestino_none & qdestinatario_none & qlotacao_origem)
        #        qdestino_destinatario_none_e_lotacao_origem = Q(qdestinatario_none & qlotacao_origem)
        qlotacao_destino = Q(lotacao_destino__in=self.lotacoes)
        #        qdestino_not_none_qdestinatario_none_qlotacao_destino = qdestinatario_none & qlotacao_destino & qservidor_destino_none
        qdestino_not_none_qdestinatario_none_qlotacao_destino = (
            qdestinatario_none & qlotacao_destino
        )
        #        log.debug("qdestino_not_none_qdestinatario_none_qlotacao_destino %s" % Movimentacao.objects.filter(qdestino_not_none_qdestinatario_none_qlotacao_destino).count())
        #        log.debug("qdestino_destinatario_none_e_lotacao_origem %s" % Movimentacao.objects.filter(qdestino_destinatario_none_e_lotacao_origem).count())
        # qdepartamento = qnao_sigiloso & Q(qdestino_destinatario_none_e_lotacao_origem | qdestino_not_none_qdestinatario_none_qlotacao_destino)
        qdepartamento = qnao_sigiloso & Q(
            qdestino_destinatario_none_e_lotacao_origem
            | qdestino_not_none_qdestinatario_none_qlotacao_destino
        )
        qdepartamento = qdepartamento | Q(
            Q(qsigiloso & qdestinatario_none)
            & Q(
                qdestino_destinatario_none_e_lotacao_origem
                | qdestino_not_none_qdestinatario_none_qlotacao_destino
            )
        )
        return qdepartamento

    def get_qgeral_entrada(self):
        # TODO: VERIFICAR AQUI NA ENTRADA GERAL
        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso
        qlotacao_criacao = Q(lotacao_criacao__in=self.lotacoes_protocolo_geral)
        qlotacao_destino_none_lotacao_criacao = (
            Q(lotacao_destino=None) & qlotacao_criacao
        )
        #        qlotacao_criacao_none_lotacao_destino = Q(lotacao_criacao = None, lotacao_destino__in=self.lotacoes_protocolo_geral)
        qlotacao_criacao_none_lotacao_destino = Q(
            lotacao_criacao=None,
            lotacao_destino__in=self.lotacoes_protocolo_geral,
            destinatario=None,
        )
        qgeral = qnao_sigiloso & Q(
            qlotacao_criacao
            | qlotacao_destino_none_lotacao_criacao
            | qlotacao_criacao_none_lotacao_destino
        )
        return qgeral

    def get_regra_caixa_entrada(self):
        # qdefault= Q(encaminhado=False) & Q(protocolo__excluido=False))
        qdefault = Q(encaminhado=False, protocolo__excluido=False)

        #        log.debug("e pessoal %s " % Movimentacao.objects.filter(qdefault & self.get_qpessoal_entrada()).exclude(EDOCBoxQuery.get_finalizado_recebido()).count())
        #        log.debug("e departamento %s " % Movimentacao.objects.filter(qdefault & self.get_qdepartamento_entrada()).exclude(EDOCBoxQuery.get_finalizado_recebido()).count())
        #        log.debug("e geral %s " % Movimentacao.objects.filter(qdefault & self.get_qgeral_entrada()).exclude(EDOCBoxQuery.get_finalizado_recebido()).count())

        q = qdefault & Q(
            self.get_qpessoal_entrada()
            | self.get_qdepartamento_entrada()
            | self.get_qgeral_entrada()
        )

        if self.valor:
            q = q & self.get_qbusca(self.valor)
        #        if self.valor:
        #            q = Q(q & self.get_qbusca(self.valor) & Q(self.get_qpessoal_entrada() | self.get_qdepartamento_entrada() | self.get_qgeral_entrada()))
        #        else:
        #            q = Q(q & Q(self.get_qpessoal_entrada() | self.get_qdepartamento_entrada() | self.get_qgeral_entrada()))
        return q

    def get_regra_caixa_saida_refactoring_original(self):

        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso

        qpasso_maoirq_zero = Q(passo__gt=0)
        qnao_excluido = Q(protocolo__excluido=False)
        qdefault = Q(qnao_excluido & qpasso_maoirq_zero)

        qservidor_origem = Q(servidor_origem=self.servidor.pk)
        qpessoal = qservidor_origem
        # RETIRADO POIS NA SAÍDA NORMAL DEVEM APARECER OS ENVIADOS POR MIM, NÃO OQ RECEBO
        # TODO: ANALISAR CAIXA DE SAÍDA DE CAIXAS DE PROTOCOLO GERAL
        # qpessoal = qservidor_origem | Q(Q(servidor_destino=self.servidor.pk) | Q(destinatario=self.servidor.pessoa_fisica.pk))

        qlotacao_destino_none = Q(lotacao_destino=None)
        qlotacao_destino_nao_none = ~qlotacao_destino_none
        qdestinatario_none = Q(destinatario=None)
        qdestinatario_nao_none = ~qdestinatario_none
        qlotacao_origem = Q(lotacao_origem__in=self.lotacoes)
        qservidor_destino_none = Q(lotacao_destino=None)
        qservidor_destino_nao_none = ~qservidor_destino_none
        qlotacao_origem_lotacao_destino_nao_none = (
            qlotacao_origem & qlotacao_destino_nao_none
        )
        qlotacao_origem_servidor_destino_nao_none = Q(
            qlotacao_origem & qservidor_destino_nao_none
        ) | Q(qlotacao_origem & qdestinatario_nao_none)
        qdepartamento = qnao_sigiloso & Q(
            qlotacao_origem_servidor_destino_nao_none
            | qlotacao_origem_lotacao_destino_nao_none
        )

        qpasso_eq_1 = Q(passo=1)
        qlotacao_criacao = Q(
            protocolo__lotacao_criacao__in=self.lotacoes_protocolo_geral
        )
        qlotacao_criacao_lotacao_destino_nao_none = (
            qlotacao_criacao & qlotacao_destino_nao_none
        )
        qlotacao_criacao_servidor_destino_destinatario_nao_none = Q(
            qlotacao_criacao & qservidor_destino_nao_none
        ) | Q(qlotacao_criacao & qdestinatario_nao_none)
        qgeral = (
            qnao_sigiloso
            & qpasso_eq_1
            & Q(
                qlotacao_criacao_servidor_destino_destinatario_nao_none
                | qlotacao_criacao_lotacao_destino_nao_none
            )
        )

        q = qdefault & Q(qpessoal | qdepartamento | qgeral)

        if self.valor:
            q = q & self.get_qbusca(self.valor)

        return q

    def get_regra_caixa_saida(self):

        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso

        qpasso_maoirq_zero = Q(passo__gt=0)
        qnao_excluido = Q(protocolo__excluido=False)
        qdefault = Q(qnao_excluido & qpasso_maoirq_zero)

        qservidor_origem = Q(servidor_origem=self.servidor.pk)
        qpessoal = qservidor_origem
        # RETIRADO POIS NA SAÍDA NORMAL DEVEM APARECER OS ENVIADOS POR MIM, NÃO OQ RECEBO
        # TODO: ANALISAR CAIXA DE SAÍDA DE CAIXAS DE PROTOCOLO GERAL
        # qpessoal = qservidor_origem | Q(Q(servidor_destino=self.servidor.pk) | Q(destinatario=self.servidor.pessoa_fisica.pk))

        qlotacao_destino_none = Q(lotacao_destino=None)
        qlotacao_destino_nao_none = ~qlotacao_destino_none
        qdestinatario_none = Q(destinatario=None)
        qdestinatario_nao_none = ~qdestinatario_none
        qlotacao_origem = Q(lotacao_origem__in=self.lotacoes)
        qservidor_destino_none = Q(lotacao_destino=None)
        qservidor_destino_nao_none = ~qservidor_destino_none
        qlotacao_origem_lotacao_destino_nao_none = (
            qlotacao_origem & qlotacao_destino_nao_none
        )
        qlotacao_origem_servidor_destino_nao_none = Q(
            qlotacao_origem & qservidor_destino_nao_none
        ) | Q(qlotacao_origem & qdestinatario_nao_none)
        qdepartamento = Q(
            qlotacao_origem_servidor_destino_nao_none
            | qlotacao_origem_lotacao_destino_nao_none
        )

        qpasso_eq_1 = Q(passo=1)
        qlotacao_criacao = Q(
            protocolo__lotacao_criacao__in=self.lotacoes_protocolo_geral
        )
        qlotacao_criacao_lotacao_destino_nao_none = (
            qlotacao_criacao & qlotacao_destino_nao_none
        )
        qlotacao_criacao_servidor_destino_destinatario_nao_none = Q(
            qlotacao_criacao & qservidor_destino_nao_none
        ) | Q(qlotacao_criacao & qdestinatario_nao_none)
        qgeral = (
            qnao_sigiloso
            & qpasso_eq_1
            & Q(
                qlotacao_criacao_servidor_destino_destinatario_nao_none
                | qlotacao_criacao_lotacao_destino_nao_none
            )
        )

        q = qdefault & Q(qpessoal | qdepartamento | qgeral)

        if self.valor:
            q = q & self.get_qbusca(self.valor)

        return q

    @staticmethod
    def get_finalizado():
        # return ~Q(protocolo__data_finalizado=None) | ~Q(data_finalizado=None)
        return ~Q(protocolo__data_finalizado=None)

    @staticmethod
    def get_finalizado_recebido():
        qnao_recebido = Q(data_recebimento=None)
        qrecebido = ~qnao_recebido
        qfinalizado_recebido = EDOCBoxQuery.get_finalizado() & qrecebido
        return qfinalizado_recebido

    @classmethod
    def get_qbusca(cls, valor):
        qbusca = (
            Q(protocolo__codigo__icontains=valor)
            | Q(protocolo__protocolo_externo__icontains=valor)
            | Q(protocolo__chancela__icontains=valor)
            | Q(protocolo__interessado__nome__icontains=valor)
            | Q(destinatario__nome__icontains=valor)
            | Q(protocolo__assunto__icontains=valor)
            | Q(servidor_origem__pessoa_fisica__nome__icontains=valor)
            | Q(lotacao_origem__nome__icontains=valor)
            | Q(lotacao_destino__nome__icontains=valor)
        )
        try:
            [midia for midia, x in list(MIDIA_ORIGEM.items()) if x == valor.upper()][0]
            qbusca = Q(qbusca | Q(protocolo__midia=midia))
        except:
            pass
        return qbusca

    @staticmethod
    def teste_todos_valores(movimentacao):
        for movs in movimentacao:
            EDOCBox.print_results(movs)

    @staticmethod
    def print_results(movimentacao):
        EDOCBox.ed(movimentacao)
        EDOCBox.eg(movimentacao)
        EDOCBox.ep(movimentacao)

    @staticmethod
    def ed(movimentacao):
        log.debug(
            """ED lot_origem %s | lot_destino %s | destinatario %s"""
            % (
                True if movimentacao.lotacao_origem else False,
                None if movimentacao.lotacao_destino is None else True,
                None if movimentacao.destinatario is None else False,
            )
        )

    @staticmethod
    def eg(movimentacao):
        log.debug(
            """EG lot_destino %s | lot_criacao %s"""
            % (
                None if movimentacao.lotacao_destino is None else True,
                None if movimentacao.lotacao_criacao is None else True,
            )
        )

    @staticmethod
    def ep(movimentacao):
        log.debug(
            """EP serv_origem %s | destinatario %s"""
            % (
                True if movimentacao.servidor_origem else False,
                True if movimentacao.destinatario else False,
            )
        )

    @staticmethod
    def teste(file, movimentacao):
        log.debug("-----------INICIO-------------")
        o = open("/home/gustavodettenborn/%s" % file, "w")
        o.write("(")
        for m in movimentacao.distinct("pk").values("pk"):
            o.write("'%s'," % (m["pk"]))
        o.write(")")
        o.close()
        log.debug("-----------FIM-------------")

    @staticmethod
    def teste_diferenca():
        saida = eval(open("/home/gustavodettenborn/saida", "r").read())
        saida_novo = eval(open("/home/gustavodettenborn/saida_novo", "r").read())
        diferenca = []
        for sa in saida:
            if sa not in saida_novo:
                diferenca.append(int(sa))
        print("diferenca = %s" % len(diferenca))
        return diferenca

    # from edocs.protocolo import utils
    # reload(utils); diferenca = utils.EDOCBoxQuery.teste_diferenca();

    @staticmethod
    def dif(diferenca):
        # ELENILSONCORREIA 129
        #        lotacoes_geral = [554]
        #        lotacoes = [554]
        #        servidor = [129]
        # CREUSASOUSA 86
        lotacoes_geral = [545]
        lotacoes = [545, 582]
        servidor = [86]
        print("PROCURANDO......")
        for m in Movimentacao.objects.filter(pk__in=diferenca):
            #            print(U"LOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s" %(m.lotacao_origem,m.lotacao_criacao,m.servidor_origem))
            try:
                if m.lotacao_origem.pk in lotacoes:
                    print(
                        "PKLOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s"
                        % (m.lotacao_origem, m.lotacao_criacao, m.servidor_origem)
                    )
            #                    print(u"LOT_ORIGEM (ENCONTRADO): %s" % m.lotacao_origem)
            except:
                pass
            try:
                if m.lotacao_origem.pk in lotacoes_geral:
                    print(
                        "PKLOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s"
                        % (m.lotacao_origem, m.lotacao_criacao, m.servidor_origem)
                    )
            #                    print(u"LOT_ORIGEM (ENCONTRADO): %s" % m.lotacao_origem)
            except:
                pass
            try:
                if m.lotacao_criacao.pk in lotacoes:
                    print(
                        "LOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s"
                        % (m.lotacao_origem, m.lotacao_criacao, m.servidor_origem)
                    )
            #                    print(u"LOT_CRIACAO (ENCONTRADO): %s" % m.lotacao_criacao)
            except:
                pass
            try:
                if m.servidor_origem.pk in servidor:
                    print(
                        "LOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s"
                        % (m.lotacao_origem, m.lotacao_criacao, m.servidor_origem)
                    )
            #                    print(u"SERV_ORIGEM (ENCONTRADO): %s" % m.servidor_origem)
            except:
                pass
        print("FIM.")

    # from edocs.protocolo import utils
    # reload(utils); utils.EDOCBoxQuery.escreve_tabela(diferenca);

    @staticmethod
    def escreve_tabela(diferenca):
        from contrib.utils import DateUtils

        # ELENILSON 129
        # EXPEDIENTE 554
        #        lotacoes_geral = [554]
        #        lotacoes = [554]
        #        servidor = [129]
        # CREUSASOUSA 86
        #        lotacoes_geral = [545]
        #        lotacoes = [545,582]
        #        servidor = [86]
        lotacoes_geral = [554]
        lotacoes = [554]
        servidor = [129]
        print("diferenca = %s" % len(diferenca))
        o = open("/home/gustavodettenborn/tabela_verdade.csv", "w")
        o.write(
            "pk|L_ORIGEM|L_DESTINO|L_CRIACAO|S_ORIGEM|S_DESTINO|DEST|PASSO|DT_FINAL|PDT_FINAL|EXCL|ENCAMI|SIGI"
        )
        for m in Movimentacao.objects.filter(pk__in=diferenca):
            if m.passo == 1:
                print(
                    "LOT_ORIGEM: %s | LOT_CRIACAO: %s | SERV_ORIGEM: %s"
                    % (m.lotacao_origem, m.lotacao_criacao, m.servidor_origem)
                )
            token = False
            # TESTES ABAIXO PARA CAIXA DE ENTRADA GERAL
            # TODO: DESENVOLVER TESTES PARA VERIFICAR OUTRAS CAIXAS
            try:
                if m.lotacao_origem.pk in lotacoes:
                    token = True
                    print(m.lotacao_origem.pk)
            except Exception as e:
                pass
            try:
                if m.lotacao_origem.pk in lotacoes_geral:
                    token = True
                    print(m.lotacao_origem.pk)
            except Exception as e:
                pass
            try:
                if m.lotacao_criacao.pk in lotacoes_geral:
                    print(m.lotacao_criacao.pk)
                    token = True
            except Exception as e:
                pass
            try:
                if m.servidor_origem.pk in servidor:
                    print(m.servidor_origem.pk)
                    token = True
            except Exception as e:
                pass
            #            if token:
            if True:
                try:
                    o.write(
                        "\n%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s"
                        % (
                            m.pk,
                            m.lotacao_origem,
                            m.lotacao_destino,
                            m.lotacao_criacao,
                            m.servidor_origem,
                            m.servidor_destino,
                            m.destinatario,
                            m.passo,
                            (
                                DateUtils.date_to_str(m.data_finalizado)
                                if m.data_finalizado
                                else ""
                            ),
                            (
                                DateUtils.date_to_str(m.protocolo.data_finalizado)
                                if m.protocolo.data_finalizado
                                else ""
                            ),
                            m.protocolo.excluido,
                            (
                                DateUtils.date_to_str(m.data_encaminhamento)
                                if m.data_encaminhamento
                                else ""
                            ),
                            m.protocolo.sigiloso,
                        )
                    )
                except Exception as e:
                    print(e)
        o.close()

    @staticmethod
    def raw_search_query(text: str) -> SearchQuery:
        """Prepare raw full text search for query.

        Strips a text, then adds ':*' wildcard for each of its parts so that it makes the search more flexible

        Parameters
        ----------
        text: str
            Text on which the operation will be performed

        Returns
        -------
        SearchQuery
            a SearchQuery using 'portuguese' as config and 'raw' as search type
        """
        text = text.strip()
        raw_expression = ""
        splitted_text = [part for part in text.split(" ") if part.strip() != ""]
        for part in splitted_text:
            if raw_expression == "":
                raw_expression += f"{part}:*"
            else:
                raw_expression += f" & {part}:*"  # Used & (and) operator in order to keep the same behavior as previously
        log.debug(f"RAW Expression for {text} -> {raw_expression}")
        return SearchQuery(raw_expression, config="portuguese", search_type="raw")
