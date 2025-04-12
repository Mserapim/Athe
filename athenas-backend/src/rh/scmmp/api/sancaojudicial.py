# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_display, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.scmmp.models import SancaoJudicial

log = getLogger(__name__)


class ScmmpSancaoJudicial(Restful):

    _model = SancaoJudicial

    force_upper = False

    full_text_index = (
        "processo_judicial__numero_cnj__icontains",
        "membro_processo__membro__pessoa_fisica__nome__icontains",
    )

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        log.info(params)

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

        if "processo_judicial" in params:
            if params.get("processo_judicial") != "":
                field = getattr(self.Model, "processo_judicial")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        processo_judicial=query.get(pk=params.get("processo_judicial"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(processo_judicial=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

        if "data_imposicao" in params:
            if params.get("data_imposicao") != "":
                params.update(
                    data_imposicao=DateUtils.str_to_date(params.get("data_imposicao"))
                )
            else:
                params.update(data_imposicao=None)

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

        if "data_cumprimento" in params:
            if params.get("data_cumprimento") != "":
                params.update(
                    data_cumprimento=DateUtils.str_to_date(
                        params.get("data_cumprimento")
                    )
                )
            else:
                params.update(data_cumprimento=None)

        if "membro_processo" in params:
            if params.get("membro_processo") != "":
                field = getattr(self.Model, "membro_processo")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        membro_processo=query.get(pk=params.get("membro_processo"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(membro_processo=None)

        if "data_reabilitacao" in params:
            if params.get("data_reabilitacao") != "":
                params.update(
                    data_reabilitacao=DateUtils.str_to_date(
                        params.get("data_reabilitacao")
                    )
                )
            else:
                params.update(data_reabilitacao=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            cumprimento=instance.cumprimento,
            cumprimento_display=nil_display(instance, "cumprimento", None),
            ext_punibilidade=instance.ext_punibilidade,
            ext_punibilidade_display=nil_display(instance, "ext_punibilidade", None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            processo_judicial=nil_pk(instance.processo_judicial, None),
            processo_judicial_unicode=str(instance.processo_judicial) or None,
            created_at=nil_datetime(instance.created_at, None),
            data_imposicao=nil_date(instance.data_imposicao, None),
            modified_at=nil_datetime(instance.modified_at, None),
            resumo=instance.resumo,
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            data_cumprimento=nil_date(instance.data_cumprimento, None),
            membro_processo=nil_pk(instance.membro_processo, None),
            membro_processo_unicode=str(instance.membro_processo) or None,
            reabilitacao=instance.reabilitacao,
            reabilitacao_display=nil_display(instance, "reabilitacao", None),
            data_reabilitacao=nil_date(instance.data_reabilitacao, None),
        )

        return rst
