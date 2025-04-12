# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.estagio.models import ComissaoAvaliadora

log = getLogger(__name__)


class GepComissaoAvaliadora(Restful):

    _model = ComissaoAvaliadora

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.comissao.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "comissao_anterior" in params:
            if params.get("comissao_anterior") != "":
                field = getattr(self.Model, "comissao_anterior")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        comissao_anterior=query.get(pk=params.get("comissao_anterior"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(comissao_anterior=None)

        if "data_fim" in params:
            if params.get("data_fim") != "":
                params.update(data_fim=DateUtils.str_to_date(params.get("data_fim")))
            else:
                params.update(data_fim=None)

        if "modificado_em" in params:
            if params.get("modificado_em") != "":
                params.update(
                    modificado_em=DateUtils.str_to_datetime(params.get("modificado_em"))
                )
            else:
                params.update(modificado_em=None)

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

        if "criado_em" in params:
            if params.get("criado_em") != "":
                params.update(
                    criado_em=DateUtils.str_to_datetime(params.get("criado_em"))
                )
            else:
                params.update(criado_em=None)

        if "data_inicio" in params:
            if params.get("data_inicio") != "":
                params.update(
                    data_inicio=DateUtils.str_to_date(params.get("data_inicio"))
                )
            else:
                params.update(data_inicio=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            comissao_anterior=nil_pk(instance.comissao_anterior, None),
            comissao_anterior_unicode=str(instance.comissao_anterior) or None,
            data_fim=nil_date(instance.data_fim, None),
            modificado_em=nil_datetime(instance.modificado_em, None),
            publicacao=nil_pk(instance.publicacao, None),
            publicacao_unicode=str(instance.publicacao) or None,
            criado_em=nil_datetime(instance.criado_em, None),
            data_inicio=nil_date(instance.data_inicio, None),
        )

        return rst
