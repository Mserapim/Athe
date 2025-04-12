# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from edocs.protocolo.models import Impressora
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EDOCImpressoraRestful(Restful):

    _model = Impressora

    def json(self, args=[]):
        self.response.write('Ext._create("edocs.protocolo.ImpressoraManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "lotacao" in params:
            if params.get("lotacao") != "":
                field = getattr(self.Model, "lotacao")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(lotacao=query.get(pk=params.get("lotacao")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lotacao=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            host=instance.host,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            lotacao=nil_pk(instance.lotacao, None),
            lotacao_unicode=nil_unicode(instance.lotacao, None),
            nome=instance.nome,
            driver=instance.driver,
            driver_display=nil_display(instance, "driver", None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            port=int(instance.port or 0),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
