# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import DetailInstitutionalParticipation
import raf.api.util

log = getLogger(__name__)


class PRONTUARYDetailInstitutionalParticipation(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = DetailInstitutionalParticipation

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.individualperformance.listindication.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYDetailInstitutionalParticipation, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                # 'icons': instance.icons,
                # 'date_edital_formatted': instance.date_edital.strftime('%d/%m/%Y'),
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
            detailinstitutionalparticipation = (
                DetailInstitutionalParticipation.objects.filter(
                    pk=int(params.get("detailinstitutionalparticipation", 0) or 0)
                ).first()
            )
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=detailinstitutionalparticipation.rendered)
        self.renderer(rst)
