# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk
from contrib.utils import getLogger
from rh.apd.models import MemberCommission

log = getLogger(__name__)


class ApdMemberCommission(Restful):
    """Classe representativa do modelo MemberCommission."""

    _model = MemberCommission

    def move_integrante(self, args=[]):
        """MOVIMENTA UM INTEGRANTE NA ORDENAÇÃO DO GRID."""
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
        """MOVIMENTA UM INTEGRANTE NA ORDENAÇÃO DO GRID."""
        rst = {"success": False, "message": "Nada foi feito ainda."}
        query = MemberCommission.objects.filter(pk=self.request.REQUEST.get("pk"))
        if query.exists() is True:
            try:
                q = MemberCommission.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception as e:
                self.log.error(e)
                rst.update(message="Não consegui encontrar o participante.")
            else:
                q.reorder()
                for cs in query.order_by("order"):
                    cs.move_up()
                rst.update(success=True)
        else:
            rst.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return rst

    def _move_down(self):
        """MOVIMENTA UM INTEGRANTE NA ORDENAÇÃO DO GRID."""
        rst = {"success": False, "message": "Nada foi feito ainda."}
        query = MemberCommission.objects.filter(pk=self.request.REQUEST.get("pk"))
        if query.exists():
            try:
                q = MemberCommission.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception:
                rst.update(message="Não consegui encontrar o participante")
            else:
                q.reorder()
                for cs in query.order_by("-order"):
                    cs.move_down()
                rst.update(success=True)
        else:
            rst.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return rst

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)
        # log.info(params)

        if "member" in params:
            if params.get("member") != "":
                field = getattr(self.Model, "member")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(member=query.get(pk=params.get("member")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(member=None)

        if "commission" in params:
            if params.get("commission") != "":
                field = getattr(self.Model, "commission")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(commission=query.get(pk=params.get("commission")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(commission=None)

        if "impediment" in params:
            params.update(impediment=params.get("impediment", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            member=nil_pk(instance.member, None),
            member_unicode=str(instance.member) or None,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            commission=nil_pk(instance.commission, None),
            commission_unicode=str(instance.commission) or None,
            impediment=str(instance.impediment),
            impediment_display="Sim" if instance.impediment else "Não",
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            type_participant=str(instance.type_participant),
            # type_participant_display=nil_display(instance, 'type_participant', None),
            type_participant_display=instance.get_display(),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            order=str(instance.order),
        )

        return rst
