# -*- coding:utf-8 -*-

import os
import importlib

"""
Módulo para manter os mecanismos de automatização e customização do settings.py.

Neste módulo NÃO DEVE HAVER import do settings ou qualquer ou outro módulo que tenha
importação do settings do Django.
"""

ATHENAS_WATCH_APPS = None

if "ATHENAS_WATCH_APPS" in os.environ:
    ATHENAS_WATCH_APPS = os.environ.get("ATHENAS_WATCH_APPS").split(",")


class ControllerCollector(object):

    def __init__(self, installed_apps=[]):
        self.__installed_apps = installed_apps

    def __get_by_default_app_config(self, path):
        app = importlib.import_module(path)
        if ATHENAS_WATCH_APPS and app not in ATHENAS_WATCH_APPS:
            pass
        elif not hasattr(app, "default_app_config"):
            raise Exception("There is no default AppConfig for %s" % path)

        return self.__get_app_config(app.default_app_config)

    def __get_app_config(self, path):
        pieces = path.split(".")
        module_path, app_config_name = ".".join(pieces[:-1]), pieces[-1]
        if "Config" not in app_config_name:
            raise Exception("There is no AppConfig for %s" % path)

        module = importlib.import_module(module_path)
        return getattr(module, app_config_name, {})

    @property
    def collection(self):
        controllers = []
        for app_path in self.__installed_apps:
            try:
                app_config = (
                    self.__get_app_config(app_path)
                    if "Config" in app_path
                    else self.__get_by_default_app_config(app_path)
                )
            except Exception as e:
                if not ATHENAS_WATCH_APPS or (
                    ATHENAS_WATCH_APPS and app_path in ATHENAS_WATCH_APPS
                ):
                    print("# %s => %s" % (app_path, e))
            else:
                controllers = controllers + getattr(app_config, "controllers", [])
        return controllers


def apps_settings(installed_apps):
    apps_settings = {}
    for app_path in installed_apps:
        try:
            settings_path = "%s.app_settings" % app_path
            settings = importlib.import_module(settings_path)
        except ImportError:
            pass
        except Exception as e:
            err = "An error occured in app_settings for %s. %s" % (app_path, e)
            raise Exception(err)
        else:
            for item in dir(settings):
                if not item.startswith("__"):
                    apps_settings[item] = getattr(settings, item)
    # print(apps_settings)
    return apps_settings


def apps_controllers(installed_apps):
    return ControllerCollector(installed_apps).collection
