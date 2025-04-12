from contrib.utils import getLogger
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from rh.afastamento.models import CIDCode, CID
from contrib.utils import DateUtils, get_json_engine

json = get_json_engine()
log = getLogger(__name__)


class CIDRestful(RestfulDRY):

    _model = CID

    full_text_index = ("description__icontains", "code", "cid_code__code__icontains")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.cid.Manage")')

    def get_query(self):
        return self.Model.objects.filter().order_by("id")

    def model_to_dict(self, instance):
        _dict = super().model_to_dict(instance)
        all_cid_codes = ""
        if instance.cid_code:
            for name in instance.cid_code.all():
                all_cid_codes += str(name) + " | "
        _dict.update(cid_code=all_cid_codes)

        return _dict


class CIDCodeRestful(RestfulDRY):

    _model = CIDCode

    full_text_index = ("code__icontains",)

    def get_query(self):
        return self.Model.objects.filter().order_by("id")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.cid.code.Manage")')
