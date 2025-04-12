# -*- coding: utf-8 -*-
"""
    Este script criar os servidores beneficiários a partir de uma folha definida.
"""

import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from django.db.models import F
from rh.gfp.models import FolhaEvento
from logging import getLogger
from contrib.middleware import set_current_user

log = getLogger(__name__)


set_current_user("athenas")


def update_old_entries():
    print("#" * 100)
    print("Script de Atualização de eventos.")
    print("#" * 100)
    query = FolhaEvento.objects.filter(
        evento__genre_event__isnull=True,
    )
    query_e = query.exclude(
        diff_employer_contribution_provisioned=0, diff_value_provisioned=0
    )
    response = input(
        f"{query_e.count()} eventos antigos com alteração. Deseja continuar? (y/N)"
    )
    if response in ("y", "Y"):
        query = query.filter(
            diff_employer_contribution_provisioned=0, diff_value_provisioned=0
        )
        ups = query.filter(evento__tipo="P").update(
            value=F("valor"),
            employer_contribution=F("employer_contribution"),
            correct_value=F("valor"),
            correct_employer_contribution=F("patronal"),
            correct_contribution_base=F("base_previdencia"),
            correct_qnt=F("qnt"),
            correct_qnt_max=F("qnt_max"),
            correct_pct=F("pct"),
            correct_base_value=F("valor_base"),
            correct_valor=F("valor"),
            correct_patronal=F("patronal"),
            correct_base_previdencia=F("base_previdencia"),
        )
        print(f"Corrigindo eventos de proventos: {ups} atualizações")
        ups = query.filter(evento__tipo="D").update(
            value=-F("valor"),
            employer_contribution=F("employer_contribution"),
            correct_value=-F("valor"),
            correct_employer_contribution=F("patronal"),
            correct_contribution_base=F("base_previdencia"),
            correct_qnt=F("qnt"),
            correct_qnt_max=F("qnt_max"),
            correct_pct=F("pct"),
            correct_base_value=F("valor_base"),
            correct_valor=F("valor"),
            correct_patronal=F("patronal"),
            correct_base_previdencia=F("base_previdencia"),
        )
        print(f"Corrigindo eventos de descontos: {ups} atualizações")
        FolhaEvento.objects.filter(
            evento__genre_event__isnull=True,
            patronal__gt=0,
            employer_contribution__lt=0,
            diff_employer_contribution_provisioned=0,
        ).update(employer_contribution=-F("employer_contribution"))


if __name__ == "__main__":
    update_old_entries()
