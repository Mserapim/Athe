from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import getLogger, get_json_engine

from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais

log = getLogger(__name__)
json_engine = get_json_engine()


class ConfigPeriodoEnvioRelatorioTeleRestful(RestfulDRY):

    _model = ConfigPeriodoEnvioRelatoriosSemestrais

    full_text_index = ("titulo__icontains",)

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.teletrabalho.config_periodo_envio_analisado.Manage")'
        )
