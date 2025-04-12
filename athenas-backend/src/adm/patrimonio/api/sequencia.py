# -*- coding: utf-8 -*-
from adm.patrimonio.models import Sequencia
from contrib.newrest import Restful
from contrib.utils import getLogger

log = getLogger(__name__)


class PATSequencia(Restful):

    _model = Sequencia

    full_text_index = ("titulo__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.parametro.SequenciaManage")')

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update({"titulo": instance.titulo, "proximo": instance.proximo})
        return _dict_
