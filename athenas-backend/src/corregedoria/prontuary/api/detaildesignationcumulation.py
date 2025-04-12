# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailDesignationCumulation
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailDesignationCumulation(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailDesignationCumulation

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.designation.designationcumulation.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailDesignationCumulation, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "icons": instance.icons,
                "designationcumulation": "Cargo/Função: <b>%s</b><br />Período: <b>%s</b>(%s) - <b>%s</b>(%s)"
                % (
                    instance.role,
                    (
                        instance.date_initial.strftime("%d/%m/%Y")
                        if instance.date_initial
                        else ""
                    ),
                    instance.act_initial,
                    (
                        instance.date_final.strftime("%d/%m/%Y")
                        if instance.date_final
                        else ""
                    ),
                    instance.act_final,
                ),
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
            detaildesignationcumulation = DetailDesignationCumulation.objects.filter(
                pk=int(params.get("detaildesignationcumulation", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detaildesignationcumulation.rendered)
        self.renderer(rst)
