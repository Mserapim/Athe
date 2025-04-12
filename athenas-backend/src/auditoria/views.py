# -*- coding: utf-8 -*-
from contrib import extjs
from django import forms
from auditoria import models


class ADTLineLog(extjs.ExtViewOnlyCrud):

    titles = {
        "PANEL": "Linhas de Auditoria",
        "LIST": "Linhas de Auditoria",
        "EDIT": "Visualizar",
    }

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.LineLog
