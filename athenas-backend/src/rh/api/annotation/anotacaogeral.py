# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import AnotacaoGeral, TipoDocumento

log = getLogger(__name__)


class RHAnotacaoGeralRestful(RestfulDRY):

    force_upper = False

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
        "resumo__icontains",
        "numero_documento__icontains",
        "publicacao__cache_unicode__icontains",
    )

    exclude_fields = [
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
        "anotacaoafastamento_ptr",
        "anotacaoausencia_ptr",
        "anotacaocarreira_ptr",
        "anotacaocomunicacao_ptr",
        "anotacaoelogio_ptr",
        "anotacaoenquadramento_ptr",
        "anotacaoevento_ptr",
        "anotacaofalta_ptr",
        "anotacaoferias_ptr",
        "anotacaofolgaaniversario_ptr",
        "anotacaofolgacompensacao_ptr",
        "anotacaofolgaeleitoral_ptr",
        "anotacaogeral_ptr",
        "anotacaogratificacao_ptr",
        "anotacaohorarioespecial_ptr",
        "anotacaolicenca_ptr",
        "anotacaopenadisciplinar_ptr",
        "anotacaoplantao_ptr",
        "anotacaorecesso_ptr",
        "anotacaoremocao_ptr",
        "anotacaotempodobro_ptr",
        "anotacaotemposervico_ptr",
        "anotacaotransposicao_ptr",
        "anotacaoviagem_ptr",
    ]

    force_persist_boolean_fields = []

    _model = AnotacaoGeral

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.anotacao.anotacaogeral.Manage")')


class RHTipoDocumentoAnotacao(RestfulDRY):

    _model = TipoDocumento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.anotacao.tipodocumento.Manage")')
