# -*- coding: utf-8 -*-

import json
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger

from ceaf.models import Capacitation, Participant
from rh.models import Servidor

log = getLogger(__name__)


class CEAFCapacitation(RestfulDRY):

    _model = Capacitation

    full_text_index = (
        "name__icontains",
        "description__icontains",
        "local__icontains",
        "period__icontains",
    )

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("ceaf.capacitation.Manage")')

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(reference_period=instance.reference_period)

        return rst


class CEAFParticipant(RestfulDRY):

    _model = Participant

    full_text_index = ("name__icontains", "employee__matricula__icontains")

    def get_query(self):
        query = super(CEAFParticipant, self).get_query()
        return query.distinct("name", "employee")

    def get_params(self, querydict=None, check_case=False):
        params = super().get_params(querydict, check_case)
        if "employee" in params and params.get("employee", None):
            params.update(name=params.get("employee").pessoa_fisica.nome)
        return params

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(
            category=(
                instance.employee.get_type_by_possession_display()
                if instance.employee
                else "CONVIDADO"
            ),
            matricula=instance.employee.matricula if instance.employee else "",
        )

        return rst

    def adicionar_membro(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_person_name(self, *args):
        obj = {"success": False}
        employee = Servidor.objects.filter(
            matricula=self.request.POST.get("matricula", None)
        )
        if employee.exists():
            obj.update(success=True)
            obj.update(name=employee.first().pessoa_fisica.nome)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
