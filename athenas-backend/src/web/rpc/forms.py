# -*- coding:utf-8 -*-

from django import forms
from rh import const
from rh.models import SeriousDiseases, SocialProgram, Localidade

from localflavor.br.forms import BRZipCodeField, BRCPFField

"""
ESTADO_CIVIL_CHOICES
SEXO_CHOICES
TIPO_NIVEL_ESCOLARIDADE
RACA_COR_CHOICES
"""


# Forms for passwords
class ChangePasswordBaseForm(forms.Form):
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirmation = forms.CharField(
        label="Confirmação da senha", widget=forms.PasswordInput
    )


class ChangePasswordForm(ChangePasswordBaseForm):
    key = forms.CharField(label="Código de verificação")
    email = forms.CharField(label="Email")


class UserForm(forms.Form):
    user_kind = forms.CharField()
    name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()

    phone_kind = forms.IntegerField(required=False)
    phone = forms.CharField(required=False)
    phone_kind2 = forms.IntegerField(required=False)
    phone2 = forms.CharField(required=False)

    address_kind = forms.IntegerField(required=False)
    address_location_kind = forms.IntegerField(required=False)
    address = forms.CharField(required=False)
    city = forms.ModelChoiceField(
        required=False,
        queryset=Localidade.objects.filter(estado__sigla="TO").order_by("nome"),
    )
    zipcode = BRZipCodeField(required=False)
    number = forms.CharField(required=False)
    neighborhood = forms.CharField(required=False)
    extra = forms.CharField(required=False)

    class Meta:
        prefetch_data = {
            "user_kind": "individual",
            "username": "joaojose",
            "password": "1234",
            "email": "joaojose@email.com",
            "name": "João José",
            "phone_kind": 3,
            "phone": "6384482854",
            "phone_kind2": 3,
            "phone2": "6384343454",
            "address_kind": 1,
            "address_location_kind": 9,
            "address": "210 Sul, Alameda 1, Lote 1, Casa 16",
            "city": 12178,
            "zipcode": "77020600",
            "number": "SN",
            "neighborhood": "Plano Diretor Sul",
            "extra": "Em frente ao Colégio Marista",
        }


# Forms for Inidividuals
class IndividualUserForm(UserForm):
    mother_name = forms.CharField()
    cpf = BRCPFField()
    rg = forms.CharField(required=False)
    nationality = forms.CharField(required=False)
    birth_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    marital_status = forms.ChoiceField(
        required=False, choices=const.ESTADO_CIVIL_CHOICES
    )
    gender = forms.CharField(required=False)
    genre = forms.CharField(required=False)
    education = forms.ChoiceField(
        required=False, choices=list(const.GRAU_INSTRUCAO_CHOICES.items())
    )
    race = forms.ChoiceField(required=False, choices=const.RACA_COR_CHOICES)
    profession = forms.CharField(required=False)
    income = forms.FloatField(required=False)
    disease = forms.ModelMultipleChoiceField(
        required=False, queryset=SeriousDiseases.objects.order_by("name")
    )
    social_program = forms.ModelMultipleChoiceField(
        required=False, queryset=SocialProgram.objects.order_by("name")
    )

    class Meta:
        prefetch_data = {
            "cpf": "359.987.311-90",
            "rg": "32165478",
            "mother_name": "Jacobina Inácia",
            "nationality": "Brasileiro",
            "birth_date": "1986-8-27",
            "marital_status": 2,
            "gender": "M",
            "genre": "Homem",
            "education": 3,
            "race": 5,
            "profession": "Butequêro",
            "income": 4000.0,
            "disease": [26, 27, 24],
            "social_program": "Bolsa empresário",
        }


class CreateIndividualUserForm(IndividualUserForm, ChangePasswordBaseForm):
    pass


class UpdateIndividualUserForm(IndividualUserForm):
    id = forms.IntegerField()


# Forms for Lawyer
class LawyerUserForm(UserForm):
    oab = forms.CharField()


class CreateLawyerUserForm(LawyerUserForm, ChangePasswordBaseForm):
    pass


class UpdateLawyerUserForm(LawyerUserForm):
    id = forms.IntegerField()


# Auth forms
class AuthenticateForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class TokenAuthenticateForm(forms.Form):
    token = forms.CharField()
