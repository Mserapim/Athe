# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from rh.pvf.models import PortalCancelSchedule
from contrib.utils import getLogger
from contrib.decorator import login_required

log = getLogger(__name__)


class PVFCancelSchedule(RestfulDRY):

    _model = PortalCancelSchedule

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalcancelschedule.Manage")')

    @login_required("JSON")
    def request_cancel(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "usufruct_id": self.request.POST.get("usufruct_id"),
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
                PortalCancelSchedule.create_cancel_schedule(params)
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
