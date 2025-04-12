# -.- coding: utf-8 -.-

import django
import os
import datetime

from rh.const import ACTIVE, CANCELED


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db import transaction
from contrib.middleware import set_current_user
from rh.utils import dump_instance_fields_dict
from rh.models import (
    Lotacao,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    Replacement,
)
from rh.afastamento.models import AfastamentoOutroOrgao, ACTIVE


AfastamentoOutroOrgao.validate_employee_active = lambda x: True
AfastamentoOutroOrgao.validate_data_prevista = lambda x: True


set_current_user("athenas")


def create_copy(dep, fields_update={}):
    new_kwargs = dump_instance_fields_dict(dep)

    pop = [
        "afastamento_ptr",
        "movimentacaopessoal_ptr",
        "baselicencaafastamento_ptr",
        "status_change_date",
        "estado",
        "alteracao",
    ]
    for key in pop:
        if key in list(new_kwargs.keys()):
            new_kwargs.pop(key)

    for key in fields_update:
        new_kwargs.update({key: fields_update.get(key)})

    # print(new_kwargs)
    print(new_kwargs.get("data_inicio"))
    print(new_kwargs.get("data_prevista"))
    print(new_kwargs.get("data_fim"))
    return AfastamentoOutroOrgao.objects.create(**new_kwargs)


def run():
    end_date_2021 = datetime.datetime(2021, 12, 31).date()
    start_date = datetime.datetime(2022, 1, 1).date()
    end_date = None
    pks = []
    pks_news = []
    pks_problems = []
    for dep in (
        AfastamentoOutroOrgao.objects.filter(
            # servidor__matricula__in=[89908, 88708],
            # servidor__tipo__in=['S', 'M']
            servidor__tipo__in=["S"]
        )
        .filter(data_inicio__lt=start_date, data_fim__gte=start_date)
        .exclude(estado=CANCELED)
    ):
        pks.append(dep.pk)
        print(dep)
        if dep.substituicao.exists():
            print("possui subsituição")
        try:
            alteracao = dep.alteracao
            alteracao_fim = dep.data_fim

            if not dep.alteracao and dep.prorrogacao.exists():
                prg = dep.prorrogacao.latest("data_inicio")
                end_date = prg.data_fim
                if prg.data_inicio < start_date:
                    prg.data_fim = end_date_2021
                    prg.save()
                else:
                    prg.delete()
            else:
                if dep.prorrogacao.exists():
                    prg = dep.prorrogacao.latest("data_inicio")
                    end_date = prg.data_fim
                else:
                    end_date = dep.data_prevista
                AfastamentoOutroOrgao.objects.filter(pk=dep.pk).update(
                    data_prevista=end_date_2021, data_fim=end_date_2021
                )
                dep = AfastamentoOutroOrgao.objects.get(pk=dep.pk)
                dep.save()

            dep.refresh_from_db()
            fields_update = {
                "data_inicio": start_date,
                "data_prevista": end_date,
                "data_fim": end_date,
                "id": None,
                "pk": None,
            }
            dep_new = create_copy(dep, fields_update=fields_update)
            if alteracao:
                dep_new.alteracao = alteracao
                dep_new.data_fim = alteracao_fim
                dep_new.save()
            pks_news.append(dep_new.pk)
            print(f"{dep}")
            print(f"dep     {dep.data_inicio} {dep.data_prevista} {dep.data_fim}")
            print(f"{dep_new}")
            print(
                f"dep_new {dep_new.data_inicio} {dep_new.data_prevista} {dep_new.data_fim}"
            )
            print("==========================")
        except Exception as err:
            print(err)
            pks_problems.append(dep.pk)

    print(f"pks_problems: {pks_problems}")


if __name__ == "__main__":
    run()
