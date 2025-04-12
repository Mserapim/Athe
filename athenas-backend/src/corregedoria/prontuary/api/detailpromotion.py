# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailPromotion
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailPromotion(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailPromotion

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.movement.promotion.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailPromotion, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "exercise": "Cargo/Função: <b>%s</b><br />Período: <b>%s</b>(%s) - <b>%s</b>(%s)"
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
            detailpromotion = DetailPromotion.objects.filter(
                pk=int(params.get("detailpromotion", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detailpromotion.rendered)
        self.renderer(rst)
