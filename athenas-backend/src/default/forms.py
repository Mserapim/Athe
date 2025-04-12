# -*- coding:utf-8 -*-

from django import forms


class LoginForm(forms.Form):
    THEME_CHOICES = (
        [0, "Tema azul"],
        [3, "Tema azul (Ampliado)"],
        [1, "Tema cinza"],
        [4, "Tema cinza (Ampliado)"],
        [2, "Tema de Alto Contraste"],
    )

    login = forms.CharField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Usuário"})
    )
    passwd = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Senha", "autocomplete": "false"}
        ),
    )
    theme = forms.ChoiceField(
        label="", choices=THEME_CHOICES, widget=forms.Select(attrs={"class": "stretch"})
    )
