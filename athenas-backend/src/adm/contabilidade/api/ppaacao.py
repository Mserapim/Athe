# -*- coding: utf-8 -*-
from adm.contabilidade.models import PPAAcao
from contrib.newrest import Restful
from contrib.nil import nil_pk, nil_unicode
from contrib.utils import getLogger

log = getLogger(__name__)


class ContabPPAAcao(Restful):

    _model = PPAAcao

    full_text_index = (
        "cache_codigo__icontains",
        "codigo__icontains",
        "titulo__icontains",
        "programa__codigo__icontains",
        "programa__revisao__ano_revisao__icontains",
    )

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "fonte_exclusiva" in params:
            if params.get("fonte_exclusiva") != "":
                field = getattr(self.Model, "fonte_exclusiva")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        fonte_exclusiva=query.get(pk=params.get("fonte_exclusiva"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(fonte_exclusiva=None)

        if "programa" in params:
            if params.get("programa") != "":
                field = getattr(self.Model, "programa")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(programa=query.get(pk=params.get("programa")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(programa=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            id=nil_pk(instance, None),
            unicode=nil_unicode(instance, None),
            cache_codigo=instance.cache_codigo,
            titulo=instance.titulo,
            funcao=instance.funcao,
            subfuncao=instance.subfuncao,
            programa=nil_pk(instance.programa, None),
            programa_titulo=instance.programa.titulo if instance.programa else "",
            programa_unicode=nil_unicode(instance.programa, None),
            codigo=instance.codigo,
            fonte_exclusiva=nil_pk(instance.fonte_exclusiva, None),
            fonte_exclusiva_unicode=nil_unicode(instance.fonte_exclusiva, None),
            revision_year=instance.revision_year,
        )

        return rst
