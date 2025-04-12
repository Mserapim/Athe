# -*- coding:utf-8 -*-

from django import forms
from judicial.models import OutCourtLawsuit
from rh.models import Pessoa


class EntryForm(forms.Form):
    subject = forms.CharField()
    doc_type = forms.IntegerField()
    story = forms.CharField()
    workplace = forms.IntegerField(required=False)


class ManifestationSaveForm(forms.Form):
    id = forms.IntegerField()
    content = forms.CharField()


class ManifestationAttachFile(forms.Form):
    manifest = forms.IntegerField(required=False)
    title = forms.CharField(required=False)
    upload = forms.FileField(required=False)


class ManifestationForm(ManifestationSaveForm, ManifestationAttachFile):
    pass


class PetitionForm(forms.Form):
    lawsuit = forms.ModelChoiceField(
        queryset=OutCourtLawsuit.objects.all(),
        to_field_name="cache_number",
        error_messages={
            "invalid_choice": "O procedimento que você informou não existe, confirme se o número do procedimento está correto."
        },
    )

    as_representative_of = forms.ModelChoiceField(
        required=False,
        queryset=Pessoa.objects.all(),
        to_field_name="pessoafisica__cpf",
        error_messages={
            "invalid_choice": "Não existe nenhuma pessoa com essa identificação. Verifique o numero de indentificação do representado."
        },
    )
    request = forms.CharField()
