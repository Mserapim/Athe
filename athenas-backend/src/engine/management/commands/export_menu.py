# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core import serializers
from django.conf import settings
from optparse import make_option
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


def natural_key(self):
    return self.uuid


Application.natural_key = natural_key
Controller.natural_key = natural_key


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

    def serialize(self, query, indent=2, use_pk=False):
        if isinstance(query, (list, QuerySet)) is False:
            query = [query]
        serial = serializers.serialize(
            "json", query, indent=indent, use_natural_keys=True
        )
        if use_pk is False:
            serial = re.sub('"pk": [0-9]*', '"pk": null', serial)
        return serial

    def dump_menu(self, module=None):
        _apps = []
        idx = 0
        query = Controller.objects.all()
        if module:
            query = query.filter(module=module)
        for c in query:
            app = c.application
            while app and app not in _apps:
                _apps.insert(idx, app)
                app = app.father
            _apps.append(c)
            idx = len(_apps)
        return _apps

    def check_menu_uuid(self):
        print(
            "GENERATE UUID MENUS -----------------------------------------------------"
        )
        for app in Application.objects.filter(uuid=None):
            print(
                Application.objects.filter(pk=app.pk).update(uuid=uuid.uuid4().hex), app
            )
        for ctr in Controller.objects.filter(uuid=None):
            print(
                Controller.objects.filter(pk=ctr.pk).update(uuid=uuid.uuid4().hex), ctr
            )
        print(
            "-------------------------------------------------------------------------"
        )

    def create_json_file(self, module="", file_path=None):

        self.check_menu_uuid()
        apps = self.dump_menu(module)
        str_ = self.serialize(apps)

        if not file_path:
            t = datetime.datetime.now()
            base_dir = getattr(settings, "BASE_DIR", ".")
            path_module = module.replace(".", "/") if module else "."
            file_menu = "menu%s.json" % t.strftime("%Y%m%d%H%M%S")
            file_path = "/".join([base_dir, path_module, "fixtures", file_menu])

        file_path = os.path.abspath(file_path)

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if os.path.exists(file_path):
            t = datetime.datetime.now()

            old_file_path = "/".join(
                [os.path.dirname(file_path), "menu%s.json" % t.strftime("%Y%m%d%H%M%S")]
            )

            os.rename(file_path, old_file_path)

            print("Renaming existing file to %s" % old_file_path)

        with codecs.open(file_path, "w", "utf-8") as fd:
            fd.write(str_)

        print("File %s generated successfully!" % file_path)

    def handle(self, module="", file_path=None, **kargs):
        self.active_athenas_user()

        if module != "" and module not in settings.INSTALLED_APPS:
            print("Menu não exportado!")
            print("OBS.: O module precisa está listado no settings.INSTALLED_APPS.")
        else:
            self.create_json_file(module, file_path)
