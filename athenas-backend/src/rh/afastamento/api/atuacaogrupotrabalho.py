# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.afastamento.models import AtuacaoGrupoTrabalho
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful


log = getLogger(__name__)


class AFAAtuacaoGrupoTrabalhoRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AtuacaoGrupoTrabalho

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.atuacaogrupotrabalho.Manage")')
