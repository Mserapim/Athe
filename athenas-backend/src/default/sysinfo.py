# -*- coding: utf-8 -*-
import json

from default.views import Application as app
from django.conf import settings
from contrib.utils import getLogger


log = getLogger(__name__)


try:
    from south.signals import post_migrate
except:
    pass
else:

    def update_permissions_after_migration(app, **kargs):
        """
        Update app permission just after every migration.
        This is based on app django_extensions update_permissions management command.
        """
        from django.conf import settings
        from django.db.models import get_app, get_models
        from django.contrib.auth.management import create_permissions

        print("Criando permissões faltantes...")
        create_permissions(get_app(app), get_models(), 2 if settings.DEBUG else 0)


class __SysInfo:

    def __load_sys_info(self):
        if not getattr(self, "loaded", False) and hasattr(settings, "SYSTEM_INFO_FILE"):
            try:
                with open(getattr(settings, "SYSTEM_INFO_FILE"), "r") as fd:
                    data = json.load(fd)
                    for key, value in list(data.items()):
                        setattr(self, "__%s" % key, value)
                    self.loaded = True
            except Exception:
                log.info("Não foi possivel carregar informações do build do sistema")

    @property
    def build(self):
        try:
            self.__load_sys_info()
        except Exception as e:
            log.exception(e)

        return getattr(self, "__build", 0)


SysInfo = __SysInfo()


@app.session_resource("build")
def __build_version():
    return SysInfo.build
