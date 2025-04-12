# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.estagio.api.estagioprobatorioservidor import GepEstagioProbatorioServidor
from rh.estagio.models import EstagioProbatorioServidor

log = getLogger(__name__)


class GepEstagioProbatorioAvaliado(GepEstagioProbatorioServidor):

    _model = EstagioProbatorioServidor

    full_text_index = (
        "posse_servidor__servidor__matricula__icontains",
        "posse_servidor__servidor__pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.avaliado.Manage")')
