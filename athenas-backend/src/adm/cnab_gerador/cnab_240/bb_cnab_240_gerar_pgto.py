import os
import re
import codecs
from datetime import datetime
from decimal import Decimal
from django.conf import settings

from rh.models import UnidadeAdministrativa
from rh.gfp.models import BankingConvenant
from ged.models import Arquivo

from contrib.middleware import get_current_user
from contrib.utils import getLogger
from rh.pvf.apiv2.utils.calendar import remove_accents

log = getLogger(__name__)


class BBCnab240GerarPgto(object):
    """
    Classe para criação de arquivo CNAB240 do Banco do Brasil.
    """

    def __init__(self, *args, **kwargs):
        tipo_servico_map = {
            "pgtos_fornecedor": "20",
            "pgtos_salario": "30",
            "pgtos_diversos": "98",
        }
        self.tipo_servico = tipo_servico_map[
            kwargs.get("tipo_servico", "pgtos_fornecedor")
        ]
        self.hoje = datetime.today()
        self.cnab_texto = ""
        self.qtd_total_registros = 0
        self.qtd_lotes = 0
        self.lote_num = 0
        self.registro_num = 0

    def criar_cnab_pgto_bb_outros_bancos(self, *args, **kwargs):
        """
        Método responsável por criar o arquivo de CNAB.
        O layout deste método é de pagamentos para contas do Banco do Brasil e para outros bancos no mesmo arquivo, separados por lotes.
        Os pagamentos para contas do Banco do Brasil devem ficar no lote inicial.

        Parâmetros pelo kwargs:
        - favorecidos_bb (list de dicts)
        - favorecidos_outros (list de dicts)
        - ident_extrato_fav (str) - não obrigatório (identificação no extrato do favorecido)
        - ident_extrato_pag (str) - não obrigatório, deve ter o mesmo valor para todos os registros do lote (identificação no extrato do pagador)
        - data_pgto (date)
        - nome_arquivo_cnab (str) - não obrigatório

        Os parâmetros 'favorecidos_bb' e 'favorecidos_outros' devem ser uma lista de dicts com a seguinte estrutura:

        {
            'doc: 'num',
            'tipo_doc': 'str',
            'nome': 'str',
            'cod_banco: 'num',
            'agencia': 'num',
            'conta_completa': 'num',
            'tipo_conta': 'num' ('1' - conta corrente, '2' - conta poupança)
            'valor_pgto': 'decimal',
        }
        """

        ### criando HEADER DO ARQUIVO
        self.cnab_texto = self.criar_header_arquivo()

        ### verificando quantidade favorecidos com contas no Banco do Brasil
        if len(kwargs.get("favorecidos_bb")) > 0:
            self.criar_lote_ab(
                kwargs.get("favorecidos_bb"), kwargs.get("data_pgto"), "01", "000"
            )

        ### verificando quantidade favorecidos com contas em outros bancos
        if len(kwargs.get("favorecidos_outros")) > 0:
            self.criar_lote_ab(
                kwargs.get("favorecidos_outros"), kwargs.get("data_pgto"), "03", "018"
            )

        self.cnab_texto += self.criar_trailer_arquivo()

        arquivo_cnab = self.criar_arquivo(kwargs.get("nome_arquivo_cnab", None))

        return arquivo_cnab

    def criar_nome_arquivo(self, nome_arquivo_cnab):
        """
        Método responsável por definir o nome do arquivo.
        """

        if nome_arquivo_cnab is None:
            nome_arquivo_cnab = f"cnab_{datetime.today().strftime('%Y%m%d%H%M%S')}.txt"
        else:
            if nome_arquivo_cnab[-4:] != ".txt":
                nome_arquivo_cnab = (
                    f"{remove_accents(nome_arquivo_cnab).replace(' ', '_')}.txt"
                )

        return nome_arquivo_cnab

    def criar_arquivo(self, nome_arquivo_cnab):
        """
        Método responsável pela criação do arquivo.
        """

        nome_arquivo_cnab = self.criar_nome_arquivo(nome_arquivo_cnab)

        if not os.path.exists(settings.UPLOAD_STORE_DIR):
            os.makedirs(settings.UPLOAD_STORE_DIR)

        arquivo_path = os.path.join(settings.UPLOAD_STORE_DIR, nome_arquivo_cnab)
        with codecs.open(arquivo_path, "w", "utf-8") as fd:
            fd.write(remove_accents(str(self.cnab_texto)))

        arquivo_cnab = Arquivo.from_filepath(
            arquivo_path, get_current_user(), "application/txt", 3
        )

        return arquivo_cnab

    def criar_lote_ab(self, favorecidos, data_pgto, forma_lanc, cod_camera):
        """
        Método responsável pela geração do lote AB
        """

        self.qtd_lotes += 1
        self.lote_num += 1
        total_valor_lote = Decimal(0)
        qtd_registros_lote = 0

        # criando HEADER DO LOTE AB - para contas do Banco do Brasil
        self.cnab_texto += self.criar_header_lote_ab(forma_lanc=forma_lanc)

        for i, fav in enumerate(favorecidos):
            total_valor_lote += Decimal(fav["valor_pgto"])

            # criando registro do SEGMENTO A
            qtd_registros_lote += 1
            self.cnab_texto += self.criar_seg_a(
                registro_num=qtd_registros_lote,
                favorecido=fav,
                ident_extrato_fav="",
                ident_extrato_pag="",
                data_pgto=data_pgto,
                cod_camera=cod_camera,
            )

            # criando registro do SEGMENTO B
            qtd_registros_lote += 1
            self.registro_num += 1
            self.cnab_texto += self.criar_seg_b(
                registro_num=qtd_registros_lote,
                favorecido_doc=fav["doc"],
                favorecido_tipo_doc=fav["tipo_doc"],
            )

        # criando TRAILER DO LOTE AB - para contas do Banco do Brasil
        qtd_registros_lote += 2
        self.cnab_texto += self.criar_trailer_lote(
            lote_num=self.lote_num,
            qtd_registros_lote=qtd_registros_lote,
            total_valores=total_valor_lote,
        )

    def buscar_infos_pgj_mt(self):
        """
        Método responsável por buscar as informações básicas da pessoa jurídica do PGJ - MT (MP MT).
        """

        pj_mpmt = UnidadeAdministrativa.objects.get(
            pk=1
        )  # pk = 1 - Unidade Administrativa PGJ - MT
        conv_banc_mpmt = BankingConvenant.objects.get(
            pk=1
        )  # pk = 1 - Convênio com o Banco do Brasil

        return {
            "tipo_inscr": "2",
            "num_inscr": pj_mpmt.pessoa_juridica.cnpj,
            "num_convenio": conv_banc_mpmt.convenant,
            "agencia": conv_banc_mpmt.agency_cod,
            "agencia_dv": conv_banc_mpmt.agency_cod_dv,
            "cc": conv_banc_mpmt.account_cod,
            "cc_dv": conv_banc_mpmt.account_cod_dv.upper(),
            "nome_empresa": f"{pj_mpmt.sigla} - {pj_mpmt.nome}",
        }

    def buscar_sessao_controle(self, tipo_servico, lote_num=0):
        """
        Método responsável por consolidar a informação da sessão de Controle.
        """

        controle = ""

        controle += "001"  # Banco 001 - Banco do Brasil
        controle += str(lote_num).rjust(4, "0")  # Lote de serviço
        controle += tipo_servico  # Tipo de serviço

        return controle

    def buscar_sessao_empresa(self):
        """
        Método responsável por consolidar a informação da sessão de Empresa.
        """

        empresa_pgj_mt = self.buscar_infos_pgj_mt()

        empresa = ""

        empresa += empresa_pgj_mt["tipo_inscr"]
        empresa += empresa_pgj_mt["num_inscr"].rjust(14, "0")
        empresa += empresa_pgj_mt["num_convenio"].rjust(13, "0")
        empresa += " " * 5  # Reservado ao banco
        empresa += (
            " " * 2
        )  # implementar verificação de ambiente, se produção deixar em branco (' ' * 2)
        empresa += empresa_pgj_mt["agencia"].rjust(5, "0")
        empresa += empresa_pgj_mt["agencia_dv"]
        empresa += empresa_pgj_mt["cc"].rjust(12, "0")
        empresa += empresa_pgj_mt["cc_dv"]
        empresa += " "  # Dígito Verificador da Ag/Conta
        empresa += empresa_pgj_mt["nome_empresa"][:30]

        return empresa

    def criar_header_arquivo(self):
        """
        Método responsável por criar o header do arquivo
        """

        self.qtd_total_registros += 1
        linha_header = ""

        # sessão Controle
        linha_header += self.buscar_sessao_controle("0")

        linha_header += " " * 9  # CNAB - deixar em branco

        # sessão Empresa
        linha_header += self.buscar_sessao_empresa()

        # sessão Outras Informações
        linha_header += "BANCO DO BRASIL".ljust(30, " ")
        linha_header += " " * 10  # CNAB - deixar em branco
        linha_header += "1"  # Arquivo Remessa = '1'
        linha_header += f"{self.hoje.date().strftime('%d%m%Y')}"  # Data de geração do arquivo - DDMMAAAA
        linha_header += f"{self.hoje.strftime('%H%M%S')}"  # Hora de geração do arquivo - HHMMSS, não obrigatório (preencher com zeros)
        linha_header += " " * 6  # Número sequencial, não obrigatório
        linha_header += " " * 3  # Versão do layout, não obrigatório
        linha_header += "0" * 5  # Densidade
        linha_header += " " * 20  # Reservado ao banco
        linha_header += " " * 20  # Reservado à empresa, não obrigatório
        linha_header += " " * 11  # CNAB - deixar em branco
        linha_header += (
            " " * 3
        )  # Identificação de cobrança sem papel - deixar em branco
        linha_header += "0" * 3  # Controle VANS - deixar em branco
        linha_header += "0" * 2  # Tipo de serviço
        linha_header += " " * 10  # Ocorrências

        return f"{linha_header}\r"

    def criar_header_lote_ab(self, **kwargs):
        """
        Método responsável por criar o header do lote (AB)
        """

        self.qtd_total_registros += 1
        linha_header_lote = ""

        # sessão Controle
        linha_header_lote += self.buscar_sessao_controle("1", self.lote_num)

        # sessão Serviço
        linha_header_lote += "C"  # Tipo da operação = 'C'
        linha_header_lote += self.tipo_servico  # Tipo de serviço
        linha_header_lote += kwargs.get(
            "forma_lanc", "01"
        )  # Forma de Lançamento = '01' - Conta Corrente
        linha_header_lote += " " * 3  # Versão do layout, não obrigatório

        linha_header_lote += " "  # CNAB - deixar em branco

        # sessão Empresa
        linha_header_lote += self.buscar_sessao_empresa()

        # sessão Outras Informações
        linha_header_lote += (
            " " * 40
        )  # Informação 1 - Mensagem - Preenchimento exclusivo do BB

        linha_header_lote += " " * 30  # Ender. Empresa - logradouro - não obrigatório
        linha_header_lote += " " * 5  # Ender. Empresa - número - não obrigatório
        linha_header_lote += " " * 15  # Ender. Empresa - compl. - não obrigatório
        linha_header_lote += " " * 20  # Ender. Empresa - cidade - não obrigatório
        linha_header_lote += " " * 5  # Ender. Empresa - cep - não obrigatório
        linha_header_lote += " " * 3  # Ender. Empresa - cep compl. - não obrigatório
        linha_header_lote += " " * 2  # Ender. Empresa - uf - não obrigatório

        linha_header_lote += " " * 8  # CNAB - deixar em branco
        linha_header_lote += " " * 10  # Ocorrências

        return f"{linha_header_lote}\r"

    def criar_seg_a(self, *args, **kwargs):
        """
        Método responsável por criar o segmento A.

        Parâmetros pelo kwargs:
        - registro_num (num)
        - favorecido (dict)
        - ident_extrato_fav (str) - não obrigatório (identificação no extrato do favorecido)
        - ident_extrato_pag (str) - não obrigatório, deve ter o mesmo valor para todos os registros do lote (identificação no extrato do pagador)
        - data_pgto (date)
        - cod_camera (str)

        O parâmetro 'favorecidos' deve ser um dict com a seguinte estrutura:
        favorecido = {
            'nome': 'str',
            'cod_banco: 'num',
            'agencia_num': 'num',
            'agencia_dv': 'num',
            'conta_num': 'num',
            'conta_dv': 'num',
            'tipo_conta': 'num' ('1' - conta corrente, '2' - conta poupança)
            'valor_pgto': 'decimal',
        }
        """

        cod_banco = kwargs.get("favorecido")["cod_banco"]
        tipo_conta = str(kwargs.get("favorecido")["tipo_conta"])

        self.qtd_total_registros += 1
        linha_seg_a = ""

        # sessão Controle
        linha_seg_a += self.buscar_sessao_controle("3", self.lote_num)

        # sessão Serviço
        linha_seg_a += str(kwargs.get("registro_num")).rjust(
            5, "0"
        )  # Número do registro no lote
        linha_seg_a += "A"  # Código do segmento
        linha_seg_a += "0"  # Tipo de movimento - Inclusão = '0'
        linha_seg_a += "00"  # Código de instrução para movimento - Inclusão = '00'

        # sessão Favorecido

        # TODO - validar com cliente sobre o Código da Câmara Centralizadora
        # O validador do BB orientou que: para a Forma de Lançamento "01", o Código da Câmara Centralizadora é "000".
        # linha_seg_a += '018' # Código da Câmara Centralizadora - TED (STR, CIP) = '018'
        linha_seg_a += kwargs.get(
            "cod_camera", "000"
        )  # Código da Câmara Centralizadora - TED (STR, CIP) = '018'

        linha_seg_a += cod_banco  # Favorecido - Código do banco
        linha_seg_a += str(kwargs.get("favorecido")["agencia_num"]).rjust(
            5, "0"
        )  # Favorecido - Agência
        linha_seg_a += str(kwargs.get("favorecido")["agencia_dv"]).rjust(
            1, " "
        )  # Favorecido - Dígito Verificador da Agência
        linha_seg_a += str(kwargs.get("favorecido")["conta_num"]).rjust(
            12, "0"
        )  # Favorecido - Número da Conta
        linha_seg_a += kwargs.get("favorecido")[
            "conta_dv"
        ]  # Favorecido - Dígito Verificador da Conta

        # Tratamento em campo Dígito verificador agência/conta
        # Para contas do Banco do Brasil o campo deve ficar em branco.
        # Para contas de outros Bancos que possuem contas com dois dígitos verificadores (DV), preencher com o segundo dígito verificador da conta.
        linha_seg_a += (
            " " if cod_banco == "001" else kwargs.get("favorecido")["conta_dv"]
        )  # Favorecido - Dígito Verificador da Agência/Conta
        linha_seg_a += kwargs.get("favorecido")["nome"][:30].ljust(
            30, " "
        )  # Favorecido - Nome

        # sessão Crédito
        linha_seg_a += str(kwargs.get("ident_extrato_fav", "")).rjust(
            6, " "
        )  # Identificação extrato do favorecido
        linha_seg_a += str(kwargs.get("ident_extrato_pag", "")).rjust(
            6, " "
        )  # Identificação extrato do pagator
        linha_seg_a += " " * 8  # Utilizados pelo banco - deixar em branco
        linha_seg_a += f"{kwargs.get('data_pgto').strftime('%d%m%Y')}"  # Data do pagamento - DDMMAAAA
        linha_seg_a += "BRL"  # Tipo moeda
        linha_seg_a += "0" * 15  # Quantidade moeda - deixar com zeros

        valor_pgto = str(round(kwargs.get("favorecido")["valor_pgto"], 2)).replace(
            ".", ""
        )
        linha_seg_a += valor_pgto.rjust(15, "0")  # Valor do pagamento

        linha_seg_a += " " * 20  # Número do doc no banco - deixar em branco
        linha_seg_a += "0" * 8  # Data real do pgto - deixar com zeros
        linha_seg_a += "0" * 15  # Valor real do pgto - deixar com zeros

        # sessão Outras Informações

        # Tratamento em tipo de conta
        # Se preenchidas com '11', o sistema irá assumir a modalidade Crédito em Poupança
        linha_seg_a += (
            "11" if tipo_conta == "2" else " " * 2
        )  # Informação 2 - tipo de conta

        linha_seg_a += " " * 38  # Informação 2 - deixar em branco
        linha_seg_a += " " * 2  # Código Finalidde doc - deixar em branco
        linha_seg_a += " " * 5  # Código Finalidde ted - deixar em branco
        linha_seg_a += " " * 2  # Código Finalidde compl - deixar em branco
        linha_seg_a += " " * 3  # CNAB - deixar em branco
        linha_seg_a += "0"  # Aviso - deixar com zero
        linha_seg_a += "0" * 10  # Aviso - deixar com zeros

        return f"{linha_seg_a}\r"

    def criar_seg_b(self, *args, **kwargs):
        """
        Método responsável por criar o segmento B.

        Parâmetros pelo kwargs:
        - registro_num (num)
        - favorecido_doc (num)
        - favorecido_tipo_doc (str)
        """

        self.qtd_total_registros += 1
        linha_seg_b = ""

        # sessão Controle
        linha_seg_b += self.buscar_sessao_controle("3", self.lote_num)

        # sessão Serviço
        linha_seg_b += str(kwargs.get("registro_num")).rjust(
            5, "0"
        )  # Número do registro no lote
        linha_seg_b += "B"  # Código do segmento

        linha_seg_b += " " * 3  # CNAB - deixar em branco

        # sessão Favorecido
        linha_seg_b += kwargs.get(
            "favorecido_tipo_doc"
        )  # Favorecido - Tipo de inscrição - CPF = '1', CNPJ = '2'
        linha_seg_b += str(kwargs.get("favorecido_doc")).rjust(
            14, "0"
        )  # Doc do Favorecido
        linha_seg_b += " " * 30  # Favorecido - Logradouro, não obrigatório
        linha_seg_b += "0" * 5  # Favorecido - Número, não obrigatório
        linha_seg_b += " " * 15  # Favorecido - Complemento, não obrigatório
        linha_seg_b += " " * 15  # Favorecido - Bairro, não obrigatório
        linha_seg_b += " " * 20  # Favorecido - Cidade, não obrigatório
        linha_seg_b += "0" * 5  # Favorecido - CEP, não obrigatório
        linha_seg_b += " " * 3  # Favorecido - CEP complemento, não obrigatório
        linha_seg_b += " " * 2  # Favorecido - UF, não obrigatório
        linha_seg_b += "0" * 8  # Favorecido - Data do Vencimento, não obrigatório
        linha_seg_b += "0" * 15  # Favorecido - Valor do documento, não obrigatório
        linha_seg_b += "0" * 15  # Favorecido - Valor do abatimento, não obrigatório
        linha_seg_b += "0" * 15  # Favorecido - Valor do desconto, não obrigatório
        linha_seg_b += "0" * 15  # Favorecido - Valor da mora, não obrigatório
        linha_seg_b += "0" * 15  # Favorecido - Valor da multa, não obrigatório
        linha_seg_b += (
            " " * 15
        )  # Favorecido - Cód./Documento do favorecido, não obrigatório
        linha_seg_b += "0"  # Aviso ao favorecido
        linha_seg_b += " " * 6  # Código UG (uso para o SIAPE), deixar em branco
        linha_seg_b += "0" * 8  # Código ISPB, deixar em branco

        return f"{linha_seg_b}\r"

    def criar_trailer_lote(self, *args, **kwargs):
        """
        Método responsável por criar o trailer do lote.

        Parâmetros pelo kwargs:
        - lote_num (num)
        - qtd_registros_lote (num)
        - total_valores (num)
        """

        self.qtd_total_registros += 1
        linha_trailer_lote = ""

        # sessão Controle
        linha_trailer_lote += self.buscar_sessao_controle("5", kwargs.get("lote_num"))

        linha_trailer_lote += " " * 9  # CNAB - deixar em branco

        # sessão Totais
        linha_trailer_lote += str(kwargs.get("qtd_registros_lote")).rjust(
            6, "0"
        )  # Quantidade de registros do lote
        linha_trailer_lote += (
            str(round(kwargs.get("total_valores"), 2)).replace(".", "").rjust(18, "0")
        )  # Somatória dos valores do lote
        linha_trailer_lote += "0" * 18  # Quantidade moeda - deixar com zeros

        # sessão Outras Informações
        linha_trailer_lote += "0" * 6  # Número aviso débitos - deixar com zeros
        linha_trailer_lote += " " * 165  # CNAB - deixar em branco
        linha_trailer_lote += " " * 10  # Ocorrências - deixar em branco

        return f"{linha_trailer_lote}\r"

    def criar_trailer_arquivo(self, *args, **kwargs):
        """
        Método responsável por criar o trailer do lote.
        """

        self.qtd_total_registros += 1
        linha_trailer_arq = ""

        # sessão Controle
        linha_trailer_arq += self.buscar_sessao_controle("9", "9999")

        linha_trailer_arq += " " * 9  # CNAB - deixar em branco

        # sessão Totais
        linha_trailer_arq += str(self.qtd_lotes).rjust(
            6, "0"
        )  # Quantidade total de lotes
        linha_trailer_arq += str(self.qtd_total_registros).rjust(
            6, "0"
        )  # Quantidade total de registros
        linha_trailer_arq += "0" * 6  # Quantidade contas concil

        linha_trailer_arq += " " * 205  # CNAB - deixar em branco

        return f"{linha_trailer_arq}\r"
