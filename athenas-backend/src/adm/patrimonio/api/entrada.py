# -*- coding: utf-8 -*-
from adm.contabilidade.models import NE as NotaEmpenho
from adm.patrimonio.models import (
    Conta,
    Especie,
    ItemEntrada,
    NotaConvenio,
    NotaDoacao,
    NotaEntrada,
    NotaFiscal,
)
from contrib.helpers import roundf
from contrib.newrest import Restful
from contrib.nil import nil_pk, nil_str
from contrib.utils import DateUtils, getLogger
from rh.models import Pessoa

log = getLogger(__name__)


class PATEntrada(Restful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.entrada.Manage")')


class PATNotaEntrada(Restful):

    _model = NotaEntrada

    force_orm_single = True

    full_text_index = (
        "fornecedor__nome__icontains",
        "conta__titulo__icontains",
        "conta__sequencia__titulo__icontains",
        "liquidacao__icontains",
        "empenho__numero__icontains",
        "processo__icontains",
        "itens__especie__titulo__icontains",
        "itens__incorporacoes__plaqueta",
        "formated_number__icontains",
    )

    def get_params(self, *args, **kargs):
        params = super(PATNotaEntrada, self).get_params(*args, **kargs)

        if params.get("fornecedor", "") != "":
            params.update(fornecedor=Pessoa.objects.get(pk=params.get("fornecedor")))

        if params.get("conta", "") != "":
            params.update(conta=Conta.objects.get(pk=params.get("conta")))

        if params.get("empenho", "") != "":
            params.update(empenho=NotaEmpenho.objects.get(pk=params.get("empenho")))

        if params.get("data_compra", "") != "":
            params.update(data_compra=DateUtils.str_to_date(params.get("data_compra")))

        if params.get("data_nota", "") != "":
            params.update(data_nota=DateUtils.str_to_date(params.get("data_nota")))

        if params.get("data_liquidacao", "") != "":
            params.update(
                data_liquidacao=DateUtils.str_to_date(params.get("data_liquidacao"))
            )
        elif "data_liquidacao" in params:
            params.update(data_liquidacao=None)

        log.debug(params)

        return params

    def model_to_dict(self, instance):
        _dict_ = super(PATNotaEntrada, self).model_to_dict(instance)

        _dict_.update(
            {
                "fornecedor_unicode": (
                    str(instance.fornecedor) if instance.fornecedor else None
                ),
                "fornecedor": instance.fornecedor.pk if instance.fornecedor else None,
                "conta_unicode": str(instance.conta) if instance.conta else None,
                "conta": instance.conta.pk if instance.conta else None,
                "empenho_unicode": str(instance.empenho) if instance.empenho else None,
                "empenho": instance.empenho.pk if instance.empenho else None,
                "data_cadastro": (
                    DateUtils.datetime_to_str(instance.data_cadastro)
                    if instance.data_cadastro
                    else None
                ),
                "data_nota": (
                    DateUtils.date_to_str(instance.data_nota)
                    if instance.data_nota
                    else None
                ),
                "data_compra": (
                    DateUtils.date_to_str(instance.data_compra)
                    if instance.data_compra
                    else None
                ),
                "data_liquidacao": (
                    DateUtils.date_to_str(instance.data_liquidacao)
                    if instance.data_liquidacao
                    else None
                ),
                "execucao_orcamentaria_unicode": (
                    instance.get_execucao_orcamentaria_display()
                    if instance.execucao_orcamentaria
                    else None
                ),
                "execucao_orcamentaria": (
                    instance.execucao_orcamentaria
                    if instance.execucao_orcamentaria
                    else None
                ),
                "processo": instance.processo,
                "note_year": instance.note_year,
                "note_number": instance.note_number,
                "formated_number": instance.formated_number,
                "type": instance.my_origin.the_type,
                "liquidacao": instance.liquidacao,
                "icons": instance.icons,
                "suspenso": instance.suspensoes.filter(ativo=True).exists(),
            }
        )

        return _dict_


class PATNotaFiscal(PATNotaEntrada):

    _model = NotaFiscal

    def model_to_dict(self, instance):
        _dict_ = super(PATNotaFiscal, self).model_to_dict(instance)

        _dict_.update(
            {
                "numero": instance.numero,
            }
        )

        return _dict_


class PATNotaConvenio(PATNotaFiscal):

    _model = NotaConvenio

    def model_to_dict(self, instance):
        _dict_ = super(PATNotaConvenio, self).model_to_dict(instance)

        _dict_.update(
            {
                "conveniada_unicode": (
                    str(instance.conveniada) if instance.conveniada else None
                ),
                "conveniada": instance.conveniada.pk if instance.conveniada else None,
                "codigo_convenio": instance.codigo_convenio,
                "data_convenio": (
                    DateUtils.date_to_str(instance.data_convenio)
                    if instance.data_convenio
                    else None
                ),
                "data_fim_convenio": (
                    DateUtils.date_to_str(instance.data_fim_convenio)
                    if instance.data_fim_convenio
                    else None
                ),
            }
        )

        return _dict_

    def get_params(self, *args, **kargs):
        _dict_ = super(PATNotaConvenio, self).get_params(*args, **kargs)

        if _dict_.get("conveniada", None):
            _dict_.update(conveniada=Pessoa.objects.get(pk=_dict_.get("conveniada")))

        if _dict_.get("data_convenio", None):
            _dict_.update(
                data_convenio=DateUtils.str_to_date(_dict_.get("data_convenio"))
            )

        if _dict_.get("data_fim_convenio", None):
            _dict_.update(
                data_fim_convenio=DateUtils.str_to_date(_dict_.get("data_fim_convenio"))
            )

        return _dict_


class PATNotaDoacao(PATNotaEntrada):

    _model = NotaDoacao


class PATItemEntrada(Restful):

    _model = ItemEntrada

    full_text_index = (
        "especie__titulo__icontains",
        "descricao__icontains",
    )

    def get_params(self, *args, **kargs):
        _dict_ = super(PATItemEntrada, self).get_params(*args, **kargs)

        if _dict_.get("nota", None):
            _dict_.update(nota=NotaEntrada.objects.get(pk=_dict_.get("nota")))

        if _dict_.get("especie", None):
            _dict_.update(especie=Especie.objects.get(pk=_dict_.get("especie")))

        return _dict_

    def model_to_dict(self, instance):
        _dict_ = super(PATItemEntrada, self).model_to_dict(instance)

        _dict_.update(
            {
                "nota_unicode": nil_str(instance.nota, None),
                "nota": nil_pk(instance.nota, None),
                "especie_unicode": nil_str(instance.especie, None),
                "especie": nil_pk(instance.especie, None),
                "conservacao_display": instance.get_conservacao_display(),
                "conservacao": instance.conservacao,
                "meses_garantia": instance.meses_garantia,
                "descricao": instance.descricao,
                "valor_unitario": float(instance.valor_unitario or 0),
                "quantidade": int(instance.quantidade or 0),
                "icons": instance.icons,
                "valor_total": roundf(
                    int(instance.quantidade or 0) * float(instance.valor_unitario or 0),
                    2,
                ),
            }
        )

        return _dict_
