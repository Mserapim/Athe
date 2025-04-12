# -.- coding: utf-8 -.-
from requests import Session
from zeep import Client
from zeep.transports import Transport

from contrib.utils import getLogger
from esocial.security import CACERTS, CERTIFICATE_X509_FILE, PRIVATE_KEY

log = getLogger(__name__)


class ESocialClient(Client):

    def __init__(self, wsdl=None, **kwargs):
        """
        @param url: The URL for the WSDL.
        @type url: str
        @param kwargs: keyword arguments.
        @see: L{Options}
        """
        wsdl = wsdl if wsdl else None
        session = Session()
        session.cert = (CERTIFICATE_X509_FILE, PRIVATE_KEY)
        session.verify = CACERTS
        transport = Transport(session=session)
        kwargs.update({"transport": transport})
        super(ESocialClient, self).__init__(wsdl, **kwargs)


class ClientSendEventBatch(ESocialClient):

    def __init__(self):
        from esocial.models import Configuration

        configuration = Configuration.current_config()
        wsdl = None
        if configuration:
            wsdl = configuration.ws_batch_submission

        super(ClientSendEventBatch, self).__init__(wsdl=wsdl)

    # WSDL = 'https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc?singleWsdl'

    def service_send_event_batch(self, message):
        self.service.EnviarLoteEventos(message)


class ClientConsultEventBatch(ESocialClient):

    def __init__(self, **kwargs):
        from esocial.models import Configuration

        configuration = Configuration.current_config()
        wsdl = None
        if configuration:
            wsdl = configuration.ws_batch_consult_process

        super(ClientConsultEventBatch, self).__init__(wsdl=wsdl)

    # WSDL = 'https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/consultarloteeventos/WsConsultarLoteEventos.svc?singleWsdl'
