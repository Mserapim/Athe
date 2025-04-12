# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import AcaoContrato as AgreementAction
from planejamento.contrato.models import Contrato as Agreement

log = getLogger(__name__)


class PHAAgreementAction(RestfulDRY):

    _model = AgreementAction

    full_text_index = (
        "user__username__icontains",
        "data_acao__icontains",
        "observacao__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(PHAAgreementAction, self).model_to_dict(instance)

        _dict_.update({"actions_list": instance.actions_list()})

        return _dict_

    def get_actions_list(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            obj.update(actions_list=AgreementAction.actions_list())
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def finalize_agreement_action(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            agreements = self.request.POST.get("agreements").split(",")
            observation = self.request.POST.get("observation")
            action = self.request.POST.get("type")
        except Exception:
            obj.update(message="Selecione pelo menos um contrato para finalizar")
        else:
            for agreement in agreements:
                agreementaction = AgreementAction()
                agreementaction.contrato = Agreement.objects.get(id=agreement)
                agreementaction.tipo = int(action)
                agreementaction.observacao = observation
                try:
                    agreementaction.save()
                except Exception as e:
                    obj.update(success=False, message=str(e))
                else:
                    obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
