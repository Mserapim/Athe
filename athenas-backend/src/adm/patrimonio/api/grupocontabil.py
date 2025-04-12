# -*- coding: utf-8 -*-
from adm.patrimonio.models import GrupoContabil
from contrib.newrest import Restful


class PATIGrupoContabil(Restful):

    _model = GrupoContabil

    full_text_index = ("cache_number__icontains", "title__icontains")

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            classificacao=instance.classificacao,
            consolidacao=instance.consolidacao,
            title=instance.title,
            cache_number=instance.cache_number,
        )

        return rst
