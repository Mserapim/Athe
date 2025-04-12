import requests
import json
import base64

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user

from django.conf import settings

from auth.mastiff.mastiff_auth import MastiffAuth

log = getLogger(__name__)


class MastiffGraphql(object):
    """
    Classe com métodos e lógicas para realizar requisições no Mastiff, por Graphql.
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

    def buscar_base_url(self):
        """
        Método para definir o base url para as requisições do Mastiff.
        """

        if settings.ATHENAS_ENV == "production":
            base_url = "https://portal.mpmt.mp.br"
        else:  # 'homolog' e 'dev'
            base_url = "https://teste.mpmt.mp.br"

        return f"{base_url}/mastiff/graphql"

    def buscar_payload(self, **kwargs):
        """
        Método para definir o payload da requisição.
        """

        if kwargs.get("nome_query") is None:
            return ""
        elif kwargs.get("nome_query") == "usuario_por_cpf":
            cpf = kwargs.get("cpf")

            query_str = '{"query":"query {\\r\\n  consultarUsuarioPorCpf(cpf: \\"valor_cpf\\"){\\r\\n    nome\\r\\n    login\\r\\n    email\\r\\n idUsuario\\r\\n }\\r\\n}","variables":{}}'.replace(
                "valor_cpf", cpf
            )

            return query_str

    def buscar_headers(self):
        """
        Método para definir o headers da requisição de autenticação.
        """

        token_base64 = MastiffAuth().autenticar()

        if token_base64 is None:
            return None
        else:
            return {"Authorization": token_base64, "Content-Type": "application/json"}

    def req_usuarios_por_cpf(self, cpf):
        """
        Método para realizar a requisição
        """

        url = self.buscar_base_url()

        payload = self.buscar_payload(nome_query="usuario_por_cpf", cpf=cpf)
        headers = self.buscar_headers()

        if headers is None:
            return None
        else:
            res = requests.request("POST", url, headers=headers, data=payload)

            return res.json()

    def buscar_infos_usuario_mastiff(self, cpf_mascarado):
        mastiff_res = self.req_usuarios_por_cpf(cpf_mascarado)

        if mastiff_res is None or "errors" in mastiff_res:
            msg = mastiff_res["errors"][0]["extensions"]["errorMessage"]
            log.info(
                f">>> Erro na busca do usuário de cpf {cpf_mascarado} no Mastiff. Msg: {msg}"
            )

            return None
        else:
            return {
                "username": mastiff_res["data"]["consultarUsuarioPorCpf"]["login"],
                "email": mastiff_res["data"]["consultarUsuarioPorCpf"]["email"],
                "id_usuario_mastiff": mastiff_res["data"]["consultarUsuarioPorCpf"][
                    "idUsuario"
                ],
            }
