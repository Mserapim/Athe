# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.pvf.models import PortalRequestUsufruct
from contrib.decorator import login_required
import json


log = getLogger(__name__)


class PortalRequestUsufructApi(RestfulDRY):

    _model = PortalRequestUsufruct

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalrequestusufruct.Manage")')

    def extract_params(self, params, signature=[]):
        params_new = {}
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                except:
                    params_new.update({key: params[key]})
        return params_new

    @login_required("JSON")
    def save_usufruct(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "usufructs_in": self.extract_params(
                    self.request.POST, ["usufructs_in"]
                ),
                "pk": self.request.POST.get("pk"),
                "observation": self.request.POST.get("observation"),
                "total_days": self.request.POST.get("total_days"),
                "type_usufruct": self.request.POST.get("type_usufruct"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
                "parcel_number": self.request.POST.get("parcel_number"),
            }
        )

        try:
            can = self.check_permission(
                self.request.user,
                "add",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para criar %s."
                    % self.Model._meta.object_name
                )
            else:
                PortalRequestUsufruct.create_request_usufruct(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
