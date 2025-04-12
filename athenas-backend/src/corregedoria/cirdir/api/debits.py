# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Debits

log = getLogger(__name__)


class CIRDIRDebits(RestfulDRY):

    force_upper = False

    full_text_index = [
        "irscode__title__icontains",
        "description__icontains",
    ]

    _model = Debits

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.debits.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRDebits, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
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
            debits = self._model.objects.get(pk=int(params.get("value", 0)))
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=debits.rendered)
        self.renderer(rst)

    def confirm_information(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            instance = Debits.objects.get(pk=self.request.POST.get("pk"))
            instance.confirm_information()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="informação confirmada")
        self.renderer(rst)
