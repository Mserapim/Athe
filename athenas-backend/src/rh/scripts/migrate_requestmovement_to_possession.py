# -*- coding: utf-8 -*-
"""
    Este script migra MovimentacaoRequisicao para RequestMove.
"""

import os

import django
from dateutil.relativedelta import relativedelta

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.cif import cif_signal
from rh.dayoff.signals import departure
from rh.estagio import receivers
from rh.models import (
    EncargoFinanceiro,
    MovimentacaoDesligamento,
    MovimentacaoRequisicao,
    PeriodoRequisicao,
    RequestMove,
    Servidor,
    ServidorLotacao,
)
from rh.profile.models import JobProfile
from rh.signals import (
    account_integration_activity_declaration,
    account_integration_employee,
    account_integration_workplace,
    cache,
    lotacao,
)

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script migra MovimentacaoRequisicao para RequestMove.

    """
    )
    MovimentacaoDesligamento.run_termination_process = lambda x: True
    ServidorLotacao.finish_workplace_from_fire = lambda x: True
    account_integration_employee.account_integration_employee_changes = (
        lambda sender, instance, *args, **kwargs: True
    )
    account_integration_workplace.account_integration_workplace_changes = (
        lambda sender, instance, *args, **kwargs: True
    )
    account_integration_activity_declaration.account_integration_activity_declaration_changes = (
        lambda sender, instance, *args, **kwargs: True
    )
    lotacao.atualizar_ativo = lambda sender, instance, *args, **kwargs: True
    cif_signal.signals_cif_movimentacao_posse = (
        lambda sender, instance, *args, **kwargs: True
    )
    departure.update_periods_dayoff = lambda sender, instance, *args, **kwargs: True
    receivers.signals_estagio_movimentacao_posse = (
        lambda sender, instance, *args, **kwargs: True
    )
    receivers.signals_estagio_movimentacao_desligamento = (
        lambda sender, instance, *args, **kwargs: True
    )
    JobProfile.signal_save_employee_location = (
        lambda sender, instance, *args, **kwargs: True
    )
    RequestMove.create_first_period = lambda x: True

    def _possession_fire_migrate(req):
        employee = req.servidor
        exercise_date = req.data_inicio
        print(employee, req.pk, req.posse_origem)
        termination_date = None
        if req.posse_origem and req.posse_origem.data_desligamento:
            termination_date = req.posse_origem.data_desligamento + relativedelta(
                days=-1
            )
        elif not employee.is_ativo:
            termination_date = employee.last_day_worked
        print(
            f"{employee.type_by_possession} | {employee} | {exercise_date} | {termination_date}"
        )
        defaults = {}
        _possession = None
        try:
            defaults.update(
                {
                    "job_position_origin": (
                        f"{req.posse_origem.quadro.cargo}" if req.posse_origem else None
                    ),
                    "possession_origin_date": (
                        req.posse_origem.data_posse if req.posse_origem else None
                    ),
                    "publicacao_movimentacao": req.publicacao_movimentacao,
                    "organ_origin": req.orgao_origem,
                    "possession_origin": req.posse_origem,
                    "onus": req.onus,
                    "category": req.category,
                    "quadro": req.posse_origem.quadro if req.posse_origem else None,
                }
            )
            _possession, _possession_created = RequestMove.objects.update_or_create(
                servidor=employee, data_exercicio=exercise_date, defaults=defaults
            )
            enc_req = EncargoFinanceiro.objects.filter(requisicao=req.pk)
            per_req = PeriodoRequisicao.objects.filter(requisicao=req.pk)
            enc_req.update(request_move=_possession.pk)
            per_req.update(request_move=_possession.pk)
            if termination_date:
                enc_req.exclude(data_fim__lt=termination_date).update(
                    data_fim=termination_date
                )
                per_req.exclude(data_fim__lt=termination_date).update(
                    data_fim=termination_date
                )
            _possession.update_request_move()
        except Exception as err:
            print(err)
            print(
                f"{employee.type_by_possession} | {employee} | {exercise_date} | {termination_date}"
            )
        # finally:
        #     if termination_date and _possession:
        #         defaults = {
        #             'tipo_desligamento': 21,  # FIM TSVE
        #             'opcao': 2,  # OFÍCIO
        #             'data_desligamento': termination_date + relativedelta(days=1)
        #         }
        #         try:
        #             _fired_obj, _fired_created = MovimentacaoDesligamento.objects.get_or_create(
        #                 servidor=employee, movimentacao_posse=_possession, defaults=defaults)
        #             # print(_fired_obj, _fired_created)
        #         except Exception as err:
        #             print(err)
        #             print(employee.type_by_possession, employee, exercise_date, termination_date)

    query = MovimentacaoRequisicao.objects.filter()  # servidor__matricula=112178551)
    total = query.count()
    count = 0
    for mr in query:
        _possession_fire_migrate(mr)
        count += 1
        print(f"{count} of {total}")


if __name__ == "__main__":
    run()
