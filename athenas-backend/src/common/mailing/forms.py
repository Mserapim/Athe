# -*- coding:utf-8 -*-
from django import forms
from common.mailing import models


class CommonForm(forms.Form):
    id = forms.IntegerField(required=False)
    name = forms.CharField(max_length=150)


class ProfileForm(CommonForm):
    printer_name = forms.CharField()


class DeleteProfileUserForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=models.Profile.objects.all())
    user = forms.ModelChoiceField(queryset=models.User.objects.all())


class ProfileUserForm(DeleteProfileUserForm):
    permission = forms.CharField(widget=forms.Select(choices=models.PERMISSION_CHOICES))


class GroupForm(CommonForm):
    profile = forms.ModelChoiceField(queryset=models.Profile.objects.all())


class TreatmentForm(CommonForm):
    pass


class CompanyForm(CommonForm):
    pass


class PositionForm(CommonForm):
    pass


class StateForm(CommonForm):
    UF = forms.CharField(max_length=2)


class CityForm(CommonForm):
    state = forms.ModelChoiceField(queryset=models.State.objects.all())


class PrintForm(forms.Form):
    profile = forms.IntegerField()
    group = forms.IntegerField(required=False)
    selected = forms.CharField(required=False)
    positions = forms.CharField()
    type_paper = forms.IntegerField()


class ContactForm(forms.Form):
    id = forms.IntegerField(required=False)
    profile = forms.ModelChoiceField(queryset=models.Profile.objects.all())
    name = forms.CharField(max_length=150)
    treatment = forms.ModelChoiceField(queryset=models.Treatment.objects.all())
    company = forms.ModelChoiceField(queryset=models.Company.objects.all())
    position = forms.ModelChoiceField(queryset=models.Position.objects.all())
    locality = forms.CharField(max_length=150)
    neighborhood = forms.CharField(max_length=100, required=False)
    code = forms.CharField(max_length=10)
    city = forms.ModelChoiceField(queryset=models.City.objects.all())
    normal = forms.CharField(max_length=15, required=False)
    mobile = forms.CharField(max_length=15, required=False)
    fax = forms.CharField(max_length=15, required=False)
    group = forms.ModelChoiceField(required=False, queryset=models.Group.objects.all())
