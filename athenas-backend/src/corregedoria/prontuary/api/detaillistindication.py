# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailListIndication
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailListIndication(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailListIndication

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.individualperformance.listindication.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailListIndication, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                # 'date_edital_formatted': instance.date_edital.strftime('%d/%m/%Y'),
            }
        )
        return _dict_

    def mark_detaillistindication(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            detaillistindication = DetailListIndication.objects.filter(
                pk=(
                    int(params.get("detaillistindication"))
                    if params.get("detaillistindication") != ""
                    else 0
                )
            ).first()
            if detaillistindication:
                detaillistindication.mark_detaillistindication()
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
            detaillistindication = DetailListIndication.objects.filter(
                pk=int(params.get("detaillistindication", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detaillistindication.rendered)
        self.renderer(rst)
