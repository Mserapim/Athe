from contrib.newrest import RestfulDRY
from web.models import MetaValue


class MetaDado(RestfulDRY):
    _model = MetaValue

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        # rst = {
        #     **rst,
        #     'departament_display': instance.departament_display
        # }

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("web.intranet.metadado.Manage")')
