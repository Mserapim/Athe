# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from raf.models import TrustRelationship, ActivityAdjustment, FunctionalActivityReport
from rh.models import Servidor
from django.db.models import Q, Min
from contrib.nil import nil_datetime


log = getLogger(__name__)


class CIRDIREmployee(RestfulDRY):

    _model = Servidor

    full_text_index = [
        "matricula__icontains",
        "pessoa_fisica__nome__icontains",
    ]

    def model_to_dict(self, instance):
        rst = super(CIRDIREmployee, self).model_to_dict(instance)
        rst.update({})
        return rst

    def get_query(self):
        cfg = Configuration.get_or_create("corregedoria")
        type_member = (
            cfg.get("autoCreateForTypeMember").replace('"', "")[1:-1].split(",")
        )
        type_employee = (
            cfg.get("autoCreateForTypeEmployee").replace('"', "")[1:-1].split(",")
        )
        query = Servidor.objects.all()
        filter = ["None"]
        if get_current_user().has_perm("cirdir.can_management_member"):
            filter = filter + type_member
        if get_current_user().has_perm("cirdir.can_management_employee"):
            filter = filter + type_employee
        if get_current_user().has_perm("cirdir.can_management_health_area"):
            filter = filter + type_employee

        return query.filter(Q(type_by_possession__in=filter))

    def employee_initial(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
        }
        try:
            params = self.request.POST
            health_area = True if params.get("health_area") == "true" else False
            employee = Servidor.objects.get(
                pk=employee_from_user(get_current_user()).pk
            )
            admin = False
            if health_area is True:
                if get_current_user().has_perm("cirdir.can_management_health_area"):
                    admin = True
            else:
                if get_current_user().has_perm(
                    "cirdir.can_management_member"
                ) or get_current_user().has_perm("cirdir.can_management_employee"):
                    admin = True
        except self.Model.DoesNotExist:
            rst.update(message="Pessoa não encontrada.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="dados carregados com sucesso",
                data={
                    "pk": employee.pk,
                    "pessoa_fisica_unicode": employee.pessoa_fisica.nome,
                    "admin": admin,
                },
            )
        self.renderer(rst)
