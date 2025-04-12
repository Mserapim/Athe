# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import EncargoFinanceiro, MovimentacaoRequisicao, PeriodoRequisicao


class RHEncargoFinanceiro(RestfulDRY):

    _model = EncargoFinanceiro

    force_orm_single = True

    full_text_index = (
        "requisicao__servidor__pessoa_fisica__nome__icontains",
        "requisicao__servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.requisicao.EncargoFinanceiroManage")'
        )


class RHPeriodoRequisicaoRestful(RestfulDRY):

    _model = PeriodoRequisicao

    force_orm_single = True

    full_text_index = (
        "requisicao__servidor__pessoa_fisica__nome__icontains",
        "requisicao__servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.requisicao.PeriodoRequisicaoManage")'
        )


class RHRequisicaoRestful(RestfulDRY):

    _model = MovimentacaoRequisicao

    force_orm_single = True

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    exclude_fields = ["orgao_origem", "movimentacaopessoal_ptr"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.requisicao.Manage")')
