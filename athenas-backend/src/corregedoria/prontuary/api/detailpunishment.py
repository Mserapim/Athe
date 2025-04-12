# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailPunishment
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailPunishment(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailPunishment

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.others.punishment.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailPunishment, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "punishment": "Cargo/Função: <b>%s</b><br />Período: <b>%s</b>(%s) - <b>%s</b>(%s)"
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
            detailpunishment = DetailPunishment.objects.filter(
                pk=int(params.get("detailpunishment", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detailpunishment.rendered)
        self.renderer(rst)
