# -*- coding:utf-8 -*-

# from collections import OrderedDict
from django import forms
from localflavor.br.forms import BRZipCodeField, BRCPFField, BRCNPJField
from standard.models import Choice
from rh.const import GRAU_INSTRUCAO_CHOICES, RACA_COR_CHOICES, SEXO_CHOICES, SIM_NAO
from rh.models import Pessoa as Person, Localidade as City, Estado as State

from rh.const import GRAU_INSTRUCAO_CHOICES, SEXO_CHOICES, SIM_NAO
from standard.models import Choice

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
        ("Pedido de Informação", "Pedido de Informação"),
        ("Reclamação", "Reclamação"),
        ("Sugestão", "Sugestão"),
        ("Protocolo Online", "Protocolo Online"),
        ("LGPD - Solicitação de informação", "LGPD - Solicitação de informação"),
    ),
    "SCHOOL": list(
        Choice.get_choices_for(
            "rh",
            "DEGREE_EDUCATION",
            query_dict={"cvalue__in": [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 18]},
        )
    ),
    "GENRE": SEXO_CHOICES,
    "YESNO": SIM_NAO,
    "ADDRESS_TYPE": list(Choice.get_choices_for("rh", "TYPE_ADDRESS")),
    "PUBLIC_PLACE_TYPE": list(
        Choice.get_choices_for(
            "rh", "TYPE_STREET", query_dict={"value__in": [1, 2, 3, 5, 8, 9]}
        )
    ),
    "PHONE_TYPE": list(Choice.get_choices_for("rh", "TYPE_PHONE")),
    "RACE": list(Choice.get_choices_for("rh", "TYPE_RACE")),
    "MARITAL_STATUS": list(Choice.get_choices_for("rh", "MARITAL_STATUS")),
    "CITY": list(
        City.objects.filter(estado__sigla="TO")
        .order_by("nome")
        .values_list("id", "nome")
    ),
    "ALL_CITIES": list(City.objects.all().order_by("nome").values_list("id", "nome")),
    "SKIN_COLOR": RACA_COR_CHOICES,
    "EYE_COLOR": (
        ("", "Não Informado"),
        ("Azul", "Azul"),
        ("Castanho claro", "Castanho claro"),
        ("Castanho escuro", "Castanho escuro"),
        ("Cinzentos", "Cinzentos"),
        ("Pretos", "Pretos"),
        ("Verdes", "Verdes"),
        ("Desiguais na cor", "Desiguais na cor"),
        ("Outros", "Outros"),
    ),
    "HAIR_TYPE": (
        ("Calvo", "Calvo"),
        ("Encaracolado", "Encaracolado"),
        ("Liso", "Liso"),
        ("Ondulado", "Ondulado"),
        ("Raspado", "Raspado"),
    ),
    "HAIR_COLOR": (
        ("Castanho claro", "Castanho claro"),
        ("Castanho escuro", "Castanho escuro"),
        ("Grisalho", "Grisalho"),
        ("Loiro", "Loiro"),
        ("Preto", "Preto"),
        ("Ruivo", "Ruivo"),
    ),
    "STATE": list(
        State.objects.filter(pais__pk=1).order_by("nome").values_list("id", "sigla")
    ),
}


class BaseForm(forms.Form):
    channel_slug = forms.CharField()
    subject = forms.ChoiceField(choices=CHOICES["SUBJECT"])
    text = forms.CharField()


class AnonymousProtocolForm(BaseForm):
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
    email = forms.EmailField(required=False)


class LegalPersonProtocolForm(BasePersonForm):
    cnpj = BRCNPJField()
    subject_detail = forms.CharField()
    document_number = forms.CharField()


