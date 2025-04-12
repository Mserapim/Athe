# -*- coding: utf-8 -*-
import json

from contrib.nil import nil_display, nil_pk, nil_unicode, nil_datetime
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger

from corregedoria.cnmp.models import Communication

log = getLogger(__name__)


class CNMPCommunication(RestfulDRY):

    _model = Communication

    full_text_index = ["employee__pessoa_fisica__nome__icontains"]

    def model_to_dict(self, instance):
        _dict_ = super(CNMPCommunication, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "employee_unicode": nil_unicode(instance.employee, ""),
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
            communication = self._model.objects.get(pk=int(params.get("pk", 0) or 0))

        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=communication.rendered())

        self.renderer(rst)

    def bulk_generate(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            logs = self._model.bulk_generate()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Comando processado", content=logs)

        self.renderer(rst)

    def send_information(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}
        try:
            params = self.request.POST
            communication = self._model.objects.get(pk=int(params.get("pk", 0) or 0))
            communication.send()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Envio realizado com sucesso.")

        self.renderer(rst)
