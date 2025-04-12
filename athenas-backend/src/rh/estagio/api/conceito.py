# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.utils import getLogger
from rh.estagio.models import Conceito

log = getLogger(__name__)


class GepConceito(Restful):

    _model = Conceito

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            valor_final=float(instance.valor_final or 0),
            descricao=instance.descricao,
            valor_inicial=float(instance.valor_inicial or 0),
        )

        return rst
