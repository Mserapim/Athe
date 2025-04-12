# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from rh.gfp.models import (
    BankingEmployeeTypePayroll,
    DadoBancarioServidorFolha,
    FolhaTipo,
    Evento,
)
from rh.models import Pessoa
from contrib.middleware import set_current_user


def populate_databankingpersontypepayroll(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    # DadoBancarioServidorFolha = apps.get_model("gfp", "DadoBancarioServidorFolha")
    # FolhaTipo = apps.get_model("gfp", "FolhaTipo")
    # Pessoa = apps.get_model("rh", "Pessoa")
    # Evento = apps.get_model("gfp", "Evento")
    # PaycheckDifference = apps.get_model("gfp", "PaycheckDifference")
    set_current_user("athenas")

    BankingEmployeeTypePayroll.objects.all().delete()
    for p in Pessoa.objects.exclude(dadosbancarios=None).order_by("nome"):
        print(p.pk, p)
        for tf in FolhaTipo.objects.all():
            dbp = (
                DadoBancarioServidorFolha.objects.filter(
                    dado_bancario_pessoa__pessoa=p, tipo_folha=tf
                )
                .order_by("-data_inicio_vigencia")
                .first()
            )
            if dbp:
                print(">> %s - %s" % (tf, dbp.dado_bancario_pessoa))
                detp = BankingEmployeeTypePayroll.objects.create(
                    person=p,
                    type_of_payroll=tf,
                    banking_person=dbp.dado_bancario_pessoa,
                )
    Evento.objects.filter(genre_event=None).update(active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0020_auto_20160524_1220"),
    ]

    operations = [
        migrations.RunPython(populate_databankingpersontypepayroll),
    ]
