from datetime import datetime

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from django.db.models import Q
from rh.pvf.models import SendingTelework
from contrib.decorator import login_required
import json
from rh.pvf.const import *

log = getLogger(__name__)


class PVFSendTeleWork(RestfulDRY):
    _model = SendingTelework

    full_text_index = ("title__icontains",)

    QTD_WORK_PLAN = 1

    @login_required("JSON")
    def send(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            pk = self.request.POST.get("pk")
            instance = SendingTelework.objects.get(pk=pk)
            instance.send()
            rst.update(
                {
                    "success": True,
                    "message": "Registro enviado com sucesso",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_request_progress(self):
        # raise Exception(self.count_workplan())
        count_progress = (
            SendingTelework.objects.filter(
                employee=employee_from_user(get_current_user()),
            )
            .exclude(
                status__in=[
                    STS_REJECTED,
                    STS_EFFECTIVE,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )
            .count()
        )

        count_work_plan = self.Model().get_count_workplan
        if count_work_plan == 0:  # trocar a quantiade para 1
            count_work_plan = self.QTD_WORK_PLAN
        if count_progress >= count_work_plan:
            return True
        return False

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

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
                if not self.get_request_progress():
                    instance = self.Model.create()
                    rst.update(
                        {
                            "success": True,
                            "message": "Registro Criado com Sucesso",
                            "pk": instance.pk,
                            "month": instance.reference_month,
                            "year": instance.reference_year,
                            "current_work_plan_start_date": instance.work_plan.data_inicio.strftime(
                                "%d/%m/%Y"
                            ),
                            "current_work_plan_end_date": (
                                instance.work_plan.data_fim.strftime("%d/%m/%Y")
                                if instance.work_plan.data_fim
                                else "-"
                            ),
                            "plan_work_id": instance.work_plan.id,
                            "plan_work_presential": (
                                instance.work_plan.presencial
                                if instance.work_plan.presencial
                                else 0
                            ),
                            "count_work_plan": instance.get_count_workplan,
                            "get_count_send": instance.get_count_send,
                        }
                    )
                else:
                    raise Exception(
                        "Já existe uma solicitação teletrabalho em andamento."
                    )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.sendtelework.Manage")')
