# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import django
import subprocess

from contrib.controller import DefaultController
from django.conf import settings
from datetime import timedelta
from contrib.decorator import is_public, update_timeout_session


class DebugInformation(DefaultController):

    def is_repo(self, path):
        return os.path.exists(os.path.join(path, ".git"))

    def get_branch(self, path):
        branchfile = os.path.sep.join([path, ".git", "HEAD"])
        with open(branchfile, "r") as fd:
            return fd.read().split("/")[2].replace("\n", "")

    def get_subapps_info(self):
        rst = []

        basedir = getattr(settings, "BASE_DIR", None)
        if basedir:
            for name in [nname for nname in os.listdir(basedir) if nname not in [".."]]:
                path = os.path.join(basedir, name)
                if self.is_repo(path):
                    rst.append({"name": name, "value": self.get_branch(path)})
            rst.append({"name": "core", "value": self.get_branch(basedir)})

        return rst

    def get_database_conf(self):
        dbconf = getattr(settings, "DATABASES", {}).get("default", {})

        return (
            {"name": "host", "value": dbconf.get("HOST", None)},
            {"name": "user", "value": dbconf.get("USER", None)},
            {"name": "name", "value": dbconf.get("NAME", None)},
            {"name": "engine", "value": dbconf.get("ENGINE", "").split(".")[-1]},
        )

    def get_sys_info(self):

        return (
            {
                "name": "python",
                "value": "%d.%d.%d (%s)"
                % (
                    sys.version_info.major,
                    sys.version_info.minor,
                    sys.version_info.micro,
                    sys.version_info.releaselevel,
                ),
            },
            {"name": "django", "value": "%d.%d.%d-%s-%d" % django.VERSION},
            {
                "name": "modo",
                "value": "DEBUG" if getattr(settings, "DEBUG", False) else "Produção",
            },
            {"name": "platform", "value": sys.platform.title()},
        )

    def get_loader_info(self):
        uptime = timedelta(seconds=float(open("/proc/uptime").read().split()[0]))

        return (
            {"name": "uptime", "value": str(uptime).split(".")[0]},
            # {'name': 'users', 'value': 'undefined'},
            {
                "name": "loader",
                "value": ", ".join(["%0.2f" % v for v in os.getloadavg()]),
            },
        )

    @is_public()
    @update_timeout_session(False)
    def data(self, args=[]):
        rst = {"success": False}

        if (
            getattr(settings, "DEBUG", False) or self.request.user.is_superuser
        ) and getattr(settings, "DEBUG_TOOLBAR", False):
            rst.update(
                success=True,
                sections=(
                    {"title": "Aplicativos", "collection": self.get_subapps_info()},
                    {"title": "Base de dados", "collection": self.get_database_conf()},
                    {"title": "Carga", "collection": self.get_loader_info()},
                    {"title": "Sistema", "collection": self.get_sys_info()},
                ),
            )

        self.response["Content-Type"] = "application/json"
        self.response.write(json.dumps(rst, indent=4))
