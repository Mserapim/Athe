# -*- coding:utf-8 -*-

from django import forms


class UserCheckForm(forms.Form):
    username = forms.CharField()


class PasswordCheckForm(forms.Form):
    new_password = forms.CharField()
    password_confirmation = forms.CharField()


class ResetPasswordForm(UserCheckForm, PasswordCheckForm):
    key = forms.CharField()


class ChangePasswordForm(UserCheckForm, PasswordCheckForm):
    current_password = forms.CharField()
