# -*- coding: utf-8 -*-
from django.db import migrations

from rh.gfp.models import ContraChequeHistorico


def up(apps, schema_editor):
    print("Running forward...")

    for cc_hist in ContraChequeHistorico.objects.all():
        if cc_hist.contracheque:
            ContraChequeHistorico.objects.filter(pk=cc_hist.pk).update(
                contracheque_ref_id=cc_hist.contracheque.pk,
                servidor_ref_id=cc_hist.contracheque.servidor.pk,
                contracheque_ref_ano=cc_hist.contracheque.folha.periodo.ano,
                contracheque_ref_mes=cc_hist.contracheque.folha.periodo.mes,
            )


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("gfp", "0123_auto_20230927_1319")]

    operations = [
        migrations.RunPython(up, down),
    ]
