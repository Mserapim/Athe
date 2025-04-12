# -.- coding: utf-8 -.-
from requests import Request, Session
from zeep import Client
from zeep.transports import Transport

import certifi
import requests
import logging
import os


logging.basicConfig(filename="webservice.log", level=logging.DEBUG)

URL_TEST = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc?singleWsdl"
BASE_CERTS_STORE = "/home/gustavodettenborn/developer/containers/athenas/volumes/storage/esocial/security/store"
PRIVATE_KEY = "%s/pkey_without_pass.pem" % BASE_CERTS_STORE
CERTIFICATE_X509_FILE = "%s/x509.pem" % BASE_CERTS_STORE
CACERTS = "%s/cacerts.pem" % BASE_CERTS_STORE


class ESocialClient(Client):

    WSDL = None

    def __init__(self, wsdl=None, **kwargs):
        """
        @param url: The URL for the WSDL.
        @type url: str
        @param kwargs: keyword arguments.
        @see: L{Options}
        """
        wsdl = wsdl if wsdl else self.WSDL
        session = Session()

        session.cert = (CERTIFICATE_X509_FILE, PRIVATE_KEY)
        session.verify = CACERTS
        transport = Transport(session=session)
        kwargs.update({"transport": transport})
        super(ESocialClient, self).__init__(wsdl, **kwargs)


class ClientSendEventBatch(ESocialClient):

    def __init__(self, wsdl=None, **kwargs):
        super(ClientSendEventBatch, self).__init__(
            "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc?singleWsdl",
            **kwargs,
        )

    def service_send_event_batch(self, message):
        self.service.EnviarLoteEventos(message)


def run_zeep():
    print(f"\nverify: CACERTS: {CACERTS}")
    try:
        client = ClientSendEventBatch()
        print(client)
    except Exception as err:
        print(err)


def run():
    run_zeep()


if __name__ == "__main__":
    run()
