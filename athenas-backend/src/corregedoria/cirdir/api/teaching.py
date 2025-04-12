# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Teaching

log = getLogger(__name__)


class CIRDIRTeaching(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = Teaching

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.teaching.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRTeaching, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "discipline_unicode": instance.discipline.name,
                "institution_unicode": getattr(
                    instance.institution, "razao_social", None
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
            teaching = self._model.objects.get(pk=int(params.get("value", 0)))
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=teaching.rendered)
        self.renderer(rst)

    def confirm_information(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            instance = self._model.objects.get(pk=self.request.POST.get("pk"))
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
