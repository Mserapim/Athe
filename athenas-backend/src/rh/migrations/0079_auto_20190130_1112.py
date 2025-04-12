# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models

from contrib.middleware import set_current_user
from rh.models import MovimentacaoRequisicao, Servidor

set_current_user("athenas")


def update_emplyee_type_by_possesion(apps, schema_editor):
    # MovimentacaoRequisicao = apps.get_model("rh", "MovimentacaoRequisicao")
    # Servidor = apps.get_model("rh", "Servidor")

    tt = "XXX"
    ups = 0
    summary = {}

    types = []
    update_type = True
    # show_only_modified = False

    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath = os.path.join(
        BASE_DIR, "rh", "fixtures", "choices_type_by_possession.json"
    )
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
    call_command("loaddata", filepath)

    q = Servidor.objects.all()
    if types:
        q = q.filter(type_by_possession__in=types)

    for s in q.order_by("type_by_possession", "-ativo", "pessoa_fisica__nome"):
        pps = s.posses.filter().count()
        ppd = s.get_declarationactivity().count()
        ppr = MovimentacaoRequisicao.objects.filter(servidor=s).count()
        if (pps or ppd or ppr) and update_type:
            s._update_type_by_possession()

        if tt != s.type_by_possession:
            # print '>>> %s - %s' % (s.type_by_possession, s.get_type_by_possession_display())
            tt = s.type_by_possession

        if tt not in summary:
            summary[tt] = [s.get_type_by_possession_display(), 0, 0]
        summary[tt][1 if s.ativo else 2] += 1

        modified = "*" if "type_by_possession" in s.diff else ""

        if modified:
            ups += 1
            # print '%1s' % modified, s.tipo, s.type_by_possession, pps, ppr, ppd, s

    print("UPDATEDS EMPLOYEES TYPE: %d" % ups)

    print("")
    # print '>>> SUMMARY'
    print(
        "\033[1;33m%03s   %-50s   %-9s %s\033[0m"
        % (">>>", "SUMMARY", "ATIVO", "INATIVO")
    )
    t_active = t_inactive = 0
    for tt in sorted(summary):
        print(
            "%03s - %-50s   %04d       %04d"
            % (tt, summary[tt][0], summary[tt][1], summary[tt][2])
        )
        t_active += summary[tt][1]
        t_inactive += summary[tt][2]
    print(
        "\033[1;33m%03s   %-50s   %04d       %04d\033[0m"
        % (">>>", "TOTAIS: ", t_active, t_inactive)
    )


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0078_auto_20190123_1048"),
    ]

    operations = [
        migrations.AddField(
            model_name="servidor",
            name="type_by_possession",
            field=models.CharField(
                default="EFE", max_length=3, verbose_name="Tipo", blank=True
            ),
        ),
        migrations.RunPython(update_emplyee_type_by_possesion, _null_function),
    ]