class CitizenProtocolForm(BasePersonForm):
    cpf = BRCPFField()
    subject_detail = forms.CharField()
    document_number = forms.CharField()
    genre = forms.ChoiceField(choices=CHOICES["GENRE"])
    school = forms.ChoiceField(choices=CHOICES["SCHOOL"])
    live_in_referenced_city = forms.ChoiceField(
        choices=CHOICES["YESNO"], required=False
    )
    marital_status = forms.ChoiceField(
        choices=CHOICES["MARITAL_STATUS"], required=False
    )
    race = forms.ChoiceField(choices=CHOICES["RACE"], required=False)
    referenced_city = forms.ModelChoiceField(queryset=City.objects.all())


class BaseCertificateForm(forms.Form):
    channel_slug = forms.CharField()
    subject = forms.CharField()
    name = forms.CharField()
    email = forms.EmailField(required=False)


class CitizenCertificateForm(BaseCertificateForm):
    cpf = BRCPFField()


class LegalPersonCertificateForm(BaseCertificateForm):
    cnpj = BRCNPJField()


class PLIDBaseForm(forms.Form):
    channel_slug = forms.CharField()
    subject = forms.CharField()


class PLIDAddressForm(forms.Form):
    public_place = forms.CharField(required=False)
    number = forms.CharField(required=False)
    extra = forms.CharField(required=False)
    zipcode = BRZipCodeField(required=False)
    neighborhood = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.ModelChoiceField(queryset=State.objects.all())


class PLIDBusinessAddressForm(forms.Form):
    baf_public_place = forms.CharField(required=False)
    baf_number = forms.CharField(required=False)
    baf_extra = forms.CharField(required=False)
    baf_zipcode = BRZipCodeField(required=False)
    baf_neighborhood = forms.CharField(required=False)
    baf_city = forms.CharField(required=False)
    baf_state = forms.ModelChoiceField(queryset=State.objects.all())


class PLIDOccorrenceDataForm(PLIDAddressForm):
    police_report_number = forms.CharField()
    registration_office = forms.CharField()
    occurrence_registration_date = forms.DateField(
        required=False, input_formats=["%Y-%m-%d"]
    )
    disappearance_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    disappearance_circumstances = forms.CharField(required=False)


class PLIDVictimQualificationForm(PLIDAddressForm, PLIDBusinessAddressForm):
    name = forms.CharField()
    birth_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    genre = forms.ChoiceField(choices=CHOICES["GENRE"])
    rg = forms.CharField(required=False)
    issuing_agency = forms.CharField(required=False)
    cpf = BRCPFField(required=False)
    mother_name = forms.CharField(required=False)
    father_name = forms.CharField(required=False)


class PLIDVictimCharacteristicsForm(forms.Form):
    skin_color = forms.ChoiceField(choices=CHOICES["SKIN_COLOR"], required=False)
    eye_color = forms.ChoiceField(choices=CHOICES["EYE_COLOR"], required=False)
    height = forms.CharField(required=False)
    particular_signs = forms.CharField(required=False)
    hair_type = forms.ChoiceField(choices=CHOICES["HAIR_TYPE"], required=False)
    hair_color = forms.ChoiceField(choices=CHOICES["HAIR_COLOR"], required=False)
    clothes = forms.CharField(required=False)
    objects = forms.CharField(required=False)


class PLIDCommunicatorQualificationForm(PLIDAddressForm, PLIDBusinessAddressForm):
    name = forms.CharField()
    email = forms.EmailField()
    birth_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    genre = forms.ChoiceField(choices=CHOICES["GENRE"])
    phone = forms.CharField(required=False)
    rg = forms.CharField(required=False)
    issuing_agency = forms.CharField(required=False)
    cpf = BRCPFField()
    kinship = forms.CharField()
    mother_name = forms.CharField()
    father_name = forms.CharField()


class LGPDCitizenProtocolForm(BaseForm):
    cpf = BRCPFField()
    name = forms.CharField()
    social_name = forms.CharField(required=False)
    birth_date = forms.DateField(input_formats=["%Y-%m-%d"])
    phone_number = forms.CharField()
    email = forms.EmailField()
