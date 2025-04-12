# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def population(apps, schema_editor):
    from rh.models import Servidor, MovimentacaoPosse
    from rh.socialsecurity.models import EmploymentBond, RetirementPrevision
    from contrib.middleware import set_current_user, User
    from dateutil.relativedelta import relativedelta

    set_current_user(User.objects.get(username="athenas"))

    for sa in Servidor.objects.filter(ativo=True):
        if sa.is_efetivo:
            rp, created = RetirementPrevision.objects.get_or_create(
                natural_person=sa.pessoa_fisica
            )
            for mp in MovimentacaoPosse.objects.filter(
                servidor__pessoa_fisica=sa.pessoa_fisica,
                quadro__cargo__tipo_lei_cargo="EF",
            ):
                if not mp.data_desligamento or (
                    mp.data_exercicio < mp.data_desligamento
                ):
                    eb, created = EmploymentBond.objects.get_or_create(
                        employer="%s" % mp.quadro.cargo.unidade_administrativa,
                        pension_system=sa.regime_previdenciario,
                        begin_date=mp.data_exercicio,
                        retirement_prevision=rp,
                        possession=mp,
                        public_employee=True,
                        with_pgj=True,
                    )
                    eb.end_date = (
                        (mp.data_desligamento + relativedelta(days=-1))
                        if mp.data_desligamento
                        else None
                    )
                    eb.save()
            rp.save()


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0001_initial"),
    ]

    operations = [migrations.RunPython(population)]
