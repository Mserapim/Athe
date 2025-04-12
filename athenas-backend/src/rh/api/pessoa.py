# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes REST de Pessoa - RH.

:Classes:
  :class:`RHPessoa`.
"""

from contrib.newrest import Restful
from contrib.utils import getLogger
from rh.models import Pessoa, PessoaFisica, PessoaJuridica

log = getLogger(__name__)


class RHPessoaRestful(Restful):

    _model = Pessoa

    force_upper = False

    full_text_index = (
        "nome__icontains",
        "pessoajuridica__razao_social__icontains",
        "pessoafisica__cpf",
        "pessoajuridica__cnpj",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pessoa.Manager",{})')

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        log.debug(params)

        return params

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)

        cpf_cnpj = ""
        try:
            if instance.pessoafisica is not None:
                cpf = instance.pessoafisica.cpf
                cpf_cnpj = "%s.%s.%s-%s" % (cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11])
        except Exception:
            pass
        try:
            if instance.pessoajuridica is not None:
                cnpj = instance.pessoajuridica.cnpj
                cpf_cnpj = "%s.%s.%s/%s-%s" % (
                    cnpj[0:2],
                    cnpj[2:5],
                    cnpj[5:8],
                    cnpj[8:12],
                    cnpj[12:],
                )
        except Exception:
            pass
        _dict_.update(
            nome=instance.nome,
            cpf_cnpj=cpf_cnpj,
            identificador="%s - %s" % (instance.nome, cpf_cnpj),
        )
        return _dict_


class RHPessoaFisicaRestful(Restful):

    _model = PessoaFisica

    force_upper = True

    full_text_index = ("nome__icontains", "cpf")

    # def json(self, args=[]):
    #     self.response['content-type'] = 'text/javascript'
    #     self.response.write('Ext._create("rh.pessoa.fisica.Manager",{})')

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor informar o nome")

        if "cpf" in params:
            if params.get("cpf", "") == "":
                raise Exception("Favor informar o cpf")
            cpf = params.get("cpf")
            cpf = cpf.replace(".", "").replace("-", "")
            if len(cpf) != 11:
                raise Exception("Cpf inválido")

            # Realizar a validacao do cpf aqui
            # if self.validate(cpf) is False:
            #     raise Exception('Cpf inválido')
            params.update(cpf=cpf)

        log.debug(params)

        return params

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)

        _dict_.update(
            nome=instance.nome,
            cpf_cnpj=instance.cpf,
            identificador="%s - %s" % (instance.nome, instance.cpf),
        )
        return _dict_


class RHPessoaJuridicaRestful(Restful):

    _model = PessoaJuridica

    force_upper = True

    full_text_index = ("nome__icontains", "cnpj")

    # def json(self, args=[]):
    #     self.response['content-type'] = 'text/javascript'
    #     self.response.write('Ext._create("rh.pessoa.juridica.Manager",{})')

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor informar o nome")

        if "cnpj" in params:
            if params.get("cnpj", "") == "":
                raise Exception("Favor informar o cnpj")
            cnpj = params.get("cnpj")
            cnpj = cnpj.replace(".", "").replace("-", "").replace("/", "")
            if len(cnpj) != 14:
                raise Exception("Cnpj inválido")

            # Realizar a validacao do cnpj aqui
            # if self.validate(cnpj) is False:
            #     raise Exception('Cnpj inválido')
            params.update(cnpj=cnpj)

        log.debug(params)

        return params

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)

        _dict_.update(
            nome=instance.nome,
            cpf_cnpj=instance.cnpj,
            identificador="%s - %s" % (instance.nome, instance.cnpj),
        )
        return _dict_
