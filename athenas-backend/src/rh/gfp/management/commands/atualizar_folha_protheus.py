# -*- coding: utf-8 -*-

from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.gfp.models import Folha

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """ Atualizar o status da folha migrada do prothues para fechado """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.atualizar_status_folha()

    def atualizar_status_folha(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando alteração do status >>>>>>>>>>>>>"
        )

        Folha.objects.filter(periodo__ano__lte=2021).update(status=3)

        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando alteração do status >>>>>>>>>>>>>"
        )
