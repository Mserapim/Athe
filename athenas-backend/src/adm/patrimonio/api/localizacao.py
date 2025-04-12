# -*- coding: utf-8 -*-
from adm.patrimonio.models import Localizacao
from contrib.newrest import RestfulTree
from contrib.nil import nil_pk, nil_unicode
from contrib.utils import getLogger

log = getLogger(__name__)


class PATLocalizacao(RestfulTree):

    _model = Localizacao

    folder_index = "dentro_de"

    force_upper = False

    full_text_index = ("titulo__icontains", "path_cache__icontains")

    def get_params(self, querydict=None, **kargs):
        params = super(PATLocalizacao, self).get_params(querydict, **kargs)

        if "dentro_de" in params:
            if params.get("dentro_de") != "":
                field = getattr(self.Model, "dentro_de")

                query = field.get_queryset()

                try:
                    params.update(dentro_de=query.get(pk=params.get("dentro_de")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(dentro_de=None)

        if "ativo" in params:
            params.update(ativo=params.get("ativo", "off").lower() == "on")

        if "lotacao_relacionada" in params:
            if params.get("lotacao_relacionada") != "":
                field = getattr(self.Model, "lotacao_relacionada")

                query = field.get_queryset()

                try:
                    params.update(
                        lotacao_relacionada=query.get(
                            pk=params.get("lotacao_relacionada")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lotacao_relacionada=None)

        return params

    def model_to_dict(self, instance):

        rst = RestfulTree.model_to_dict(self, instance)

        rst.update(
            {
                "titulo": instance.titulo,
                "dentro_de_unicode": nil_unicode(instance.dentro_de, None),
                "dentro_de": nil_pk(instance.dentro_de, None),
                "lotacao_relacionada_unicode": nil_unicode(
                    instance.lotacao_relacionada, None
                ),
                "lotacao_relacionada": nil_pk(instance.lotacao_relacionada, None),
                "endereco": instance.endereco,
                "ativo": instance.ativo,
            }
        )
        return rst

    def childs(self, args=[]):
        obj = {"success": False, "message": "Nada foi processado ainda."}

        root = args[0]
        query = Localizacao.objects.filter(
            folder_index__regex=r"^(\.\d+|)+\.%s(\.\d+)+$"
            % (root if root not in ["", None] else "")
        )

        obj.update(
            success=True,
            count=query.count(),
            collection=[self.model_to_dict(inst) for inst in query],
        )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/javascript")
        )
        rendererer(obj)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.localizacao.Manage")')
