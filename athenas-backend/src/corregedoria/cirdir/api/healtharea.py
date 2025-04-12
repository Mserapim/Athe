# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user, person_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from corregedoria.cirdir.models import ControlInformation
from rh.models import Servidor

log = getLogger(__name__)


class CIRDIRHealthArea(RestfulDRY):
    _model = ControlInformation
    force_upper = False
    full_text_index = [
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
        "year__icontains",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.health.healtharea.Manage")'
        )

    def get_query(self):
        atual_employee = employee = Servidor.objects.get(
            pk=employee_from_user(get_current_user()).pk
        )
        cfg = Configuration.get_or_create("corregedoria")
        type_member = (
            cfg.get("autoCreateForTypeMember").replace('"', "")[1:-1].split(",")
        )
        type_employee = (
            cfg.get("autoCreateForTypeEmployee").replace('"', "")[1:-1].split(",")
        )
        query = ControlInformation.objects.all()
        filter = ["None"]
        if get_current_user().has_perm("cirdir.can_management_health_area"):
            filter = filter + type_member + type_employee
        return query.filter(
            Q(employee__type_by_possession__in=filter) | Q(employee=atual_employee)
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRHealthArea, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "person_id": instance.employee.pessoa_fisica.pk,
                "employee_type": instance.employee.tipo,
                "previous_year": (
                    instance.previous_controlinformation.year
                    if instance.previous_controlinformation
                    else None
                ),
                "check_address": instance.check_access_criteria("address"),
                "check_teaching": instance.check_access_criteria("teaching"),
                "check_property": instance.check_access_criteria("property"),
                "check_debits": instance.check_access_criteria("debits"),
                "check_health": instance.check_access_criteria("health"),
            }
        )
        return _dict_

    def renderer_document_health_area(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            controlinformation = ControlInformation.objects.filter(
                pk=int(params.get("controlinformation", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                content=controlinformation.rendered_healtharea,
            )
        self.renderer(rst)
