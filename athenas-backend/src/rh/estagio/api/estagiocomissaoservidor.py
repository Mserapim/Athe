# -*- coding: utf-8 -*-

from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.estagio.models import (
    ApreciacaoComissao,
    EstagioComissaoServidor,
    IntegrantesComissao,
)

log = getLogger(__name__)


class GepEstagioComissaoServidor(Restful):

    _model = EstagioComissaoServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.comissaoavaliacao.Manage")')

    def decisao_comissao(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            with transaction.atomic():
                avaliador = self.request.user.servidor
                estagio_comissao = EstagioComissaoServidor.objects.get(
                    pk=self.request.POST.get("pk")
                )
                ec = estagio_comissao.integrante_comissao_avaliadora.values(
                    "comissao_id_id"
                )[0].get("comissao_id_id")
                integrante_comissao = IntegrantesComissao.objects.get(
                    servidor_id=avaliador, comissao_id=ec
                )

                apreciacao_comissao = ApreciacaoComissao(
                    comissao_servidor=estagio_comissao,
                    integrante_avaliador=integrante_comissao,
                    decisao=int(self.request.POST.get("decisao")),
                )
                apreciacao_comissao.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados salvos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "modified_at" in params:
            if params.get("modified_at") != "":
                params.update(
                    modified_at=DateUtils.str_to_datetime(params.get("modified_at"))
                )
            else:
                params.update(modified_at=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

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

        if "estagio_prob_servidor" in params:
            if params.get("estagio_prob_servidor") != "":
                field = getattr(self.Model, "estagio_prob_servidor")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        estagio_prob_servidor=query.get(
                            pk=params.get("estagio_prob_servidor")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(estagio_prob_servidor=None)

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

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("estagio.estagio_comissao"):
            user = self.request.user.servidor
            query = query.filter(
                integrante_comissao_avaliadora__servidor_id=user.pk,
                decisao_chefe_orgao__isnull=True,
            )
        else:
            query = query.exclude(id__gt=0)

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            status=instance.get_status(),
            estagio_prob_servidor=nil_pk(instance.estagio_prob_servidor, None),
            estagio_prob_servidor_unicode=str(
                instance.estagio_prob_servidor.posse_servidor
            )
            or None,
            servidor_id=instance.estagio_prob_servidor.posse_servidor.servidor.pk,
            questionario=str(instance.estagio_prob_servidor.configuracao.questionario)
            or None,
            questionario_id=nil_pk(
                instance.estagio_prob_servidor.configuracao.questionario, None
            ),
            questionario_manifestacao_id=nil_pk(
                instance.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor,
                None,
            ),
            questionario_manifestacao=str(
                instance.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor
            )
            or None,
            etapa_atual=instance.estagio_prob_servidor.current_stage,
            cargo_id=nil_pk(
                instance.estagio_prob_servidor.posse_servidor.quadro.cargo, None
            ),
            posse_servidor=nil_pk(instance.estagio_prob_servidor.posse_servidor, None),
            posse_servidor_unicode=str(instance.estagio_prob_servidor.posse_servidor)
            or None,
            data_exercicio=nil_date(
                instance.estagio_prob_servidor._inicio_estagio, None
            ),
            ultima_avaliacao=nil_date(
                instance.estagio_prob_servidor.ultima_avaliacao, None
            ),
            media=float(instance.estagio_prob_servidor.media or 0),
        )

        return rst
