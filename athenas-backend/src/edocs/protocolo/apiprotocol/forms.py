# -*- coding:utf-8 -*-

# from collections import OrderedDict
from django import forms
from localflavor.br.forms import BRCNPJField, BRCPFField, BRZipCodeField

from rh.const import GRAU_INSTRUCAO_CHOICES, RACA_COR_CHOICES, SEXO_CHOICES
from rh.models import Estado as State
from rh.models import Localidade as City
from rh.models import Pessoa as Person
from standard.models import Choice

CHOICES = {
    "GENRE": SEXO_CHOICES,
    "YESNO": (
        (1, "SIM"),
        (0, "NÃO"),
    ),
    "ADDRESS_TYPE": list(Choice.get_choices_for("rh", "TYPE_ADDRESS")),
    "PUBLIC_PLACE_TYPE": list(Choice.get_choices_for("rh", "TYPE_STREET")),
    "PHONE_TYPE": list(Choice.get_choices_for("rh", "TYPE_PHONE")),
    "RACE": list(Choice.get_choices_for("rh", "TYPE_RACE")),
    "MARITAL_STATUS": list(
        Choice.get_choices_for("rh", "MARITAL_STATUS", query_dict={"active": True})
    ),
    "ALL_CITIES": list(City.objects.all().order_by("nome").values_list("id", "nome")),
    "EDUCATION_LEVEL": list(
        Choice.get_choices_for(
            "rh",
            "DEGREE_EDUCATION",
            query_dict={"cvalue__in": [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 18]},
        )
    ),
    "CITY": list(
        City.objects.filter(estado__sigla="TO")
        .order_by("nome")
        .values_list("id", "nome")
    ),
    "STATE": list(
        State.objects.filter(pais__pk=1).order_by("nome").values_list("id", "sigla")
    ),
}

OMBUDSMAN_CHOICES = {
    **CHOICES,
    **{
        "SUBJECT": (
            ("", "----------------------"),
            ("Comentário", "Comentário"),
            ("Crítica", "Crítica"),
            ("Denúncia", "Denúncia"),
            ("Elogio", "Elogio"),
            ("Pedido de Informação", "Pedido de Informação"),
            ("Reclamação", "Reclamação"),
            ("Sugestão", "Sugestão"),
        )
    },
}

ONLINE_PROTOCOL_CHOICES = CHOICES.copy()


class BaseForm(forms.Form):
    channel_slug = forms.CharField()
    subject = forms.CharField()
    text = forms.CharField()


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
    email = forms.EmailField(required=False)


class AnonymousProtocolForm(BaseForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(), to_field_name="slug"
    )


class CitizenProtocolForm(BasePersonForm):
    cpf = BRCPFField()
    subject_detail = forms.CharField(required=False)
    document_number = forms.CharField(required=False)
    genre = forms.ChoiceField(choices=CHOICES["GENRE"])
    education_level = forms.ChoiceField(choices=CHOICES["EDUCATION_LEVEL"])
    live_in_referenced_city = forms.BooleanField(required=False)
    marital_status = forms.ChoiceField(
        choices=CHOICES["MARITAL_STATUS"], required=False
    )
    race = forms.ChoiceField(choices=CHOICES["RACE"], required=False)
    referenced_city = forms.ModelChoiceField(
        queryset=City.objects.all(), required=False
    )


class LegalPersonProtocolForm(BasePersonForm):
    cnpj = BRCNPJField()
    subject_detail = forms.CharField(required=False)
    document_number = forms.CharField(required=False)


class BasePersonCertificate(BaseForm):
    name = forms.CharField()
    email = forms.EmailField(required=False)


class CitizenCertificateForm(BasePersonCertificate):
    cpf = BRCPFField()


class LegalPersonCertificateForm(BasePersonCertificate):
    cnpj = BRCNPJField()
