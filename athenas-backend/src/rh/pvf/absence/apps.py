import importlib
from django.apps import AppConfig


class PVFAbsenceConfig(AppConfig):
    name = "rh.pvf.absence"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "rh.pvf.absence.api.absence",
        "rh.pvf.absence.api.person.person",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    # Application.register_stylesheet('/%(context)s/static/rh/cif/cif.css')

    js_paths = (
        "/%(context)s/static/rh/pvf/absence/absence/GenericWindow.js",
        "/%(context)s/static/rh/pvf/absence/absence/DetailWindow.js",
        "/%(context)s/static/rh/pvf/absence/absence/Window.js",
        "/%(context)s/static/rh/pvf/absence/absence/Grid.js",
        "/%(context)s/static/rh/pvf/absence/absence/Restful.js",
        "/%(context)s/static/rh/pvf/absence/absence/Manage.js",
        "/%(context)s/static/rh/pvf/absence/familyhealthtreatment/Window.js",
        "/%(context)s/static/rh/pvf/absence/familyhealthtreatment/Grid.js",
        "/%(context)s/static/rh/pvf/absence/familyhealthtreatment/Restful.js",
        "/%(context)s/static/rh/pvf/absence/familyhealthtreatment/Manage.js",
        "/%(context)s/static/rh/pvf/absence/healthtreatment/Window.js",
        "/%(context)s/static/rh/pvf/absence/healthtreatment/Grid.js",
        "/%(context)s/static/rh/pvf/absence/healthtreatment/Restful.js",
        "/%(context)s/static/rh/pvf/absence/healthtreatment/Manage.js",
        "/%(context)s/static/rh/pvf/absence/marriage/Window.js",
        "/%(context)s/static/rh/pvf/absence/marriage/Grid.js",
        "/%(context)s/static/rh/pvf/absence/marriage/Restful.js",
        "/%(context)s/static/rh/pvf/absence/marriage/Manage.js",
        "/%(context)s/static/rh/pvf/absence/maternity/Window.js",
        "/%(context)s/static/rh/pvf/absence/maternity/Grid.js",
        "/%(context)s/static/rh/pvf/absence/maternity/Restful.js",
        "/%(context)s/static/rh/pvf/absence/maternity/Manage.js",
        "/%(context)s/static/rh/pvf/absence/blood_donation/Window.js",
        "/%(context)s/static/rh/pvf/absence/blood_donation/Grid.js",
        "/%(context)s/static/rh/pvf/absence/blood_donation/Restful.js",
        "/%(context)s/static/rh/pvf/absence/blood_donation/Manage.js",
        "/%(context)s/static/rh/pvf/absence/paternity/Window.js",
        "/%(context)s/static/rh/pvf/absence/paternity/Grid.js",
        "/%(context)s/static/rh/pvf/absence/paternity/Restful.js",
        "/%(context)s/static/rh/pvf/absence/paternity/Manage.js",
        "/%(context)s/static/rh/pvf/absence/mourning/Window.js",
        "/%(context)s/static/rh/pvf/absence/mourning/Grid.js",
        "/%(context)s/static/rh/pvf/absence/mourning/Restful.js",
        "/%(context)s/static/rh/pvf/absence/mourning/Manage.js",
        "/%(context)s/static/rh/pvf/absence/politicalactivity/Window.js",
        "/%(context)s/static/rh/pvf/absence/politicalactivity/Grid.js",
        "/%(context)s/static/rh/pvf/absence/politicalactivity/Restful.js",
        "/%(context)s/static/rh/pvf/absence/politicalactivity/Manage.js",
        "/%(context)s/static/rh/pvf/absence/privateinterest/Window.js",
        "/%(context)s/static/rh/pvf/absence/privateinterest/Grid.js",
        "/%(context)s/static/rh/pvf/absence/privateinterest/Restful.js",
        "/%(context)s/static/rh/pvf/absence/privateinterest/Manage.js",
        "/%(context)s/static/rh/pvf/absence/training/Window.js",
        "/%(context)s/static/rh/pvf/absence/training/Grid.js",
        "/%(context)s/static/rh/pvf/absence/training/Restful.js",
        "/%(context)s/static/rh/pvf/absence/training/Manage.js",
        "/%(context)s/static/rh/pvf/person/Restful.js",
        "/%(context)s/static/rh/pvf/person/ChildRestful.js",
        "/%(context)s/static/rh/pvf/person/Window.js",
        "/%(context)s/static/rh/pvf/person/ChildWindow.js",
        "/%(context)s/static/rh/pvf/person/Grid.js",
        "/%(context)s/static/rh/pvf/person/ChildGrid.js",
        "/%(context)s/static/rh/pvf/person/Manage.js",
        "/%(context)s/static/rh/pvf/person/ChildManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
