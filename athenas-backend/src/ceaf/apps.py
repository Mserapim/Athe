import importlib
from django.apps import AppConfig


class CeafConfig(AppConfig):
    name = "ceaf"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "ceaf.api.capacitation",
    ]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/ceaf/capacitation/Manage.js",
        "/%(context)s/static/ceaf/capacitation/Grid.js",
        "/%(context)s/static/ceaf/capacitation/Window.js",
        "/%(context)s/static/ceaf/capacitation/Restful.js",
        "/%(context)s/static/ceaf/capacitation/participants/Grid.js",
        "/%(context)s/static/ceaf/capacitation/participants/Window.js",
        "/%(context)s/static/ceaf/capacitation/participants/Restful.js",
        "/%(context)s/static/ceaf/reports/Capacitation.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="ceaf")
