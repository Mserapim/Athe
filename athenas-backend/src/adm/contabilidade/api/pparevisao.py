# -*- coding: utf-8 -*-
from adm.contabilidade.models import PPARevisao
from contrib.newrest import Restful
from contrib.nil import nil_date, nil_pk, nil_unicode
from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class ContabPPARevisao(Restful):

    _model = PPARevisao

    def _filter_eval_value(self, value):
        if isinstance(value, str) and value.lower() in ("on", "true"):
            value = True
        elif isinstance(value, str) and value.lower() in ("off", "false"):
            value = False
        return value

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "data_vigencia" in params:
            if params.get("data_vigencia") != "":
                params.update(
                    data_vigencia=DateUtils.str_to_date(params.get("data_vigencia"))
                )
            else:
                params.update(data_vigencia=None)

        if "publicacao" in params:
            if params.get("publicacao") != "":
                field = getattr(self.Model, "publicacao")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(publicacao=query.get(pk=params.get("publicacao")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(publicacao=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            ano_revisao=int(instance.ano_revisao or 0),
            data_vigencia=nil_date(instance.data_vigencia, None),
            ano_inicio=int(instance.ano_inicio or 0),
            ano_fim=int(instance.ano_fim or 0),
            publicacao=nil_pk(instance.publicacao, None),
            ativo=instance.ativo,
            publicacao_unicode=nil_unicode(instance.publicacao, None),
        )

        return rst
