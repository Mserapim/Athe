# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_datetime
from raf.models import YearBase

log = getLogger(__name__)


class RAFYearBase(RestfulDRY):

    _model = YearBase

    full_text_index = ("title__icontains",)

    force_persist_boolean_fields = ["activated"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.yearbase.Launcher")')

    def model_to_dict(self, instance):
        rst = super(RAFYearBase, self).model_to_dict(instance)

        rst.update(
            {"icons": instance.icons, "valid_of": nil_datetime(instance.valid_of, None)}
        )

        return rst

    def enable(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            yearbase = self.get_query().get(pk=args[0])
            yearbase.activated = not yearbase.activated
            yearbase.save()

        except self.Model.DoesNotExist:
            rst.update(message="Ano Base não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True)

        return self.renderer(rst)
