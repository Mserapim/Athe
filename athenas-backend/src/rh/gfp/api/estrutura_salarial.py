# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.gfp.models import (
    CargosEstrutura,
    EstruturaTabelaSalarial,
    ModeloTabelaSalarial,
    ReferenciaNiveis2D,
    ReferenciaSalario,
    TabelaSalarial,
)


class GFPEstruturaSalarialRestful(RestfulDRY):

    _model = EstruturaTabelaSalarial

    full_text_index = (
        "titulo__icontains",
        "codigo__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.EstruturaSalarialManage")'
        )


class GFPModeloTabelaSalarialRestful(RestfulDRY):

    _model = ModeloTabelaSalarial

    full_text_index = ("titulo__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.ModeloTabelaSalarialManage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(GFPModeloTabelaSalarialRestful, self).model_to_dict(instance)

        referencias = {}

        for rn2d in instance.referencias.order_by("ordem"):
            referencias[rn2d.sigla_cache] = {
                "sigla_cache": rn2d.sigla_cache,
                "tipo_valor": rn2d.tipo_valor,
                "tipo_gratificacao": rn2d.tipo_gratificacao,
                "ativo": rn2d.ativo,
                "ordem": rn2d.ordem,
            }

        _dict_.update({"referencias": referencias})

        return _dict_


class GFPReferenciaNiveis2DRestful(RestfulDRY):

    _model = ReferenciaNiveis2D

    full_text_index = (
        "estrutura_salarial__titulo__icontains",
        "sigla_cache__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.ReferenciaNiveis2DManage")'
        )


class GFPTabelaSalarialRestful(RestfulDRY):

    _model = TabelaSalarial

    full_text_index = (
        "estrutura_salarial__titulo__icontains",
        "info_adicional__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.TabelaSalarialManage")'
        )


class GFPCargosEstruturaRestful(RestfulDRY):

    _model = CargosEstrutura

    full_text_index = (
        "cargo__nome__icontains",
        "estrutura_salarial__titulo__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.CargosEstruturaManage")'
        )


class GFPReferenciaSalarioRestful(RestfulDRY):

    _model = ReferenciaSalario

    full_text_index = (
        "tabela_salarial__estrutura_salarial__titulo__icontains",
        "tabela_salarial__estrutura_salarial__codigo__iexact",
        "sigla_cache__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.estrutura_salarial.ReferenciaSalarioManage")'
        )
