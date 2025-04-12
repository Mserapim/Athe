from django import forms
from standard.questionario import models


class QuestionarioForm(forms.ModelForm):

    class Meta:
        model = models.Questionario
        exclude = ["criado_em", "modificado_em", "unico"]
