import hashlib
import os
import re
from functools import partial

from django.conf import settings
from PyPDF2 import PdfWriter, PdfReader
from contrib.middleware import set_current_user

from contrib.utils import getLogger
from ged.models import Arquivo
from rh.models import Servidor, User
from rh.queryregistration.ged_file import GedFile
import base64

log = getLogger(__name__)


def tmp_dir():
    """
    Função que retorna o path padrão para salvar arquivos da importação de Cédula C
    """
    return os.path.join(settings.UPLOAD_STORE_DIR, "import_cc")


def search_cpf_and_indentifier(text: str) -> str or None:
    """
    Esta função identifica se é o pdf é início de um novo documento,
    verificando se há a presença de dois elementos um CPF e o CNPJ
    da instituição descrita como "Fonte Pagadora".

    :params: text (str) Página do PDF convertida em texto

    :returns: str: Numero do CPF do servidor (sem pontuação) ou None
    """
    padrao = re.compile(r"([0-9]{3}[.]?[0-9]{3}[.]?[0-9]{3}[-]?[0-9]{2})")
    cnpj_mpmt = "14.921.092/0001-57"
    cnpj_tre = "05.901.308/0001-21"
    busca = padrao.search(text)
    busca2 = re.search(cnpj_mpmt, text) or re.search(cnpj_tre, text)
    if busca and busca2:
        return busca.group().replace("-", "").replace(".", "")
    else:
        return None


def create_gedfile(
    filepath: str, user: User, mimetype: str, identifier: str
) -> GedFile:
    """
    Função responsável por criar o arquivo GedFile e salvar na pasta
    padronizada, vinculando com o user do servidor

    :params: filepath (str) Caminho absoluto do arquivo cache
    :params: user (User) Usuário a ser vinculado ao arquivo
    :params: mimetype (str) Tipo de Formatação do Arquivo
    :params: identifier (str) Nome identificador do arquivo

    :returns: GedFile: Objeto de salvamento do arquivo

    """
    ged = None
    set_current_user(user.pk)
    with open(filepath, "rb") as fd:
        buffer = b"".join([chunk for chunk in iter(partial(fd.read, 8192), b"")])
    signature = Arquivo.hash_buffer(buffer)
    gedfile = GedFile(signature, identifier)
    ged = Arquivo().from_filepath(filepath, user, mimetype)
    gedfile.save_file(gedfile, signature, buffer)
    ahash = Arquivo.hash_file(filepath, hashlib.md5())
    ged.save_file(ged, ahash, buffer)
    try:
        Arquivo.objects.filter(pk=ged.pk).update(file=ahash)
    except Exception as err:
        log.error(err)
    return gedfile, ged


def get_filepath(filepath: str, filename: str) -> str:
    """
    Função que cria um diretório para salvamento de arquivo em cache.

    :params: filepath (str) caminho (path) para o arquivo, se houver.
    :params: filename (str) nome do arquivo.

    :returns: str: caminho (path) para salvamento em cache.
    """
    if not filepath:
        filepath = os.path.join(tmp_dir(), filename)
        if not os.path.exists(tmp_dir()):
            os.makedirs(tmp_dir())
    return filepath


def create_pdf_cedula_c(
    reader: PdfReader,
    page: int,
    output: PdfWriter,
    cpf: str,
    reference: str,
    gedfile: GedFile,
    servidor: Servidor,
    arquivo: Arquivo,
) -> GedFile:
    """
    Esta função divide um PDF contendo vários documentos de Cédula-C,
    separando por cpf de servidor e salva cada arquivo por usuário.

    :params: reader (PdfReader) Leitor para pdf
    :params: page (int) Página do arquivo que será tratada
    :params: output (PdfWriter) Instância de Writer para,
        podendo ser uma nova inst. ou já conter outras páginas
    :params: cpf (str) Numero do cpf contido no documento
        as ser utilizado para vincular com servidor
    :params: reference (str) Ano-Tipo de referência da Cédula-c
    :params: gedfile (GedFile) Instância de Gedfile
    :params: servidor (Servidor) Servidor vinculado ao arquivo
    :params: arquivo (Arquivo) Instância de Arquivo

    :returns: tuple -[0] GedFile:Instância de Gedfile
    -[1]Servidor: Servidor vinculado ao arquivo
    -[2]Arquivo: Instância do arquivo criado/modificado
    """
    mimetype = "application/pdf"
    identifier = "cedula-c"
    if gedfile and servidor and arquivo:
        try:
            filename = f"cedula-c-{reference}-{servidor.pessoa_fisica.nome}"
            output.add_page(reader.pages[page])
            filepath = arquivo.absolute_path
            with open(filepath, "wb") as f:
                PdfWriter.write(output, f)
        except Exception as err:
            log.error(err)
    else:
        try:
            arquivos = None
            servidor = Servidor.objects.filter(
                pessoa_fisica__cpf=cpf, ativo=True
            ).last()
            if not servidor:
                servidor = Servidor.objects.filter(pessoa_fisica__cpf=cpf).last()

            arquivos = Arquivo.objects.filter(
                user=servidor.user, filename__icontains="cedula-c-R"
            )
            if arquivos:
                arquivos.delete()

            filename = f"cedula-c-{reference}-{servidor.pessoa_fisica.nome}"
            output.add_page(reader.pages[page])
            filepath = get_filepath(filepath=None, filename=filename)
            with open(filepath, "wb") as f:
                output.write(f)

        except Exception as err:
            log.error(err)

    if servidor and servidor.user:
        gedfile, arquivo = create_gedfile(
            filepath=filepath,
            user=servidor.user,
            mimetype=mimetype,
            identifier=identifier,
        )
        return gedfile, servidor, arquivo
    return None, None, arquivo


def get_cedula_c(cpf, year):
    """
    Esta função retorna um dicionaŕio com o arquivo da cédula-c

    :params: cpf (str) cpf do servidor/beneficiário
    :params: year (int) Ano/referência da cédula-c

    :returns: dict (base64) arquivo da cédula-c
    """
    data = {"file": None, "message": "Nada do feito ainda."}
    employee = Servidor.objects.filter(pessoa_fisica__cpf=cpf, ativo=True).first()
    document = Arquivo.objects.filter(
        user=employee.user, filename__icontains=f"cedula-c-{year}-MPMT"
    ).last()
    if document:
        try:
            with open(document.absolute_path, "rb") as f:
                file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes)
            data.update(file=file_b64, message="Cédula-c gerada com sucesso.")
            return data
        except Exception as e:
            log.info(e)
    data.update(message="Não foi encontrada cédula-c.")
    return data
