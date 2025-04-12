# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.pvf.models import PortalRequestWorkload
from contrib.decorator import login_required


log = getLogger(__name__)


class PortalRequestWorkloadApi(RestfulDRY):

    _model = PortalRequestWorkload

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalrequestworkload.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "pk": self.request.POST.get("pk"),
                "start_date": self.request.POST.get("date_work_load"),
                "to_workload": self.request.POST.get("new_workload"),
                "observation": self.request.POST.get("observation"),
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
                PortalRequestWorkload.create_change_workload(params)
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
