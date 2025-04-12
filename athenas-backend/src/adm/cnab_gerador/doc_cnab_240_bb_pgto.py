"""
Consolidação da documentação para geração de arquivo CNAB 240 do Banco do Brasil (bb).
Com base na documentação da versão: novembro/2019.

Esta documentação é para geração de arquivos para pagamentos de seguimentos AB, disponibilizando os tipos de pagamentos:
    - Pagamento a Fornecedor = '20'
    - Pagamento de Salário = '30'
    - Pagamentos Diversos = '98'

Definições na geração do arquivo:
    - O arquivo deve estar ANSI (ISO-8859-1)
    - No final de cada linha, na posição 241, deve conter caractere de quebra de linha.
    - A extensão do arquivo deve ser '.txt'.

A composição das informações do arquivo deve seguir a ordem:
    > header do arquivo
    > header lote AB
    > segmento A
    > segmento B
    > trailer lote
    > trailer arquivo

Obs.:
Os pagamentos aos favorecidos com contas no Banco do Brasil devem estar em um único lote.
E aos favorecidos com contas em outros banco devem estar em um lote separado, porém unificados em um mesmo lote.

A composição de um lote é:
    > header lote AB
    > segmento A
    > segmento B
    > trailer lote

Abaixo segue mapa com as posições das informações.
"""

header_arquivo = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote_servico": "0000",  # 4 - 7 qtd: 4 (num)
        "tipo_registro": "0",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "cnab": "",  # 9 - 17 qtd: 9 (alfa) - deixar em branco
    "empresa": {
        "tipo_inscr": "2",  # 18 - 18 qtd: 1 (num) - CPF = '1' ou CNPJ = '2'
        "num_inscr": "",  # 19 - 32 qtd: 14 (num) - Número da inscrição (CNPJ da Empresa), alinhado à direita com zeros à esquerda
        "numero_conveio": "",  # 33 - 45 qtd: 13 (num) - número do convênio
        "reservado_banco": "",  # 46 - 50 qtd: 5 (alfa) - deixar em branco
        "arquivo_teste": "",  # 51 - 52 qtd: 2 (alfa) - Em produção = Brancos ou Em teste = 'TS'
        "agencia": "",  # 53 - 57 qtd: 5 (num) - Número da agência - Alinhar a direita com zeros à esquerda
        "agencia_dv": "",  # 58 - 58 qtd: 1 (alfa) - Dig. verificador da agência - Em caso de dígito X informar maiúsculo
        "cc": "",  # 59 - 70 qtd: 12 (num) - Número da conta corrente - Alinhar a direita com zeros à esquerda
        "cc_dv": "",  # 71 - 71 qtd: 1 (alfa) - Dig. verificador da agência - Em caso de dígito X informar maiúsculo.
        "ag_cc_dv": "",  # 72 - 72 qtd: 1 (num)
        # Banco do Brasil = branco, Outros Bancos = Para favorecidos de outros bancos que possuem contas com dois dígitos verificadores (DV),
        # preencher este campo com o segundo dígito verificador.
        "nome_empresa": "",  # 73 - 102 qtd: 30 (num) - Nome da empresa
    },
    "nome_banco": "BANCO DO BRASIL",  # 103 - 132 qtd: 30 (alfa)
    "cnab": "",  # 133 - 142 qtd: 10 (alfa) - deixar em branco
    "codigo_remessa": "1",  # 143 - 143 qtd: 1 (num) - Arquivo Remessa = '1' ou Arquivo Retorno = '2'
    "data_geracao_arquivo": "",  # - 144 - 151 qtd: 8 (num) - DDMMAAAA
    "hora_geracao_arquivo": "",  # - 152 - 157 qtd: 6 (num) - não obrigatório, preencher com zeros ou HHMMSS
    "num_seq_arquivo": "000000",  # - 158 - 163 qtd: 6 (num) - não obrigatório, preencher com zeros ou número sequencial incrmentado
    "num_versao_layout": "",  # 164 - 166 qtd: 3 (num) - não obrigatório, deixar vazio ou número da versão do layout
    "densidade": "00000",  # 167 - 171 qtd: 5 (num)
    "reservado_banco": "",  # 172 - 191 qtd: 20 (alfa) - deixar vazio para ser utilizado pelo banco
    "reservado_empresa": "",  # 192 - 211 qtd: 20 (alfa) - não obrigatório
    "cnab": "",  # 212 - 222 qtd: 11 (alfa) - deixar em branco
    "identif_cobranca": "",  # 223 - 225 qtd: 3 (alfa) - deixar em branco
    "controle_vans": "",  # 226 - 228 qtd: 3 (num) - deixar em branco
    "tipo_servico": "00",  # 229 - 230 qtd: 2 (num)
    "ocorrencias": "0000000000",  # 231 - 240 qtd: 10 (alfa)
}

