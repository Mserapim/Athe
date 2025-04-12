# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.decorator import deprecated
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.task.workplace import manager_taks_updater

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--call",
            action="store",
            dest="call",
            help="Chamada ao comando de migração de lotações antigas novas.",
        )

    def __init__(self, *args, **kargs):
        set_current_user(User.objects.get(username="athenas"))
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["call"]:
            self.call_manager_taks_updater(options["call"])

    @deprecated
    def call_manager_taks_updater(self, workplace):
        log.info(
            "COMANDO -> call_manager_taks_updater. Chamada ao comando de migração de lotações antigas às novas."
        )
        Task.start(manager_taks_updater, new=workplace, user=get_current_user().pk)
