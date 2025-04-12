# -*- coding:utf-8 -*-

from collections import OrderedDict
from django.forms import *

# from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from standard.models import Choice
from rh.models import Localidade
from web.ouvidoria.choices import *
from localflavor.br.forms import BRZipCodeField, BRCPFField, BRCNPJField


class TipoPessoaForm(Form):
    tipo = CharField(
        error_messages={"required": "Selecione o tipo de pessoa"},
        label="Tipo de Pessoa",
        widget=RadioSelect(choices=POR),
    )


class BaseForm(Form):
    tipo = CharField(widget=HiddenInput())
    assunto = CharField(
        label="*Assunto", widget=Select(attrs={"class": "normal"}, choices=ASSUNTO)
    )
    resumo = CharField(label="*Resumo", widget=Textarea(attrs={"class": "full"}))
    # captcha = ReCaptchaField(label='')
    field_order = []

    def order_fields(self, field_order=[]):
        field_order = field_order or self.field_order
        if field_order:
            ordered_fields = OrderedDict()
            for field_name in self.field_order:
                ordered_fields[field_name] = self.fields[field_name]

            self.fields = ordered_fields


class PessoaForm(BaseForm):
    nome = CharField(label="*Nome", widget=TextInput(attrs={"class": "large"}))
    tipo_endereco = ChoiceField(
        label="*Tipo de Endereço", choices=Choice.get_choices_for("rh", "TYPE_ADDRESS")
    )
    tipo_logradouro = ChoiceField(
        label="*Tipo de Logradouro", choices=Choice.get_choices_for("rh", "TYPE_STREET")
    )
    logradouro = CharField(
        label="*Logradouro", widget=TextInput(attrs={"class": "full"})
    )
    numero = CharField(label="*Número")
    bairro = CharField(label="*Bairro", widget=TextInput(attrs={"class": "normal"}))
    complemento = CharField(
        label="Complemento", widget=TextInput(attrs={"class": "large"}), required=False
    )
    municipio = ChoiceField(
        label="*Município",
        choices=Localidade.objects.filter(estado__sigla="TO")
        .order_by("nome")
        .values_list("id", "nome"),
    )
    cep = BRZipCodeField(
        label="*CEP",
        help_text="*Somente números",
        widget=TextInput(attrs={"class": "mask"}),
    )
    email = EmailField(
        required=False,
        help_text="Caso deseje receber informações sobre o andamento de sua manifestação. Ex: joao@email.com",
        widget=TextInput(attrs={"class": "normal"}),
    )
    telefone = CharField(
        help_text="Somente números", widget=TextInput(attrs={"class": "mask"})
    )


class PessoaFisicaForm(PessoaForm):

    cpf = BRCPFField(
        label="*CPF",
        help_text="Somente números",
        widget=TextInput(attrs={"class": "mask"}),
    )
    grau_instrucao = IntegerField(
        label="Grau de instrução",
        widget=Select(attrs={"class": "normal"}, choices=ESCOLARIDADE),
    )
    sexo = CharField(
        label="*Sexo", widget=Select(attrs={"class": "normal"}, choices=SEXO)
    )
    mora_no_municipio_referido = CharField(
        label="Reside no município referente à manifestação?",
        widget=Select(attrs={"class": "normal"}, choices=SIM_NAO),
    )

    field_order = [
        "tipo",
        "cpf",
        "nome",
        "assunto",
        "resumo",
        "tipo_endereco",
        "tipo_logradouro",
        "logradouro",
        "numero",
        "bairro",
        "complemento",
        "municipio",
        "cep",
        "email",
        "telefone",
        "grau_instrucao",
        "sexo",
        "mora_no_municipio_referido",
        "captcha",
    ]


class PessoaJuridicaForm(PessoaForm):
    cnpj = BRCNPJField(
        label="*CNPJ",
        help_text="Somente números",
        widget=TextInput(attrs={"class": "mask"}),
    )

    field_order = [
        "tipo",
        "cnpj",
        "nome",
        "assunto",
        "resumo",
        "tipo_endereco",
        "tipo_logradouro",
        "logradouro",
        "numero",
        "bairro",
        "complemento",
        "municipio",
        "cep",
        "email",
        "telefone",
        "captcha",
    ]


class FindForm(Form):
    KINDS = (
        ("code", "Protocolo"),
        ("seal", "Chancela"),
        # ('name', 'Nome')
    )
    kind = CharField(widget=Select(choices=KINDS))
    value = CharField(widget=TextInput(attrs={"class": "normal"}))
