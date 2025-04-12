from contrib.newrest import RestfulDRY
from web.models import WebGroup


class WebGroupIntranet(RestfulDRY):
    _model = WebGroup

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('web.intranet.webgroup.Manage')")

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        # rst = {
        #     **rst,
        #     'departament_display': instance.departament_display
        # }

        return rst
