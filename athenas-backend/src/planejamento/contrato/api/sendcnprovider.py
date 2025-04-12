# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import EnvioNEFornecedor as SendCNProvider


log = getLogger(__name__)


class PHASendCNProvider(RestfulDRY):

    _model = SendCNProvider
