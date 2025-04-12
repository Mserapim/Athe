# -.- coding: utf-8 -.-
import os

import OpenSSL

from contrib.utils import getLogger
from esocial.managers.file_support import directory_certs

log = getLogger(__name__)


BASE_CERTS_STORE = directory_certs()
PRIVATE_KEY = "%s/pkey_without_pass.pem" % BASE_CERTS_STORE
CERTIFICATE_X509_FILE = "%s/x509.pem" % BASE_CERTS_STORE
CACERTS = "%s/cacerts.pem" % BASE_CERTS_STORE


def extract_certificate(certificate_path=None, certificate_ca_path=None, passwd=""):
    """Este método extrai a chave privada do certificado e a x509. Também cria o arquivo cacerts.pem a partir de certificate_ca_path."""

    certificate_path = certificate_path.absolute_path if certificate_path else None
    certificate_ca_path = (
        certificate_ca_path.absolute_path if certificate_ca_path else None
    )

    dir_certs = directory_certs()

    x509_file_name = "%s/x509.pem" % dir_certs
    pkey_file_name = "%s/pkey_without_pass.pem" % dir_certs
    cacerts_file_name = "%s/cacerts.pem" % dir_certs

    if certificate_path:
        p12 = OpenSSL.crypto.load_pkcs12(open(certificate_path, "rb").read(), passwd)
        with open(x509_file_name, "wb") as certx509:
            certx509.write(
                OpenSSL.crypto.dump_certificate(
                    OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()
                )
            )
        with open(pkey_file_name, "wb") as private_key:
            private_key.write(
                OpenSSL.crypto.dump_privatekey(
                    OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()
                )
            )

    if certificate_ca_path:
        with open(cacerts_file_name, "wb") as ca_certificate:
            ca_certificate.write(open(certificate_ca_path, "rb").read())

    if os.path.exists(x509_file_name):
        log.info("Arquivo x509 criado com sucesso!")
    if os.path.exists(pkey_file_name):
        log.info("Arquivo pfx criado com sucesso!")
    if os.path.exists(cacerts_file_name):
        log.info("Arquivo cacerts criado com sucesso!")

    return True
