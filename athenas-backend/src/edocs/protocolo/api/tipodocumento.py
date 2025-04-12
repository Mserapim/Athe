# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from edocs.protocolo.models import TipoDocumento as DocumentType


log = getLogger(__name__)


class EDOCTipoDocumentoRestful(Restful):

    _model = DocumentType

    full_text_index = ("nome__icontains",)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("edocs.protocolo.TipoDocumentoManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        bool_value = {"on": True, "off": False}

        if "habilita" in params:
            params.update(
                habilita=bool_value.get(params.get("habilita", "off").lower(), None)
            )

        return params

    def model_to_dict(self, instance):
        result = Restful.model_to_dict(self, instance)

        result.update(
            pk=instance.pk,
            nome=instance.nome,
            descricao=instance.descricao,
            habilita=instance.habilita,
        )

        return result
