# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from edocs.protocolo.models import Referencia
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EDOCReferenciaRestful(Restful):

    _model = Referencia

    force_upper = False

    full_text_index = ("protocolo__codigo__icontains",)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("edocs.protocolo.ReferenciaManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "protocolo" in params:
            if params.get("protocolo") != "":
                field = getattr(self.Model, "protocolo")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(protocolo=query.get(pk=params.get("protocolo")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(protocolo=None)

        if "modified_by" in params:
            if params.get("modified_by") != "":
                field = getattr(self.Model, "modified_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(modified_by=query.get(pk=params.get("modified_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(modified_by=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

        if "movimentacao" in params:
            if params.get("movimentacao") != "":
                field = getattr(self.Model, "movimentacao")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(movimentacao=query.get(pk=params.get("movimentacao")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(movimentacao=None)

        if "modified_at" in params:
            if params.get("modified_at") != "":
                params.update(
                    modified_at=DateUtils.str_to_datetime(params.get("modified_at"))
                )
            else:
                params.update(modified_at=None)

        if "created_by" in params:
            if params.get("created_by") != "":
                field = getattr(self.Model, "created_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(created_by=query.get(pk=params.get("created_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(created_by=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            observation=instance.observation,
            protocolo=nil_pk(instance.protocolo, None),
            protocolo_unicode=nil_unicode(instance.protocolo, None),
            protocolo_codigo=instance.protocolo.codigo if instance.protocolo else None,
            protocolo_assunto=(
                instance.protocolo.assunto if instance.protocolo else None
            ),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            created_at=nil_datetime(instance.created_at, None),
            movimentacao=nil_pk(instance.movimentacao, None),
            movimentacao_unicode=nil_unicode(instance.movimentacao, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
