# -*- coding: utf-8 -*-
import subprocess
import os
import codecs
import uuid
import re
import datetime
import glob

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core import serializers
from django.conf import settings
from optparse import make_option
from contrib.utils import get_json_engine, Locker
from contrib.middleware import set_current_user
from engine.models import Application, Controller, TaskSession
from dateutil.relativedelta import relativedelta

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Command(BaseCommand):

    help = """Locks for routines' Athenas!"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--delete-zombies",
            default=False,
            action="store_true",
            dest="delete_zombies",
            help="Delete all zombies locks!",
        )
        parser.add_argument(
            "-f",
            "--force",
            default=False,
            action="store_true",
            dest="force",
            help="Force the restart of the system!",
        )
        parser.add_argument(
            "-n",
            "--no-touch",
            default=False,
            action="store_true",
            dest="no_touch",
            help="Dont restart system!",
        )

    def log(self, message):
        (LEVEL_QUIET <= self.verbosity) and self.print_message(message)

    def error(self, message):
        (LEVEL_ERROR <= self.verbosity) and self.print_message(message)

    def info(self, message):
        (LEVEL_INFO <= self.verbosity) and self.print_message(message)

    def debug(self, message):
        (LEVEL_DEBUG <= self.verbosity) and self.print_message(message)

    def print_message(self, message):
        print(message)

    def active_athenas_user(self):
        try:
            user = User.objects.get(username="athenas")
        except User.DoesNotExist as e:
            self.log.error('Não econtrei o usuário "athenas"')
            raise e
        else:
            set_current_user(user)

    def touch(self, force=False):
        if force:
            print("")
            print("*************** FORCING TOUCH ***************")

        if hasattr(settings, "RESTART_FILE"):
            file_ = os.environ.get("ATHENAS_RESTART_FILE", settings.RESTART_FILE)
            if file_:
                print(
                    "TOUCHING FILE %s" % file_,
                )
                return_code = subprocess.call(["touch %s" % file_], shell=True)
                print(" OK" if return_code == 0 else " ERROR")
                print("**********************************************")
                print("")
        else:
            print("WARNING: RESTART_FILE não esta configurado.")

    def tasks(self, delete_zombies=False):
        lockers = Locker.locks()
        active_locks = 0
        locks_dir = getattr(settings, "LOCKS_DIR", None)
        print("")
        print(
            "%s--------------- LOCKS / TASKS -------------------%s"
            % (bcolors.HEADER, bcolors.ENDC)
        )
        for host in lockers:
            host_ = (
                (bcolors.FAIL + "**ZOMBIE**" + bcolors.ENDC)
                if host == "__zombies__"
                else (bcolors.OKBLUE + host + bcolors.ENDC)
            )
            locks = lockers[host]
            for l in locks:
                task = TaskSession.objects.filter(starter_id=l.get("id")).first()
                print(
                    ">>>> %s %s %s"
                    % (
                        host_,
                        l.get("duration_str"),
                        task.description if task else l.get("slug"),
                    ),
                )
                if host != "__zombies__":
                    active_locks += 1
                    print("")
                elif delete_zombies:
                    zombie_path = os.path.join(locks_dir, l.get("file"))
                    os.remove(zombie_path)
                    if task:
                        task.info("Tarefa abortada no servidor!", 3)
                        task.finish_execution("ERROR")
                    print(bcolors.OKGREEN + ">> DELETED <<" + bcolors.ENDC)
                else:
                    print("")
        zombie_tasks = TaskSession.objects.filter(finished_task=None).exclude(
            starter_id__in=list(Locker.started_ids().keys())
        )
        if zombie_tasks:
            print("")
        print(
            "%s-------------------------------------------------%s"
            % (bcolors.HEADER, bcolors.ENDC)
        )
        print("")

        return active_locks

    def handle(self, delete_zombies=False, force=False, no_touch=False, *args, **kargs):

        self.active_athenas_user()
        locks = self.tasks(delete_zombies)
        touch = not locks and no_touch is False
        # print 'LOCKS %s (%s) %s/%s' % (locks, touch, not locks, no_touch is False)

        if force or touch:
            self.touch(force)
        elif no_touch is False:
            print("")
            print("---------------!!!!!------------------")
            print("DONT RESTART SYSTEM. WAIT FOR LOCKS...")
            print("--------------------------------------")
            print("")
