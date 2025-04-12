# -*- coding: utf-8 -*-
"""
    Este script migra MovimentacaoRequisicao para RequestMove.
"""

from datetime import datetime, date
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
    DeclaracaoAtividade,
    EncargoFinanceiro,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoRequisicao,
    PeriodoRequisicao,
    PossessionCollaborator,
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

    def create_fired_employee(data_encerramento, _possession, employee, data_exercicio):
        if data_encerramento and data_encerramento < date.today() and _possession:
            try:
                md = MovimentacaoDesligamento(
                    servidor=employee,
                    movimentacao_posse=_possession,
                    tipo_desligamento=21,
                    opcao=2,
                    data_desligamento=data_encerramento,
                    created_by_id=1,
                    modified_by_id=1,
                )

                md.save_base()
                employee.save()
            except Exception as err:
                print(err)
                print(
                    employee.type_by_possession,
                    employee,
                    data_exercicio,
                    data_encerramento,
                )

    def dec_to_collaborator(servidor):

        _klass = PossessionCollaborator
        defaults = {}
        _possession = None

        decs = DeclaracaoAtividade.objects.filter(servidor=servidor)
        for dec in decs:
            try:
                defaults.update(
                    {
                        "data_posse": dec.data_exercicio,
                        "quadro": dec.quadro,
                        "bond": False,
                    }
                )
                if dec.data_encerramento:
                    defaults.update({"data_desligamento": dec.data_encerramento})

                _possession, _possession_created = _klass.objects.get_or_create(
                    servidor=servidor, defaults=defaults
                )
                _change_exercise(_possession, dec)
            except Exception as err:
                print(err)
                print(
                    servidor.type_by_possession,
                    servidor,
                    dec.data_exercicio,
                    dec.data_encerramento,
                )
            finally:
                create_fired_employee(
                    dec.data_encerramento, _possession, servidor, dec.data_exercicio
                )

    def movposse_to_collaborator(servidor):
        _klass = PossessionCollaborator
        defaults = {}
        _possession = None
        mvs = MovimentacaoPosse.objects.filter(servidor=servidor).filter(
            tipo_movcarreira="NOMEACAO"
        )

        for mv in mvs:
            try:
                defaults.update(
                    {
                        "data_posse": mv.data_posse,
                        "quadro": mv.quadro,
                        "bond": False,
                        "publication_possession": mv.publication_possession,
                        "publication_exercise": mv.publication_possession,
                    }
                )
                if mv.data_desligamento:
                    defaults.update({"data_desligamento": mv.data_desligamento})

                _possession, _possession_created = _klass.objects.get_or_create(
                    servidor=servidor, defaults=defaults
                )
                _change_exercise(_possession, mv)
            except Exception as err:
                print(err)
                print(
                    servidor.type_by_possession,
                    servidor,
                    mv.data_exercicio,
                    mv.data_desligamento,
                )
            finally:
                create_fired_employee(
                    mv.data_desligamento, _possession, servidor, mv.data_exercicio
                )

    def movreq_to_collaborator(servidor):
        _klass = PossessionCollaborator
        defaults = {}
        _possession = None
        mrs = MovimentacaoRequisicao.objects.filter(servidor=servidor)

        for mr in mrs:
            try:
                defaults.update(
                    {
                        "data_posse": mr.data_posse,
                        "quadro": mr.quadro,
                        "bond": False,
                        "publication_possession": mr.publication_possession,
                        "publication_exercise": mr.publication_possession,
                    }
                )
                if mr.data_desligamento:
                    defaults.update({"data_desligamento": mr.data_desligamento})

                _possession, _possession_created = _klass.objects.get_or_create(
                    servidor=servidor, defaults=defaults
                )
                _change_exercise(_possession, mr)
            except Exception as err:
                print(err)
                print(
                    servidor.type_by_possession,
                    servidor,
                    mr.data_exercicio,
                    mr.data_desligamento,
                )
            finally:
                create_fired_employee(
                    mr.data_desligamento, _possession, servidor, mr.data_exercicio
                )

    def _change_exercise(request_move, req):
        """
        Atualiza o model ServidorLotacao para que a movimentação posse seja atualizada para o Provimento de Requisição.
        """
        publicacao = None

        if isinstance(req, MovimentacaoRequisicao) or isinstance(
            req, DeclaracaoAtividade
        ):
            publicacao = req.publicacao_movimentacao
        elif isinstance(req, MovimentacaoPosse):
            publicacao = req.publication_possession

        try:
            if publicacao:
                ServidorLotacao.objects.filter(
                    publicacao=publicacao, servidor=request_move.servidor
                ).update(movimentacao_posse=request_move)

        except Exception as err:
            print(err)

    query = Servidor.objects.filter(type_by_possession="EXT")
    total = query.count()
    counter = 0
    for servidor in query:
        # counter += _possession_fire_migrate(servidor)

        if DeclaracaoAtividade.objects.filter(servidor=servidor).count() > 0:
            dec_to_collaborator(servidor)
        elif (
            MovimentacaoPosse.objects.filter(servidor=servidor)
            .filter(tipo_movcarreira="NOMEACAO")
            .count()
            > 0
        ):
            movposse_to_collaborator(servidor)
        elif MovimentacaoRequisicao.objects.filter(servidor=servidor).count() > 0:
            movreq_to_collaborator(servidor)
        else:
            print("##########")
            print(
                f"O servidor {servidor} não possui DeclaracaoAtividade Movposse e MovimentacaoRequisicao"
            )

    print(f"contador : {counter}")
    print(f"total de bkp {BKP_MovimentacaoPosseReq.objects.count()}")
    print(total)


if __name__ == "__main__":
    run()
