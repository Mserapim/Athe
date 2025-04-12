# -*- coding: utf-8 -*-
from adm.contabilidade.models import PPAPrograma
from contrib.newrest import Restful
from contrib.nil import nil_pk, nil_unicode
from contrib.utils import getLogger

log = getLogger(__name__)


class ContabPPAPrograma(Restful):

    _model = PPAPrograma

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('adm.contabilidade.PPAManage')")

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "revisao" in params:
            if params.get("revisao") != "":
                field = getattr(self.Model, "revisao")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(revisao=query.get(pk=params.get("revisao")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(revisao=None)

        if "parent" in params:
            if params.get("parent") != "":
                field = getattr(self.Model, "parent")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(parent=query.get(pk=params.get("parent")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(parent=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            titulo=instance.titulo,
            codigo=instance.codigo,
            revisao=nil_pk(instance.revisao, None),
            revisao_unicode=nil_unicode(instance.revisao, None),
            parent=nil_pk(instance.parent, None),
            parent_unicode=nil_unicode(instance.parent, None),
        )

        return rst
