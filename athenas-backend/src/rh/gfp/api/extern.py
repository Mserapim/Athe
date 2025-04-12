from contrib.controller import DefaultController
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from contrib.decorator import login_required
import requests


log = getLogger(__name__)


class GFPNeoConsig(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        url = None
        try:
            employee = employee_from_user(get_current_user())
            data = {
                "cpf": int(employee.pessoa_fisica.cpf),
                "matricula": "%s" % employee.matricula,
            }
            request = requests.post(
                "https://www.clubeusemais.com.br/integracao-meu-consignado-to/autenticar-usuario",
                params=data,
                headers={
                    "Authorization": "Bearer da39a3ee5e6b4b0d3255bfef95601890afd80709"
                },
            ).json()
            url = request["url"]
        except Exception as e:
            log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.extern.NeoConsig", {url: "%s"})' % url)


class GFPConsigFacil(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        url = "https://www.faciltecnologia.com.br/consigfacil/mpto/index_servidor.php"

        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.extern.ConsigFacil", {url: "%s"})' % url
        )
