# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from corregedoria.cirdir.models import InformationEvaluation

log = getLogger(__name__)


class BaseView(Restful):

    def json(self, args=[]):
        self.response["content-type"] = self.content_type
        self.response.write(self.view_rendered)

    @property
    def content_type(self):
        return "text/javascript"

    @property
    def view_rendered(self):
        return ""

    def _renderer_document(self, pk):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            instance = self._model.objects.get(pk=pk)
            rst.update(success=True, content=instance.rendered)
        except AttributeError as e:
            rst.update(message=str(e))
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def renderer_document(self, args=[]):
        return self._renderer_document(args[0])


class CIRDIRInformationEvaluation(BaseView):

    _model = InformationEvaluation

    @property
    def view_rendered(self):
        return 'Ext._create("corregedoria.cirdir.AuditManage")'

    def to_accept(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }

        try:
            obj = self._model.objects.get(pk=self.request.POST.get("pk"))

            value = {"true": True, "false": False}.get(
                self.request.POST.get("accept", None), None
            )

            if value is None:
                raise Exception("Ocorreu um erro ao realizar a ação.")

            obj.to_accept(value)

            rst.update(success=True, message="Ação realizada")

        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
