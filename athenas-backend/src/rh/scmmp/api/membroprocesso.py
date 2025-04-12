# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_display, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.scmmp.models import MembroProcesso, ProcessoJudicial

log = getLogger(__name__)


class ScmmpMembroProcesso(Restful):

    _model = MembroProcesso

    full_text_index = (
        "processo_judicial__numero_cnj__icontains",
        "membro__pessoa_fisica__nome__icontains",
    )

    def adicionar_membro(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            ProcessoJudicial.objects.get(pk=self.request.POST.get("pk_processo"))

        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "data_situacao" in params:
            if params.get("data_situacao") != "":
                params.update(
                    data_situacao=DateUtils.str_to_date(params.get("data_situacao"))
                )
            else:
                params.update(data_situacao=None)

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

        if "membro" in params:
            if params.get("membro") != "":
                field = getattr(self.Model, "membro")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(membro=query.get(pk=params.get("membro")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(membro=None)

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
            icons=instance.icons,
            data_situacao=nil_date(instance.data_situacao, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            situacao=instance.situacao,
            situacao_display=nil_display(instance, "situacao", None),
            membro=nil_pk(instance.membro, None),
            membro_unicode=str(instance.membro) or None,
            processo_judicial=nil_pk(instance.processo_judicial, None),
            processo_judicial_unicode=str(instance.processo_judicial) or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
