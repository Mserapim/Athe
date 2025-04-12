# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.api.annotation.anotacaogeral import RHAnotacaoGeralRestful
from rh.models import AnotacaoGratificacao

log = getLogger(__name__)


class RHAnotacaoGratificacaoRestful(RHAnotacaoGeralRestful):

    _model = AnotacaoGratificacao

    full_text_index = () + RHAnotacaoGeralRestful.full_text_index

    exclude_fields = RHAnotacaoGeralRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + RHAnotacaoGeralRestful.force_persist_boolean_fields
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.anotacao.anotacaogratificacao.Manage")')
