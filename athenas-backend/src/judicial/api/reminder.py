# -*- coding: utf-8 -*-
import json
from django.db.models import Q
from django.db import transaction
from contrib.newrest import RestfulDRY
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, person_from_user
from judicial.models import (
    Reminder,
    LawsuitReminder,
    PartLawsuitReminder,
    RequestCollaboration,
)


log = getLogger(__name__)


class EJudReminder(RestfulDRY):

    _model = Reminder

    force_upper = False

    full_text_index = ("title__icontains",)

    def render(self, args=[]):
        rst = {"success": False, "message": "Nada foi implementado"}

        oid = args[0] if args else 0

        try:
            reminder = self.Model.objects.get(pk=oid)
            rst.update(
                success=True,
                message="Dados processados com sucesso",
                rendered=reminder.rendered,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update({"is_active": False if instance.deactivated_by else True})

        return _dict_

    def get_query(self):

        query = super().get_query()
        user = get_current_user()
        employee = employee_from_user(user)
        workplaces = [sl.lotacao for sl in employee.work_assignment_effective_exercise]

        collaborations = RequestCollaboration.objects.filter(
            Q(canceled_by=None)
            & Q(
                Q(requestcollaborationperson__person=employee.pessoa_fisica)
                | Q(
                    requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
                )
            )
        )

        if collaborations.exists():
            workplaces += [collab.origin_location.lotacao for collab in collaborations]

        query = query.filter(
            Q(created_by=user)
            | Q(access_level=self.Model.PUBLIC)
            | Q(workplace__in=workplaces)
        )

        return query

    def deactivate(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                log.debug(self.request.PUT.getlist("pkset"))
                for reminder in self.Model.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset"),
                    deactivated_by__isnull=True,
                ):
                    reminder.deactivate()
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Lembretes desativados com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))


class EJudLawsuitReminder(EJudReminder):
    _model = LawsuitReminder


class EJudPartLawsuitReminder(EJudReminder):
    _model = PartLawsuitReminder
