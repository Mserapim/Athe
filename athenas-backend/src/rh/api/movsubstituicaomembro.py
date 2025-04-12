# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.api.movsubstituicao import RHMovimentacaoSubstituicaoRestful
from rh.models import MovimentacaoSubstituicaoMembro

log = getLogger(__name__)


class RHMovimentacaoSubstituicaoMembroRestful(RHMovimentacaoSubstituicaoRestful):

    _model = MovimentacaoSubstituicaoMembro

    exclude_fields = RHMovimentacaoSubstituicaoRestful.exclude_fields + [
        "movimentacaosubstituicao_ptr",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.substituicaomembro.Manage")')
