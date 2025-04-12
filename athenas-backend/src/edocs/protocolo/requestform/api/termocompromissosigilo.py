# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import TermoCompromissoManutencaoSigilo as Termo


log = getLogger(__name__)


class RFTermoCompromissoSigilo(EDOCManage):

    _model = Termo
