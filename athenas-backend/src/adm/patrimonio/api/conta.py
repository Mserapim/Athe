# -*- coding: utf-8 -*-
from adm.patrimonio.models import Conta, Sequencia
from contrib.newrest import Restful


class PATConta(Restful):

    _model = Conta

    full_text_index = ("titulo__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.parametro.ContaManage")')

    def get_params(self, querydict=None, **kargs):
        params = super(PATConta, self).get_params(querydict, **kargs)

        if "sequencia" in params:
            params.update(sequencia=Sequencia.objects.get(pk=params.get("sequencia")))

        if "principal" in params:
            params.update(principal=params.get("principal", "off") == "on")

        return params

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            {
                "tipo": instance.tipo,
                "tipo_display": instance.get_tipo_display(),
                "sequencia": (
                    instance.sequencia.pk if instance.sequencia is not None else 0
                ),
                "sequencia_unicode": (
                    str(instance.sequencia)
                    if instance.sequencia is not None
                    else "Nenhuma"
                ),
                "prefix": instance.prefix,
                "sufix": instance.sufix,
                "principal": instance.principal,
                "titulo": instance.titulo,
            }
        )
        return params
