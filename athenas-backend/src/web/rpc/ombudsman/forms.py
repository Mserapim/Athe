# -*- coding:utf-8 -*-

# from collections import OrderedDict
from django import forms
from localflavor.br.forms import BRZipCodeField, BRCPFField, BRCNPJField
from standard.models import Choice
from rh.const import GRAU_INSTRUCAO_CHOICES, SEXO_CHOICES, SIM_NAO
from rh.models import Pessoa as Person, Localidade as City, Estado as State


CHOICES = {
    "PERSON_TYPE": (
        ("0", "Anônimo"),
        ("1", "Cidadão"),
        ("2", "Órgão Público"),
        ("3", "Órgão Privado"),
    ),
    "SUBJECT": (
        ("", "----------------------"),
        ("Comentário", "Comentário"),
        ("Crítica", "Crítica"),
        ("Denúncia", "Denúncia"),
        ("Elogio", "Elogio"),
        ("Mulheres na Política", "Mulheres na Política"),
        ("Pedido de Informação", "Pedido de Informação"),
        ("Reclamação", "Reclamação"),
        ("Sugestão", "Sugestão"),
    ),
    "SCHOOL": tuple(list(GRAU_INSTRUCAO_CHOICES.items())[:-1]),
    "GENRE": SEXO_CHOICES,
    "YESNO": SIM_NAO,
    "ADDRESS_TYPE": list(Choice.get_choices_for("rh", "TYPE_ADDRESS")),
    "PUBLIC_PLACE_TYPE": list(Choice.get_choices_for("rh", "TYPE_STREET")),
    "PHONE_TYPE": list(Choice.get_choices_for("rh", "TYPE_PHONE")),
    "RACE": list(Choice.get_choices_for("rh", "TYPE_RACE")),
    "MARITAL_STATUS": list(Choice.get_choices_for("rh", "MARITAL_STATUS")),
    "CITY": list(City.objects.all().order_by("nome").values_list("id", "nome")),
    "STATE": list(State.objects.all().order_by("sigla").values_list("id", "sigla")),
}


class BaseForm(forms.Form):
    subject = forms.ChoiceField(choices=CHOICES["SUBJECT"])
    text = forms.CharField()


class AnonymousManifestationForm(BaseForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(), to_field_name="slug"
    )


class AddressForm(forms.Form):
    address_type = forms.ChoiceField(choices=CHOICES["ADDRESS_TYPE"])
    public_place_type = forms.ChoiceField(choices=CHOICES["PUBLIC_PLACE_TYPE"])
    public_place = forms.CharField()
    zipcode = BRZipCodeField()
    extra = forms.CharField(required=False)
    neighborhood = forms.CharField()
    number = forms.CharField()
    city = forms.ModelChoiceField(queryset=City.objects.all())


class PhoneForm(forms.Form):
    phone_type = forms.ChoiceField(choices=CHOICES["PHONE_TYPE"], required=False)
    phone_number = forms.CharField(required=False)


class BasePersonForm(BaseForm, AddressForm, PhoneForm):
    name = forms.CharField()
    email = forms.EmailField()


class LegalPersonManifestationForm(BasePersonForm):
    cnpj = BRCNPJField()


class CitizenManifestationForm(BasePersonForm):
    cpf = BRCPFField()
    genre = forms.ChoiceField(choices=CHOICES["GENRE"])
    school = forms.ChoiceField(choices=CHOICES["SCHOOL"])
    live_in_referenced_city = forms.ChoiceField(
        choices=CHOICES["YESNO"], required=False
    )
    marital_status = forms.ChoiceField(
        choices=CHOICES["MARITAL_STATUS"], required=False
    )
    race = forms.ChoiceField(choices=CHOICES["RACE"], required=False)
