# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.utils import getLogger
from gfp.models import FolhaMensagem
from contrib.nil import nil_pk


log = getLogger(__name__)


class GFPFolhaMensagem(Restful):

    _model = FolhaMensagem

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "servidor" in params:
            if params.get("servidor") != "":
                field = getattr(self.Model, "servidor")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(servidor=query.get(pk=params.get("servidor")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(servidor=None)

        if "folha" in params:
            if params.get("folha") != "":
                field = getattr(self.Model, "folha")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(folha=query.get(pk=params.get("folha")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(folha=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            servidor=nil_pk(instance.servidor, None),
            servidor_unicode=str(instance.servidor) or None,
            texto=instance.texto,
            folha=nil_pk(instance.folha, None),
            folha_unicode=str(instance.folha) or None,
        )

        return rst
