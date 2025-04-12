# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from planejamento.contrato.models import (
    SupervisorClassification,
    AgreementSupervisor,
    MinuteSupervisor,
)
from contrib.utils import getLogger, DateUtils
import json

log = getLogger(__name__)


class PHSupervisorClassification(RestfulDRY):
    _model = SupervisorClassification

    force_persist_boolean_fields = ["active"]


class PHSupervisor(RestfulDRY):

    _model = None

    full_text_index = ("employee__pessoa_fisica__nome__icontains",)

    # force_persist_clear_m2m = []

    def close_supervisor(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            s = self.__class__._model.objects.get(pk=self.request.POST.get("pk"))
            s._end = DateUtils.str_to_date(self.request.POST.get("end_date"))
            s.observation = self.request.POST.get("observation")
            s._close_supervisor = True
            s.save()
        except self.__class__._model.DoesNotExist as dne:
            obj.update(message=str(dne))
            log.exception(dne)
        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def check_close_action(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            s = self.__class__._model.objects.get(pk=self.request.POST.get("pk"))
            s._validate_close_supervisor()
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Validação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class PHAAgreementSupervisor(PHSupervisor):

    _model = AgreementSupervisor


class PHMMinuteSupervisor(PHSupervisor):

    _model = MinuteSupervisor
