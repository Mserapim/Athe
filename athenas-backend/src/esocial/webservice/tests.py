# -.- coding: utf-8 -.-
import unittest
from esocial.webservice import (
    ESocialClient,
    ClientSendEventBatch,
    ClientConsultEventBatch,
)

import requests
from requests import Session

# from contrib.utils import getLogger

# These lines enable debug logging; remove them once everything works.
import logging

logging.basicConfig(filename="webservice.log", level=logging.DEBUG)
logging.getLogger("suds").setLevel(logging.DEBUG)
logging.getLogger("suds.client").setLevel(logging.DEBUG)
logging.getLogger("suds.transport").setLevel(logging.DEBUG)

# log = getLogger(__name__)


# url_test = 'https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/consultarloteeventos/WsConsultarLoteEventos.svc?singleWsdl'
url_test = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc?singleWsdl"
BASE_DIR = "/app/root/esocial/security"
# PRIVATE_KEY = "%s/store/keypgjto.pem" % BASE_DIR
PRIVATE_KEY = "%s/store/keynopass.pem" % BASE_DIR
PASSWORD = b"1234"
CERTIFICATE_X509_FILE = "%s/store/pgjtoA1ecnpjx509pem.cer" % BASE_DIR
CACERTS = "/app/root/esocial/security/store/pgjtoA1ecnpjcacerts.pem"


class ESocialClientTestCase(unittest.TestCase):

    @unittest.skip("zeep_test")
    def zeep_test(self):
        print("zeep_test")
        from requests import Session
        from zeep import Client
        from zeep.transports import Transport
        from zeep.transports import Signature

        session = Session()
        # session.verify = '/home/user/certs/gustavodettenbornserasa.pem'
        # session.verify = '/home/user/certs/gustavodettenbornserasa_allca.pem'
        # session.verify = '/app/root/esocial/security/store/pgjtoA1ecnpjsemhierarquia.pem'
        # session.verify = '/app/root/esocial/security/store/pgjtoA1ecnpjcompleto.pem'
        transport = Transport(session=session)
        client = Client(url_test, transport=transport)

    @unittest.skip("test suds")
    def test_new_suds(self):
        from future.standard_library import install_aliases

        install_aliases()
        import urllib.request
        import urllib.error
        import urllib.parse
        import http.client
        import socket
        from suds.client import Client
        from suds.transport.http import HttpTransport, Reply, TransportError

        class HTTPSClientAuthHandler(urllib.request.HTTPSHandler):
            def __init__(self, key, cert):
                urllib.request.HTTPSHandler.__init__(self)
                self.key = key
                self.cert = cert

            def https_open(self, req):
                # Rather than pass in a reference to a connection class, we pass in
                # a reference to a function which, for all intents and purposes,
                # will behave as a constructor
                return self.do_open(self.getConnection, req)

            def getConnection(self, host, timeout=300):
                return http.client.HTTPSConnection(
                    host, key_file=self.key, cert_file=self.cert
                )

        class HTTPSClientCertTransport(HttpTransport):
            def __init__(self, key, cert, *args, **kwargs):
                HttpTransport.__init__(self, *args, **kwargs)
                self.key = key
                self.cert = cert

            def u2open(self, u2request):
                """
                Open a connection.
                @param u2request: A urllib2 request.
                @type u2request: urllib2.Requet.
                @return: The opened file-like urllib2 object.
                @rtype: fp
                """
                tm = self.options.timeout
                url = urllib.request.build_opener(
                    HTTPSClientAuthHandler(self.key, self.cert)
                )
                if self.u2ver() < 2.6:
                    socket.setdefaulttimeout(tm)
                    return url.open(u2request)
                else:
                    return url.open(u2request, timeout=tm)

        c = Client(
            url_test,
            transport=HTTPSClientCertTransport(PRIVATE_KEY, CERTIFICATE_X509_FILE),
        )
        print(c)

    @unittest.skip("test_request")
    def test_request(self):
        import os
        import requests

        # key_filename = "/etc/ssl/certs/cert.key.pem"
        # cert_filename = "/etc/ssl/certs/cert.crt.pem"
        key_filename = PRIVATE_KEY
        cert_filename = CERTIFICATE_X509_FILE

        # r = requests.get(url_test, cert=(cert_filename, key_filename), verify=False)
        # print r
        # try:
        #     print('------------------------------------------------------------------')
        #     session = requests.Session()
        #     session.cert = (cert_filename, key_filename)
        #     print('verify with: %s' % CACERTS)
        #     session.verify = CACERTS
        #     r = session.get(url_test)
        #     print(r)
        # except Exception as err:
        #     print('err 1')
        #     print(err)
        # try:
        print("------------------------------------------------------------------")
        session = requests.Session()
        session.cert = (cert_filename, key_filename)
        # cacerts_all = '%s/store/AC-Raiz-V5.pem' % BASE_DIR
        # cacerts_all = '%s/store/cacerts.pem' % BASE_DIR
        cacerts_all = "/app/root/esocial/security/store/cacerts.pem"
        print("verify with: %s" % (cacerts_all))
        session.verify = cacerts_all
        # session.verify = False
        print("before get %s" % url_test)
        r = session.get(url_test)
        print("after get")
        print(r)
        print(r.text)
        # except Exception as err:
        #     print('err 2')
        #     print(err)
        try:
            print("------------------------------------------------------------------")
            session = requests.Session()
            session.cert = (cert_filename, key_filename)
            print("verify with: %s" % ("%s/store/AC-Certisign-RFB-G5.cer" % BASE_DIR))
            session.verify = "%s/store/AC-Certisign-RFB-G5.cer" % BASE_DIR
            # session.verify = False
            print("before get %s" % url_test)
            r = session.get(url_test)
            print("after get")
            print(r)
            print(r.text)
        except Exception as err:
            print("err 3")
            print(err)
        # try:
        #     print('------------------------------------------------------------------')
        #     session = requests.Session()
        #     session.cert = (cert_filename, key_filename)
        #     print('verify with: %s' % ('%s/store/AC-RFB-V4.cer' % BASE_DIR))
        #     session.verify = '%s/store/AC-RFB-V4.cer' % BASE_DIR
        #     r = session.get(url_test)
        #     print(r)
        # except Exception as err:
        #     print('err 4')
        #     print(err)
        #     logging.exception(err)

    # @unittest.skip('zeep_ssl_test')
    def zeep_ssl_test(self):
        # from requests import Session
        # from zeep import Client
        # from zeep.transports import Transport

        # url_test = 'https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc?singleWsdl'
        # BASE_DIR = "/app/root/esocial/security"
        # # PRIVATE_KEY = "%s/store/keypgjto.pem" % BASE_DIR
        # PRIVATE_KEY = "%s/store/keynopass.pem" % BASE_DIR
        # PASSWORD = b"1234"
        # CERTIFICATE_X509_FILE = "%s/store/pgjtoA1ecnpjx509pem.cer" % BASE_DIR

        # session = Session()
        # session.cert = (CERTIFICATE_X509_FILE, PRIVATE_KEY)
        # session.verify = '/app/root/esocial/security/store/cacerts.pem'
        # transport = Transport(session=session)
        # client = Client(
        #     url_test,
        #     transport=transport
        # )
        # print(client)
        client = ClientSendEventBatch()
        print(client)
        # client = ClientConsultEventBatch()
        # print(client)
