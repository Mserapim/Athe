# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core import serializers
from django.conf import settings
from optparse import make_option
from contrib.utils import get_json_engine
from contrib.middleware import set_current_user
from engine.models import Application, Controller
import os
import codecs
import uuid
import re
import datetime

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3


class Command(BaseCommand):

    help = """Este comando é responsável por executar rotinas de manutenção dos menus no Athenas."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--file_path",
            default=None,
            dest="file_path",
            help="Arquivo json a ser criado",
        )

        parser.add_argument(
            "-m",
            "--module",
            default=None,
            dest="module",
            help="Modulo do Athenas que terá o menu gerado. Se não for informado será exportado apenas o menu cujo module vazio",
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

    def get_last_menu_file(self, dir_):
        import glob

        dirs = glob.glob("%s/menu*.json" % dir_)
        last = 0
        for d in dirs:
            res = re.match(".*/menu([0-9]*).json", d)
            if res and res.groups() and int(res.groups()[0] or "0") > last:
                last = int(res.groups()[0])

        return "%s/menu%s.json" % (dir_, last or "")

    def create_or_update_menu(self, module="", file_path=None):

        json = get_json_engine()

        if not file_path:
            base_dir = getattr(settings, "BASE_DIR", ".")
            path_module = module.replace(".", "/") if module else "."
            file_path = self.get_last_menu_file(
                "/".join([base_dir, path_module, "fixtures"])
            )
            # file_path = '/'.join([base_dir, path_module, 'fixtures', file_menu])

        if not os.path.exists(file_path):
            print("Menu file (%s) not found!" % file_path)
        else:
            with codecs.open(file_path, "r", "utf-8") as fd:
                str_ = fd.read()

            menu = json.decode(str_)
            changed = False
            for m in menu:
                try:
                    cls = (
                        Controller if m["model"] == "engine.controller" else Application
                    )

                    field = "father" if "father" in m["fields"] else "application"
                    m["fields"][field] = (
                        Application.objects.get(uuid=m["fields"][field])
                        if m["fields"][field]
                        else None
                    )

                    obj, created = cls.objects.get_or_create(
                        uuid=m["fields"]["uuid"], defaults=m["fields"]
                    )
                    if created:
                        print("GENERATING %s - %s" % (cls, obj))
                        changed = True
                    else:
                        for k in m["fields"]:
                            setattr(obj, k, m["fields"][k])
                        if obj.changed:
                            obj.save()
                            print("UPDATING %s - %s: %s" % (cls, obj, obj.old_fields))
                            changed = True
                except Exception as e:
                    print("ERRO ao carregar menu para %s" % m)

            if not changed:
                print("No changes in menu!")

    def handle(self, module="", file_path=None, *args, **kargs):
        self.active_athenas_user()

        if module != "" and module not in settings.INSTALLED_APPS:
            print("Menu não carregado!")
            print("OBS.: O module precisa está listado no settings.INSTALLED_APPS.")
        else:
            self.create_or_update_menu(module, file_path)
