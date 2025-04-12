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
    BKP_MovimentacaoPosseReq,
    BKP_MovimentacaoPosseReq,
    EncargoFinanceiro,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
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
        counter = 0
        employee = req.servidor
        exercise_date = req.data_inicio
        print(employee, req.pk, req.posse_origem)
        termination_date = None

        if not req.posse_origem:
            try:
                req.posse_origem = MovimentacaoPosse.objects.get(
                    servidor=employee,
                    publicacao_movimentacao=req.publicacao_movimentacao,
                    tipo_movcarreira="NOMEACAO",
                )
                if req.posse_origem.data_exercicio != req.data_inicio:
                    exercise_date = req.posse_origem.data_exercicio

            except Exception as e:
                print(">>>>>>>>>>>>>>")
                print(e)
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
                    "data_desligamento": termination_date if termination_date else None,
                    "category": (
                        req.category
                        if (req.category and req.category in [301, 305])
                        else 301
                    ),  # Servidor Público Titular de Cargo Efetivo, Magistrado, Ministro de Tribunal de Contas, Conselheiro de Tribunal de Contas e Membro do Ministério Público
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
                print(f"desligado {employee}")
                enc_req.exclude(data_fim__lt=termination_date).update(
                    data_fim=termination_date
                )
                per_req.exclude(data_fim__lt=termination_date).update(
                    data_fim=termination_date
                )

            _possession.update_request_move(termination_date)

            print(f"{_possession} - {_possession_created}")

        except Exception as err:
            print(err)
            print(
                f"{employee.type_by_possession} | {employee} | {exercise_date} | {termination_date}"
            )
        if _possession:

            mp = MovimentacaoPosse.objects.filter(
                servidor=employee,
                data_exercicio=exercise_date,
                publicacao_movimentacao=req.publicacao_movimentacao,
            )

            for posse in mp:

                if posse.tipo_movcarreira == "NOMEACAO":
                    counter += 1
                    bkp = None

                    try:
                        kwargs = posse.__dict__
                        kwargs.pop("_initial_fields")
                        kwargs.pop("audit_fields")
                        kwargs.pop("_state")
                        bkp = BKP_MovimentacaoPosseReq(**kwargs)
                        bkp.save_base()

                    except Exception as e:
                        print(
                            "Erro ao fazer Backup da Movimentação Posse em BKP_MovimentacaoPosse"
                        )
                        print(e)

                    if bkp:
                        try:
                            posse = MovimentacaoPosse.objects.get(
                                pk=posse.pk, tipo_movcarreira="NOMEACAO"
                            )
                            if _possession.possession_origin == posse:
                                _possession.possession_origin = None
                                _possession.save()

                            MovimentacaoRequisicao.objects.filter(
                                posse_origem=posse
                            ).update(posse_origem=_possession)
                            _change_exercise(_possession, req)
                            # posse.delete()

                        except Exception as e:
                            print(e)
        employee.save()
        return counter

    def _change_exercise(
        request_move: RequestMove, req: MovimentacaoRequisicao
    ) -> None:
        """
        Atualiza o model ServidorLotacao para que a movimentação posse seja atualizada para o Provimento de Requisição.
        """
        try:
            sl = ServidorLotacao.objects.filter(
                publicacao=req.publicacao_movimentacao, servidor=request_move.servidor
            ).update(movimentacao_posse=request_move)

        except Exception as err:
            print(err)

    #### ----- #### ---- ### ---- #### ---- ### ---- #### ---- ####
    # 6898 : TATIANE GARCIA FERREIRA 2616247 None
    # REQ | 6878 : KAMMYLLA PEREIRA RODRIGUES | 2015-01-27 | None
    # Uelinton - 515312345
    # 6898 Tatiane Garcia
    # 7185 Andre Monteiro

    query = MovimentacaoRequisicao.objects.exclude(servidor__type_by_possession="EXT")
    total = query.count()
    count = 0
    counter = 0
    for mr in query:

        counter += _possession_fire_migrate(mr)

    print(f"contador : {counter}")
    print(f"total de bkp {BKP_MovimentacaoPosseReq.objects.count()}")
    print(total)


if __name__ == "__main__":
    run()
