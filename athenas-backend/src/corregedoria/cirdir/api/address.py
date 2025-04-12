# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Address

log = getLogger(__name__)


class CIRDIRAddress(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = Address

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.address.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRAddress, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "ref_address_unicode": str(instance.ref_address),
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
            address = self._model.objects.get(pk=int(params.get("value", 0)))
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=address.rendered)
        self.renderer(rst)

    def confirm_information(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            address = self._model.objects.get(pk=self.request.POST.get("pk"))
            address.confirm_information()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="informação confirmada")
        self.renderer(rst)
