# -*- coding: utf-8 -*-
"""
    Este script migra Colaboradores para PossessionCollaborator e PossessionTraine.
    Este script migra Declaração de Atividade para Designação de Exercício.
"""

import os
from datetime import datetime, date

import django
from dateutil.relativedelta import relativedelta
from django.db.models.aggregates import Max, Min

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.cif import cif_signal
from rh.dayoff.signals import departure
from rh.estagio import receivers
from rh.models import (
    DeclaracaoAtividade,
    MovimentacaoDesligamento,
    PossessionCollaborator,
    PossessionTrainee,
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
        Este script migra Colaboradores para PossessionCollaborator e PossessionTraine.
        Este script migra Declaração de Atividade para Designação de Exercício."""
    )
    MovimentacaoDesligamento.run_termination_process = lambda x: True
    ServidorLotacao.finish_workplace_from_fire = lambda x: True
    PossessionTrainee.validate_vacancy_number_filled = lambda x: True
    PossessionTrainee.validate = lambda x: True
    PossessionCollaborator.validate_vacancy_number_filled = lambda x: True
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

    def _possession_fire_migrate(employee, quadro, data_exercicio, data_encerramento):
        log.debug(
            f"{employee.type_by_possession} | {employee} | {data_exercicio} | {data_encerramento}"
        )
        defaults = {}
        _klass = PossessionCollaborator
        if type_of == "E":
            _klass = PossessionTrainee
            if hasattr(employee, "trainee"):
                employee = employee.trainee
                defaults.update(
                    {
                        "employee_supervisor": employee.employee_supervisor,
                        "educational_institution": employee.educational_institution,
                        "integration_agent": employee.integration_agent,
                        "nature": employee.nature,
                        "level": employee.level,
                        "occupation_area": employee.occupation_area,
                        "insurance_number": employee.insurance_number,
                        "value": employee.value,
                    }
                )
        _possession = None
        try:
            defaults.update(
                {"data_posse": data_exercicio, "quadro": quadro, "bond": False}
            )
            if data_encerramento:
                defaults.update({"data_desligamento": data_encerramento})
            _possession, _possession_created = _klass.objects.get_or_create(
                servidor=employee, defaults=defaults
            )
        except Exception as err:
            print(err)
            print(
                employee.type_by_possession, employee, data_exercicio, data_encerramento
            )
        finally:
            if data_encerramento and data_encerramento < date.today() and _possession:
                defaults = {
                    "tipo_desligamento": 21,  # FIM TSVE
                    "opcao": 2,  # OFÍCIO
                    "data_desligamento": data_encerramento,
                }
                try:
                    md = MovimentacaoDesligamento(
                        # servidor=employee, movimentacao_posse=_possession, defaults=defaults)
                        servidor=employee,
                        movimentacao_posse=_possession,
                        tipo_desligamento=21,
                        opcao=2,
                        data_desligamento=data_encerramento,
                        created_by_id=1,
                        modified_by_id=1,
                    )
                    # print(_fired_obj)
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

    def _create_exercise(da, data_exercicio, data_encerramento):
        # for da in query_da:
        print(da)
        # data_exercicio = da.data_exercicio
        # data_encerramento = da.data_encerramento
        if data_encerramento and data_exercicio > data_encerramento:
            print("Erro data de encerramento menor que data de exercício")
            print(da)
            # data_exercicio = data_encerramento - relativedelta(days=1)
            data_exercicio = data_encerramento
        defaults = {
            # 'data_vigencia_inicio': data_exercicio,
            # 'data_vigencia_fim': data_encerramento,
            "designacao": True,
            "main_schedule_date": da.main_schedule_date,
            "main": da.main,
        }
        try:
            _obj, _created = ServidorLotacao.objects.get_or_create(
                servidor=da.servidor,
                lotacao=da.lotacao,
                data_vigencia_inicio=data_exercicio,
                data_vigencia_fim=data_encerramento,
                defaults=defaults,
            )
            # print(_obj, _created)
        except Exception as err:
            print(err)
            print(da)

    query = Servidor.objects.filter(  # matricula=3780)
        pk__in=DeclaracaoAtividade.objects.filter().values("servidor")
    ).exclude(type_by_possession="EXT")

    total = query.count()
    count = 0
    for employee in query:
        type_of = employee.tipo
        for da in DeclaracaoAtividade.objects.filter(servidor=employee):
            quadro = da.quadro
            # qda = DeclaracaoAtividade.objects.filter(servidor=employee, quadro=quadro)
            # data_exercicio = da.aggregate(data_exercicio=Min('data_exercicio'))['data_exercicio']
            data_exercicio = da.data_exercicio
            # data_encerramento = da.aggregate(data_encerramento=Max('data_encerramento'))['data_encerramento']
            data_encerramento = da.data_encerramento
            _possession_fire_migrate(
                employee, quadro, data_exercicio, data_encerramento
            )
            _create_exercise(da, data_exercicio, data_encerramento)
        count += 1
        print(f"{count} of {total}")


#

if __name__ == "__main__":
    run()
