# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk
from contrib.utils import getLogger
from rh.estagio.models import IntegrantesComissao

log = getLogger(__name__)


class GepIntegrantesComissao(Restful):

    _model = IntegrantesComissao

    full_text_index = (
        "servidor_id__pessoa_fisica__nome__icontains",
        "servidor_id__matricula__icontains",
    )

    def move_integrante(self, args=[]):
        rst = (
            self._move_up()
            if self.request.POST.get("direction") == "up"
            else self._move_down()
        )
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def _move_up(self):
        rst = {"success": False, "message": "Nada foi feito ainda."}
        query = IntegrantesComissao.objects.filter(pk=self.request.REQUEST.get("pk"))
        if query.exists() is True:
            try:
                q = IntegrantesComissao.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception as e:
                self.log.error(e)
                rst.update(message="Não consegui encontrar o participante.")
            else:
                q.reorder()
                for cs in query.order_by("ordem"):
                    cs.move_up()
                rst.update(success=True)
        else:
            rst.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return rst

    def _move_down(self):
        rst = {"success": False, "message": "Nada foi feito ainda."}
        query = IntegrantesComissao.objects.filter(pk=self.request.REQUEST.get("pk"))
        if query.exists():
            try:
                q = IntegrantesComissao.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception:
                rst.update(message="Não consegui encontrar o participante")
            else:
                q.reorder()
                for cs in query.order_by("-ordem"):
                    cs.move_down()
                rst.update(success=True)
        else:
            rst.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return rst

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        log.info(params)
        if "impedimento" in params:
            params.update(
                impedimento=False if int(params.get("impedimento")) == 1 else True
            )

        if "servidor_id" in params:
            if params.get("servidor_id") != "":
                field = getattr(self.Model, "servidor_id")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(servidor_id=query.get(pk=params.get("servidor_id")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(servidor_id=None)

        if "comissao_id" in params:
            if params.get("comissao_id") != "":
                field = getattr(self.Model, "comissao_id")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(comissao_id=query.get(pk=params.get("comissao_id")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(comissao_id=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            ordem=instance.ordem,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            impedimento=2 if instance.impedimento else 1,
            impedimento_display=instance.get_impedimento(),
            tipo_participante=instance.tipo_participante,
            tipo_participante_display=instance.get_display(),
            created_at=nil_datetime(instance.created_at, None),
            servidor_id=nil_pk(instance.servidor_id, None),
            servidor_id_unicode=str(instance.servidor_id) or None,
            modified_at=nil_datetime(instance.modified_at, None),
            comissao_id=nil_pk(instance.comissao_id, None),
            comissao_id_unicode=str(instance.comissao_id) or None,
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
