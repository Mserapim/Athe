# -*- coding: utf-8 -*-
from adm.contabilidade.models import FonteRecurso
from contrib.newrest import Restful
from contrib.utils import getLogger

log = getLogger(__name__)


class ContabFonteRecurso(Restful):

    _model = FonteRecurso

    full_text_index = ("numero__icontains", "descricao__icontains")

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        params.update(convenio="convenio" in params)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            convenio=instance.convenio,
            descricao=instance.descricao,
            numero=instance.numero,
        )

        return rst
