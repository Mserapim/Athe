# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user, person_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from corregedoria.cirdir.models import Health
from rh.models import Servidor

log = getLogger(__name__)


class CIRDIRHealthAreaEvaluation(RestfulDRY):
    force_upper = False

    full_text_index = [
        "title__icontains",
    ]

    _model = Health

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.health.healtharea.attendance.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRHealthAreaEvaluation, self).model_to_dict(instance)
        _dict_.update(
            {
                "unicode": str(instance),
                "authorization_health": instance.controlinformation.authorization_health,
                "evaluate_unicode": instance.created_at.strftime("%Y%m%d%H%M%S%s"),
            }
        )
        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            health = Health.objects.filter(pk=int(params.get("health", 0) or 0)).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                content=health.rendered_evaluation,
                evaluation=health.evaluation,
            )
        self.renderer(rst)
