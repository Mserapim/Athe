# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import Minute, MinuteAction

log = getLogger(__name__)


class PHMMinuteAction(RestfulDRY):

    _model = MinuteAction

    full_text_index = (
        "user__username__icontains",
        "date__icontains",
        "observation__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteAction, self).model_to_dict(instance)

        _dict_.update({"actions_list": instance.actions_list()})

        return _dict_

    def get_actions_list(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            obj.update(actions_list=MinuteAction.actions_list())
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def finalize_minute_action(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            minutes = self.request.POST.get("minutes").split(",")
            observation = self.request.POST.get("observation")
        except Exception:
            obj.update(message="Selecione pelo menos uma ata para finalizar")
        else:
            for minute in minutes:
                minuteaction = MinuteAction()
                minuteaction.minute = Minute.objects.get(id=minute)
                minuteaction.action = 4
                minuteaction.observation = observation
                try:
                    minuteaction.save()
                except Exception as e:
                    obj.update(success=False, message=str(e))
                else:
                    obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
