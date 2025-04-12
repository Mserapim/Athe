# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rh.models import Servidor
from rh.dayoff.vacations_generator import VacationsGenerator
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from standard.models import Choice


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá gerar o período aquisitivo de férias de arcodo com as seguintes regras:
    - Executado diariamente
    - Deve gerar periodos aquisitivos de férias para servidores efetivo, efetivos em comissão, comissionados 
    e membros
    - Situação A: É o primeiro ano do servidor
        O primeiro periodo aquisitivo  do servidor iniciará no dia da admissão e finalizará após 1 ano.
        Exemplo: 12/02/2021 até 11/02/2021 O sistema deve verificar o servidor tem pelo menos 1 periodo
        aquisitivo de férias, senão tiver, então deve gerar conforme regra acima.
    - Situação B: É o segundo ano em diante 
        Se o último periodo aquisitivo do servidor está com data anterior a data de hoje, o sistema deve 
        iniciar novo periodo iniciando um dia após o encerramento e finalizando no dia 31/12 do mesmo ano. 
        Se for membro, então deve gerar dois periodos aquisitivos de 30 dias por ano 
    """

    # def add_arguments(self, parser):
    #     parser.add_argument('-s', '--acquisition_period_server', action='store_true', dest="acquisition_period_server", help="Cria Período de Férias Servidor")
    #     parser.add_argument('-m', '--acquisition_period_member', action='store_true', dest="acquisition_period_member", help="Cria Período de Férias Membros")
    #     parser.add_argument('-a', '--all', action='store_true', dest="all", help="Cria Período de Férias de Servidor e Membro ")

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
        self.server_generator()
        self.member_generator()
        self.trainee_generator()
        self.resident_generator()

    def server_generator(self):
        self.set_user_to_job("job_vacationgeneratorctl_server_generator")
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de férias Servidores >>>>>>>>>>>>>"
        )
        generator = VacationsGenerator()
        server_possessions = Choice.objects.filter(
            name="TYPE_SERVER_POSSESSION", app_label="dayoff"
        ).values_list("cvalue")
        list_types = [x[0] for x in server_possessions]
        try:
            for employee in Servidor.objects.filter(
                type_by_possession__in=list_types, ativo=True
            ):
                generator.server_period_generator(employee)
        except Exception as err:
            log.info(err)
            print(err)
        print(
            ">>> [%s] Finalizando criação automatica de período aquisitivo de férias Servidores >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )

    def member_generator(self):
        self.set_user_to_job("job_vacationgeneratorctl_member_generator")
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de férias Membros >>>>>>>>>>>>>"
        )
        generator = VacationsGenerator()
        member_possessions = Choice.objects.filter(
            name="TYPE_MEMBER_POSSESSION", app_label="dayoff"
        ).values_list("cvalue")
        list_types = [x[0] for x in member_possessions]
        try:
            for employee in Servidor.objects.filter(
                type_by_possession__in=list_types, ativo=True
            ):
                generator.member_period_generator(employee)
        except Exception as err:
            log.info(err)
            print(err)
        print(
            ">>> [%s] Finalizando criação automatica de período aquisitivo de férias Membros"
            % DateUtils.datetime_to_str(date)
        )

    def trainee_generator(self):
        self.set_user_to_job("job_vacationgeneratorctl_trainee_generator")
        date = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de recesso de estagiários >>>>>>>>>>>>>"
        )
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de recesso de estagiários >>>>>>>>>>>>>"
        )
        generator = VacationsGenerator()
        trainee_possessions = ["EST"]
        try:
            for employee in Servidor.objects.filter(
                type_by_possession__in=trainee_possessions, ativo=True
            ):
                log.info(
                    f">> Iniciando verificação/cadastro do Estagiário: {employee} - data de exercicio {employee.data_exercicio}"
                )
                generator.trainee_period_generator(employee)

        except Exception as err:
            log.info(err)
            print(err)
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando criação automatica de período aquisitivo de recesso de estagiários"
        )
        print(
            ">>> [%s] Finalizando criação automatica de período aquisitivo de recesso de estagiários"
            % DateUtils.datetime_to_str(date)
        )

    def resident_generator(self):
        self.set_user_to_job("job_vacationgeneratorctl_resident_generator")
        date = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de recesso de residentes >>>>>>>>>>>>>"
        )
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando criação automatica de período aquisitivo de recesso de residentes >>>>>>>>>>>>>"
        )
        generator = VacationsGenerator()
        resident_possessions = ["RES"]
        try:
            for employee in Servidor.objects.filter(
                type_by_possession__in=resident_possessions, ativo=True
            ):
                log.info(
                    f">> Iniciando verificação/cadastro do Residente: {employee} - data de exercicio {employee.data_exercicio}"
                )
                generator.resident_period_generator(employee)

        except Exception as err:
            log.info(err)
            print(err)
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando criação automatica de período aquisitivo de recesso de residentes"
        )
        print(
            ">>> [%s] Finalizando criação automatica de período aquisitivo de recesso de residentes"
            % DateUtils.datetime_to_str(date)
        )
