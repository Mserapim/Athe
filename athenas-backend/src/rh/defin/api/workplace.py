from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required

from rh.models import Lotacao

log = getLogger(__name__)


class DEFINWorkplaceRestful(RestfulDRY):

    _model = Lotacao

    full_text_index = (
        "nome__icontains",
        "sigla__icontains",
        "abreviacao__icontains",
        "cache_identifier__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.defin.workplace.Manage")')
