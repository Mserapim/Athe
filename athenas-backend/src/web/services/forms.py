#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.forms import *
from edocs.protocolo.models import Protocolo
from localflavor.br.forms import BRZipCodeField, BRCPFField, BRCNPJField


class EstagioForm(Form):
    faculdade = CharField()
    matricula = CharField()
    periodo = CharField()
    conclusao = DateField()
    curso = CharField()
    disponibilidade = CharField()


class RecursoForm(Form):
    inscricao = CharField(min_length=17, max_length=17)
    assunto = CharField()
    resumo = CharField()


class EnderecoForm(Form):
    endereco = CharField()
    bairro = CharField()
    cidade = CharField()
    # estado = CharField()
    CEP = BRZipCodeField()


class PessoaForm(Form):
    interessado = CharField()
    email = EmailField(required=False)
    telefone = CharField()


class PessoaFisicaForm(PessoaForm):
    CPF = BRCPFField()
    estado_civil = CharField(required=False)
    raca_cor = IntegerField()
    naturalidade = CharField(required=False)
    identidade = CharField(required=False)
    emissor = CharField(required=False)


class PessoaJuridicaForm(PessoaForm):
    razao_social = CharField()
    CNPJ = BRCNPJField()


class ProtocoloForm(Form):
    tipo_pessoa = CharField()
    resumo = CharField()
    assunto = CharField()
    sigla_lotacao = CharField()
    tipo_doc = CharField()


class ProtocoloPFisicaForm(ProtocoloForm, PessoaFisicaForm, EnderecoForm):
    pass


class ProtocoloPJuridicaForm(ProtocoloForm, PessoaJuridicaForm, EnderecoForm):
    pass


class InscricaoConcursoForm(ProtocoloPFisicaForm):
    pass
