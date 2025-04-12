# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def updatekind(apps, schema_editor):
    from rh.models import Pessoa, PessoaFisica, PessoaJuridica, AnonymousPerson, Lawyer
    from django.contrib.auth.models import User
    from contrib.middleware import set_current_user

    set_current_user(User.objects.get(username="athenas"))

    for p in Pessoa.objects.filter(
        anonymousperson__isnull=True,
        pessoajuridica__isnull=True,
        pessoafisica__isnull=True,
    ):
        p.save()

    for ap in AnonymousPerson.objects.filter():
        ap.save()

    for pj in PessoaJuridica.objects.filter():
        pj.save()

    for pf in PessoaFisica.objects.filter(lawyer__isnull=True):
        pf.save()

    for lw in Lawyer.objects.filter():
        lw.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0011_pessoa_kind"),
    ]

    operations = [migrations.RunPython(updatekind)]
