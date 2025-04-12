# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.scmmp.models import FaseRecursal

log = getLogger(__name__)


class ScmmpFaseRecursal(Restful):

    _model = FaseRecursal

    force_upper = False

    full_text_index = (
        "numero_local__icontains",
        "orgao_julgador__icontains",
        "nome_acao__icontains",
    )

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

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
            nome_acao=instance.nome_acao,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            url=instance.url,
            processo_judicial=nil_pk(instance.processo_judicial, None),
            processo_judicial_unicode=str(instance.processo_judicial) or None,
            created_at=nil_datetime(instance.created_at, None),
            orgao_julgador=instance.orgao_julgador,
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            numero_local=instance.numero_local,
        )

        return rst
