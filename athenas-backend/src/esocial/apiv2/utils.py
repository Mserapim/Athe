import codecs
from datetime import datetime
import os
import uuid
from django.conf import settings


def get_categoria_tipo_pessoa():
    return [
        {"texto": "Servidor Ativo", "valor": 1},
        {"texto": "Servidor Inativo", "valor": 2},
        {"texto": "Dependente", "valor": 3},
        {"texto": "Pensionista", "valor": 4},
        {"texto": "Estagiário", "valor": 5},
        {"texto": "Alimentando", "valor": 6},
        {"texto": "Desconhecido", "valor": 7},
    ]


def get_status_qualificacao():
    return [
        {"texto": "Aguardando qualificação", "valor": 1},
        {"texto": "Erro nos dados", "valor": 2},
        {"texto": "Processado com erro", "valor": 3},
        {"texto": "Rejeitado", "valor": 4},
        {"texto": "Qualificado", "valor": 10},
    ]


def get_filtro_orientacao_cpf():
    return [
        {"texto": "OK", "valor": 0},
        {"texto": "Procurar Conveniadas da RFB", "valor": 1},
    ]


def get_filtro_orientacao_nis_pis_pasep():
    return [
        {"texto": "OK", "valor": 0},
        {"texto": "Atualizar NIS no INSS", "valor": 1},
        {"texto": "Atualizar NIS na CAIXA", "valor": 2},
        {"texto": "Atualizar NIS no BB", "valor": 3},
    ]


def criar_arquivo_qualificacao(caminho_arquivo, objs=[], xml=False):
    """Este método criar o arquivo de qualificação cadaastral
    Args:
        caminho_arquivo (str):caminho do arquivo
        objs (list): valores
        xml (bool)
    Returns:
        arquivo
    """
    if not os.path.exists(os.path.dirname(caminho_arquivo)):
        os.makedirs(os.path.dirname(caminho_arquivo))
    if xml:
        objs.write(caminho_arquivo, encoding="utf-8", xml_declaration=True)
    else:
        with codecs.open(caminho_arquivo, "w", "utf-8") as fd:
            try:
                iter(objs)
            except TypeError:
                fd.write(str(objs))
            else:
                fd.writelines(objs)
    return caminho_arquivo


def get_gerar_nome_arquivo():
    today = datetime.now().strftime("%d%m%Y")
    return "%s_%s.txt" % (settings.ORGAN_IDENTIFIER, today)


def tmp_dir(dir):
    cod_uuid = uuid.uuid1().hex
    return os.path.join(settings.UPLOAD_STORE_DIR, dir, cod_uuid)
