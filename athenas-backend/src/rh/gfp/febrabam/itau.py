# -*- coding: utf-8 -*-

from datetime import datetime

from django.db.models import Count

from contrib.helpers import clear_to_ascii
from rh.gfp.febrabam import Protocol
from rh.gfp.models import FolhaEvento
from rh.models import Banco, Servidor, UnidadeAdministrativa

# from standard.models import Configuration

__name__ = "Banco Itaú"
__hid__ = "341"


class File(Protocol):

    def __init__(self, conf):
        Protocol.__init__(self)

        banco = Banco.objects.get(numero="341")

        try:
            # cfg = Configuration.objects.get(application="gfp")
            # FIXME: int(cfg.itens.get(key = "orgao").value))
            uadm = UnidadeAdministrativa.objects.get(pk=84)
            unidade = uadm.orgao_geral.nome
        except:
            unidade = "PROCURADORIA GERAL DE JUSTICA"
            pass

        self.header = self.Header(
            banco=banco.numero,
            lote=0,
            registro=0,
            brancos1=" ",
            versao="080",
            tipo_inscricao=2,  # 1 = CPF; 2 = CNPJ
            num_inscricao="01786078000146",  # FIXME
            brancos2=" ",
            agencia=banco.agencia,
            brancos3=" ",
            conta_corrente=banco.conta,
            brancos4=" ",
            dv_ag_conta=" ",
            nome_empresa=unidade,
            nome_banco=banco.nome,
            brancos5=" ",
            codigo_remessa=1,
            data_geracao=datetime.now().strftime("%d%m%Y"),
            hora_geracao=datetime.now().strftime("%H%M%S"),
            zeros=0,
            densidade="01600",
            brancos6=" ",
        )

        cc = self.CreditoConta(
            banco=banco.numero,
            lote=1,
            registro=1,
            operacao="C",
            tipo_pgto=30,
            forma_pgto=1,
            layout_lote="040",
            brancos1=" ",
            tipo_inscricao=2,
            num_inscricao="01786078000146",  # FIXME
            brancos2=" ",
            agencia=banco.agencia,
            brancos3=" ",
            conta_corrente=banco.conta,
            brancos4=" ",
            dv_ag_conta=" ",
            nome_empresa=unidade,
            finalidade=" ",
            historico=" ",
            logradouro="QD 202 NORTE, AV LO 4, CONJ 3",
            numero=0,
            complemento="LTS 5 e 6",
            cidade="PALMAS",
            cep=77006214,
            estado="TO",
            brancos5=" ",
            ocorrencias=" ",
            data_pagamento=conf["data_compromisso"],
            folha=conf["folha"],
        )

        self.bodys.append(cc)

        num_lote = len(self.bodys)
        num_reg = 0

        self.trailer = self.Trailer(
            banco=banco.numero,
            lote=9999,
            registro=9,
            brancos1=" ",
            qtde_lotes=num_lote,
            qtde_registros=num_reg,
            brancos2=" ",
        )

    class CreditoConta(Protocol):
        def __init__(self, **kargs):
            Protocol.__init__(self)

            self.banco = "banco" in kargs and kargs["banco"] or 0
            self.lote = "lote" in kargs and kargs["lote"] or 0
            self.registro = "registro" in kargs and kargs["registro"] or 0
            self.operacao = "operacao" in kargs and kargs["operacao"] or " "
            self.tipo_pgto = "tipo_pgto" in kargs and kargs["tipo_pgto"] or 0
            self.forma_pgto = "forma_pgto" in kargs and kargs["forma_pgto"] or 0
            self.layout_lote = "layout_lote" in kargs and kargs["layout_lote"] or 0
            self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
            self.tipo_inscricao = (
                "tipo_inscricao" in kargs and kargs["tipo_inscricao"] or 0
            )
            self.num_inscricao = (
                "num_inscricao" in kargs and kargs["num_inscricao"] or 0
            )
            self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "
            self.agencia = "agencia" in kargs and kargs["agencia"] or 0
            self.brancos3 = "brancos3" in kargs and kargs["brancos3"] or " "
            self.conta_corrente = (
                "conta_corrente" in kargs and kargs["conta_corrente"] or 0
            )
            self.brancos4 = "brancos4" in kargs and kargs["brancos4"] or " "
            self.dv_ag_conta = "dv_ag_conta" in kargs and kargs["dv_ag_conta"] or " "
            self.nome_empresa = "nome_empresa" in kargs and kargs["nome_empresa"] or " "
            self.finalidade = "finalidade" in kargs and kargs["finalidade"] or " "
            self.historico = "historico" in kargs and kargs["historico"] or " "
            self.logradouro = "logradouro" in kargs and kargs["logradouro"] or " "
            self.numero = "numero" in kargs and kargs["numero"] or 0
            self.complemento = "complemento" in kargs and kargs["complemento"] or " "
            self.cidade = "cidade" in kargs and kargs["cidade"] or " "
            self.cep = "cep" in kargs and kargs["cep"] or 0
            self.estado = "estado" in kargs and kargs["estado"] or " "
            self.brancos5 = "brancos5" in kargs and kargs["brancos5"] or " "
            self.ocorrencias = "ocorrencias" in kargs and kargs["ocorrencias"] or " "
            self.data_pagamento = (
                "data_pagamento" in kargs and kargs["data_pagamento"] or datetime.now()
            )
            self.folha = "folha" in kargs and kargs["folha"] or None

            self.header = self.Header(
                banco=self.banco,
                lote=self.lote,
                registro=self.registro,
                operacao=self.operacao,
                tipo_pgto=self.tipo_pgto,
                forma_pgto=self.forma_pgto,
                layout_lote=self.layout_lote,
                brancos1=self.brancos1,
                tipo_inscricao=self.tipo_inscricao,
                num_inscricao=self.num_inscricao,
                brancos2=self.brancos2,
                agencia=self.agencia,
                brancos3=self.brancos3,
                conta_corrente=self.conta_corrente,
                brancos4=self.brancos4,
                dv_ag_conta=self.dv_ag_conta,
                nome_empresa=self.nome_empresa,
                finalidade=self.finalidade,
                historico=self.historico,
                logradouro=self.logradouro,
                numero=self.numero,
                complemento=self.complemento,
                cidade=self.cidade,
                cep=self.cep,
                estado=self.estado,
                brancos5=self.brancos5,
                ocorrencias=self.ocorrencias,
            )

            count = 0
            soma = 0.0
            banco = Banco.objects.get(
                numero=Protocol.prepare_str(self.banco, size=3, align=1, branco="0")
            )
            query = (
                FolhaEvento.objects.filter(folha=self.folha)
                .order_by("servidor__pessoa_fisica__nome")
                .values("servidor")
                .annotate(Count("servidor"))
            )

            for info in query:
                if info["servidor__count"] > 0:
                    try:
                        s = Servidor.objects.get(pk=info["servidor"])
                        db = s.pessoa_fisica.dado_bancario.filter(
                            banco=banco.pk
                        ).order_by("-id")[0]

                        if db.banco == banco:
                            positivo = 0
                            negativo = 0
                            for e in FolhaEvento.objects.filter(
                                folha=self.folha, servidor=s
                            ):
                                if e.evento.tipo == "P":
                                    positivo += float(e.valor)
                                else:
                                    negativo += float(e.valor)

                            self.bodys.append(
                                self.Credito(
                                    # segmento A
                                    banco=banco.numero,
                                    lote="0001",
                                    registro=3,
                                    num_registro=count + 1,
                                    segmento="A",
                                    tipo_movimento=0,
                                    zeros1=0,
                                    banco_favorecido=db.banco.numero,
                                    agencia=db.agencia,
                                    nome="{0}".format(
                                        clear_to_ascii(s.pessoa_fisica.nome)
                                    ),
                                    num_doc_empresa=s.matricula,
                                    data_lcto=self.data_pagamento,
                                    moeda="REA",
                                    zeros2=0,
                                    valor_lcto=(positivo - negativo),
                                    nosso_numero=" ",
                                    brancos1=" ",
                                    data_efetivacao=" ",
                                    valor_efetivacao=" ",
                                    finalidade=" ",
                                    brancos2=" ",
                                    num_documento=" ",
                                    cpf_cnpj_favorec=s.pessoa_fisica.cpf,
                                    finalidade_doc=" ",
                                    finalidade_ted=10,
                                    brancos3=" ",
                                    aviso_favorecido=0,
                                    ocorrencias="",
                                )
                            )

                            count += 1
                            soma += positivo - negativo
                    except:
                        pass

            self.trailer = self.Trailer(
                banco=banco.numero,
                lote=1,
                registro=5,
                brancos1=" ",
                qtde_registros=count,
                soma=soma,
                zeros=0,
                brancos2=" ",
                ocorrencias=" ",
            )

        class Credito(Protocol.Header):
            def __init__(self, **kargs):
                self.banco = "banco" in kargs and kargs["banco"] or 0
                self.lote = "lote" in kargs and kargs["lote"] or 0
                self.registro = "registro" in kargs and kargs["registro"] or 0
                self.num_registro = (
                    "num_registro" in kargs and kargs["num_registro"] or 0
                )
                self.segmento = "segmento" in kargs and kargs["segmento"] or " "
                self.tipo_movimento = (
                    "tipo_movimento" in kargs and kargs["tipo_movimento"] or 0
                )
                self.zeros1 = "zeros1" in kargs and kargs["zeros1"] or 0
                self.banco_favorecido = (
                    "banco_favorecido" in kargs and kargs["banco_favorecido"] or 0
                )
                self.agencia = "agencia" in kargs and kargs["agencia"] or " "
                self.nome = "nome" in kargs and kargs["nome"] or " "
                self.num_doc_empresa = (
                    "num_doc_empresa" in kargs and kargs["num_doc_empresa"] or " "
                )
                self.data_lcto = (
                    "data_lcto" in kargs and kargs["data_lcto"] or datetime.now()
                )
                self.moeda = "moeda" in kargs and kargs["moeda"] or " "
                self.zeros2 = "zeros2" in kargs and kargs["zeros2"] or 0
                self.valor_lcto = "valor_lcto" in kargs and kargs["valor_lcto"] or 0
                self.nosso_numero = (
                    "nosso_numero" in kargs and kargs["nosso_numero"] or " "
                )
                self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
                self.data_efetivacao = (
                    "data_efetivacao" in kargs and kargs["data_efetivacao"] or " "
                )
                self.valor_efetivacao = (
                    "valor_efetivacao" in kargs and kargs["valor_efetivacao"] or " "
                )
                self.finalidade = "finalidade" in kargs and kargs["finalidade"] or " "
                self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "
                self.num_documento = (
                    "num_documento" in kargs and kargs["num_documento"] or 0
                )
                self.cpf_cnpj_favorec = (
                    "cpf_cnpj_favorec" in kargs and kargs["cpf_cnpj_favorec"] or 0
                )
                self.finalidade_doc = (
                    "finalidade_doc" in kargs and kargs["finalidade_doc"] or " "
                )
                self.finalidade_ted = (
                    "finalidade_ted" in kargs and kargs["finalidade_ted"] or " "
                )
                self.brancos3 = "brancos3" in kargs and kargs["brancos3"] or " "
                self.aviso_favorecido = (
                    "aviso_favorecido" in kargs and kargs["aviso_favorecido"] or " "
                )
                self.ocorrencias = (
                    "ocorrencias" in kargs and kargs["ocorrencias"] or " "
                )

            def __str__(self):
                return "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}\
                        {20}{21}{22}{23}{24}{25}{26}{27}".format(
                    Protocol.prepare_str(self.banco, size=3, align=1, branco="0"),  # 0
                    Protocol.prepare_str(self.lote, size=4, align=1, branco="0"),  # 1
                    Protocol.prepare_str(
                        self.registro, size=1, align=1, branco="0"
                    ),  # 2
                    Protocol.prepare_str(
                        self.num_registro, size=5, align=1, branco="0"
                    ),  # 3
                    Protocol.prepare_str(
                        self.segmento, size=1, align=0, branco=" "
                    ),  # 4
                    Protocol.prepare_str(
                        self.tipo_movimento, size=3, align=1, branco="0"
                    ),  # 5
                    Protocol.prepare_str(self.zeros1, size=3, align=1, branco="0"),  # 6
                    Protocol.prepare_str(
                        self.banco_favorecido, size=3, align=1, branco="0"
                    ),  # 7
                    Protocol.prepare_str(
                        self.agencia, size=20, align=0, branco=" "
                    ),  # 8
                    Protocol.prepare_str(self.nome, size=30, align=0, branco=" "),  # 9
                    Protocol.prepare_str(
                        self.num_doc_empresa, size=20, align=0, branco=" "
                    ),  # 10
                    Protocol.prepare_date(self.data_lcto, tipo=0),  # 11
                    Protocol.prepare_str(self.moeda, size=3, align=0, branco=" "),  # 12
                    Protocol.prepare_str(
                        self.zeros2, size=15, align=1, branco="0"
                    ),  # 13
                    Protocol.prepare_float(self.valor_lcto, size=15, decimal=2),  # 14
                    Protocol.prepare_str(
                        self.nosso_numero, size=15, align=0, branco=" "
                    ),  # 15
                    Protocol.prepare_str(
                        self.brancos1, size=5, align=0, branco=" "
                    ),  # 16
                    Protocol.prepare_str(
                        self.data_efetivacao, size=8, align=0, branco=" "
                    ),  # 17
                    Protocol.prepare_str(
                        self.valor_efetivacao, size=15, align=0, branco=" "
                    ),  # 18
                    Protocol.prepare_str(
                        self.finalidade, size=18, align=0, branco=" "
                    ),  # 19
                    Protocol.prepare_str(
                        self.brancos2, size=2, align=0, branco=" "
                    ),  # 20
                    Protocol.prepare_str(
                        self.num_documento, size=6, align=1, branco="0"
                    ),  # 21
                    Protocol.prepare_str(
                        self.cpf_cnpj_favorec, size=14, align=1, branco="0"
                    ),  # 22
                    Protocol.prepare_str(
                        self.finalidade_doc, size=2, align=0, branco=" "
                    ),  # 23
                    Protocol.prepare_str(
                        self.finalidade_ted, size=5, align=0, branco=" "
                    ),  # 24
                    Protocol.prepare_str(
                        self.brancos3, size=5, align=0, branco=" "
                    ),  # 25
                    Protocol.prepare_str(
                        self.aviso_favorecido, size=1, align=0, branco=" "
                    ),  # 26
                    Protocol.prepare_str(
                        self.ocorrencias, size=10, align=0, branco=" "
                    ),  # 27
                )

        class Header(Protocol.Header):
            def __init__(self, **kargs):
                self.banco = "banco" in kargs and kargs["banco"] or 0
                self.lote = "lote" in kargs and kargs["lote"] or 0
                self.registro = "registro" in kargs and kargs["registro"] or 0
                self.operacao = "operacao" in kargs and kargs["operacao"] or " "
                self.tipo_pgto = "tipo_pgto" in kargs and kargs["tipo_pgto"] or 0
                self.forma_pgto = "forma_pgto" in kargs and kargs["forma_pgto"] or 0
                self.layout_lote = "layout_lote" in kargs and kargs["layout_lote"] or 0
                self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
                self.tipo_inscricao = (
                    "tipo_inscricao" in kargs and kargs["tipo_inscricao"] or 0
                )
                self.num_inscricao = (
                    "num_inscricao" in kargs and kargs["num_inscricao"] or 0
                )
                self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "
                self.agencia = "agencia" in kargs and kargs["agencia"] or 0
                self.brancos3 = "brancos3" in kargs and kargs["brancos3"] or " "
                self.conta_corrente = (
                    "conta_corrente" in kargs and kargs["conta_corrente"] or 0
                )
                self.brancos4 = "brancos4" in kargs and kargs["brancos4"] or " "
                self.dv_ag_conta = (
                    "dv_ag_conta" in kargs and kargs["dv_ag_conta"] or " "
                )
                self.nome_empresa = (
                    "nome_empresa" in kargs and kargs["nome_empresa"] or " "
                )
                self.finalidade = "finalidade" in kargs and kargs["finalidade"] or " "
                self.historico = "historico" in kargs and kargs["historico"] or " "
                self.logradouro = "logradouro" in kargs and kargs["logradouro"] or " "
                self.numero = "numero" in kargs and kargs["numero"] or 0
                self.complemento = (
                    "complemento" in kargs and kargs["complemento"] or " "
                )
                self.cidade = "cidade" in kargs and kargs["cidade"] or " "
                self.cep = "cep" in kargs and kargs["cep"] or 0
                self.estado = "estado" in kargs and kargs["estado"] or " "
                self.brancos5 = "brancos5" in kargs and kargs["brancos5"] or " "
                self.ocorrencias = (
                    "ocorrencias" in kargs and kargs["ocorrencias"] or " "
                )
                self.data_pagamento = (
                    "data_pagamento" in kargs
                    and kargs["data_pagamento"]
                    or datetime.now()
                )
                self.folha = "folha" in kargs and kargs["folha"] or None

            def __str__(self):
                return "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}\
                        {19}{20}{21}{22}{23}{24}{25}{26}".format(
                    Protocol.prepare_str(self.banco, size=3, align=1, branco="0"),  # 0
                    Protocol.prepare_str(self.lote, size=4, align=1, branco="0"),  # 1
                    Protocol.prepare_str(
                        self.registro, size=1, align=1, branco="0"
                    ),  # 2
                    Protocol.prepare_str(
                        self.operacao, size=1, align=0, branco=" "
                    ),  # 3
                    Protocol.prepare_str(
                        self.tipo_pgto, size=2, align=1, branco="0"
                    ),  # 4
                    Protocol.prepare_str(
                        self.forma_pgto, size=2, align=1, branco="0"
                    ),  # 5
                    Protocol.prepare_str(
                        self.layout_lote, size=3, align=1, branco="0"
                    ),  # 6
                    Protocol.prepare_str(
                        self.brancos1, size=1, align=0, branco=" "
                    ),  # 7
                    Protocol.prepare_str(
                        self.tipo_inscricao, size=1, align=1, branco="0"
                    ),  # 8
                    Protocol.prepare_str(
                        self.num_inscricao, size=14, align=1, branco="0"
                    ),  # 9
                    Protocol.prepare_str(
                        self.brancos2, size=20, align=0, branco=" "
                    ),  # 10
                    Protocol.prepare_str(
                        self.agencia, size=5, align=1, branco="0"
                    ),  # 11
                    Protocol.prepare_str(
                        self.brancos3, size=1, align=0, branco=" "
                    ),  # 12
                    Protocol.prepare_str(
                        self.conta_corrente, size=12, align=1, branco="0"
                    ),  # 13
                    Protocol.prepare_str(
                        self.brancos4, size=1, align=0, branco=" "
                    ),  # 14
                    Protocol.prepare_str(
                        self.dv_ag_conta, size=1, align=1, branco="0"
                    ),  # 15
                    Protocol.prepare_str(
                        self.nome_empresa, size=30, align=0, branco=" "
                    ),  # 16
                    Protocol.prepare_str(
                        self.finalidade, size=30, align=0, branco=" "
                    ),  # 17
                    Protocol.prepare_str(
                        self.historico, size=10, align=0, branco=" "
                    ),  # 18
                    Protocol.prepare_str(
                        self.logradouro, size=30, align=0, branco=" "
                    ),  # 19
                    Protocol.prepare_str(
                        self.numero, size=5, align=1, branco="0"
                    ),  # 20
                    Protocol.prepare_str(
                        self.complemento, size=15, align=0, branco=" "
                    ),  # 21
                    Protocol.prepare_str(
                        self.cidade, size=20, align=0, branco=" "
                    ),  # 22
                    Protocol.prepare_str(self.cep, size=8, align=1, branco="0"),  # 23
                    Protocol.prepare_str(
                        self.estado, size=2, align=0, branco=" "
                    ),  # 24
                    Protocol.prepare_str(
                        self.brancos5, size=8, align=0, branco=" "
                    ),  # 25
                    Protocol.prepare_str(
                        self.ocorrencias, size=10, align=0, branco=" "
                    ),  # 26
                )

        class Trailer(Protocol.Trailer):
            def __init__(self, **kargs):
                self.banco = "banco" in kargs and kargs["banco"] or 0
                self.lote = "lote" in kargs and kargs["lote"] or 0
                self.registro = "registro" in kargs and kargs["registro"] or 0
                self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
                self.qtde_registros = (
                    "qtde_registros" in kargs and kargs["qtde_registros"] or 0
                )
                self.soma = "soma" in kargs and kargs["soma"] or 0
                self.zeros = "zeros" in kargs and kargs["zeros"] or 0
                self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "
                self.ocorrencias = (
                    "ocorrencias" in kargs and kargs["ocorrencias"] or " "
                )

            def __str__(self):
                return "{0}{1}{2}{3}{4}{5}{6}{7}{8}".format(
                    Protocol.prepare_str(self.banco, align=1, size=3, branco="0"),  # 0
                    Protocol.prepare_str(self.lote, align=1, size=4, branco="0"),  # 1
                    Protocol.prepare_str(
                        self.registro, align=1, size=1, branco="0"
                    ),  # 2
                    Protocol.prepare_str(
                        self.brancos1, align=0, size=9, branco=" "
                    ),  # 3
                    Protocol.prepare_str(
                        self.qtde_registros, align=1, size=6, branco="0"
                    ),  # 4
                    Protocol.prepare_float(self.soma, size=18, decimal=2),  # 5
                    Protocol.prepare_str(self.zeros, align=1, size=18, branco="0"),  # 6
                    Protocol.prepare_str(
                        self.brancos2, align=0, size=171, branco=" "
                    ),  # 7
                    Protocol.prepare_str(
                        self.ocorrencias, align=0, size=10, branco=" "
                    ),  # 8
                )

    class Header(Protocol.Header):
        def __init__(self, **kargs):
            self.banco = "banco" in kargs and kargs["banco"] or 0
            self.lote = "lote" in kargs and kargs["lote"] or 0
            self.registro = "registro" in kargs and kargs["registro"] or 0
            self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
            self.versao = "versao" in kargs and kargs["versao"] or 0
            self.tipo_inscricao = (
                "tipo_inscricao" in kargs and kargs["tipo_inscricao"] or 0
            )
            self.num_inscricao = (
                "num_inscricao" in kargs and kargs["num_inscricao"] or 0
            )
            self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "
            self.agencia = "agencia" in kargs and kargs["agencia"] or 0
            self.brancos3 = "brancos3" in kargs and kargs["brancos3"] or " "
            self.conta_corrente = (
                "conta_corrente" in kargs and kargs["conta_corrente"] or 0
            )
            self.brancos4 = "brancos4" in kargs and kargs["brancos4"] or " "
            self.dv_ag_conta = "dv_ag_conta" in kargs and kargs["dv_ag_conta"] or " "
            self.nome_empresa = "nome_empresa" in kargs and kargs["nome_empresa"] or " "
            self.nome_banco = "nome_banco" in kargs and kargs["nome_banco"] or " "
            self.brancos5 = "brancos5" in kargs and kargs["brancos5"] or " "
            self.codigo_remessa = (
                "codigo_remessa" in kargs and kargs["codigo_remessa"] or 0
            )
            self.data_geracao = "data_geracao" in kargs and kargs["data_geracao"] or 0
            self.hora_geracao = "hora_geracao" in kargs and kargs["hora_geracao"] or 0
            self.zeros = "zeros" in kargs and kargs["zeros"] or 0
            self.densidade = "densidade" in kargs and kargs["densidade"] or 0
            self.brancos6 = "brancos6" in kargs and kargs["brancos6"] or " "

        def __str__(self):
            return "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}".format(
                Protocol.prepare_str(self.banco, align=1, size=3, branco="0"),  # 0
                Protocol.prepare_str(self.lote, align=1, size=4, branco="0"),  # 1
                Protocol.prepare_str(self.registro, align=1, size=1, branco="0"),  # 2
                Protocol.prepare_str(self.brancos1, align=0, size=6, branco=" "),  # 3
                Protocol.prepare_str(self.versao, align=1, size=3, branco="0"),  # 4
                Protocol.prepare_str(
                    self.tipo_inscricao, align=1, size=1, branco="0"
                ),  # 5
                Protocol.prepare_str(
                    self.num_inscricao, align=1, size=14, branco="0"
                ),  # 6
                Protocol.prepare_str(self.brancos2, align=0, size=20, branco=" "),  # 7
                Protocol.prepare_str(self.agencia, align=1, size=5, branco="0"),  # 8
                Protocol.prepare_str(self.brancos3, align=0, size=1, branco=" "),  # 9
                Protocol.prepare_str(
                    self.conta_corrente, align=1, size=12, branco="0"
                ),  # 10
                Protocol.prepare_str(self.brancos4, align=0, size=1, branco=" "),  # 11
                Protocol.prepare_str(
                    self.dv_ag_conta, align=1, size=1, branco="0"
                ),  # 12
                Protocol.prepare_str(
                    self.nome_empresa, align=0, size=30, branco=" "
                ),  # 13
                Protocol.prepare_str(
                    self.nome_banco, align=0, size=30, branco=" "
                ),  # 14
                Protocol.prepare_str(self.brancos5, align=0, size=10, branco=" "),  # 15
                Protocol.prepare_str(
                    self.codigo_remessa, align=1, size=1, branco="0"
                ),  # 16
                Protocol.prepare_date(datetime.now(), tipo=0),  # 17
                Protocol.prepare_time(datetime.now()),  # 18
                Protocol.prepare_str(self.zeros, align=1, size=9, branco="0"),  # 19
                Protocol.prepare_str(self.densidade, align=1, size=5, branco="0"),  # 20
                Protocol.prepare_str(self.brancos6, align=0, size=69, branco=" "),  # 21
            )

    class Trailer(Protocol.Trailer):
        def __init__(self, **kargs):
            self.banco = "banco" in kargs and kargs["banco"] or 0
            self.lote = "lote" in kargs and kargs["lote"] or 0
            self.registro = "registro" in kargs and kargs["registro"] or 0
            self.brancos1 = "brancos1" in kargs and kargs["brancos1"] or " "
            self.qtde_lotes = "qtde_lotes" and kargs["qtde_lotes"] or 0
            self.qtde_registros = (
                "qtde_registros" in kargs and kargs["qtde_registros"] or 0
            )
            self.brancos2 = "brancos2" in kargs and kargs["brancos2"] or " "

        def __str__(self):
            return "{0}{1}{2}{3}{4}{5}{6}".format(
                Protocol.prepare_str(self.banco, align=1, size=3, branco="0"),  # 0
                Protocol.prepare_str(self.lote, align=1, size=4, branco="0"),  # 1
                Protocol.prepare_str(self.registro, align=1, size=1, branco="0"),  # 2
                Protocol.prepare_str(self.brancos1, align=0, size=9, branco=" "),  # 3
                Protocol.prepare_str(self.qtde_lotes, align=1, size=6, branco="0"),  # 4
                Protocol.prepare_str(
                    self.qtde_registros, align=1, size=6, branco="0"
                ),  # 5
                Protocol.prepare_str(self.brancos2, align=0, size=211, branco=" "),  # 6
            )
