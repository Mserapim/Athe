# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import InativacaoCargoMembro
from rh.utils import departure_reason_unicode, situation_unicode

log = getLogger(__name__)


class RHInativacaoCargoMembroRestful(RestfulDRY):

    _model = InativacaoCargoMembro

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.inativacaocargomembro.Manage")')

    def model_to_dict(self, instance):
        params = super(RHInativacaoCargoMembroRestful, self).model_to_dict(instance)
        params.update(
            {
                "matricula": (
                    instance.afastamento.servidor.matricula
                    if instance.afastamento
                    else ""
                ),
                "posse_cargo_unicode": (
                    instance.possession.quadro if instance.possession else ""
                ),
                "situation_unicode": situation_unicode(
                    instance.data_inicio, instance.data_fim
                ),
                "departure_reason_unicode": departure_reason_unicode(
                    instance.afastamento
                ),
            }
        )
        return params
