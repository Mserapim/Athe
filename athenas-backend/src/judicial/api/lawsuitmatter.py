# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import LawsuitMatter
from contrib.nil import nil_pk, nil_unicode

log = getLogger(__name__)


class EJudLawsuitMatter(Restful):

    _model = LawsuitMatter

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "principal" in params:
            params.update(principal=params.get("principal", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            matter_unicode=nil_unicode(instance.matter, None),
            matter=nil_pk(instance.matter, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            lawsuit=nil_pk(instance.lawsuit, None),
            principal=instance.principal,
        )

        return rst

    def define_principal(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            lm = self.get_query().get(pk=args[0])

            lm.define_principal()
            rst.update(message="Assunto definido como principal.", success=True)

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
