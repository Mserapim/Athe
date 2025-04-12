# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ProntuaryConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "corregedoria.prontuary"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "corregedoria.prontuary.api.prontuary",
        "corregedoria.prontuary.api.employee",
        "corregedoria.prontuary.api.inspectionlink",
        "corregedoria.prontuary.api.listcumulation",
        "corregedoria.prontuary.api.detaillistindication",
        "corregedoria.prontuary.api.attachmentslistindication",
        "corregedoria.prontuary.api.detailinstitutionalparticipation",
        "corregedoria.prontuary.api.attachmentsdetailinstitutionalparticipation",
        "corregedoria.prontuary.api.detailcoursesparticipation",
        "corregedoria.prontuary.api.attachmentsdetailcoursesparticipation",
        "corregedoria.prontuary.api.detailtrainingimprovement",
        "corregedoria.prontuary.api.attachmentsdetailtrainingimprovement",
        "corregedoria.prontuary.api.detailperformanceparticulardifficulty",
        "corregedoria.prontuary.api.detailinstitutionalcontribution",
        "corregedoria.prontuary.api.attachmentsdetailinstitutionalcontribution",
        "corregedoria.prontuary.api.detailintegratestrategicworkgroup",
        "corregedoria.prontuary.api.attachmentsdetailintegratestrategicworkgroup",
        "corregedoria.prontuary.api.detailintegrateworkgroup",
        "corregedoria.prontuary.api.attachmentsdetailintegrateworkgroup",
        "corregedoria.prontuary.api.detailexerciseinrole",
        "corregedoria.prontuary.api.attachmentsdetailexerciseinrole",
        "corregedoria.prontuary.api.detailpromotion",
        "corregedoria.prontuary.api.attachmentsdetailpromotion",
        "corregedoria.prontuary.api.detailremoval",
        "corregedoria.prontuary.api.attachmentsdetailremoval",
        "corregedoria.prontuary.api.detailpermutation",
        "corregedoria.prontuary.api.attachmentsdetailpermutation",
        "corregedoria.prontuary.api.detailadministrativefunction",
        "corregedoria.prontuary.api.attachmentsdetailadministrativefunction",
        "corregedoria.prontuary.api.detaildesignationcumulation",
        "corregedoria.prontuary.api.attachmentsdetaildesignationcumulation",
        "corregedoria.prontuary.api.detailexercise",
        "corregedoria.prontuary.api.attachmentsdetailexercise",
        "corregedoria.prontuary.api.detailjointaction",
        "corregedoria.prontuary.api.attachmentsdetailjointaction",
        "corregedoria.prontuary.api.detailpartieshearings",
        "corregedoria.prontuary.api.attachmentsdetailpartieshearings",
        "corregedoria.prontuary.api.detailreplacement",
        "corregedoria.prontuary.api.attachmentsdetailreplacement",
        "corregedoria.prontuary.api.detailexoneration",
        "corregedoria.prontuary.api.attachmentsdetailexoneration",
        "corregedoria.prontuary.api.detailretirement",
        "corregedoria.prontuary.api.attachmentsdetailretirement",
        "corregedoria.prontuary.api.detaildeparture",
        "corregedoria.prontuary.api.attachmentsdetaildeparture",
        "corregedoria.prontuary.api.detailavailability",
        "corregedoria.prontuary.api.attachmentsdetailavailability",
        "corregedoria.prontuary.api.detailpunishment",
        "corregedoria.prontuary.api.attachmentsdetailpunishment",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app
        load_notify()


def load_notify():
    importlib.import_module("corregedoria.prontuary.notify")


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("corregedoria.prontuary.signals")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/corregedoria/prontuary/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/Window.js",
        "/%(context)s/static/corregedoria/prontuary/generaldata/Window.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/inspectionlink/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/inspectionlink/Window.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/inspectionlink/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/inspectionlink/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/listcumulation/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/listcumulation/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/functionalperformance/listcumulation/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/listindication/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalparticipation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/coursesparticipation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/trainingimprovement/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/performanceparticulardifficulty/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/performanceparticulardifficulty/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/performanceparticulardifficulty/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/performanceparticulardifficulty/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/institutionalcontribution/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integratestrategicworkgroup/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/integrateworkgroup/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/individualperformance/exerciseinrole/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/promotion/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/removal/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/movement/permutation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/administrativefunction/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/designationcumulation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/exercise/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/jointaction/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/partieshearings/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/designation/replacement/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/exoneration/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/termination/retirement/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/departure/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/availability/attachments/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/Manage.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/Restful.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/attachments/Window.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/attachments/Grid.js",
        "/%(context)s/static/corregedoria/prontuary/career/others/punishment/attachments/Restful.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="corregedoria")
