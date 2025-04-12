# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailPerformanceParticularDifficulty
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailPerformanceParticularDifficulty(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailPerformanceParticularDifficulty

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(
            PRONTUARYDetailPerformanceParticularDifficulty, self
        ).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "total_days": instance.total_days,
                "employeelocation_description": instance.employeelocation_description,
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
            detailperformanceparticulardifficulty = (
                DetailPerformanceParticularDifficulty.objects.filter(
                    pk=int(params.get("detailperformanceparticulardifficulty", 0) or 0)
                ).first()
            )
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True, content=detailperformanceparticulardifficulty.rendered
            )
        self.renderer(rst)
