from django.forms import Form, CharField


class ParecerForm(Form):
    tipo = CharField()
    inscricao = CharField()
    recurso = CharField()
    parecer = CharField(required=False)
