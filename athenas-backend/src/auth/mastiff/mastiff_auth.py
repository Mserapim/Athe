import requests
import json
import base64
from lxml import etree

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user

from django.conf import settings

log = getLogger(__name__)


class MastiffAuth(object):
    """
    Classe com métodos e lógicas básicas para realizar autenticação no Mastiff através do Crowd.
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

    def buscar_base_url(self):
        """
        Método para definir o base url para a requisição de autenticação.
        """

        if settings.ATHENAS_ENV == "production":
            base_url = "https://crowd.mpmt.mp.br"
        else:  # 'homolog' e 'dev'
            base_url = "https://dev-crowd.mpmt.mp.br"

        return f"{base_url}/crowd/rest/usermanagement/1/session"

    def buscar_payload(self):
        """
        Método para definir o payload da requisição de autenticação.
        """

        crowd_username = settings.CROWD_USERNAME
        crowd_password = settings.CROWD_PASSWORD

        return json.dumps({"username": crowd_username, "password": crowd_password})

    def buscar_headers(self):
        """
        Método para definir o headers da requisição de autenticação.
        """

        crowd_token = settings.CROWD_TOKEN

        return {
            "Authorization": f"Basic {crowd_token}",
            "Content-Type": "application/json",
        }

    def realizar_req(self):
        """
        Método para realizar a requisição
        """

        url = self.buscar_base_url()

        payload = self.buscar_payload()
        headers = self.buscar_headers()

        return requests.request("POST", url, headers=headers, data=payload)

    def buscar_xml_token(self, content):
        """
        Método para buscar o Token no conteúdo em XML da resposta da requisição
        """

        xmltree = etree.fromstring(content)

        return xmltree.find("token").text

    def transform_texto_para_base64(self, token):
        """
        Método para transformar (encode) um texto (token) para base64
        """

        b64 = base64.b64encode(bytes(f"crowd.token_key:{token}", "utf-8"))

        return b64.decode("utf-8")

    def autenticar(self):
        response = self.realizar_req()

        try:
            if response.status_code != 201:
                log.info(
                    f""">>> Status incorreto no retorno da requisição de autenticação do Mastiff pelo Crowd!
                    O status correto é 201. O status retornado foi: {response.status_code}"""
                )

                return None
            else:
                token = self.buscar_xml_token(response.content)
                token_base64 = self.transform_texto_para_base64(token)

                return token_base64
        except Exception as e:
            log.info(">>> Erro na autenticação do Mastiff pelo Crowd!")
            log.error(e)