header_lote_ab = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote": "",  # 4 - 7 qtd: 4 (num)
        # Se primeiro lote do arquivo, começar com '0001'. Essa informação deve ser igual em todos os registros
        # desse lote, até o seu trailer. Se o arquivo possui mais de um lote, incrementar em 1 cada lote, exemplo
        # o 2º lote do arquivo é o '0002', e assim sucessivamente
        "tipo_registro": "1",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "servico": {
        "operacao": "C",  # 9 - 9 qtd: 1 (alfa) - Tipo da Operação
        "tipo_servico": "20",  # 10 - 11 qtd: 2 (num) - Pagamento a Fornecedor = '20, Pagamento de Salário = '30 ou Pagamentos Diversos = '98'
        "forma_lanc": "01",  # 12 - 13 qtd: 2 (alfa) - conta corrente = '01'
        "layout_lote": "000",  # 14 - 16 qtd: 3 (num) - N° da versão do layout do lote
    },
    "cnab": "",  # 17 - 17 qtd: 1 (alfa) - deixar em branco
    "empresa": {
        "tipo_inscr": "2",  # 18 - 18 qtd: 1 (num) - CPF = '1' ou CNPJ = '2'
        "num_inscr": "",  # 19 - 32 qtd: 14 (num) - Número da inscrição (CNPJ da Empresa), alinhado à direita com zeros à esquerda
        "numero_conveio": "",  # 33 - 45 qtd: 13 (num) - número do convênio
        "reservado_banco": "",  # 46 - 50 qtd: 5 (alfa) - deixar em branco
        "arquivo_teste": "",  # 51 - 52 qtd: 2 (alfa) - Em produção = Brancos ou Em teste = 'TS'
        "agencia": "",  # 53 - 57 qtd: 5 (num) - Número da agência - Alinhar a direita com zeros à esquerda
        "agencia_dv": "",  # 58 - 58 qtd: 1 (alfa) - Dig. verificador da agência - Em caso de dígito X informar maiúsculo
        "cc": "",  # 59 - 70 qtd: 12 (num) - Número da conta corrente - Alinhar a direita com zeros à esquerda
        "cc_dv": "",  # 71 - 71 qtd: 1 (alfa) - Dig. verificador da agência - Em caso de dígito X informar maiúsculo.
        "ag_cc_dv": "",  # 72 - 72 qtd: 1 (num)
        # Banco do Brasil = branco, Outros Bancos = Para favorecidos de outros bancos que possuem contas com dois dígitos verificadores (DV),
        # preencher este campo com o segundo dígito verificador.
        "nome_empresa": "",  # 73 - 102 qtd: 30 (num) - Nome da empresa
    },
    "info_1": "",  # 103 - 142 qtd: 40 (alfa) - deixar em branco
    "endereco_empresa": {
        "logr": "",  # 143 - 172 qtd: 30 (alfa) - não obrigatório, deixar em branco
        "num": "00000",  # 173 - 177 qtd: 5 (num) - não obrigatório, completar com zeros
        "compl": "",  # 178 - 192 qtd: 15 (alfa) - não obrigatório, deixar em branco
        "cidade": "",  # 193 - 212 qtd: 20 (alfa) - não obrigatório, deixar em branco
        "cep": "00000",  # 213 - 217 qtd: 5 (alfa) - não obrigatório, completar com zeros
        "cep_compl": "",  # 218 - 220 qtd: 3 (alfa) - não obrigatório, deixar em branco
        "uf": "",  # 221 - 222 qtd: 2 (alfa) - não obrigatório, deixar em branco
    },
    "cnab": "",  # 223 - 230 qtd: 8 (alfa) - deixar em branco
    "ocorrencia": "0000000000",  # 231 - 240 qtd: 10 (alfa) - Arquivo Remessa = '0000000000'
}

