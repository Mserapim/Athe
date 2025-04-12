# -*- coding: utf-8 -*-
import json

from adm.patrimonio.models import Suspensao
from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_pk, nil_unicode
from contrib.utils import getLogger, person_from_user

log = getLogger(__name__)


class PATSuspensao(Restful):

    _model = Suspensao

    force_upper = False

    def close(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda!"}

        try:
            suspensao = Suspensao.objects.get(pk=self.get_params().get("pk"))
        except Suspensao.DoesNotExist:
            rst.update(message="Não consegui encontrar a suspensão.")
        else:
            try:
                suspensao.ativo = False
                suspensao.save()
            except Exception as e:
                rst.update(message="Não foi possivel finalizar a suspensão")
                log.exception(e)
            else:
                rst.update(success=True)

        self.response.write(json.dumps(rst))

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "nota_entrada" in params:
            if params.get("nota_entrada") != "":
                field = getattr(self.Model, "nota_entrada")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(nota_entrada=query.get(pk=params.get("nota_entrada")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(nota_entrada=None)

        if "item_entrada" in params:
            if params.get("item_entrada") != "":
                field = getattr(self.Model, "item_entrada")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(item_entrada=query.get(pk=params.get("item_entrada")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(item_entrada=None)

        if "ativo" in params:
            params.update(ativo=params.get("ativo", "off") == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        def nil_user_pessoa(u, n):
            return str(person_from_user(u)) if u and person_from_user(u) else n

        rst.update(
            data_fim=nil_datetime(instance.data_fim, None),
            aberto_por=nil_pk(instance.aberto_por, None),
            aberto_por_unicode=nil_unicode(instance.aberto_por, None),
            aberto_por_pessoa=nil_user_pessoa(instance.aberto_por, None),
            fechado_por=nil_pk(instance.fechado_por, None),
            fechado_por_unicode=nil_unicode(instance.fechado_por, None),
            fechado_por_pessoa=nil_user_pessoa(instance.fechado_por, None),
            justificativa=instance.justificativa,
            nota_entrada=nil_pk(instance.nota_entrada, None),
            nota_entrada_unicode=nil_unicode(instance.nota_entrada, None),
            item_entrada=nil_pk(instance.item_entrada, None),
            item_entrada_unicode=nil_unicode(instance.item_entrada, None),
            ativo=instance.ativo,
            data_inicio=nil_datetime(instance.data_inicio, None),
        )

        return rst
