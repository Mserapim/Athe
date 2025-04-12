# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib

from django.apps import AppConfig


class RequestFormConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "edocs.protocolo.requestform"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "edocs.protocolo.requestform.api.vacationdaysell",
        "edocs.protocolo.requestform.api.mobileliabilitystatement",
        "edocs.protocolo.requestform.api.mobilereturnstatement",
        "edocs.protocolo.requestform.api.debitauthorization",
        "edocs.protocolo.requestform.api.electorallicense",
        "edocs.protocolo.requestform.api.employeerequest",
        "edocs.protocolo.requestform.api.memberrequest",
        "edocs.protocolo.requestform.api.weddingdayoff",
        "edocs.protocolo.requestform.api.childbirthdayoff",
        "edocs.protocolo.requestform.api.childbirthallowance",
        "edocs.protocolo.requestform.api.finalpaperdayoff",
        "edocs.protocolo.requestform.api.blooddonationdayoff",
        "edocs.protocolo.requestform.api.electoralenlistment",
        "edocs.protocolo.requestform.api.transitpass",
        "edocs.protocolo.requestform.api.bereavementleave",
        "edocs.protocolo.requestform.api.funeralallowance",
        "edocs.protocolo.requestform.api.vacancydeclaration",
        "edocs.protocolo.requestform.api.resignation",
        "edocs.protocolo.requestform.api.mealallowance",
        "edocs.protocolo.requestform.api.childcareallowance",
        "edocs.protocolo.requestform.api.specialneedsallowance",
        "edocs.protocolo.requestform.api.functionalidentity",
        "edocs.protocolo.requestform.api.idbadge",
        "edocs.protocolo.requestform.api.anticipationthirteenth",
        "edocs.protocolo.requestform.api.nonanticipationthirteenth",
        "edocs.protocolo.requestform.api.dependentinclusion",
        "edocs.protocolo.requestform.api.dependentexclusion",
        "edocs.protocolo.requestform.api.fulltimehomeoffice",
        "edocs.protocolo.requestform.api.comebybike",
        "edocs.protocolo.requestform.api.thirteenthanticipation",
        "edocs.protocolo.requestform.api.healthcareallowance",
        "edocs.protocolo.requestform.api.termocompromissosigilo",
        "edocs.protocolo.requestform.api.homeoffice",
        "edocs.protocolo.requestform.api.evaluation",
        "edocs.protocolo.requestform.api.removenotificationapplication",
        "edocs.protocolo.requestform.api.removenotificationresistance",
        "edocs.protocolo.requestform.api.intimationwhatsappvictim",
        "edocs.protocolo.requestform.api.intimationwhatsappintimate",
        "edocs.protocolo.requestform.api.medicallicenseemployee",
        "edocs.protocolo.requestform.api.medicallicensefamiliar",
        "edocs.protocolo.requestform.api.compensateexpense",
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
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:
        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/edocs/protocolo/requestform/mixins/Common.js",
        # Removido a pedido da chefia imediata (issue #1038)
        "/%(context)s/static/edocs/protocolo/requestform/thirteenthanticipation/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/thirteenthanticipation/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/thirteenthanticipation/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/EmployeeAcquisitionPeriodRestful.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/EmployeeAcquisitionPeriodGrid.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacationdaysell/EmployeeAcquisitionPeriodWindow.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobileliabilitystatement/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobileliabilitystatement/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobileliabilitystatement/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobilereturnstatement/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobilereturnstatement/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/mobilereturnstatement/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/debitauthorization/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/debitauthorization/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/debitauthorization/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/electorallicense/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/electorallicense/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/electorallicense/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/employeerequest/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/employeerequest/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/employeerequest/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/memberrequest/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/memberrequest/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/memberrequest/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/weddingdayoff/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/weddingdayoff/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/weddingdayoff/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthdayoff/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthdayoff/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthdayoff/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthallowance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthallowance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/childbirthallowance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/finalpaperdayoff/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/finalpaperdayoff/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/finalpaperdayoff/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/blooddonationdayoff/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/blooddonationdayoff/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/blooddonationdayoff/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/electoralenlistment/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/electoralenlistment/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/electoralenlistment/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/transitpass/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/transitpass/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/transitpass/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/bereavementleave/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/bereavementleave/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/bereavementleave/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/funeralallowance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/funeralallowance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/funeralallowance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacancydeclaration/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacancydeclaration/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/vacancydeclaration/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/resignation/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/resignation/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/resignation/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/mealallowance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/mealallowance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/mealallowance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/childcareallowance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/childcareallowance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/childcareallowance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/specialneedsallowance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/specialneedsallowance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/specialneedsallowance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/functionalidentity/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/functionalidentity/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/functionalidentity/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/idbadge/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/idbadge/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/idbadge/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/anticipationthirteenth/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/anticipationthirteenth/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/anticipationthirteenth/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/anticipationthirteenth/Manage.js",
        "/%(context)s/static/edocs/protocolo/requestform/nonanticipationthirteenth/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/nonanticipationthirteenth/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/nonanticipationthirteenth/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependent/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependent/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependent/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentinclusion/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentinclusion/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentinclusion/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusionitem/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusionitem/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusionitem/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusion/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusion/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/dependentexclusion/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/fulltimehomeoffice/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/fulltimehomeoffice/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/fulltimehomeoffice/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/comebybike/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/comebybike/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/comebybike/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/activeemployee/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/activeemployee/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/activeemployee/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/inactiveemployee/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/inactiveemployee/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/healthcareallowance/inactiveemployee/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/termocompromissosigilo/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/termocompromissosigilo/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/termocompromissosigilo/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/evaluation/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/evaluation/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/evaluation/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/homeoffice/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/homeoffice/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/homeoffice/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationapplication/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationapplication/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationapplication/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationresistance/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationresistance/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/removenotificationresistance/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicenseemployee/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicenseemployee/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicenseemployee/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicensefamiliar/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicensefamiliar/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/medicallicensefamiliar/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappvictim/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappvictim/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappvictim/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappintimate/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappintimate/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/intimationwhatsappintimate/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpense/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpense/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpense/Window.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpenseitem/Grid.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpenseitem/Restful.js",
        "/%(context)s/static/edocs/protocolo/requestform/compensateexpenseitem/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="edocs")


def loaders():
    pass
