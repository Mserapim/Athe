# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Evaluator, Health

log = getLogger(__name__)


class CIRDIREvaluatorRestful(RestfulDRY):

    force_upper = True

    full_text_index = [
        "name__icontains",
    ]

    _model = Evaluator

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.evaluator.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIREvaluatorRestful, self).model_to_dict(instance)
        _dict_.update({"icons": instance.icons})
        return _dict_

    def delivery(self, args=[]):

        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            evaluators = list(map(str, self.request.POST.getlist("evaluators", [])))
            healths = list(map(str, self.request.POST.getlist("healths", [])))

            Health.delivery_health_to_evaluators(healths=healths, evaluators=evaluators)

            rst.update(success=True, message="Distribuição concluida.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