seg_a = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote": "",  # 4 - 7 qtd: 4 (num) - Informar o número do lote ao qual pertence o registro. Deve ser igual ao número informado no Header do lote
        "tipo_registro": "3",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "servico": {
        "num_registro": "00001",  # 9 - 13 qtd: 5 (num)
        # Começar com 00001 no primeiro registro detalhe do lote, e ir incrementando em 1 a cada nova linha de registro detalhe
        "cod_segmento": "A",  # 14 - 14 qtd: 1 (alfa) - Còdigo do segmento
        "tipo_movimento": "0",  # 15 -15 qtd: 1 (num) - Inclusão = '0'
        "cod_instr_movimento": "00",  # 16 - 17 qtd: 2 (num) - Inclusão = '00'
    },
    "favorecido": {
        "cod_camara": "018",  # 18 - 20 qtd: 3 (num) - Código da Câmara Centralizadora - TED (STR, CIP) = '018'
        "cod_banco": "",  # 21 - 23 qtd: 3 (num) - Código do banco do favorecido
        "agencia": "",  # 24 - 28 qtd: 5 (num) - Número da agência - Alinhar a direita com zeros à esquerda
        "agencia_dv": "",  # 29 - 29 qtd: 1 (alfa) - Dig. verificador da agência - Em caso de dígito X informar maiúsculo
        "cc": "",  # 30 - 41 qtd: 12 (num) - Número da conta corrente - Alinhar a direita com zeros à esquerda
        "cc_dv": "",  # 42 - 42 qtd: 1 (alfa) - Dig. verificador da conta - Em caso de dígito X informar maiúsculo.
        # Banco do Brasil = branco, Outros Bancos = Para favorecidos de outros bancos que possuem contas com dois dígitos verificadores (DV),
        # preencher este campo com o segundo dígito verificador.
        "ag_cc_dv": "",  # 43 - 43 qtd: 1 (num)
        "nome": "",  # 44 - 73 qtd: 30 (num) - Nome do favorecido
    },
    "credito": {
        "identif_extrato": "",  # 74 - 93 qtd: 20 (alfa)
        # Os número colocados nas posições 74 a 79 aparecerão como número do documento no extrato do favorecido, e os números das
        # posições 80 a 85, serão utilizadas como número do documento no extrato do pagador. Obs.: Como os lançamentos ocorridos na conta
        # do pagador são aglutinados num mesmo lote as posições 80 a 85 de todos os detalhes devem ser iguais, caso contrário será
        # considerado apenas o número constante no primeiro registro detalhe de cada lote. As posições 86 a 93 não são tratadas pelo sistema.
        # As informações impostas nessa posição voltarão iguais no arquivo retorno.
        "data_pgto": "",  # 94 - 101 qtd: 8 (num) - DDMMAAAA
        "tipo_moeda": "BRL",  # 102 - 104 qtd: 3 (alfa)
        "qtd_moeda": "000000000000000",  # 105 - 119 qtd: 15 (num)
        "valor_pgto": "",  # 120- 134 qtd: 13 - decimal: 2 (num)
        "num_doc_banco": "",  # 135 - 154 qtd: 20 (alfa) - utilizado pelo banco, deixar em branco
        "dt_real_pgto": "00000000",  # 155 - 162 qtd: 8 (num), deixar com zeros (8)
        "valor_real_pgto": "000000000000000",  # 163 - 177 qtd: 13 - decimal: 2 (num), deixar com zeros
    },
    "infos_2": {
        "outras_infos": "",  # 178 - 217 qtd: 40 (alfa)
        # Caso as posições 178 e 179 estajam preenchidas com '11', o sistema irá assumir a modalidade Crédito em Poupança
    },
    "cod_finalidade_doc": "",  # 218 - 219 qtd: qtd: 2 (alfa) - deixar em branco
    "cod_finalidade_ted": "",  # 220 - 224 qtd: 5 (alfa) - deixar em branco
    "cod_finalidade_compl": "",  # 225 - 226 qtd: 2 (alfa) - deixar em branco
    "cnab": "",  # 227 - 229 qtd: 3 (alfa) - deixar em branco
    "aviso": "0",  # 230 - 230 qtd: 1 (num)
    "ocorrencias": "0000000000",  # 231 - 240 qtd: 10 (alfa) - deixar com zeros
}

