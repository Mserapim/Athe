# -*- coding: utf-8 -*-
import os
import importlib

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Comando pós instalação."

    def handle(self, *args, **options):
        from django.conf import settings

        apps = [args[0]] if len(args) > 0 else settings.INSTALLED_APPS
        for app_name in apps:
            self.stdout.write("Setting up application %s\n" % app_name)
            try:
                app = importlib.import_module(app_name)
            except ImportError as e:
                self.stdout.write("Aplicativo %s não existe. %s" % (app_name, e))
            else:
                if app.__path__:

                    for fixture in [
                        "menu-application.json",
                        "menu-controller.json",
                        "messgaes.json",
                    ]:
                        fixture_path = os.path.join(
                            app.__path__[0], "fixtures", fixture
                        )

                        if os.path.exists(fixture_path):
                            self.stdout.write(
                                "--Load fixture %s from %s app...\n"
                                % (fixture, app_name)
                            )
                            call_command("loaddata", fixture_path)

                if hasattr(app, "post_install"):
                    self.stdout.write(
                        "--Executing post_install function from %s app...\n" % app_name
                    )
                    app.post_install()
