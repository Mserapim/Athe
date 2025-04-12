import requests

from django.conf import settings

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user


log = getLogger(__name__)


class DAADistanciaItinerario(object):
    """
    Classe com métodos e lógicas básicos para realizar a busca de distância entre municípios utilizando a API do sistema do DAA.
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

    def buscar_base_url(self):
        """
        Método para definir o base url para requisição.
        """

        if settings.ATHENAS_ENV == "production":
            url = "https://gmt.mpmt.mp.br/api/v1"
        else:
            url = "https://gmt-homolog.mpmt.mp.br/api/v1"

        return url

    def buscar_headers(self):
        """
        Método para definir o header da requisição.
        """

        token = settings.TOKEN_API_DAA_TRANSP_DIST
        headers = {
            "User-Agent": "Python3",
            "Authorization": f"Bearer {token}",
        }

        return headers

    def realizar_req(self, *args, **kwargs):
        """
        Método para realizar a requisição
        """

        url = f"{self.buscar_base_url()}/{kwargs.get('url')}"
        headers = self.buscar_headers()
        metodo_req = kwargs.get("metodo_req", "GET")
        payload = kwargs.get("payload", {})

        response = requests.request(metodo_req, url, headers=headers, data=payload)

        return response

    def buscar_distancia_cidades(self, ibge_mun_origem, ibge_mun_destino):
        url = f"transportes/distancias?cidades={ibge_mun_origem},{ibge_mun_destino}"

        res = self.realizar_req(url=url)

        return res.json()


def buscar_gravar_distancia_destino(destino):
    from diarias.models import Destino

    try:
        if (
            destino.municipio_origem
            and destino.municipio_destino
            and destino.distancia_m is None
            and destino.distancia_km is None
            and destino.beneficiario.viagem.importada is False
        ):
            res = DAADistanciaItinerario().buscar_distancia_cidades(
                destino.municipio_origem.ibge, destino.municipio_destino.ibge
            )

            Destino.objects.filter(pk=destino.pk).update(
                distancia_m=res[0]["distancia"], distancia_km=res[0]["distancia_km"]
            )
    except Exception as e:
        import traceback

        error_message = traceback.format_exc()
        log.info(
            f"Erro ao tentar calcular a distância entre os municípios de origem e destino: {error_message}"
        )