seg_b = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote": "",  # 4 - 7 qtd: 4 (num) - Informar o número do lote ao qual pertence o registro. Deve ser igual ao número informado no Header do lote
        "tipo_registro": "3",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "servico": {
        "num_registro": "00001",  # 9 - 13 qtd: 5 (num)
        # Começar com 00001 no primeiro registro detalhe do lote, e ir incrementando em 1 a cada nova linha de registro detalhe
        "cod_segmento": "B",  # 14 - 14 qtd: 1 (alfa) - Còdigo do segmento
    },
    "cnab": "",  # 15 - 17 qtd: 3(alfa) - deixar em branco
    "favorecido": {
        "tipo_inscr": "1",  # 18 - 18 (num) qtd: 1 - CPF = '1' ou CNPJ = '2'
        "num_inscr": "",  # 19 - 32 qtd: 14 (num) - Número da inscrição (CPF ou CNPJ) da Empresa, alinhado à direita com zeros à esquerda
        "endereco": {
            "logr": "",  # 33 - 62 qtd: 30 (alfa) - não obrigatório, deixar em branco
            "num": "00000",  # 63 - 67 qtd: 5 (num) - não obrigatório, completar com zeros
            "compl": "",  # 68 - 82 qtd: 15 (alfa) - não obrigatório, deixar em branco
            "bairro": "",  # 83 - 97 qtd: 15 (alfa) - não obrigatório, deixar em branco
            "cidade": "",  # 98 - 117 qtd: 20 (alfa) - não obrigatório, deixar em branco
            "cep": "00000",  # 118 - 122 qtd: 5 (alfa) - não obrigatório, completar com zeros
            "cep_compl": "",  # 123 - 125 qtd: 3 (alfa) - não obrigatório, deixar em branco
            "uf": "",  # 126 - 127 qtd: 2 (alfa) - não obrigatório, deixar em branco
        },
        "pgto": {
            "data_venc": "",  # 128 - 135 qtd: 8 (num) - não obrigatório, completar com zeros
            "valor_doc": "",  # 136 - 150 qtd: 15 (num) - não obrigatório, completar com zeros
            "valor_abat": "",  # 151 - 165 qtd: 15 (num) - não obrigatório, completar com zeros
            "valor_desc": "",  # 166 - 180 qtd: 15 (num) - não obrigatório, completar com zeros
            "valor_mora": "",  # 181 - 195 qtd: 15 (num) - não obrigatório, completar com zeros
            "valor_multa": "",  # 196 - 210 qtd: 15 (num) - não obrigatório, completar com zeros
        },
        "cod_favorecido": "",  # 211 - 225 qtd: 15 (alfa) - não obrigatório, deixar em branco
    },
    "aviso": "0",  # 226 - 226 qtd: 1 (alfa) - não obrigatório, deixar em branco
    "cod_ug": "0",  # 227 - 232 qtd: 6 (alfa) - não obrigatório, deixar em branco
    "cod_ispb": "0",  # 233 - 240 qtd: 8 (alfa) - não obrigatório, deixar em branco
}

trailer_lote = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote_servico": "0000",  # 4 - 7 qtd: 4 (num) - informar o mesmo número do header do lote
        "tipo_registro": "5",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "cnab": "",  # 9 - 17 qtd: 9 (alfa) - deixar em branco
    "totais": {
        "qtd_registros_lote": "",  # 18 - 23 qtd: 6 (num) - Somatório dos registros tipo 1 e 3
        "total_valores": "",  # 24 - 41 qtd: 16 - decimal: 2 (num) - Somatório dos valores de pagamento dos registros de detalhe (Registro = '3')
        "total_qtd_moedas": "000000000000000000",  # 42 - 59 qtd: 18 (num)
    },
    "num_aviso_debito": "000000",  # 60 - 65 qtd: 6 (num)
    "cnab": "",  # 66 - 230 qtd: 165 (alfa) - deixar em branco
    "ocorrencias": "0000000000",  # 231 - 240 qtd: 10 (alfa)
}

trailer_arquivo = {
    "controle": {
        "banco": "001",  # 1 - 3 qtd: 3 (num) - Código no Banco da Compensação
        "lote_servico": "9999",  # 4 - 7 qtd: 4 (num)
        "tipo_registro": "9",  # 8 - 8 qtd: 1 (num) - Tipo de Registro
    },
    "cnab": "",  # 9 - 17 qtd: 9 (alfa) - deixar em branco
    "totais": {
        "qtd_lotes": "",  # 18 - 23 qtd: 6 (num) - Somatória dos registros de tipo 1
        "qtd_registros": "",  # 24 - 29 qtd: 6 (num) - Somatória dos registros de tipo 0, 1, 3, 5 e 9
        "qtd_contas_concil": "000000",  # 30 - 35 qtd: 6 (num)
    },
    "cnab": "",  # 36 - 240 qtd: 205 (alfa) - deixar em branco
}
