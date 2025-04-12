# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailJointAction
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailJointAction(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailJointAction

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.designation.jointaction.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailJointAction, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "jointaction": "Cargo/Função: <b>%s</b><br />Período: <b>%s</b>(%s) - <b>%s</b>(%s)"
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
            detailjointaction = DetailJointAction.objects.filter(
                pk=int(params.get("detailjointaction", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detailjointaction.rendered)
        self.renderer(rst)
