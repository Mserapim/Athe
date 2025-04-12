import requests

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user

log = getLogger(__name__)


class SincFormNomeacao(object):
    """
    Classe com métodos e lógicas básicos para realizar sincronização com API de formulários para nomeação.
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

        self.url = self.buscar_base_url()
        self.headers = self.buscar_headers()
        self.tipo_nomeacao = None

    def buscar_base_url(self):
        """
        Método para definir o base url para requisição.
        Deve ser sobreescrito para o contexto necessário.
        """

        # Alterar a url abaixo quando houver uma rota API com o contexto de Nomeação
        url = "https://dominio.api.com"

        return url

    def buscar_headers(self):
        """
        Método para definir o header da requisição.
        Deve ser sobreescrito com as definições de header necessários para o contexto.
        """

        headers = {}

        return headers

    def realizar_req(self, *args, **kwargs):
        """
        Método para realizar a requisição
        """

        url = kwargs.get("url", self.url)
        headers = kwargs.get("headers", self.headers)
        metodo_req = kwargs.get("metodo_req", "GET")
        payload = kwargs.get("payload", {})

        response = requests.request(metodo_req, url, headers=headers, data=payload)

        return response
