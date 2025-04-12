from django.conf import settings
from django import forms


class PollForm(forms.Form):
    id = forms.IntegerField(required=False, min_value=1)
    title = forms.CharField(max_length=300)
    key = forms.CharField(max_length=16)
    confirm_key = forms.CharField(max_length=16)
    max_of_choices = forms.IntegerField(min_value=1)
    target = forms.IntegerField(min_value=1)


class ChoiceForm(forms.Form):
    id = forms.IntegerField(required=False, min_value=1)
    choice = forms.CharField(max_length=300)
    poll = forms.IntegerField(min_value=1)


class DeleteForm(forms.Form):
    id = forms.IntegerField(min_value=1)
    poll = forms.IntegerField(min_value=1, required=False)
    model = forms.CharField()


class PublicationForm(forms.Form):
    poll = forms.IntegerField(min_value=1)
    start = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS)
    end = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS)


class VoteForm(forms.Form):
    poll = forms.IntegerField(min_value=1)
    votes = forms.CharField(required=False)
    password = forms.CharField()


class CountForm(forms.Form):
    poll = forms.IntegerField(min_value=1)
    key = forms.CharField(max_length=16)


class BlockUserForm(forms.Form):
    poll = forms.IntegerField(min_value=1)
    user = forms.IntegerField(min_value=1)
