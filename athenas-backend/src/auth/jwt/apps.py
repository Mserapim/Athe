# -*- coding:utf-8 -*-

from django import apps
import importlib


class AppConfig(apps.AppConfig):
    name = "auth.jwt"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = ["auth.jwt.api.voucher"]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application
    Application.register_javascript(
        "/%(context)s/static/js/auth/jwt/VoucherRestful.js", scope="core"
    )
    Application.register_javascript(
        "/%(context)s/static/js/auth/jwt/VoucherWindow.js", scope="core"
    )
    Application.register_javascript(
        "/%(context)s/static/js/auth/jwt/VoucherGrid.js", scope="core"
    )
    Application.register_javascript(
        "/%(context)s/static/js/auth/jwt/VoucherManage.js", scope="core"
    )
