# -*- coding: utf-8 -*-
from adm.patrimonio.models import Documento, Movimento, NotaEntrada, Patrimonio
from contrib.newrest import Restful
from contrib.utils import DateUtils
from django.template.defaultfilters import slugify
from ged.models import Arquivo


class PATDocumento(Restful):

    _model = Documento

    force_upper = False

    def model_to_dict(self, instance):
        rst = super(PATDocumento, self).model_to_dict(instance)

        rst.update(
            icons=[
                {
                    "title": instance.data.mimetype,
                    "iconCls": "icon-ged icon-ged-%s"
                    % slugify(
                        instance.data.mimetype.replace("/", "-").replace("+", "-")
                    ),
                }
            ],
            mimetype=instance.data.mimetype,
            titulo=instance.titulo,
            criado=DateUtils.datetime_to_str(instance.criado),
            criado_por=instance.data.user.username,
            permalink=instance.data.permalink(),
            data=instance.data.pk,
        )

        return rst

    def get_params(self, querydict=None, **kargs):
        params = super(PATDocumento, self).get_params(querydict, **kargs)

        if params.get("documentos_de_movimentacao", "") != "":
            params.update(
                {
                    "documentos_de_movimentacao": [
                        Movimento.objects.get(
                            pk=params.get("documentos_de_movimentacao")
                        )
                    ]
                }
            )
        elif "documentos_de_movimentacao" in params:
            del params["documentos_de_movimentacao"]

        if params.get("documentos_de_entrada", "") != "":
            params.update(
                {
                    "documentos_de_entrada": [
                        NotaEntrada.objects.get(pk=params.get("documentos_de_entrada"))
                    ]
                }
            )
        elif "documentos_de_entrada" in params:
            del params["documentos_de_entrada"]

        if params.get("documentos_do_patrimonio", "") != "":
            params.update(
                {
                    "documentos_do_patrimonio": [
                        Patrimonio.objects.get(
                            pk=params.get("documentos_do_patrimonio")
                        )
                    ]
                }
            )
        elif "documentos_do_patrimonio" in params:
            del params["documentos_do_patrimonio"]

        if params.get("data", "") != "":
            params.update({"data": Arquivo.objects.get(pk=params.get("data"))})
        elif "data" in params:
            del params["data"]

        return params
