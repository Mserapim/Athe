from datetime import datetime
from contrib.controller import DefaultController
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from django.db.models import Q
from rh.pvf.models import SendingTimeSheet
from contrib.decorator import login_required
import json
from rh.pvf.const import *

from rh.models import Employee, Servidor
from standard.models import Choice

log = getLogger(__name__)


class PVFSendPointSheet(RestfulDRY):
    _model = SendingTimeSheet

    full_text_index = ("title__icontains",)

    @login_required("JSON")
    def pending(self, args=[]):
        employee = Servidor.objects.get(pk=args[0])
        request = SendingTimeSheet.objects.get(pk=args[3])
        data_resume = ""
        lack = int(data_resume["FALTASPERIODO"])
        balance = int(data_resume["SALDOPERIODO"].split(":")[0])
        obj = {"count": 0, "collection": []}
        if lack > 0:
            obj["collection"].append({"type": "Faltas", "value": lack})
        elif balance < 0:
            obj["collection"].append(
                {"type": "Saldo do Período", "value": data_resume["SALDOPERIODO"]}
            )

        justifications = request.pvf_request_justification.filter(
            reason_type__in=Choice.objects.filter(
                name="TYPE_OF_REASON_PENDING"
            ).values_list("value", flat=True)
        )
        for justification in justifications:
            obj["collection"].append(
                {"type": "Justificativas", "value": justification.get_reason_type_str}
            )

        # obj = {
        #     'count': 0,
        #     'collection': [{'type':'teste','value':20}]
        # }

        obj.update(count=len(obj.get("collection")))
        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_reference(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            references = []
            qtd_reference = Choice.objects.get(
                app_label="pvf", name="RETROACTIVE_MONTHS"
            ).value
            data_year = datetime.today().year
            data_month = datetime.today().month
            count = 0
            while count < qtd_reference:
                if (
                    not SendingTimeSheet.objects.filter(
                        employee=employee_from_user(get_current_user()),
                        reference_month=data_month,
                        reference_year=data_year,
                    )
                    .exclude(
                        status__in=[
                            STS_REJECTED,
                            STS_CANCELED_DGP,
                            STS_CANCELED_APPLICANT,
                        ]
                    )
                    .exists()
                ):
                    references.append((data_month, data_year))
                data_year = data_year - 1 if data_month == 1 else data_year
                data_month = 12 if data_month == 1 else data_month - 1
                count = count + 1

            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(references),
                collection=[
                    {
                        "pk": reference[0],
                        "description": str(reference[0]) + "/" + str(reference[1]),
                    }
                    for reference in references
                ],
            )

        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required("JSON")
    def send(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            pk = self.request.POST.get("pk")
            instance = SendingTimeSheet.objects.get(pk=pk)
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
        return (
            SendingTimeSheet.objects.filter(
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
            .exists()
        )

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
                    reference = self.request.POST.get("reference", None)
                    instance = self.Model.create(reference)
                    rst.update(
                        {
                            "success": True,
                            "message": "Registro Criado com Sucesso",
                            "pk": instance.pk,
                            "month": instance.reference_month,
                            "year": instance.reference_year,
                            "daily_workload": instance.daily_workload,
                            "last_working_day_month": instance.get_last_working_day_month,
                        }
                    )
                else:
                    raise Exception(
                        "Já existe uma solicitação de folha ponto em andamento."
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
        self.response.write('Ext._create("rh.pvf.sendpointsheet.Manage")')


class RegisterPoint(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.sendpointsheet.RegisterPoint")')
