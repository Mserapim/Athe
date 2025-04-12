# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import Servidor
from rh.registration.models import DependentFormInformation, FormInformation

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--create",
            action="store_true",
            dest="create",
            help="Faz o load do formulário para servidores novos.",
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
        if options["create"]:
            self.load_employeers()
            self.load_dependents()

    def load_employeers(self):
        self.set_user_to_job("job_registration_load_employeers")
        employeers = FormInformation.objects.filter(employee__ativo=True).values_list(
            "employee__matricula", flat=True
        )
        for s in Servidor.objects.filter(ativo=True, tipo__in=["S", "M", "P"]).exclude(
            matricula__in=employeers
        ):
            FormInformation.command_load_info_employee(s)

    def load_dependents(self):
        self.set_user_to_job("job_registration_load_dependents")
        for employee in Servidor.objects.filter(ativo=True):
            DependentFormInformation.command_load_info_dependent(employee=employee)
