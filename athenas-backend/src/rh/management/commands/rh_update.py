# -*- coding: utf-8 -*-

from datetime import date, datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import (
    CargaHoraria,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    PossessionTrainee,
    PossessionResident,
)

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--movposse",
            action="store_true",
            dest="movposse",
            help="Realiza procedimentos relacionados à MovimentacaoPosse.",
        )
        parser.add_argument(
            "-t",
            "--terminatetrainee",
            action="store_true",
            dest="terminatetrainee",
            help="Comando para desligar estagiários cuja data de encerramento seja menor que hoje.",
        )
        parser.add_argument(
            "-r",
            "--terminateresident",
            action="store_true",
            dest="terminateresident",
            help="Comando para desligar residentes cuja data de encerramento seja menor que hoje.",
        )
        parser.add_argument(
            "-d",
            "--movdesligamento",
            action="store_true",
            dest="movdesligamento",
            help="Realiza procedimentos relacionados à MovimentacaoDesligamento.",
        )
        parser.add_argument(
            "-w",
            "--actworkload",
            action="store_true",
            dest="actworkload",
            help="Comando para ativar Carga Horária com data início igual a data de hoje",
        )
        parser.add_argument(
            "-i",
            "--inaworkload",
            action="store_true",
            dest="inaworkload",
            help="Comando para inativar Carga Horária com data fim menor que a data de hoje",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        if options["movposse"]:
            self.set_user_to_job("job_rh_update_atualizar_movimentacao_posse")
            self.atualizar_movimentacao_posse()
        if options["terminatetrainee"]:
            self.set_user_to_job("job_rh_update_cmd_terminate_trainee")
            self.cmd_terminate_trainee()
        if options["terminateresident"]:
            self.set_user_to_job("job_rh_update_cmd_terminate_resident")
            self.cmd_terminate_resident()
        if options["movdesligamento"]:
            self.set_user_to_job("job_rh_update_cmd_termination_process")
            self.cmd_termination_process()
        if options["actworkload"]:
            self.set_user_to_job("job_rh_update_cmd_activate_workload_by_date")
            self.cmd_activate_workload_by_date()
        if options["inaworkload"]:
            self.set_user_to_job("job_rh_update_cmd_inactivate_workload_by_date")
            self.cmd_inactivate_workload_by_date()

    def atualizar_movimentacao_posse(self):
        log.info(
            "COMANDO -> atualizar_movimentacao_posse(MovimentacaoPosse.cmd_atualizar_cache_ativo)"
        )
        print(
            "COMANDO -> atualizar_movimentacao_posse(MovimentacaoPosse.cmd_atualizar_cache_ativo)"
        )
        MovimentacaoPosse.cmd_atualizar_cache_ativo()

    def cmd_activate_workload_by_date(self):
        print("Início -> Activate Workload by Date")
        for workload in CargaHoraria.objects.filter(
            data_inicio=date.today(), servidor__ativo=True
        ):
            try:
                workload.activate_workload_by_date()
            except Exception as err:
                log.exception(f"Erro: {workload} - {err}")

        print("FIM -> Activate Workload by Date")

    def cmd_inactivate_workload_by_date(cls):
        print("Início -> Inactivate Workload by Date")
        for workload in CargaHoraria.objects.filter(
            data_fim__lt=date.today(), servidor__ativo=True
        ):
            try:
                workload.inactivate_workload_by_date()
            except Exception as err:
                log.exception(f"Erro: {workload} - {err}")
        print("FIM -> Inactivate Workload by Date")

    def cmd_termination_process(self):
        log.info("COMANDO -> MovimentacaoDesligamento.cmd_termination_process()")
        print("COMANDO -> MovimentacaoDesligamento.cmd_termination_process()")
        MovimentacaoDesligamento.cmd_termination_process()

    def cmd_terminate_trainee(self):
        log.info("Início -> Desligamento de Etagiários")
        PossessionTrainee().terminate_trainee_by_end_contract()
        log.info("FIM -> Desligamento de Etagiários")

    def cmd_terminate_resident(self):
        log.info("Início -> Desligamento de Residentes")
        PossessionResident().terminate_resident_by_end_contract()
        log.info("FIM -> Desligamento de Residentes")
