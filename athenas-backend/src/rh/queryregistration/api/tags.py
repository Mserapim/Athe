# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.queryregistration.models import TagField
from contrib.decorator import login_required


log = getLogger(__name__)


class QRTags(RestfulDRY):

    _model = TagField

    full_text_index = (
        "pk__icontains",
        "name__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.queryregistration.tags.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            pk = self.request.POST.get("pk")
            if not pk:
                tag = self._model()
            else:
                tag = TagField.objects.get(pk=pk)
            tag.name = self.request.POST.get("name")
            tag.key_tag = self.request.POST.get("key_tag")
            tag.type_tag = self.request.POST.get("type_tag")
            tag.type_rest = self.request.POST.get("type_rest")
            tag.choice_id = self.request.POST.get("choice_id")
            tag.value = self.request.POST.get("value")
            tag.controller = self.request.POST.get("controller")
            tag.model = self.request.POST.get("model")
            tag.colums = (
                self.request.POST.get("colums")
                if self.request.POST.get("colums")
                else None
            )
            tag.length = (
                self.request.POST.get("length")
                if self.request.POST.get("length")
                else None
            )
            tag.many = True if self.request.POST.get("many") else False
            tag.sql_in = True if self.request.POST.get("sql_in") else False
            tag.save()

            rst.update(
                {
                    "success": True,
                    "message": "Registro Criado com Sucesso",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
