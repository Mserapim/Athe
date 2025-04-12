#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.forms import *
from contrib.controller import DefaultController
from ged.models import Arquivo
from contrib.decorator import is_public
from contrib.utils import getLogger, person_from_user

log = getLogger(__name__)


def is_file_public(_file):

    if _file.acesso != 3:
        return False

    for attach in _file.anexo_set.all():
        for m in attach.movimentacao.all():
            if m.protocolo.sigiloso:
                return False

    return True


class HashForm(Form):
    part1 = CharField(
        error_messages={"required": "Códgio inválido"},
        max_length=8,
        min_length=8,
        widget=TextInput(attrs={"class": "small3"}),
    )
    part2 = CharField(
        error_messages={"required": "Códgio inválido"},
        max_length=8,
        min_length=8,
        widget=TextInput(attrs={"class": "small3"}),
    )
    part3 = CharField(
        error_messages={"required": "Códgio inválido"},
        max_length=8,
        min_length=8,
        widget=TextInput(attrs={"class": "small3"}),
    )
    part4 = CharField(
        error_messages={"required": "Códgio inválido"},
        max_length=8,
        min_length=8,
        widget=TextInput(attrs={"class": "small3 omega"}),
    )


class Docsverify(DefaultController):

    @is_public()
    def index(self, args=[]):
        return self.render_template("docsverify/index.html")

    @is_public()
    def verify(self, args=[]):
        pars = {}
        form = HashForm()
        if self.request.POST:
            form = HashForm(self.request.POST)
            if form.is_valid():
                f = form.cleaned_data
                filehash = "%s%s%s%s" % (f["part1"], f["part2"], f["part3"], f["part4"])

                _file = Arquivo.objects.filter(file=filehash.lower())

                if _file:
                    pars["creator"] = person_from_user(_file[0].user).nome
                    pars["created"] = _file[0].created
                    pars["url"] = _file[0].permalink()
                    pars["filename"] = _file[0].filename
                    pars["publico"] = is_file_public(_file[0])

                    return self.render_template("docsverify/doc-found.html", pars)

                pars["msg"] = "Nenhum documento encontrado."

        pars["f"] = form

        return self.render_template("docsverify/verify.html", pars)
