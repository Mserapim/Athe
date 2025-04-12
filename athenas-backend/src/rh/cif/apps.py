# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class CIFConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.cif"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # CIF - INFORMATION MEMBER
        "rh.cif.api.attachment",
        "rh.cif.api.educationalinstitution",
        "rh.cif.api.discipline",
        "rh.cif.api.schedule",
        "rh.cif.api.codeproperty",
        "rh.cif.api.controlinformationmember",
        "rh.cif.api.teaching",
        "rh.cif.api.address",
        "rh.cif.api.property",
        "rh.cif.api.referenceperiod",
        "rh.cif.api.referenceperiod",
        "rh.cif.api.codedebtsencumbrances",
        "rh.cif.api.debtsencumbrances",
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

    Application.register_stylesheet("/%(context)s/static/rh/cif/cif.css")

    js_paths = (
        "/%(context)s/static/rh/cif/educational/EducationalInstitutionRestful.js",
        "/%(context)s/static/rh/cif/educational/EducationalInstitutionWindow.js",
        "/%(context)s/static/rh/cif/educational/EducationalInstitutionGrid.js",
        "/%(context)s/static/rh/cif/educational/Manage.js",
        "/%(context)s/static/rh/cif/discipline/DisciplineRestful.js",
        "/%(context)s/static/rh/cif/discipline/DisciplineWindow.js",
        "/%(context)s/static/rh/cif/discipline/DisciplineGrid.js",
        "/%(context)s/static/rh/cif/discipline/Manage.js",
        "/%(context)s/static/rh/cif/schedule/ScheduleRestful.js",
        "/%(context)s/static/rh/cif/schedule/ScheduleWindow.js",
        "/%(context)s/static/rh/cif/schedule/ScheduleGrid.js",
        "/%(context)s/static/rh/cif/schedule/Manage.js",
        "/%(context)s/static/rh/cif/codeproperty/CodePropertyRestful.js",
        "/%(context)s/static/rh/cif/codeproperty/CodePropertyWindow.js",
        "/%(context)s/static/rh/cif/codeproperty/CodePropertyGrid.js",
        "/%(context)s/static/rh/cif/codeproperty/Manage.js",
        "/%(context)s/static/rh/cif/codedebtsencumbrances/CodeDebtsEncumbrancesRestful.js",
        "/%(context)s/static/rh/cif/codedebtsencumbrances/CodeDebtsEncumbrancesWindow.js",
        "/%(context)s/static/rh/cif/codedebtsencumbrances/CodeDebtsEncumbrancesGrid.js",
        "/%(context)s/static/rh/cif/teaching/TeachingRestful.js",
        "/%(context)s/static/rh/cif/teaching/TeachingWindow.js",
        "/%(context)s/static/rh/cif/teaching/TeachingGrid.js",
        "/%(context)s/static/rh/cif/teaching/Manage.js",
        "/%(context)s/static/rh/cif/address/AddressRestful.js",
        "/%(context)s/static/rh/cif/address/AddressWindow.js",
        "/%(context)s/static/rh/cif/address/AddressGrid.js",
        "/%(context)s/static/rh/cif/address/Manage.js",
        "/%(context)s/static/rh/cif/attachment/AttachmentRestful.js",
        "/%(context)s/static/rh/cif/attachment/AttachmentWindow.js",
        "/%(context)s/static/rh/cif/attachment/AttachmentGrid.js",
        "/%(context)s/static/rh/cif/attachment/Manage.js",
        "/%(context)s/static/rh/cif/property/PropertyRestful.js",
        "/%(context)s/static/rh/cif/property/PropertyWindow.js",
        "/%(context)s/static/rh/cif/property/PropertyGrid.js",
        "/%(context)s/static/rh/cif/property/Manage.js",
        "/%(context)s/static/rh/cif/debtsencumbrances/DebtsEncumbrancesRestful.js",
        "/%(context)s/static/rh/cif/debtsencumbrances/DebtsEncumbrancesWindow.js",
        "/%(context)s/static/rh/cif/debtsencumbrances/DebtsEncumbrancesGrid.js",
        "/%(context)s/static/rh/cif/referenceperiod/ReferencePeriodRestful.js",
        "/%(context)s/static/rh/cif/referenceperiod/ReferencePeriodWindow.js",
        "/%(context)s/static/rh/cif/referenceperiod/ReferencePeriodGrid.js",
        "/%(context)s/static/rh/cif/referenceperiod/ConfigurationManage.js",
        "/%(context)s/static/rh/cif/referenceperiod/Manage.js",
        "/%(context)s/static/rh/cif/controlinformationmember/ControlInformationMemberRestful.js",
        "/%(context)s/static/rh/cif/controlinformationmember/ControlInformationMemberWindow.js",
        "/%(context)s/static/rh/cif/controlinformationmember/CopyInformationWindow.js",
        "/%(context)s/static/rh/cif/controlinformationmember/NotificationWindow.js",
        "/%(context)s/static/rh/cif/controlinformationmember/NotificationAllWindow.js",
        "/%(context)s/static/rh/cif/controlinformationmember/ControlInformationMemberGrid.js",
        "/%(context)s/static/rh/cif/controlinformationmember/ControlMemberGrid.js",
        "/%(context)s/static/rh/cif/Manage.js",
        "/%(context)s/static/rh/cif/ManageConfiguration.js",
        "/%(context)s/static/rh/cif/controlinformationmember/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
