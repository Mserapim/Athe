# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import InspectionLink
import raf.api.util

log = getLogger(__name__)


class PRONTUARYInspectionLink(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = InspectionLink

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.functionalperformance.inspection.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYInspectionLink, self).model_to_dict(instance)
        _dict_.update(
            {
                "inspection_execution_organ": instance.inspection.execution_organ.nome,
                "inspection_date_initial": instance.inspection.inspection_date_initial_formatted,
                "inspection_date_final": instance.inspection.inspection_date_final_formatted,
            }
        )
        return _dict_

    def mark_inspection(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            inspectionlink = InspectionLink.objects.filter(
                pk=(
                    int(params.get("inspectionlink"))
                    if params.get("inspectionlink") != ""
                    else 0
                )
            ).first()
            if inspectionlink:
                inspectionlink.mark_inspection()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção/Correição marcada com sucesso.",
            )
        return self.renderer(rst)

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            inspectionLink = InspectionLink.objects.filter(
                pk=int(params.get("inspectionLink", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=inspectionLink.rendered)
        self.renderer(rst)
