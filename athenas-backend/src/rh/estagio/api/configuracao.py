# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.estagio.models import Configuracao

log = getLogger(__name__)


class GepConfiguracao(Restful):

    _model = Configuracao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.configuracao.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "questionario" in params:
            if params.get("questionario") != "":
                field = getattr(self.Model, "questionario")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(questionario=query.get(pk=params.get("questionario")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(questionario=None)

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

        if "questionario_manifestacao_servidor" in params:
            if params.get("questionario_manifestacao_servidor") != "":
                field = getattr(self.Model, "questionario_manifestacao_servidor")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        questionario_manifestacao_servidor=query.get(
                            pk=params.get("questionario_manifestacao_servidor")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(questionario_manifestacao_servidor=None)

        if "data_inicio" in params:
            if params.get("data_inicio") != "":
                params.update(
                    data_inicio=DateUtils.str_to_date(params.get("data_inicio"))
                )
            else:
                params.update(data_inicio=None)

        if "configuracao_anterior" in params:
            if params.get("configuracao_anterior") != "":
                field = getattr(self.Model, "configuracao_anterior")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        configuracao_anterior=query.get(
                            pk=params.get("configuracao_anterior")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(configuracao_anterior=None)

        if "criado_em" in params:
            if params.get("criado_em") != "":
                params.update(
                    criado_em=DateUtils.str_to_datetime(params.get("criado_em"))
                )
            else:
                params.update(criado_em=None)

        if "data_fim" in params:
            if params.get("data_fim") != "":
                params.update(data_fim=DateUtils.str_to_date(params.get("data_fim")))
            else:
                params.update(data_fim=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            questionario=nil_pk(instance.questionario, None),
            questionario_unicode=str(instance.questionario) or None,
            porc_aprovacao=float(instance.porc_aprovacao or 0),
            modificado_em=nil_datetime(instance.modificado_em, None),
            qtde_avaliacoes=int(instance.qtde_avaliacoes or 0),
            publicacao=nil_pk(instance.publicacao, None),
            publicacao_unicode=str(instance.publicacao) or None,
            qtde_meses_entre_avaliacao=int(instance.qtde_meses_entre_avaliacao or 0),
            questionario_manifestacao_servidor=nil_pk(
                instance.questionario_manifestacao_servidor, None
            ),
            questionario_manifestacao_servidor_unicode=str(
                instance.questionario_manifestacao_servidor
            )
            or None,
            data_inicio=nil_date(instance.data_inicio, None),
            configuracao_anterior=nil_pk(instance.configuracao_anterior, None),
            configuracao_anterior_unicode=str(instance.configuracao_anterior) or None,
            criado_em=nil_datetime(instance.criado_em, None),
            data_fim=nil_date(instance.data_fim, None),
        )

        return rst
